"""Run the source session lifecycle checks in the existing isolated image."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import sys
from pathlib import Path


def main() -> int:
    """Verify the existing pins and test a source overlay without building a package."""
    if os.environ.get("UV_NO_SYNC") != "1" or os.environ.get("UV_NO_EDITABLE") != "1":
        raise RuntimeError("Implicit dependency synchronization must be disabled")
    if importlib.metadata.version("claude-agent-sdk") != "0.2.162":
        raise RuntimeError("SDK pin differs from the authorized isolated lane")
    cli_hash = hashlib.sha256(Path("/opt/claude").read_bytes()).hexdigest()
    if cli_hash != "15e2d05148f801b5774032faad87e624ecd172e9903288bda448b892eb58fa07":
        raise RuntimeError("CLI hash differs from the unchanged isolated pin")
    import pytest

    import temporalio

    # The installed package stays untouched. This verifies source, not a wheel.
    temporalio.__path__.insert(0, "/source/temporalio")
    files = [
        Path("/source/temporalio/claude_agent_sdk/_runner.py"),
        Path("/source/temporalio/claude_agent_sdk/_session_control.py"),
        Path("/checks/test_lifecycle.py"),
        Path("/checks/test_tool_policy.py"),
    ]
    print(
        json.dumps(
            {
                "evidence_kind": "offline_source_lifecycle_and_policy_checks",
                "python": sys.version,
                "sdk": importlib.metadata.version("claude-agent-sdk"),
                "temporalio": importlib.metadata.version("temporalio"),
                "cli_sha256": cli_hash,
                "source_sha256": {
                    str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files
                },
                "model_calls": 0,
                "engine_launches": 0,
                "installation_build_or_sync": False,
                "host_process_teardown_proved": False,
            }
        ),
        flush=True,
    )
    return pytest.main(
        [
            "/checks/test_lifecycle.py",
            "/checks/test_tool_policy.py",
            "--confcutdir=/checks",
            "-q",
            "-p",
            "no:cacheprovider",
            "-o",
            "asyncio_mode=auto",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
