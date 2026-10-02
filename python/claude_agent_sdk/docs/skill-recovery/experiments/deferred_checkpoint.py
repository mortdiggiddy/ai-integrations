"""Check an actual deferred Write transcript at the SDK recovery boundary."""

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import sys
import uuid
from dataclasses import asdict
from pathlib import Path

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ToolResultBlock,
    project_key_for_directory,
)
from claude_agent_sdk._internal.main_agent_recovery import pending_tool_uses
from claude_agent_sdk._internal.transport.subprocess_cli import SubprocessCLITransport
from main_preflight import MemoryStore

from temporalio.claude_agent_sdk import (
    ClaudeAgentSdkRunner,
    FileSessionStore,
    SegmentInput,
    ToolPolicy,
    ToolPolicyEntry,
)


class TransportBoundaryReached(RuntimeError):
    pass


class RecoveryStore(MemoryStore):
    async def append_if_unchanged(self, key, expected_last_uuid, entries):
        head = next(
            (entry["uuid"] for entry in reversed(self.entries) if entry.get("uuid")),
            None,
        )
        self.append_attempts += 1
        if key != self.key or head != expected_last_uuid:
            return False
        self.entries.extend(json.loads(json.dumps(entries)))
        self.commits += 1
        return True


async def probe(root, cli):
    plugin = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(plugin))
    from tests.helpers.fake_messages_api import FakeMessagesAPI, engine_env

    for name in list(os.environ):
        if name.startswith(("ANTHROPIC_", "CLAUDE_")) or name.lower() in (
            "http_proxy",
            "https_proxy",
            "all_proxy",
        ):
            os.environ.pop(name, None)
    work = root / "work"
    work.mkdir(parents=True)
    marker = work / "engine-write.txt"
    request = {
        "type": "tool_use",
        "id": "toolu_deferred_write_original",
        "name": "Write",
        "input": {"file_path": str(marker), "content": "DEFERRED_WRITE_MARKER\n"},
    }

    def decide(body):
        del body
        return [request]

    class NativeAPI(FakeMessagesAPI):
        def write(self, handler, body, blocks):
            offered = {tool.get("name") for tool in body.get("tools", [])}
            if "Write" in offered:
                blocks = decide(body)
            return super().write(handler, body, blocks)

    api = NativeAPI(decide).start()
    assert api.base_url.startswith("http://127.0.0.1:")
    store = FileSessionStore(root / "store")
    policy = ToolPolicy((ToolPolicyEntry("Write", "effect", "repeatable"),))
    runner = ClaudeAgentSdkRunner(
        session_store=store,
        cwd=str(work),
        cli_path=str(cli),
        env=engine_env(api, str(root / "config")),
        tool_policy=policy,
    )
    report = {
        "sdk_version": importlib.metadata.version("claude-agent-sdk"),
        "temporal_version": importlib.metadata.version("temporalio"),
        "cli_sha256": hashlib.sha256(cli.read_bytes()).hexdigest(),
        "paid_model_calls": 0,
        "effect_executions": 0,
        "scope": "Actual policy runner Write defer; SDK preflight only, no resumed CLI",
    }

    def record(name, value):
        raw = json.dumps(value, indent=2, default=str)
        raw = raw.replace(str(root), "<scratch>").replace(str(plugin), "<plugin>")
        (root / name).write_text(raw + "\n")

    try:
        first = await asyncio.wait_for(
            runner.run(
                SegmentInput(
                    session_id=str(uuid.uuid4()),
                    prompt="Write the offered scratch file once.",
                    tools=[],
                    builtin_tools=["Write"],
                    tool_policy=policy.canonical_json(),
                ),
                1,
            ),
            45,
        )
        report["segment"] = asdict(first)
        report["engine_marker_exists"] = marker.exists()
        report["stub_calls"] = runner.stub_calls
        if first.is_error or first.deferred is None or marker.exists():
            report["status"] = "failed before accepted deferred checkpoint"
            return report
        assert first.deferred.id == request["id"]
        assert first.deferred.name == request["name"]
        assert first.deferred.input == request["input"]
        key = {
            "project_key": project_key_for_directory(str(work)),
            "session_id": first.session_id,
        }
        entries = await store.load(key)
        assert entries
        record("original-transcript.json", entries)
        report["original_transcript_sha256"] = hashlib.sha256(
            json.dumps(entries, sort_keys=True).encode()
        ).hexdigest()
        pending, leaf = pending_tool_uses(key, entries)
        report["pending"] = [asdict(p) for p in pending]
        report["message_leaf_uuid"] = leaf.get("uuid") if leaf else None
        if len(pending) != 1 or pending[0].id != first.deferred.id:
            report["status"] = (
                "failed: unchanged deferred transcript has no matching unresolved call"
            )
            return report
        assert (pending[0].name, pending[0].input) == (
            first.deferred.name,
            first.deferred.input,
        )
        fixture = RecoveryStore(key, entries, "actual-defer")
        callbacks = []
        starts = []

        async def recover(call):
            callbacks.append(asdict(call))
            assert asdict(call) == asdict(pending[0])
            return ToolResultBlock(call.id, "RECORDED_WRITE_RESULT_FIXTURE", False)

        async def guard_start(self):
            starts.append(type(self).__name__)
            raise TransportBoundaryReached("Resumed CLI deliberately blocked")

        original = SubprocessCLITransport.connect
        SubprocessCLITransport.connect = guard_start
        client = ClaudeSDKClient(
            options=ClaudeAgentOptions(
                cwd=str(work),
                cli_path=str(cli),
                env={"CLAUDE_CONFIG_DIR": str(root / "recovery-config")},
                tools=[],
                allowed_tools=[],
                setting_sources=[],
                strict_mcp_config=True,
                permission_mode="default",
                session_store=fixture,
                session_store_flush="eager",
                resume=first.session_id,
                recover_pending_tool=recover,
                parallel_tool_recovery=False,
            )
        )
        try:
            await asyncio.wait_for(client.connect(), 10)
            raise AssertionError("Transport guard did not fire")
        except TransportBoundaryReached:
            pass
        finally:
            await client.disconnect()
            SubprocessCLITransport.connect = original
        report["recovery_callbacks"] = callbacks
        report["guarded_transport_attempts"] = starts
        report["recovery_commits"] = fixture.commits
        assert len(callbacks) == len(starts) == fixture.commits == 1
        assert len(api.requests) == 1 and not api.errors and not marker.exists()
        assert runner.stub_calls == 0
        record("preflight-transcript.json", fixture.entries)
        report["status"] = "passed: actual deferred call recovered before transport"
        report["limits"] = (
            "In-memory conditional append fixture, no external effect Activity/result, "
            "no resumed CLI/model, no replacement Worker, no real model proof"
        )
        return report
    except Exception as exc:
        report["status"] = "failed"
        report["exception"] = {"type": type(exc).__name__, "message": str(exc)}
        return report
    finally:
        report["model_requests"] = len(api.requests)
        report["api_errors"] = api.errors
        report["engine_marker_exists"] = marker.exists()
        record("model-requests.json", api.requests)
        record("report.json", report)
        api.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--cli", type=Path, required=True)
    args = parser.parse_args()
    if args.root.exists() or not args.cli.is_file():
        parser.error("Fresh output root and existing explicit CLI required")
    args.root.mkdir(parents=True)
    report = asyncio.run(probe(args.root.resolve(), args.cli.resolve()))
    print(
        json.dumps(
            {"status": report["status"], "model_requests": report["model_requests"]}
        )
    )


if __name__ == "__main__":
    main()
