"""Offline policy validation, hook decisions, and engine option assembly."""

from __future__ import annotations

import dataclasses
import json
import sys
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import pytest
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    PermissionResultDeny,
    ResultMessage,
    SystemMessage,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)

from temporalio.claude_agent_sdk import (
    ClaudeAgentSdkRunner,
    DurableClaudeAgent,
    FileSessionStore,
    SegmentInput,
    ToolOutcome,
    ToolPolicy,
    ToolPolicyEntry,
    _defer_hook,
    _runner,
)
from temporalio.claude_agent_sdk._policy import policy_extra_options
from temporalio.exceptions import ApplicationError


def _policy() -> ToolPolicy:
    return ToolPolicy(
        (
            ToolPolicyEntry("Read", "read"),
            ToolPolicyEntry("Grep", "read"),
            ToolPolicyEntry("Glob", "read"),
            ToolPolicyEntry("Write", "effect", "repeatable"),
            ToolPolicyEntry("Edit", "effect", "repeatable"),
            ToolPolicyEntry("Bash", "effect", "claimed"),
            ToolPolicyEntry("AskUserQuestion", "ask"),
        )
    )


def _input(policy: ToolPolicy | None) -> SegmentInput:
    return SegmentInput(
        session_id="s",
        prompt="hello",
        tools=[],
        builtin_tools=[row.name for row in policy.entries] if policy else ["Write"],
        tool_policy=policy.canonical_json() if policy is not None else None,
    )


def _runner_in(tmp_path: Path, **kwargs: Any) -> ClaudeAgentSdkRunner:
    return ClaudeAgentSdkRunner(
        session_store=FileSessionStore(tmp_path / "store"),
        cwd=str(tmp_path),
        **kwargs,
    )


def test_policy_names_are_exact() -> None:
    policy = _policy()
    assert policy.lookup("Bash").mode == "claimed"
    for name in ("bash", "Write(extra)", "mcp__durable__Write", "Unknown"):
        with pytest.raises(ValueError):
            policy.lookup(name)
        with pytest.raises(ValueError):
            ToolPolicyEntry(name, "effect", "claimed")


@pytest.mark.parametrize(
    "name,classification,mode",
    [
        ("Bash", "read", None),
        ("Bash", "effect", "repeatable"),
        ("Write", "effect", "claimed"),
        ("Read", "effect", "repeatable"),
        ("AskUserQuestion", "effect", "claimed"),
    ],
)
def test_policy_rejects_changed_classifications(
    name: str, classification: Any, mode: Any
) -> None:
    with pytest.raises(ValueError):
        ToolPolicyEntry(name, classification, mode)


def test_policy_is_immutable_and_digest_is_order_independent() -> None:
    rows = list(_policy().entries)
    policy = ToolPolicy(tuple(rows))
    rows.clear()
    assert len(policy.entries) == 7
    assert (
        policy.policy_version
        == ToolPolicy(tuple(reversed(policy.entries))).policy_version
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(policy.entries[0], "name", "Bash")
    with pytest.raises(ValueError):
        ToolPolicy((policy.entries[0], policy.entries[0]))


@pytest.mark.parametrize(
    "key",
    sorted(
        {field.name for field in dataclasses.fields(ClaudeAgentOptions)}
        - {"system_prompt", "extra_args"}
    ),
)
def test_policy_rejects_every_other_sdk_extra(tmp_path: Path, key: str) -> None:
    with pytest.raises(ValueError):
        _runner_in(tmp_path, tool_policy=_policy(), extra_options={key: "override"})


@pytest.mark.parametrize(
    "raw",
    [
        {"permission-mode": "bypassPermissions"},
        {"debug-to-stderr": None},
        {"--debug-to-stderr": None},
        {"resume": "x"},
        {"": None},
        [],
    ],
)
def test_policy_rejects_raw_flags(raw: Any) -> None:
    with pytest.raises(ValueError):
        policy_extra_options({"extra_args": raw})


def test_policy_extra_snapshot_and_backstop(tmp_path: Path) -> None:
    policy = _policy()
    extra: dict[str, Any] = {"system_prompt": "worker", "extra_args": {}}
    runner = _runner_in(tmp_path, tool_policy=policy, extra_options=extra)
    extra["permission_mode"] = "bypassPermissions"
    extra["extra_args"]["allowedTools"] = "Bash"
    options = runner._engine_options(
        _input(policy), {}, "s", False, None, str(tmp_path), None
    )
    assert options["tools"] == [row.name for row in policy.entries]
    assert options["allowed_tools"] == ["Read", "Grep", "Glob"]
    assert options["permission_mode"] == "default"
    assert options["extra_args"] == {}
    assert options["setting_sources"] == []
    assert options["can_use_tool"] is _runner._deny_policy_permission
    assert options["env"]["TCA_POLICY_MODE"] == "1"


async def test_policy_permission_callback_never_grants() -> None:
    assert isinstance(
        await _runner._deny_policy_permission("Read", {}, None),
        PermissionResultDeny,
    )


def test_policy_runner_requires_matching_inventory(tmp_path: Path) -> None:
    runner = _runner_in(tmp_path, tool_policy=_policy())
    with pytest.raises(ValueError, match="match"):
        runner._effective_policy(_input(None))
    inp = _input(_policy())
    inp.builtin_tools.append("Unknown")
    with pytest.raises(ValueError, match="match"):
        runner._effective_policy(inp)


def test_legacy_options_stay_unrestricted(tmp_path: Path) -> None:
    runner = _runner_in(tmp_path, extra_options={"permission_mode": "acceptEdits"})
    options = runner._engine_options(
        _input(None), {}, "s", False, None, str(tmp_path), None
    )
    assert "Write" in options["allowed_tools"]
    assert options["permission_mode"] == "acceptEdits"
    assert "can_use_tool" not in options


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Read", None),
        ("Grep", None),
        ("Glob", None),
        ("Write", "defer"),
        ("Edit", "defer"),
        ("Bash", "defer"),
        ("AskUserQuestion", "defer"),
        ("Unknown", "deny"),
        ("mcp__durable__Bash", "deny"),
    ],
)
def test_policy_hook_table(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, expected: str | None
) -> None:
    monkeypatch.setenv("TCA_POLICY_MODE", "1")
    monkeypatch.setenv("TCA_HOOK_DIR", str(tmp_path))
    (tmp_path / "policy.json").write_text(
        json.dumps(
            {
                "entries": json.loads(_policy().canonical_json()),
                "workspace_root": str(tmp_path),
            }
        )
    )
    answer = _defer_hook.decide(
        {
            "tool_name": name,
            "tool_use_id": "one",
            "tool_input": {"file_path": str(tmp_path / "inside")},
        }
    )
    assert answer.get("permissionDecision") == expected


def test_policy_hook_pause_stop_resume_and_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TCA_POLICY_MODE", "1")
    monkeypatch.setenv("TCA_HOOK_DIR", str(tmp_path))
    (tmp_path / "policy.json").write_text(
        json.dumps(
            {
                "entries": json.loads(_policy().canonical_json()),
                "workspace_root": str(tmp_path),
            }
        )
    )

    def call(name: str, identity: str, **tool_input: Any) -> dict[str, Any]:
        return _defer_hook.decide(
            {
                "tool_name": name,
                "tool_use_id": identity,
                "tool_input": tool_input,
            }
        )

    assert (
        call("Read", "outside", file_path=str(tmp_path.parent / "secret"))[
            "permissionDecision"
        ]
        == "deny"
    )
    monkeypatch.setenv("TCA_ANSWERED_IDS", "answered")
    assert call("Bash", "answered")["permissionDecision"] == "defer"
    assert not (tmp_path / "paused_call").exists()
    assert call("Write", "one")["permissionDecision"] == "defer"
    assert call("Read", "two", file_path="inside")["permissionDecision"] == "deny"
    assert call("Bash", "three")["permissionDecision"] == "deny"
    (tmp_path / "stop").touch()
    assert call("Bash", "one")["permissionDecision"] == "deny"


@pytest.mark.parametrize("event", ["PostToolUse", "PostToolUseFailure"])
def test_policy_observes_execution_events(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, event: str
) -> None:
    monkeypatch.setenv("TCA_POLICY_MODE", "1")
    monkeypatch.setenv("TCA_HOOK_DIR", str(tmp_path))
    (tmp_path / "policy.json").write_text(
        json.dumps(
            {
                "entries": json.loads(_policy().canonical_json()),
                "workspace_root": str(tmp_path),
            }
        )
    )
    _defer_hook.decide(
        {"hook_event_name": event, "tool_name": "Write", "tool_use_id": "one"}
    )
    assert json.loads((tmp_path / "observed_effects").read_text())["name"] == "Write"
    error = _runner.ClaudeAgentSdkRunner._pause_contract_problem(
        ["Write"],
        None,
        None,
        set(),
        "test",
        None,
        policy_mode=True,
    )
    assert error and "Write" in error and "cannot undo" in error


async def test_policy_workflow_never_supplies_missing_executor_result() -> None:
    from temporalio.claude_agent_sdk import DeferredCall

    agent = DurableClaudeAgent(tool_policy=_policy())
    call = DeferredCall(id="one", name="Bash", input={"command": "echo hello"})
    with pytest.raises(ApplicationError, match="executor"):
        await agent._run_tool(call)
    assert agent.state().blocked_policy_call == call
    assert agent.state().pending == {}


def test_input_only_policy_options_snapshot(
    tmp_path: Path,
) -> None:
    extra: dict[str, Any] = {"system_prompt": "original", "extra_args": {}}
    runner = _runner_in(tmp_path, extra_options=extra)
    extra["system_prompt"] = "changed"
    extra["extra_args"]["permission-mode"] = "bypassPermissions"
    extra["allowed_tools"] = ["Bash"]
    options = runner._engine_options(
        _input(_policy()), {}, "s", False, None, str(tmp_path), None
    )
    assert options["system_prompt"].startswith("original")
    assert options["extra_args"] == {}
    assert options["permission_mode"] == "default"
    assert "Bash" not in options["allowed_tools"]


async def test_unknown_policy_workflow_call_is_nonretryable() -> None:
    from temporalio.claude_agent_sdk import DeferredCall

    agent = DurableClaudeAgent(tool_policy=_policy())
    with pytest.raises(ApplicationError) as failure:
        await agent._run_tool(
            DeferredCall(id="unknown", name="mcp__durable__Bash", input={})
        )
    assert failure.value.non_retryable
    assert failure.value.type == "PolicyToolNotOffered"
    assert agent.state().pending == {}


@pytest.mark.parametrize("observation", ["result", "PostToolUse", "PostToolUseFailure"])
async def test_runner_rejects_observed_policy_effect_before_checkpoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, observation: str
) -> None:
    async def scripted(**kwargs: Any) -> AsyncIterator[Any]:
        yield SystemMessage(subtype="init", data={"claude_code_version": "2.1.274"})
        yield AssistantMessage(
            content=[ToolUseBlock(id="effect", name="Write", input={})],
            model="offline",
        )
        if observation == "result":
            yield UserMessage(
                content=[
                    ToolResultBlock(
                        tool_use_id="effect", content="written", is_error=False
                    )
                ]
            )
        else:
            monkeypatch.setenv("TCA_POLICY_MODE", "1")
            monkeypatch.setenv("TCA_HOOK_DIR", kwargs["options"].env["TCA_HOOK_DIR"])
            _defer_hook.decide(
                {
                    "hook_event_name": observation,
                    "tool_name": "Write",
                    "tool_use_id": "effect",
                }
            )
        yield ResultMessage(
            subtype="success",
            duration_ms=1,
            duration_api_ms=1,
            is_error=False,
            num_turns=1,
            session_id="s",
        )

    async def no_checkpoint(*args: Any, **kwargs: Any) -> Any:
        del args, kwargs
        raise AssertionError("Contract violation must not commit a checkpoint")

    monkeypatch.setattr(_runner, "query", scripted)
    monkeypatch.setattr(ClaudeAgentSdkRunner, "_checkpoint", no_checkpoint)
    runner = _runner_in(tmp_path, tool_policy=_policy())
    output = await runner._run_engine(_input(_policy()), {}, "s", False)
    assert output.is_error
    assert output.deferred is None and output.checkpoint is None
    assert output.error and "Write" in output.error and "cannot undo" in output.error


@pytest.mark.parametrize("shape", ["request", "denial", "injected"])
async def test_runner_does_not_confuse_requests_denials_or_host_results_with_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, shape: str
) -> None:
    async def scripted(**kwargs: Any) -> AsyncIterator[Any]:
        del kwargs
        yield SystemMessage(subtype="init", data={"claude_code_version": "2.1.274"})
        yield AssistantMessage(
            content=[ToolUseBlock(id="effect", name="Write", input={})],
            model="offline",
        )
        if shape != "request":
            yield UserMessage(
                content=[
                    ToolResultBlock(
                        tool_use_id="effect",
                        content="denied or supplied by host",
                        is_error=shape == "denial",
                    )
                ]
            )
        yield ResultMessage(
            subtype="success",
            duration_ms=1,
            duration_api_ms=1,
            is_error=False,
            num_turns=1,
            session_id="s",
        )

    async def checkpoint(*args: Any, **kwargs: Any) -> str:
        del args, kwargs
        return "checkpoint"

    monkeypatch.setattr(_runner, "query", scripted)
    monkeypatch.setattr(ClaudeAgentSdkRunner, "_checkpoint", checkpoint)
    runner = _runner_in(tmp_path, tool_policy=_policy())
    injected = {"effect": ToolOutcome("host result")} if shape == "injected" else {}
    output = await runner._run_engine(_input(_policy()), injected, "s", False)
    assert not output.is_error
    assert output.checkpoint == "checkpoint"


@pytest.mark.parametrize(
    "field",
    [
        "start_to_close",
        "heartbeat_timeout",
        "schedule_to_close",
        "schedule_to_start",
        "silence_timeout",
    ],
)
async def test_policy_duration_wire_roundtrip(tmp_path: Path, field: str) -> None:
    from datetime import timedelta

    from temporalio.converter import DataConverter

    durations: dict[str, Any] = {field: timedelta(seconds=1.25)}
    policy = ToolPolicy((ToolPolicyEntry("Bash", "effect", "claimed", **durations),))
    agent = DurableClaudeAgent(tool_policy=policy)
    assert agent._tool_policy == policy
    original = _input(policy)
    converter = DataConverter.default
    wire = await converter.encode([original])
    values = await converter.decode(wire, [SegmentInput])
    decoded = values[0]
    assert isinstance(decoded, SegmentInput)
    rebuilt = _runner_in(tmp_path, tool_policy=policy)._effective_policy(decoded)
    assert rebuilt == policy
    assert rebuilt is not None and rebuilt.policy_version == policy.policy_version
    assert getattr(rebuilt.entries[0], field) == timedelta(seconds=1.25)


@pytest.mark.parametrize(
    "malformed",
    [
        "not JSON",
        "{}",
        '[{"name":"Bash"}]',
    ],
)
async def test_policy_wire_rejected_before_version_or_store(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, malformed: str
) -> None:
    async def must_not_start(*args: Any, **kwargs: Any) -> Any:
        del args, kwargs
        raise AssertionError("Invalid policy must not touch engine or session store")

    monkeypatch.setattr(ClaudeAgentSdkRunner, "_engine_version", must_not_start)
    monkeypatch.setattr(ClaudeAgentSdkRunner, "_start", must_not_start)
    inp = _input(_policy())
    inp.tool_policy = malformed
    with pytest.raises(ValueError):
        await _runner_in(tmp_path).run(inp, 1)


@pytest.mark.parametrize(
    "shape", ["stream_then_runtime", "hook_then_result_error", "effect_and_mirror"]
)
async def test_policy_execution_fault_wins_over_query_and_store_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, shape: str
) -> None:
    from claude_agent_sdk import MirrorErrorMessage, ResultError

    async def scripted(**kwargs: Any) -> AsyncIterator[Any]:
        yield SystemMessage(subtype="init", data={"claude_code_version": "2.1.274"})
        yield AssistantMessage(
            content=[ToolUseBlock(id="effect", name="Write", input={})],
            model="offline",
        )
        if shape == "hook_then_result_error":
            monkeypatch.setenv("TCA_POLICY_MODE", "1")
            monkeypatch.setenv("TCA_HOOK_DIR", kwargs["options"].env["TCA_HOOK_DIR"])
            _defer_hook.decide(
                {
                    "hook_event_name": "PostToolUse",
                    "tool_name": "Write",
                    "tool_use_id": "effect",
                }
            )
            raise ResultError(
                "temporary engine failure", {"subtype": "error_during_execution"}
            )
        yield UserMessage(
            content=[
                ToolResultBlock(tool_use_id="effect", content="written", is_error=False)
            ]
        )
        if shape == "stream_then_runtime":
            raise RuntimeError("temporary transport failure")
        yield MirrorErrorMessage(
            subtype="mirror_error", data={}, error="store unavailable"
        )
        yield ResultMessage(
            subtype="success",
            duration_ms=1,
            duration_api_ms=1,
            is_error=False,
            num_turns=1,
            session_id="s",
        )

    async def no_checkpoint(*args: Any, **kwargs: Any) -> Any:
        del args, kwargs
        raise AssertionError("An observed effect must not commit or retry")

    monkeypatch.setattr(_runner, "query", scripted)
    monkeypatch.setattr(ClaudeAgentSdkRunner, "_checkpoint", no_checkpoint)
    output = await _runner_in(tmp_path, tool_policy=_policy())._run_engine(
        _input(_policy()), {}, "s", False
    )
    assert output.is_error and output.error and "Write" in output.error
    assert output.checkpoint is None and output.deferred is None


async def test_policy_query_failure_without_observation_still_reraises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def scripted(**kwargs: Any) -> AsyncIterator[Any]:
        del kwargs
        yield SystemMessage(subtype="init", data={"claude_code_version": "2.1.274"})
        raise RuntimeError("transport failed without executing a tool")

    monkeypatch.setattr(_runner, "query", scripted)
    with pytest.raises(RuntimeError, match="without executing"):
        await _runner_in(tmp_path, tool_policy=_policy())._run_engine(
            _input(_policy()), {}, "s", False
        )


def test_policy_pause_fault_does_not_claim_no_effect_ran() -> None:
    from types import SimpleNamespace

    for marker, deferred, answered in (
        (None, SimpleNamespace(id="answered"), {"answered"}),
        ("paused", None, set()),
    ):
        error = _runner.ClaudeAgentSdkRunner._pause_contract_problem(
            [], marker, deferred, answered, "test", None, policy_mode=True
        )
        assert error and "Execution safety" in error
        assert "nothing ran outside Temporal" not in error


async def test_policy_stopped_hook_does_not_claim_no_effect_ran(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def scripted(**kwargs: Any) -> AsyncIterator[Any]:
        del kwargs
        yield SystemMessage(subtype="init", data={"claude_code_version": "2.1.274"})
        yield UserMessage(
            content=[
                ToolResultBlock(
                    tool_use_id="denied", content=_defer_hook.STOPPED, is_error=True
                )
            ]
        )
        yield ResultMessage(
            subtype="success",
            duration_ms=1,
            duration_api_ms=1,
            is_error=False,
            num_turns=1,
            session_id="s",
        )

    monkeypatch.setattr(_runner, "query", scripted)
    output = await _runner_in(tmp_path, tool_policy=_policy())._run_engine(
        _input(_policy()), {}, "s", False
    )
    assert output.is_error and output.error
    assert "No tool ran" not in output.error
    assert "does not prove" in output.error


def _install_hook_policy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, include_skill: bool = False
) -> None:
    monkeypatch.setenv("TCA_POLICY_MODE", "1")
    monkeypatch.setenv("TCA_HOOK_DIR", str(tmp_path))
    monkeypatch.delenv("TCA_ANSWERED_IDS", raising=False)
    entries = _policy().entries
    if include_skill:
        entries = (*entries, ToolPolicyEntry("Skill", "read"))
    (tmp_path / "policy.json").write_text(
        json.dumps(
            {
                "entries": json.loads(ToolPolicy(entries).canonical_json()),
                "workspace_root": str(tmp_path),
            }
        )
    )


@pytest.mark.parametrize("name", ["Write", "Bash", "AskUserQuestion"])
def test_identical_paused_call_reannouncement_redefers_without_new_slot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    _install_hook_policy(tmp_path, monkeypatch)
    event = {
        "tool_name": name,
        "tool_use_id": "paused",
        "tool_input": {"same": "payload"},
    }
    assert _defer_hook.decide(event)["permissionDecision"] == "defer"
    marker = tmp_path / "paused_call"
    assert json.loads(marker.read_text())["id"] == "paused"
    assert _defer_hook.decide(dict(event))["permissionDecision"] == "defer"
    assert json.loads(marker.read_text())["id"] == "paused"


@pytest.mark.parametrize("name", ["Write", "Bash", "AskUserQuestion"])
def test_answered_call_reannouncement_redefers_without_paused_slot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    _install_hook_policy(tmp_path, monkeypatch)
    monkeypatch.setenv("TCA_ANSWERED_IDS", "answered")
    event = {"tool_name": name, "tool_use_id": "answered", "tool_input": {}}
    assert _defer_hook.decide(event)["permissionDecision"] == "defer"
    assert not (tmp_path / "paused_call").exists()
    assert _defer_hook.decide(dict(event))["permissionDecision"] == "defer"
    assert not (tmp_path / "paused_call").exists()


@pytest.mark.parametrize(
    "name",
    [
        "Read",
        "Grep",
        "Glob",
        "Skill",
        "Write",
        "Edit",
        "Bash",
        "AskUserQuestion",
    ],
)
def test_every_new_call_after_pause_is_denied(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    _install_hook_policy(tmp_path, monkeypatch, include_skill=True)
    assert (
        _defer_hook.decide(
            {
                "tool_name": "Write",
                "tool_use_id": "paused",
                "tool_input": {},
            }
        )["permissionDecision"]
        == "defer"
    )
    denied = _defer_hook.decide(
        {
            "tool_name": name,
            "tool_use_id": "new-call",
            "tool_input": {"file_path": "inside"},
        }
    )
    assert denied["permissionDecision"] == "deny"
    assert denied["permissionDecisionReason"] == _defer_hook.ONE_AT_A_TIME
    assert json.loads((tmp_path / "paused_call").read_text())["id"] == "paused"


def test_read_cannot_reuse_paused_call_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install_hook_policy(tmp_path, monkeypatch)
    assert (
        _defer_hook.decide(
            {
                "tool_name": "Bash",
                "tool_use_id": "paused",
                "tool_input": {},
            }
        )["permissionDecision"]
        == "defer"
    )
    denied = _defer_hook.decide(
        {
            "tool_name": "Read",
            "tool_use_id": "paused",
            "tool_input": {"file_path": "inside"},
        }
    )
    assert denied["permissionDecision"] == "deny"
    assert denied["permissionDecisionReason"] == _defer_hook.ONE_AT_A_TIME


@pytest.mark.parametrize(
    "name",
    [
        "Read",
        "Grep",
        "Glob",
        "Skill",
        "Write",
        "Edit",
        "Bash",
        "AskUserQuestion",
        "Unknown",
        "mcp__durable__Write",
    ],
)
@pytest.mark.parametrize("identity", ["new-call", "paused"])
def test_every_tool_is_denied_after_stop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, identity: str
) -> None:
    _install_hook_policy(tmp_path, monkeypatch, include_skill=True)
    assert (
        _defer_hook.decide(
            {
                "tool_name": "Write",
                "tool_use_id": "paused",
                "tool_input": {},
            }
        )["permissionDecision"]
        == "defer"
    )
    (tmp_path / "stop").touch()
    denied = _defer_hook.decide(
        {
            "tool_name": name,
            "tool_use_id": identity,
            "tool_input": {"file_path": "inside"},
        }
    )
    assert denied["permissionDecision"] == "deny"
    assert denied["permissionDecisionReason"]
    assert json.loads((tmp_path / "paused_call").read_text())["id"] == "paused"


def test_listed_skill_without_package_validator_is_denied(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install_hook_policy(tmp_path, monkeypatch, include_skill=True)
    denied = _defer_hook.decide(
        {
            "tool_name": "Skill",
            "tool_use_id": "skill",
            "tool_input": {"skill": "unvalidated"},
        }
    )
    assert denied["permissionDecision"] == "deny"
    assert "validated package" in denied["permissionDecisionReason"]
    assert not (tmp_path / "paused_call").exists()


@pytest.mark.parametrize(
    "payload",
    [
        None,
        "not JSON",
        "{}",
        '{"entries": null}',
        '{"entries": [{}]}',
        '{"entries": {"Read": "read"}}',
        '{"entries": [{"name": "Write"}]}',
    ],
)
def test_missing_or_unreadable_policy_table_denies_with_reason(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, payload: str | None
) -> None:
    monkeypatch.setenv("TCA_POLICY_MODE", "1")
    monkeypatch.setenv("TCA_HOOK_DIR", str(tmp_path))
    if payload is not None:
        (tmp_path / "policy.json").write_text(payload)
    denied = _defer_hook.decide(
        {
            "tool_name": "Write",
            "tool_use_id": "call",
            "tool_input": {},
        }
    )
    assert denied["permissionDecision"] == "deny"
    assert "unavailable or invalid" in denied["permissionDecisionReason"]
    assert not (tmp_path / "paused_call").exists()


@pytest.mark.parametrize("configured", [False, True])
def test_missing_hook_folder_denies_every_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, configured: bool
) -> None:
    monkeypatch.setenv("TCA_POLICY_MODE", "1")
    if configured:
        monkeypatch.setenv("TCA_HOOK_DIR", str(tmp_path / "missing"))
    else:
        monkeypatch.delenv("TCA_HOOK_DIR", raising=False)
    denied = _defer_hook.decide(
        {
            "tool_name": "Bash",
            "tool_use_id": "call",
            "tool_input": {},
        }
    )
    assert denied["permissionDecision"] == "deny"
    assert denied["permissionDecisionReason"] == _defer_hook.STOPPED


@pytest.mark.parametrize("change", ["name", "input"])
def test_paused_identity_rejects_reused_id_with_changed_request(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, change: str
) -> None:
    _install_hook_policy(tmp_path, monkeypatch)
    event: dict[str, Any] = {
        "tool_name": "Write",
        "tool_use_id": "paused",
        "tool_input": {"file_path": "file", "content": "original"},
    }
    assert _defer_hook.decide(event)["permissionDecision"] == "defer"
    original = (tmp_path / "paused_call").read_text()
    changed = dict(event)
    if change == "name":
        changed["tool_name"] = "Bash"
    else:
        changed["tool_input"] = {"file_path": "file", "content": "changed"}
    assert _defer_hook.decide(changed)["permissionDecision"] == "deny"
    assert (tmp_path / "paused_call").read_text() == original


def test_paused_identity_accepts_equivalent_nested_object_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install_hook_policy(tmp_path, monkeypatch)
    first = {"file_path": "file", "content": {"left": 1, "right": [2, 3]}}
    second = {"content": {"right": [2, 3], "left": 1}, "file_path": "file"}
    for tool_input in (first, second):
        assert (
            _defer_hook.decide(
                {
                    "tool_name": "Write",
                    "tool_use_id": "paused",
                    "tool_input": tool_input,
                }
            )["permissionDecision"]
            == "defer"
        )
    stored = json.loads((tmp_path / "paused_call").read_text())
    assert stored == {"id": "paused", "name": "Write", "input": first}


@pytest.mark.parametrize(
    "marker",
    [
        "paused",
        "not JSON",
        "{}",
        '{"id":"paused","name":"Write"}',
        '{"id":"paused","name":"Write","input":{"value":NaN}}',
        '{"id":"paused","id":"changed","name":"Write","input":{}}',
    ],
)
def test_corrupt_or_legacy_marker_denies_without_replacement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, marker: str
) -> None:
    _install_hook_policy(tmp_path, monkeypatch)
    (tmp_path / "paused_call").write_text(marker)
    denied = _defer_hook.decide(
        {
            "tool_name": "Write",
            "tool_use_id": "paused",
            "tool_input": {},
        }
    )
    assert denied["permissionDecision"] == "deny"
    assert (tmp_path / "paused_call").read_text() == marker


@pytest.mark.parametrize(
    "tool_input",
    [
        {"number": float("nan")},
        {"number": float("inf")},
        {"tuple": (1, 2)},
        {1: "non string key"},
    ],
)
def test_non_json_policy_request_denies_without_claiming_slot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, tool_input: Any
) -> None:
    _install_hook_policy(tmp_path, monkeypatch)
    denied = _defer_hook.decide(
        {
            "tool_name": "Write",
            "tool_use_id": "paused",
            "tool_input": tool_input,
        }
    )
    assert denied["permissionDecision"] == "deny"
    assert not (tmp_path / "paused_call").exists()


@pytest.mark.parametrize(
    "raw",
    [
        '{"tool_name":"Write","tool_name":"Bash","tool_use_id":"paused","tool_input":{}}',
        '{"tool_name":"Write","tool_use_id":"paused","tool_input":{"value":NaN}}',
    ],
)
def test_policy_hook_main_rejects_duplicate_or_nonfinite_event_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    raw: str,
) -> None:
    import io
    from types import SimpleNamespace

    _install_hook_policy(tmp_path, monkeypatch)
    monkeypatch.setattr(sys, "stdin", SimpleNamespace(buffer=io.BytesIO(raw.encode())))
    _defer_hook.main()
    answer = json.loads(capsys.readouterr().out)["hookSpecificOutput"]
    assert answer["permissionDecision"] == "deny"
    assert not (tmp_path / "paused_call").exists()


def test_concurrent_different_policy_requests_have_only_one_winner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import threading
    from concurrent.futures import ThreadPoolExecutor

    _install_hook_policy(tmp_path, monkeypatch)
    barrier = threading.Barrier(2)

    def call(identity: str) -> tuple[str, dict[str, Any]]:
        barrier.wait()
        return identity, _defer_hook.decide(
            {
                "tool_name": "Write",
                "tool_use_id": identity,
                "tool_input": {"content": identity},
            }
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(call, ["first", "second"]))
    winners = [
        identity
        for identity, result in results
        if result["permissionDecision"] == "defer"
    ]
    assert len(winners) == 1
    assert json.loads((tmp_path / "paused_call").read_text()) == {
        "id": winners[0],
        "name": "Write",
        "input": {"content": winners[0]},
    }


@pytest.mark.parametrize(
    "change", ["id", "name", "input", "missing", "corrupt", "equivalent"]
)
async def test_runner_matches_returned_deferred_request_before_checkpoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, change: str
) -> None:
    from claude_agent_sdk import DeferredToolUse

    checkpoint_calls: list[bool] = []
    original_input = {"content": "original", "file_path": "file"}

    async def scripted(**kwargs: Any) -> AsyncIterator[Any]:
        yield SystemMessage(subtype="init", data={"claude_code_version": "2.1.274"})
        hook_dir = kwargs["options"].env["TCA_HOOK_DIR"]
        monkeypatch.setenv("TCA_POLICY_MODE", "1")
        monkeypatch.setenv("TCA_HOOK_DIR", hook_dir)
        if change != "missing":
            assert (
                _defer_hook.decide(
                    {
                        "tool_name": "Write",
                        "tool_use_id": "paused",
                        "tool_input": original_input,
                    }
                )["permissionDecision"]
                == "defer"
            )
        if change == "corrupt":
            Path(hook_dir, "paused_call").write_text("paused")
        yield ResultMessage(
            subtype="success",
            duration_ms=1,
            duration_api_ms=1,
            is_error=False,
            num_turns=1,
            session_id="s",
            stop_reason="tool_deferred",
            deferred_tool_use=DeferredToolUse(
                id="other" if change == "id" else "paused",
                name="Bash" if change == "name" else "Write",
                input={"content": "changed"}
                if change == "input"
                else {
                    "file_path": "file",
                    "content": "original",
                },
            ),
        )

    async def checkpoint(*args: Any, **kwargs: Any) -> str:
        del args, kwargs
        checkpoint_calls.append(True)
        return "checkpoint"

    monkeypatch.setattr(_runner, "query", scripted)
    monkeypatch.setattr(ClaudeAgentSdkRunner, "_checkpoint", checkpoint)
    output = await _runner_in(tmp_path, tool_policy=_policy())._run_engine(
        _input(_policy()), {}, "s", False
    )
    if change == "equivalent":
        assert not output.is_error and output.deferred is not None
        assert output.checkpoint == "checkpoint" and checkpoint_calls == [True]
    else:
        assert output.is_error and output.deferred is None
        assert output.checkpoint is None and checkpoint_calls == []


def _deep_marker_json() -> str:
    nested = "[" * 3000 + "0" + "]" * 3000
    return '{"id":"paused","name":"Write","input":{"nested":' + nested + "}}"


def test_deep_policy_input_denies_without_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install_hook_policy(tmp_path, monkeypatch)
    nested: Any = 0
    for _ in range(3000):
        nested = [nested]
    denied = _defer_hook.decide(
        {
            "tool_name": "Write",
            "tool_use_id": "paused",
            "tool_input": {"nested": nested},
        }
    )
    assert denied["permissionDecision"] == "deny"
    assert not (tmp_path / "paused_call").exists()


@pytest.mark.parametrize(
    "payload",
    [
        b'{"tool_name":"Write","tool_use_id":"paused","tool_input":{"nested":'
        + b"[" * 3000
        + b"0"
        + b"]" * 3000
        + b"}}",
        b"\xff",
    ],
)
def test_policy_main_denies_deep_json_or_invalid_utf8(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    payload: bytes,
) -> None:
    import io
    from types import SimpleNamespace

    _install_hook_policy(tmp_path, monkeypatch)
    monkeypatch.setattr(sys, "stdin", SimpleNamespace(buffer=io.BytesIO(payload)))
    _defer_hook.main()
    output = json.loads(capsys.readouterr().out)["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    assert not (tmp_path / "paused_call").exists()


def test_deep_policy_marker_denies_without_replacement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install_hook_policy(tmp_path, monkeypatch)
    marker = _deep_marker_json()
    (tmp_path / "paused_call").write_text(marker)
    denied = _defer_hook.decide(
        {
            "tool_name": "Write",
            "tool_use_id": "paused",
            "tool_input": {},
        }
    )
    assert denied["permissionDecision"] == "deny"
    assert (tmp_path / "paused_call").read_text() == marker


async def test_deep_marker_does_not_replace_runner_cancellation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import asyncio

    async def scripted(**kwargs: Any) -> AsyncIterator[Any]:
        yield SystemMessage(subtype="init", data={"claude_code_version": "2.1.274"})
        hook_dir = kwargs["options"].env["TCA_HOOK_DIR"]
        Path(hook_dir, "paused_call").write_text(_deep_marker_json())
        raise asyncio.CancelledError()

    monkeypatch.setattr(_runner, "query", scripted)
    with pytest.raises(asyncio.CancelledError):
        await _runner_in(tmp_path, tool_policy=_policy())._run_engine(
            _input(_policy()), {}, "s", False
        )
