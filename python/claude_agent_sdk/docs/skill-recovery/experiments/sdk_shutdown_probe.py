"""Observe public SDK control without a prompt inside the retained host gate."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import inspect
import json
import os
import time
import uuid
from pathlib import Path

from host_session import AdmissionRefused, Docker, HostSession
from host_session_offline import CLI_HASH, IMAGE


def save(path, value):
    """Retain diagnostics as a documented probe output."""
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def inventory(root=Path("/proc"), *, timeout=2):
    """Collect PID/start identities; any collection failure leaves uncertainty.

    ENOENT during collection records a race, not a termination receipt. Reads
    use only stat and comm on the local proc filesystem, never environments.
    """
    observation = {
        "version": 1,
        "enumeration_completed": False,
        "enumerated_pids": [],
        "processes": [],
        "errors": [],
        "complete": False,
    }
    deadline = time.monotonic() + timeout
    try:
        paths = []
        for path in root.iterdir():
            if time.monotonic() >= deadline:
                raise TimeoutError("Process enumeration deadline expired")
            if path.name.isascii() and path.name.isdecimal():
                observation["enumerated_pids"].append(int(path.name))
                paths.append(path)
        observation["enumeration_completed"] = True
    except (OSError, ValueError) as exc:
        observation["errors"].append(
            {"operation": "enumerate", "error": type(exc).__name__}
        )
        return observation
    for path in paths:
        operation = "stat"
        try:
            if time.monotonic() >= deadline:
                raise TimeoutError("Process observation deadline expired")
            stat = (path / "stat").read_text()
            fields = stat[stat.rindex(")") + 2 :].split()
            if int(stat.split("(", 1)[0]) != int(path.name):
                raise ValueError("Process PID differs")
            row = {"pid": int(path.name), "start": fields[19], "state": fields[0]}
            operation = "comm"
            row["comm"] = (path / "comm").read_text().strip()
            if not valid_inventory(
                {
                    "version": 1,
                    "enumeration_completed": True,
                    "complete": True,
                    "errors": [],
                    "enumerated_pids": [int(path.name)],
                    "processes": [row],
                }
            ):
                raise ValueError("Malformed process data")
            operation = "stat_identity"
            repeated = (path / "stat").read_text()
            if repeated[repeated.rindex(")") + 2 :].split()[19] != row["start"]:
                raise ValueError("Process identity changed during collection")
            if time.monotonic() >= deadline:
                raise TimeoutError("Process observation deadline expired")
            observation["processes"].append(row)
        except (OSError, ValueError, IndexError) as exc:
            observation["errors"].append(
                {
                    "pid": int(path.name),
                    "operation": operation,
                    "error": type(exc).__name__,
                    "vanished_during_collection": isinstance(exc, FileNotFoundError),
                }
            )
    observation["enumerated_pids"].sort()
    observation["processes"].sort(key=lambda row: row["pid"])
    observation["complete"] = not observation["errors"]
    return observation


def valid_inventory(value):
    """Accept only complete snapshots with one valid identity per enumerated PID."""
    if not isinstance(value, dict):
        return False
    if (
        type(value.get("version")) is not int
        or value["version"] != 1
        or value.get("enumeration_completed") is not True
        or value.get("complete") is not True
        or value.get("errors") != []
        or not isinstance(value.get("enumerated_pids"), list)
        or not isinstance(value.get("processes"), list)
    ):
        return False
    pids = value["enumerated_pids"]
    if any(type(pid) is not int or pid <= 0 for pid in pids):
        return False
    if len(set(pids)) != len(pids):
        return False
    observed = []
    for row in value["processes"]:
        if not isinstance(row, dict):
            return False
        start = row.get("start")
        if (
            type(row.get("pid")) is not int
            or row["pid"] <= 0
            or not isinstance(start, str)
            or not start.isascii()
            or not start.isdecimal()
            or int(start) <= 0
            or str(int(start)) != start
            or row.get("state")
            not in ("R", "S", "D", "Z", "T", "t", "X", "x", "K", "W", "P", "I")
            or not isinstance(row.get("comm"), str)
            or not row["comm"].strip()
        ):
            return False
        observed.append(row["pid"])
    return len(set(observed)) == len(observed) and set(observed) == set(pids)


def classify_observations(state):
    """Separate SDK completion from sampled absence; neither grants admission."""
    report = {
        "sdk_control_completed": False,
        "sdk_process_absence_before_host_teardown": False,
        "sdk_processes_observed": [],
        "process_observations_valid": False,
        "process_observation_unresolved": [],
    }
    if not isinstance(state, dict):
        report["process_observation_unresolved"].append(
            "SDK observations are not an object"
        )
        return report
    report["sdk_control_completed"] = bool(
        all(
            state.get(field) is True
            for field in (
                "connected",
                "stop_requested",
                "interrupt_acknowledged",
                "sdk_closed",
            )
        )
        and state.get("shutdown_unresolved") is False
        and state.get("prompt_submission_started") is False
        and state.get("stage") == "finished"
        and not any(
            field in state
            for field in (
                "timeout_stage",
                "connect_error",
                "interrupt_error",
                "close_error",
            )
        )
    )
    for name in ("before_connect", "after_connect", "after_disconnect"):
        if not valid_inventory(state.get(name)):
            report["process_observation_unresolved"].append(
                name + " inventory missing, invalid or incomplete"
            )
    if report["process_observation_unresolved"]:
        return report
    report["process_observations_valid"] = True
    before = {
        (row["pid"], row["start"]) for row in state["before_connect"]["processes"]
    }
    relevant = [
        row
        for row in state["after_connect"]["processes"]
        if (row["pid"], row["start"]) not in before or "claude" in row["comm"].lower()
    ]
    report["sdk_processes_observed"] = relevant
    after = {
        (row["pid"], row["start"]) for row in state["after_disconnect"]["processes"]
    }
    surviving = [row for row in relevant if (row["pid"], row["start"]) in after]
    if not relevant:
        report["process_observation_unresolved"].append(
            "No relevant process identity observed after connection"
        )
    if surviving:
        report["process_observation_unresolved"].append(
            "Relevant process identities survive disconnect"
        )
    report["sdk_process_absence_before_host_teardown"] = bool(
        state.get("sdk_closed") is True and relevant and not surviving
    )
    return report


async def lifecycle(host, attempt, session, runner, state):
    """Keep connect and disconnect in the same task as required by SDK scopes."""
    from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

    options = ClaudeAgentOptions(
        cli_path="/opt/claude",
        cwd="/tmp/work",
        tools=[],
        allowed_tools=[],
        setting_sources=[],
        mcp_servers={},
        plugins=[],
        permission_mode="default",
        env={"CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"},
        stderr=lambda line: print(
            json.dumps({"kind": "sdk_stderr", "line": line}), flush=True
        ),
    )
    client = ClaudeSDKClient(options=options)
    try:
        host.check_runner(attempt, session, runner)
        state["stage"] = "connect"
        await client.connect()
        state["connected"] = True
        state["after_connect"] = inventory()
        host.stop(attempt)
        state["stop_requested"] = True
        state["stage"] = "interrupt"
        try:
            await client.interrupt()
            state["interrupt_acknowledged"] = True
        except Exception as exc:
            state["interrupt_error"] = type(exc).__name__ + ": " + str(exc)
            state["shutdown_unresolved"] = True
    except Exception as exc:
        state["connect_error"] = type(exc).__name__ + ": " + str(exc)
        state["shutdown_unresolved"] = True
    finally:
        state["stage"] = "disconnect"
        try:
            await client.disconnect()
            state["sdk_closed"] = True
        except BaseException as exc:
            state["close_error"] = type(exc).__name__ + ": " + str(exc)
            state["shutdown_unresolved"] = True
        state["after_disconnect"] = inventory()
        state["stage"] = "finished"


async def child_control(args):
    host = HostSession(Path("/state/host.db"))
    runner = host.claim_runner(args.attempt, args.session)
    state = {
        "stage": "created",
        "connected": False,
        "sdk_closed": False,
        "stop_requested": False,
        "interrupt_acknowledged": False,
        "shutdown_unresolved": False,
        "prompt_submission_started": False,
        "before_connect": inventory(),
    }
    owner = asyncio.create_task(
        lifecycle(host, args.attempt, args.session, runner, state)
    )
    stage, deadline = None, time.monotonic() + 20
    while not owner.done():
        if state["stage"] != stage:
            stage = state["stage"]
            deadline = time.monotonic() + 20
        if time.monotonic() >= deadline:
            state["timeout_stage"] = stage
            state["shutdown_unresolved"] = True
            host.stop(args.attempt)
            break
        await asyncio.sleep(0.05)
    if owner.done():
        owner.result()
    host.observe(args.attempt, runner, state)
    save(Path("/state/sdk-observations.json"), state)
    print(json.dumps({"kind": "ready", "state": state}), flush=True)
    # A wedged SDK owner is retained until the host contains the whole namespace.
    await asyncio.Event().wait()


def child(args):
    assert os.environ["UV_NO_SYNC"] == os.environ["UV_NO_EDITABLE"] == "1"
    assert importlib.metadata.version("claude-agent-sdk") == "0.2.162"
    assert hashlib.sha256(Path("/opt/claude").read_bytes()).hexdigest() == CLI_HASH
    for directory in ("/tmp/home", "/tmp/config", "/tmp/work"):
        Path(directory).mkdir()
    import claude_agent_sdk.client as client
    from claude_agent_sdk._internal.transport.subprocess_cli import (
        SubprocessCLITransport,
    )

    sources = {
        "client.connect": inspect.getsource(client.ClaudeSDKClient.connect),
        "client.interrupt": inspect.getsource(client.ClaudeSDKClient.interrupt),
        "client.disconnect": inspect.getsource(client.ClaudeSDKClient.disconnect),
        "transport.close": inspect.getsource(SubprocessCLITransport.close),
    }
    save(Path("/state/installed-lifecycle-source.json"), sources)
    print(json.dumps({"kind": "installed_source", "sdk": "0.2.162"}), flush=True)
    if args.inspect_only:
        return
    asyncio.run(child_control(args))


def refused(operation):
    try:
        operation()
    except AdmissionRefused as exc:
        return str(exc)
    raise AssertionError("Replacement was admitted before authoritative cleanup")


def host_probe(args):
    """Use the existing supervisor and fixed offline image; expose no query API."""
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    state_dir = output / "state"
    state_dir.mkdir(mode=0o777)
    state_dir.chmod(0o777)
    host = HostSession.initialize(state_dir / "host.db")
    host.path.chmod(0o666)
    session = str(uuid.uuid4())
    attempt = host.admit(session)
    docker = Docker()
    report = {
        "image": IMAGE,
        "cli_sha256": CLI_HASH,
        "inspect_only": args.inspect_only,
        "network": "none",
        "prompt_calls": 0,
        "model_calls": 0,
        "graceful_engine_shutdown_proved": False,
        "recovery_proved": False,
    }
    resource = None
    try:
        assert docker.command("image", "inspect", IMAGE, "--format", "{{.Id}}") == IMAGE
        row = host.snapshot(attempt)
        argv = [
            "create",
            "--pull",
            "never",
            "--name",
            row["name"],
            "--label",
            "durability.attempt=" + attempt,
            "--network",
            "none",
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
        for variable in (
            "UV_NO_SYNC=1",
            "UV_NO_EDITABLE=1",
            "PYTHONDONTWRITEBYTECODE=1",
            "PYTHONPATH=/opt/packages:/fixture",
            "HOME=/tmp/home",
            "CLAUDE_CONFIG_DIR=/tmp/config",
        ):
            argv.extend(["-e", variable])
        argv.extend(["-v", str(state_dir) + ":/state:rw"])
        for name in ("host_session.py", "host_session_offline.py", Path(__file__).name):
            argv.extend(
                [
                    "-v",
                    str(Path(__file__).with_name(name)) + ":/fixture/" + name + ":ro",
                ]
            )
        argv.extend(
            [
                "--entrypoint",
                "/opt/python/bin/python3.13",
                IMAGE,
                "/fixture/" + Path(__file__).name,
                "--child",
                "--attempt",
                attempt,
                "--session",
                session,
            ]
        )
        if args.inspect_only:
            argv.append("--inspect-only")
        save(
            output / "command.json",
            [
                arg.replace(str(output), "<output>").replace(
                    str(Path(__file__).parent), "<experiments>"
                )
                for arg in argv
            ],
        )
        resource = docker.command(*argv)
        host.bind(attempt, resource)
        docker.command("container", "start", resource)
        deadline = time.monotonic() + 75
        while True:
            logs = docker.command("container", "logs", resource)
            (output / "container-output.txt").write_text(logs + "\n")
            info = docker.inspect(resource)
            save(
                output / "container-inspection.json",
                json.loads(
                    json.dumps(
                        {
                            key: info[key]
                            for key in ("Id", "Name", "State", "HostConfig")
                        }
                    )
                    .replace(str(output), "<output>")
                    .replace(str(Path(__file__).parent), "<experiments>")
                ),
            )
            if (state_dir / "sdk-observations.json").is_file() or not info["State"][
                "Running"
            ]:
                break
            if time.monotonic() >= deadline:
                raise TimeoutError("Host lifecycle observation deadline expired")
            time.sleep(0.1)
        report["before_teardown"] = host.snapshot(attempt)
        report["replacement_before_cleanup"] = refused(
            lambda: HostSession(host.path).admit(session)
        )
        report["fresh_runner_before_cleanup"] = (
            refused(lambda: HostSession(host.path).claim_runner(attempt, session))
            if not args.inspect_only
            else "unexecuted"
        )
        if (
            not args.inspect_only
            and not (state_dir / "sdk-observations.json").is_file()
        ):
            raise RuntimeError(
                "SDK control did not produce observations; see retained diagnostics"
            )
        if not args.inspect_only:
            state = json.loads((state_dir / "sdk-observations.json").read_text())
            report.update(classify_observations(state))
            if not report["sdk_control_completed"]:
                raise RuntimeError(
                    "Public SDK lifecycle unresolved; retain limitation and stop this approach"
                )
            if not report["sdk_process_absence_before_host_teardown"]:
                raise RuntimeError(
                    "SDK subprocess disappearance is unverified before host teardown"
                )
    except Exception as exc:
        report["error"] = type(exc).__name__ + ": " + str(exc)
    finally:
        if resource is not None:
            try:
                report["after_teardown"] = host.teardown(attempt, docker)
                replacement = HostSession(host.path).admit(session)
                report["replacement_after_cleanup"] = replacement != attempt
                report["stale_observation"] = refused(
                    lambda: host.observe(attempt, "stale", {"sdk_closed": True})
                )
            except Exception as exc:
                report["teardown_error"] = type(exc).__name__ + ": " + str(exc)
        report["source_sha256"] = {
            name: hashlib.sha256(
                Path(__file__).with_name(name).read_bytes()
            ).hexdigest()
            for name in (
                "host_session.py",
                "host_session_offline.py",
                Path(__file__).name,
            )
        }
        save(output / "report.json", report)
    print(json.dumps(report, indent=2), flush=True)
    if "error" in report or "teardown_error" in report:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--inspect-only", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--attempt")
    parser.add_argument("--session")
    arguments = parser.parse_args()
    if arguments.child:
        child(arguments)
    elif arguments.output:
        host_probe(arguments)
    else:
        parser.error("A fresh output directory is required")
