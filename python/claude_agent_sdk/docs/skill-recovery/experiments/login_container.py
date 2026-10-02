"""Prepare an isolated login container from existing artifacts without model calls."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

IMAGE = "claude-recovery-proof:checkpoint-6d220335"
VOLUME = "claude-recovery-proof-login"
CLI_SHA256 = "15e2d05148f801b5774032faad87e624ecd172e9903288bda448b892eb58fa07"


def call(command, **kwargs):
    return subprocess.run(command, check=True, **kwargs)


def image_id():
    result = call(
        ["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"],
        capture_output=True,
        text=True,
    )
    identity = result.stdout.strip()
    if not identity.startswith("sha256:") or len(identity) != 71:
        raise RuntimeError("Image identity is invalid")
    return identity


def container_args(*, network, login=False):
    args = [
        "docker",
        "run",
        "--rm",
        "--init",
        "--read-only",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--pids-limit=128",
        "--memory=2g",
        "--cpus=2",
        "--network",
        network,
        "--tmpfs",
        "/tmp:rw,nosuid,nodev,size=256m",
        "--tmpfs",
        "/work:rw,nosuid,nodev,uid=1000,gid=1000,size=128m",
    ]
    if login:
        args += ["--mount", f"type=volume,source={VOLUME},target=/home/proof"]
    else:
        args += ["--tmpfs", "/home/proof:rw,nosuid,nodev,uid=1000,gid=1000,size=128m"]
    return args


def build(args):
    runtime = args.runtime.resolve(strict=True)
    packages = args.packages.resolve(strict=True)
    cli = args.cli.resolve(strict=True)
    if hashlib.sha256(cli.read_bytes()).hexdigest() != CLI_SHA256:
        raise ValueError("CLI differs from the recorded feasibility binary")
    if not (runtime / "bin/python3.13").is_file():
        raise ValueError("Expected the existing Python 3.13 runtime")
    if not (packages / "claude_agent_sdk").is_dir():
        raise ValueError("Expected installed SDK packages")
    if not args.base.startswith("sha256:") or len(args.base) != 71:
        raise ValueError("Use an existing base image's full sha256 identity")
    call(["docker", "image", "inspect", args.base], stdout=subprocess.DEVNULL)
    base_tag = f"claude-recovery-base:{args.base[7:19]}"
    call(["docker", "tag", args.base, base_tag])
    with tempfile.TemporaryDirectory(prefix="claude-login-image-") as directory:
        context = Path(directory)
        shutil.copytree(runtime, context / "runtime")
        shutil.copytree(packages, context / "packages")
        shutil.copy2(cli, context / "claude")
        shutil.copy2(Path(__file__).with_suffix(".Dockerfile"), context / "Dockerfile")
        call(
            [
                "docker",
                "build",
                "--network=none",
                "--pull=false",
                "--build-arg",
                f"BASE_IMAGE={base_tag}",
                "--tag",
                IMAGE,
                str(context),
            ]
        )


def check():
    identity = image_id()
    print(json.dumps({"image_id": identity}), flush=True)
    code = (
        "import hashlib,importlib.metadata,json,os,sys; "
        "from temporalio.claude_agent_sdk import ClaudeAgentSdkRunner; "
        "from claude_agent_sdk._internal.main_agent_recovery import pending_tool_uses; "
        "assert os.getuid()==1000; "
        "assert sys.version_info[:3]==(3,13,15); "
        "assert importlib.metadata.version('claude-agent-sdk')=='0.2.162'; "
        f"assert hashlib.sha256(open('/opt/claude','rb').read()).hexdigest()=='{CLI_SHA256}'; "
        "assert not any(k.startswith('ANTHROPIC_') for k in os.environ); "
        "print(json.dumps({'python':sys.version.split()[0], "
        "'sdk':importlib.metadata.version('claude-agent-sdk'), "
        "'temporal':importlib.metadata.version('temporalio'), "
        "'model_calls':0,'credentials_mounted':False}))"
    )
    call(
        container_args(network="none")
        + ["--entrypoint", "/opt/python/bin/python3.13", identity, "-c", code]
    )
    call(container_args(network="none") + [identity, "--version"])
    call(container_args(network="none") + [identity, "auth", "login", "--help"])


def status():
    identity = image_id()
    result = subprocess.run(
        container_args(network="none", login=True) + [identity, "auth", "status"],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            "Authentication status returned no JSON; raw output withheld"
        ) from None
    print(
        json.dumps(
            {
                "image_id": identity,
                **{
                    key: data.get(key)
                    for key in ("loggedIn", "authMethod", "apiProvider")
                },
            }
        )
    )
    if result.returncode not in (0, 1):
        raise RuntimeError("Authentication status command failed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    builder = commands.add_parser("build")
    builder.add_argument("--base", required=True)
    builder.add_argument("--runtime", type=Path, required=True)
    builder.add_argument("--packages", type=Path, required=True)
    builder.add_argument("--cli", type=Path, required=True)
    commands.add_parser("check")
    commands.add_parser("login")
    commands.add_parser("status")
    args = parser.parse_args()
    if args.command == "build":
        build(args)
    elif args.command == "check":
        check()
    elif args.command == "status":
        status()
    else:
        if not os.isatty(0):
            raise RuntimeError("Run login yourself from an interactive terminal")
        identity = image_id()
        print(json.dumps({"image_id": identity}), flush=True)
        call(
            container_args(network="bridge", login=True)
            + ["-it", identity, "auth", "login", "--claudeai"]
        )


if __name__ == "__main__":
    main()
