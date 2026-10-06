"""Refuse mismatched recovery against an unchanged recorded model checkpoint."""

import copy
import hashlib
import importlib
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest

for parent in Path(__file__).resolve().parents:
    experiments = parent / "docs/skill-recovery/experiments"
    if (experiments / "write_recovery.py").exists():
        sys.path.insert(0, str(experiments))
        break


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "fault",
    [
        "id",
        "name",
        "input",
        "transcript_uuid",
        "project_key",
        "session_id",
        "outcome",
        "missing-transcript",
        "append-refused",
    ],
)
async def test_recorded_checkpoint_refuses_before_transport(
    fault: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    evidence = os.environ.get("RECORDED_CHECKPOINT_EVIDENCE")
    if not evidence:
        pytest.skip(
            "Requires the recorded checkpoint mounted in the isolated SDK image"
        )

    from host_session import AdmissionRefused
    from write_recovery import ProofStore, recorded_result

    sdk = importlib.import_module("claude_agent_sdk")
    recovery = importlib.import_module("claude_agent_sdk._internal.main_agent_recovery")
    transport_module = importlib.import_module(
        "claude_agent_sdk._internal.transport.subprocess_cli"
    )

    root = Path(evidence)
    original = json.loads((root / "original-transcript.json").read_text())
    accepted = json.loads((root / "segment_committed.json").read_text())["accepted"]
    outcome = json.loads((root / "effect_committed.json").read_text())["outcome"]
    assert (
        hashlib.sha256(json.dumps(original, sort_keys=True).encode()).hexdigest()
        == accepted["transcript_sha256"]
    )
    key = accepted["key"]
    pending, _ = recovery.pending_tool_uses(key, original)
    assert len(pending) == 1 and asdict(pending[0]) == accepted["pending"]
    expected = copy.deepcopy({**accepted, "outcome": outcome})
    if fault in {"id", "name", "transcript_uuid"}:
        expected["pending"][fault] += "-changed"
    elif fault == "input":
        expected["pending"]["input"]["content"] += "changed"
    elif fault in {"project_key", "session_id"}:
        expected["pending"]["key"][fault] += "-changed"
    elif fault == "outcome":
        expected["outcome"]["content"] += "changed"

    store = ProofStore(tmp_path / "transcript.db", create=True)
    if fault != "missing-transcript":
        await store.append(key, original)
    before = await store.load(key)
    callbacks: list[dict[str, Any]] = []
    transports: list[str] = []

    async def recover(call: Any):
        callbacks.append(asdict(call))
        return recorded_result(call, expected)

    async def forbidden_transport(transport: Any):
        transports.append(type(transport).__name__)
        raise AssertionError("Refused recovery attempted transport startup")

    async def refuse_append(session_key: Any, expected_last_uuid: Any, entries: Any):
        return False

    monkeypatch.setattr(
        transport_module.SubprocessCLITransport, "connect", forbidden_transport
    )
    if fault == "append-refused":
        monkeypatch.setattr(store, "append_if_unchanged", refuse_append)
    client = sdk.ClaudeSDKClient(
        options=sdk.ClaudeAgentOptions(
            cwd="/state/work",
            cli_path="/opt/claude",
            tools=[],
            allowed_tools=[],
            setting_sources=[],
            permission_mode="default",
            session_store=store,
            session_store_flush="eager",
            resume=key["session_id"],
            recover_pending_tool=recover,
            parallel_tool_recovery=False,
        )
    )
    error = None
    try:
        with pytest.raises((AdmissionRefused, RuntimeError)) as raised:
            await client.connect()
        error = {"type": type(raised.value).__name__, "message": str(raised.value)}
        assert not transports and client._transport is None
        assert callbacks == (
            [] if fault == "missing-transcript" else [accepted["pending"]]
        )
        assert await store.load(key) == before
    finally:
        await client.disconnect()
    output = Path(os.environ["RECORDED_CHECKPOINT_OUTPUT"])
    (output / (fault + ".json")).write_text(
        json.dumps(
            {
                "fault": fault,
                "error": error,
                "pending_seen": callbacks,
                "transport_starts": transports,
                "transcript_sha256": accepted["transcript_sha256"],
                "parallel_tool_recovery": False,
                "original_transcript_unchanged": True,
                "result_published": False,
                "model_calls": 0,
                "effects": 0,
            },
            indent=2,
        )
    )


@pytest.mark.parametrize(
    "fault",
    [
        "control",
        "transcript",
        "missing-workspace",
        "changed-workspace",
        "missing-claim",
        "changed-claim",
        "batch",
        "ambiguous",
    ],
)
def test_recorded_recovery_state_guard(
    fault: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    evidence = os.environ.get("RECORDED_CHECKPOINT_EVIDENCE")
    if not evidence:
        pytest.skip(
            "Requires the recorded checkpoint mounted in the isolated SDK image"
        )
    from host_session import AdmissionRefused
    from write_recovery import CONTENT, validate_recovery_state

    root = Path(evidence)
    entries = json.loads((root / "original-transcript.json").read_text())
    accepted = json.loads((root / "segment_committed.json").read_text())["accepted"]
    claim = json.loads((root / "effect-invocation.json").read_text())
    state = tmp_path
    (state / "work").mkdir()
    marker = state / "work/marker.txt"
    marker.write_text(CONTENT)
    receipt = state / "effect-invocation.json"
    receipt.write_text(json.dumps(claim))
    scenario = "write"
    if fault == "transcript":
        accepted["transcript_sha256"] = "changed"
    elif fault == "missing-workspace":
        marker.unlink()
    elif fault == "changed-workspace":
        marker.write_text("changed")
    elif fault == "missing-claim":
        receipt.unlink()
    elif fault == "changed-claim":
        claim["accepted"]["pending"]["id"] += "-changed"
        receipt.write_text(json.dumps(claim))
    elif fault == "batch":
        recovery = importlib.import_module(
            "claude_agent_sdk._internal.main_agent_recovery"
        )
        pending, metadata = recovery.pending_tool_uses(accepted["key"], entries)
        monkeypatch.setattr(
            recovery,
            "pending_tool_uses",
            lambda key, data: ([pending[0], pending[0]], metadata),
        )
    elif fault == "ambiguous":
        scenario = "bash-park"
    if fault == "control":
        validate_recovery_state(accepted, entries, state, scenario)
        reason = None
    else:
        with pytest.raises(AdmissionRefused) as raised:
            validate_recovery_state(accepted, entries, state, scenario)
        reason = str(raised.value)
        if fault == "batch":
            assert "batch refused" in reason
    assert entries == json.loads((root / "original-transcript.json").read_text())
    output = Path(os.environ["RECORDED_CHECKPOINT_OUTPUT"])
    (output / ("state-" + fault + ".json")).write_text(
        json.dumps(
            {
                "fault": fault,
                "reason": reason,
                "model_calls": 0,
                "effects": 0,
                "original_transcript_unchanged": True,
                "batch_fixture": "two pending references injected at the SDK parser boundary"
                if fault == "batch"
                else None,
            },
            indent=2,
        )
    )


@pytest.mark.asyncio
async def test_production_runner_commits_recorded_recovery_before_transport(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    evidence = os.environ.get("RECORDED_CHECKPOINT_EVIDENCE")
    if not evidence:
        pytest.skip(
            "Requires the recorded checkpoint mounted in the isolated SDK image"
        )
    from write_recovery import ProofStore, recorded_result

    from temporalio.claude_agent_sdk import (
        ClaudeAgentSdkRunner,
        SegmentInput,
        ToolPolicy,
        ToolPolicyEntry,
    )

    sdk = importlib.import_module("claude_agent_sdk")
    transport_module = importlib.import_module(
        "claude_agent_sdk._internal.transport.subprocess_cli"
    )
    root = Path(evidence)
    original = json.loads((root / "original-transcript.json").read_text())
    accepted = json.loads((root / "segment_committed.json").read_text())["accepted"]
    outcome = json.loads((root / "effect_committed.json").read_text())["outcome"]
    store = ProofStore(tmp_path / "transcript.db", create=True)
    await store.append(accepted["key"], original)
    callbacks = []
    starts = []

    async def recover(call: Any):
        callbacks.append(asdict(call))
        return recorded_result(call, {**accepted, "outcome": outcome})

    class TransportBarrier(Exception):
        pass

    async def guarded_transport(transport: Any):
        starts.append(len(callbacks))
        raise TransportBarrier("Recorded recovery verified; no CLI launch permitted")

    monkeypatch.setattr(
        transport_module.SubprocessCLITransport, "connect", guarded_transport
    )
    policy = ToolPolicy((ToolPolicyEntry("Write", "effect", "repeatable"),))
    runner = ClaudeAgentSdkRunner(
        session_store=store,
        cwd="/state/work",
        cli_path="/opt/claude",
        tool_policy=policy,
        recover_pending_tool=recover,
    )
    options = runner._engine_options(
        SegmentInput(
            session_id=accepted["key"]["session_id"],
            prompt=None,
            tools=[],
            builtin_tools=["Write"],
            tool_policy=policy.canonical_json(),
        ),
        {},
        accepted["key"]["session_id"],
        True,
        accepted["segment"]["checkpoint"],
        str(tmp_path),
        None,
    )
    client = sdk.ClaudeSDKClient(options=sdk.ClaudeAgentOptions(**options))
    try:
        with pytest.raises(TransportBarrier):
            await client.connect()
        assert starts == [1] and callbacks == [accepted["pending"]]
        entries = await options["session_store"].load(accepted["key"])
        blocks = [
            b
            for e in entries
            for b in e.get("message", {}).get("content", [])
            if isinstance(b, dict)
            and b.get("type") == "tool_result"
            and b.get("tool_use_id") == accepted["pending"]["id"]
        ]
        assert blocks == [{"type": "tool_result", **outcome}]
        assert entries[: len(original)] == original
        assert options["parallel_tool_recovery"] is False
        assert type(runner) is ClaudeAgentSdkRunner
    finally:
        await client.disconnect()
    Path(os.environ["RECORDED_CHECKPOINT_OUTPUT"], "production-runner.json").write_text(
        json.dumps(
            {
                "callbacks": callbacks,
                "transport_barrier": starts,
                "result": blocks,
                "original_transcript_unchanged": True,
                "model_calls": 0,
                "effects": 0,
            },
            indent=2,
        )
    )
