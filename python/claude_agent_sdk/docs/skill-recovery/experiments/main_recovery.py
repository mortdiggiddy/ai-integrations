"""Compare the pinned experimental recovery callback with isolated fake models."""

import argparse
import asyncio
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import subprocess
import sys
import traceback
import uuid
from dataclasses import asdict
from pathlib import Path


def record(path, value, root):
    path.write_text(json.dumps(value, indent=2).replace(str(root), "<scratch>"))


def load_supervision(path):
    spec = importlib.util.spec_from_file_location("experiment_supervision", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def environment_scrub():
    for key in list(os.environ):
        if key.startswith(
            (
                "ANTHROPIC_",
                "CLAUDE_",
                "HYBRID_",
                "OPENAI_",
                "AWS_",
                "GOOGLE_",
                "AZURE_",
                "BEDROCK_",
            )
        ) or key.lower() in {
            "http_proxy",
            "https_proxy",
            "all_proxy",
            "pythonpath",
            "pythonhome",
        }:
            os.environ.pop(key, None)


async def compatibility_worker(args):
    from tests.hybrid.engine import Burst
    from tests.hybrid.models import Attempt, Reply
    from tests.hybrid.store import TranscriptStore

    root = Path(args.root)
    env = {
        k: v
        for k, v in os.environ.items()
        if k.startswith(("ANTHROPIC_", "CLAUDE_", "DISABLE_"))
        or k.lower() == "no_proxy"
    }
    calls = []

    async def echo(call):
        calls.append(
            {
                "id": call.id,
                "name": call.name,
                "arguments": call.arguments,
                "transcript_uuid": call.transcript_uuid,
            }
        )
        return Reply("recorded echo outcome")

    burst = Burst(
        root,
        env,
        TranscriptStore(root / "store.db"),
        str(uuid.uuid4()),
        Attempt(0, 1, "compatibility-owner"),
        echo,
        recovery=True,
    )
    try:
        await burst.open()
        result = await asyncio.wait_for(burst.query("work"), 35)
        checkpoint = await burst.checkpoint()
        entries = await burst.store.load(burst.key)
        record(
            root / "compatibility.json",
            {
                "status": "PASS",
                "result": result.result,
                "calls": calls,
                "checkpoint": checkpoint,
                "cli_pid": burst.pid,
                "source_reported_cli": burst.version,
            },
            root,
        )
        record(root / "transcript.json", entries, root)
        assert len(calls) == 1 and calls[0]["id"] == "original-echo"
        assert calls[0]["name"] == "echo" and calls[0]["arguments"] == {"n": 7}
    except Exception as exc:
        record(
            root / "compatibility.json",
            {
                "status": "FAILED; stop matrix",
                "exception": type(exc).__name__ + ": " + str(exc),
                "traceback": traceback.format_exc(),
            },
            root,
        )
        raise
    finally:
        await burst.close()


async def launch_worker(args, root, api, mode, number=1, address=None, queue=None):
    from tests.helpers.fake_messages_api import engine_env

    supervision = load_supervision(args.supervision_helper)
    log = root / (mode + "-" + str(number) + ".log")
    argv = [
        args.python,
        str(Path(__file__).resolve()),
        "--worker",
        "--source-root",
        args.source_root,
        "--root",
        str(root),
        "--cli-path",
        args.cli_path,
        "--mode",
        mode,
        "--worker-number",
        str(number),
    ]
    if address:
        argv.extend(["--address", address, "--queue", queue])
    with log.open("wb") as out:
        proc = subprocess.Popen(
            argv,
            env={
                **os.environ,
                **engine_env(api, str(root / ("config-" + str(number)))),
            },
            stdout=out,
            stderr=subprocess.STDOUT,
        )
    proc._owned_children = []
    proc._monitor = asyncio.create_task(supervision.monitor_children(proc))
    return proc, supervision


async def compatibility(args, root):
    from tests.helpers.fake_messages_api import FakeMessagesAPI, history_of

    def model(body):
        _, _, results = history_of(body)
        if results:
            assert len(results) == 1 and results[0].id == "original-echo"
            assert (
                results[0].content == "recorded echo outcome"
                and not results[0].is_error
            )
            return [{"type": "text", "text": "DONE recorded result"}]
        return [
            {
                "type": "tool_use",
                "id": "original-echo",
                "name": "mcp__durable__echo",
                "input": {"n": 7},
            }
        ]

    api = FakeMessagesAPI(model).start()
    assert api.base_url.startswith("http://127.0.0.1:")
    proc = None
    try:
        proc, supervision = await launch_worker(args, root, api, "compatibility")
        deadline = asyncio.get_running_loop().time() + 50
        while proc.poll() is None:
            if asyncio.get_running_loop().time() > deadline:
                raise TimeoutError("Compatibility owner did not exit")
            await asyncio.sleep(0.05)
        if proc.returncode != 0:
            raise RuntimeError(
                (root / "compatibility-1.log").read_text(errors="replace")
            )
        report = json.loads((root / "compatibility.json").read_text())
        assert (
            report["status"] == "PASS" and len(api.requests) == 2 and api.errors == []
        )
        record(root / "model-requests.json", api.requests, root)
        return True
    finally:
        if proc is not None:
            cleanup = await supervision.stop(proc)
            record(root / "cleanup.json", cleanup, root)
        api.stop()


async def temporal_worker(args):
    from temporalio import activity
    from temporalio.client import Client
    from temporalio.worker import Worker
    from tests.hybrid.activities import HybridActivities
    from tests.hybrid.models import Call, Reply
    from tests.hybrid.store import TranscriptStore
    from tests.hybrid.workflows import HybridWorkflow

    root = Path(args.root)
    client = await Client.connect(args.address)
    env = {
        k: v
        for k, v in os.environ.items()
        if k.startswith(("ANTHROPIC_", "CLAUDE_", "DISABLE_"))
        or k.lower() == "no_proxy"
    }
    acts = HybridActivities(client, root, env, TranscriptStore(root / "store.db"))
    acts.recovery = True
    if args.worker_number == 1:
        acts.before_delivery = asyncio.Event()

    @activity.defn(name="hybrid_tool")
    async def logged_tool(call: Call) -> Reply:
        with (root / "tool-invocations.jsonl").open("a") as log:
            log.write(
                json.dumps({"id": call.id, "worker_number": args.worker_number}) + "\n"
            )
        if args.mode == "error":
            return Reply("synthetic recorded MCP error", True)
        return await acts.tool(call)

    async with Worker(
        client,
        task_queue=args.queue,
        workflows=[HybridWorkflow],
        activities=[acts.burst, logged_tool],
    ):
        print("worker ready", flush=True)
        await asyncio.Event().wait()


def read_records(path):
    return (
        [json.loads(line) for line in path.read_text().splitlines()]
        if path.exists()
        else []
    )


async def until(check, timeout=60):
    deadline = asyncio.get_running_loop().time() + timeout
    while asyncio.get_running_loop().time() < deadline:
        result = await check()
        if result:
            return result
        await asyncio.sleep(0.05)
    raise TimeoutError("Requested bounded condition did not arrive")


async def temporal_case(args, base, mode):
    from claude_agent_sdk import project_key_for_directory

    from temporalio.testing import WorkflowEnvironment
    from temporalio.worker import Replayer
    from tests.helpers.fake_messages_api import FakeMessagesAPI, history_of
    from tests.hybrid.models import State
    from tests.hybrid.store import TranscriptStore
    from tests.hybrid.workflows import HybridWorkflow

    root = base / mode
    root.mkdir()
    expected_input = {
        "n": 7,
        **({"approval": True} if mode in ("approve", "reject") else {}),
    }

    def model(body):
        _, _, results = history_of(body)
        if results:
            assert len(results) == 1 and results[0].id == "original-echo"
            return [{"type": "text", "text": "DONE recorded result"}]
        return [
            {
                "type": "tool_use",
                "id": "original-echo",
                "name": "mcp__durable__echo",
                "input": expected_input,
            }
        ]

    api = FakeMessagesAPI(model).start()
    environment = await WorkflowEnvironment.start_local(
        dev_server_existing_path=args.server
    )
    queue, session = "experimental-main-" + uuid.uuid4().hex, str(uuid.uuid4())
    procs, cleanup, report, handle = [], [], None, None
    store = TranscriptStore(root / "store.db")
    key = {"project_key": project_key_for_directory(str(root)), "session_id": session}
    try:
        proc, supervision = await launch_worker(
            args,
            root,
            api,
            mode,
            address=environment.client.service_client.config.target_host,
            queue=queue,
        )
        procs.append(proc)

        async def ready():
            if proc.poll() is not None:
                raise RuntimeError(
                    (root / (mode + "-1.log")).read_text(errors="replace")
                )
            return "worker ready" in (root / (mode + "-1.log")).read_text(
                errors="replace"
            )

        await until(ready)
        handle = await environment.client.start_workflow(
            HybridWorkflow.run, State(session, ["work"]), id=queue, task_queue=queue
        )

        async def boundary():
            snapshot = await handle.query(HybridWorkflow.snapshot)
            entry = snapshot.ledger.get("original-echo")
            return (
                snapshot
                if entry
                and (mode in ("approve", "reject") or entry.outcome is not None)
                else None
            )

        before = await until(boundary)
        entry = before.ledger["original-echo"]
        assert entry.call.name == "echo" and entry.call.arguments == expected_input
        original_identity = entry.call.identity()
        pending_entries = await store.load(key)
        assert pending_entries
        from claude_agent_sdk._internal.main_agent_recovery import pending_tool_uses

        unresolved, _ = pending_tool_uses(key, pending_entries)
        assert len(unresolved) == 1
        pending = unresolved[0]
        assert pending.id == "original-echo"
        assert pending.name == "mcp__durable__echo" and pending.input == expected_input
        assert (
            pending.key == key and pending.transcript_uuid == entry.call.transcript_uuid
        )
        assert len(api.requests) == 1
        record(root / "original-pending-transcript.json", pending_entries, base)
        record(root / "original-ledger.json", asdict(before), base)
        cleanup.append(await supervision.stop(proc))
        replacement, _ = await launch_worker(
            args,
            root,
            api,
            mode,
            2,
            environment.client.service_client.config.target_host,
            queue,
        )
        procs.append(replacement)
        if mode in ("approve", "reject"):

            async def registered():
                snapshot = await handle.query(HybridWorkflow.snapshot)
                return (
                    snapshot
                    if snapshot.attempts.get(0) and snapshot.attempts[0].number >= 2
                    else None
                )

            waiting = await until(registered)
            await asyncio.sleep(0.3)
            assert len(api.requests) == 1
            assert len(read_records(root / "cli-pids.jsonl")) == 1
            assert read_records(root / "tool-invocations.jsonl") == []
            assert waiting.ledger["original-echo"].approved is None
            approved = mode == "approve"
            await handle.execute_update(
                HybridWorkflow.review, ("original-echo", approved)
            )
            await handle.execute_update(
                HybridWorkflow.review, ("original-echo", approved)
            )
            try:
                await handle.execute_update(
                    HybridWorkflow.review, ("original-echo", not approved)
                )
            except Exception as exc:
                causes = []
                cause = exc
                while cause is not None and cause not in causes:
                    causes.append(cause)
                    cause = getattr(cause, "cause", None) or cause.__cause__
                assert any("conflicting approval" in str(c) for c in causes)
                conflicting_review = "refused"
            else:
                raise AssertionError("Conflicting approval was accepted")
        state = await asyncio.wait_for(handle.result(), 70)
        final = state.ledger["original-echo"]
        assert final.call.identity() == original_identity
        assert final.call.transcript_uuid == entry.call.transcript_uuid
        if entry.outcome:
            assert final.outcome == entry.outcome
        error = mode in ("error", "reject")
        assert final.outcome.is_error == error
        expected_block = {
            "type": "tool_result",
            "tool_use_id": "original-echo",
            "content": final.outcome.text,
            "is_error": error,
        }
        transcript = await store.load(key)
        blocks = [
            b
            for e in transcript
            if e.get("type") == "user"
            for b in e.get("message", {}).get("content", [])
            if isinstance(b, dict)
            and b.get("type") == "tool_result"
            and b.get("tool_use_id") == "original-echo"
        ]
        assert blocks == [expected_block]
        _, _, received = history_of(api.requests[-1])
        assert len(received) == 1
        assert received[0].id == "original-echo" and received[0].is_error == error
        raw_received = [
            b
            for message in api.requests[-1]["messages"]
            for b in message.get("content", [])
            if isinstance(b, dict) and b.get("type") == "tool_result"
        ]
        assert len(raw_received) == 1
        assert raw_received[0]["content"] == final.outcome.text
        assert len(api.requests) == 2 and api.errors == []
        invocations = read_records(root / "tool-invocations.jsonl")
        assert len(invocations) == (0 if mode == "reject" else 1)
        history = await handle.fetch_history()
        record(root / "history.json", json.loads(history.to_json()), base)
        scheduled = [
            e.activity_task_scheduled_event_attributes.activity_id
            for e in history.events
            if e.HasField("activity_task_scheduled_event_attributes")
            and e.activity_task_scheduled_event_attributes.activity_type.name
            == "hybrid_tool"
        ]
        assert scheduled == ([] if mode == "reject" else ["tool-original-echo"])
        await Replayer(workflows=[HybridWorkflow]).replay_workflow(history)
        report = {
            "mode": mode,
            "status": "PASS",
            "identity_before": asdict(entry.call),
            "identity_after": asdict(final.call),
            "original_host_outcome": asdict(entry.outcome) if entry.outcome else None,
            "published_outcome": asdict(final.outcome),
            "expected_recovery_block": expected_block,
            "stored_recovery_block": blocks[0],
            "model_received_result": raw_received[0],
            "unresolved_original_request": asdict(pending),
            "model_requests_before_replacement": 1,
            "model_requests_total": len(api.requests),
            "tool_invocations": invocations,
            "scheduled_tools": scheduled,
            "history_replay": "PASS",
            "approval_preflight": {
                "no_new_cli": True,
                "no_new_model_request": True,
                "duplicate_decision": "accepted",
                "conflicting_decision": conflicting_review,
            }
            if mode in ("approve", "reject")
            else None,
            "proof_scope": "Synthetic MCP echo outcomes and tuple approvals; no native effect metadata, signed decisions, protected claims or Bash effects",
        }
        record(root / "published-transcript.json", transcript, base)
        record(root / "model-requests.json", api.requests, base)
        record(root / "result-block.json", blocks[0], base)
        print(json.dumps(report), flush=True)
    except Exception as exc:
        report = {
            "mode": mode,
            "status": "FAILED; no completion claim",
            "exception": type(exc).__name__ + ": " + str(exc),
            "traceback": traceback.format_exc(),
        }
        if handle:
            record(
                root / "history.json",
                json.loads((await handle.fetch_history()).to_json()),
                base,
            )
        raise
    finally:
        for proc in procs:
            if proc.poll() is None:
                cleanup.append(await supervision.stop(proc))
        if report:
            report["cleanup"] = cleanup
            report["orphan_observed"] = any(c["survivors_after_kill"] for c in cleanup)
            record(root / "report.json", report, base)
        await environment.shutdown()
        api.stop()


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-root", required=True)
    p.add_argument("--root", required=True)
    p.add_argument("--cli-path", required=True)
    p.add_argument("--python", default=sys.executable)
    p.add_argument("--supervision-helper")
    p.add_argument("--worker", action="store_true")
    p.add_argument("--mode", default="compatibility")
    p.add_argument("--server")
    p.add_argument("--worker-number", type=int, default=1)
    p.add_argument("--address")
    p.add_argument("--queue")
    p.add_argument("--compatibility-only", action="store_true")
    args = p.parse_args()
    sys.path.insert(0, args.source_root)
    if args.worker:
        os.environ["HYBRID_CLI_PATH"] = args.cli_path
        if args.mode == "compatibility":
            await compatibility_worker(args)
        else:
            await temporal_worker(args)
        return
    if not args.supervision_helper:
        p.error("--supervision-helper must name the bounded native experiment helper")
    root = Path(args.root)
    if root.exists():
        p.error("--root must be fresh")
    if not Path(args.cli_path).is_file():
        p.error("--cli-path must name the unchanged installed CLI")
    environment_scrub()
    cli_hash = hashlib.sha256(Path(args.cli_path).read_bytes()).hexdigest()
    if cli_hash != "15e2d05148f801b5774032faad87e624ecd172e9903288bda448b892eb58fa07":
        p.error("CLI hash differs from the pinned comparison lane")
    if importlib.metadata.version("claude-agent-sdk") != "0.2.162":
        p.error("The experimental SDK must resolve from the disposable environment")
    root.mkdir(parents=True)
    record(
        root / "invocation.json",
        {
            "cli_sha256": cli_hash,
            "cli_path": args.cli_path,
            "python": sys.version,
            "python_prefix": sys.prefix,
            "source_root": args.source_root,
            "server_sha256": hashlib.sha256(Path(args.server).read_bytes()).hexdigest()
            if args.server
            else None,
            "paid_model_calls": False,
        },
        root,
    )
    record(
        root / "versions.json",
        {
            k: importlib.metadata.version(k)
            for k in ["claude-agent-sdk", "temporalio", "temporalio-claude-agent-sdk"]
        },
        root,
    )
    await compatibility(args, root)
    if not args.compatibility_only:
        if not args.server or not Path(args.server).is_file():
            p.error("--server must name an existing cached Temporal binary")
        for mode in ["success", "error", "approve", "reject"]:
            await temporal_case(args, root, mode)


if __name__ == "__main__":
    asyncio.run(main())
