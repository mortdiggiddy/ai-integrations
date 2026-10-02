"""Exercise disposable Ed25519 decisions against actual pending SDK calls."""

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
import traceback
import uuid
from dataclasses import asdict
from pathlib import Path

import main_recovery as helpers


async def worker(args):
    from host_approval_workflow import SignedApprovalWorkflow

    from temporalio import activity
    from temporalio.client import Client
    from temporalio.worker import Worker
    from temporalio.worker.workflow_sandbox import (
        SandboxedWorkflowRunner,
        SandboxRestrictions,
    )
    from tests.hybrid.activities import HybridActivities
    from tests.hybrid.models import Call, Reply
    from tests.hybrid.store import TranscriptStore

    root = Path(args.root)
    client = await Client.connect(
        args.address, identity="bounded-approval-worker-" + str(args.number)
    )
    env = {
        k: v
        for k, v in os.environ.items()
        if k.startswith(("ANTHROPIC_", "CLAUDE_", "DISABLE_"))
        or k.lower() == "no_proxy"
    }
    acts = HybridActivities(client, root, env, TranscriptStore(root / "store.db"))
    acts.recovery = True

    @activity.defn(name="hybrid_tool")
    async def tool(call: Call) -> Reply:
        with (root / "tool-invocations.jsonl").open("a") as stream:
            stream.write(json.dumps({"id": call.id, "worker": args.number}) + "\n")
        return await acts.tool(call)

    async with Worker(
        client,
        task_queue=args.queue,
        workflows=[SignedApprovalWorkflow],
        activities=[acts.burst, tool],
        workflow_runner=SandboxedWorkflowRunner(
            restrictions=SandboxRestrictions.default.with_passthrough_modules(
                "cryptography", "_cffi_backend"
            )
        ),
    ):
        print("worker ready", flush=True)
        await asyncio.Event().wait()


async def launch(args, root, api, address, queue, number):
    from tests.helpers.fake_messages_api import engine_env

    supervision = helpers.load_supervision(args.supervision_helper)
    log = root / ("worker-" + str(number) + ".log")
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker",
        "--source-root",
        args.source_root,
        "--root",
        str(root),
        "--cli-path",
        args.cli_path,
        "--address",
        address,
        "--queue",
        queue,
        "--number",
        str(number),
    ]
    with log.open("wb") as out:
        proc = subprocess.Popen(
            command,
            stdout=out,
            stderr=subprocess.STDOUT,
            env={
                **os.environ,
                **engine_env(api, str(root / ("config-" + str(number)))),
            },
        )
    proc._owned_children = []
    proc._monitor = asyncio.create_task(supervision.monitor_children(proc))

    async def ready():
        if proc.poll() is not None:
            raise RuntimeError(log.read_text(errors="replace"))
        return "worker ready" in log.read_text(errors="replace")

    await helpers.until(ready)
    return proc, supervision


async def run_case(args, base, approved):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from host_approval_workflow import SignedApprovalWorkflow, canonical, request_digest

    from temporalio.testing import WorkflowEnvironment
    from temporalio.worker import Replayer
    from temporalio.worker.workflow_sandbox import (
        SandboxedWorkflowRunner,
        SandboxRestrictions,
    )
    from tests.helpers.fake_messages_api import FakeMessagesAPI, history_of

    root = base / ("approve" if approved else "reject")
    root.mkdir()

    def model(body):
        _, _, results = history_of(body)
        if results:
            assert len(results) == 1 and results[0].id == "signed-echo"
            assert results[0].is_error == (not approved)
            return [{"type": "text", "text": "DONE signed decision"}]
        return [
            {
                "type": "tool_use",
                "id": "signed-echo",
                "name": "mcp__durable__echo",
                "input": {"n": 7, "approval": True},
            }
        ]

    api = FakeMessagesAPI(model).start()
    assert api.base_url.startswith("http://127.0.0.1:")
    environment = await WorkflowEnvironment.start_local(
        dev_server_existing_path=args.server, identity="bounded-approval-client"
    )
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw().hex()
    queue, session = "signed-comparison-" + uuid.uuid4().hex, str(uuid.uuid4())
    procs, cleanup, rejected = [], [], []
    handle, report = None, {"status": "FAILED; no completion claim"}
    try:
        address = environment.client.service_client.config.target_host
        proc, supervision = await launch(args, root, api, address, queue, 1)
        procs.append(proc)
        handle = await environment.client.start_workflow(
            SignedApprovalWorkflow.run,
            {"session": session, "public_key": public_key},
            id=queue,
            task_queue=queue,
        )

        async def pending():
            state = await handle.query(SignedApprovalWorkflow.snapshot)
            return state if "signed-echo" in state.ledger else None

        pending_state = await helpers.until(pending)
        accepted = pending_state.ledger["signed-echo"].call
        assert len(api.requests) == 1
        cleanup.append(await supervision.stop(proc))
        proc, _ = await launch(args, root, api, address, queue, 2)
        procs.append(proc)

        async def replaced():
            state = await handle.query(SignedApprovalWorkflow.snapshot)
            return state if state.attempts[0].number >= 2 else None

        await helpers.until(replaced)
        await asyncio.sleep(0.3)
        assert len(api.requests) == 1
        assert len(helpers.read_records(root / "cli-pids.jsonl")) == 1
        assert helpers.read_records(root / "tool-invocations.jsonl") == []
        now = int((await handle.describe()).start_time.timestamp())
        body = {
            "version": 1,
            "key_id": "experiment-key",
            "workflow": queue,
            "session": session,
            "id": accepted.id,
            "digest": request_digest(session, accepted),
            "approved": approved,
            "expires": now + 3600,
        }

        def sign(value):
            return {
                "body": value,
                "signature": private_key.sign(canonical(value)).hex(),
            }

        async def reject(name, token):
            from temporalio.client import WorkflowUpdateFailedError
            from temporalio.exceptions import ApplicationError

            before = len((await handle.fetch_history()).events)
            try:
                await asyncio.wait_for(
                    handle.execute_update(SignedApprovalWorkflow.review, token), 15
                )
            except WorkflowUpdateFailedError as exc:
                assert isinstance(exc.cause, ApplicationError), repr(exc.cause)
                if name == "unsigned legacy tuple":
                    assert (
                        exc.cause.type == "RuntimeError"
                        and str(exc.cause.message) == "Failed decoding arguments"
                    )
                    assert (
                        isinstance(exc.cause.cause, ApplicationError)
                        and exc.cause.cause.type == "TypeError"
                    )
                else:
                    assert exc.cause.type in {"ValueError", "InvalidSignature"}, repr(
                        exc.cause
                    )
                rejected.append(
                    {
                        "case": name,
                        "error": str(exc.cause),
                        "failure_type": exc.cause.type,
                        "history_before": before,
                    }
                )
            else:
                raise AssertionError("Invalid decision accepted: " + name)

        await reject("unsigned legacy tuple", [accepted.id, approved])
        await reject("forged signature", {"body": body, "signature": "00" * 64})
        for name, changes in (
            ("other workflow", {"workflow": "other"}),
            ("other session", {"session": "other"}),
            ("other call", {"id": "other"}),
            ("changed accepted input", {"digest": "00" * 32}),
            ("expired", {"expires": now - 1}),
            ("unknown key", {"key_id": "other"}),
            ("unsupported version", {"version": 0}),
        ):
            await reject(name, sign({**body, **changes}))
        assert len(api.requests) == 1
        assert helpers.read_records(root / "tool-invocations.jsonl") == []
        token = sign(body)
        await handle.execute_update(SignedApprovalWorkflow.review, token)
        await handle.execute_update(SignedApprovalWorkflow.review, token)
        await reject(
            "conflicting signed decision", sign({**body, "approved": not approved})
        )

        async def complete():
            return (await handle.query(SignedApprovalWorkflow.signed_state))[
                "completed"
            ]

        await helpers.until(complete)
        assert len(api.requests) == 2 and api.errors == []
        cleanup.append(await supervision.stop(proc))
        proc, _ = await launch(args, root, api, address, queue, 3)
        procs.append(proc)
        restored = await handle.query(SignedApprovalWorkflow.signed_state)
        assert restored == {"decisions": {accepted.id: approved}, "completed": True}
        await handle.execute_update(SignedApprovalWorkflow.review, token)
        await reject(
            "conflict after second replacement",
            sign({**body, "approved": not approved}),
        )
        assert len(api.requests) == 2
        await handle.execute_update(SignedApprovalWorkflow.finish_experiment)
        result = await asyncio.wait_for(handle.result(), 30)
        final = result.ledger[accepted.id]
        assert request_digest(session, final.call) == body["digest"]
        assert final.outcome.is_error == (not approved)
        tools = helpers.read_records(root / "tool-invocations.jsonl")
        assert len(tools) == (1 if approved else 0)
        history = await handle.fetch_history()
        await Replayer(
            workflows=[SignedApprovalWorkflow],
            workflow_runner=SandboxedWorkflowRunner(
                restrictions=SandboxRestrictions.default.with_passthrough_modules(
                    "cryptography", "_cffi_backend"
                )
            ),
        ).replay_workflow(history)
        helpers.record(root / "history.json", json.loads(history.to_json()), base)
        helpers.record(root / "model-requests.json", api.requests, base)
        helpers.record(root / "accepted-request.json", asdict(accepted), base)
        accepted_updates = [
            e
            for e in history.events
            if e.HasField("workflow_execution_update_accepted_event_attributes")
            and e.workflow_execution_update_accepted_event_attributes.accepted_request.input.name
            == "review"
        ]
        assert len(accepted_updates) == 3
        report = {
            "status": "PASS",
            "approved": approved,
            "public_key": public_key,
            "signed_token": token,
            "rejected": rejected,
            "accepted_review_updates": len(accepted_updates),
            "restored_signed_state": restored,
            "tool_invocations": tools,
            "model_requests_before_decision": 1,
            "model_requests_total": len(api.requests),
            "history_replay": "PASS",
            "final_outcome": asdict(final.outcome),
            "proof_scope": "Disposable Ed25519 verifier and exact main MCP request; cryptography and fixture Workflow imported through sandbox passthrough. No production gateway, key rotation, subclass security, Continue-As-New, unsigned migration or general executor proof. Harness supplies sequential ownership and cleanup.",
        }
    except Exception:
        report["traceback"] = traceback.format_exc()
        if handle:
            helpers.record(
                root / "history.json",
                json.loads((await handle.fetch_history()).to_json()),
                base,
            )
        raise
    finally:
        for proc in procs:
            if proc.poll() is None:
                cleanup.append(await supervision.stop(proc))
        report["cleanup"] = cleanup
        helpers.record(root / "report.json", report, base)
        await environment.shutdown()
        api.stop()
    print(
        json.dumps(
            {
                "status": report["status"],
                "approved": approved,
                "rejected": len(rejected),
            }
        ),
        flush=True,
    )


async def main():
    parser = argparse.ArgumentParser()
    for name in ("source-root", "root", "cli-path"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--server")
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--supervision-helper")
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--address")
    parser.add_argument("--queue")
    parser.add_argument("--number", type=int)
    args = parser.parse_args()
    sys.path.insert(0, args.source_root)
    if args.worker:
        os.environ["HYBRID_CLI_PATH"] = args.cli_path
        await worker(args)
        return
    helpers.environment_scrub()
    root = Path(args.root).resolve()
    if root.exists():
        parser.error("Root must be fresh")
    from verify_experimental_sdk import main as verify_install

    saved_argv = sys.argv
    try:
        sys.argv = ["verify", "--root", str(Path(sys.prefix).parent)]
        verify_install()
    finally:
        sys.argv = saved_argv
    assert importlib.metadata.version("cryptography") == "50.0.1"
    assert (
        hashlib.sha256(Path(args.cli_path).read_bytes()).hexdigest()
        == "15e2d05148f801b5774032faad87e624ecd172e9903288bda448b892eb58fa07"
    )
    assert (
        hashlib.sha256(Path(args.server).read_bytes()).hexdigest()
        == "eff36463f7c0fbfcfd50f117370fc582fe964912a62cf271b91af05447d1fdfe"
    )
    root.mkdir(parents=True)
    helpers.record(
        root / "invocation.json",
        {
            "python": sys.version,
            "sdk": "0.2.162",
            "temporal": importlib.metadata.version("temporalio"),
            "cryptography": "50.0.1",
            "cli_sha256": hashlib.sha256(Path(args.cli_path).read_bytes()).hexdigest(),
            "server_sha256": hashlib.sha256(Path(args.server).read_bytes()).hexdigest(),
            "paid_calls": False,
        },
        root,
    )
    await run_case(args, root, True)
    await run_case(args, root, False)
    if args.archive:
        if args.archive.exists():
            parser.error("Archive must be fresh")
        for source in root.rglob("*.json"):
            if any(
                part.startswith("config-") for part in source.relative_to(root).parts
            ):
                continue
            target = args.archive / source.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            text = (
                source.read_text()
                .replace(str(root), "<scratch>")
                .replace(args.source_root, "<candidate-source>")
            )
            text = text.replace(
                str(Path(__file__).resolve().parents[5]), "<repo>"
            ).replace(str(Path(sys.prefix).parent), "<installation>")
            target.write_text(text)


if __name__ == "__main__":
    asyncio.run(main())
