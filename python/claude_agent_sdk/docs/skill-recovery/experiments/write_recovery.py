"""Prepare or run one fixed effect scenario using the existing host supervisor.

The default command prints the fixed scenario and its source bound approval token.
Execution requires that token and explicit acceptance of reactive monitoring risk.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

from host_session import (
    AdmissionRefused,
    Docker,
    ExperimentAdmission,
    HostSession,
    owned_runner,
)
from host_session_offline import CLI_HASH, IMAGE
from sdk_shutdown_probe import inventory, refused, save

MODEL = "claude-haiku-4-5-20251001"
SERVER_HASH = "eff36463f7c0fbfcfd50f117370fc582fe964912a62cf271b91af05447d1fdfe"
RESULT = "WRITE_ONCE_RECORDED_OK"
CONTENT = "WRITE_ONCE_MARKER\n"
BASH_RESULT = "BASH_KNOWN_ERROR_EXIT_7"
BASH_CONTENT = "BASH_ONCE_MARKER\n"
BASH_REJECTED = "BASH_REJECTED_BY_HOST"
READ_SEED = "READ_BEFORE_EFFECT\n"
BASH_PARK_COMMAND = "echo BASH_ONCE_MARKER > /state/work/marker.txt; sleep 30"
BASH_COMMAND = (
    "echo BASH_ONCE_MARKER > /state/work/marker.txt; "
    "printf BASH_KNOWN_ERROR_EXIT_7 >&2; exit 7"
)


class VerifiedPark(Exception):
    """Finish the bounded park scenario through the common cleanup path."""


def proof_case(scenario="write") -> dict[str, Any]:
    if scenario == "mixed-read":
        case = proof_case("write")
        case["prompt"] = (
            "First call Read on /state/work/input.txt and inspect its contents. "
            "Then in your next single assistant message call Write twice, with two distinct tool calls "
            "both using file_path /state/work/marker.txt and content WRITE_ONCE_MARKER followed by a newline. "
            "In that same message, after both Write calls, call Read on /state/work/input.txt again. "
            "Do not combine these into Bash, do not omit a call, and do not use other tools. "
            "After the tool results, describe which calls were denied and include the recorded Write result."
        )
        return case
    if scenario == "write":
        return {
            "tool": "Write",
            "mode": "repeatable",
            "result": RESULT,
            "content": CONTENT,
            "is_error": False,
            "prompt": "Use Write exactly once to create /state/work/marker.txt with exactly WRITE_ONCE_MARKER followed by a newline. Then reply with the tool result only. Do not use any other tool.",
        }
    if scenario in {"bash-error", "bash-reject", "bash-park"}:
        command = BASH_PARK_COMMAND if scenario == "bash-park" else BASH_COMMAND
        result = BASH_REJECTED if scenario == "bash-reject" else BASH_RESULT
        return {
            "tool": "Bash",
            "mode": "claimed",
            "result": result,
            "command": command,
            "content": BASH_CONTENT,
            "is_error": True,
            "prompt": "Call Bash exactly once with this literal command:\n```sh\n"
            + command
            + "\n```\nDo not call any other tool or change the command. After its result, reply with exactly "
            + result
            + ".",
        }
    raise AdmissionRefused("Unknown proof scenario")


def validate_effect_input(pending, scenario):
    case = proof_case(scenario)
    inputs = pending["input"]
    if pending["name"] != case["tool"]:
        raise AdmissionRefused("Accepted tool differs from approved scenario")
    if scenario in {"write", "mixed-read"}:
        valid = inputs == {"file_path": "/state/work/marker.txt", "content": CONTENT}
    else:
        valid = (
            isinstance(inputs, dict)
            and inputs.get("command") == case["command"]
            and set(inputs) <= {"command", "description"}
            and ("description" not in inputs or isinstance(inputs["description"], str))
        )
    if not valid:
        raise AdmissionRefused("Accepted input differs from approved scenario")


def external_effect(accepted, scenario, state=Path("/state"), *, activity_attempt=None):
    """Execute the fixed approved effect once; uncertainty records a park, never a result."""
    validate_effect_input(accepted["pending"], scenario)
    case = proof_case(scenario)
    if scenario == "bash-reject":
        save(state / "host-rejection.json", {"accepted": accepted, "effects": 0})
        return {
            "tool_use_id": accepted["pending"]["id"],
            "content": case["result"],
            "is_error": True,
        }
    with (state / "effect-invocation.json").open("x") as file:
        json.dump({"accepted": accepted, "activity_attempt": activity_attempt}, file)
    marker = state / "work/marker.txt"
    if scenario in {"write", "mixed-read"}:
        with marker.open("x") as file:
            file.write(case["content"])
    else:
        # The exclusive invocation file is the retained claim for this fixed command.
        try:
            completed = subprocess.run(
                ["/bin/sh", "-c", case["command"]],
                capture_output=True,
                text=True,
                timeout=3,
            )
            save(
                state / "bash-process.json",
                {
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                },
            )
            if (
                completed.returncode != 7
                or completed.stdout != ""
                or completed.stderr != BASH_RESULT
                or marker.read_text() != BASH_CONTENT
            ):
                raise AdmissionRefused("Bash terminal outcome differs")
        except Exception as exc:
            park = {
                "parked": True,
                "cause": type(exc).__name__ + ": " + str(exc),
                "accepted": accepted,
                "model_result": None,
            }
            save(state / "bash-park.json", park)
            return park
    return {
        "tool_use_id": accepted["pending"]["id"],
        "content": case["result"],
        "is_error": case["is_error"],
    }


class WriteRateMonitor:
    """Retain allowed Enterprise usage events without claiming verified billing."""

    def __init__(self):
        self.events = []
        self.rate_limit_seen = False

    def inspect(self, event):
        info = event.get("message", {}).get("rate_limit_info")
        self.events.append(event)
        if not isinstance(info, dict) or not isinstance(info.get("raw"), dict):
            return "rate_limit_refused_or_unverifiable"
        raw = info["raw"]
        if (
            info.get("status") not in {"allowed", "allowed_warning"}
            or raw.get("status") != info["status"]
            or not isinstance(info.get("rate_limit_type"), str)
            or not info["rate_limit_type"]
            or raw.get("rateLimitType") != info["rate_limit_type"]
            or any(
                key in raw and type(raw[key]) is not bool
                for key in ("isUsingOverage", "overageInUse")
            )
        ):
            return "rate_limit_refused_or_unverifiable"
        if (
            info["rate_limit_type"] == "overage"
            or raw.get("isUsingOverage") is True
            or raw.get("overageInUse") is True
        ) and (
            info.get("overage_status") not in {"allowed", "allowed_warning"}
            or raw.get("overageStatus") != info["overage_status"]
            or info.get("overage_disabled_reason")
        ):
            return "rate_limit_refused_or_unverifiable"
        self.rate_limit_seen = True
        return None


def recorded_result(call, expected, scenario="write"):
    """Return only the stored outcome for the entire accepted pending identity."""
    from claude_agent_sdk import ToolResultBlock

    case = proof_case(scenario)
    if (
        expected is None
        or asdict(call) != expected["pending"]
        or expected["outcome"]
        != {
            "tool_use_id": call.id,
            "content": case["result"],
            "is_error": case["is_error"],
        }
    ):
        raise AdmissionRefused("Original pending call or recorded result differs")
    return ToolResultBlock(
        call.id, expected["outcome"]["content"], expected["outcome"]["is_error"]
    )


def validate_recovery_state(accepted, entries, state, scenario="write"):
    """Refuse changed transcript, pending batch, workspace or dispatch ownership."""
    from claude_agent_sdk._internal.main_agent_recovery import pending_tool_uses

    if scenario == "bash-park":
        raise AdmissionRefused("Ambiguous Bash has no recoverable result")
    if (
        not entries
        or hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()
        != accepted["transcript_sha256"]
    ):
        raise AdmissionRefused("Accepted transcript state differs")
    pending, _ = pending_tool_uses(accepted["key"], entries)
    if len(pending) != 1:
        raise AdmissionRefused(
            "Recovery requires exactly one accepted pending call; batch refused"
        )
    if asdict(pending[0]) != accepted["pending"]:
        raise AdmissionRefused("Accepted pending identity differs")
    marker = state / "work/marker.txt"
    claim = state / "effect-invocation.json"
    if scenario == "bash-reject":
        if marker.exists() or claim.exists():
            raise AdmissionRefused("Rejected call has unexpected effect state")
        receipt = state / "host-rejection.json"
    else:
        if not marker.exists() or marker.read_text() != proof_case(scenario)["content"]:
            raise AdmissionRefused("Accepted workspace state missing or changed")
        receipt = claim
    if (
        not receipt.exists()
        or json.loads(receipt.read_text()).get("accepted") != accepted
    ):
        raise AdmissionRefused("Accepted dispatch ownership missing or changed")


def configuration(scenario="write", seed=None):
    proof_case(scenario)
    authorization = source_digest()
    if scenario != "write":
        authorization = hashlib.sha256(
            (authorization + ":" + scenario).encode()
        ).hexdigest()
    if seed is not None:
        authorization = hashlib.sha256(
            (authorization + json.dumps(seed, sort_keys=True)).encode()
        ).hexdigest()
    return {
        "scenario": "deferred-" + scenario + "-fresh-worker-metered-enterprise-v1",
        "authorization": authorization,
        "authentication": "retained-claude.ai-volume-only",
        "model": MODEL,
        "image": IMAGE,
        "sdk": "0.2.162",
        "cli_sha256": CLI_HASH,
        "allowance_usd": 0.05,
        "input_limit": 20000,
        "output_limit": 2048,
        "segments": 1 if scenario == "bash-park" or seed is not None else 2,
        "max_turns": 2,
        "retries": 0,
        "segment_seconds": 45,
        "shutdown_seconds": 20,
        "host_seconds": 180,
        "residual_risk_accepted": True,
    }


def retained_seed(path):
    """Validate the stopped mixed checkpoint with no external dispatch or recovery."""
    path = Path(path).resolve()
    report = json.loads((path / "report.json").read_text())
    if (
        report.get("status") != "nonpassing"
        or report.get("error")
        != "AdmissionRefused: Observed allowance or request planning bound reached"
    ):
        raise AdmissionRefused(
            "Only the retained predispatch turn refusal can continue"
        )
    if (
        report["config"]["scenario"]
        != "deferred-mixed-read-fresh-worker-metered-enterprise-v1"
    ):
        raise AdmissionRefused("Retained scenario differs")
    if {row["role"] for row in report["cleanup"]} != {"initial", "coordinator"}:
        raise AdmissionRefused("Retained owner cleanup is incomplete")
    for row in report["cleanup"]:
        receipt = json.loads(row["receipt"]["host_receipt"])
        if not receipt["removal_verified"] or receipt["stopped_state"] != {
            "Pid": 0,
            "Running": False,
        }:
            raise AdmissionRefused("Retained owner cleanup is unproved")
    if any(
        (path / name).exists()
        for name in (
            "effect-invocation.json",
            "effect_committed.json",
            "recovered-transcript.json",
            "work/marker.txt",
            "dispatch",
        )
    ):
        raise AdmissionRefused("Retained checkpoint already dispatched or continued")
    accepted = json.loads((path / "segment_committed.json").read_text())["accepted"]
    entries = json.loads((path / "original-transcript.json").read_text())
    if (
        hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()
        != accepted["transcript_sha256"]
    ):
        raise AdmissionRefused("Retained checkpoint digest differs")
    validate_effect_input(accepted["pending"], "mixed-read")
    if (path / "work/input.txt").read_text() != READ_SEED:
        raise AdmissionRefused("Retained read seed differs")
    accounting = json.loads((path / "initial-accounting.json").read_text())
    if (
        accounting["model"] != MODEL
        or accounting["cost_usd"] >= 0.05
        or accounting["input"] >= 20000
        or accounting["output"] >= 2048
    ):
        raise AdmissionRefused("Retained usage has no approved allowance headroom")
    return {
        "accepted": accepted,
        "entries": entries,
        "prior_accounting": accounting,
        "decisions": (path / "initial-hook-decisions.jsonl").read_text(),
        "prompt": json.loads((path / "prompt.json").read_text()),
    }


def inspect_mixed_read(output, accepted, result):
    """Require preserved read output, actual pause denial and a recorded next action."""
    import runpy

    experiments = Path(__file__).resolve().parent
    source = (
        Path("/source/temporalio/claude_agent_sdk")
        if str(experiments) == "/fixture"
        else experiments.parents[2] / "src/temporalio/claude_agent_sdk"
    )
    denial_reason = runpy.run_path(str(source / "_defer_hook.py"))["ONE_AT_A_TIME"]

    original = json.loads((output / "original-transcript.json").read_text())
    decisions = [
        json.loads(row)
        for row in (output / "initial-hook-decisions.jsonl").read_text().splitlines()
    ]
    calls, outcomes = {}, {}
    for entry in original:
        content = entry.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                calls[block["id"]] = block
            elif block.get("type") == "tool_result":
                outcomes[block["tool_use_id"]] = block
    effect_ids = [key for key, call in calls.items() if call["name"] == "Write"]
    accepted_id = accepted["pending"]["id"]
    denies = {
        row["id"]
        for row in decisions
        if row["event"] == "PreToolUse"
        and row["decision"] == "deny"
        and row["reason"] == denial_reason
    }
    if set(effect_ids) - {accepted_id} - denies:
        raise AdmissionRefused("An effect call lacks acceptance or visible denial")
    for denied_id in set(effect_ids) & denies:
        if not outcomes.get(denied_id, {}).get("is_error"):
            raise AdmissionRefused("Effect denial is absent from the model transcript")
    successful_reads = [
        key
        for key, call in calls.items()
        if call["name"] == "Read"
        and key in outcomes
        and not outcomes[key].get("is_error")
        and "READ_BEFORE_EFFECT" in json.dumps(outcomes[key])
    ]
    denied_reads = [
        key
        for key, call in calls.items()
        if call["name"] == "Read"
        and key in denies
        and outcomes.get(key, {}).get("is_error")
    ]
    if not successful_reads or not denied_reads:
        raise AdmissionRefused(
            "Read before effect or visible read denial after pause is unproved"
        )
    deferred_index = next(
        index
        for index, row in enumerate(decisions)
        if row["id"] == accepted_id and row["decision"] == "defer"
    )
    if not any(
        row["id"] in successful_reads and row["event"] == "PostToolUse"
        for row in decisions[:deferred_index]
    ):
        raise AdmissionRefused("Read completion before accepted deferral is unproved")
    next_action = result["segment"]["result"]
    if not isinstance(next_action, str) or "den" not in next_action.lower():
        raise AdmissionRefused("Model response to denial is unproved")
    return {
        "effect_calls": effect_ids,
        "accepted": accepted_id,
        "denied": sorted(denies),
        "multiple_effect_shape": len(effect_ids) >= 2,
        "shape_trial": "prompt.json",
        "successful_reads": successful_reads,
        "denied_reads": denied_reads,
        "model_next_action": next_action,
    }


def source_digest():
    experiments = Path(__file__).resolve().parent
    source = (
        Path("/source/temporalio/claude_agent_sdk")
        if str(experiments) == "/fixture"
        else experiments.parents[2] / "src/temporalio/claude_agent_sdk"
    )
    paths = sorted(experiments.glob("*.py")) + sorted(source.glob("*.py"))
    return hashlib.sha256(
        b"".join(path.name.encode() + path.read_bytes() for path in paths)
    ).hexdigest()


class ProofStore:
    """Retain exact transcript entries with SQLite conditional append on one host."""

    def __init__(self, path, *, create=False):
        path = Path(path).resolve()
        if create:
            with path.open("xb"):
                pass
        self.path = path.as_uri() + "?mode=rw"
        with sqlite3.connect(self.path, uri=True) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS transcript (key TEXT PRIMARY KEY, entries TEXT NOT NULL)"
            )

    def transaction(self, key, entries=None, expected=None, conditional=False):
        with sqlite3.connect(self.path, uri=True) as db:
            db.execute("PRAGMA synchronous=FULL")
            db.execute("BEGIN IMMEDIATE")
            encoded = json.dumps(key, sort_keys=True)
            row = db.execute(
                "SELECT entries FROM transcript WHERE key=?", (encoded,)
            ).fetchone()
            current = json.loads(row[0]) if row else []
            if entries is None:
                return current or None
            head = next(
                (entry["uuid"] for entry in reversed(current) if entry.get("uuid")),
                None,
            )
            if conditional and head != expected:
                return False
            known = {entry.get("uuid") for entry in current if entry.get("uuid")}
            current.extend(
                entry
                for entry in entries
                if not entry.get("uuid") or entry["uuid"] not in known
            )
            db.execute(
                "INSERT OR REPLACE INTO transcript VALUES (?,?)",
                (encoded, json.dumps(current)),
            )
            return True

    async def load(self, key):
        return await asyncio.to_thread(self.transaction, key)

    async def append(self, key, entries):
        await asyncio.to_thread(self.transaction, key, entries)

    async def append_if_unchanged(self, key, expected_last_uuid, entries):
        return await asyncio.to_thread(
            self.transaction, key, entries, expected_last_uuid, True
        )


def verify_child(scenario="write"):
    import importlib.metadata
    import subprocess

    from subscription_sdk_run import verify_sdk

    seed_path = Path("/state/retained-seed.json")
    seed = json.loads(seed_path.read_text()) if seed_path.exists() else None
    expected = configuration(scenario, seed)
    config = json.loads(Path("/state/admission.json").read_text())["config"]
    ExperimentAdmission.validate(config, expected)
    if os.environ.get("DURABILITY_APPROVED_SCENARIO") != expected["authorization"]:
        raise AdmissionRefused("Source bound scenario approval absent")
    if any(
        name.startswith("ANTHROPIC_")
        or name
        in {
            "CLAUDE_CODE_OAUTH_TOKEN",
            "CLAUDE_CODE_USE_BEDROCK",
            "CLAUDE_CODE_USE_VERTEX",
            "CLAUDE_CODE_USE_FOUNDRY",
        }
        for name in os.environ
    ):
        raise AdmissionRefused("Provider environment refused; values withheld")
    assert os.environ["UV_NO_SYNC"] == os.environ["UV_NO_EDITABLE"] == "1"
    assert hashlib.sha256(Path("/opt/claude").read_bytes()).hexdigest() == CLI_HASH
    assert os.environ["RECOVERY_CLI"] == "/opt/claude"
    version = subprocess.run(
        ["/opt/claude", "-v"], capture_output=True, text=True, check=True, timeout=15
    ).stdout.strip()
    assert version == "2.1.274 (Claude Code)"
    return {
        "sdk": importlib.metadata.version("claude-agent-sdk"),
        "cli": version,
        "model": MODEL,
        "sdk_record_files": verify_sdk(),
    }


async def worker(args):
    import temporalio

    temporalio.__path__.insert(0, "/source/temporalio")
    from claude_agent_sdk import ToolResultBlock, project_key_for_directory
    from claude_agent_sdk._internal.main_agent_recovery import pending_tool_uses

    from temporalio import activity
    from temporalio.claude_agent_sdk import (
        ClaudeAgentSdkRunner,
        SegmentInput,
        ToolPolicy,
        ToolPolicyEntry,
    )
    from temporalio.client import Client
    from temporalio.worker import Worker

    state = Path("/state")
    case = proof_case(args.scenario)
    info = verify_child(args.scenario)
    host = HostSession(state / "worker-host.db")
    store = ProofStore(state / "transcript.db", create=args.role == "initial")
    policy_entries = [ToolPolicyEntry(case["tool"], "effect", case["mode"])]
    if args.scenario == "mixed-read":
        policy_entries.append(ToolPolicyEntry("Read", "read"))
    policy = ToolPolicy(tuple(policy_entries))
    builtin_tools = [entry.name for entry in policy.entries]
    callbacks = []
    transport_starts = []
    expected = None
    from claude_agent_sdk._internal.transport.subprocess_cli import (
        SubprocessCLITransport,
    )

    original_connect = SubprocessCLITransport.connect

    async def observed_connect(transport):
        if args.role == "replacement" and len(callbacks) != 1:
            raise AdmissionRefused("Transport attempted before exact original recovery")
        transport_starts.append({"recovery_callbacks_before_transport": len(callbacks)})
        return await original_connect(transport)

    SubprocessCLITransport.connect = observed_connect

    async def recover(call):
        result = recorded_result(call, expected, args.scenario)
        callbacks.append(asdict(call))
        return result

    owner = owned_runner(
        host,
        args.attempt,
        args.session,
        runner_factory=ClaudeAgentSdkRunner,
        recover_pending_tool=recover,
        session_store=store,
        cwd="/state/work",
        cli_path=os.environ["RECOVERY_CLI"],
        model=MODEL,
        max_budget_usd=0.05,
        tool_policy=policy,
        one_tool_at_a_time=args.scenario != "mixed-read",
        env={
            "CLAUDE_CODE_MAX_RETRIES": "0",
            "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "1024",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
            "TCA_HOOK_LOG": str(state / (args.role + "-hook-decisions.jsonl")),
        },
    )

    async def segment(inp):
        before = inventory()
        task = asyncio.create_task(owner.run(inp, 1))
        deadline = time.monotonic() + 45
        observed, monitor = 0, WriteRateMonitor()
        failure = None
        try:
            while not task.done():
                control = owner.session_control(args.session)
                if control:
                    control._timeout = 20
                messages = control.messages if control else []
                while observed < len(messages):
                    message = messages[observed]
                    observed += 1
                    raw = asdict(message)
                    event = raw.get("event") or {}
                    if (
                        raw.get("error")
                        or raw.get("stop_reason") == "max_tokens"
                        or (
                            event.get("type") == "message_delta"
                            and event.get("delta", {}).get("stop_reason")
                            == "max_tokens"
                        )
                    ):
                        owner.stop_session(args.session)
                        raise AdmissionRefused("Observed engine error or output limit")
                    if type(message).__name__ == "RateLimitEvent":
                        reason = monitor.inspect(
                            {"kind": "RateLimitEvent", "message": raw}
                        )
                        if reason:
                            owner.stop_session(args.session)
                            raise AdmissionRefused(reason)
                if time.monotonic() >= deadline:
                    owner.stop_session(args.session)
                    raise TimeoutError("Segment deadline expired")
                await asyncio.sleep(0.02)
            result = await task
            control = owner.session_control(args.session)
            for message in control.messages[observed:]:
                if type(message).__name__ == "RateLimitEvent":
                    reason = monitor.inspect(
                        {"kind": "RateLimitEvent", "message": asdict(message)}
                    )
                    if reason:
                        raise AdmissionRefused(reason)
            if result.is_error or not monitor.rate_limit_seen:
                raise AdmissionRefused(
                    "Nonpassing segment or missing allowed usage observation"
                )
            control = owner.session_control(args.session)
            terminal = [
                message
                for message in control.messages
                if type(message).__name__ == "ResultMessage"
            ]
            if len(terminal) != 1 or terminal[0].is_error:
                raise AdmissionRefused("Complete terminal accounting required")
            raw = asdict(terminal[0])
            usage = raw["usage"]
            counts = [
                usage.get(field)
                for field in (
                    "input_tokens",
                    "cache_read_input_tokens",
                    "cache_creation_input_tokens",
                    "output_tokens",
                )
            ]
            if any(type(count) is not int or count < 0 for count in counts) or set(
                raw.get("model_usage") or {}
            ) != {MODEL}:
                raise AdmissionRefused("Complete exact-model usage required")
            save(
                state / (args.role + "-accounting.json"),
                {
                    "model": MODEL,
                    "cost_usd": raw["total_cost_usd"],
                    "input": sum(counts[:3]),
                    "output": counts[3],
                    "turns": raw["num_turns"],
                },
            )
            return result
        except BaseException as exc:
            failure = {"error": type(exc).__name__ + ": " + str(exc)}
            raise
        finally:
            if not task.done():
                host.stop(args.attempt)
                owner.runner.stop_session(args.session)
                await asyncio.wait({task}, timeout=20)
            control = owner.session_control(args.session)
            save(
                state / (args.role + "-observations.json"),
                {
                    "versions": info,
                    "before": before,
                    "after": inventory(),
                    "callbacks": callbacks,
                    "transport_starts": transport_starts,
                    "controller": asdict(control.state) if control else None,
                    "messages": [asdict(message) for message in control.messages]
                    if control
                    else [],
                    "host": host.snapshot(args.attempt),
                    "rate_limit_events": monitor.events,
                    "billing_verified": False,
                    "metered_enterprise_usage_accepted": True,
                },
            )
            if failure is not None:
                save(state / "failure.json", failure)
            if not task.done():
                # Keep the owner alive until the authoritative host contains it.
                await asyncio.Event().wait()

    @activity.defn(name="proof_segment")
    async def initial(session: str):
        assert args.role == "initial" and session == args.session
        seed_path = state / "retained-seed.json"
        if seed_path.exists():
            seed = json.loads(seed_path.read_text())
            assert args.scenario == "mixed-read"
            assert seed["accepted"]["key"]["session_id"] == session
            await store.append(seed["accepted"]["key"], seed["entries"])
            pending, _ = pending_tool_uses(seed["accepted"]["key"], seed["entries"])
            assert [asdict(call) for call in pending] == [seed["accepted"]["pending"]]
            assert not (state / "work/marker.txt").exists()
            save(state / "original-transcript.json", seed["entries"])
            return seed["accepted"]
        result = await segment(
            SegmentInput(
                session_id=session,
                prompt=case["prompt"],
                tools=[],
                builtin_tools=builtin_tools,
                tool_policy=policy.canonical_json(),
                max_turns=2,
            )
        )
        assert result.deferred and not Path("/state/work/marker.txt").exists()
        key = {
            "project_key": project_key_for_directory("/state/work"),
            "session_id": session,
        }
        entries = await store.load(key)
        pending, _ = pending_tool_uses(key, entries)
        assert len(pending) == 1
        call = asdict(pending[0])
        assert (pending[0].id, pending[0].name, pending[0].input) == (
            result.deferred.id,
            result.deferred.name,
            result.deferred.input,
        )
        try:
            validate_effect_input(call, args.scenario)
        except AdmissionRefused as exc:
            save(state / "failure.json", {"error": "AdmissionRefused: " + str(exc)})
            raise
        save(state / "original-transcript.json", entries)
        return {
            "segment": asdict(result),
            "pending": call,
            "key": key,
            "transcript_sha256": hashlib.sha256(
                json.dumps(entries, sort_keys=True).encode()
            ).hexdigest(),
        }

    @activity.defn(name="proof_write")
    async def effect(accepted: dict):
        assert args.role == "initial"
        assert activity.info().attempt == 1
        return external_effect(
            accepted, args.scenario, activity_attempt=activity.info().attempt
        )

    @activity.defn(name="proof_recovery")
    async def replacement(data: dict):
        nonlocal expected
        assert args.role == "replacement"
        expected = {**data["accepted"], "outcome": data["outcome"]}
        entries = await store.load(expected["key"])
        try:
            validate_recovery_state(data["accepted"], entries, state, args.scenario)
        except Exception as exc:
            save(
                state / "failure.json", {"error": type(exc).__name__ + ": " + str(exc)}
            )
            raise
        inp = SegmentInput(
            session_id=args.session,
            prompt=(
                "Include the recorded Write result and describe which later tools were denied. Do not call tools."
                if args.scenario == "mixed-read"
                else "Reply with exactly " + case["result"] + ". Do not call tools."
            ),
            tools=[],
            builtin_tools=builtin_tools,
            tool_policy=policy.canonical_json(),
            max_turns=2,
            checkpoint=expected["segment"]["checkpoint"],
            segment_index=1,
        )
        result = await segment(inp)
        assert not result.deferred and len(callbacks) == 1
        if args.scenario == "mixed-read":
            assert isinstance(result.result, str) and case["result"] in result.result
        else:
            assert result.result == case["result"]
        recovered = await store.load(expected["key"])
        assert recovered[: len(entries)] == entries
        blocks = [
            block
            for entry in recovered
            for block in (
                entry.get("message", {}).get("content", [])
                if isinstance(entry.get("message", {}).get("content"), list)
                else []
            )
            if block.get("type") == "tool_result"
            and block.get("tool_use_id") == expected["pending"]["id"]
        ]
        assert blocks == [
            {
                "type": "tool_result",
                "tool_use_id": expected["pending"]["id"],
                "content": case["result"],
                "is_error": case["is_error"],
            }
        ]
        save(state / "recovered-transcript.json", recovered)
        if args.scenario == "bash-reject":
            assert not Path("/state/work/marker.txt").exists()
            assert not (state / "effect-invocation.json").exists()
        else:
            assert Path("/state/work/marker.txt").read_text() == case["content"]
        return {
            "segment": asdict(result),
            "callbacks": callbacks,
            "effect_count": 0 if args.scenario == "bash-reject" else 1,
        }

    client = await Client.connect(
        json.loads((state / "server.json").read_text())["address"]
    )
    async with Worker(
        client,
        task_queue="write-proof",
        activities=[initial, effect] if args.role == "initial" else [replacement],
    ):
        await asyncio.Event().wait()


async def coordinator(args):
    from write_recovery_workflow import WriteRecoveryProof

    from temporalio.testing import WorkflowEnvironment
    from temporalio.worker import UnsandboxedWorkflowRunner, Worker

    state = Path("/state")
    assert hashlib.sha256(Path("/opt/temporal").read_bytes()).hexdigest() == SERVER_HASH
    env = await WorkflowEnvironment.start_local(
        dev_server_existing_path="/opt/temporal"
    )
    try:
        save(
            state / "server.json",
            {"address": env.client.service_client.config.target_host},
        )
        async with Worker(
            env.client,
            task_queue="write-proof",
            workflows=[WriteRecoveryProof],
            workflow_runner=UnsandboxedWorkflowRunner(),
        ):
            handle = await env.client.start_workflow(
                WriteRecoveryProof.run,
                args.session,
                id=args.session,
                task_queue="write-proof",
            )
            for stage, signal, flag in (
                ("segment_committed", WriteRecoveryProof.allow_dispatch, "dispatch"),
                ("effect_committed", WriteRecoveryProof.allow_recovery, "recover"),
            ):
                while True:
                    current = await handle.query(WriteRecoveryProof.state)
                    if current["stage"] == "parked":
                        save(state / "parked.json", current)
                        (state / "history.json").write_text(
                            (await handle.fetch_history()).to_json()
                        )
                        await asyncio.Event().wait()
                    if current["stage"] == stage:
                        save(state / (stage + ".json"), current)
                        break
                    await asyncio.sleep(0.05)
                while not (state / flag).exists():
                    await asyncio.sleep(0.05)
                await handle.signal(signal)
            result = await handle.result()
            save(state / "result.json", result)
            (state / "history.json").write_text(
                (await handle.fetch_history()).to_json()
            )
            await asyncio.Event().wait()
    finally:
        await env.shutdown()


def check_output_space(output):
    """Refuse an occupied output path or less than 64 MiB of free space."""
    if output.exists():
        raise AdmissionRefused(
            "Output path already exists; preserve it and select a fresh path"
        )
    ancestor = output.parent
    while not ancestor.exists():
        ancestor = ancestor.parent
    if shutil.disk_usage(ancestor).free < 64 * 1024 * 1024:
        raise AdmissionRefused(
            "Output filesystem has less than 64 MiB free; reservation not consumed"
        )


def execute(args):
    case = proof_case(args.scenario)
    seed = retained_seed(args.resume_from) if args.resume_from else None
    if seed is not None and args.scenario != "mixed-read":
        raise AdmissionRefused("Checkpoint continuation only supports mixed-read")
    expected = configuration(args.scenario, seed)
    config = {
        **expected,
        "authorization": args.approval,
        "residual_risk_accepted": args.accept_residual_risk,
    }
    ExperimentAdmission.validate(config, expected)
    output = Path(args.output).resolve()
    check_output_space(output)
    output.mkdir(parents=True, exist_ok=False)
    output.chmod(0o777)
    (output / "work").mkdir(mode=0o777)
    (output / "work").chmod(0o777)
    save(
        output / "prompt.json",
        {
            "scenario": args.scenario,
            "prompt": case["prompt"],
            "one_tool_at_a_time": args.scenario != "mixed-read",
        },
    )
    if args.scenario == "mixed-read":
        (output / "work/input.txt").write_text(READ_SEED)
        (output / "work/input.txt").chmod(0o444)
    if seed is not None:
        save(output / "retained-seed.json", seed)
        save(output / "prompt.json", seed["prompt"])
        (output / "initial-hook-decisions.jsonl").write_text(seed["decisions"])
    reservation = (
        Path(__file__).parent
        / "results"
        / ("write-recovery-reservation-" + config["authorization"] + ".json")
    )
    admission = ExperimentAdmission.initialize(reservation, config, expected)
    save(output / "admission.json", admission.read())
    docker = Docker()
    experiments = Path(__file__).parent
    plugin = experiments.parents[2]
    session = (
        seed["accepted"]["key"]["session_id"] if seed is not None else str(uuid.uuid4())
    )
    active, receipts = [], []
    report = {
        "config": config,
        "status": "nonpassing",
        "billing": "CLI list estimate; subscription charges/headroom unverified",
        "provider_prevention_proved": False,
        "metered_enterprise_usage_accepted": True,
        "retained_checkpoint_continuation": seed is not None,
    }
    deadline = time.monotonic() + 180
    stop_deadlines = {}

    coordinator_resource = None

    def launch(role, host):
        attempt = host.admit(session)
        active.append((host, attempt, role))
        mounts = [str(output) + ":/state:rw", str(plugin / "src") + ":/source:ro"]
        mounts.extend(
            str(path) + ":/fixture/" + path.name + ":ro"
            for path in experiments.glob("*.py")
        )
        mounts.append(str(Path(args.server).resolve()) + ":/opt/temporal:ro")
        if role != "coordinator":
            mounts.append("claude-recovery-proof-login:/home/proof:rw")
        return host.launch(
            attempt,
            IMAGE,
            [
                "/fixture/write_recovery.py",
                "--role",
                role,
                "--attempt",
                attempt,
                "--session",
                session,
                "--scenario",
                args.scenario,
            ],
            mounts,
            network="bridge"
            if role == "coordinator"
            else "container:" + coordinator_resource,
            environment=(
                "UV_NO_SYNC=1",
                "UV_NO_EDITABLE=1",
                "PYTHONDONTWRITEBYTECODE=1",
                "PYTHONPATH=/opt/packages:/fixture",
                "RECOVERY_CLI=/opt/claude",
                "DURABILITY_APPROVED_SCENARIO=" + config["authorization"],
            ),
            docker=docker,
        )

    def wait(filename):
        while not (output / filename).is_file():
            if args.scenario != "bash-park" and (output / "parked.json").is_file():
                raise AdmissionRefused(
                    "Bash outcome parked; no result or replacement allowed"
                )
            if (output / "failure.json").is_file():
                raise AdmissionRefused(
                    json.loads((output / "failure.json").read_text())["error"]
                )
            for host, attempt, role in active:
                row = host.snapshot(attempt)
                resource = row["resource"]
                if resource:
                    (output / (role + "-container.log")).write_text(
                        docker.command("container", "logs", resource)
                    )
                    if not docker.inspect(resource)["State"]["Running"]:
                        raise AdmissionRefused(role + " owner exited")
                    if row["stopped"]:
                        stop_deadlines.setdefault(resource, time.monotonic() + 20)
                        if time.monotonic() >= stop_deadlines[resource]:
                            raise AdmissionRefused(
                                role + " SDK ownership stopped or unresolved"
                            )
            if time.monotonic() >= deadline:
                raise TimeoutError("Scenario observation deadline expired")
            time.sleep(0.05)
        return json.loads((output / filename).read_text())

    def cleanup(host, attempt, role):
        row = host.snapshot(attempt)
        try:
            (output / (role + "-container.log")).write_text(
                docker.command("container", "logs", row["resource"])
            )
        except Exception as exc:
            report.setdefault("log_errors", []).append(
                type(exc).__name__ + ": " + str(exc)
            )
            report["status"] = "nonpassing"
        receipts.append({"role": role, "receipt": host.teardown(attempt, docker)})
        active.remove((host, attempt, role))

    try:
        assert hashlib.sha256(Path(args.server).read_bytes()).hexdigest() == SERVER_HASH
        server_host = HostSession.initialize(output / "server-host.db")
        coordinator_resource = launch("coordinator", server_host)
        wait("server.json")
        worker_host = HostSession.initialize(output / "worker-host.db")
        worker_host.path.chmod(0o666)
        if seed is None:
            admission.begin()
        launch("initial", worker_host)
        accepted = wait("segment_committed.json")
        assert accepted["accepted"] and not (output / "work/marker.txt").exists()
        initial_totals = (
            admission.reconcile(wait("initial-accounting.json"))
            if seed is None
            else None
        )
        (output / "dispatch").touch()
        if args.scenario == "bash-park":
            parked = wait("parked.json")
            history = wait("history.json")
            scheduled = [
                event["activityTaskScheduledEventAttributes"]["activityType"]["name"]
                for event in history["events"]
                if "activityTaskScheduledEventAttributes" in event
            ]
            assert scheduled == ["proof_segment", "proof_write"]
            assert (
                parked["stage"] == "parked"
                and parked["outcome"]["model_result"] is None
            )
            assert (output / "effect-invocation.json").exists()
            assert (output / "work/marker.txt").read_text() == case["content"]
            assert not (output / "recover").exists()
            assert not (output / "recovered-transcript.json").exists()
            report["parked"] = parked
            report["totals"] = initial_totals
            report["effect_activity_count"] = 1
            report["status"] = "passed bounded Bash park fixture"
            raise VerifiedPark()
        committed = wait("effect_committed.json")
        assert committed["outcome"] == {
            "tool_use_id": accepted["accepted"]["pending"]["id"],
            "content": case["result"],
            "is_error": case["is_error"],
        }
        if args.scenario == "bash-reject":
            assert not (output / "work/marker.txt").exists()
            assert not (output / "effect-invocation.json").exists()
        else:
            assert (output / "work/marker.txt").read_text() == case["content"]
        host, attempt, role = active[-1]
        report["replacement_before_cleanup"] = refused(
            lambda: HostSession(host.path).admit(session)
        )
        cleanup(host, attempt, role)
        admission.begin()
        launch("replacement", worker_host)
        (output / "recover").touch()
        result = wait("result.json")
        history = wait("history.json")
        scheduled = [
            event["activityTaskScheduledEventAttributes"]["activityType"]["name"]
            for event in history["events"]
            if "activityTaskScheduledEventAttributes" in event
        ]
        assert scheduled == ["proof_segment", "proof_write", "proof_recovery"]
        assert (
            len(
                [
                    event
                    for event in history["events"]
                    if "activityTaskCompletedEventAttributes" in event
                ]
            )
            == 3
        )
        report["effect_activity_count"] = scheduled.count("proof_write")
        report["totals"] = admission.reconcile(wait("replacement-accounting.json"))
        if seed is not None:
            prior = seed["prior_accounting"]
            report["prior_accounting"] = prior
            cumulative = {
                field: prior[field] + report["totals"][field]
                for field in ("cost_usd", "input", "output", "turns")
            }
            report["cumulative_checkpoint_usage"] = cumulative
            if (
                cumulative["cost_usd"] >= 0.05
                or cumulative["input"] >= 20000
                or cumulative["output"] >= 2048
            ):
                raise AdmissionRefused("Cumulative checkpoint allowance reached")
        assert result["effect_count"] == (0 if args.scenario == "bash-reject" else 1)
        assert len(result["callbacks"]) == 1
        if args.scenario == "bash-reject":
            assert not (output / "work/marker.txt").exists()
            assert not (output / "effect-invocation.json").exists()
        else:
            assert (output / "work/marker.txt").read_text() == case["content"]
        report["result"] = result
        if args.scenario == "mixed-read":
            report["mixed_read"] = inspect_mixed_read(
                output, accepted["accepted"], result
            )
        if not report.get("log_errors"):
            report["status"] = "passed bounded " + case["tool"] + " fixture"
    except VerifiedPark:
        pass
    except BaseException as exc:
        report["error"] = type(exc).__name__ + ": " + str(exc)
        admission.fail(report["error"])
    finally:
        for host, attempt, role in list(reversed(active)):
            try:
                cleanup(host, attempt, role)
            except Exception as exc:
                report["status"] = "nonpassing"
                report.setdefault("cleanup_errors", []).append(
                    type(exc).__name__ + ": " + str(exc)
                )
        report["cleanup"] = receipts
        save(output / "report.json", report)
    return 0 if report["status"].startswith("passed") else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--approval")
    parser.add_argument(
        "--scenario",
        choices=("write", "bash-error", "bash-reject", "bash-park", "mixed-read"),
        default="write",
    )
    parser.add_argument("--accept-residual-risk", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--server")
    parser.add_argument("--resume-from")
    parser.add_argument("--role", choices=("coordinator", "initial", "replacement"))
    parser.add_argument("--attempt")
    parser.add_argument("--session")
    args = parser.parse_args()
    if args.role:
        asyncio.run(coordinator(args) if args.role == "coordinator" else worker(args))
    elif args.approval and args.output and args.server:
        raise SystemExit(execute(args))
    else:
        print(
            json.dumps(
                configuration(
                    args.scenario,
                    retained_seed(args.resume_from) if args.resume_from else None,
                ),
                indent=2,
                sort_keys=True,
            )
        )
