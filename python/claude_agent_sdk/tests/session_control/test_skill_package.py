"""Package admission and native invocation through the retained isolated host."""

from __future__ import annotations

import asyncio
import dataclasses
import importlib.metadata
import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

from temporalio.claude_agent_sdk import (
    FileSessionStore,
    SegmentInput,
    ToolOutcome,
    ToolPolicy,
    ToolPolicyEntry,
    ToolSpec,
    _defer_hook,
    _runner,
)
from temporalio.claude_agent_sdk._skill_package import (  # pyright: ignore[reportMissingImports]
    ValidatedSkillPackage,
)

CLEAN = "---\nname: probe\ndescription: Controlled package proof\n---\nPACKAGE_BODY_SENTINEL\nRead resource.txt only.\n"
CASES = (
    "package-proof",
    "package-question",
    "package-shell",
    "package-empty",
    "package-default",
    "package-plugin",
    "package-user",
    "package-resume",
    "package-resume-main",
    "package-no-decision",
    "package-child",
)


def package(work: Path, text: str = CLEAN) -> Path:
    skill = work / ".claude/skills/probe"
    skill.mkdir(parents=True)
    path = skill / "SKILL.md"
    path.write_text(text)
    (skill / "resource.txt").write_text("RESOURCE_SENTINEL\n")
    return path


@pytest.mark.parametrize(
    "feature,reason",
    [
        ("!`touch marker`", "shell injection"),
        ("hooks: {}", "hooks"),
        ("context: fork", "context"),
        ("allowed-tools: Write", "allowed-tools"),
        ("", ""),
    ],
    ids=[
        "shell-injection",
        "skill-hook",
        "fork-context",
        "permission-grant",
        "clean-package",
    ],
)
def test_validator_fixture(tmp_path: Path, feature: str, reason: str) -> None:
    text = (
        CLEAN
        if not feature
        else CLEAN.replace(
            "description: Controlled package proof",
            "description: Controlled package proof\n" + feature,
        )
        if "!`" not in feature
        else CLEAN + feature
    )
    package(tmp_path, text)
    if reason:
        with pytest.raises(ValueError, match=reason):
            ValidatedSkillPackage.validate(str(tmp_path))
    else:
        assert ValidatedSkillPackage.validate(str(tmp_path)).names == ("probe",)


@pytest.mark.parametrize(
    "field",
    [
        "user-invocable",
        "disable-model-invocation",
        "agent",
        "model",
        "argument-hint",
        "when_to_use",
    ],
)
def test_unsupported_frontmatter(tmp_path: Path, field: str) -> None:
    package(tmp_path, CLEAN.replace("description:", field + ": true\ndescription:"))
    with pytest.raises(ValueError, match="Unsupported skill frontmatter"):
        ValidatedSkillPackage.validate(str(tmp_path))


@pytest.mark.parametrize(
    "route", ["commands", "settings.json", "hidden", "symlink", "ancestor"]
)
def test_alternate_package_route_refuses(tmp_path: Path, route: str) -> None:
    work = tmp_path / "work"
    work.mkdir()
    path = package(work)
    if route in {"commands", "settings.json"}:
        (work / ".claude" / route).write_text("unvalidated")
    elif route == "hidden":
        path.write_text(
            CLEAN.replace("description:", "user-invocable: false\ndescription:")
        )
    elif route == "symlink":
        (path.parent / "link").symlink_to(tmp_path)
    else:
        (tmp_path / ".claude").mkdir()
    with pytest.raises(ValueError):
        ValidatedSkillPackage.validate(str(work))


def test_changed_package_refuses(tmp_path: Path) -> None:
    path = package(tmp_path)
    validated = ValidatedSkillPackage.validate(str(tmp_path))
    path.write_text(CLEAN + "changed")
    with pytest.raises(ValueError, match="changed"):
        validated.verify(str(tmp_path))


@pytest.mark.parametrize(
    "text,reason",
    [
        (
            CLEAN.replace("name: probe", "name: probe\nname: probe"),
            "Unsupported skill frontmatter: name",
        ),
        (
            CLEAN.replace("description: Controlled package proof\n", ""),
            "Skill requires name and description",
        ),
        (CLEAN.replace("name: probe", "name: Other"), "Unsupported skill name"),
        (
            CLEAN.replace("name: probe", "name: other"),
            "Skill name must match its directory",
        ),
    ],
    ids=["duplicate-name", "missing-description", "invalid-name", "directory-mismatch"],
)
def test_package_metadata_refuses(tmp_path: Path, text: str, reason: str) -> None:
    package(tmp_path, text)
    with pytest.raises(ValueError, match=reason):
        ValidatedSkillPackage.validate(str(tmp_path))


@pytest.mark.parametrize("fault", ["changed", "missing"], ids=["changed", "missing"])
def test_skill_invocation_refuses_changed_inventory(tmp_path: Path, fault: str) -> None:
    skill = package(tmp_path)
    validated = ValidatedSkillPackage.validate(str(tmp_path))
    (tmp_path / "policy.json").write_text(
        json.dumps(
            {
                "workspace_root": str(tmp_path),
                "entries": [{"name": "Skill", "class": "read"}],
                "skill_package": validated.document(),
            }
        )
    )
    event = {
        "tool_name": "Skill",
        "tool_input": {"skill": "probe"},
        "tool_use_id": "skill-inventory",
    }
    decide: Any = _defer_hook._policy_decide
    assert decide(event, str(tmp_path)) == {"hookEventName": "PreToolUse"}
    if fault == "changed":
        skill.write_text(CLEAN + "Changed body.\n")
        reason = "Validated skill package changed."
    else:
        (tmp_path / ".claude").rename(tmp_path / "removed")
        reason = "Validated skill package cannot be verified."
    decision = decide(event, str(tmp_path))
    assert decision["permissionDecision"] == "deny"
    assert decision["permissionDecisionReason"] == reason
    assert not (tmp_path / "paused_call").exists()


def test_empty_package_refuses(tmp_path: Path) -> None:
    (tmp_path / ".claude/skills").mkdir(parents=True)
    with pytest.raises(ValueError, match="Skill package is empty"):
        ValidatedSkillPackage.validate(str(tmp_path))


@pytest.mark.parametrize(
    "inputs,reason",
    [
        ({"skill": "probe", "unexpected": True}, "Skill invocation is not validated."),
        ({"skill": "unknown"}, "Skill invocation is not validated."),
        ({"skill": "plugin:probe"}, "Skill invocation is not validated."),
        ({"skill": "probe", "args": False}, "Skill arguments must be text."),
        ({"skill": "probe", "args": None}, "Skill arguments must be text."),
        ({"skill": "probe", "args": []}, "Skill arguments must be text."),
        ({"skill": "probe", "args": {}}, "Skill arguments must be text."),
        ({"skill": "probe", "args": "controlled text"}, None),
    ],
    ids=[
        "extra-key",
        "unknown",
        "plugin",
        "bool",
        "null",
        "list",
        "object",
        "valid-text",
    ],
)
def test_skill_invocation_argument_boundary(
    tmp_path: Path, inputs: dict[str, Any], reason: str | None
) -> None:
    package(tmp_path)
    validated = ValidatedSkillPackage.validate(str(tmp_path))
    (tmp_path / "policy.json").write_text(
        json.dumps(
            {
                "workspace_root": str(tmp_path),
                "entries": [{"name": "Skill", "class": "read"}],
                "skill_package": validated.document(),
            }
        )
    )
    decide: Any = _defer_hook._policy_decide
    decision = decide(
        {"tool_name": "Skill", "tool_input": inputs, "tool_use_id": "skill-args"},
        str(tmp_path),
    )
    if reason is None:
        assert decision == {"hookEventName": "PreToolUse"}
    else:
        assert decision["permissionDecision"] == "deny"
        assert decision["permissionDecisionReason"] == reason
    assert not (tmp_path / "paused_call").exists()


@pytest.mark.parametrize("mode", ["hook", "callback"])
@pytest.mark.parametrize(
    "name,fault",
    [
        (name, fault)
        for name in ("Read", "Glob", "Grep")
        for fault in ("valid", "absolute", "parent", "symlink")
    ]
    + [
        (name, field + ":" + fault)
        for name in ("Glob", "Grep")
        for field in ("pattern", "glob")
        for fault in ("absolute", "parent", "backslash", "colon", "nontext")
    ]
    + [(name, "subtree") for name in ("Glob", "Grep")],
)
async def test_shared_read_confinement_without_native_engine(
    tmp_path: Path, mode: str, name: str, fault: str
) -> None:
    work = tmp_path / "work"
    work.mkdir()
    package(work)
    (work / "inside.txt").write_text("controlled read")
    outside = tmp_path / "outside.txt"
    outside.write_text("outside")
    policy = ToolPolicy(
        tuple(
            ToolPolicyEntry(tool, "read") for tool in ("Skill", "Read", "Glob", "Grep")
        )
    )
    validated = ValidatedSkillPackage.validate(str(work))
    hook_dir = tmp_path / "hooks"
    hook_dir.mkdir()
    (hook_dir / "policy.json").write_text(
        json.dumps(
            {
                "workspace_root": str(work),
                "entries": json.loads(policy.canonical_json()),
                "skill_package": validated.document(),
            }
        )
    )
    (hook_dir / "settings.json").write_text(json.dumps({"permissions": {}}))
    runner = _runner.ClaudeAgentSdkRunner(
        session_store=FileSessionStore(tmp_path / "store"),
        cwd=str(work),
        tool_policy=policy,
        skill_package=validated,  # pyright: ignore[reportCallIssue]
    )
    options = runner._engine_options(
        SegmentInput(
            prompt="scripted read",
            session_id="session",
            tools=[],
            tool_policy=policy.canonical_json(),
            builtin_tools=[entry.name for entry in policy.entries],
        ),
        {},
        "session",
        False,
        None,
        str(hook_dir),
        None,
    )
    assert options["setting_sources"] == ["project"]
    assert options["skills"] == ["probe"]
    assert options["plugins"] == []
    assert options["allowed_tools"] == []
    assert options["env"]["CLAUDE_CODE_DISABLE_BUNDLED_SKILLS"] == "1"
    assert json.loads((hook_dir / "settings.json").read_text())["permissions"][
        "ask"
    ] == [entry.name for entry in policy.entries]
    target = str(work / "inside.txt") if name == "Read" else str(work)
    reason = None
    if fault == "absolute":
        target = str(outside)
        reason = "Read path is outside the workspace root."
    elif fault == "parent":
        target = "../outside.txt"
        reason = "Read path is outside the workspace root."
    elif fault == "symlink":
        (work / "link").symlink_to(outside)
        target = str(work / "link")
        reason = "Read path is outside the workspace root."
    elif fault == "subtree":
        (work / "link").symlink_to(outside)
        reason = "Read search includes an outside symlink."
    inputs: dict[str, Any] = (
        {"file_path": target}
        if name == "Read"
        else {"path": target, "pattern": "inside"}
    )
    if ":" in fault:
        field, kind = fault.split(":")
        inputs[field] = {
            "absolute": "/outside",
            "parent": "../outside",
            "backslash": "outside\\path",
            "colon": "outside:path",
            "nontext": False,
        }[kind]
        reason = "Read pattern is outside the workspace root."
    if mode == "callback":
        decision = await options["can_use_tool"](name, inputs, object())
        assert decision.behavior == ("allow" if reason is None else "deny")
        if reason is not None:
            assert decision.message == reason
    else:
        decide: Any = _defer_hook._policy_decide
        decision = decide(
            {"tool_name": name, "tool_input": inputs, "tool_use_id": "read"},
            str(hook_dir),
        )
        if reason is None:
            assert decision == {"hookEventName": "PreToolUse"}
        else:
            assert decision["permissionDecision"] == "deny"
            assert decision["permissionDecisionReason"] == reason
    assert not (hook_dir / "paused_call").exists()


def test_package_root_symlink_refuses(tmp_path: Path) -> None:
    original = tmp_path / "original"
    work = tmp_path / "work"
    original.mkdir()
    work.mkdir()
    package(original)
    (work / ".claude").symlink_to(original / ".claude", target_is_directory=True)
    with pytest.raises(
        ValueError, match="Skill package requires a real .claude directory"
    ):
        ValidatedSkillPackage.validate(str(work))


async def test_native_package_shell_disable_settings_without_transport(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claude_agent_sdk import ResultMessage, SystemMessage

    package(tmp_path)
    policy = ToolPolicy((ToolPolicyEntry("Skill", "read"),))
    runner = _runner.ClaudeAgentSdkRunner(
        session_store=FileSessionStore(tmp_path / "store"),
        cwd=str(tmp_path),
        tool_policy=policy,
        skill_package=ValidatedSkillPackage.validate(str(tmp_path)),  # pyright: ignore[reportCallIssue]
    )
    observed = []

    async def scripted(*, prompt: Any, options: Any, control: Any):
        settings = json.loads(Path(options.settings).read_text())
        assert settings["disableSkillShellExecution"] is True
        assert settings["permissions"]["ask"] == ["Skill"]
        assert options.setting_sources == ["project"]
        assert options.skills == ["probe"]
        assert options.plugins == []
        assert options.allowed_tools == []
        assert options.env["CLAUDE_CODE_DISABLE_BUNDLED_SKILLS"] == "1"
        observed.append(prompt)
        yield SystemMessage(subtype="init", data={"claude_code_version": "2.1.274"})
        yield ResultMessage(
            subtype="success",
            duration_ms=1,
            duration_api_ms=0,
            is_error=False,
            num_turns=1,
            session_id="session",
            result="done",
        )

    monkeypatch.setattr(_runner, "query", scripted)

    async def checkpoint(*args: Any, **kwargs: Any):
        return "scripted-checkpoint"

    monkeypatch.setattr(runner, "_checkpoint", checkpoint)
    result = await runner._run_engine(
        SegmentInput(
            prompt="scripted",
            session_id="session",
            tools=[],
            tool_policy=policy.canonical_json(),
            builtin_tools=["Skill"],
        ),
        {},
        "session",
        False,
    )
    assert observed == ["scripted"]
    assert result.result == "done" and not result.is_error


async def test_changed_package_refuses_before_segment_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    skill = package(tmp_path)
    policy = ToolPolicy((ToolPolicyEntry("Skill", "read"),))
    runner = _runner.ClaudeAgentSdkRunner(
        session_store=FileSessionStore(tmp_path / "store"),
        cwd=str(tmp_path),
        tool_policy=policy,
        skill_package=ValidatedSkillPackage.validate(str(tmp_path)),  # pyright: ignore[reportCallIssue]
    )
    skill.write_text(CLEAN + "Changed body.\n")

    async def forbidden():
        pytest.fail("Changed package reached engine startup")

    monkeypatch.setattr(runner, "_engine_version", forbidden)
    with pytest.raises(ValueError, match="Validated skill package changed"):
        await runner.run(
            SegmentInput(
                prompt="scripted",
                session_id="session",
                tools=[],
                tool_policy=policy.canonical_json(),
                builtin_tools=["Skill"],
            ),
            1,
        )


def test_unknown_package_name_refuses_before_engine(tmp_path: Path) -> None:
    package(tmp_path)
    validated = dataclasses.replace(
        ValidatedSkillPackage.validate(str(tmp_path)), names=("unknown",)
    )
    with pytest.raises(ValueError, match="changed"):
        _runner.ClaudeAgentSdkRunner(
            session_store=FileSessionStore(tmp_path / "store"),
            cwd=str(tmp_path),
            tool_policy=ToolPolicy((ToolPolicyEntry("Skill", "read"),)),
            skill_package=validated,  # pyright: ignore[reportCallIssue]
        )


@pytest.mark.parametrize(
    "prompt", ["/probe", "/unknown", "\n /compact", "/plugin:probe"]
)
async def test_slash_dispatch_refuses_before_engine(
    tmp_path: Path, prompt: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    policy = ToolPolicy((ToolPolicyEntry("Skill", "read"),))
    runner = _runner.ClaudeAgentSdkRunner(
        session_store=FileSessionStore(tmp_path / "store"),
        cwd=str(tmp_path),
        tool_policy=policy,
    )

    async def forbidden() -> str:
        pytest.fail("Engine version/start reached")

    monkeypatch.setattr(runner, "_engine_version", forbidden)
    with pytest.raises(ValueError, match="slash dispatch"):
        await runner.run(
            SegmentInput(
                session_id="s",
                prompt=prompt,
                tools=[],
                builtin_tools=["Skill"],
                tool_policy=policy.canonical_json(),
            ),
            1,
        )


@pytest.mark.parametrize(
    "name", ["Agent", "Task", "mcp__plugin__Write", "plugin:Write"]
)
def test_child_and_plugin_tools_not_offered(name: str) -> None:
    with pytest.raises(ValueError):
        ToolPolicyEntry(name, "effect", "claimed")


@pytest.mark.parametrize("child_field", ["agent_id", "agent_type"])
def test_child_pending_call_fails_closed(tmp_path: Path, child_field: str) -> None:
    (tmp_path / "policy.json").write_text(
        json.dumps(
            {
                "workspace_root": str(tmp_path),
                "entries": [{"name": "Write", "class": "effect"}],
            }
        )
    )
    decide: Any = _defer_hook._policy_decide
    decision = decide(
        {
            child_field: "child",
            "tool_name": "Write",
            "tool_use_id": "pending",
            "tool_input": {"file_path": str(tmp_path / "marker"), "content": "effect"},
        },
        str(tmp_path),
    )
    assert decision["permissionDecision"] == "deny"
    assert (
        not (tmp_path / "marker").exists() and not (tmp_path / "paused_call").exists()
    )


@pytest.mark.parametrize("case", CASES)
async def test_actual_package_engine(
    case: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    if case != os.environ.get("BACKSTOP_CASE"):
        pytest.skip("Requires an isolated host grant")
    from host_session import HostSession, owned_runner
    from sdk_shutdown_probe import inventory, save
    from test_preventive_backstop import FakeMessagesAPI, engine_env, history_of

    class NativeAPI(FakeMessagesAPI):
        def write(
            self, handler: Any, body: dict[str, Any], blocks: list[dict[str, Any]]
        ) -> None:
            if any(
                tool.get("name")
                in {"Skill", "AskUserQuestion", "Agent", "mcp__durable__child_effect"}
                for tool in body.get("tools", [])
            ):
                blocks = self.decide(body)
            super().write(handler, body, blocks)

    root = Path("/state/package")
    root.mkdir()
    work = root / "work"
    work.mkdir()
    skill = package(work)
    safe = work / "safe"
    safe.mkdir()
    (safe / "input.txt").write_text("INPUT_SENTINEL\n")
    outside = root / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("OUTSIDE_SENTINEL\n")
    (work / "link").symlink_to(outside, target_is_directory=True)
    question = {
        "questions": [
            {
                "question": "Which color?",
                "header": "Color",
                "options": [
                    {"label": "Blue", "description": "Choose blue"},
                    {"label": "Red", "description": "Choose red"},
                ],
                "multiSelect": False,
            }
        ]
    }
    calls: list[tuple[str, dict[str, Any], bool | None]] = [
        ("Skill", {"skill": "probe"}, False)
    ]
    if case in {"package-proof", "package-no-decision"}:
        calls += [
            ("Read", {"file_path": str(skill.parent / "resource.txt")}, False),
            ("Glob", {"path": str(safe), "pattern": "*.txt"}, False),
            ("Grep", {"path": str(safe), "pattern": "INPUT_SENTINEL"}, False),
        ]
        for tool in ("Read", "Glob", "Grep"):
            for escape in ("symlink", "absolute", "parent"):
                inputs = (
                    {
                        "file_path": str(work / "link/secret.txt")
                        if escape == "symlink"
                        else str(outside / "secret.txt")
                        if escape == "absolute"
                        else "../outside/secret.txt"
                    }
                    if tool == "Read"
                    else {
                        "path": str(work / "link")
                        if escape == "symlink"
                        else str(work),
                        "pattern": "*.txt" if tool == "Glob" else "OUTSIDE_SENTINEL",
                    }
                )
                if tool != "Read" and escape != "symlink":
                    inputs["pattern" if tool == "Glob" else "glob"] = (
                        str(outside / "*.txt")
                        if escape == "absolute"
                        else "../outside/*.txt"
                    )
                calls.append((tool, inputs, True))
        calls += [
            ("Skill", {"skill": "unknown"}, True),
            ("Skill", {"skill": "code-review"}, True),
            ("Skill", {"skill": "plugin:probe"}, True),
            ("Write", {"file_path": str(safe / "marker"), "content": "EFFECT"}, None),
        ]
    elif case in {"package-question", "package-resume", "package-resume-main"}:
        calls = [("AskUserQuestion", question, None)]
        if case.startswith("package-resume"):
            calls += [
                ("Skill", {"skill": "probe"}, False),
                ("Read", {"file_path": str(skill.parent / "resource.txt")}, False),
                ("Read", {"file_path": str(outside / "secret.txt")}, True),
                ("Skill", {"skill": "plugin:probe"}, True),
            ]
    elif case == "package-child":
        calls = [
            (
                "Agent",
                {
                    "subagent_type": "probe-child",
                    "description": "Child deferral spike",
                    "prompt": "Call child_effect once and return its result.",
                },
                None,
            )
        ]

    def decide(body: dict[str, Any]) -> list[dict[str, Any]]:
        uses, _, _ = history_of(body)
        if case == "package-child" and not any(
            tool.get("name") == "Agent" for tool in body.get("tools", [])
        ):
            if not uses:
                return [
                    {
                        "type": "tool_use",
                        "id": "toolu_child",
                        "name": "mcp__durable__child_effect",
                        "input": {},
                    }
                ]
            return [{"type": "text", "text": "CHILD_FINISHED"}]
        position = len(uses)
        if position < len(calls):
            name, inputs, _ = calls[position]
            return [
                {
                    "type": "tool_use",
                    "id": f"toolu_package_{position}",
                    "name": name,
                    "input": inputs,
                }
            ]
        return [{"type": "text", "text": "PACKAGE_PROOF_FINISHED"}]

    policy = ToolPolicy(
        (
            ToolPolicyEntry("Skill", "read"),
            ToolPolicyEntry("Read", "read"),
            ToolPolicyEntry("Glob", "read"),
            ToolPolicyEntry("Grep", "read"),
            ToolPolicyEntry("Write", "effect", "repeatable"),
            ToolPolicyEntry("AskUserQuestion", "ask"),
        )
    )
    validated = ValidatedSkillPackage.validate(str(work))
    if case == "package-shell":
        skill.write_text(CLEAN + "\n!`touch /state/package/work/shell-marker`\n")
    original_options = _runner.ClaudeAgentSdkRunner._engine_options
    configured_options = []

    def options(self: Any, *args: Any, **kwargs: Any) -> dict[str, Any]:
        result = original_options(self, *args, **kwargs)
        if case == "package-child":
            from claude_agent_sdk import AgentDefinition

            result["agents"] = {
                "probe-child": AgentDefinition(
                    description="Controlled child probe",
                    prompt="Call child_effect once and return its result.",
                    tools=["mcp__durable__child_effect"],
                )
            }
        if case == "package-empty":
            result["setting_sources"] = []
        elif case == "package-default":
            result["setting_sources"] = None
        elif case == "package-user":
            user_skill = root / "config/skills/probe"
            user_skill.mkdir(parents=True, exist_ok=True)
            (user_skill / "SKILL.md").write_text(
                CLEAN.replace("PACKAGE_BODY_SENTINEL", "USER_SOURCE_SENTINEL")
            )
            result["setting_sources"] = ["user"]
        elif case == "package-plugin":
            plugin = root / "plugin"
            manifest = plugin / ".claude-plugin/plugin.json"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text(
                json.dumps({"name": "probe-plugin", "version": "1.0.0"})
            )
            plugin_skill = plugin / "skills/probe"
            plugin_skill.mkdir(parents=True, exist_ok=True)
            (plugin_skill / "SKILL.md").write_text(
                CLEAN.replace("PACKAGE_BODY_SENTINEL", "PLUGIN_SOURCE_SENTINEL")
            )
            result["setting_sources"] = []
            result["plugins"] = [{"type": "local", "path": str(plugin)}]
            result["skills"] = ["probe-plugin:probe"]
            calls[0] = ("Skill", {"skill": "probe-plugin:probe"}, False)
        if case in {"package-shell", "package-user", "package-plugin"}:
            # Diagnostic loading routes do not qualify as governed invocations.
            result["env"].pop("TCA_POLICY_MODE", None)
            result["allowed_tools"] = ["Skill", "Read"]
            result.pop("can_use_tool", None)
            settings = Path(result["settings"])
            contents = json.loads(settings.read_text())
            contents.pop("permissions", None)
            settings.write_text(json.dumps(contents))
        configured_options.append(
            {
                key: result.get(key)
                for key in (
                    "setting_sources",
                    "skills",
                    "plugins",
                    "tools",
                    "allowed_tools",
                    "permission_mode",
                )
            }
        )
        return result

    monkeypatch.setattr(_runner.ClaudeAgentSdkRunner, "_engine_options", options)
    if case == "package-shell":
        monkeypatch.setattr(ValidatedSkillPackage, "verify", lambda self, cwd: None)
    if case == "package-no-decision":
        monkeypatch.setattr(
            _runner,
            "_hook_entry",
            lambda: {
                "type": "command",
                "command": sys.executable,
                "args": [
                    str(Path(__file__).with_name("no_decision_hook.py")),
                    str(Path(_runner.__file__).with_name("_defer_hook.py")),
                ],
            },
        )
    api = NativeAPI(decide).start()
    session = os.environ["BACKSTOP_SESSION"]
    host = HostSession(Path("/state/host.db"))
    recovery_calls = []
    answer = {"questions": question["questions"], "answers": {"Which color?": "Blue"}}

    async def recover(call: Any) -> Any:
        from claude_agent_sdk import ToolResultBlock

        assert (
            call.id == "toolu_package_0"
            and call.name == "AskUserQuestion"
            and call.input == question
        )
        recovery_calls.append(dataclasses.asdict(call))
        return ToolResultBlock(call.id, json.dumps(answer, sort_keys=True), False)

    store: Any = FileSessionStore(root / "store")
    if case == "package-resume-main":
        from write_recovery import ProofStore

        store = ProofStore(root / "transcript.db", create=True)
    owner = owned_runner(
        host,
        os.environ["BACKSTOP_ATTEMPT"],
        session,
        session_store=store,
        recover_pending_tool=recover if case == "package-resume-main" else None,
        cwd=str(work),
        cli_path="/opt/claude",
        tool_policy=None if case == "package-child" else policy,
        skill_package=None if case == "package-child" else validated,
        env={
            **engine_env(api, str(root / "config")),
            "BACKSTOP_HOOK_LOG": str(root / "hook-log.jsonl"),
        },
    )
    report: dict[str, Any] = {
        "case": case,
        "before": inventory(),
        "live_model_calls": 0,
        "provider_spend_usd": 0,
        "sdk": importlib.metadata.version("claude-agent-sdk"),
        "python": sys.version,
    }
    try:
        inp = SegmentInput(
            session_id=session,
            prompt="Run the controlled proof.",
            tools=[
                ToolSpec(
                    "child_effect",
                    "Record a controlled child request",
                    {"type": "object", "properties": {}},
                )
            ]
            if case == "package-child"
            else [],
            builtin_tools=["Agent"]
            if case == "package-child"
            else [entry.name for entry in policy.entries],
            tool_policy=None if case == "package-child" else policy.canonical_json(),
            model="claude-haiku-4-5-20251001",
            max_turns=25,
        )
        result = await asyncio.wait_for(owner.run(inp, 1), 100)
        control = owner.session_control(session)
        assert control is not None and control.state.sdk_closed
        report["result"] = dataclasses.asdict(result)
        report["messages"] = [
            dataclasses.asdict(message) for message in control.messages
        ]
        report["options"] = configured_options
        _, _, history = history_of(api.requests[-1])
        report["tool_results"] = [dataclasses.asdict(row) for row in history]
        if case.startswith("package-resume"):
            assert result.deferred is not None and result.checkpoint is not None
            resumed = await asyncio.wait_for(
                owner.run(
                    dataclasses.replace(
                        inp,
                        prompt="Continue the controlled proof."
                        if case == "package-resume-main"
                        else None,
                        checkpoint=result.checkpoint,
                        injected={}
                        if case == "package-resume-main"
                        else {result.deferred.id: ToolOutcome(answer)},
                    ),
                    1,
                ),
                100,
            )
            resumed_control = owner.session_control(session)
            assert resumed_control is not None
            report["resumed_result"] = dataclasses.asdict(resumed)
            report["resumed_messages"] = [
                dataclasses.asdict(message) for message in resumed_control.messages
            ]
            _, _, resumed_history = history_of(api.requests[-1])
            report["resumed_tool_results"] = [
                dataclasses.asdict(row) for row in resumed_history
            ]
            report["recovery_calls"] = recovery_calls
            resumed_rows = [
                row for row in resumed_history if row.id != "toolu_package_0"
            ]
            report["resumed_callback_delivery"] = len(resumed_rows) == 4 and [
                row.is_error for row in resumed_rows
            ] == [False, False, True, True]
            if case == "package-resume-main":
                assert report["resumed_callback_delivery"]
            report["status"] = (
                "PASS" if report["resumed_callback_delivery"] else "DEFECT"
            )
        elif case == "package-child":
            assert result.is_error or result.deferred is not None
            assert any(
                getattr(message, "parent_tool_use_id", None) == "toolu_package_0"
                and any(
                    getattr(block, "id", None) == "toolu_child"
                    and getattr(block, "name", None) == "mcp__durable__child_effect"
                    for block in getattr(message, "content", [])
                )
                for message in control.messages
            )
            assert owner.runner.stub_calls == 0
            assert not (safe / "marker").exists()
            report["child_disposition"] = (
                "pauses" if result.deferred is not None else "fails closed"
            )
            report["status"] = "PASS"
        elif case == "package-question":
            assert result.deferred is not None
            assert (
                result.deferred.name == "AskUserQuestion"
                and result.deferred.input == question
            )
        elif case in {"package-proof", "package-no-decision"}:
            assert "PACKAGE_BODY_SENTINEL" in str(report["messages"])
            assert any(
                isinstance(receipt := getattr(message, "tool_use_result", None), dict)
                and receipt.get("commandName") == "probe"
                and receipt.get("success") is True
                for message in control.messages
            )
            if case == "package-proof":
                assert result.deferred is not None and result.deferred.name == "Write"
                assert len(history) == len(calls) - 1
            else:
                assert len(history) == len(calls) and history[-1].is_error
                assert "Policy denies engine execution of Write" in str(
                    history[-1].content
                )
            for row, (name, inputs, error) in zip(history, calls):
                assert (
                    row.name == name
                    and row.input == inputs
                    and (error is None or row.is_error is error)
                )
            assert any(
                isinstance(receipt := getattr(message, "tool_use_result", None), dict)
                and isinstance(file := receipt.get("file"), dict)
                and file.get("filePath") == str(skill.parent / "resource.txt")
                and file.get("content") == "RESOURCE_SENTINEL\n"
                for message in control.messages
            )
            assert "OUTSIDE_SENTINEL" not in str([row.content for row in history])
            assert not (safe / "marker").exists()
        elif case == "package-empty":
            assert history[0].is_error and "PACKAGE_BODY_SENTINEL" not in str(
                api.requests
            )
        else:
            assert not history[0].is_error
            sentinel = (
                "PLUGIN_SOURCE_SENTINEL"
                if case == "package-plugin"
                else "USER_SOURCE_SENTINEL"
                if case == "package-user"
                else "PACKAGE_BODY_SENTINEL"
            )
            assert sentinel in str(api.requests)
        assert not (work / "shell-marker").exists()
        assert api.errors == []
        report.setdefault("status", "PASS")
    except BaseException as exc:
        report.update(status="FAIL", error=type(exc).__name__ + ": " + str(exc))
        raise
    finally:
        report["after"] = inventory()
        save(root / "report.json", report)
        save(root / "requests.json", api.requests)
        api.stop()
