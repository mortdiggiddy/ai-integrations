"""Own one SDK exchange and retain unresolved shutdown state for the host."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, AsyncIterator
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, cast

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    Message,
    PermissionResultDeny,
    ResultError,
    ResultMessage,
)


class SessionShutdownUnresolved(RuntimeError):
    """SDK shutdown lacks confirmation; the host must contain the owned processes."""


@dataclass
class SessionControlState:
    """SDK observations only; SDK closure does not prove host process containment."""

    stop_requested: bool = False
    interrupt_acknowledged: bool = False
    terminal_received: bool = False
    sdk_closed: bool = False
    shutdown_unresolved: bool = False
    interrupt_error: str | None = None
    close_error: str | None = None
    prompt_submission_started: bool = False


class SdkSessionControl:
    """Hold a client for one exchange, with no follow-up prompt after a stop."""

    def __init__(self, hook_dir: str, *, shutdown_timeout: float = 30) -> None:
        """Set the cooperative shutdown deadline and retain this exchange's receipts."""
        self.state = SessionControlState()
        self.messages: list[Message] = []
        self._hook_dir = hook_dir
        self._timeout = shutdown_timeout
        self._stop = asyncio.Event()
        self._queue: asyncio.Queue[Message | None] = asyncio.Queue()
        self._owner: asyncio.Task[None] | None = None
        self._error: BaseException | None = None
        self._interrupt_required = False
        self._deadline_expired = False
        self._stop_deadline: float | None = None
        self._response_finished = False
        self._terminal_observed = False

    def request_stop(self) -> None:
        """Deny subsequent hooks immediately and request cooperative SDK interruption."""
        if not self.state.stop_requested:
            self._stop_deadline = asyncio.get_running_loop().time() + self._timeout
        self.state.stop_requested = True
        if self.state.prompt_submission_started and not self._response_finished:
            self._interrupt_required = True
        self._stop.set()
        try:
            Path(self._hook_dir, "stop").touch()
        except OSError:
            pass  # An absent hook directory also denies execution.

    @property
    def active(self) -> bool:
        """Whether the SDK owner still holds this exchange."""
        return self._owner is not None and not self._owner.done()

    async def _interrupt(self, client: ClaudeSDKClient) -> None:
        await self._stop.wait()
        if not self._interrupt_required:
            return
        try:
            await asyncio.wait_for(client.interrupt(), self._timeout)
            self.state.interrupt_acknowledged = True
        except Exception as exc:
            self.state.interrupt_error = type(exc).__name__ + ": " + str(exc)

    async def _drive(self, prompt: Any, options: ClaudeAgentOptions) -> None:
        client: ClaudeSDKClient | None = None
        interrupter: asyncio.Task[None] | None = None
        try:
            client = ClaudeSDKClient(options=options)
            submit = asyncio.Event()

            async def initial_input() -> AsyncIterator[dict[str, Any]]:
                await submit.wait()
                if self.state.stop_requested:
                    return
                if isinstance(prompt, str):
                    yield {
                        "type": "user",
                        "message": {"role": "user", "content": prompt},
                        "parent_tool_use_id": None,
                        "session_id": options.resume or options.session_id or "default",
                    }
                else:
                    async for message in prompt:
                        if self.state.stop_requested:
                            return
                        yield message

            # Gate submission until startup completes. The SDK owns the finite
            # input stream and closes stdin after its run-ending result boundary.
            await client.connect(initial_input())
            if self.state.stop_requested:
                submit.set()
                return
            interrupter = asyncio.create_task(self._interrupt(client))
            self.state.prompt_submission_started = True
            submit.set()
            stream = cast("AsyncGenerator[Message, None]", client.receive_messages())

            async def receive_one() -> Message:
                return await stream.__anext__()

            pending: asyncio.Task[Message] | None = None
            try:
                while True:
                    remaining = (
                        self._stop_deadline - asyncio.get_running_loop().time()
                        if self._stop_deadline is not None
                        else None
                    )
                    if remaining is not None and remaining <= 0:
                        self.state.shutdown_unresolved = True
                        raise SessionShutdownUnresolved("SDK terminal drain timed out")
                    pending = asyncio.create_task(receive_one())
                    while not pending.done():
                        if self.state.interrupt_error is not None:
                            self.state.shutdown_unresolved = True
                            raise SessionShutdownUnresolved("SDK interrupt failed")
                        watched: set[asyncio.Task[Any]] = {pending}
                        if not interrupter.done():
                            watched.add(interrupter)
                        remaining = (
                            self._stop_deadline - asyncio.get_running_loop().time()
                            if self._stop_deadline is not None
                            else None
                        )
                        done, _ = await asyncio.wait(
                            watched,
                            timeout=remaining,
                            return_when=asyncio.FIRST_COMPLETED,
                        )
                        if not done or self.state.interrupt_error is not None:
                            self.state.shutdown_unresolved = True
                            raise SessionShutdownUnresolved(
                                "SDK interrupt failed or terminal drain timed out"
                            )
                    try:
                        message = pending.result()
                    except StopAsyncIteration:
                        self._response_finished = True
                        self.state.terminal_received = self._terminal_observed
                        break
                    self.messages.append(message)
                    self._queue.put_nowait(message)
                    if isinstance(message, ResultMessage):
                        self._terminal_observed = True
                        if message.is_error:
                            self._error = ResultError(
                                "Claude Code returned an error result: "
                                + message.subtype
                                + ": "
                                + (message.result or ""),
                                data=asdict(message),
                            )
            except ResultError:
                # The SDK can raise ResultError for a terminal CLI failure.
                self.state.terminal_received = True
                self._response_finished = True
                raise
            finally:
                if pending is not None:
                    if not pending.done():
                        pending.cancel()
                    try:
                        await pending
                    except (asyncio.CancelledError, Exception):
                        pass
                await stream.aclose()
        except BaseException as exc:
            self._error = exc
        finally:
            self._queue.put_nowait(None)
            if interrupter is not None:
                if self._interrupt_required:
                    await interrupter
                else:
                    interrupter.cancel()
                    try:
                        await interrupter
                    except asyncio.CancelledError:
                        pass
            try:
                # The SDK's anyio scopes must exit in the task that connected.
                if client is not None:
                    await client.disconnect()
                self.state.sdk_closed = True
            except BaseException as exc:
                self.state.close_error = type(exc).__name__ + ": " + str(exc)
                self.state.shutdown_unresolved = True
            if (
                self.state.prompt_submission_started
                and not self.state.terminal_received
            ):
                self.state.shutdown_unresolved = True
            if self._interrupt_required and (
                not self.state.terminal_received
                or not self.state.interrupt_acknowledged
                or not self.state.sdk_closed
            ):
                self.state.shutdown_unresolved = True

    async def finish(self) -> None:
        """Wait without cancelling SDK cleanup; retain a wedged owner for containment."""
        if self._owner is None:
            return
        if self._deadline_expired:
            raise SessionShutdownUnresolved("SDK interruption or closure is unresolved")
        done, _ = await asyncio.wait({self._owner}, timeout=self._timeout)
        if not done:
            self.state.shutdown_unresolved = True
            self._deadline_expired = True
            raise SessionShutdownUnresolved("SDK owner did not finish shutdown")
        if self._owner.cancelled() or self._owner.exception() is not None:
            self.state.shutdown_unresolved = True
            raise SessionShutdownUnresolved("SDK owner failed during cleanup")
        if self.state.shutdown_unresolved:
            raise SessionShutdownUnresolved("SDK interruption or closure is unresolved")

    async def stream(
        self, prompt: Any, options: ClaudeAgentOptions
    ) -> AsyncGenerator[Message, None]:
        """Submit once and drain messages before accepting closure or cancellation."""
        if self._owner is not None:
            raise RuntimeError("SDK session control is single use")
        permission = options.can_use_tool
        if permission is not None:

            async def guarded_permission(
                name: str, inputs: dict[str, Any], context: Any
            ) -> Any:
                if self.state.stop_requested:
                    return PermissionResultDeny(
                        message="Session stop requested", interrupt=True
                    )
                return await permission(name, inputs, context)

            options = replace(options, can_use_tool=guarded_permission)
        self._owner = asyncio.create_task(self._drive(prompt, options))
        try:
            while True:
                message = await self._queue.get()
                if message is None:
                    break
                if not self.state.stop_requested:
                    yield message
            await self.finish()
            if self.state.stop_requested:
                raise asyncio.CancelledError
            if self._error is not None:
                raise self._error
        except BaseException:
            if not self._owner.done():
                self.request_stop()
            await self.finish()
            raise
