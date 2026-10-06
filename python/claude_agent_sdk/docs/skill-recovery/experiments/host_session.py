"""Fence the Phase 1 harness on one retained local store and Docker daemon.

Only cooperating harness processes may write this store. It is not an effect
workspace, distributed lease, production supervisor or model execution command.
"""

from __future__ import annotations

import json
import math
import sqlite3
import subprocess
import uuid
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any


class AdmissionRefused(RuntimeError):
    """Ownership or teardown evidence is insufficient for execution."""


class ExperimentAdmission:
    """Validate one monitored scenario and retain consumed segment admissions.

    This journal is local experiment accounting, not a provider request gate.
    Missing accounting never authorizes another segment.
    """

    REQUIRED = {
        "scenario",
        "authorization",
        "authentication",
        "model",
        "image",
        "sdk",
        "cli_sha256",
        "allowance_usd",
        "input_limit",
        "output_limit",
        "segments",
        "max_turns",
        "retries",
        "segment_seconds",
        "shutdown_seconds",
        "host_seconds",
        "residual_risk_accepted",
    }

    @classmethod
    def validate(cls, config, expected):
        if (
            set(config) != cls.REQUIRED
            or config != expected
            or any(type(config[key]) is not type(expected[key]) for key in config)
        ):
            raise AdmissionRefused(
                "Exact scenario approval and all pinned controls required"
            )
        for field in (
            "allowance_usd",
            "input_limit",
            "output_limit",
            "segments",
            "max_turns",
            "segment_seconds",
            "shutdown_seconds",
            "host_seconds",
        ):
            value = config[field]
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value <= 0
            ):
                raise AdmissionRefused("Positive finite experiment limits required")
        if (
            type(config["retries"]) is not int
            or config["retries"] != 0
            or config["residual_risk_accepted"] is not True
        ):
            raise AdmissionRefused(
                "No retries and explicit residual risk acceptance required"
            )

    @classmethod
    def initialize(cls, path, config, expected):
        cls.validate(config, expected)
        with path.open("x") as file:
            json.dump({"config": config, "segments": [], "failure": None}, file)
            file.flush()
            import os

            os.fsync(file.fileno())
        return cls(path, expected)

    def __init__(self, path, expected):
        self.path, self.expected = Path(path), expected

    def read(self):
        state = json.loads(self.path.read_text())
        self.validate(state["config"], self.expected)
        return state

    def write(self, state):
        # The host supervisor is the sole writer, after each container is fenced.
        with self.path.open("w") as file:
            json.dump(state, file, indent=2, sort_keys=True)
            file.flush()
            import os

            os.fsync(file.fileno())

    def begin(self):
        state = self.read()
        if (
            state["failure"]
            or any(row["accounting"] is None for row in state["segments"])
            or len(state["segments"]) >= self.expected["segments"]
        ):
            raise AdmissionRefused("Consumed or unresolved scenario admission")
        state["segments"].append({"accounting": None})
        self.write(state)

    def fail(self, reason):
        state = self.read()
        state["failure"] = reason
        self.write(state)

    def reconcile(self, accounting):
        state = self.read()
        valid = isinstance(accounting, dict)
        for field in ("input", "output", "turns"):
            value = accounting.get(field) if valid else None
            valid = valid and type(value) is int and value >= 0
        cost = accounting.get("cost_usd") if valid else None
        valid = (
            valid
            and not isinstance(cost, bool)
            and isinstance(cost, (int, float))
            and math.isfinite(cost)
            and cost >= 0
        )
        if not valid or accounting.get("model") != self.expected["model"]:
            self.fail("Unresolved accounting or unexpected model")
            raise AdmissionRefused("Unresolved accounting or unexpected model")
        if (
            not state["segments"]
            or state["segments"][-1]["accounting"] is not None
            or state["failure"]
        ):
            raise AdmissionRefused("No current unresolved segment")
        state["segments"][-1]["accounting"] = accounting
        totals = {
            field: sum(row["accounting"][field] for row in state["segments"])
            for field in ("cost_usd", "input", "output", "turns")
        }
        if (
            any(
                totals[field] >= self.expected[cap]
                for field, cap in (
                    ("cost_usd", "allowance_usd"),
                    ("input", "input_limit"),
                    ("output", "output_limit"),
                )
            )
            or accounting["turns"] > self.expected["max_turns"]
        ):
            state["failure"] = "Observed allowance or request planning bound reached"
        self.write(state)
        if state["failure"]:
            raise AdmissionRefused(state["failure"])
        return totals


def contend(path, event, queue):
    """Attempt admission in an independent offline test process."""
    event.wait(5)
    try:
        result = HostSession(Path(path)).admit("session")
    except AdmissionRefused:
        result = "refused"
    queue.put(result)


class HostSession:
    """Retain one logical session's current container and runner ownership."""

    def __init__(self, path: Path) -> None:
        self.path = path.resolve()

    @classmethod
    def initialize(cls, path: Path) -> HostSession:
        """Create a new disposable store explicitly; never recreate on reopen."""
        with path.open("xb"):
            pass
        host = cls(path)
        with host.transaction() as db:
            db.execute(
                "CREATE TABLE execution (singleton INTEGER PRIMARY KEY CHECK(singleton=1), "
                "session TEXT NOT NULL, attempt TEXT NOT NULL, name TEXT NOT NULL, "
                "resource TEXT, runner TEXT, stopped INTEGER NOT NULL DEFAULT 0, "
                "observations TEXT, terminated INTEGER NOT NULL DEFAULT 0, "
                "removed INTEGER NOT NULL DEFAULT 0, host_receipt TEXT)"
            )
        return host

    @contextmanager
    def transaction(self):
        """Serialize local changes and refuse missing or unreadable storage."""
        try:
            db = sqlite3.connect(self.path.as_uri() + "?mode=rw", uri=True, timeout=1)
            try:
                db.row_factory = sqlite3.Row
                db.execute("PRAGMA synchronous=FULL")
                db.execute("BEGIN IMMEDIATE")
                yield db
                db.commit()
            finally:
                db.close()
        except sqlite3.Error as exc:
            raise AdmissionRefused(
                "Retained host ownership store is unavailable"
            ) from exc

    @staticmethod
    def current(db, attempt: str):
        row = db.execute("SELECT * FROM execution WHERE singleton=1").fetchone()
        if row is None or row["attempt"] != attempt:
            raise AdmissionRefused("Stale or absent host ownership")
        return row

    def admit(self, session: str) -> str:
        """Reserve before resource creation; unresolved creation also fences retry."""
        with self.transaction() as db:
            row = db.execute("SELECT * FROM execution WHERE singleton=1").fetchone()
            if row is not None and not (row["terminated"] and row["removed"]):
                raise AdmissionRefused(
                    "Prior host termination and teardown are unresolved"
                )
            if row is not None and row["session"] != session:
                raise AdmissionRefused("This store belongs to another logical session")
            attempt = uuid.uuid4().hex
            db.execute(
                "INSERT OR REPLACE INTO execution(singleton,session,attempt,name) VALUES(1,?,?,?)",
                (session, attempt, "sdk-host-" + attempt),
            )
            return attempt

    def snapshot(self, attempt: str) -> dict[str, Any]:
        with self.transaction() as db:
            return dict(self.current(db, attempt))

    def launch(
        self,
        attempt,
        image,
        command,
        mounts,
        *,
        network="none",
        environment=(),
        docker=None,
    ):
        """Create, bind and start a restricted container under the retained grant."""
        docker = docker or Docker()
        row = self.snapshot(attempt)
        if row["resource"] or row["stopped"]:
            raise AdmissionRefused("Container grant is already consumed")
        if docker.command("image", "inspect", image, "--format", "{{.Id}}") != image:
            raise AdmissionRefused("Immutable existing image required")
        argv = [
            "create",
            "--pull",
            "never",
            "--name",
            row["name"],
            "--label",
            "durability.attempt=" + attempt,
            "--network",
            network,
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            "128",
            "--memory",
            "2g",
            "--cpus",
            "2",
            "--tmpfs",
            "/tmp:rw,nosuid,nodev,size=512m",
        ]
        for value in environment:
            argv.extend(["-e", value])
        for value in mounts:
            argv.extend(["-v", value])
        argv.extend(["--entrypoint", "/opt/python/bin/python3.13", image, *command])
        resource = docker.command(*argv)
        self.bind(attempt, resource)
        docker.command("container", "start", resource)
        return resource

    def bind(self, attempt: str, resource: str) -> None:
        """Bind the created immutable container ID once, before starting it."""
        if len(resource) != 64 or any(c not in "0123456789abcdef" for c in resource):
            raise AdmissionRefused("An immutable Docker container ID is required")
        with self.transaction() as db:
            row = self.current(db, attempt)
            if row["resource"] is not None or row["terminated"] or row["removed"]:
                raise AdmissionRefused("Resource already bound or execution closed")
            db.execute("UPDATE execution SET resource=? WHERE singleton=1", (resource,))

    def claim_runner(self, attempt: str, session: str) -> str:
        """Permit exactly one runner instance in this owned execution."""
        with self.transaction() as db:
            row = self.current(db, attempt)
            if (
                row["session"] != session
                or not row["resource"]
                or row["runner"]
                or row["stopped"]
                or row["terminated"]
                or row["removed"]
            ):
                raise AdmissionRefused("Fresh runner has no current host grant")
            runner = uuid.uuid4().hex
            db.execute("UPDATE execution SET runner=? WHERE singleton=1", (runner,))
            return runner

    def check_runner(self, attempt: str, session: str, runner: str) -> None:
        with self.transaction() as db:
            row = self.current(db, attempt)
            if (
                row["session"] != session
                or row["runner"] != runner
                or row["stopped"]
                or row["terminated"]
                or row["removed"]
            ):
                raise AdmissionRefused("Runner ownership is stopped, stale or lost")

    def observe(self, attempt: str, runner: str, state: dict[str, Any]) -> None:
        """Retain SDK observations without turning them into host teardown proof."""
        with self.transaction() as db:
            row = self.current(db, attempt)
            if row["runner"] != runner or row["terminated"] or row["removed"]:
                raise AdmissionRefused("Stale SDK observation")
            stopped = (
                row["stopped"]
                or state.get("stop_requested")
                or state.get("shutdown_unresolved")
            )
            previous = json.loads(row["observations"] or "{}")
            state = dict(state)
            for field in (
                "stop_requested",
                "interrupt_acknowledged",
                "terminal_received",
                "sdk_closed",
                "shutdown_unresolved",
                "prompt_submission_started",
            ):
                if field in previous or field in state:
                    state[field] = bool(previous.get(field) or state.get(field))
            db.execute(
                "UPDATE execution SET observations=?,stopped=? WHERE singleton=1",
                (json.dumps(state, sort_keys=True), int(bool(stopped))),
            )

    def stop(self, attempt: str) -> None:
        """Revoke admission before cooperative interruption or host teardown."""
        with self.transaction() as db:
            self.current(db, attempt)
            db.execute("UPDATE execution SET stopped=1 WHERE singleton=1")

    def teardown(self, attempt: str, docker=None) -> dict[str, Any]:
        """Verify stopped container state, removal and absence on the owned daemon.

        A Docker error, lost identity or uncertain removal leaves admission fenced.
        The daemon must remain the same local daemon for the entire session.
        """
        docker = docker or Docker()
        self.stop(attempt)
        with self.transaction() as db:
            row = self.current(db, attempt)
            resource = row["resource"]
            if not resource or row["removed"]:
                raise AdmissionRefused("No unresolved bound container to tear down")
            info = docker.inspect(resource)
            if (
                info["Id"] != resource
                or info["Config"]["Labels"].get("durability.attempt") != attempt
                or info["Name"] != "/" + row["name"]
            ):
                raise AdmissionRefused("Container ownership identity differs")
            if info["State"]["Running"]:
                docker.kill(resource)
            exit_code = docker.wait(resource)
            info = docker.inspect(resource)
            if (
                info["Id"] != resource
                or info["State"]["Running"]
                or info["State"]["Pid"] != 0
            ):
                raise AdmissionRefused("Host process termination is unverified")
            if type(exit_code) is not int:
                raise AdmissionRefused("Container exit receipt is unverified")
            receipt = {
                "resource": resource,
                "wait_exit_code": exit_code,
                "stopped_state": {
                    key: info["State"][key] for key in ("Running", "Pid")
                },
                "removal_verified": False,
            }
            db.execute(
                "UPDATE execution SET terminated=1,host_receipt=? WHERE singleton=1",
                (json.dumps(receipt, sort_keys=True),),
            )
            # Persist termination independently of a later failed removal.
        with self.transaction() as db:
            row = self.current(db, attempt)
            docker.remove(resource)
            if not docker.absent(resource):
                raise AdmissionRefused("Containment teardown is unverified")
            receipt = json.loads(row["host_receipt"])
            receipt["removal_verified"] = True
            db.execute(
                "UPDATE execution SET removed=1,host_receipt=? WHERE singleton=1",
                (json.dumps(receipt, sort_keys=True),),
            )
        return self.snapshot(attempt)


class Docker:
    """Use bounded Docker CLI operations on an immutable local container ID."""

    def command(self, *args: str) -> str:
        result = subprocess.run(
            ["docker", *args],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode:
            raise AdmissionRefused("Docker operation failed: " + args[0])
        if args[:2] == ("container", "logs"):
            return result.stdout.strip() + "\n" + result.stderr.strip()
        return result.stdout.strip()

    def inspect(self, resource: str) -> dict[str, Any]:
        return json.loads(self.command("container", "inspect", resource))[0]

    def kill(self, resource: str) -> None:
        self.command("container", "kill", resource)

    def wait(self, resource: str) -> int:
        return int(self.command("container", "wait", resource))

    def remove(self, resource: str) -> None:
        self.command("container", "rm", resource)

    def absent(self, resource: str) -> bool:
        # Successful daemon enumeration distinguishes absence from inspect errors.
        return (
            resource
            not in self.command("container", "ls", "-aq", "--no-trunc").splitlines()
        )


def owned_runner(
    host: HostSession, attempt: str, session: str, *, runner_factory=None, **kwargs: Any
):
    """Construct the Phase 1 runner with one retained host grant.

    This harness adapter is not installed plugin policy. Raw plugin construction
    remains outside this bounded host contract. No paid execution route is added.
    """
    from temporalio.claude_agent_sdk import ClaudeAgentSdkRunner

    runner_id = host.claim_runner(attempt, session)

    class OwnedRunner:
        def __init__(self):
            self.runner = (runner_factory or ClaudeAgentSdkRunner)(**kwargs)

        def session_control(self, session_id: str):
            return self.runner.session_control(session_id)

        def stop_session(self, session_id: str) -> None:
            host.check_runner(attempt, session_id, runner_id)
            host.stop(attempt)
            self.runner.stop_session(session_id)

        async def run(self, inp, segment_attempt):
            host.check_runner(attempt, inp.session_id, runner_id)
            try:
                result = await self.runner.run(inp, segment_attempt)
                host.check_runner(attempt, inp.session_id, runner_id)
                return result
            finally:
                control = self.session_control(inp.session_id)
                if control is not None:
                    state = asdict(control.state)
                    state["messages"] = [
                        {"type": type(message).__name__, "message": asdict(message)}
                        for message in control.messages
                    ]
                    host.observe(attempt, runner_id, state)

    return OwnedRunner()
