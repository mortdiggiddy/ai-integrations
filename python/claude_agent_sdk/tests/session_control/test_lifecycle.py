"""Offline SDK lifecycle contracts with no transport, provider or effect execution."""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any, cast

import pytest
from claude_agent_sdk import (
    ClaudeAgentOptions,
    PermissionResultDeny,
    ResultError,
    ResultMessage,
    SystemMessage,
)

from temporalio import activity
from temporalio.claude_agent_sdk import (
    ClaudeAgentSdkRunner,
    SegmentInput,
    ToolOutcome,
    _runner,
    _session_control,
)
from temporalio.claude_agent_sdk._session_control import (
    SdkSessionControl,
    SessionShutdownUnresolved,
)


def terminal() -> ResultMessage:
    return ResultMessage(
        subtype="success",
        duration_ms=1,
        duration_api_ms=0,
        is_error=False,
        num_turns=1,
        session_id="session",
        result="done",
    )


class Client:
    """Script lifecycle barriers without connecting to Claude Code."""

    instances: list[Client] = []

    def __init__(self, *, options: ClaudeAgentOptions) -> None:
        self.options = options
        self.connected = asyncio.Event()
        self.submitted = asyncio.Event()
        self.release = asyncio.Event()
        self.connect_gate: asyncio.Event | None = None
        self.close_gate: asyncio.Event | None = None
        self.interrupt_error: Exception | None = None
        self.close_error: Exception | None = None
        self.no_terminal = False
        self.hang_after_init = False
        self.continuous_nonterminal = False
        self.error_result: str | None = None
        self.prompts: list[Any] = []
        self.query_session_ids: list[str] = []
        self.interrupts = 0
        self.owner: asyncio.Task[Any] | None = None
        self.initial_input: Any = None
        self.closed = False
        self.instances.append(self)

    async def connect(self, prompt: Any = None) -> None:
        self.owner = asyncio.current_task()
        self.initial_input = prompt
        self.connected.set()
        if self.connect_gate is not None:
            await self.connect_gate.wait()

    async def query(self, prompt: Any, session_id: str = "default") -> None:
        assert asyncio.current_task() is self.owner
        self.prompts.append(prompt)
        self.query_session_ids.append(session_id)
        self.submitted.set()

    async def receive_messages(self) -> AsyncIterator[Any]:
        if self.initial_input is not None:
            async for message in self.initial_input:
                self.query_session_ids.append(message["session_id"])
                content = message["message"]["content"]
                if isinstance(content, str):
                    self.prompts.append(content)
                else:

                    async def replay() -> AsyncIterator[Any]:
                        yield message

                    self.prompts.append(replay())
                self.submitted.set()
        await self.release.wait()
        yield SystemMessage(subtype="init", data={"claude_code_version": "2.1.274"})
        while self.continuous_nonterminal:
            await asyncio.sleep(0.002)
            yield SystemMessage(subtype="progress", data={})
        if self.hang_after_init:
            await asyncio.Event().wait()
        if not self.no_terminal:
            result = terminal()
            if self.error_result is not None:
                result.is_error = True
                result.subtype = self.error_result
            yield result

    async def interrupt(self) -> None:
        self.interrupts += 1
        self.release.set()
        if self.interrupt_error is not None:
            raise self.interrupt_error

    async def disconnect(self) -> None:
        assert asyncio.current_task() is self.owner
        if self.close_gate is not None:
            await self.close_gate.wait()
        if self.close_error is not None:
            raise self.close_error
        self.closed = True


@pytest.fixture
def client_factory(monkeypatch: pytest.MonkeyPatch) -> Any:
    Client.instances = []
    configuration: dict[str, Any] = {}

    def factory(*, options: ClaudeAgentOptions) -> Client:
        client = Client(options=options)
        for name, value in configuration.items():
            setattr(client, name, value)
        return client

    monkeypatch.setattr(_session_control, "ClaudeSDKClient", factory)
    return configuration


async def collect(
    control: SdkSessionControl,
    options: ClaudeAgentOptions | None = None,
    prompt: Any = "work",
) -> list[Any]:
    return [m async for m in control.stream(prompt, options or ClaudeAgentOptions())]


async def started() -> Client:
    for _ in range(100):
        if Client.instances:
            return Client.instances[0]
        await asyncio.sleep(0)
    raise AssertionError("SDK client was not constructed")


async def test_one_owner_and_terminal_before_closed(
    tmp_path: Path, client_factory: Any
) -> None:
    control = SdkSessionControl(str(tmp_path))
    task = asyncio.create_task(collect(control))
    client = await started()
    await client.submitted.wait()
    assert control.active and not control.state.terminal_received
    client.release.set()
    messages = await task
    assert len(messages) == 2 and client.prompts == ["work"]
    assert control.state.terminal_received and control.state.sdk_closed
    assert not control.active and not control.state.stop_requested


async def test_cancel_drains_buffered_terminal_without_publishing(
    tmp_path: Path, client_factory: Any
) -> None:
    control = SdkSessionControl(str(tmp_path))
    task = asyncio.create_task(collect(control))
    client = await started()
    await client.submitted.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert client.interrupts == 1 and client.closed
    assert control.state.stop_requested and control.state.interrupt_acknowledged
    assert control.state.terminal_received and control.state.sdk_closed
    assert isinstance(control.messages[-1], ResultMessage)
    assert (tmp_path / "stop").exists()


@pytest.mark.parametrize("fault", ["interrupt_error", "close_error", "no_terminal"])
async def test_failed_stop_is_unresolved(
    tmp_path: Path, client_factory: Any, fault: str
) -> None:
    client_factory[fault] = (
        True if fault == "no_terminal" else RuntimeError("injected fault")
    )
    control = SdkSessionControl(str(tmp_path))
    task = asyncio.create_task(collect(control))
    client = await started()
    await client.submitted.wait()
    task.cancel()
    with pytest.raises(SessionShutdownUnresolved):
        await task
    assert control.state.shutdown_unresolved and control.state.stop_requested


async def test_cancel_during_connect_submits_nothing(
    tmp_path: Path, client_factory: Any
) -> None:
    gate = asyncio.Event()
    client_factory["connect_gate"] = gate
    control = SdkSessionControl(str(tmp_path))
    task = asyncio.create_task(collect(control))
    client = await started()
    await client.connected.wait()
    task.cancel()
    await asyncio.sleep(0)
    gate.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert client.prompts == [] and client.closed and client.interrupts == 0


async def test_wedged_close_retains_owner_and_unresolved_state(
    tmp_path: Path, client_factory: Any
) -> None:
    gate = asyncio.Event()
    client_factory["close_gate"] = gate
    control = SdkSessionControl(str(tmp_path), shutdown_timeout=0.01)
    task = asyncio.create_task(collect(control))
    client = await started()
    await client.submitted.wait()
    client.release.set()
    with pytest.raises(SessionShutdownUnresolved):
        await task
    assert control.state.terminal_received and not control.state.sdk_closed
    assert control.active and control.state.shutdown_unresolved
    gate.set()
    await asyncio.sleep(0)
    assert client.closed
    assert control.state.shutdown_unresolved


async def test_permission_stop_interrupts_without_changing_original_policy(
    tmp_path: Path, client_factory: Any
) -> None:
    original_calls: list[str] = []

    async def deny(name: str, inputs: Any, context: Any) -> Any:
        original_calls.append(name)
        return PermissionResultDeny(message="policy")

    options = ClaudeAgentOptions(can_use_tool=deny)
    control = SdkSessionControl(str(tmp_path))
    task = asyncio.create_task(collect(control, options))
    client = await started()
    await client.submitted.wait()
    permission = client.options.can_use_tool
    assert permission is not None
    before = await permission("Write", {}, cast(Any, None))
    assert isinstance(before, PermissionResultDeny)
    assert before.message == "policy"
    control.request_stop()
    after = await permission("Write", {}, cast(Any, None))
    assert isinstance(after, PermissionResultDeny)
    assert after.interrupt and original_calls == ["Write"]
    assert options.can_use_tool is deny
    with pytest.raises(asyncio.CancelledError):
        await task


async def runner_in(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> ClaudeAgentSdkRunner:
    monkeypatch.setattr(_runner, "_key_mismatch", lambda directory: None)
    runner = ClaudeAgentSdkRunner(
        session_store=object(),
        cwd=str(tmp_path),
        env={"ANTHROPIC_API_KEY": "synthetic"},
    )

    async def version() -> str:
        return "2.1.274"

    async def checkpoint(*args: Any) -> str:
        assert any(c.state.sdk_closed for c in runner._session_controls.values())
        return "recorded-checkpoint"

    monkeypatch.setattr(runner, "_engine_version", version)
    monkeypatch.setattr(runner, "_checkpoint", checkpoint)
    return runner


async def test_runner_stop_blocks_retry_before_start(
    tmp_path: Path, client_factory: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = await runner_in(tmp_path, monkeypatch)
    inp = SegmentInput(session_id=str(uuid.uuid4()), prompt="work", tools=[])
    task = asyncio.create_task(runner.run(inp, 1))
    client = await started()
    await client.submitted.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    with pytest.raises(SessionShutdownUnresolved, match="replacement"):
        await runner.run(inp, 2)
    assert len(Client.instances) == 1 and client.prompts == ["work"]


async def test_runner_normal_result_commits_after_sdk_close(
    tmp_path: Path, client_factory: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = await runner_in(tmp_path, monkeypatch)
    inp = SegmentInput(session_id=str(uuid.uuid4()), prompt="work", tools=[])
    task = asyncio.create_task(runner.run(inp, 1))
    client = await started()
    await client.submitted.wait()
    client.release.set()
    output = await task
    assert output.checkpoint == "recorded-checkpoint" and output.result == "done"
    assert client.query_session_ids == [inp.session_id]


async def test_structured_original_result_and_resume_options_preserved(
    tmp_path: Path, client_factory: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = await runner_in(tmp_path, monkeypatch)
    outcome = ToolOutcome(content="exact recorded outcome", is_error=True)
    inp = SegmentInput(
        session_id=str(uuid.uuid4()),
        prompt=None,
        tools=[],
        checkpoint="accepted-checkpoint",
        injected={"original-call": outcome},
    )
    task = asyncio.create_task(runner.run(inp, 1))
    client = await started()
    await client.submitted.wait()
    assert client.options.resume == inp.session_id
    assert client.query_session_ids == [inp.session_id]
    assert client.options.session_store is not runner._store
    stream = client.prompts[0]
    messages = [m async for m in stream]
    block = messages[0]["message"]["content"][0]
    assert block == {
        "type": "tool_result",
        "tool_use_id": "original-call",
        "content": "exact recorded outcome",
        "is_error": True,
    }
    client.release.set()
    await task


@pytest.mark.parametrize("subtype", ["error_max_turns", "error_during_execution"])
async def test_error_results_preserve_terminal_vs_retryable_behavior(
    tmp_path: Path, client_factory: Any, monkeypatch: pytest.MonkeyPatch, subtype: str
) -> None:
    client_factory["error_result"] = subtype
    runner = await runner_in(tmp_path, monkeypatch)
    inp = SegmentInput(session_id=str(uuid.uuid4()), prompt="work", tools=[])
    task = asyncio.create_task(runner.run(inp, 1))
    client = await started()
    await client.submitted.wait()
    client.release.set()
    if subtype == "error_max_turns":
        output = await task
        assert output.is_error and output.checkpoint is None
    else:
        with pytest.raises(ResultError):
            await task
    control = runner.session_control(inp.session_id)
    assert control is not None
    assert client.closed and control.state.terminal_received


async def test_activity_stop_intent_without_parent_cancel(
    tmp_path: Path, client_factory: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = await runner_in(tmp_path, monkeypatch)
    cancelled = asyncio.Event()
    monkeypatch.setattr(activity, "in_activity", lambda: True)
    monkeypatch.setattr(activity, "wait_for_cancelled", cancelled.wait)
    task = asyncio.create_task(
        runner.run(
            SegmentInput(session_id=str(uuid.uuid4()), prompt="work", tools=[]), 1
        )
    )
    client = await started()
    await client.submitted.wait()
    cancelled.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert client.interrupts == 1 and client.closed


async def test_cancel_after_terminal_during_close_does_not_claim_interrupt(
    tmp_path: Path, client_factory: Any
) -> None:
    gate = asyncio.Event()
    client_factory["close_gate"] = gate
    control = SdkSessionControl(str(tmp_path))
    task = asyncio.create_task(collect(control))
    client = await started()
    await client.submitted.wait()
    client.release.set()
    while not control.state.terminal_received:
        await asyncio.sleep(0)
    task.cancel()
    await asyncio.sleep(0)
    gate.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert control.state.terminal_received and control.state.sdk_closed
    assert control.state.stop_requested and not control.state.interrupt_acknowledged
    assert client.interrupts == 0


async def test_repeated_cancellation_retains_owner(
    tmp_path: Path, client_factory: Any
) -> None:
    gate = asyncio.Event()
    client_factory["close_gate"] = gate
    control = SdkSessionControl(str(tmp_path))
    task = asyncio.create_task(collect(control))
    client = await started()
    await client.submitted.wait()
    task.cancel()
    while not control.state.terminal_received:
        await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert (
        control.active and control.state.stop_requested and not control.state.sdk_closed
    )
    gate.set()
    await control.finish()
    assert control.state.sdk_closed


async def test_pinned_client_checks_resume_guard_before_transport(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claude_agent_sdk import ClaudeSDKClient
    from claude_agent_sdk._internal.transport import subprocess_cli

    calls: list[str] = []

    class Store:
        async def load(self, key: Any) -> Any:
            calls.append("load")
            return [{"type": "assistant", "uuid": "unaccepted-later-entry"}]

        async def append(self, key: Any, entries: Any) -> None:
            raise AssertionError("Guard refusal must not append")

    def forbidden_transport(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Guard refusal must precede transport construction")

    sid = str(uuid.uuid4())
    monkeypatch.setattr(subprocess_cli, "SubprocessCLITransport", forbidden_transport)
    client = ClaudeSDKClient(
        options=ClaudeAgentOptions(
            cwd=str(tmp_path),
            resume=sid,
            session_store=_runner._guarded(Store(), sid, "accepted-checkpoint"),
        )
    )
    with pytest.raises(RuntimeError) as error:
        await client.connect()
    assert _runner._moved(error.value)
    assert calls == ["load"]


async def test_runner_refuses_overlap_and_unresolved_close(
    tmp_path: Path, client_factory: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    client_factory["close_error"] = RuntimeError("unresolved teardown")
    runner = await runner_in(tmp_path, monkeypatch)
    inp = SegmentInput(session_id=str(uuid.uuid4()), prompt="work", tools=[])
    task = asyncio.create_task(runner.run(inp, 1))
    client = await started()
    await client.submitted.wait()
    with pytest.raises(SessionShutdownUnresolved):
        await runner.run(inp, 2)
    client.release.set()
    with pytest.raises(SessionShutdownUnresolved):
        await task
    with pytest.raises(SessionShutdownUnresolved):
        await runner.run(inp, 2)
    assert len(Client.instances) == 1


@pytest.mark.parametrize("fail_interrupt", [False, True])
async def test_stop_without_terminal_escalates_disconnect(
    tmp_path: Path, client_factory: Any, fail_interrupt: bool
) -> None:
    client_factory["hang_after_init"] = True
    if fail_interrupt:
        client_factory["interrupt_error"] = RuntimeError("interrupt refused")
    control = SdkSessionControl(str(tmp_path), shutdown_timeout=0.02)
    task = asyncio.create_task(collect(control))
    client = await started()
    await client.submitted.wait()
    task.cancel()
    with pytest.raises(SessionShutdownUnresolved):
        await task
    # The drain timeout can race the host wait deadline. The retained owner still
    # completes its SDK close; neither path accepts the missing terminal frame.
    for _ in range(100):
        if client.closed:
            break
        await asyncio.sleep(0.001)
    assert client.closed and control.state.shutdown_unresolved
    assert not control.state.terminal_received


async def test_stop_is_scoped_to_logical_session(
    tmp_path: Path, client_factory: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = await runner_in(tmp_path, monkeypatch)
    first = SegmentInput(session_id=str(uuid.uuid4()), prompt="first", tools=[])
    second = SegmentInput(session_id=str(uuid.uuid4()), prompt="second", tools=[])
    task_one = asyncio.create_task(runner.run(first, 1))
    client_one = await started()
    await client_one.submitted.wait()
    task_two = asyncio.create_task(runner.run(second, 1))
    while len(Client.instances) < 2:
        await asyncio.sleep(0)
    client_two = Client.instances[1]
    await client_two.submitted.wait()
    runner.stop_session(first.session_id)
    with pytest.raises(asyncio.CancelledError):
        await task_one
    assert client_one.closed and not client_two.closed and client_two.interrupts == 0
    client_two.release.set()
    output = await task_two
    assert output.result == "done"
    with pytest.raises(SessionShutdownUnresolved):
        await runner.run(first, 2)
    with pytest.raises(ValueError, match="No SDK exchange"):
        runner.stop_session("unowned-session")


async def test_continuous_messages_do_not_reset_stop_deadline(
    tmp_path: Path, client_factory: Any
) -> None:
    client_factory["continuous_nonterminal"] = True
    control = SdkSessionControl(str(tmp_path), shutdown_timeout=0.02)
    task = asyncio.create_task(collect(control))
    client = await started()
    await client.submitted.wait()
    control.request_stop()
    with pytest.raises(SessionShutdownUnresolved):
        await asyncio.wait_for(task, 0.5)
    assert client.closed and control.state.shutdown_unresolved
    assert not control.state.terminal_received


async def test_missing_terminal_without_cancellation_blocks_replacement(
    tmp_path: Path, client_factory: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    client_factory["no_terminal"] = True
    runner = await runner_in(tmp_path, monkeypatch)
    inp = SegmentInput(session_id=str(uuid.uuid4()), prompt="work", tools=[])
    task = asyncio.create_task(runner.run(inp, 1))
    client = await started()
    await client.submitted.wait()
    client.release.set()
    with pytest.raises(SessionShutdownUnresolved):
        await task
    assert client.closed
    control = runner.session_control(inp.session_id)
    assert control is not None and control.state.shutdown_unresolved
    with pytest.raises(SessionShutdownUnresolved):
        await runner.run(inp, 2)
    assert len(Client.instances) == 1
