"""Run one approved connectivity plan and retain complete output in private scratch."""

import json
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path


def main():
    plan = json.loads(
        subprocess.run(
            [sys.executable, str(Path(__file__).with_name("connectivity_plan.py"))],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )
    root = Path(tempfile.mkdtemp(prefix="claude-connectivity-"))
    name = f"claude-connectivity-{uuid.uuid4().hex}"
    command = plan["command_argv"]
    command[command.index("--name") + 1] = name
    plan["command_argv"] = command
    (root / "plan.json").write_text(json.dumps(plan, indent=2))
    timed_out = False
    with (
        (root / "stdout.json").open("w") as stdout,
        (root / "stderr.txt").open("w") as stderr,
    ):
        process = subprocess.Popen(
            command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr
        )
        try:
            code = process.wait(timeout=plan["outer_timeout_seconds"])
        except subprocess.TimeoutExpired:
            timed_out = True
            subprocess.run(
                ["docker", "kill", name], capture_output=True, timeout=15, check=False
            )
            process.kill()
            code = process.wait(timeout=15)
        finally:
            cleanup = subprocess.run(
                ["docker", "rm", "--force", name],
                capture_output=True,
                timeout=15,
                check=False,
            )
    try:
        result = json.loads((root / "stdout.json").read_text())
    except json.JSONDecodeError:
        result = {}
    passed = (
        code == 0
        and not timed_out
        and result.get("result", "").strip() == "CONNECTIVITY_OK"
        and not result.get("is_error")
    )
    report = {
        "status": "passed" if passed else "failed",
        "image_id": plan["image_id"],
        "requested_model": plan["model"],
        "host_attempts": 1,
        "exit_code": code,
        "timed_out": timed_out,
        "result_subtype": result.get("subtype"),
        "num_turns": result.get("num_turns"),
        "usage": result.get("usage"),
        "model_usage": result.get("modelUsage"),
        "reported_cost_usd": result.get("total_cost_usd"),
        "cost_kind": "CLI estimate, not verified subscription billing",
        "cleanup_returncode": cleanup.returncode,
        "evidence_root": str(root),
        "limits": plan["limits"],
    }
    (root / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
