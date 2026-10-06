"""Run the fixed offline budget experiment in the existing immutable image.

The container has only five read only fixture mounts and disposable storage.
No image build, dependency synchronization or live execution mode exists.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.metadata
import inspect
import io
import json
import os
import signal
import subprocess
import sys
import tarfile
import time
import traceback
import uuid
from pathlib import Path

IMAGE = "sha256:cf99136b343499bf8762afe546e24bf728c8db00ceee3931b6dc629275498afa"
CLI_HASH = "15e2d05148f801b5774032faad87e624ecd172e9903288bda448b892eb58fa07"
PYTHON = "/opt/python/bin/python3.13"


def record(path, value):
    path.write_text(json.dumps(value, indent=2))


def provenance(root):
    """Verify pinned runtime and hashed installed SDK files before fixture import."""
    from claude_agent_sdk import ClaudeAgentOptions
    from claude_agent_sdk._internal.transport.subprocess_cli import (
        SubprocessCLITransport,
    )

    version = importlib.metadata.version("claude-agent-sdk")
    cli_hash = hashlib.sha256(Path("/opt/claude").read_bytes()).hexdigest()
    assert version == "0.2.162" and cli_hash == CLI_HASH
    assert sys.version_info[:3] == (3, 13, 15)
    sdk = importlib.metadata.distribution("claude-agent-sdk")
    records = []
    for file in sdk.files:
        if file.hash is None:
            continue
        data = file.locate().read_bytes()
        actual = (
            base64.urlsafe_b64encode(hashlib.new(file.hash.mode, data).digest())
            .decode()
            .rstrip("=")
        )
        assert actual == file.hash.value, str(file)
        records.append({"path": str(file), "sha256": hashlib.sha256(data).hexdigest()})
    assert records
    cli = subprocess.run(
        ["/opt/claude", "--version"],
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    assert cli.stdout.strip() == "2.1.274 (Claude Code)"
    source = inspect.getsource(SubprocessCLITransport.connect)
    command_source = inspect.getsource(SubprocessCLITransport._build_command)
    (root / "sdk-transport-source.txt").write_text(
        (source + "\n" + command_source).replace(chr(0x2014), ",")
    )
    signature = str(inspect.signature(ClaudeAgentOptions))
    gate = {
        "status": "candidate-only",
        "configuration": "ANTHROPIC_BASE_URL with literal synthetic API key, SDK env passthrough",
        "source_observation": "SDK merges explicit env into CLI; provider HTTP gateway supplies admission before forwarding, not a private CLI hook",
        "confinement": "network none; only loopback fake provider accepts single-use bound gateway receipt; no account login or credential mounts",
        "subscription_route": "unproved; fake endpoint configuration is not an Enterprise admission API",
        "official_source": "https://code.claude.com/docs/en/llm-gateway-connect",
        "source_checked": "2026-10-02",
        "options_signature": signature,
        "runtime_proof": "unexecuted at entry gate",
    }
    record(root / "entry-gate.json", gate)
    record(
        root / "provenance.json",
        {
            "image": IMAGE,
            "python": sys.version,
            "sdk": version,
            "cli": cli.stdout.strip(),
            "cli_sha256": cli_hash,
            "sdk_record_hashes": records,
            "fixture_hashes": {
                file.name: hashlib.sha256(file.read_bytes()).hexdigest()
                for file in Path("/fixtures").glob("*.py")
            },
        },
    )
    return gate


def inside(root, *, request_only=False, loss_only=False, faults_only=False):
    """Execute independent arms and retain diagnostics even when an arm fails."""
    started = time.monotonic()
    os.environ.clear()
    os.environ.update(
        {
            "PATH": "/opt/python/bin:/usr/bin:/bin",
            "HOME": "/tmp/empty-home",
            "TMPDIR": "/tmp",
            "CLAUDE_CONFIG_DIR": "/tmp/empty-config",
            "UV_NO_SYNC": "1",
            "UV_NO_EDITABLE": "1",
            "PYTHONPATH": "/opt/packages:/fixtures",
            "PYTHONDONTWRITEBYTECODE": "1",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        }
    )
    for name in ("empty-home", "empty-config", "work", "session"):
        (Path("/tmp") / name).mkdir(exist_ok=True)
    root.mkdir()
    report = {
        "provider_spend_usd": 0,
        "synthetic_only": True,
        "batch_seconds_limit": 900,
        "request_case_seconds_limit": 60,
        "fake_provider_receipt_limit": 40,
    }
    try:
        report["entry_gate"] = provenance(root)
    except Exception:
        report["status"] = "failed-entry-gate"
        report["diagnostic"] = traceback.format_exc()
        record(root / "report.json", report)
        return report
    arms = (
        (("budget_request_offline.py", "request"),)
        if request_only
        else (
            ("budget_request_offline.py", "request"),
            ("budget_usage_offline.py", "usage"),
        )
    )
    for script, arm in arms:
        remaining = 900 - (time.monotonic() - started)
        if remaining <= 0:
            report[arm] = {"status": "unexecuted", "reason": "batch bound exhausted"}
            break
        child_command = [
            sys.executable,
            str(Path("/fixtures") / script),
            str(root / arm),
        ]
        if loss_only:
            child_command.append("--loss-only")
        if faults_only:
            child_command.append("--faults-only")
        child = subprocess.Popen(
            child_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            stdout, stderr = child.communicate(
                timeout=min(remaining, 500 if arm == "request" else 100)
            )
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            stdout, stderr = child.communicate(timeout=5)
            report[arm] = {
                "status": "failed",
                "reason": "arm execution bound; owned process group killed",
            }
        else:
            try:
                report[arm] = json.loads(stdout)
            except ValueError:
                report[arm] = {
                    "status": "failed",
                    "reason": "fixture did not return complete report",
                    "exit_code": child.returncode,
                }
        (root / (arm + "-stdout.log")).write_text(stdout)
        (root / (arm + "-stderr.log")).write_text(stderr)
        record(
            root / (arm + "-cleanup.json"),
            {
                "pid": child.pid,
                "exit_code": child.returncode,
                "waited_before_next_arm": True,
            },
        )
    report["elapsed_seconds"] = time.monotonic() - started
    report["scope"] = "affected request arm only" if request_only else "both arms"
    report["status"] = (
        "passed"
        if all(report.get(arm, {}).get("status") == "passed" for _, arm in arms)
        else "nonpassing"
    )
    record(root / "report.json", report)
    return report


def host(archive, *, request_only=False, loss_only=False, faults_only=False):
    """Create, run, copy measured artifacts, then remove the disposable container."""
    started = time.monotonic()
    archive.mkdir(parents=True, exist_ok=False)
    here = Path(__file__).resolve().parent
    plugin = here.parents[2]
    fixtures = [
        here / name
        for name in (
            "budget_offline_batch.py",
            "budget_request_offline.py",
            "budget_usage_offline.py",
        )
    ]
    fixtures += [
        plugin / "tests/helpers" / name
        for name in ("budget_ledger.py", "fake_messages_api.py")
    ]
    assert all(file.is_file() for file in fixtures)
    image = subprocess.run(
        ["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"],
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    assert image.stdout.strip() == IMAGE
    name = "budget-offline-" + uuid.uuid4().hex[:12]
    command = [
        "docker",
        "create",
        "--name",
        name,
        "--pull",
        "never",
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
        "--workdir",
        "/tmp",
        "--entrypoint",
        PYTHON,
    ]
    for key, value in {
        "UV_NO_SYNC": "1",
        "UV_NO_EDITABLE": "1",
        "HOME": "/tmp/empty-home",
        "CLAUDE_CONFIG_DIR": "/tmp/empty-config",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": "/opt/packages:/fixtures",
    }.items():
        command.extend(["--env", key + "=" + value])
    for file in fixtures:
        command.extend(
            ["--mount", f"type=bind,src={file},dst=/fixtures/{file.name},readonly"]
        )
    command.extend([IMAGE, "-c", "import time; time.sleep(900)"])
    execute = [
        "docker",
        "exec",
        name,
        PYTHON,
        "/fixtures/budget_offline_batch.py",
        "--inside",
        "/tmp/proof",
    ]
    if request_only:
        execute.append("--request-only")
    if loss_only:
        execute.append("--loss-only")
    if faults_only:
        execute.append("--faults-only")
    sanitized = [part.replace(str(plugin), "<plugin>") for part in command]
    record(
        archive / "invocation.json",
        {
            "command": sanitized,
            "start": ["docker", "start", name],
            "execute": execute,
            "copy": [
                "docker",
                "exec",
                name,
                PYTHON,
                "-c",
                "import sys,tarfile; t=tarfile.open(fileobj=sys.stdout.buffer,mode='w|'); t.add('/tmp/proof',arcname='proof'); t.close()",
            ],
            "remove": ["docker", "rm", "--force", name],
            "provider_spend_usd": 0,
            "fixture_hashes": {
                file.name: hashlib.sha256(file.read_bytes()).hexdigest()
                for file in fixtures
            },
        },
    )
    created = False
    try:
        create = subprocess.run(
            command, capture_output=True, text=True, timeout=20, check=True
        )
        created = True
        record(
            archive / "container.json", {"id": create.stdout.strip(), "image": IMAGE}
        )
        subprocess.run(
            ["docker", "start", name],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
        try:
            result = subprocess.run(
                execute,
                capture_output=True,
                text=True,
                timeout=max(1, 890 - (time.monotonic() - started)),
                check=False,
            )
            (archive / "container-stdout.log").write_text(result.stdout)
            (archive / "container-stderr.log").write_text(result.stderr)
        except subprocess.TimeoutExpired:
            subprocess.run(
                ["docker", "kill", name], capture_output=True, timeout=10, check=False
            )
            record(
                archive / "host-timeout.json",
                {"status": "nonpassing", "reason": "15 minute batch bound"},
            )
        export = subprocess.run(
            [
                "docker",
                "exec",
                name,
                PYTHON,
                "-c",
                "import sys,tarfile; t=tarfile.open(fileobj=sys.stdout.buffer,mode='w|'); t.add('/tmp/proof',arcname='proof'); t.close()",
            ],
            capture_output=True,
            timeout=10,
            check=True,
        )
        with tarfile.open(fileobj=io.BytesIO(export.stdout)) as bundle:
            bundle.extractall(archive, filter="data")
        record(
            archive / "export.json",
            {
                "sha256": hashlib.sha256(export.stdout).hexdigest(),
                "bytes": len(export.stdout),
            },
        )
    except Exception:
        (archive / "host-diagnostic.log").write_text(
            traceback.format_exc().replace(str(plugin), "<plugin>")
        )
        raise
    finally:
        if created:
            removed = subprocess.run(
                ["docker", "rm", "--force", name],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            check = subprocess.run(
                ["docker", "container", "inspect", name],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            record(
                archive / "host-cleanup.json",
                {
                    "remove_exit_code": removed.returncode,
                    "inspect_exit_code": check.returncode,
                    "confirmed_removed": removed.returncode == 0
                    and check.returncode != 0,
                    "elapsed_seconds": time.monotonic() - started,
                },
            )
            assert removed.returncode == 0 and check.returncode != 0
    return json.loads((archive / "proof/report.json").read_text())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inside", type=Path)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--request-only", action="store_true")
    parser.add_argument("--loss-only", action="store_true")
    parser.add_argument("--faults-only", action="store_true")
    args = parser.parse_args()
    if bool(args.inside) == bool(args.archive):
        parser.error("Select exactly one disposable execution destination")
    if (args.loss_only or args.faults_only) and not args.request_only:
        parser.error("A request refinement requires --request-only")
    if args.loss_only and args.faults_only:
        parser.error("Select only one request refinement")
    report = (
        inside(
            args.inside,
            request_only=args.request_only,
            loss_only=args.loss_only,
            faults_only=args.faults_only,
        )
        if args.inside
        else host(
            args.archive,
            request_only=args.request_only,
            loss_only=args.loss_only,
            faults_only=args.faults_only,
        )
    )
    print(json.dumps(report))
