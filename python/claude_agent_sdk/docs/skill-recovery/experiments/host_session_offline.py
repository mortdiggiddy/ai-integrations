"""Measure the bounded host slice using source tests and a harmless container child."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
from contextlib import nullcontext
from pathlib import Path

from host_session import AdmissionRefused, Docker, HostSession, owned_runner

IMAGE = "sha256:cf99136b343499bf8762afe546e24bf728c8db00ceee3931b6dc629275498afa"
CLI_HASH = "15e2d05148f801b5774032faad87e624ecd172e9903288bda448b892eb58fa07"


async def child_exchange(host, attempt, session):
    """Bind a scripted public client lifecycle to the actual container grant."""
    from test_lifecycle import Client

    from temporalio.claude_agent_sdk import SegmentInput, _runner, _session_control

    _session_control.ClaudeSDKClient = Client
    _runner._key_mismatch = lambda directory: None
    Client.instances = []
    owner = owned_runner(host, attempt, session, session_store=object(), cwd="/tmp")

    async def version():
        return "2.1.274"

    owner.runner._engine_version = version
    task = asyncio.create_task(
        owner.run(SegmentInput(session_id=session, prompt="scripted", tools=[]), 1)
    )
    while not Client.instances:
        await asyncio.sleep(0)
    await Client.instances[0].submitted.wait()
    owner.stop_session(session)
    try:
        await task
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError("Stopped source runner published a result")
    try:
        owned_runner(HostSession(host.path), attempt, session, session_store=object())
    except AdmissionRefused:
        pass
    else:
        raise AssertionError("Fresh runner bypassed the container grant")
    print(
        json.dumps({"kind": "sdk_observations", "row": host.snapshot(attempt)}),
        flush=True,
    )


def child(args):
    """Run with installed dependencies only, then leave a detached harmless child."""
    if os.environ.get("UV_NO_SYNC") != "1" or os.environ.get("UV_NO_EDITABLE") != "1":
        raise RuntimeError("Dependency synchronization must be disabled")
    assert importlib.metadata.version("claude-agent-sdk") == "0.2.162"
    assert hashlib.sha256(Path("/opt/claude").read_bytes()).hexdigest() == CLI_HASH
    import pytest

    import temporalio

    temporalio.__path__.insert(0, "/source/temporalio")
    sys.path.insert(0, "/checks")
    checks = (
        [
            "/checks/test_preventive_backstop.py",
            "/checks/test_tool_policy.py",
            "/checks/test_pending_recovery.py",
            "/checks/test_lifecycle.py",
            "/checks/test_host_admission.py",
            "/checks/test_shutdown_probe.py",
            "/checks/test_experiment_admission.py",
        ]
        if args.backstop_case
        else [
            "/checks/test_host_admission.py",
            "/checks/test_lifecycle.py",
            "/checks/test_shutdown_probe.py",
            "/checks/test_experiment_admission.py",
        ]
    )
    if args.backstop_case:
        sys.path.insert(0, "/test-root")
        os.environ["BACKSTOP_CASE"] = args.backstop_case
        os.environ["BACKSTOP_ATTEMPT"] = args.attempt
        os.environ["BACKSTOP_SESSION"] = args.session
    code = pytest.main(
        [
            *checks,
            "--confcutdir=/checks",
            "-q",
            "-p",
            "no:cacheprovider",
            "-o",
            "asyncio_mode=auto",
        ]
    )
    if code:
        return code
    if not args.backstop_case:
        asyncio.run(
            child_exchange(
                HostSession(Path("/state/host.db")), args.attempt, args.session
            )
        )
    process = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(300)"],
        start_new_session=True,
    )
    Path("/state/ready.json").write_text(
        json.dumps(
            {
                "attempt": args.attempt,
                "session": args.session,
                "pytest_exit_code": code,
                "child_pid": process.pid,
            }
        )
    )
    print(
        json.dumps(
            {
                "kind": "ready",
                "child_pid": process.pid,
                "child_sid": os.getsid(process.pid),
            }
        ),
        flush=True,
    )
    # Keep the container namespace alive until the host proves forced teardown.
    process.wait()
    return 0


def host_probe(server=None, output=None, backstop_case=None):
    """Create only the fixed offline probe; never expose a model execution command."""
    plugin = Path(__file__).resolve().parents[3]
    docker = Docker()
    assert docker.command("image", "inspect", IMAGE, "--format", "{{.Id}}") == IMAGE
    if output is not None:
        Path(output).mkdir(parents=True, exist_ok=False)
    with (
        tempfile.TemporaryDirectory(prefix="sdk-host-slice-")
        if output is None
        else nullcontext(output)
    ) as scratch:
        root = Path(scratch)
        root.chmod(0o777)
        host = HostSession.initialize(root / "host.db")
        host.path.chmod(0o666)
        session = str(uuid.uuid4())
        attempt = host.admit(session)
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
            "-e",
            "UV_NO_SYNC=1",
            "-e",
            "UV_NO_EDITABLE=1",
            "-e",
            "PYTHONDONTWRITEBYTECODE=1",
            "-e",
            "PYTHONPATH=/opt/packages:/fixture:/checks",
            "-e",
            "HOME=/tmp/home",
            "-e",
            "CLAUDE_CONFIG_DIR=/tmp/config",
            "-v",
            str(root) + ":/state:rw",
            "-v",
            str(plugin / "src") + ":/source:ro",
        ]
        for source, destination in (
            (
                Path(__file__).with_name("subscription_sdk_control.py"),
                "/fixture/subscription_sdk_control.py",
            ),
            (
                Path(__file__).with_name("subscription_sdk_run.py"),
                "/fixture/subscription_sdk_run.py",
            ),
            (
                plugin / "tests/session_control/test_experiment_admission.py",
                "/checks/test_experiment_admission.py",
            ),
            (
                Path(__file__).with_name("write_recovery.py"),
                "/fixture/write_recovery.py",
            ),
            (
                plugin / "tests/session_control/test_lifecycle.py",
                "/checks/test_lifecycle.py",
            ),
            (
                plugin / "tests/session_control/test_host_admission.py",
                "/checks/test_host_admission.py",
            ),
            (
                plugin / "tests/session_control/test_shutdown_probe.py",
                "/checks/test_shutdown_probe.py",
            ),
            (
                plugin / "tests/session_control/test_preventive_backstop.py",
                "/checks/test_preventive_backstop.py",
            ),
            (
                plugin / "tests/session_control/no_decision_hook.py",
                "/checks/no_decision_hook.py",
            ),
            (plugin / "tests/test_tool_policy.py", "/checks/test_tool_policy.py"),
            (
                plugin / "tests/test_pending_recovery.py",
                "/checks/test_pending_recovery.py",
            ),
            (plugin / "tests", "/test-root/tests"),
            (
                Path(__file__).with_name("sdk_shutdown_probe.py"),
                "/fixture/sdk_shutdown_probe.py",
            ),
            (Path(__file__).with_name("host_session.py"), "/fixture/host_session.py"),
            (Path(__file__), "/fixture/host_session_offline.py"),
        ):
            argv.extend(["-v", str(source) + ":" + destination + ":ro"])
        argv.extend(
            [
                "-v",
                str(Path(__file__).with_name("write_recovery_workflow.py"))
                + ":/fixture/write_recovery_workflow.py:ro",
            ]
        )
        if server is not None:
            argv.extend(["-v", str(Path(server).resolve()) + ":/opt/temporal:ro"])
        argv.extend(
            [
                "--entrypoint",
                "/opt/python/bin/python3.13",
                IMAGE,
                "/fixture/host_session_offline.py",
                "--child",
                "--attempt",
                attempt,
                "--session",
                session,
            ]
        )
        if backstop_case is not None:
            argv.extend(["--backstop-case", backstop_case])
        resource = docker.command(*argv)
        host.bind(attempt, resource)
        removed = False
        try:
            docker.command("container", "start", resource)
            deadline = time.monotonic() + (60 if backstop_case else 45)
            while True:
                logs = docker.command("container", "logs", resource)
                ready_path = root / "ready.json"
                if ready_path.is_file():
                    ready = json.loads(ready_path.read_text())
                    if (
                        ready.get("attempt") != attempt
                        or ready.get("session") != session
                        or type(ready.get("pytest_exit_code")) is not int
                        or ready["pytest_exit_code"] != 0
                        or type(ready.get("child_pid")) is not int
                        or ready["child_pid"] <= 0
                    ):
                        raise RuntimeError("Offline child completion receipt differs")
                    break
                if (
                    time.monotonic() >= deadline
                    or not docker.inspect(resource)["State"]["Running"]
                ):
                    print(logs, flush=True)
                    raise RuntimeError(
                        "Offline child failed or never reached the lifecycle barrier"
                    )
                time.sleep(0.1)
            print(logs, flush=True)
            if output is not None:
                (root / "container-output.txt").write_text(logs)
            before = host.snapshot(attempt)
            try:
                HostSession(host.path).admit(session)
            except AdmissionRefused:
                blocked = True
            else:
                raise AssertionError("Replacement admitted before teardown")
            after = host.teardown(attempt, docker)
            if output is not None:
                (root / "host-receipt.json").write_text(json.dumps(after, indent=2))
            removed = True
            replacement = HostSession(host.path).admit(session)
            stale_refused = False
            try:
                host.teardown(attempt, docker)
            except AdmissionRefused:
                stale_refused = True
            assert stale_refused and replacement != attempt
            report = {
                "evidence_kind": "actual_engine_local_provider_backstop"
                if backstop_case
                else "scripted_sdk_and_harmless_container_child",
                "image": IMAGE,
                "cli_sha256": CLI_HASH,
                "before_teardown": before,
                "after_teardown": after,
                "replacement_before_teardown_refused": blocked,
                "replacement_after_teardown_admitted": True,
                "stale_teardown_refused": stale_refused,
                "network": "none",
                "credentials_or_login_mounts": False,
                "model_calls": 0,
                "engine_launches": 1 if backstop_case else 0,
                "provider_spend_usd": 0,
                "installed_plugin_provenance_proved": False,
                "live_engine_shutdown_or_recovery_proved": False,
                "source_sha256": {
                    str(path.relative_to(plugin)): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in [
                        Path(__file__),
                        Path(__file__).with_name("host_session.py"),
                        plugin / "tests/session_control/test_preventive_backstop.py"
                        if backstop_case
                        else plugin / "tests/session_control/test_host_admission.py",
                        plugin / "tests/session_control/no_decision_hook.py",
                        plugin / "tests/helpers/fake_messages_api.py",
                        plugin / "tests/test_tool_policy.py",
                        plugin / "tests/test_pending_recovery.py",
                        plugin / "tests/session_control/test_lifecycle.py",
                        plugin / "tests/session_control/test_host_admission.py",
                        plugin / "src/temporalio/claude_agent_sdk/_defer_hook.py",
                        plugin / "src/temporalio/claude_agent_sdk/_runner.py",
                        plugin / "src/temporalio/claude_agent_sdk/_session_control.py",
                    ]
                },
            }
            if output is not None:
                (root / "report.json").write_text(json.dumps(report, indent=2))
            print(
                json.dumps(
                    {
                        "evidence_kind": report["evidence_kind"],
                        "cleanup_verified": True,
                        "engine_launches": report["engine_launches"],
                    }
                ),
                flush=True,
            )
        finally:
            if not removed:
                try:
                    logs = docker.command("container", "logs", resource)
                    if output is not None:
                        (root / "container-output.txt").write_text(logs)
                finally:
                    receipt = host.teardown(attempt, docker)
                    if output is not None:
                        (root / "failure-cleanup.json").write_text(
                            json.dumps(receipt, indent=2)
                        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--attempt")
    parser.add_argument("--session")
    parser.add_argument("--server")
    parser.add_argument("--output")
    parser.add_argument(
        "--backstop-case",
        choices=[
            "write",
            "removed",
            "system-prompt",
            "extra-args",
            "combined-options",
            "bash-read",
            "bash-deny",
            "bash-defer",
            "skill-grant",
            "skill-removed",
            "skill-batch",
            "write-ask",
            "bash-ask",
            "bash-ask-defer",
            "skill-ask-batch",
            "skill-ask-removed-batch",
            "bash-ask-removed",
            "write-ask-defer",
            "edit-ask",
            "edit-removed",
            "ask-system-prompt",
            "ask-extra-args",
            "ask-combined-options",
        ],
    )
    arguments = parser.parse_args()
    if arguments.child:
        raise SystemExit(child(arguments))
    host_probe(arguments.server, arguments.output, arguments.backstop_case)
