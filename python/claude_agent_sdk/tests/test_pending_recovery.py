"""Production recovery options and conditional checkpoint advancement."""

from typing import Any

import pytest
from claude_agent_sdk import ClaudeAgentOptions

from temporalio.claude_agent_sdk import (
    ClaudeAgentSdkRunner,
    SegmentInput,
    ToolPolicy,
    ToolPolicyEntry,
    _runner,
)


class Store:
    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = [{"uuid": "original", "type": "assistant"}]
        self.commit = True
        self.calls = 0

    async def load(self, key: Any) -> list[Any]:
        del key
        return list(self.entries)

    async def append_if_unchanged(self, key: Any, expected: Any, entries: Any) -> bool:
        del key
        self.calls += 1
        if self.commit and self.entries[-1]["uuid"] == expected:
            self.entries.extend(entries)
            return True
        return False


async def recover(call: Any) -> Any:
    del call
    raise AssertionError("Option assembly must not invoke recovery")


def test_pending_recovery_requires_supported_sdk_and_managed_options(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy = ToolPolicy((ToolPolicyEntry("Write", "effect", "repeatable"),))
    with pytest.raises(ValueError, match="bound tool policy"):
        ClaudeAgentSdkRunner(session_store=Store(), recover_pending_tool=recover)
    with pytest.raises(ValueError, match="conditional session append"):
        ClaudeAgentSdkRunner(
            session_store=object(), tool_policy=policy, recover_pending_tool=recover
        )
    monkeypatch.setattr(ClaudeAgentOptions, "__dataclass_fields__", {})
    with pytest.raises(ValueError, match="Installed SDK"):
        ClaudeAgentSdkRunner(
            session_store=Store(), tool_policy=policy, recover_pending_tool=recover
        )
    for name in ("recover_pending_tool", "parallel_tool_recovery"):
        with pytest.raises(ValueError, match=name):
            ClaudeAgentSdkRunner(session_store=Store(), extra_options={name: recover})
    monkeypatch.setattr(
        ClaudeAgentOptions,
        "__dataclass_fields__",
        {"recover_pending_tool": None, "parallel_tool_recovery": None},
    )
    runner = ClaudeAgentSdkRunner(
        session_store=Store(), tool_policy=policy, recover_pending_tool=recover
    )
    inp = SegmentInput(
        session_id="s",
        prompt=None,
        tools=[],
        builtin_tools=["Write"],
        tool_policy=policy.canonical_json(),
    )

    def options(resume: bool) -> dict[str, Any]:
        return runner._engine_options(
            inp,
            session_id="s",
            injected={},
            resume=resume,
            guard="original" if resume else None,
            hook_dir="/tmp",
            durable_server=None,
        )

    assert "recover_pending_tool" not in options(False)
    assert options(True)["recover_pending_tool"] is recover
    assert options(True)["parallel_tool_recovery"] is False


@pytest.mark.asyncio
async def test_conditional_recovery_advances_guard_only_after_commit() -> None:
    store = Store()
    guard = _runner._guarded(store, "s", "original")
    key = {"session_id": "s"}
    recovered = [{"uuid": "recovered", "type": "user"}]
    assert not await guard.append_if_unchanged(key, "stale", recovered)
    assert store.calls == 0
    store.commit = False
    assert not await guard.append_if_unchanged(key, "original", recovered)
    assert await guard.load(key) == [{"uuid": "original", "type": "assistant"}]
    store.commit = True
    assert await guard.append_if_unchanged(key, "original", recovered)
    assert (await guard.load(key))[-1]["uuid"] == "recovered"
    store.entries.append({"uuid": "concurrent", "type": "assistant"})
    with pytest.raises(_runner._SessionMoved):
        await guard.append_if_unchanged(key, "recovered", [{"uuid": "unsafe"}])
    assert store.calls == 2


@pytest.mark.asyncio
async def test_conditional_recovery_rejects_wrong_session_or_missing_checkpoint() -> (
    None
):
    store = Store()
    guard = _runner._guarded(store, "s", "original")
    for key in ({"session_id": "other"}, {"session_id": "s", "subpath": "child"}):
        with pytest.raises(ValueError, match="main session"):
            await guard.append_if_unchanged(key, "original", [{"uuid": "recovered"}])
    with pytest.raises(ValueError, match="transcript checkpoint"):
        await guard.append_if_unchanged({"session_id": "s"}, "original", [])
    assert store.calls == 0
    assert not hasattr(
        _runner._guarded(object(), "s", "original"), "append_if_unchanged"
    )


@pytest.mark.asyncio
async def test_pending_recovery_preserves_denials_and_refuses_session_copy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        ClaudeAgentOptions,
        "__dataclass_fields__",
        {"recover_pending_tool": None, "parallel_tool_recovery": None},
    )
    store = Store()
    store.entries = [
        {"uuid": "assistant", "type": "assistant"},
        {
            "uuid": "defer",
            "type": "attachment",
            "attachment": {"type": "hook_deferred_tool", "toolUseID": "accepted"},
        },
        {"uuid": "denials", "type": "user"},
    ]
    policy = ToolPolicy((ToolPolicyEntry("Write", "effect", "repeatable"),))
    runner = ClaudeAgentSdkRunner(
        session_store=store, tool_policy=policy, recover_pending_tool=recover
    )
    assert await runner._checkpoint("s", "assistant", "accepted", None) == "denials"
    inp = SegmentInput(session_id="s", prompt=None, tools=[], checkpoint="denials")
    assert await runner._start(inp, 1) == ("s", True)
    with pytest.raises(ValueError, match="original session"):
        await runner._start(inp, 2)
    inp.fork = True
    with pytest.raises(ValueError, match="original session"):
        await runner._start(inp, 1)
