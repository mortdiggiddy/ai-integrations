"""Process observation contracts with scripted clients and daemons, no engine calls."""

# Scripted pytest fixtures use dynamic payloads, including malformed records.
# pyright: reportMissingParameterType=false

from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
import sdk_shutdown_probe as probe
from host_session import HostSession
from test_host_admission import (  # pyright: ignore[reportImplicitRelativeImport]
    Container,
)


def process(pid, start, comm="claude", state="S") -> dict[str, Any]:
    return {"pid": pid, "start": start, "comm": comm, "state": state}


def snapshot(*rows) -> dict[str, Any]:
    return {
        "version": 1,
        "enumeration_completed": True,
        "enumerated_pids": [row["pid"] for row in rows],
        "processes": list(rows),
        "errors": [],
        "complete": True,
    }


def completed() -> dict[str, Any]:
    parent = process(1, "100", "python")
    return {
        "stage": "finished",
        "connected": True,
        "interrupt_acknowledged": True,
        "sdk_closed": True,
        "stop_requested": True,
        "shutdown_unresolved": False,
        "prompt_submission_started": False,
        "before_connect": snapshot(parent),
        "after_connect": snapshot(
            parent, process(7, "200"), process(8, "201", "child")
        ),
        "after_disconnect": snapshot(parent),
    }


@pytest.mark.parametrize(
    "name", ["before_connect", "after_connect", "after_disconnect"]
)
@pytest.mark.parametrize("value", [None, [], {}, "bad", {"complete": True}])
def test_missing_or_malformed_inventory_never_proves_absence(name, value):
    state = completed()
    if value is None:
        del state[name]
    else:
        state[name] = value
    result = probe.classify_observations(state)
    assert result["sdk_control_completed"] is True
    assert result["sdk_process_absence_before_host_teardown"] is False
    assert result["process_observation_unresolved"] == [
        name + " inventory missing, invalid or incomplete"
    ]


@pytest.mark.parametrize(
    "fault",
    [
        "enumeration",
        "errors",
        "incomplete",
        "missing_pid",
        "duplicate_pid",
        "bool_pid",
        "row_pid",
        "start",
        "bool_start",
        "noncanonical_start",
        "state",
        "comm",
        "row",
        "version",
    ],
)
def test_invalid_observation_contract(fault):
    state = completed()
    value = state["after_disconnect"]
    if fault == "enumeration":
        value["enumeration_completed"] = False
    elif fault == "errors":
        value["errors"] = [{"pid": 7, "error": "PermissionError"}]
    elif fault == "incomplete":
        value["complete"] = False
    elif fault == "missing_pid":
        value["enumerated_pids"].append(7)
    elif fault == "duplicate_pid":
        value["enumerated_pids"].append(1)
        value["processes"].append(copy.deepcopy(value["processes"][0]))
    elif fault == "bool_pid":
        value["enumerated_pids"] = [True]
    elif fault == "row_pid":
        value["processes"][0]["pid"] = True
    elif fault == "row":
        value["processes"] = [None]
    elif fault == "version":
        value["version"] = True
    else:
        field, changed = {
            "start": ("start", "bad"),
            "bool_start": ("start", True),
            "noncanonical_start": ("start", "0100"),
            "state": ("state", []),
            "comm": ("comm", ""),
        }[fault]
        value["processes"][0][field] = changed
    result = probe.classify_observations(state)
    assert not result["process_observations_valid"]
    assert not result["sdk_process_absence_before_host_teardown"]
    assert result["process_observation_unresolved"]


@pytest.mark.parametrize(
    "pid,start,state,absent",
    [(7, "200", "S", False), (8, "201", "Z", False), (7, "999", "S", True)],
)
def test_every_identity_including_zombie_and_pid_reuse(pid, start, state, absent):
    value = completed()
    value["after_disconnect"] = snapshot(
        process(1, "100", "python"), process(pid, start, state=state)
    )
    result = cast(dict[str, Any], probe.classify_observations(value))
    assert result["sdk_process_absence_before_host_teardown"] is absent
    assert {row["pid"] for row in result["sdk_processes_observed"]} == {7, 8}


def test_explicit_valid_disappearance_and_no_launch():
    value = completed()
    result = probe.classify_observations(value)
    assert result["sdk_control_completed"] and result["process_observations_valid"]
    assert result["sdk_process_absence_before_host_teardown"]
    assert result["process_observation_unresolved"] == []
    value["after_connect"] = copy.deepcopy(value["before_connect"])
    result = probe.classify_observations(value)
    assert not result["sdk_process_absence_before_host_teardown"]
    assert result["process_observation_unresolved"] == [
        "No relevant process identity observed after connection"
    ]


def test_existing_claude_identity_is_also_relevant():
    value = completed()
    value["before_connect"] = copy.deepcopy(value["after_connect"])
    value["after_disconnect"] = copy.deepcopy(value["after_connect"])
    result = probe.classify_observations(value)
    assert result["sdk_processes_observed"] == [process(7, "200")]
    assert not result["sdk_process_absence_before_host_teardown"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("connected", False),
        ("interrupt_acknowledged", False),
        ("sdk_closed", False),
        ("stop_requested", False),
        ("shutdown_unresolved", True),
        ("prompt_submission_started", True),
        ("stage", "disconnect"),
        ("timeout_stage", "disconnect"),
        ("interrupt_error", "failed"),
    ],
)
def test_control_completion_does_not_follow_process_absence(field, value):
    state = completed()
    state[field] = value
    result = probe.classify_observations(state)
    assert not result["sdk_control_completed"]
    assert result["process_observations_valid"]
    assert result["sdk_process_absence_before_host_teardown"] is (field != "sdk_closed")


def stat(pid=7, start="200"):
    return f"{pid} (claude) " + " ".join(["S"] + ["0"] * 18 + [start])


@pytest.mark.parametrize(
    "fault",
    [
        "enumerate",
        "partial_enumerate",
        "stat",
        "comm",
        "vanished",
        "malformed",
        "identity",
        "deadline",
    ],
)
def test_collection_failure_is_recorded(tmp_path, monkeypatch, fault):
    directory = tmp_path / "7"
    directory.mkdir()
    real_read = Path.read_text
    reads = 0

    def read(path, *args, **kwargs):
        nonlocal reads
        if path.parent == directory:
            if path.name == "stat":
                reads += 1
                if fault == "stat":
                    raise PermissionError("unreadable")
                if fault == "vanished":
                    raise FileNotFoundError("raced")
                if fault == "malformed":
                    return "bad stat"
                return stat(start="201" if fault == "identity" and reads > 1 else "200")
            if fault == "comm":
                raise PermissionError("unreadable comm")
            return "claude\n"
        return real_read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read)
    if fault in {"enumerate", "partial_enumerate"}:

        def enumerate_paths(path):
            if fault == "partial_enumerate":
                yield directory
            raise PermissionError("enumeration denied")

        monkeypatch.setattr(Path, "iterdir", enumerate_paths)
    result = cast(
        dict[str, Any],
        probe.inventory(tmp_path, timeout=0 if fault == "deadline" else 2),
    )
    assert result["complete"] is False
    assert result["errors"]
    assert not probe.valid_inventory(result)
    assert result["errors"][0]["operation"] == (
        "enumerate"
        if fault in {"enumerate", "partial_enumerate", "deadline"}
        else "comm"
        if fault == "comm"
        else "stat_identity"
        if fault == "identity"
        else "stat"
    )
    if fault == "vanished":
        assert result["errors"][0]["vanished_during_collection"] is True
    elif fault not in {"enumerate", "partial_enumerate", "deadline"}:
        assert result["errors"][0]["vanished_during_collection"] is False


def test_successful_collection(tmp_path, monkeypatch):
    (tmp_path / "7").mkdir()
    monkeypatch.setattr(
        Path, "read_text", lambda path: stat() if path.name == "stat" else "claude\n"
    )
    result = probe.inventory(tmp_path)
    assert probe.valid_inventory(result)
    assert result["processes"] == [process(7, "200")]
    assert result["errors"] == []


@pytest.mark.parametrize(
    "fault",
    ["missing", "malformed", "unreadable", "surviving", "valid", "partial_teardown"],
)
def test_host_probe_inventory_contract_end_to_end(tmp_path, monkeypatch, fault):
    output = tmp_path / "results"
    daemons = []

    class Daemon(Container):
        def __init__(self):  # pyright: ignore[reportMissingSuperCall]
            self.host = HostSession(output / "host.db")
            self.root = output
            self.session = ""

        def inspect(self, resource):
            return {**super().inspect(resource), "HostConfig": {}}

        def command(self, *args):
            if args[:2] == ("image", "inspect"):
                return probe.IMAGE  # pyright: ignore[reportPrivateLocalImportUsage]
            if args[0] == "create":
                root = Path(args[args.index("-v") + 1].split(":")[0])
                self.host = HostSession(root / "host.db")
                attempt = args[args.index("--attempt") + 1]
                super().__init__(self.host, attempt)
                self.root = root
                self.session = args[args.index("--session") + 1]
                if fault == "partial_teardown":
                    self.fail = "remove"
                daemons.append(self)
                return "a" * 64
            if args[:2] == ("container", "start"):
                runner = self.host.claim_runner(self.row["attempt"], self.session)
                value = completed()
                if fault == "missing":
                    del value["after_disconnect"]
                elif fault == "malformed":
                    value["after_disconnect"] = []
                elif fault == "unreadable":
                    value["after_disconnect"]["errors"] = [
                        {"pid": 7, "error": "PermissionError"}
                    ]
                elif fault == "surviving":
                    value["after_disconnect"] = copy.deepcopy(value["after_connect"])
                self.host.observe(self.row["attempt"], runner, value)
                (self.root / "sdk-observations.json").write_text(json.dumps(value))
            return ""

    monkeypatch.setattr(probe, "Docker", Daemon)
    args = SimpleNamespace(output=str(output), inspect_only=False)
    if fault == "valid":
        probe.host_probe(args)
    else:
        with pytest.raises(SystemExit) as exc:
            probe.host_probe(args)
        assert exc.value.code == 1
    report = json.loads((output / "report.json").read_text())
    assert report["sdk_control_completed"] is True
    assert report["sdk_process_absence_before_host_teardown"] is (
        fault in {"valid", "partial_teardown"}
    )
    assert (
        report["replacement_before_cleanup"]
        == "Prior host termination and teardown are unresolved"
    )
    assert (
        report["fresh_runner_before_cleanup"]
        == "Fresh runner has no current host grant"
    )
    if fault == "partial_teardown":
        assert "teardown_error" in report
        assert "replacement_after_cleanup" not in report
        assert daemons[0].host.snapshot(daemons[0].row["attempt"])["removed"] == 0
    else:
        assert report["replacement_after_cleanup"] is True
        receipt = json.loads(report["after_teardown"]["host_receipt"])
        assert receipt["removal_verified"] is True
        assert receipt["stopped_state"] == {"Running": False, "Pid": 0}
