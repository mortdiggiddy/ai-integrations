"""Exercise production permission controls with the actual engine and a local provider."""

# ruff: noqa: E402

from __future__ import annotations

import asyncio
import dataclasses
import importlib.metadata
import json
import os
import runpy
import sys
import traceback
from pathlib import Path
from typing import Any

import pytest
from claude_agent_sdk import PermissionResultDeny

for parent in Path(__file__).resolve().parents:
    experiments = parent / "docs/skill-recovery/experiments"
    if (experiments / "host_session.py").exists():
        sys.path.insert(0, str(experiments))
        break

from host_session import HostSession, owned_runner
from sdk_shutdown_probe import inventory, save

from temporalio.claude_agent_sdk import (
    FileSessionStore,
    SegmentInput,
    ToolPolicy,
    ToolPolicyEntry,
    _runner,
)

helpers = next(
    root / "helpers/fake_messages_api.py"
    for root in (Path(__file__).resolve().parents[1], Path("/test-root/tests"))
    if (root / "helpers/fake_messages_api.py").is_file()
)
provider = runpy.run_path(str(helpers))
FakeMessagesAPI = provider["FakeMessagesAPI"]
engine_env = provider["engine_env"]
history_of = provider["history_of"]

CASES = (
    "write",
    "removed",
    "system-prompt",
    "extra-args",
    "combined-options",
    "bash-read",
    "bash-deny",
    "bash-defer",
    "skill-grant",
    "skill-removed",
    "skill-batch",
    "write-ask",
    "bash-ask",
    "bash-ask-defer",
    "skill-ask-batch",
    "skill-ask-removed-batch",
    "bash-ask-removed",
    "write-ask-defer",
    "edit-ask",
    "edit-removed",
    "ask-system-prompt",
    "ask-extra-args",
    "ask-combined-options",
)


@pytest.mark.parametrize(
    "key,value",
    [
        ("permission_mode", "bypassPermissions"),
        ("can_use_tool", lambda *args: None),
        ("permission_prompt_tool_name", "grant"),
        ("disallowed_tools", []),
        ("setting_sources", ["user", "project", "local"]),
    ],
    ids=[
        "permission_mode",
        "can_use_tool",
        "permission_prompt_tool_name",
        "disallowed_tools",
        "setting_sources",
    ],
)
def test_pinned_option_cannot_be_changed(tmp_path: Path, key: str, value: Any) -> None:
    policy = ToolPolicy((ToolPolicyEntry("Write", "effect", "repeatable"),))
    with pytest.raises(ValueError, match="Policy extra_options cannot set"):
        _runner.ClaudeAgentSdkRunner(
            session_store=FileSessionStore(tmp_path / "store"),
            cwd=str(tmp_path),
            tool_policy=policy,
            extra_options={key: value},
        )


class BuiltinAPI(FakeMessagesAPI):  # type: ignore[valid-type,misc]
    """Use the existing local provider for native tool requests as well as MCP."""

    def write(
        self, handler: Any, body: dict[str, Any], blocks: list[dict[str, Any]]
    ) -> None:
        if any(tool.get("name") == "Write" for tool in body.get("tools", [])):
            blocks = self.decide(body)
        super().write(handler, body, blocks)


def assert_prevented(
    marker: Path, callback: list[dict[str, Any]], history: Any
) -> None:
    """Require absent effect bytes and the production callback's exact denial."""
    assert not marker.exists(), "Engine created the effect marker"
    assert any(row["name"] == "Write" for row in callback)
    assert any(
        "Policy denies engine execution of Write" in str(row.content)
        for row in history
        if row.name == "Write" and row.is_error
    )


def assert_bash_prevented(callback: list[dict[str, Any]], history: Any) -> None:
    """Require both denied Bash execution and the permission callback receipt."""
    assert any(row["name"] == "Bash" for row in callback), (
        "Bash permission callback was not invoked"
    )
    assert any(
        row.name == "Bash"
        and row.is_error
        and "Policy denies engine execution of Bash" in str(row.content)
        for row in history
    )


@pytest.mark.parametrize("case", CASES)
async def test_actual_engine_backstop(
    case: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    if case != os.environ.get("BACKSTOP_CASE"):
        pytest.skip("Each engine case requires its own retained host grant")
    root = Path("/state/backstop")
    root.mkdir()
    work = root / "work"
    work.mkdir()
    marker = work / "marker.txt"
    edit_target = work / "edit.txt"
    edit_target.write_text("BEFORE\n")
    hook_log = root / "hooks.jsonl"
    callback = []
    emitted = []
    policy = ToolPolicy(
        (
            ToolPolicyEntry("Write", "effect", "repeatable"),
            ToolPolicyEntry("Read", "read"),
            ToolPolicyEntry("Edit", "effect", "repeatable"),
            ToolPolicyEntry("Bash", "effect", "claimed"),
            ToolPolicyEntry("Skill", "read"),
        )
    )
    if case.startswith("skill"):
        package = work / ".claude/skills/backstop-probe"
        package.mkdir(parents=True)
        (package / "SKILL.md").write_text(
            "---\nname: backstop-probe\ndescription: Permission grant probe\n"
            "allowed-tools: Write\n---\nCreate marker.txt using Write.\n"
        )

    def decide(body: dict[str, Any]) -> list[dict[str, Any]]:
        uses, _, _ = history_of(body)
        if not uses:
            name = (
                "Skill"
                if case.startswith("skill")
                else "Read"
                if case.startswith("edit")
                else ("Bash" if case.startswith("bash") else "Write")
            )
            inputs = (
                {"skill": "backstop-probe"}
                if name == "Skill"
                else {
                    "file_path": str(edit_target),
                }
                if name == "Read"
                else {"command": "pwd"}
                if name == "Bash"
                else {"file_path": str(marker), "content": "BACKSTOP_MARKER\n"}
            )
            emitted.append(name)
            return [
                {
                    "type": "tool_use",
                    "id": "toolu_probe_1",
                    "name": name,
                    "input": inputs,
                }
            ]
        if case.startswith("edit") and "toolu_probe_2" not in uses:
            emitted.append("Edit")
            return [
                {
                    "type": "tool_use",
                    "id": "toolu_probe_2",
                    "name": "Edit",
                    "input": {
                        "file_path": str(edit_target),
                        "old_string": "BEFORE",
                        "new_string": "BACKSTOP_MARKER",
                    },
                }
            ]
        if case.startswith("skill") and "toolu_probe_2" not in uses:
            emitted.append("Write")
            blocks = [
                {
                    "type": "tool_use",
                    "id": "toolu_probe_2",
                    "name": "Write",
                    "input": {"file_path": str(marker), "content": "BACKSTOP_MARKER\n"},
                }
            ]
            if case.endswith("batch"):
                emitted.append("Write")
                blocks.append(
                    {
                        "type": "tool_use",
                        "id": "toolu_probe_3",
                        "name": "Write",
                        "input": {
                            "file_path": str(work / "second.txt"),
                            "content": "SECOND_EFFECT\n",
                        },
                    }
                )
            return blocks
        return [{"type": "text", "text": "PROBE_FINISHED"}]

    original_deny = _runner._deny_policy_permission

    async def deny(
        name: str, inputs: dict[str, Any], context: Any
    ) -> PermissionResultDeny:
        callback.append({"name": name, "input": inputs})
        answer = await original_deny(name, inputs, context)
        assert isinstance(answer, PermissionResultDeny)
        callback[-1]["reason"] = answer.message
        return answer

    monkeypatch.setattr(_runner, "_deny_policy_permission", deny)
    observer = Path(_runner.__file__).with_name("_defer_hook.py")
    if case not in {"bash-defer", "bash-ask-defer", "write-ask-defer"}:
        monkeypatch.setattr(
            _runner,
            "_hook_entry",
            lambda: {
                "type": "command",
                "command": sys.executable,
                "args": [
                    str(Path(__file__).with_name("no_decision_hook.py")),
                    str(observer),
                ],
            },
        )
    original_options = _runner.ClaudeAgentSdkRunner._engine_options
    permission_rules: list[dict[str, Any]] = []

    def options(
        self: _runner.ClaudeAgentSdkRunner, *args: Any, **kwargs: Any
    ) -> dict[str, Any]:
        result = original_options(self, *args, **kwargs)
        settings = Path(result["settings"])
        configured = json.loads(settings.read_text()).get("permissions")
        assert configured == {"ask": ["Write", "Edit", "Bash", "Skill"]}
        if case in {"removed", "skill-removed", "edit-removed"}:
            result.pop("can_use_tool")
            result["allowed_tools"] = ["Write", "Edit", "Bash", "Skill"]
        if "ask" not in case or "removed" in case:
            settings = Path(result["settings"])
            contents = json.loads(settings.read_text())
            contents.pop("permissions", None)
            settings.write_text(json.dumps(contents))
        if case in {"bash-deny", "bash-defer"}:
            settings = Path(result["settings"])
            contents = json.loads(settings.read_text())
            contents["permissions"] = {"deny": ["Bash"]}
            settings.write_text(json.dumps(contents))
        if case.startswith("skill"):
            # Expose the permission grant only in this diagnostic fixture.
            result["setting_sources"] = ["project"]
            result["allowed_tools"].append("Skill")
            settings = Path(result["settings"])
            contents = json.loads(settings.read_text())
            if "permissions" in contents:
                contents["permissions"]["ask"].remove("Skill")
            settings.write_text(json.dumps(contents))
        permission_rules.append(
            {
                "configured": configured,
                "effective": json.loads(settings.read_text()).get("permissions"),
            }
        )
        return result

    monkeypatch.setattr(_runner.ClaudeAgentSdkRunner, "_engine_options", options)
    extra_case = case.removeprefix("ask-")
    extra: dict[str, Any] = (
        {"system_prompt": "Permission probe", "extra_args": {}}
        if extra_case == "combined-options"
        else {"system_prompt": "Permission probe"}
        if extra_case == "system-prompt"
        else ({"extra_args": {}} if extra_case == "extra-args" else {})
    )
    api = BuiltinAPI(decide).start()
    session = os.environ["BACKSTOP_SESSION"]
    host = HostSession(Path("/state/host.db"))
    owner = owned_runner(
        host,
        os.environ["BACKSTOP_ATTEMPT"],
        session,
        session_store=FileSessionStore(root / "store"),
        cwd=str(work),
        cli_path="/opt/claude",
        tool_policy=policy,
        extra_options=extra,
        env={
            **engine_env(api, str(root / "config")),
            "BACKSTOP_HOOK_LOG": str(hook_log),
            "TCA_HOOK_LOG": str(root / "production-hooks.jsonl"),
        },
    )
    before = inventory()
    report: dict[str, Any] = {
        "case": case,
        "provider": "loopback scripted Messages API",
        "live_model_calls": 0,
        "provider_spend_usd": 0,
        "sdk": importlib.metadata.version("claude-agent-sdk"),
        "temporal_sdk": importlib.metadata.version("temporalio"),
        "python": sys.version,
    }
    try:
        result = await asyncio.wait_for(
            owner.run(
                SegmentInput(
                    session_id=session,
                    prompt="Run the permission probe once.",
                    tools=[],
                    builtin_tools=[entry.name for entry in policy.entries],
                    tool_policy=policy.canonical_json(),
                    model="claude-haiku-4-5-20251001",
                    max_turns=4,
                ),
                1,
            ),
            35,
        )
        control = owner.session_control(session)
        assert control is not None
        report.update(
            {
                "output": dataclasses.asdict(result),
                "callback_denials": callback,
                "emitted": emitted,
                "marker_exists": marker.exists(),
                "marker": marker.read_text() if marker.exists() else None,
                "sdk_state": dataclasses.asdict(control.state),
                "messages": [
                    {
                        "type": type(message).__name__,
                        "message": dataclasses.asdict(message),
                    }
                    for message in control.messages
                ],
            }
        )
        _, _, history = history_of(api.requests[-1])
        report["tool_results"] = [dataclasses.asdict(row) for row in history]
        assert api.errors == []
        assert emitted
        assert control.state.sdk_closed
        if case.startswith("skill"):
            skill = next(row for row in history if row.name == "Skill")
            assert skill.id == "toolu_probe_1"
            assert skill.input == {"skill": "backstop-probe"}
            assert not skill.is_error
            assert any(
                isinstance(grant := getattr(message, "tool_use_result", None), dict)
                and grant.get("commandName") == "backstop-probe"
                and grant.get("success") is True
                and grant.get("allowedTools") == ["Write"]
                for message in control.messages
            )
        if case in {"removed", "skill-removed"}:
            assert marker.read_text() == "BACKSTOP_MARKER\n"
            assert result.is_error and "Write" in (result.error or "")
            report["prevention_assertion"] = (
                "FAIL: engine created marker with backstop removed"
            )
            try:
                assert_prevented(marker, callback, history)
            except AssertionError as exc:
                assert str(exc).startswith("Engine created the effect marker")
                report["negative_control_failure"] = traceback.format_exc()
            else:
                pytest.fail("Removed backstop did not break the prevention assertion")
        elif case in {"bash-ask-defer", "write-ask-defer"}:
            assert result.deferred is not None
            expected = "Bash" if case.startswith("bash") else "Write"
            assert result.deferred.name == expected
            assert result.deferred.id == "toolu_probe_1"
            assert result.deferred.input == (
                {"command": "pwd"}
                if expected == "Bash"
                else {"file_path": str(marker), "content": "BACKSTOP_MARKER\n"}
            )
            assert callback == [] and not marker.exists()
            report["scoped_ask_preserves_deferral"] = True
        elif case in {"edit-ask", "edit-removed"}:
            read = next(row for row in history if row.name == "Read")
            assert read.id == "toolu_probe_1"
            assert read.input == {"file_path": str(edit_target)}
            assert not read.is_error
            assert any(
                isinstance(receipt := getattr(message, "tool_use_result", None), dict)
                and isinstance(file := receipt.get("file"), dict)
                and file.get("filePath") == str(edit_target)
                and file.get("content") == "BEFORE\n"
                for message in control.messages
            )
            if case == "edit-ask":
                assert edit_target.read_text() == "BEFORE\n"
                assert any(row["name"] == "Edit" for row in callback)
                assert any(
                    row.name == "Edit"
                    and row.is_error
                    and "Policy denies engine execution of Edit" in str(row.content)
                    for row in history
                )
                assert not result.is_error
            else:
                assert edit_target.read_text() == "BACKSTOP_MARKER\n"
                assert result.is_error and "Edit" in (result.error or "")
                with pytest.raises(AssertionError) as failure:
                    assert edit_target.read_text() == "BEFORE\n"
                report["negative_control_failure"] = str(failure.value)
                report["prevention_assertion"] = "FAIL: engine modified file"
            report["edit_bytes"] = edit_target.read_text()
        elif case == "skill-ask-batch":
            assert not marker.exists() and not (work / "second.txt").exists()
            assert sum(row["name"] == "Write" for row in callback) == 2
            assert_prevented(marker, callback, history)
            assert not result.is_error
            report["unrecorded_effects"] = 0
        elif case == "bash-defer":
            assert result.deferred is None
            bash = next(row for row in history if row.name == "Bash")
            assert bash.is_error and not result.is_error
            assert callback == [] and not marker.exists()
            report["scoped_deny_preserves_deferral"] = False
            report["prevention_assertion"] = (
                "FAIL: scoped deny blocks production Bash deferral"
            )
        elif case.startswith("bash"):
            bash = next(row for row in history if row.name == "Bash")
            report["bash_ran"] = not bash.is_error
            if case in {"bash-deny", "bash-ask"}:
                assert bash.is_error
                assert not result.is_error
                if case == "bash-ask":
                    assert_bash_prevented(callback, history)
            else:
                assert result.is_error and "Bash" in (result.error or "")
                if case == "bash-ask-removed":
                    assert not bash.is_error and callback == []
                    try:
                        assert_bash_prevented(callback, history)
                    except AssertionError as exc:
                        assert str(exc).startswith(
                            "Bash permission callback was not invoked"
                        )
                        report["negative_control_failure"] = traceback.format_exc()
                    else:
                        pytest.fail("Removing the ask rule did not expose Bash")
            assert not marker.exists()
        elif case in {"skill-grant", "skill-batch", "skill-ask-removed-batch"}:
            assert marker.read_text() == "BACKSTOP_MARKER\n"
            assert callback == []
            assert result.is_error and "Write" in (result.error or "")
            report["prevention_assertion"] = (
                "FAIL: skill grant bypassed permission callback"
            )
            if case.endswith("batch"):
                assert (work / "second.txt").read_text() == "SECOND_EFFECT\n"
                assert (
                    sum(row.name == "Write" and not row.is_error for row in history)
                    == 2
                )
                report["unrecorded_effects"] = 2
                if case == "skill-ask-removed-batch":
                    try:
                        assert_prevented(marker, callback, history)
                    except AssertionError as exc:
                        assert str(exc).startswith("Engine created the effect marker")
                        report["negative_control_failure"] = traceback.format_exc()
                    else:
                        pytest.fail(
                            "Removing the ask rules did not break the prevention assertion"
                        )
        else:
            assert_prevented(marker, callback, history)
            assert not result.is_error
            report["prevention_assertion"] = (
                "PASS: marker absent and permission callback denied Write"
            )
        report["status"] = (
            "DEFECT" if case in {"skill-grant", "skill-batch", "bash-defer"} else "PASS"
        )
    except BaseException as exc:
        report.update({"status": "FAIL", "error": type(exc).__name__ + ": " + str(exc)})
        raise
    finally:
        report["process_before"] = before
        report["permission_rules"] = permission_rules
        report["process_after"] = inventory()
        save(root / "report.json", report)
        save(root / "requests.json", api.requests)
        api.stop()
