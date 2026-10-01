"""PreToolUse command hook for the Claude Code engine (settings based, not in process).

The engine runs this file as a plain script (standard library only, so it starts in
tens of milliseconds) for every durable tool call. It always answers "defer", so the
Workflow runs the tool as a Temporal Activity. It never answers "allow": on a resumed paused call, "allow" sends
the engine down its auto-resume path, where a later "defer" is ignored.

Parallel calls: the engine keeps only one paused call per run. So the first new
durable call in a run is deferred, and any other call after it in the same run,
durable or built-in, is denied with a clear message, so Claude asks again after the
paused call's result. (A built-in call allowed to run after the pause would have its
result cut from the session with the denials, and Claude would run it again.)

Stopped runs: when the segment Activity is cancelled or times out, the runner writes
``$TCA_HOOK_DIR/stop``, so an engine that is still shutting down cannot start another
built-in tool (a durable call still defers: that ends the run, and no one runs it).
If the folder is missing (the run ended, or the engine cannot see the Worker's
temporary folder), every call is denied, and the runner fails a step that finished
that way.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

ONE_AT_A_TIME = (
    "Only one tool call can run at a time. Your other tool call is running now. "
    "Call this tool again after you get that result."
)
"""The reason Claude sees when a second parallel call is denied."""

STOPPED = "This step was stopped (cancelled or timed out). Do not call tools."
"""The reason Claude sees when the segment is no longer running (the runner looks for it)."""


DURABLE_PREFIX = "mcp__durable__"
"""Names of durable tools as the engine sees them (the runner's ``PREFIX``)."""


def _deny(reason: str = ONE_AT_A_TIME) -> dict[str, Any]:
    return {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }


def decide(event: dict[str, Any]) -> dict[str, Any]:
    """Return the ``hookSpecificOutput`` for one PreToolUse event.

    Also records the paused call in ``$TCA_HOOK_DIR/paused_call``, so the runner can
    check that the engine really paused there.

    Args:
        event: The PreToolUse event the engine sent on stdin.

    Returns:
        The hook decision.
    """
    if os.environ.get("TCA_POLICY_MODE") == "1":
        return _policy_decide(event)
    tool_use_id = str(event.get("tool_use_id") or "")
    answered = set(os.environ.get("TCA_ANSWERED_IDS", "").split())
    run_dir = os.environ.get("TCA_HOOK_DIR")
    marker = os.path.join(run_dir, "paused_call") if run_dir else None
    output: dict[str, Any]
    if run_dir is not None and not os.path.isdir(run_dir):
        output = _deny(STOPPED)  # the run ended, or this hook cannot see its folder
    elif not str(event.get("tool_name") or "").startswith(DURABLE_PREFIX):
        # A built-in tool runs normally, unless the step was stopped or a durable
        # call already paused this run.
        if run_dir is not None and os.path.exists(os.path.join(run_dir, "stop")):
            output = _deny(STOPPED)
        elif marker is not None and os.path.exists(marker):
            output = _deny()
        else:
            output = {"hookEventName": "PreToolUse"}
    else:
        output = {"hookEventName": "PreToolUse", "permissionDecision": "defer"}
        # On resume the engine re-announces the call that was just answered. It must
        # not take the "one paused call per run" slot, or Claude's next call is denied.
        if marker is not None and tool_use_id not in answered:
            try:
                # Atomic: exactly one call wins the slot.
                fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    handle.write(tool_use_id)
            except FileExistsError:
                with open(marker, encoding="utf-8") as handle:
                    if handle.read().strip() != tool_use_id:
                        output = _deny()
    log = os.environ.get("TCA_HOOK_LOG")
    if log:  # debugging aid: one line per decision
        with open(log, "a", encoding="utf-8") as handle:
            decision = output.get("permissionDecision", "none")
            handle.write(f"{tool_use_id} {decision}\n")
    return output


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate JSON key")
        value[key] = item
    return value


def _reject_constant(value: str) -> Any:
    raise ValueError(f"Nonfinite JSON constant: {value}")


def _check_json(value: Any) -> None:
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("JSON object keys must be strings")
        for item in value.values():
            _check_json(item)
    elif isinstance(value, list):
        for item in value:
            _check_json(item)
    elif value is not None and not isinstance(value, (str, int, float, bool)):
        raise ValueError("Tool input must contain JSON values")


def _request_identity(identity: Any, name: Any, tool_input: Any) -> str:
    """Return strict canonical JSON for one complete paused request."""
    if not isinstance(identity, str) or not identity:
        raise ValueError("Policy tool call has no valid identity")
    if not isinstance(name, str) or not name:
        raise ValueError("Policy tool call has no valid name")
    if not isinstance(tool_input, dict):
        raise ValueError("Policy tool input must be an object")
    try:
        _check_json(tool_input)
        return json.dumps(
            {"id": identity, "name": name, "input": tool_input},
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except RecursionError as err:
        raise ValueError("Policy tool input nesting is too deep") from err


def _read_paused_request(marker: str) -> dict[str, Any]:
    """Read a complete strict JSON request, rejecting legacy or corrupt markers."""
    try:
        with open(marker, encoding="utf-8") as handle:
            request = json.load(
                handle,
                object_pairs_hook=_unique_object,
                parse_constant=_reject_constant,
            )
    except RecursionError as err:
        raise ValueError("Paused policy request nesting is too deep") from err
    if not isinstance(request, dict) or set(request) != {"id", "name", "input"}:
        raise ValueError("Invalid paused policy request")
    _request_identity(request["id"], request["name"], request["input"])
    return request


def _policy_decide(event: dict[str, Any]) -> dict[str, Any]:
    directory = os.environ.get("TCA_HOOK_DIR")
    if not directory or not os.path.isdir(directory):
        return _deny(STOPPED)
    try:
        with open(os.path.join(directory, "policy.json"), encoding="utf-8") as handle:
            document = json.load(handle)
        entries = {row["name"]: row for row in document["entries"]}
        name = event.get("tool_name")
        row = entries.get(name)
        event_name = event.get("hook_event_name", "PreToolUse")
        if event_name in ("PostToolUse", "PostToolUseFailure"):
            if row is None or row["class"] in ("effect", "ask"):
                with open(
                    os.path.join(directory, "observed_effects"), "a", encoding="utf-8"
                ) as handle:
                    handle.write(json.dumps({"name": name, "event": event_name}) + "\n")
            return {"hookEventName": event_name}
        if row is None:
            return _deny("Tool is not offered by policy.")
        if os.path.exists(os.path.join(directory, "stop")):
            return _deny(STOPPED)
        marker = os.path.join(directory, "paused_call")
        tool_use_id = event.get("tool_use_id")
        request = _request_identity(tool_use_id, name, event.get("tool_input", {}))
        if os.path.exists(marker):
            paused = _read_paused_request(marker)
            if (
                _request_identity(paused["id"], paused["name"], paused["input"])
                != request
                or row["class"] == "read"
            ):
                return _deny()
        if row["class"] == "read":
            if name == "Skill":
                return _deny("Skill requires a validated package configuration.")
            tool_input = event.get("tool_input") or {}
            path = tool_input.get("file_path" if name == "Read" else "path")
            if name == "Read" and (not isinstance(path, str) or not path):
                return _deny("Read requires a file path.")
            if path is None:
                path = document["workspace_root"]
            if not isinstance(path, str):
                return _deny("Read path must be a string.")
            root = document["workspace_root"]
            target = os.path.realpath(os.path.join(root, path))
            if os.path.commonpath([root, target]) != root:
                return _deny("Read path is outside the workspace root.")
            return {"hookEventName": "PreToolUse"}
        if row["class"] not in ("effect", "ask"):
            return _deny("Invalid policy classification.")
        answered = set(os.environ.get("TCA_ANSWERED_IDS", "").split())
        if tool_use_id not in answered:
            try:
                fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    handle.write(request)
            except FileExistsError:
                paused = _read_paused_request(marker)
                if (
                    _request_identity(paused["id"], paused["name"], paused["input"])
                    != request
                ):
                    return _deny()
        return {"hookEventName": "PreToolUse", "permissionDecision": "defer"}
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        return _deny("Policy configuration is unavailable or invalid.")


def main() -> None:
    """Read one event from stdin and print the decision.

    The engine sends UTF-8; read bytes, so a Windows code page cannot garble or
    reject the tool input. The answer is ASCII (``json.dumps`` escapes the rest).
    """
    payload = sys.stdin.buffer.read()
    if os.environ.get("TCA_POLICY_MODE") == "1":
        try:
            raw = payload.decode("utf-8")
            event = json.loads(
                raw, object_pairs_hook=_unique_object, parse_constant=_reject_constant
            )
            if not isinstance(event, dict):
                raise ValueError("Hook event must be an object")
        except (TypeError, ValueError, RecursionError):
            print(
                json.dumps({"hookSpecificOutput": _deny("Invalid policy hook event.")})
            )
            return
    else:
        event = json.loads(payload.decode("utf-8"))
    print(json.dumps({"hookSpecificOutput": decide(event)}))


if __name__ == "__main__":
    main()
