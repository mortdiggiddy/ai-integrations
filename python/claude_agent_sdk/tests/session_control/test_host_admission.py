"""Host admission source checks; Docker faults here are scripted, not engine proof."""

# Scripted pytest fixtures use dynamic payloads, including malformed records.
# pyright: reportMissingParameterType=false

from __future__ import annotations

import asyncio
import json
import multiprocessing
import sqlite3
import sys
import uuid
from collections.abc import Callable
from pathlib import Path

import pytest
import test_lifecycle as lifecycle  # pyright: ignore[reportImplicitRelativeImport]
from test_lifecycle import (  # pyright: ignore[reportImplicitRelativeImport]
    Client,
    started,
)

from temporalio.claude_agent_sdk import SegmentInput, _runner
from temporalio.claude_agent_sdk._session_control import SessionShutdownUnresolved

# Repository tests locate the same module that the isolated driver mounts.
for parent in Path(__file__).resolve().parents:
    experiments = parent / "docs/skill-recovery/experiments"
    if (experiments / "host_session.py").is_file():
        sys.path.insert(0, str(experiments))
        break

from host_session import (  # noqa: E402
    AdmissionRefused,
    HostSession,
    contend,
    owned_runner,
)


class Container:
    def __init__(self, host, attempt):
        self.row = host.snapshot(attempt)
        self.running = True
        self.removed = False
        self.fail: str | None = None
        self.on_remove: Callable[[], None] | None = None

    def inspect(self, resource):
        if self.fail == "inspect":
            raise AdmissionRefused("inspection lost")
        return {
            "Id": resource if self.fail != "identity" else "b" * 64,
            "Name": "/" + self.row["name"],
            "Config": {"Labels": {"durability.attempt": self.row["attempt"]}},
            "State": {"Running": self.running, "Pid": 42 if self.running else 0},
        }

    def kill(self, resource):
        if self.fail == "kill":
            raise AdmissionRefused("kill failed")
        self.running = False

    def wait(self, resource):
        if self.fail == "wait":
            raise AdmissionRefused("wait unresolved")
        return 0

    def remove(self, resource):
        if self.on_remove:
            self.on_remove()
        if self.fail == "remove":
            raise AdmissionRefused("remove unresolved")
        self.removed = True

    def absent(self, resource):
        if self.fail == "enumerate":
            raise AdmissionRefused("daemon unavailable")
        return self.removed and self.fail != "present"


def owned(tmp_path):
    host = HostSession.initialize(tmp_path / "host.db")
    attempt = host.admit("session")
    host.bind(attempt, "a" * 64)
    return host, attempt


@pytest.mark.parametrize(
    "fault", ["inspect", "identity", "kill", "wait", "remove", "enumerate", "present"]
)
def test_unresolved_teardown_blocks_reopened_admission(tmp_path, fault):
    host, attempt = owned(tmp_path)
    resource = Container(host, attempt)
    resource.fail = fault
    with pytest.raises(AdmissionRefused):
        host.teardown(attempt, resource)
    with pytest.raises(AdmissionRefused):
        HostSession(host.path).admit("session")
    row = host.snapshot(attempt)
    assert row["removed"] == 0
    assert bool(row["terminated"]) == (fault in {"remove", "enumerate", "present"})


def test_sdk_closure_and_late_success_do_not_release_host(tmp_path):
    host, attempt = owned(tmp_path)
    runner = host.claim_runner(attempt, "session")
    host.observe(
        attempt,
        runner,
        {"stop_requested": True, "terminal_received": True, "sdk_closed": True},
    )
    host.observe(attempt, runner, {"stop_requested": False, "sdk_closed": True})
    assert host.snapshot(attempt)["stopped"] == 1
    assert json.loads(host.snapshot(attempt)["observations"])["stop_requested"] is True
    with pytest.raises(AdmissionRefused):
        HostSession(host.path).claim_runner(attempt, "session")
    with pytest.raises(AdmissionRefused):
        HostSession(host.path).admit("session")


def test_termination_does_not_admit_during_resource_removal(tmp_path):
    host, attempt = owned(tmp_path)
    contender = HostSession(host.path)
    resource = Container(host, attempt)

    def race():
        with pytest.raises(AdmissionRefused):
            contender.admit("session")

    resource.on_remove = race
    row = host.teardown(attempt, resource)
    assert row["terminated"] and row["removed"]
    replacement = contender.admit("session")
    assert replacement != attempt


def test_stale_owner_and_completion_cannot_change_replacement(tmp_path):
    host, attempt = owned(tmp_path)
    runner = host.claim_runner(attempt, "session")
    host.teardown(attempt, Container(host, attempt))
    replacement = host.admit("session")
    host.bind(replacement, "b" * 64)
    for operation in (
        lambda: host.observe(attempt, runner, {"sdk_closed": True}),
        lambda: host.teardown(attempt, Container(host, replacement)),
        lambda: host.check_runner(attempt, "session", runner),
    ):
        with pytest.raises(AdmissionRefused):
            operation()
    assert host.snapshot(replacement)["terminated"] == 0
    assert host.snapshot(replacement)["removed"] == 0


def test_independent_process_admission_and_owner_loss(tmp_path):
    host = HostSession.initialize(tmp_path / "host.db")
    context = multiprocessing.get_context("spawn")
    event, queue = context.Event(), context.Queue()
    processes = [
        context.Process(target=contend, args=(str(host.path), event, queue))
        for _ in range(2)
    ]
    for process in processes:
        process.start()
    event.set()
    outcomes = [queue.get(timeout=10) for _ in processes]
    for process in processes:
        process.join(10)
        assert process.exitcode == 0
    assert outcomes.count("refused") == 1
    # The winning owner has exited without resource creation or teardown proof.
    with pytest.raises(AdmissionRefused):
        HostSession(host.path).admit("session")


def test_missing_corrupt_and_locked_storage_refuses(tmp_path):
    with pytest.raises(AdmissionRefused):
        HostSession(tmp_path / "absent").admit("session")
    host, _ = owned(tmp_path)
    with pytest.raises(FileExistsError):
        HostSession.initialize(host.path)
    db = sqlite3.connect(host.path)
    db.execute("BEGIN IMMEDIATE")
    try:
        with pytest.raises(AdmissionRefused):
            host.admit("session")
    finally:
        db.close()
    host.path.write_bytes(b"corrupt")
    with pytest.raises(AdmissionRefused):
        host.admit("session")


@pytest.mark.parametrize(
    "fault",
    ["log", "attempt", "session", "code", "boolcode", "pid", "boolpid", "negativepid"],
)
def test_driver_requires_bound_completion_receipt(tmp_path, monkeypatch, fault):
    import host_session_offline as driver

    monkeypatch.setattr(
        driver,
        "__file__",
        str(
            tmp_path
            / "python/claude_agent_sdk/docs/skill-recovery/experiments/host_session_offline.py"
        ),
    )
    operations = []

    class FailedChild:
        def __init__(self):
            self.root = tmp_path
            self.attempt = ""
            self.session = ""

        def command(self, *args):
            operations.append(args)
            if args[:2] == ("image", "inspect"):
                return driver.IMAGE
            if args[0] == "create":
                self.root = Path(args[args.index("-v") + 1].split(":")[0])
                self.attempt = args[args.index("--label") + 1].split("=")[1]
                self.session = args[args.index("--session") + 1]
                return "a" * 64
            if args[:2] == ("container", "logs"):
                if fault != "log":
                    receipt = {
                        "attempt": self.attempt,
                        "session": self.session,
                        "pytest_exit_code": 0,
                        "child_pid": 42,
                    }
                    field, value = {
                        "attempt": ("attempt", "stale"),
                        "session": ("session", "other"),
                        "code": ("pytest_exit_code", 1),
                        "boolcode": ("pytest_exit_code", False),
                        "pid": ("child_pid", "42"),
                        "boolpid": ("child_pid", True),
                        "negativepid": ("child_pid", -1),
                    }[fault]
                    receipt[field] = value
                    (self.root / "ready.json").write_text(json.dumps(receipt))
                return '{"kind": "ready"}\n1 failed, 39 passed'
            return ""

        def inspect(self, resource):
            return {"State": {"Running": False}}

    monkeypatch.setattr(driver, "Docker", FailedChild)
    expected = (
        "Offline child failed"
        if fault == "log"
        else "Offline child completion receipt differs"
    )
    with pytest.raises(RuntimeError, match=expected):
        driver.host_probe()
    assert ("container", "rm", "-f", "a" * 64) in operations
    assert not any(args[:2] == ("container", "wait") for args in operations)


@pytest.fixture(name="client_factory")
def scripted_client(monkeypatch):
    return getattr(lifecycle.client_factory, "__wrapped__")(monkeypatch)


@pytest.mark.parametrize("failure", ["stop", "interrupt", "close", "wedged"])
async def test_controller_stop_fences_fresh_runner(
    tmp_path, monkeypatch, client_factory, failure
):
    host = HostSession.initialize(tmp_path / "host.db")
    session = str(uuid.uuid4())
    attempt = host.admit(session)
    host.bind(attempt, "a" * 64)
    monkeypatch.setattr(_runner, "_key_mismatch", lambda directory: None)
    owner = owned_runner(
        host, attempt, session, session_store=object(), cwd=str(tmp_path)
    )

    async def version():
        return "2.1.274"

    async def checkpoint(*args):
        return "checkpoint"

    monkeypatch.setattr(owner.runner, "_engine_version", version)
    monkeypatch.setattr(owner.runner, "_checkpoint", checkpoint)
    if failure == "interrupt":
        client_factory["interrupt_error"] = RuntimeError("interruption failed")
    if failure == "close":
        client_factory["close_error"] = RuntimeError("closure failed")
    if failure == "wedged":
        client_factory["close_gate"] = asyncio.Event()
    inp = SegmentInput(session_id=session, prompt="work", tools=[])
    task = asyncio.create_task(owner.run(inp, 1))
    client = await started()
    await client.submitted.wait()
    control = owner.session_control(session)
    assert control is not None
    if failure == "wedged":
        control._timeout = 0.01
    owner.stop_session(session)
    with pytest.raises((asyncio.CancelledError, SessionShutdownUnresolved)):
        await task
    row = host.snapshot(attempt)
    state = json.loads(row["observations"])
    assert state["stop_requested"] and row["stopped"]
    assert len(state["messages"]) == len(control.messages)
    if state["terminal_received"]:
        assert state["messages"][-1]["type"] == "ResultMessage"
    if failure == "interrupt":
        assert state["shutdown_unresolved"] and state["interrupt_error"]
    assert row["terminated"] == row["removed"] == 0
    with pytest.raises(AdmissionRefused):
        owned_runner(HostSession(host.path), attempt, session, session_store=object())
    with pytest.raises(AdmissionRefused):
        await owner.run(inp, 2)
    assert len(Client.instances) == 1
    if failure == "wedged":
        assert client.close_gate is not None
        client.close_gate.set()
        await asyncio.sleep(0)
        with pytest.raises(AdmissionRefused):
            HostSession(host.path).admit(session)
    host.teardown(attempt, Container(host, attempt))
    replacement = HostSession(host.path).admit(session)
    host.bind(replacement, "b" * 64)
    fresh = owned_runner(
        host, replacement, session, session_store=object(), cwd=str(tmp_path)
    )
    assert fresh.runner is not owner.runner
    client_factory.clear()
    monkeypatch.setattr(fresh.runner, "_engine_version", version)
    monkeypatch.setattr(fresh.runner, "_checkpoint", checkpoint)
    replacement_task = asyncio.create_task(fresh.run(inp, 1))
    for _ in range(100):
        if len(Client.instances) == 2:
            break
        await asyncio.sleep(0)
    assert len(Client.instances) == 2
    Client.instances[1].release.set()
    output = await replacement_task
    assert output.result == "done"
