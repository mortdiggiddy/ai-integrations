"""Measure a disposable native Bash uncertainty park and lost recovery state."""

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import shlex
import socket
import sqlite3
import subprocess
import sys
import traceback
import uuid
from datetime import timedelta
from pathlib import Path

import main_recovery as helpers
import native_replay as supervision

from temporalio import activity, workflow
from temporalio.common import RetryPolicy


@workflow.defn
class ParkWorkflow:
    @workflow.run
    async def run(self, inputs: dict) -> None:
        self.state = {"phase": "running", "reason": None}
        refusal = await workflow.execute_activity(
            "bounded_native_bash",
            inputs,
            start_to_close_timeout=timedelta(seconds=90),
            heartbeat_timeout=timedelta(seconds=2),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1), maximum_attempts=3
            ),
        )
        self.state = {"phase": "parked", "reason": refusal}
        await workflow.wait_condition(lambda: False)

    @workflow.query
    def snapshot(self) -> dict:
        return self.state


class Refusal(RuntimeError):
    pass


def save(path, data):
    path.write_text(json.dumps(data, indent=2))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


async def execute(inputs, root, cli, number):
    from claude_agent_sdk import (
        ClaudeAgentOptions,
        ClaudeSDKClient,
        project_key_for_directory,
    )
    from claude_agent_sdk._internal.main_agent_recovery import pending_tool_uses

    from tests.hybrid.store import TranscriptStore

    session = inputs["session"]
    key = {"project_key": project_key_for_directory(str(root)), "session_id": session}
    store = TranscriptStore(root / "store.db")
    marker = root / "workspace" / "marker.txt"
    command = "printf 'EFFECT\\n' >> " + shlex.quote(str(marker)) + "; sleep 300"
    expected = {
        "id": "original-bash",
        "name": "Bash",
        "input": {"command": command, "timeout": 600000},
    }
    env = {
        k: v
        for k, v in os.environ.items()
        if k.startswith(("ANTHROPIC_", "CLAUDE_", "DISABLE_"))
        or k.lower() == "no_proxy"
    }
    if number > 1 or activity.info().attempt > 1:
        try:
            if not (root / "accepted.json").exists():
                raise Refusal("accepted request missing")
            accepted = json.loads((root / "accepted.json").read_text())
            if accepted != {**expected, "session": session}:
                raise Refusal("accepted request changed")
            entries = await store.load(key)
            if not entries:
                raise Refusal("conversation transcript missing")
            pending, _ = pending_tool_uses(key, entries)
            if len(pending) != 1 or (
                pending[0].id,
                pending[0].name,
                pending[0].input,
            ) != (expected["id"], expected["name"], expected["input"]):
                raise Refusal("conversation request identity missing or changed")
            if not marker.exists():
                raise Refusal("required filesystem state missing")
            manifest_path = root / "manifest.json"
            if not manifest_path.exists():
                raise Refusal("filesystem manifest missing")
            manifest = json.loads(manifest_path.read_text())
            if manifest != {"marker_sha256": sha(marker), "generation": 1}:
                raise Refusal("filesystem state or generation changed")
            claim_path = root / "claim.json"
            if not claim_path.exists():
                raise Refusal("required claim missing")
            if json.loads(claim_path.read_text()) != {**expected, "session": session}:
                raise Refusal("claim identity changed")

            async def recover(pending):
                raise Refusal("Bash outcome absent after claimed actual effect")

            client = ClaudeSDKClient(
                options=ClaudeAgentOptions(
                    cwd=str(root),
                    cli_path=cli,
                    env=env,
                    tools=["Bash"],
                    allowed_tools=["Bash"],
                    setting_sources=[],
                    permission_mode="default",
                    session_store=store,
                    session_store_flush="eager",
                    resume=session,
                    recover_pending_tool=recover,
                    parallel_tool_recovery=False,
                )
            )
            try:
                await client.connect()
                raise AssertionError("Ambiguous recovery started a CLI")
            finally:
                await client.disconnect()
        except Refusal as exc:
            save(root / "refusal.json", {"reason": str(exc), "worker": number})
            return str(exc)
    save(root / "accepted.json", {**expected, "session": session})
    save(root / "claim.json", {**expected, "session": session})
    client = ClaudeSDKClient(
        options=ClaudeAgentOptions(
            cwd=str(root),
            cli_path=cli,
            env=env,
            tools=["Bash"],
            allowed_tools=["Bash"],
            setting_sources=[],
            permission_mode="default",
            session_store=store,
            session_store_flush="eager",
            session_id=session,
        )
    )
    await client.connect()
    save(root / "cli.json", supervision.identity(client._transport._process.pid))
    await client.query("Run the one requested harmless scratch marker command.")

    async def consume():
        async for _ in client.receive_messages():
            pass

    reader = asyncio.create_task(consume())
    try:
        while True:
            activity.heartbeat("native effect pending")
            if marker.exists() and marker.read_text() == "EFFECT\n":
                entries = await store.load(key)
                if entries:
                    pending, _ = pending_tool_uses(key, entries)
                    if len(pending) == 1 and pending[0].id == "original-bash":
                        save(
                            root / "manifest.json",
                            {"marker_sha256": sha(marker), "generation": 1},
                        )
                        save(
                            root / "boundary.json",
                            {
                                "pending": True,
                                "effect_lines": 1,
                                "outcome_published": False,
                            },
                        )
            if reader.done():
                await reader
                raise AssertionError("Native Bash completed before Worker loss")
            await asyncio.sleep(0.1)
    finally:
        reader.cancel()
        await client.disconnect()


async def worker(args):
    from claude_agent_sdk._internal.transport.subprocess_cli import (
        SubprocessCLITransport,
    )

    from temporalio.client import Client
    from temporalio.worker import Worker

    client = await Client.connect(
        args.address, identity=f"bounded-native-worker-{args.number}"
    )
    original_connect = SubprocessCLITransport.connect

    async def observed_connect(transport):
        with (Path(args.root) / "transport-starts.jsonl").open("a") as log:
            log.write(json.dumps({"worker": args.number}) + "\n")
        return await original_connect(transport)

    SubprocessCLITransport.connect = observed_connect

    @activity.defn(name="bounded_native_bash")
    async def run(inputs: dict) -> str:
        async def heartbeat():
            while True:
                activity.heartbeat("bounded adapter active")
                await asyncio.sleep(0.2)

        heartbeats = asyncio.create_task(heartbeat())
        try:
            return await execute(inputs, Path(args.root), args.cli, args.number)
        finally:
            heartbeats.cancel()

    async with Worker(
        client, task_queue=args.queue, workflows=[ParkWorkflow], activities=[run]
    ):
        print("worker ready", flush=True)
        await asyncio.Event().wait()


async def launch(args, root, api, env, queue, number):
    from tests.helpers.fake_messages_api import engine_env

    argv = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker",
        "--root",
        str(root),
        "--cli",
        args.cli,
        "--source-root",
        args.source_root,
        "--server",
        args.server,
        "--number",
        str(number),
        "--address",
        env.client.service_client.config.target_host,
        "--queue",
        queue,
    ]
    log = root / f"worker-{number}.log"
    with log.open("wb") as output:
        proc = subprocess.Popen(
            argv,
            env={**os.environ, **engine_env(api, str(root / f"config-{number}"))},
            stdout=output,
            stderr=subprocess.STDOUT,
        )
    proc._owned_children = []
    proc._monitor = asyncio.create_task(supervision.monitor_children(proc))

    async def ready():
        if proc.poll() is not None:
            raise RuntimeError(log.read_text())
        return "worker ready" in log.read_text()

    try:
        await helpers.until(ready)
    except BaseException:
        await supervision.stop(proc)
        raise
    return proc


async def case(args, base, mode):
    from temporalio.client import Client
    from temporalio.testing import WorkflowEnvironment
    from temporalio.worker import Replayer
    from tests.helpers.fake_messages_api import FakeMessagesAPI, history_of

    root = base / mode
    root.mkdir()
    (root / "workspace").mkdir()
    marker = root / "workspace" / "marker.txt"
    command = "printf 'EFFECT\\n' >> " + shlex.quote(str(marker)) + "; sleep 300"

    def model(body):
        _, _, outcomes = history_of(body)
        if outcomes:
            raise AssertionError("Tool fallback or continuation reached model")
        return [
            {
                "type": "tool_use",
                "id": "original-bash",
                "name": "Bash",
                "input": {"command": command, "timeout": 600000},
            }
        ]

    api = FakeMessagesAPI(model, primary_tools={"Bash"}).start()
    env = await WorkflowEnvironment.start_local(dev_server_existing_path=args.server)
    controller = await Client.connect(
        env.client.service_client.config.target_host,
        identity="bounded-native-comparison",
    )
    queue = "bounded-native-park-" + uuid.uuid4().hex
    workers, cleanup, handle = [], [], None
    try:
        workers.append(await launch(args, root, api, env, queue, 1))
        handle = await controller.start_workflow(
            ParkWorkflow.run, {"session": str(uuid.uuid4())}, id=queue, task_queue=queue
        )

        async def boundary():
            return (root / "boundary.json").exists()

        await helpers.until(boundary, 75)
        assert len(api.requests) == 1 and marker.read_text() == "EFFECT\n"
        cleanup.append(await supervision.stop(workers[0]))
        if mode in (
            "missing-request",
            "missing-claims",
            "missing-manifest",
            "missing-filesystem",
        ):
            target = {
                "missing-request": root / "accepted.json",
                "missing-claims": root / "claim.json",
                "missing-manifest": root / "manifest.json",
                "missing-filesystem": marker,
            }[mode]
            target.unlink()
        elif mode == "changed-filesystem":
            marker.write_text("CHANGED\n")
        elif mode == "missing-transcript":
            with sqlite3.connect(root / "store.db") as db:
                db.execute("DELETE FROM entries")
        elif mode == "changed-request":
            value = json.loads((root / "accepted.json").read_text())
            value["input"]["command"] = "different harmless request"
            save(root / "accepted.json", value)
        workers.append(await launch(args, root, api, env, queue, 2))

        async def parked():
            state = await handle.query(ParkWorkflow.snapshot)
            return state if state["phase"] == "parked" else None

        state = await helpers.until(parked)
        expected = {
            "ambiguous-bash": "Bash outcome absent after claimed actual effect",
            "missing-request": "accepted request missing",
            "changed-request": "accepted request changed",
            "missing-transcript": "conversation transcript missing",
            "missing-filesystem": "required filesystem state missing",
            "changed-filesystem": "filesystem state or generation changed",
            "missing-claims": "required claim missing",
            "missing-manifest": "filesystem manifest missing",
        }[mode]
        assert state["reason"] == expected
        cleanup.append(await supervision.stop(workers[1]))
        workers.append(await launch(args, root, api, env, queue, 3))
        assert await helpers.until(parked) == state
        await asyncio.sleep(0.5)
        assert len(api.requests) == 1 and api.errors == []
        starts = [
            json.loads(line)
            for line in (root / "transport-starts.jsonl").read_text().splitlines()
        ]
        assert starts == [{"worker": 1}]
        if mode not in ("missing-filesystem", "changed-filesystem"):
            assert marker.read_text() == "EFFECT\n"
        with sqlite3.connect(root / "store.db") as db:
            transcript = [
                json.loads(row[0])
                for row in db.execute("SELECT data FROM entries ORDER BY seq")
            ]
        results = [
            block
            for entry in transcript
            for block in entry.get("message", {}).get("content", [])
            if isinstance(block, dict) and block.get("type") == "tool_result"
        ]
        assert results == []
        history = await handle.fetch_history()
        await Replayer(workflows=[ParkWorkflow]).replay_workflow(history)
        save(root / "history.json", json.loads(history.to_json()))
        save(root / "model-requests.json", api.requests)
        save(
            root / "report.json",
            {
                "status": "PASS",
                "case": mode,
                "park": state,
                "history_replay": "PASS",
                "actual_initial_bash_effects": 1,
                "replacement_model_requests": 0,
                "replacement_cli_spawns": 0,
                "published_tool_results": 0,
                "second_replacement_park_unchanged": True,
                "transport_start_events": starts,
                "claim": "Disposable host preflight plus Workflow state owns refusal; candidate SDK alone does not provide this contract",
                "limits": "Same host injected loss; no distributed storage, fencing, remote effect, arbitrary child containment or resolution procedure proved",
            },
        )
    except BaseException as exc:
        save(
            root / "report.json",
            {
                "status": "FAILED; no completion claim",
                "case": mode,
                "exception": type(exc).__name__ + ": " + str(exc),
                "traceback": traceback.format_exc(),
            },
        )
        if handle is not None:
            save(
                root / "history.json",
                json.loads((await handle.fetch_history()).to_json()),
            )
        raise
    finally:
        for proc in workers:
            if proc.poll() is None:
                cleanup.append(await supervision.stop(proc))
        save(root / "cleanup.json", cleanup)
        await env.shutdown()
        api.stop()


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--cli", required=True)
    parser.add_argument("--server", required=True)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--address")
    parser.add_argument("--queue")
    parser.add_argument("--number", type=int, default=1)
    parser.add_argument("--archive")
    parser.add_argument("--normalize-archive", action="store_true")
    args = parser.parse_args()
    sys.path.insert(0, args.source_root)
    if args.worker:
        await worker(args)
        return
    helpers.environment_scrub()
    subprocess.run(
        [
            sys.executable,
            str(Path(__file__).parent / "verify_experimental_sdk.py"),
            "--root",
            str(Path(sys.prefix).parent),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert importlib.metadata.version("claude-agent-sdk") == "0.2.162"
    assert importlib.metadata.version("temporalio") == "1.33.0"
    assert (
        sha(Path(args.cli))
        == "15e2d05148f801b5774032faad87e624ecd172e9903288bda448b892eb58fa07"
    )
    assert (
        sha(Path(args.server))
        == "eff36463f7c0fbfcfd50f117370fc582fe964912a62cf271b91af05447d1fdfe"
    )
    manifest = json.loads(
        (Path(__file__).parent / "results/native-source-manifest.json").read_text()
    )
    for entry in manifest["files"]:
        assert sha(Path(args.source_root) / entry["relative_path"]) == entry["sha256"]
    root = Path(args.root)
    for protected in (
        Path(__file__).resolve().parents[5],
        Path(args.source_root).resolve(),
    ):
        if root.resolve().is_relative_to(protected) or protected.is_relative_to(
            root.resolve()
        ):
            raise RuntimeError("Scratch root must be disjoint from fork and source")
    if args.archive and not Path(args.archive).resolve().is_relative_to(
        Path(__file__).parent.resolve() / "results" / "host-park"
    ):
        raise RuntimeError("Archive must be under the bounded host-park results tree")
    if args.normalize_archive:
        if not args.archive or not root.is_dir():
            raise RuntimeError(
                "Normalization needs an existing scratch root and archive"
            )
        archive_results(root, Path(args.archive), existing=True)
        return
    root.mkdir(parents=True, exist_ok=False)
    save(
        root / "invocation.json",
        {
            "sdk_version": "0.2.162",
            "python": sys.version,
            "cli_sha256": sha(Path(args.cli)),
            "server_sha256": sha(Path(args.server)),
            "source_revision": manifest["revision"],
            "paid_model_calls": False,
        },
    )
    for mode in [
        "ambiguous-bash",
        "missing-request",
        "changed-request",
        "missing-transcript",
        "missing-filesystem",
        "changed-filesystem",
        "missing-claims",
        "missing-manifest",
    ]:
        await case(args, root, mode)
        print(mode + " PASS", flush=True)
    if args.archive:
        archive_results(root, Path(args.archive))


def archive_results(root, archive, existing=False):
    archive.mkdir(parents=True, exist_ok=existing)
    for path in root.rglob("*.json"):
        if path.name not in {
            "report.json",
            "history.json",
            "model-requests.json",
            "cleanup.json",
            "invocation.json",
            "boundary.json",
            "refusal.json",
        }:
            continue
        destination = archive / path.relative_to(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            path.read_text()
            .replace(str(root), "<scratch>")
            .replace(socket.gethostname(), "<host>")
        )
    reports = [
        json.loads(path.read_text()) for path in sorted(archive.glob("*/report.json"))
    ]
    save(
        archive / "summary.json",
        {
            "status": "PASS"
            if len(reports) == 8 and all(r["status"] == "PASS" for r in reports)
            else "INCOMPLETE",
            "cases": reports,
        },
    )


if __name__ == "__main__":
    asyncio.run(main())
