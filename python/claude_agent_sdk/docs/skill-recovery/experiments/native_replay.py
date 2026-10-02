"""Run pinned native file replay fault experiments with installed dependencies."""

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import shutil
import signal
import sqlite3
import subprocess
import sys
import time
import traceback
import uuid
from dataclasses import asdict
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def bytes_digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def identity(pid):
    try:
        fields = (
            (Path("/proc") / str(pid) / "stat").read_text().rsplit(")", 1)[1].split()
        )
        return {
            "pid": pid,
            "state": fields[0],
            "parent": int(fields[1]),
            "start_ticks": fields[19],
        }
    except (FileNotFoundError, ProcessLookupError):
        return None


def descendants(pid):
    snapshot = [
        identity(int(p.name)) for p in Path("/proc").iterdir() if p.name.isdigit()
    ]
    owned, result = {pid}, []
    while found := [
        p for p in snapshot if p and p["parent"] in owned and p["pid"] not in owned
    ]:
        result.extend(found)
        owned.update(p["pid"] for p in found)
    return result


async def stop(proc):
    monitor = getattr(proc, "_monitor", None)
    if monitor is not None:
        monitor.cancel()
        try:
            await monitor
        except asyncio.CancelledError:
            pass
    known = {c["pid"]: c for c in getattr(proc, "_owned_children", [])}
    if proc.poll() is None:
        known.update({c["pid"]: c for c in descendants(proc.pid)})
    children = list(known.values())
    if proc.poll() is None:
        proc.kill()
    proc.wait()
    survivors = []
    for old in children:
        now = identity(old["pid"])
        if now and now["start_ticks"] == old["start_ticks"] and now["state"] != "Z":
            survivors.append(now)
            os.kill(old["pid"], signal.SIGKILL)
    for _ in range(40):
        states = [identity(c["pid"]) for c in children]
        active = [
            now
            for old, now in zip(children, states)
            if now and old["start_ticks"] == now["start_ticks"] and now["state"] != "Z"
        ]
        if not active:
            return {
                "children": children,
                "survivors_after_kill": survivors,
                "remaining_active": [],
                "final_states": states,
            }
        await asyncio.sleep(0.05)
    raise RuntimeError("Owned engine remains alive; replacement refused")


async def monitor_children(proc):
    while proc.poll() is None:
        known = {c["pid"]: c for c in proc._owned_children}
        known.update({c["pid"]: c for c in descendants(proc.pid)})
        proc._owned_children = list(known.values())
        await asyncio.sleep(0.02)


def write(path, value, root, source):
    path.write_text(
        json.dumps(value, indent=2)
        .replace(str(root), "<scratch>")
        .replace(str(source), "<candidate-source>")
    )


def native_result(entry, tid):
    blocks = [
        b
        for b in entry.get("message", {}).get("content", [])
        if isinstance(b, dict)
        and b.get("type") == "tool_result"
        and b.get("tool_use_id") == tid
    ]
    if len(blocks) != 1:
        raise RuntimeError("Expected exactly one native result block")
    return {"tool_result": blocks[0], "toolUseResult": entry.get("toolUseResult")}


def find_actual(root, store, tid):
    found = []
    with store.connect() as db:
        actor = db.execute(
            "SELECT owner FROM native_calls WHERE id=?", (tid,)
        ).fetchone()[0]
    path = root / (actor.replace(":", "_") + ".db")
    with sqlite3.connect(path) as db:
        for (raw,) in db.execute("SELECT data FROM entries"):
            entry = json.loads(raw)
            if any(
                isinstance(b, dict) and b.get("tool_use_id") == tid
                for b in entry.get("message", {}).get("content", [])
            ):
                found.append(entry)
    if len(found) != 1:
        raise RuntimeError("Actual native outcome transcript missing before fault")
    return found[0]


async def worker(args):
    from temporalio.client import Client
    from temporalio.worker import Worker
    from tests.hybrid.native_replay import ReplayActivities
    from tests.hybrid.replay_store import ReplayStore
    from tests.hybrid.replay_workflow import NativeReplayWorkflow

    root = Path(args.root)
    env = {
        k: v
        for k, v in os.environ.items()
        if k.startswith(("ANTHROPIC_", "CLAUDE_", "DISABLE_"))
        or k.lower() == "no_proxy"
    }
    acts = ReplayActivities(root, env, ReplayStore(root, args.phase))
    client = await Client.connect(args.address)
    async with Worker(
        client,
        task_queue=args.queue,
        workflows=[NativeReplayWorkflow],
        activities=[acts.decide, acts.execute],
    ):
        print("worker ready", flush=True)
        await asyncio.Event().wait()


async def launch(args, root, address, queue, api, phase, number):
    from tests.helpers.fake_messages_api import engine_env

    log = root / f"worker-{number}.log"
    argv = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker",
        "--source-root",
        args.source_root,
        "--repo",
        args.repo,
        "--root",
        str(root),
        "--address",
        address,
        "--queue",
        queue,
        "--phase",
        phase,
    ]
    with log.open("wb") as out:
        proc = subprocess.Popen(
            argv,
            env={**os.environ, **engine_env(api, str(root / f"machine-{number}"))},
            stdout=out,
            stderr=subprocess.STDOUT,
        )
    proc._owned_children = []
    for _ in range(600):
        if proc.poll() is None:
            known = {c["pid"]: c for c in proc._owned_children}
            known.update({c["pid"]: c for c in descendants(proc.pid)})
            proc._owned_children = list(known.values())
        if "worker ready" in log.read_text(errors="replace"):
            proc._monitor = asyncio.create_task(monitor_children(proc))
            return proc
        if proc.poll() is not None:
            await stop(proc)
            raise RuntimeError(log.read_text(errors="replace"))
        await asyncio.sleep(0.1)
    await stop(proc)
    raise TimeoutError("Worker did not become ready")


async def run_case(args, base, scenario):
    from temporalio.testing import WorkflowEnvironment
    from temporalio.worker import Replayer
    from tests.helpers.fake_messages_api import FakeMessagesAPI, history_of
    from tests.hybrid.replay_models import ReplayState
    from tests.hybrid.replay_store import ReplayStore
    from tests.hybrid.replay_workflow import NativeReplayWorkflow

    root = base / scenario
    root.mkdir()
    store = ReplayStore(root)
    store.initialize("BEFORE\n")
    invalid = scenario == "native-error"
    emitted = {}

    def policy(body):
        _, _, outcomes = history_of(body)
        if any(h.is_error for h in outcomes):
            return [{"type": "text", "text": "NATIVE ERROR"}]
        names = {h.name for h in outcomes}
        if "Edit" in names:
            return [{"type": "text", "text": "EDIT DONE"}]
        name = "Read" if "Read" not in names else "Edit"
        tid = "original-read" if name == "Read" else "original-edit"
        arguments = {"file_path": str(root / "workspace" / "note.txt")}
        if name == "Edit":
            arguments.update(
                old_string="MISSING" if invalid else "BEFORE",
                new_string="AFTER",
                replace_all=False,
            )
        emitted[tid] = {"id": tid, "name": name, "input": arguments}
        return [{"type": "tool_use", **emitted[tid]}]

    api = FakeMessagesAPI(policy, primary_tools={"Read", "Edit"}).start()
    assert api.base_url.startswith("http://127.0.0.1:")
    env = await WorkflowEnvironment.start_local(dev_server_existing_path=args.server)
    workers, cleanup, report = [], [], None
    phase = (
        "Edit-after-write"
        if scenario == "unpublished-edit"
        else "Edit-after-commit-before-completion"
    )
    queue = "native-file-comparison-" + uuid.uuid4().hex
    session = str(uuid.uuid4())
    try:
        workers.append(
            await launch(
                args,
                root,
                env.client.service_client.config.target_host,
                queue,
                api,
                phase,
                1,
            )
        )
        handle = await env.client.start_workflow(
            NativeReplayWorkflow.run, ReplayState(session), id=queue, task_queue=queue
        )
        limit = time.monotonic() + 75
        while True:
            calls = store.decision(session, 1)
            if (
                calls
                and (row := store.execution(calls[0].id))
                and row["phase"]
                == ("executed" if scenario == "unpublished-edit" else "committed")
            ):
                break
            if time.monotonic() > limit:
                raise TimeoutError("Native Edit did not reach selected fault boundary")
            await asyncio.sleep(0.05)
        assert len(calls) == 1 and calls[0].name == "Edit"
        accepted = asdict(calls[0])
        assert store.receipt(calls[0])["block"] == {
            "type": "tool_use",
            **emitted[calls[0].id],
        }
        before_entry = find_actual(root, store, calls[0].id)
        before_native = native_result(before_entry, calls[0].id)
        before_file, before_durable = (
            (store.workspace / "note.txt").read_text(),
            store.durable_text(),
        )
        assert before_file == ("BEFORE\n" if invalid else "AFTER\n")
        assert before_durable == (
            "BEFORE\n" if invalid or scenario == "unpublished-edit" else "AFTER\n"
        )
        write(
            root / "fault-boundary.json",
            {
                "accepted_edit": accepted,
                "physical_file": before_file,
                "durable_file": before_durable,
                "actual_native_outcome": before_entry,
                "physical_sha256": bytes_digest(before_file),
                "durable_sha256": bytes_digest(before_durable),
            },
            base,
            Path(args.source_root),
        )
        with store.connect() as db:
            events_before = list(
                db.execute("SELECT id,phase,owner FROM native_events ORDER BY seq")
            )
        committed_before = sum(
            tid == calls[0].id and event == "committed"
            for tid, event, _ in events_before
        )
        assert committed_before == (0 if scenario == "unpublished-edit" else 1)
        assert (row["result"] is None) == (scenario == "unpublished-edit")
        requests_before = sum(
            any(t.get("name") in {"Read", "Edit"} for t in r.get("tools", []))
            for r in api.requests
        )
        assert requests_before == 2
        cleanup.append(await stop(workers[0]))
        shutil.rmtree(store.workspace)
        shutil.rmtree(root / "machine-1", ignore_errors=True)
        for path in root.glob("*.db"):
            if path != store.path:
                path.unlink()
        for path in root.glob("cache-*"):
            shutil.rmtree(path)
        workers.append(
            await launch(
                args,
                root,
                env.client.service_client.config.target_host,
                queue,
                api,
                "replacement",
                2,
            )
        )
        state = await asyncio.wait_for(handle.result(), 75)
        assert asdict(store.decision(session, 1)[0]) == accepted
        store.receipt(state.calls[-1])
        with store.connect() as db:
            published_entry = json.loads(
                db.execute(
                    "SELECT data FROM replay_entries WHERE id=?", (calls[0].id,)
                ).fetchone()[0]
            )
            events = list(
                db.execute("SELECT id,phase,owner FROM native_events ORDER BY seq")
            )
        published_native = native_result(published_entry, calls[0].id)
        if scenario != "unpublished-edit":
            assert before_native == published_native
        assert (
            before_native["tool_result"]
            == published_native["tool_result"]
            == state.results[calls[0].id]
        )
        mode = (store.workspace / "note.txt").stat().st_mode & 0o777
        assert mode == 0o640
        assert bool(state.results[calls[0].id].get("is_error")) == invalid
        assert "toolUseResult" in published_entry
        assert state.answer == ("NATIVE ERROR" if invalid else "EDIT DONE")
        assert (
            (store.workspace / "note.txt").read_text()
            == store.durable_text()
            == ("BEFORE\n" if invalid else "AFTER\n")
        )
        physical_edits = sum(
            tid == calls[0].id and event == "executed" for tid, event, _ in events
        )
        committed_edits = sum(
            tid == calls[0].id and event == "committed" for tid, event, _ in events
        )
        assert physical_edits == (2 if scenario == "unpublished-edit" else 1)
        assert committed_edits == 1
        requests = [
            r
            for r in api.requests
            if any(t.get("name") in {"Read", "Edit"} for t in r.get("tools", []))
        ]
        assert len(requests) == 3 and api.errors == []
        _, _, delivered = history_of(requests[-1])
        assert {h.id for h in delivered} == set(emitted) == set(state.results)
        history = await handle.fetch_history()
        write(
            root / "history.json",
            json.loads(history.to_json()),
            base,
            Path(args.source_root),
        )
        await Replayer(workflows=[NativeReplayWorkflow]).replay_workflow(history)
        schedules = [
            e.activity_task_scheduled_event_attributes.activity_id
            for e in history.events
            if e.HasField("activity_task_scheduled_event_attributes")
            and e.activity_task_scheduled_event_attributes.activity_type.name
            == "native_replay_execution"
        ]
        assert sorted(schedules) == ["tool-original-edit", "tool-original-read"]
        report = {
            "scenario": scenario,
            "accepted_edit_before": accepted,
            "accepted_edit_after": asdict(store.decision(session, 1)[0]),
            "before_file": before_file,
            "before_durable": before_durable,
            "before_physical_file_sha256": bytes_digest(before_file),
            "before_durable_file_sha256": bytes_digest(before_durable),
            "final_physical_file_sha256": bytes_digest(
                (store.workspace / "note.txt").read_text()
            ),
            "final_durable_file_sha256": bytes_digest(store.durable_text()),
            "final_file_mode": oct(mode),
            "final_file": store.durable_text(),
            "physical_edit_attempts": physical_edits,
            "committed_edit_outcomes": committed_edits,
            "original_native_hash": digest(before_native),
            "published_native_hash": digest(published_native),
            "native_metadata_equal": before_native == published_native,
            "original_tool_result_hash": digest(before_native["tool_result"]),
            "published_tool_result_hash": digest(published_native["tool_result"]),
            "original_carrier_hash": digest(before_entry),
            "published_carrier_hash": digest(published_entry),
            "model_requests": len(requests),
            "model_requests_before_fault": requests_before,
            "model_requests_after_fault": len(requests) - requests_before,
            "local_cached_execution_requests": sum(
                event == "cached-response" for _, event, _ in events
            ),
            "outcome_disposition": "first unpublished outcome discarded; real native Edit rerun after committed snapshot restoration, one replacement outcome published"
            if scenario == "unpublished-edit"
            else "original committed native result and metadata reused without another Edit execution",
            "activity_schedules": schedules,
            "answer": state.answer,
            "api_errors": api.errors,
            "history_replay": "PASS",
            "events_before_fault": events_before,
            "events_final": events,
            "host_controls": "Sequential Worker ownership and verified descendant termination are experimental prerequisites, not candidate production supervision",
        }
        write(
            root / "original-outcome.json", before_entry, base, Path(args.source_root)
        )
        write(
            root / "published-outcome.json",
            published_entry,
            base,
            Path(args.source_root),
        )
        write(root / "model-requests.json", requests, base, Path(args.source_root))
        write(
            root / "calls.json",
            [asdict(c) for c in state.calls],
            base,
            Path(args.source_root),
        )
        print(json.dumps(report), flush=True)
    except Exception as exc:
        report = {
            "scenario": scenario,
            "disposition": "FAILED or unsupported experiment boundary; no completion claim",
            "exception": type(exc).__name__ + ": " + str(exc),
            "traceback": traceback.format_exc(),
        }
        raise
    finally:
        for proc in workers:
            if proc.poll() is None:
                cleanup.append(await stop(proc))
        if report is not None:
            report["cleanup"] = cleanup
            write(root / "report.json", report, base, Path(args.source_root))
        await env.shutdown()
        api.stop()


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-root", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--root", required=True)
    p.add_argument("--server")
    p.add_argument("--worker", action="store_true")
    p.add_argument("--address")
    p.add_argument("--queue")
    p.add_argument("--phase")
    args = p.parse_args()
    sys.path.insert(0, args.source_root)
    if args.worker:
        await worker(args)
        return
    root = Path(args.root)
    if root.exists():
        p.error("--root must be fresh")
    for protected in (Path(args.source_root).resolve(), Path(args.repo).resolve()):
        if root.resolve().is_relative_to(protected) or protected.is_relative_to(
            root.resolve()
        ):
            p.error("--root must be disjoint from source closure and fork")
    if not args.server or not Path(args.server).is_file():
        p.error("--server must name an existing cached Temporal binary")
    for key in list(os.environ):
        if key.startswith(("ANTHROPIC_", "CLAUDE_", "HYBRID_")) or key.lower() in {
            "http_proxy",
            "https_proxy",
            "all_proxy",
        }:
            os.environ.pop(key, None)
    import claude_agent_sdk

    cli = Path(claude_agent_sdk.__file__).resolve().parent / "_bundled" / "claude"
    if not cli.is_file():
        p.error("Installed SDK bundled CLI absent; no download allowed")
    os.environ["HYBRID_CLI_PATH"] = str(cli)
    root.mkdir(parents=True)
    write(
        root / "versions.json",
        {
            k: importlib.metadata.version(k)
            for k in ["temporalio", "claude-agent-sdk", "temporalio-claude-agent-sdk"]
        },
        root,
        Path(args.source_root),
    )
    write(
        root / "invocation.json",
        {
            "cli_version": subprocess.run(
                [str(cli), "--version"], capture_output=True, text=True, check=True
            ).stdout.strip(),
            "cli_sha256": hashlib.sha256(cli.read_bytes()).hexdigest(),
            "server_sha256": hashlib.sha256(Path(args.server).read_bytes()).hexdigest(),
            "settings": {
                "tools": ["Read", "Edit"],
                "allowed_tools": ["Read", "Edit"],
                "permission_mode": "acceptEdits",
                "setting_sources": [],
                "mcp_servers": {},
                "strict_mcp_config": True,
            },
            "scope": "Pinned candidate probe settings; no governed production prevention claim",
        },
        root,
        Path(args.source_root),
    )
    for scenario in ["committed-edit", "unpublished-edit", "native-error"]:
        await run_case(args, root, scenario)


if __name__ == "__main__":
    asyncio.run(main())
