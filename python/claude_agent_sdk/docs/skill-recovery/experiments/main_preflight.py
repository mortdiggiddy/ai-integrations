"""Exercise actual SDK recovery refusal before its default transport starts."""

import argparse
import asyncio
import copy
import hashlib
import importlib.metadata
import json
import uuid
from dataclasses import asdict
from pathlib import Path

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ToolResultBlock,
    project_key_for_directory,
)
from claude_agent_sdk._internal.transport.subprocess_cli import SubprocessCLITransport


class ParkUnknownOutcome(RuntimeError):
    pass


class AcceptedIdentityMismatch(RuntimeError):
    pass


class MemoryStore:
    def __init__(self, key, entries, mode):
        self.key = key
        self.entries = copy.deepcopy(entries)
        self.mode = mode
        self.loads = 0
        self.append_attempts = 0
        self.commits = 0

    async def load(self, key):
        if key != self.key:
            raise RuntimeError("Unexpected session key")
        self.loads += 1
        if self.mode == "missing-transcript":
            return None
        data = copy.deepcopy(self.entries)
        if self.mode == "readback-mismatch" and self.commits:
            data[-1]["message"]["content"][0]["content"] = "CORRUPTED_READBACK"
        return data

    async def append(self, key, entries):
        raise RuntimeError("Ordinary mirroring must not run in preflight")

    async def append_if_unchanged(self, key, expected_last_uuid, entries):
        self.append_attempts += 1
        if key != self.key:
            raise RuntimeError("Unexpected session key")
        if self.mode == "failed-append":
            raise OSError("Injected recovery append failure")
        if self.entries[-1]["uuid"] != expected_last_uuid:
            return False
        self.entries.extend(copy.deepcopy(entries))
        self.commits += 1
        return True


def transcript(session, directory, mode):
    uid = str(uuid.uuid4())
    tid = "toolu_preflight_original"
    arguments = {"n": 1}
    name = "mcp__durable__echo"
    if mode == "changed-input":
        arguments["n"] = 2
    if mode == "bash-park":
        name = "Bash"
        arguments = {"command": "synthetic previously started Bash request"}
    entry = {
        "type": "assistant",
        "uuid": uid,
        "parentUuid": None,
        "isSidechain": False,
        "sessionId": session,
        "cwd": str(directory),
        "version": "2.1.274",
        "message": {
            "id": "msg_preflight_synthetic",
            "role": "assistant",
            "content": [
                {"type": "tool_use", "id": tid, "name": name, "input": arguments}
            ],
        },
    }
    return [entry]


async def run_case(root, cli, mode):
    directory = root / mode
    directory.mkdir()
    config = directory / "isolated-config"
    config.mkdir()
    session = str(uuid.uuid4())
    key = {
        "project_key": project_key_for_directory(str(directory)),
        "session_id": session,
    }
    entries = transcript(session, directory, mode)
    store = MemoryStore(key, entries, mode)
    pending_seen = []
    transport_starts = []
    marker = directory / "prior-marker.txt"
    if mode == "bash-park":
        marker.write_text("SYNTHETIC_PRIOR_EFFECT_MARKER\n")
    marker_before = marker.read_bytes() if marker.exists() else None

    async def recover(pending):
        pending_seen.append(asdict(pending))
        if mode == "bash-park":
            raise ParkUnknownOutcome("Unknown Bash outcome; host parks before resume")
        if mode == "changed-input":
            accepted = ("mcp__durable__echo", {"n": 1})
            if (pending.name, pending.input) != accepted:
                raise AcceptedIdentityMismatch(
                    "Stored call differs from accepted ledger inputs"
                )
        returned_id = "toolu_wrong" if mode == "wrong-result-id" else pending.id
        return ToolResultBlock(returned_id, "RECORDED_RESULT", False)

    async def forbidden_start(self):
        transport_starts.append(type(self).__name__)
        raise RuntimeError("Unexpected default transport startup")

    original_connect = SubprocessCLITransport.connect
    SubprocessCLITransport.connect = forbidden_start
    client = ClaudeSDKClient(
        options=ClaudeAgentOptions(
            cwd=str(directory),
            cli_path=str(cli),
            env={"CLAUDE_CONFIG_DIR": str(config)},
            tools=[],
            allowed_tools=[],
            setting_sources=[],
            strict_mcp_config=True,
            permission_mode="default",
            session_store=store,
            session_store_flush="eager",
            resume=session,
            recover_pending_tool=recover,
            parallel_tool_recovery=False,
        )
    )
    error = None
    try:
        await asyncio.wait_for(client.connect(), timeout=5)
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        await client.disconnect()
        SubprocessCLITransport.connect = original_connect
    expected = {
        "wrong-result-id": ("ValueError", "original native tool-use ID"),
        "missing-transcript": ("RuntimeError", "missing from session storage"),
        "changed-input": ("AcceptedIdentityMismatch", "accepted ledger inputs"),
        "failed-append": ("OSError", "append failure"),
        "readback-mismatch": ("RuntimeError", "exact recovery transcript"),
        "bash-park": ("ParkUnknownOutcome", "host parks before resume"),
    }[mode]
    if not error or error["type"] != expected[0] or expected[1] not in error["message"]:
        raise RuntimeError("Unexpected refusal result for " + mode + ": " + str(error))
    if transport_starts or client._transport is not None:
        raise RuntimeError("Recovery reached transport startup: " + mode)
    if marker_before is not None and marker.read_bytes() != marker_before:
        raise RuntimeError("Prior marker changed during park")
    if mode == "missing-transcript" and pending_seen:
        raise RuntimeError("Missing transcript invoked recovery callback")
    if mode == "readback-mismatch" and store.commits != 1:
        raise RuntimeError("Readback fault did not follow the recovery commit")
    if mode == "bash-park" and (store.commits or store.append_attempts):
        raise RuntimeError("Unknown outcome published a tool result")
    report = {
        "case": mode,
        "status": "passed",
        "fixture_kind": "synthetic parent-linked pending transcript and in-memory test store",
        "entry_point": "ClaudeSDKClient.connect with default transport selection",
        "transport_start_guard": "Only SubprocessCLITransport.connect is guarded; no custom transport supplied",
        "error": error,
        "pending_seen": pending_seen,
        "store_loads": store.loads,
        "append_attempts": store.append_attempts,
        "commits": store.commits,
        "transport_start_attempts": len(transport_starts),
        "cli_spawns": 0,
        "model_requests": 0,
        "actual_bash_invocations": 0,
        "synthetic_prior_effect_markers": 1 if marker_before is not None else 0,
        "post_park_tool_result_publications": 0 if mode == "bash-park" else None,
        "input_refusal_owner": "host callback ledger binding"
        if mode == "changed-input"
        else None,
        "park_owner": "host callback exception" if mode == "bash-park" else None,
        "original_entries": entries,
        "stored_entries_after": store.entries,
        "unsupported": "No native CLI effect, real transcript, durable park state, Worker recovery or session lease is proved",
    }
    (directory / "report.json").write_text(json.dumps(report, indent=2))
    return report


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    if root.exists():
        raise RuntimeError("Fresh root required")
    root.mkdir(parents=True)
    import claude_agent_sdk

    installed = (
        Path(claude_agent_sdk.__file__).parent / "_internal/main_agent_recovery.py"
    )
    source = (
        args.source_root.resolve()
        / "src/claude_agent_sdk/_internal/main_agent_recovery.py"
    )
    if installed.read_bytes() != source.read_bytes():
        raise RuntimeError(
            "Installed recovery implementation differs from pinned source"
        )
    reports = []
    for mode in (
        "wrong-result-id",
        "missing-transcript",
        "changed-input",
        "failed-append",
        "readback-mismatch",
        "bash-park",
    ):
        reports.append(await run_case(root, args.cli.resolve(), mode))
    summary = {
        "status": "passed",
        "sdk_version": importlib.metadata.version("claude-agent-sdk"),
        "temporal_version": importlib.metadata.version("temporalio"),
        "installed_recovery_file": str(installed),
        "recovery_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "cases": [
            {
                k: r[k]
                for k in (
                    "case",
                    "status",
                    "error",
                    "store_loads",
                    "append_attempts",
                    "commits",
                    "transport_start_attempts",
                    "cli_spawns",
                    "model_requests",
                    "actual_bash_invocations",
                    "synthetic_prior_effect_markers",
                )
            }
            for r in reports
        ],
        "cas_race": "not executed",
        "lease_claim": False,
        "paid_model_calls": False,
    }
    (root / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
