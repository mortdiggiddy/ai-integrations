"""Exercise installed defer recovery against a local fake model and Temporal server."""

import argparse
import asyncio
import json
import os
import signal
import sys
import uuid
from collections import Counter
from pathlib import Path

SCRATCH_ROOT = ""
PLUGIN_ROOT = ""


def write_record(path, value):
    text = json.dumps(value, indent=2)
    text = text.replace(SCRATCH_ROOT, "<scratch>").replace(PLUGIN_ROOT, "<repo>")
    path.write_text(text)


def process_identity(pid):
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
        process_identity(int(p.name))
        for p in Path("/proc").iterdir()
        if p.name.isdigit()
    ]
    owned = {pid}
    result = []
    while True:
        found = [
            p for p in snapshot if p and p["parent"] in owned and p["pid"] not in owned
        ]
        if not found:
            return result
        result.extend(found)
        owned.update(p["pid"] for p in found)


async def account_children(inventory):
    for child in inventory:
        now = process_identity(child["pid"])
        if now and now["start_ticks"] == child["start_ticks"] and now["state"] != "Z":
            os.kill(child["pid"], signal.SIGKILL)
    for _ in range(40):
        states = [process_identity(p["pid"]) for p in inventory]
        active = [
            now
            for old, now in zip(inventory, states)
            if now and now["start_ticks"] == old["start_ticks"] and now["state"] != "Z"
        ]
        if not active:
            return {"remaining_active": [], "observed_states": states}
        await asyncio.sleep(0.05)
    return {"remaining_active": active, "observed_states": states}


async def results(root):
    from temporalio.claude_agent_sdk import (
        ClaudeAgentSdkRunner,
        FileSessionStore,
        SegmentInput,
        ToolOutcome,
        ToolSpec,
    )
    from tests.helpers.fake_messages_api import FakeMessagesAPI, engine_env, history_of

    reports = []
    for mode in (
        "success",
        "error",
        "changed-id",
        "missing-checkpoint",
        "missing-store",
        "competing-resume",
    ):
        work = root / mode
        work.mkdir(parents=True, exist_ok=True)
        seen = []

        def decide(body):
            uses, _, history = history_of(body)
            if not uses:
                return [
                    {
                        "type": "tool_use",
                        "id": "toolu_exact_1",
                        "name": "mcp__durable__probe",
                        "input": {"nested": {"b": 2, "a": 1}},
                    }
                ]
            seen.extend(
                [
                    {"id": h.id, "content": h.content, "is_error": h.is_error}
                    for h in history
                ]
            )
            return [{"type": "text", "text": "FINAL: observed stored outcome"}]

        api = FakeMessagesAPI(decide).start()
        assert api.base_url.startswith("http://127.0.0.1:")
        runner = ClaudeAgentSdkRunner(
            session_store=FileSessionStore(work / "store"),
            cwd=str(work),
            env=engine_env(api, str(work / "cfg")),
        )
        tools = [ToolSpec("probe", "Probe stored outcomes", {"type": "object"})]
        report = {"mode": mode}
        try:
            first = await asyncio.wait_for(
                runner.run(
                    SegmentInput(
                        session_id=str(uuid.uuid4()), prompt="Probe once", tools=tools
                    ),
                    1,
                ),
                35,
            )
            report["lane"] = "legacy MCP defer runner; tool_policy unset"
            report["first"] = {
                "id": first.deferred.id if first.deferred else None,
                "name": first.deferred.name if first.deferred else None,
                "input": first.deferred.input if first.deferred else None,
                "checkpoint": first.checkpoint,
                "error": first.error,
                "stub_calls": runner.stub_calls,
            }
            assert first.deferred is not None
            value = {"recorded": "exact payload", "nested": [1, {"value": "kept"}]}
            continuation = SegmentInput(
                session_id=first.session_id,
                prompt=None,
                tools=tools,
                checkpoint=None if mode == "missing-checkpoint" else first.checkpoint,
                injected={
                    "wrong-id"
                    if mode == "changed-id"
                    else first.deferred.id: ToolOutcome(value, is_error=mode == "error")
                },
                segment_index=1,
            )
            if mode == "missing-store":
                runner = ClaudeAgentSdkRunner(
                    session_store=FileSessionStore(work / "empty-store"),
                    cwd=str(work),
                    env=engine_env(api, str(work / "cfg-empty")),
                )
            if mode == "competing-resume":
                outcomes = await asyncio.wait_for(
                    asyncio.gather(
                        runner.run(continuation, 1),
                        runner.run(continuation, 1),
                        return_exceptions=True,
                    ),
                    30,
                )
                report["competing"] = [
                    {"exception": type(x).__name__ + ": " + str(x)}
                    if isinstance(x, BaseException)
                    else {
                        "result": x.result,
                        "error": x.error,
                        "deferred": x.deferred.id if x.deferred else None,
                    }
                    for x in outcomes
                ]
                successes = sum(
                    not isinstance(x, BaseException) and not x.is_error
                    for x in outcomes
                )
                report["disposition"] = (
                    "FAIL: two successful concurrent continuations, no exclusive owner"
                    if successes == 2
                    else "observed only; no host ownership lease or side effect executor tested"
                )
                continue
            second = await asyncio.wait_for(runner.run(continuation, 1), 25)
            report["second"] = {
                "result": second.result,
                "error": second.error,
                "deferred": second.deferred.id if second.deferred else None,
                "stub_calls": runner.stub_calls,
            }
            if mode in ("success", "error"):
                assert seen == [
                    {
                        "id": "toolu_exact_1",
                        "content": value,
                        "is_error": mode == "error",
                    }
                ]
                assert first.deferred.name == "probe"
                assert first.deferred.input == {"nested": {"a": 1, "b": 2}}
                assert (
                    not second.is_error
                    and second.result == "FINAL: observed stored outcome"
                )
                assert runner.stub_calls == 0
                report["disposition"] = (
                    "PASS: exact recorded payload, request ID and error bit retained"
                )
            if mode == "changed-id":
                report["disposition"] = (
                    "FAIL: malformed result identity reached another model request before final runner refusal"
                    if len(api.requests) > 1
                    else "malformed identity refused before model continuation"
                )
        except AssertionError:
            raise
        except Exception as exc:
            if mode not in ("missing-checkpoint", "missing-store"):
                raise
            report["exception"] = type(exc).__name__ + ": " + str(exc)
            report["disposition"] = (
                "unsupported malformed or unavailable checkpoint state; explicit failure observed"
            )
        finally:
            report["observed_outcomes"] = seen
            report["api_errors"] = api.errors
            report["model_requests"] = len(api.requests)
            report["continuation_model_requests"] = max(0, len(api.requests) - 1)
            write_record(work / "model-requests.json", api.requests)
            api.stop()
            assert api.errors == []
            reports.append(report)
            print(json.dumps(report), flush=True)
    write_record(root / "result-reuse.json", reports)


async def replacement(root, server, inflight=False, orphan=False):
    from temporalio.testing import WorkflowEnvironment
    from tests.conftest import wait_for_approval
    from tests.helpers.fake_messages_api import engine_env, start_with_policy
    from tests.refund import shop
    from tests.refund.policy import refund_policy
    from tests.refund.workflows import MANAGER, RefundAgentWorkflow
    from tests.test_crash import kill, start_worker
    from tests.test_workflow_engine import hang_on_request

    work = root / "replacement"
    work.mkdir(parents=True, exist_ok=True)
    os.environ["SHOP_DIR"] = str(work / "shop")
    api = start_with_policy(refund_policy)
    assert api.base_url.startswith("http://127.0.0.1:")
    arrived, release = (
        hang_on_request(api, 1 if orphan else 2) if inflight or orphan else (None, None)
    )
    workers = []
    child_inventory = []
    report = None
    env = await WorkflowEnvironment.start_local(dev_server_existing_path=server)
    queue = "recovery-comparison-" + uuid.uuid4().hex
    shared = {
        "SHOP_DIR": os.environ["SHOP_DIR"],
        "SESSION_DIR": str(work / "sessions"),
        "ENGINE_CWD": str(work),
    }
    try:
        workers.append(
            await start_worker(
                env.client.service_client.config.target_host,
                queue,
                {**shared, **engine_env(api, str(work / "cfg1"))},
                work / "w1.log",
                real=True,
            )
        )
        handle = await env.client.start_workflow(
            RefundAgentWorkflow.run,
            "Order A-1001 arrived broken, I want my money back.",
            id=queue,
            task_queue=queue,
        )
        if inflight or orphan:
            assert await asyncio.to_thread(arrived.wait, 120)
            pending1 = None
        else:
            pending1 = await wait_for_approval(handle, timeout=120)
            assert pending1 is not None
        calls_before = len(api.requests)
        assert shop.executions("issue_refund") == []
        child_inventory = descendants(workers[0].pid)
        kill(workers[0])
        await asyncio.sleep(0.2)
        survivors = [
            now
            for p in child_inventory
            if (now := process_identity(p["pid"]))
            and now["start_ticks"] == p["start_ticks"]
            and now["state"] != "Z"
        ]
        if inflight or orphan:
            before_replacement_cleanup = await account_children(survivors)
            if before_replacement_cleanup["remaining_active"]:
                raise RuntimeError(
                    "Verified experiment descendants remain active; replacement refused"
                )
            release.set()
        if orphan:
            await handle.cancel()
            history = await handle.fetch_history()
            (work / "history.json").write_text(
                history.to_json()
                .replace(SCRATCH_ROOT, "<scratch>")
                .replace(PLUGIN_ROOT, "<repo>")
            )
            report = {
                "lane": "legacy MCP defer runner; tool_policy unset",
                "old_worker_descendants": child_inventory,
                "surviving_descendants_after_worker_kill": survivors,
                "model_requests": len(api.requests),
                "tool_executions": shop.read("executions.jsonl"),
                "replacement_started": False,
                "disposition": "FAIL: Worker death leaves engine descendant alive; experiment terminated verified owned orphan"
                if survivors
                else "No surviving engine descendant observed at sample",
            }
            report["cleanup_before_replacement"] = before_replacement_cleanup
            assert not report["tool_executions"]
            write_record(work / "report.json", report)
            write_record(work / "model-requests.json", api.requests)
            print(json.dumps(report), flush=True)
            return
        workers.append(
            await start_worker(
                env.client.service_client.config.target_host,
                queue,
                {**shared, **engine_env(api, str(work / "cfg2"))},
                work / "w2.log",
                real=True,
            )
        )
        pending2 = await wait_for_approval(handle, timeout=120)
        assert pending2 is not None
        if not inflight:
            assert pending1 == pending2
            assert len(api.requests) == calls_before
        requests_at_replacement = len(api.requests)
        assert shop.executions("issue_refund") == []
        await handle.execute_update(
            RefundAgentWorkflow.review, args=[pending2["id"], True, MANAGER]
        )
        result = await asyncio.wait_for(handle.result(), 120)
        history = await handle.fetch_history()
        (work / "history.json").write_text(
            history.to_json()
            .replace(SCRATCH_ROOT, "<scratch>")
            .replace(PLUGIN_ROOT, "<repo>")
        )
        kinds = Counter()
        for event in history.events:
            if event.HasField("activity_task_scheduled_event_attributes"):
                kinds[
                    event.activity_task_scheduled_event_attributes.activity_type.name
                ] += 1
        report = {
            "pending_before": pending1,
            "pending_after": pending2,
            "model_requests_while_replacing": requests_at_replacement - calls_before,
            "model_requests_before_approval": calls_before,
            "model_requests_total": len(api.requests),
            "result": result,
            "activity_scheduled_counts": dict(kinds),
            "refund_executions": len(shop.executions("issue_refund")),
            "refund_records": len(shop.read("refunds.jsonl")),
            "api_errors": api.errors,
            "worker_pids": [w.pid for w in workers],
        }
        report["killed_while_model_request_inflight"] = inflight
        report["old_worker_descendants"] = child_inventory
        report["surviving_descendants_after_worker_kill"] = survivors
        if inflight:
            report["cleanup_before_replacement"] = before_replacement_cleanup
        assert report["refund_executions"] == report["refund_records"] == 1
        assert not api.errors
        write_record(work / "report.json", report)
        write_record(work / "model-requests.json", api.requests)
        print(json.dumps(report), flush=True)
    finally:
        if release is not None:
            release.set()
        for worker in workers:
            if worker.poll() is None:
                kill(worker)
        cleanup = await account_children(child_inventory)
        if report is not None:
            report["final_cleanup"] = cleanup
            write_record(work / "report.json", report)
        await env.shutdown()
        api.stop()
        if cleanup["remaining_active"]:
            raise RuntimeError("Experiment descendant cleanup failed")


async def main():
    global SCRATCH_ROOT, PLUGIN_ROOT
    p = argparse.ArgumentParser()
    p.add_argument("--repo")
    p.add_argument("--root", required=True)
    p.add_argument("--server")
    p.add_argument(
        "--case", choices=["reuse", "replacement", "inflight", "orphan"], required=True
    )
    args = p.parse_args()
    plugin_root = Path(args.repo) if args.repo else Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(plugin_root))
    root = Path(args.root)
    if root.exists():
        p.error("--root must name a fresh output directory")
    if root.resolve().is_relative_to(plugin_root.resolve()):
        p.error("--root must be outside the plugin repository")
    if args.case != "reuse" and (not args.server or not Path(args.server).is_file()):
        p.error("--server must name an existing cached Temporal binary")
    root.mkdir(parents=True, exist_ok=True)
    SCRATCH_ROOT, PLUGIN_ROOT = str(root), str(plugin_root)
    for key in list(os.environ):
        if key.startswith(("ANTHROPIC_", "CLAUDE_")) or key.lower() in (
            "http_proxy",
            "https_proxy",
            "all_proxy",
        ):
            os.environ.pop(key, None)
    if args.case == "reuse":
        await results(root)
    else:
        if not args.server:
            p.error(
                "--server must name an existing cached Temporal binary for replacement cases"
            )
        await replacement(
            root, args.server, args.case == "inflight", args.case == "orphan"
        )


if __name__ == "__main__":
    asyncio.run(main())
