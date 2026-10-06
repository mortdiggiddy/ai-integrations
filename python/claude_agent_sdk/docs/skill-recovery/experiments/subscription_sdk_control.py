"""Prepare and monitor one separately approved subscription connectivity probe."""

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import subprocess
import tempfile
import threading
import uuid
from pathlib import Path
from unittest.mock import patch

import subscription_sdk_run as previous

APPROVAL = "sdk-subscription-control-single-20261002"
MODEL = previous.MODEL
PROMPT = previous.PROMPT
IMAGE = previous.IMAGE


def options():
    from claude_agent_sdk import ClaudeAgentOptions

    return ClaudeAgentOptions(
        cli_path="/opt/claude",
        cwd="/work",
        model=MODEL,
        system_prompt="Return the requested text without explanation.",
        tools=[],
        allowed_tools=[],
        skills=[],
        setting_sources=[],
        mcp_servers='{"mcpServers":{}}',
        strict_mcp_config=True,
        permission_mode="default",
        max_turns=1,
        max_budget_usd=0.05,
        parallel_tool_recovery=False,
        thinking={"type": "disabled"},
        include_partial_messages=True,
        env={
            "CLAUDE_CODE_MAX_RETRIES": "0",
            "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "64",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        },
        extra_args={
            "disable-slash-commands": None,
            "no-chrome": None,
            "no-session-persistence": None,
            "prompt-suggestions": "false",
        },
    )


def identity():
    forbidden = {
        "CLAUDE_CODE_USE_BEDROCK",
        "CLAUDE_CODE_USE_VERTEX",
        "CLAUDE_CODE_USE_FOUNDRY",
        "CLAUDE_CODE_OAUTH_TOKEN",
    }
    if any(name.startswith("ANTHROPIC_") or name in forbidden for name in os.environ):
        raise PermissionError("Provider environment forbidden; values withheld")
    checked = previous.verify_sdk()
    if (
        hashlib.sha256(Path("/opt/claude").read_bytes()).hexdigest()
        != previous.CLI_HASH
    ):
        raise RuntimeError("CLI identity differs")
    version = subprocess.run(
        ["/opt/claude", "--version"],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    ).stdout.strip()
    if version != "2.1.274 (Claude Code)":
        raise RuntimeError("CLI version differs")
    return {
        "kind": "provenance",
        "sdk": importlib.metadata.version("claude-agent-sdk"),
        "cli": version,
        "cli_sha256": previous.CLI_HASH,
        "sdk_record_files": checked,
        "probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "helper_sha256": hashlib.sha256(
            Path(previous.__file__).read_bytes()
        ).hexdigest(),
    }


async def prepare():
    from claude_agent_sdk import query
    from claude_agent_sdk._internal.transport.subprocess_cli import (
        SubprocessCLITransport,
    )

    provenance = identity()
    selected = options()
    transport = SubprocessCLITransport(prompt=PROMPT, options=selected)
    transport._cli_path = "/opt/claude"
    command = transport._build_command()
    for flag, value in (
        ("--tools", ""),
        ("--model", MODEL),
        ("--max-turns", "1"),
        ("--max-budget-usd", "0.05"),
        ("--thinking", "disabled"),
        ("--mcp-config", '{"mcpServers":{}}'),
    ):
        if command[command.index(flag) + 1] != value:
            raise RuntimeError(f"SDK command differs at {flag}")
    for flag in (
        "--setting-sources=",
        "--include-partial-messages",
        "--strict-mcp-config",
    ):
        if flag not in command:
            raise RuntimeError(f"Missing SDK control {flag}")
    if selected.fallback_model or selected.resume or selected.plugins:
        raise RuntimeError("Fallback, resume and plugins are excluded")
    attempts = []

    async def refuse(self):
        attempts.append(type(self).__name__)
        raise PermissionError("Offline preparation forbids transport startup")

    generator = query(prompt=PROMPT, options=selected)
    with patch.object(SubprocessCLITransport, "connect", refuse):
        try:
            await anext(generator)
        except PermissionError:
            pass
        else:
            raise AssertionError("Transport startup guard did not fire")
        finally:
            await generator.aclose()
    if len(attempts) != 1:
        raise AssertionError("Unexpected transport admission count")
    print(
        json.dumps(
            {
                **provenance,
                "status": "offline_prepared",
                "sdk_command": command,
                "env": selected.env,
                "guarded_transport_attempts": 1,
                "model_cli_spawns": 0,
                "model_requests": 0,
            },
            indent=2,
        )
    )


async def container_query():
    from claude_agent_sdk import query

    if os.environ.get("DURABILITY_APPROVED_INVOCATION") != APPROVAL:
        raise PermissionError("Separate single invocation approval required")
    print(json.dumps(identity()), flush=True)
    generator = query(prompt=PROMPT, options=options())
    try:
        async for message in generator:
            print(
                json.dumps(
                    {
                        "kind": type(message).__name__,
                        "message": previous.encode(message),
                    }
                ),
                flush=True,
            )
    finally:
        await generator.aclose()


class Monitor:
    """Refuse failures at the host reader; this cannot gate the CLI producer."""

    def __init__(self, *, source_hashes=None):
        self.reason = None
        self.init_seen = False
        self.result_seen = False
        self.overage_clear_seen = False
        self.source_hashes = source_hashes
        self.provenance_seen = False

    def inspect(self, event):
        kind = event.get("kind")
        message = event.get("message", {})
        if self.result_seen:
            return "event_after_terminal_result"
        if kind == "provenance":
            if (
                self.provenance_seen
                or event.get("sdk") != "0.2.162"
                or event.get("cli_sha256") != previous.CLI_HASH
                or event.get("cli") != "2.1.274 (Claude Code)"
                or type(event.get("sdk_record_files")) is not int
                or event.get("sdk_record_files", 0) <= 0
                or any(
                    event.get(key) != value
                    for key, value in (self.source_hashes or {}).items()
                )
            ):
                return "unknown_provenance"
            self.provenance_seen = True
            return None
        if kind == "UserMessage":
            return "unexpected_user_continuation"
        if kind == "RateLimitEvent":
            info = message.get("rate_limit_info", {})
            raw = info.get("raw") or {}
            flags = [raw.get("isUsingOverage"), raw.get("overageInUse")]
            if any(flag is not False for flag in flags):
                return "ambiguous_active_or_unverifiable_overage"
            if (
                info.get("rate_limit_type") == "overage"
                or raw.get("rateLimitType") == "overage"
            ):
                return "ambiguous_active_or_unverifiable_overage"
            if info.get("status") not in {"allowed", "allowed_warning"}:
                return "rate_limit_refused_or_unverifiable"
            self.overage_clear_seen = True
            return None
        if kind == "SystemMessage":
            if message.get("subtype") == "init":
                data = message.get("data", {})
                if self.init_seen or data.get("model") != MODEL:
                    return "unknown_or_repeated_init_model"
                if any(
                    data.get(key) != []
                    for key in ("tools", "mcp_servers", "skills", "plugins")
                ):
                    return "unexpected_init_tools_or_configuration"
                self.init_seen = True
            return None
        if kind == "StreamEvent":
            raw = message.get("event", {})
            if (
                raw.get("type") == "message_delta"
                and raw.get("delta", {}).get("stop_reason") == "max_tokens"
            ):
                return "output_limit_partial_delta"
            if (
                raw.get("type") == "message_start"
                and raw.get("message", {}).get("model") != MODEL
            ):
                return "unknown_partial_model"
            if raw.get("type") == "content_block_start" and raw.get(
                "content_block", {}
            ).get("type") in {"tool_use", "server_tool_use"}:
                return "unexpected_partial_tool"
            return None
        if kind == "AssistantMessage":
            if (
                message.get("error") == "max_output_tokens"
                or message.get("stop_reason") == "max_tokens"
            ):
                return "output_limit_assistant"
            if message.get("error"):
                return "assistant_error"
            if message.get("model") != MODEL:
                return "unknown_assistant_model"
            if any(
                "name" in block or "input" in block or "id" in block
                for block in message.get("content", [])
            ):
                return "unexpected_assistant_tool"
            return None
        if kind == "ResultMessage":
            self.result_seen = True
            if (
                not self.provenance_seen
                or not self.init_seen
                or not self.overage_clear_seen
            ):
                return "missing_init_or_overage_observation"
            if (
                message.get("is_error") is not False
                or message.get("subtype") != "success"
                or type(message.get("num_turns")) is not int
                or message.get("num_turns") != 1
            ):
                return "failed_or_multiple_turn_result"
            if message.get("result") != "SDK_CONNECTIVITY_OK" or message.get("errors"):
                return "unexpected_final_result"
            model_usage = message.get("model_usage") or {}
            if set(model_usage) != {MODEL}:
                return "unknown_final_model"
            usage = message.get("usage") or {}
            for counts, keys in (
                (
                    usage,
                    (
                        "input_tokens",
                        "output_tokens",
                        "cache_read_input_tokens",
                        "cache_creation_input_tokens",
                    ),
                ),
                (
                    model_usage[MODEL],
                    (
                        "inputTokens",
                        "outputTokens",
                        "cacheReadInputTokens",
                        "cacheCreationInputTokens",
                    ),
                ),
            ):
                if any(
                    type(counts.get(key)) is not int or counts[key] < 0 for key in keys
                ):
                    return "unverifiable_final_usage"
            aggregate_thinking = (usage.get("output_tokens_details") or {}).get(
                "thinking_tokens"
            )
            if (
                usage["output_tokens"] > 64
                or (
                    aggregate_thinking is not None
                    and (type(aggregate_thinking) is not int or aggregate_thinking != 0)
                )
                or type(model_usage[MODEL].get("thinkingTokens")) is not int
                or model_usage[MODEL].get("thinkingTokens") != 0
            ):
                return "output_or_thinking_limit_exceeded"
            cost = message.get("total_cost_usd")
            if type(cost) not in (int, float) or not 0 <= cost < 0.05:
                return "unverifiable_or_exceeded_list_cost"
            return None
        return "unknown_event"

    def observe(self, event):
        if self.reason is None:
            self.reason = self.inspect(event)
        return self.reason


def consume(lines, stop, record, *, source_hashes=None):
    """Stop the owned container before asking the iterator for another line."""
    monitor = Monitor(source_hashes=source_hashes)
    for line in lines:
        try:
            event = json.loads(line)
            reason = monitor.observe(event)
        except (ValueError, TypeError, AttributeError):
            event = {"kind": "malformed_event"}
            reason = "malformed_event"
        record(event)
        if reason:
            stop(reason)
            return monitor, reason
    if not monitor.result_seen:
        stop("missing_terminal_result")
        return monitor, "missing_terminal_result"
    return monitor, None


def reserve():
    path = Path.home() / ".local/state/claude-recovery-proof" / f"{APPROVAL}.json"
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(
        path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600
    )
    with os.fdopen(descriptor, "w") as stream:
        stream.write(
            json.dumps({"approval": APPROVAL, "status": "consumed_before_launch"})
        )
        stream.flush()
        os.fsync(stream.fileno())
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def container_command(name, *, offline):
    here = Path(__file__).resolve().parent
    command = previous.container_args(
        login=not offline, network="none" if offline else "bridge"
    )
    command += [
        "--name",
        name,
        "--mount",
        f"type=bind,source={here / 'subscription_sdk_control.py'},target=/probe/subscription_sdk_control.py,readonly",
        "--mount",
        f"type=bind,source={here / 'subscription_sdk_run.py'},target=/probe/subscription_sdk_run.py,readonly",
        "--entrypoint",
        "/opt/python/bin/python3.13",
    ]
    if not offline:
        command += ["--env", f"DURABILITY_APPROVED_INVOCATION={APPROVAL}"]
    command += [
        IMAGE,
        "/probe/subscription_sdk_control.py",
        "--container-prepare" if offline else "--container-query",
    ]
    return command


def prepare_host():
    image = subprocess.run(
        ["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    ).stdout.strip()
    if image != IMAGE:
        raise RuntimeError("Image identity differs")
    status = subprocess.run(
        previous.container_args(login=True, network="none") + [IMAGE, "auth", "status"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    data = json.loads(status.stdout)
    if (
        status.returncode != 0
        or data.get("loggedIn") is not True
        or data.get("authMethod") != "claude.ai"
        or data.get("apiProvider") != "firstParty"
    ):
        raise RuntimeError("Retained subscription route not ready; raw status withheld")


def cleanup_passed(records):
    return bool(records) and all(
        record.get("confirmed_removed") is True
        and not any(key.endswith("error") for key in record)
        for record in records
    )


def execute():
    prepare_host()
    root = Path(tempfile.mkdtemp(prefix="sdk-subscription-control-"))
    name = f"sdk-subscription-control-{uuid.uuid4().hex}"
    command = container_command(name, offline=False)
    source_hashes = {
        "probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "helper_sha256": hashlib.sha256(
            Path(previous.__file__).read_bytes()
        ).hexdigest(),
    }
    reserve()
    (root / "invocation.json").write_text(
        json.dumps({"command": command, "approval": APPROVAL}, indent=2)
    )
    removals = []
    lock = threading.Lock()
    process = None

    def stop(reason):
        with lock:
            record = {"reason": reason}
            try:
                record.update(previous.cleanup(name))
            except Exception as exc:
                record.update(confirmed_removed=False, cleanup_error=type(exc).__name__)
            if process is not None and process.poll() is None:
                try:
                    process.kill()
                except Exception as exc:
                    record["client_kill_error"] = type(exc).__name__
            removals.append(record)

    watchdog = threading.Timer(60, stop, args=("wall_clock_watchdog",))
    failure = "host_startup_failure"
    code = -1
    results = []
    with (
        (root / "stream.jsonl").open("w") as output,
        (root / "raw-stdout.jsonl").open("w") as raw_output,
        (root / "stderr.txt").open("w") as stderr,
    ):
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=stderr,
                text=True,
            )
            watchdog.start()

            def record(event):
                output.write(json.dumps(event) + "\n")
                output.flush()
                if event.get("kind") == "ResultMessage":
                    results.append(event.get("message"))

            def raw_lines():
                for line in process.stdout:
                    raw_output.write(line)
                    raw_output.flush()
                    yield line

            _, failure = consume(raw_lines(), stop, record, source_hashes=source_hashes)
            code = process.wait(timeout=15)
        except Exception as exc:
            failure = "host_exception:" + type(exc).__name__
        finally:
            stop("finally_cleanup")
            watchdog.cancel()
            if watchdog.ident is not None:
                watchdog.join()
            if process is not None and process.poll() is None:
                try:
                    process.kill()
                    process.wait(timeout=15)
                except Exception as exc:
                    removals.append(
                        {
                            "reason": "client_reap",
                            "confirmed_removed": False,
                            "client_reap_error": type(exc).__name__,
                        }
                    )
            if process is not None and process.stdout is not None:
                if failure is not None and any(
                    item.get("confirmed_removed") for item in removals
                ):
                    try:
                        (root / "post-stop-tail.jsonl").write_text(
                            process.stdout.read()
                        )
                    except Exception as exc:
                        removals.append(
                            {
                                "reason": "tail_capture",
                                "confirmed_removed": False,
                                "tail_capture_error": type(exc).__name__,
                            }
                        )
                process.stdout.close()
    watchdog_fired = any(
        item.get("reason") == "wall_clock_watchdog" for item in removals
    )
    if watchdog_fired and failure is None:
        failure = "wall_clock_watchdog"
    report = {
        "status": "observed_control_subset_passed"
        if failure is None and code == 0 and cleanup_passed(removals)
        else "failed",
        "failure": failure,
        "watchdog_fired": watchdog_fired,
        "exit_code": code,
        "removals": removals,
        "host_admissions": 1,
        "evidence_root": str(root),
        "preventive_budget_enforcement": "unproved",
        "subscription_billing": "unverified",
        "provider_request_count": "not independently measured",
        "final_usage_if_stopped_before_result": "unknown; no zero default",
        "observed_final_results": results,
        "accounting": "observed final result, list estimate only"
        if results
        else "unknown and unreconciled; stopped before final result",
    }
    (root / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    if report["status"] != "observed_control_subset_passed":
        raise SystemExit(1)


def offline_test():
    cases = [
        (
            {
                "kind": "StreamEvent",
                "message": {
                    "event": {
                        "type": "message_delta",
                        "delta": {"stop_reason": "max_tokens"},
                    }
                },
            },
            "output_limit_partial_delta",
        ),
        (
            {"kind": "AssistantMessage", "message": {"error": "max_output_tokens"}},
            "output_limit_assistant",
        ),
        ({"kind": "UserMessage", "message": {}}, "unexpected_user_continuation"),
        (
            {
                "kind": "RateLimitEvent",
                "message": {
                    "rate_limit_info": {
                        "raw": {"isUsingOverage": False, "overageInUse": True}
                    }
                },
            },
            "ambiguous_active_or_unverifiable_overage",
        ),
        (
            {"kind": "RateLimitEvent", "message": {}},
            "ambiguous_active_or_unverifiable_overage",
        ),
        (
            {"kind": "AssistantMessage", "message": {"model": "unknown"}},
            "unknown_assistant_model",
        ),
        (
            {
                "kind": "StreamEvent",
                "message": {
                    "event": {
                        "type": "content_block_start",
                        "content_block": {"type": "tool_use"},
                    }
                },
            },
            "unexpected_partial_tool",
        ),
    ]
    for event, expected in cases:
        order = []

        def lines():
            order.append("first_read")
            yield json.dumps(event)
            order.append("queued_continuation_read")
            yield json.dumps({"kind": "UserMessage"})

        monitor, reason = consume(
            lines(),
            lambda value: order.append("hard_stop:" + value),
            lambda value: order.append("record"),
        )
        assert reason == expected and monitor.reason == expected
        assert order == ["first_read", "record", "hard_stop:" + expected]
    replay_path = (
        Path(__file__).resolve().parent / "results/subscription-sdk-query/stream.jsonl"
    )
    replay = iter(replay_path.read_text().splitlines())
    captured = []
    stopped = []
    _, reason = consume(replay, stopped.append, captured.append)
    assert reason == "ambiguous_active_or_unverifiable_overage"
    assert len(captured) == 7 and len(stopped) == 1
    assert json.loads(next(replay))["kind"] == "UserMessage"
    commands = container_command("offline-owned", offline=True)
    assert commands[commands.index("--network") + 1] == "none"
    assert previous.VOLUME not in " ".join(commands)
    assert previous.APPROVAL != APPROVAL
    result = {
        "kind": "ResultMessage",
        "message": {
            "is_error": False,
            "subtype": "success",
            "num_turns": 1,
            "result": "SDK_CONNECTIVITY_OK",
            "total_cost_usd": 0.001,
            "usage": {
                "input_tokens": 1,
                "output_tokens": 1,
                "cache_read_input_tokens": 0,
                "cache_creation_input_tokens": 0,
                "output_tokens_details": {"thinking_tokens": 0},
            },
            "model_usage": {
                MODEL: {
                    "inputTokens": 1,
                    "outputTokens": 1,
                    "cacheReadInputTokens": 0,
                    "cacheCreationInputTokens": 0,
                    "thinkingTokens": 0,
                }
            },
        },
    }

    def initialized():
        monitor = Monitor()
        monitor.provenance_seen = True
        monitor.init_seen = True
        monitor.overage_clear_seen = True
        return monitor

    assert initialized().observe(result) is None
    for key, value in (
        ("is_error", True),
        ("num_turns", 4),
        ("num_turns", True),
        ("result", " SDK_CONNECTIVITY_OK "),
        ("model_usage", {}),
        ("usage", {}),
        ("total_cost_usd", 0.05),
        ("errors", ["failure"]),
    ):
        bad = {"kind": "ResultMessage", "message": {**result["message"], key: value}}
        assert initialized().observe(bad) is not None
    assert Monitor().observe(result) == "missing_init_or_overage_observation"
    missing_thinking = {**result["message"]["model_usage"][MODEL]}
    del missing_thinking["thinkingTokens"]
    assert (
        initialized().observe(
            {
                "kind": "ResultMessage",
                "message": {
                    **result["message"],
                    "model_usage": {MODEL: missing_thinking},
                },
            }
        )
        is not None
    )
    assert cleanup_passed([{"confirmed_removed": True}])
    assert not cleanup_passed(
        [{"confirmed_removed": True, "remove_error": "TimeoutExpired"}]
    )
    assert not cleanup_passed([{"confirmed_removed": False}])
    with tempfile.TemporaryDirectory(prefix="sdk-control-offline-") as directory:
        root = Path(directory)
        with patch.object(Path, "home", return_value=root):
            reserve()
            try:
                reserve()
            except FileExistsError:
                pass
            else:
                raise AssertionError("Second reservation accepted")
            assert not (
                root
                / ".local/state/claude-recovery-proof"
                / f"{previous.APPROVAL}.json"
            ).exists()
        removals = []
        with (
            patch("tempfile.mkdtemp", return_value=directory),
            patch("subprocess.Popen") as popen,
            patch("threading.Timer") as timer,
            patch(__name__ + ".prepare_host"),
            patch(
                "subscription_sdk_run.cleanup",
                side_effect=lambda name: (
                    removals.append(name) or {"confirmed_removed": True}
                ),
            ),
            patch(__name__ + ".reserve"),
            patch("builtins.print"),
        ):
            popen.return_value.wait.return_value = -9
            popen.return_value.poll.return_value = None
            popen.return_value.stdout = type(
                "MockStream",
                (),
                {
                    "__iter__": lambda self: iter([json.dumps(cases[0][0])]),
                    "close": lambda self: None,
                    "read": lambda self: "",
                },
            )()
            try:
                execute()
            except SystemExit as exc:
                assert exc.code == 1
            else:
                raise AssertionError("Failed probe accepted")
            assert popen.call_count == 1 and len(removals) == 2
            assert len(set(removals)) == 1
            assert timer.call_args.args[0] == 60
            timer.return_value.start.assert_called_once()
            timer.return_value.cancel.assert_called_once()
            timer.return_value.join.assert_called_once()
            timer.call_args.args[1]("offline_watchdog_fire")
            assert len(removals) == 3
            assert popen.return_value.kill.call_count >= 3
        report = json.loads((root / "report.json").read_text())
        assert report["failure"] == "output_limit_partial_delta"
        assert report["host_admissions"] == 1 and report["status"] == "failed"
        released = threading.Event()
        real_timer = threading.Timer

        class BlockedStream:
            def __iter__(self):
                assert released.wait(2), "Watchdog failed to unblock client reader"
                return iter([])

            def close(self):
                pass

        with (
            patch("tempfile.mkdtemp", return_value=directory),
            patch("subprocess.Popen") as popen,
            patch(
                "threading.Timer",
                side_effect=lambda seconds, callback, args: real_timer(
                    0.01, callback, args=args
                ),
            ),
            patch(
                "subscription_sdk_run.cleanup",
                return_value={
                    "confirmed_removed": False,
                    "remove_error": "TimeoutExpired",
                },
            ),
            patch(__name__ + ".reserve"),
            patch(__name__ + ".prepare_host"),
            patch("builtins.print"),
        ):
            popen.return_value.stdout = BlockedStream()
            popen.return_value.poll.return_value = None
            popen.return_value.kill.side_effect = released.set
            popen.return_value.wait.return_value = -9
            try:
                execute()
            except SystemExit as exc:
                assert exc.code == 1
            else:
                raise AssertionError("Unconfirmed watchdog removal accepted")
            assert released.is_set() and popen.call_count == 1
        blocked_report = json.loads((root / "report.json").read_text())
        assert blocked_report["status"] == "failed"
        assert any(
            item["reason"] == "wall_clock_watchdog" and not item["confirmed_removed"]
            for item in blocked_report["removals"]
        )
        provenance = {
            "kind": "provenance",
            "sdk": "0.2.162",
            "cli": "2.1.274 (Claude Code)",
            "cli_sha256": previous.CLI_HASH,
            "sdk_record_files": 36,
            "probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "helper_sha256": hashlib.sha256(
                Path(previous.__file__).read_bytes()
            ).hexdigest(),
        }
        valid_events = [
            provenance,
            {
                "kind": "SystemMessage",
                "message": {
                    "subtype": "init",
                    "data": {
                        "model": MODEL,
                        "tools": [],
                        "skills": [],
                        "plugins": [],
                        "mcp_servers": [],
                    },
                },
            },
            {
                "kind": "RateLimitEvent",
                "message": {
                    "rate_limit_info": {
                        "status": "allowed",
                        "rate_limit_type": "five_hour",
                        "raw": {"isUsingOverage": False, "overageInUse": False},
                    }
                },
            },
            result,
        ]
        for fire_watchdog in (False, True):
            with (
                patch("tempfile.mkdtemp", return_value=directory),
                patch("subprocess.Popen") as popen,
                patch("threading.Timer") as timer,
                patch(
                    "subscription_sdk_run.cleanup",
                    return_value={"confirmed_removed": True},
                ),
                patch(__name__ + ".reserve"),
                patch(__name__ + ".prepare_host"),
                patch("builtins.print"),
            ):
                popen.return_value.stdout = type(
                    "ValidStream",
                    (),
                    {
                        "__iter__": lambda self: iter(
                            [json.dumps(event) for event in valid_events]
                        ),
                        "close": lambda self: None,
                        "read": lambda self: "",
                    },
                )()
                popen.return_value.wait.return_value = 0
                popen.return_value.poll.return_value = 0
                if fire_watchdog:
                    timer.return_value.join.side_effect = lambda: timer.call_args.args[
                        1
                    ]("wall_clock_watchdog")
                try:
                    execute()
                except SystemExit as exc:
                    assert fire_watchdog and exc.code == 1
                else:
                    assert not fire_watchdog, "Successful result hid watchdog race"
            race_report = json.loads((root / "report.json").read_text())
            assert race_report["watchdog_fired"] is fire_watchdog
            if fire_watchdog:
                assert (
                    race_report["status"] == "failed"
                    and race_report["failure"] == "wall_clock_watchdog"
                )
                assert (
                    race_report["exit_code"] == 0
                    and len(race_report["observed_final_results"]) == 1
                )
            else:
                assert race_report["status"] == "observed_control_subset_passed"
    print(
        json.dumps(
            {
                "status": "offline_control_checks_passed",
                "model_requests": 0,
                "mock_cases": len(cases),
                "replay_consumed_events": len(captured),
                "replay_first_stop": reason,
                "queued_continuation_unread": True,
                "watchdog_success_race_rejected": True,
                "boolean_turn_count_rejected": True,
                "whitespace_result_rejected": True,
                "limits": [
                    "CLI producer can already have started another request before host observation.",
                    "Removal cannot undo provider usage or charges already incurred.",
                    "No currency, input token or phase aggregate preventive cap is proved.",
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--offline-test", action="store_true")
    mode.add_argument("--container-prepare", action="store_true")
    mode.add_argument("--container-query", action="store_true")
    mode.add_argument("--execute-approved", choices=[APPROVAL])
    args = parser.parse_args()
    if args.offline_test:
        offline_test()
    elif args.container_prepare:
        asyncio.run(prepare())
    elif args.container_query:
        asyncio.run(container_query())
    else:
        execute()
