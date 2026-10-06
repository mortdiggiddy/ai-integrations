"""Refuse incomplete approvals and retain nonpassing monitored scenario state."""

# Scripted pytest fixtures use dynamic payloads, including malformed records.
# pyright: reportMissingParameterType=false

import sys
from pathlib import Path
from typing import Any

import pytest

for parent in Path(__file__).resolve().parents:
    experiments = parent / "docs/skill-recovery/experiments"
    if (experiments / "host_session.py").exists():
        sys.path.insert(0, str(experiments))
        break

from host_session import AdmissionRefused, ExperimentAdmission, HostSession
from write_recovery import (
    BASH_COMMAND,
    BASH_CONTENT,
    BASH_PARK_COMMAND,
    BASH_REJECTED,
    BASH_RESULT,
    RESULT,
    ProofStore,
    WriteRateMonitor,
    check_output_space,
    configuration,
    external_effect,
    inspect_mixed_read,
    proof_case,
    recorded_result,
    retained_seed,
    validate_effect_input,
)


@pytest.mark.parametrize(
    "fault", [None, "cleanup", "role", "effect", "digest", "input", "seed", "usage"]
)
def test_retained_checkpoint_continuation_refuses_changed_state(tmp_path, fault):
    import hashlib
    import json

    from write_recovery import CONTENT, READ_SEED

    entries = [{"uuid": "pending", "type": "assistant"}]
    accepted: dict[str, Any] = {
        "pending": {
            "id": "original",
            "name": "Write",
            "input": {"file_path": "/state/work/marker.txt", "content": CONTENT},
        },
        "transcript_sha256": hashlib.sha256(
            json.dumps(entries, sort_keys=True).encode()
        ).hexdigest(),
    }
    receipt = {"removal_verified": True, "stopped_state": {"Pid": 0, "Running": False}}
    report: dict[str, Any] = {
        "status": "nonpassing",
        "error": "AdmissionRefused: Observed allowance or request planning bound reached",
        "config": {
            "scenario": "deferred-mixed-read-fresh-worker-metered-enterprise-v1"
        },
        "cleanup": [
            {"role": role, "receipt": {"host_receipt": json.dumps(receipt)}}
            for role in ("initial", "coordinator")
        ],
    }
    accounting = {
        "model": "claude-haiku-4-5-20251001",
        "cost_usd": 0.00714,
        "input": 4545,
        "output": 519,
        "turns": 4,
    }
    if fault == "cleanup":
        report["cleanup"][0]["receipt"]["host_receipt"] = json.dumps(
            {**receipt, "removal_verified": False}
        )
    if fault == "role":
        report["cleanup"].pop()
    if fault == "digest":
        accepted["transcript_sha256"] = "changed"
    if fault == "input":
        accepted["pending"]["input"]["content"] = "changed"
    if fault == "usage":
        accounting["cost_usd"] = 0.05
    (tmp_path / "work").mkdir()
    (tmp_path / "work/input.txt").write_text(
        "changed" if fault == "seed" else READ_SEED
    )
    if fault == "effect":
        (tmp_path / "effect-invocation.json").write_text("{}")
    for name, data in (
        ("report.json", report),
        ("segment_committed.json", {"accepted": accepted}),
        ("original-transcript.json", entries),
        ("initial-accounting.json", accounting),
        ("prompt.json", {"prompt": "retained"}),
    ):
        (tmp_path / name).write_text(json.dumps(data))
    (tmp_path / "initial-hook-decisions.jsonl").write_text("")
    if fault is None:
        seed = retained_seed(tmp_path)
        assert seed["accepted"] == accepted
        assert configuration("mixed-read", seed)["segments"] == 1
        assert (
            configuration("mixed-read", seed)["authorization"]
            != configuration("mixed-read")["authorization"]
        )
    else:
        with pytest.raises(AdmissionRefused):
            retained_seed(tmp_path)


@pytest.mark.parametrize(
    "mutation",
    [
        None,
        "single-effect",
        "lost-effect",
        "missing-denial",
        "missing-read",
        "late-read",
        "silent-model",
    ],
)
def test_mixed_read_acceptance_requires_transcript_and_hook_order(tmp_path, mutation):
    import json

    from temporalio.claude_agent_sdk._defer_hook import ONE_AT_A_TIME

    calls = [
        {"type": "tool_use", "id": key, "name": name}
        for key, name in (
            ("before", "Read"),
            ("accepted", "Write"),
            ("extra", "Write"),
            ("after", "Read"),
        )
    ]
    results = [
        {
            "type": "tool_result",
            "tool_use_id": key,
            "content": content,
            "is_error": error,
        }
        for key, content, error in (
            ("before", "READ_BEFORE_EFFECT", False),
            ("extra", "denied", True),
            ("after", "denied", True),
        )
    ]
    decisions = [
        {
            "id": key,
            "event": event,
            "decision": decision,
            "reason": ONE_AT_A_TIME if decision == "deny" else None,
        }
        for key, event, decision in (
            ("before", "PostToolUse", "none"),
            ("accepted", "PreToolUse", "defer"),
            ("extra", "PreToolUse", "deny"),
            ("after", "PreToolUse", "deny"),
        )
    ]
    response = "The later Write and Read were denied. " + RESULT
    if mutation == "single-effect":
        calls = [row for row in calls if row["id"] != "extra"]
    if mutation == "lost-effect":
        decisions = [row for row in decisions if row["id"] != "extra"]
    if mutation == "missing-denial":
        results = [row for row in results if row["tool_use_id"] != "extra"]
    if mutation == "missing-read":
        results = [row for row in results if row["tool_use_id"] != "before"]
    if mutation == "late-read":
        decisions.append(decisions.pop(0))
    if mutation == "silent-model":
        response = RESULT
    (tmp_path / "original-transcript.json").write_text(
        json.dumps([{"message": {"content": calls}}, {"message": {"content": results}}])
    )
    (tmp_path / "initial-hook-decisions.jsonl").write_text(
        "\n".join(json.dumps(row) for row in decisions)
    )
    args = (
        tmp_path,
        {"pending": {"id": "accepted"}},
        {"segment": {"result": response}},
    )
    if mutation in (None, "single-effect"):
        evidence = inspect_mixed_read(*args)
        assert evidence["multiple_effect_shape"] == (mutation is None)
        assert evidence["successful_reads"] == ["before"]
        assert evidence["denied_reads"] == ["after"]
    else:
        with pytest.raises(AdmissionRefused):
            inspect_mixed_read(*args)


def test_bash_profile_has_separate_exact_authorization(monkeypatch):
    monkeypatch.setattr("write_recovery.source_digest", lambda: "same-source")
    write, bash = configuration(), configuration("bash-error")
    assert write["authorization"] != bash["authorization"]
    assert bash["segments"] == 2 and bash["retries"] == 0
    assert "\\" not in BASH_COMMAND
    assert "```sh\n" + BASH_COMMAND + "\n```" in proof_case("bash-error")["prompt"]
    with pytest.raises(AdmissionRefused):
        ExperimentAdmission.validate(write, bash)


@pytest.mark.parametrize(
    "inputs",
    [
        {"command": "exit 7"},
        {"command": BASH_COMMAND, "run_in_background": True},
        {"command": BASH_COMMAND, "timeout": 60000},
        {"command": BASH_COMMAND, "description": 1},
    ],
)
def test_bash_unapproved_input_never_dispatches(inputs, tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "write_recovery.subprocess.run", lambda *a, **kw: calls.append(a)
    )
    with pytest.raises(AdmissionRefused):
        external_effect(
            {"pending": {"name": "Bash", "id": "original", "input": inputs}},
            "bash-error",
            tmp_path,
        )
    assert not calls and not (tmp_path / "effect-invocation.json").exists()


@pytest.mark.parametrize("failure", [None, "timeout", "lost", "wrong-terminal"])
def test_bash_claim_known_error_and_uncertainty(tmp_path, monkeypatch, failure):
    import subprocess

    (tmp_path / "work").mkdir()
    accepted = {
        "pending": {
            "name": "Bash",
            "id": "original",
            "input": {"command": BASH_COMMAND},
        }
    }
    calls = []

    def run(argv, **options):
        calls.append((argv, options))
        (tmp_path / "work/marker.txt").write_text(BASH_CONTENT)
        if failure == "timeout":
            raise subprocess.TimeoutExpired(argv, 3)
        if failure == "lost":
            raise OSError("executor observation lost")
        return subprocess.CompletedProcess(
            argv, 0 if failure == "wrong-terminal" else 7, "", BASH_RESULT
        )

    monkeypatch.setattr("write_recovery.subprocess.run", run)
    outcome = external_effect(accepted, "bash-error", tmp_path)
    assert len(calls) == 1 and calls[0][1]["timeout"] == 3
    if failure:
        assert outcome["parked"] and outcome["model_result"] is None
        assert (tmp_path / "bash-park.json").exists()
    else:
        assert outcome == {
            "tool_use_id": "original",
            "content": BASH_RESULT,
            "is_error": True,
        }
    with pytest.raises(FileExistsError):
        external_effect(accepted, "bash-error", tmp_path)
    assert len(calls) == 1


def test_fixed_bash_command_in_isolated_image():
    if not Path("/fixture/host_session_offline.py").is_file():
        pytest.skip("The fixed command requires the isolated image state mount")
    state = Path("/state")
    (state / "work").mkdir(exist_ok=True)
    accepted = {
        "pending": {
            "name": "Bash",
            "id": "original",
            "input": {"command": BASH_COMMAND},
        }
    }
    outcome = external_effect(accepted, "bash-error", state, activity_attempt=1)
    assert outcome == {
        "tool_use_id": "original",
        "content": BASH_RESULT,
        "is_error": True,
    }
    assert (state / "work/marker.txt").read_text() == BASH_CONTENT
    with pytest.raises(FileExistsError):
        external_effect(accepted, "bash-error", state, activity_attempt=2)


def test_bash_rejection_dispatches_no_process(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "write_recovery.subprocess.run", lambda *a, **kw: calls.append(a)
    )
    accepted = {
        "pending": {
            "name": "Bash",
            "id": "original",
            "input": {"command": BASH_COMMAND},
        }
    }
    outcome = external_effect(accepted, "bash-reject", tmp_path, activity_attempt=1)
    assert not calls
    assert not (tmp_path / "effect-invocation.json").exists()
    assert not (tmp_path / "work/marker.txt").exists()
    assert outcome == {
        "tool_use_id": "original",
        "content": BASH_REJECTED,
        "is_error": True,
    }


def test_bash_park_profile_has_one_segment_and_distinct_command(tmp_path, monkeypatch):
    import subprocess

    accepted = {
        "pending": {
            "name": "Bash",
            "id": "original",
            "input": {"command": BASH_PARK_COMMAND},
        }
    }
    calls = []

    def run(argv, **options):
        calls.append(argv)
        raise subprocess.TimeoutExpired(argv, 3)

    monkeypatch.setattr("write_recovery.subprocess.run", run)
    outcome = external_effect(accepted, "bash-park", tmp_path, activity_attempt=1)
    assert outcome["parked"] and outcome["model_result"] is None
    assert calls == [["/bin/sh", "-c", BASH_PARK_COMMAND]]
    assert configuration("bash-park")["segments"] == 1
    with pytest.raises(FileExistsError):
        external_effect(accepted, "bash-park", tmp_path, activity_attempt=2)
    assert len(calls) == 1


def test_fixed_park_command_in_isolated_image():
    if not Path("/fixture/host_session_offline.py").is_file():
        pytest.skip("The fixed command requires the isolated image state mount")
    state = Path("/state/park-command-check")
    state.mkdir()
    Path("/state/work").mkdir(exist_ok=True)
    accepted = {
        "pending": {
            "name": "Bash",
            "id": "original-park",
            "input": {"command": BASH_PARK_COMMAND},
        }
    }
    outcome = external_effect(accepted, "bash-park", state, activity_attempt=1)
    assert outcome["parked"] and outcome["model_result"] is None
    cause = outcome["cause"]
    assert isinstance(cause, str) and "TimeoutExpired" in cause
    assert Path("/state/work/marker.txt").read_text() == BASH_CONTENT
    with pytest.raises(FileExistsError):
        external_effect(accepted, "bash-park", state, activity_attempt=2)


def test_bash_exact_recorded_error_does_not_become_write_success():
    from dataclasses import asdict, make_dataclass

    Call = make_dataclass("Call", [("id", str), ("name", str), ("input", dict)])
    call = Call("original", "Bash", {"command": BASH_COMMAND})
    validate_effect_input(asdict(call), "bash-error")
    expected = {
        "pending": asdict(call),
        "outcome": {"tool_use_id": call.id, "content": BASH_RESULT, "is_error": True},
    }
    result = recorded_result(call, expected, "bash-error")
    assert (
        result.tool_use_id == "original"
        and result.content == BASH_RESULT
        and result.is_error
    )
    with pytest.raises(AdmissionRefused):
        recorded_result(call, expected)
    expected["outcome"]["is_error"] = False
    with pytest.raises(AdmissionRefused):
        recorded_result(call, expected, "bash-error")


def usage_event(**raw_changes: Any) -> dict[str, Any]:
    raw = {
        "status": "allowed",
        "rateLimitType": "overage",
        "overageStatus": "allowed",
        "isUsingOverage": False,
        "overageInUse": True,
        **raw_changes,
    }
    return {
        "kind": "RateLimitEvent",
        "message": {
            "rate_limit_info": {
                "status": raw["status"],
                "rate_limit_type": raw["rateLimitType"],
                "overage_status": raw["overageStatus"],
                "raw": raw,
            }
        },
    }


def test_write_monitor_accepts_metered_event_without_changing_legacy_guard():
    from subscription_sdk_control import Monitor

    event = usage_event()
    monitor = WriteRateMonitor()
    assert monitor.inspect(event) is None
    assert monitor.rate_limit_seen
    assert monitor.events == [event]
    assert Monitor().inspect(event) == "ambiguous_active_or_unverifiable_overage"


def test_write_monitor_accepts_omitted_false_header():
    event = usage_event(rateLimitType="five_hour")
    del event["message"]["rate_limit_info"]["raw"]["overageInUse"]
    monitor = WriteRateMonitor()
    assert monitor.inspect(event) is None
    assert monitor.rate_limit_seen


@pytest.mark.parametrize(
    "changes",
    [
        {"status": "rejected"},
        {"status": None},
        {"rateLimitType": None},
        {"overageStatus": "rejected"},
        {"overageStatus": None},
        {"overageInUse": "true"},
        {"isUsingOverage": 0},
    ],
)
def test_write_monitor_refuses_denial_and_incomplete_metadata(changes):
    monitor = WriteRateMonitor()
    assert (
        monitor.inspect(usage_event(**changes)) == "rate_limit_refused_or_unverifiable"
    )
    assert not monitor.rate_limit_seen


def test_write_monitor_refuses_typed_raw_disagreement_and_missing_info():
    event = usage_event()
    event["message"]["rate_limit_info"]["status"] = "allowed_warning"
    monitor = WriteRateMonitor()
    assert monitor.inspect(event) == "rate_limit_refused_or_unverifiable"
    assert (
        monitor.inspect({"kind": "RateLimitEvent", "message": {}})
        == "rate_limit_refused_or_unverifiable"
    )
    assert not monitor.rate_limit_seen


def test_output_space_refuses_before_creating_directory(tmp_path, monkeypatch):
    from types import SimpleNamespace

    output = tmp_path / "new-parent" / "proof"
    monkeypatch.setattr(
        "write_recovery.shutil.disk_usage", lambda path: SimpleNamespace(free=0)
    )
    with pytest.raises(AdmissionRefused, match="reservation not consumed"):
        check_output_space(output)
    assert not output.parent.exists()


def test_output_space_preserves_existing_directory(tmp_path):
    marker = tmp_path / "retained.txt"
    marker.write_text("retained")
    with pytest.raises(AdmissionRefused, match="already exists"):
        check_output_space(tmp_path)
    assert marker.read_text() == "retained"


@pytest.fixture
def config(monkeypatch):
    monkeypatch.setattr("write_recovery.source_digest", lambda: "approved-source")
    return configuration()


@pytest.mark.parametrize("field", sorted(ExperimentAdmission.REQUIRED))
def test_each_missing_or_changed_control_refuses(tmp_path, config, field):
    for candidate in (
        {key: value for key, value in config.items() if key != field},
        {**config, field: None},
    ):
        with pytest.raises(AdmissionRefused):
            ExperimentAdmission.initialize(
                tmp_path / "admission.json", candidate, config
            )
        assert not (tmp_path / "admission.json").exists()


def accounted(config, **changes):
    return {
        "model": config["model"],
        "cost_usd": 0.001,
        "input": 20,
        "output": 5,
        "turns": 1,
        **changes,
    }


@pytest.mark.parametrize(
    "reason", ["interrupt failed", "timeout", "owner lost", "unknown usage"]
)
def test_failed_attempt_blocks_fresh_admission(tmp_path, config, reason):
    admission = ExperimentAdmission.initialize(
        tmp_path / "admission.json", config, config
    )
    admission.begin()
    admission.fail(reason)
    with pytest.raises(AdmissionRefused):
        ExperimentAdmission(admission.path, config).begin()
    assert admission.read()["segments"][0]["accounting"] is None


@pytest.mark.parametrize(
    "changes",
    [
        {"input": None},
        {"input": True},
        {"output": -1},
        {"cost_usd": float("nan")},
        {"cost_usd": None},
        {"model": "other"},
        {"turns": 3},
        {"cost_usd": 0.05},
        {"input": 20000},
        {"output": 2048},
    ],
)
def test_unresolved_or_excessive_usage_blocks_continuation(tmp_path, config, changes):
    admission = ExperimentAdmission.initialize(
        tmp_path / "admission.json", config, config
    )
    admission.begin()
    with pytest.raises(AdmissionRefused):
        admission.reconcile(accounted(config, **changes))
    with pytest.raises(AdmissionRefused):
        ExperimentAdmission(admission.path, config).begin()
    assert admission.read()["failure"]


def test_replacement_accumulates_without_reusing_reservation(tmp_path, config):
    admission = ExperimentAdmission.initialize(
        tmp_path / "admission.json", config, config
    )
    admission.begin()
    with pytest.raises(AdmissionRefused):
        ExperimentAdmission(admission.path, config).begin()
    admission.reconcile(accounted(config))
    reopened = ExperimentAdmission(admission.path, config)
    reopened.begin()
    assert reopened.reconcile(accounted(config)) == {
        "input": 40,
        "output": 10,
        "cost_usd": 0.002,
        "turns": 2,
    }
    with pytest.raises(AdmissionRefused):
        reopened.begin()
    with pytest.raises(FileExistsError):
        ExperimentAdmission.initialize(admission.path, config, config)


def test_false_retry_bound_is_not_integer_zero(tmp_path, config):
    with pytest.raises(AdmissionRefused):
        ExperimentAdmission.initialize(
            tmp_path / "admission.json", {**config, "retries": False}, config
        )


@pytest.mark.asyncio
async def test_retained_transcript_cas_refuses_stale_head(tmp_path):
    store = ProofStore(tmp_path / "store.db", create=True)
    key = {"project_key": "fixture", "session_id": "original"}
    original = [{"uuid": "pending", "message": {"id": "tool-original"}}]
    await store.append(key, original)
    reopened = ProofStore(tmp_path / "store.db")
    assert not await reopened.append_if_unchanged(key, "wrong", [{"uuid": "bad"}])
    assert await reopened.load(key) == original
    assert await reopened.append_if_unchanged(
        key,
        "pending",
        [{"uuid": "result", "tool_use_id": "tool-original", "content": "exact"}],
    )
    assert not await store.append_if_unchanged(key, "pending", [{"uuid": "repeat"}])
    retained = await reopened.load(key)
    assert isinstance(retained, list) and len(retained) == 2


def test_missing_transcript_store_is_never_recreated(tmp_path):
    import sqlite3

    with pytest.raises(sqlite3.OperationalError):
        ProofStore(tmp_path / "missing.db")
    assert not (tmp_path / "missing.db").exists()


@pytest.mark.parametrize(
    "field", ["id", "name", "input", "session_key", "transcript_uuid", "subpath"]
)
def test_original_pending_identity_is_exact(field):
    from dataclasses import asdict, make_dataclass

    Call = make_dataclass(
        "Call",
        [
            (key, object)
            for key in (
                "id",
                "name",
                "input",
                "session_key",
                "transcript_uuid",
                "subpath",
            )
        ],
    )
    call = Call(
        "original",
        "Write",
        {"content": "same"},
        {"session_id": "original-session"},
        "original-uuid",
        None,
    )
    expected = {
        "pending": asdict(call),
        "outcome": {"tool_use_id": call.id, "content": RESULT, "is_error": False},
    }
    result = recorded_result(call, expected)
    assert (
        result.tool_use_id == call.id
        and result.content == RESULT
        and result.is_error is False
    )
    setattr(call, field, "changed")
    with pytest.raises(AdmissionRefused):
        recorded_result(call, expected)


@pytest.mark.parametrize(
    "field,value", [("tool_use_id", "other"), ("content", "other"), ("is_error", True)]
)
def test_recorded_result_is_not_replaced(field, value):
    from dataclasses import asdict, dataclass

    @dataclass
    class Call:
        id: str = "original"

    call = Call()
    expected = {
        "pending": asdict(call),
        "outcome": {"tool_use_id": call.id, "content": RESULT, "is_error": False},
    }
    expected["outcome"][field] = value
    with pytest.raises(AdmissionRefused):
        recorded_result(call, expected)


def test_launcher_binds_before_start_and_refuses_second_launch(tmp_path):
    host = HostSession.initialize(tmp_path / "host.db")
    attempt = host.admit("session")

    class Engine:
        calls = []

        def command(self, *argv):
            self.calls.append(argv)
            if argv[:2] == ("image", "inspect"):
                return "sha256:" + "b" * 64
            if argv[0] == "create":
                assert host.snapshot(attempt)["resource"] is None
                assert "never" in argv and "--read-only" in argv and "none" in argv
                return "a" * 64
            assert argv[:2] == ("container", "start")
            assert host.snapshot(attempt)["resource"] == "a" * 64
            return ""

    engine = Engine()
    host.launch(attempt, "sha256:" + "b" * 64, ["harmless"], [], docker=engine)
    with pytest.raises(AdmissionRefused):
        host.launch(attempt, "sha256:" + "b" * 64, ["harmless"], [], docker=engine)
    assert len(engine.calls) == 3


@pytest.mark.asyncio
async def test_uncertain_bash_workflow_parks_without_recovery():
    if not Path("/opt/temporal").is_file():
        pytest.skip(
            "Existing server must be supplied explicitly to the isolated driver"
        )
    import asyncio

    from write_recovery_workflow import WriteRecoveryProof

    from temporalio import activity
    from temporalio.testing import WorkflowEnvironment
    from temporalio.worker import UnsandboxedWorkflowRunner, Worker

    recovered = []

    @activity.defn(name="proof_segment")
    async def initial(session: str):
        return {"pending": {"id": session, "name": "Bash"}}

    @activity.defn(name="proof_write")
    async def uncertain(accepted: dict):
        return {"parked": True, "model_result": None, "accepted": accepted}

    @activity.defn(name="proof_recovery")
    async def recovery(data: dict):
        recovered.append(data)
        raise AssertionError("An ambiguous outcome cannot reach recovery")

    async with await WorkflowEnvironment.start_local(
        dev_server_existing_path="/opt/temporal"
    ) as env:
        async with Worker(
            env.client,
            task_queue="park-proof",
            workflows=[WriteRecoveryProof],
            activities=[initial, uncertain, recovery],
            workflow_runner=UnsandboxedWorkflowRunner(),
        ):
            handle = await env.client.start_workflow(
                WriteRecoveryProof.run,
                "original-bash",
                id="park-proof",
                task_queue="park-proof",
            )
            await handle.signal(WriteRecoveryProof.allow_dispatch)
            await handle.signal(WriteRecoveryProof.allow_recovery)

            async def parked():
                while (await handle.query(WriteRecoveryProof.state))[
                    "stage"
                ] != "parked":
                    await asyncio.sleep(0.05)

            await asyncio.wait_for(parked(), 10)
            state = await handle.query(WriteRecoveryProof.state)
            outcome = state["outcome"]
            assert isinstance(outcome, dict)
            assert outcome["model_result"] is None and not recovered
            events = (await handle.fetch_history()).events
            scheduled = [
                e.activity_task_scheduled_event_attributes.activity_type.name
                for e in events
                if e.HasField("activity_task_scheduled_event_attributes")
            ]
            assert scheduled == ["proof_segment", "proof_write"]
            description = await handle.describe()
            assert (
                description.status is not None and description.status.name == "RUNNING"
            )
            await handle.terminate("Offline park check complete")


@pytest.mark.asyncio
async def test_workflow_commits_before_effect_and_replacement_reuses_result(tmp_path):
    if not Path("/opt/temporal").is_file():
        pytest.skip(
            "Existing server must be supplied explicitly to the isolated driver"
        )
    import asyncio
    from datetime import timedelta

    from write_recovery_workflow import WriteRecoveryProof

    from temporalio import activity
    from temporalio.testing import WorkflowEnvironment
    from temporalio.worker import UnsandboxedWorkflowRunner, Worker

    marker = tmp_path / "marker"
    calls = []

    @activity.defn(name="proof_segment")
    async def initial(session: str):
        return {"pending": {"id": session, "name": "Write"}}

    @activity.defn(name="proof_write")
    async def effect(accepted: dict):
        calls.append(accepted)
        marker.write_text("one effect")
        return {
            "tool_use_id": accepted["pending"]["id"],
            "content": RESULT,
            "is_error": False,
        }

    @activity.defn(name="proof_recovery")
    async def recovery(data: dict):
        assert len(calls) == 1 and marker.read_text() == "one effect"
        return data["outcome"]

    async with await WorkflowEnvironment.start_local(
        dev_server_existing_path="/opt/temporal"
    ) as env:
        async with Worker(
            env.client,
            task_queue="proof-check",
            workflows=[WriteRecoveryProof],
            workflow_runner=UnsandboxedWorkflowRunner(),
        ):
            async with Worker(
                env.client, task_queue="proof-check", activities=[initial, effect]
            ):
                handle = await env.client.start_workflow(
                    WriteRecoveryProof.run,
                    "original",
                    id="write-order-check",
                    task_queue="proof-check",
                    execution_timeout=timedelta(seconds=20),
                )

                async def stage(name):
                    for _ in range(100):
                        if (await handle.query(WriteRecoveryProof.state))[
                            "stage"
                        ] == name:
                            return
                        await asyncio.sleep(0.02)
                    raise AssertionError("Stage not reached")

                await stage("segment_committed")
                assert not marker.exists() and not calls
                await handle.signal(WriteRecoveryProof.allow_dispatch)
                await stage("effect_committed")
                assert len(calls) == 1
            async with Worker(
                env.client, task_queue="proof-check", activities=[recovery]
            ):
                await handle.signal(WriteRecoveryProof.allow_recovery)
                assert await handle.result() == {
                    "tool_use_id": "original",
                    "content": RESULT,
                    "is_error": False,
                }
                events = (await handle.fetch_history()).events
                assert (
                    len(
                        [
                            event
                            for event in events
                            if event.HasField(
                                "activity_task_completed_event_attributes"
                            )
                        ]
                    )
                    == 3
                )
                assert len(calls) == 1
