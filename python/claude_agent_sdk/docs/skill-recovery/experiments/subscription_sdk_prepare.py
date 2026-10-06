"""Check the proposed SDK subscription options without starting a transport."""

import asyncio
import hashlib
import importlib.metadata
import json
import os
import subprocess
from pathlib import Path
from unittest.mock import patch

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from claude_agent_sdk._internal.transport.subprocess_cli import SubprocessCLITransport

MODEL = "claude-haiku-4-5-20251001"
PROMPT = "Reply with exactly SDK_CONNECTIVITY_OK."
CLI_HASH = "15e2d05148f801b5774032faad87e624ecd172e9903288bda448b892eb58fa07"


class OfflineBoundary(RuntimeError):
    pass


def options():
    return ClaudeAgentOptions(
        cli_path="/opt/claude",
        cwd="/work",
        model=MODEL,
        system_prompt="Return the requested text without explanation.",
        tools=[],
        allowed_tools=[],
        skills=[],
        setting_sources=[],
        mcp_servers='{"mcpServers":{}}',
        strict_mcp_config=True,
        permission_mode="default",
        max_turns=1,
        max_budget_usd=0.05,
        parallel_tool_recovery=False,
        env={
            "CLAUDE_CODE_MAX_RETRIES": "0",
            "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "64",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        },
        extra_args={
            "disable-slash-commands": None,
            "no-chrome": None,
            "no-session-persistence": None,
            "prompt-suggestions": "false",
        },
    )


async def prepare():
    if any(name.startswith("ANTHROPIC_") for name in os.environ):
        raise RuntimeError("Provider environment is forbidden; values withheld")
    if importlib.metadata.version("claude-agent-sdk") != "0.2.162":
        raise RuntimeError("Unexpected SDK version")
    if hashlib.sha256(Path("/opt/claude").read_bytes()).hexdigest() != CLI_HASH:
        raise RuntimeError("Unexpected CLI identity")
    selected = options()
    transport = SubprocessCLITransport(prompt=PROMPT, options=selected)
    transport._cli_path = "/opt/claude"
    command = transport._build_command()
    for flag, value in (
        ("--tools", ""),
        ("--model", MODEL),
        ("--max-turns", "1"),
        ("--max-budget-usd", "0.05"),
        ("--mcp-config", '{"mcpServers":{}}'),
    ):
        if command[command.index(flag) + 1] != value:
            raise RuntimeError(f"SDK command differs at {flag}")
    if "--setting-sources=" not in command or "--strict-mcp-config" not in command:
        raise RuntimeError("SDK settings or MCP boundary differs")
    if selected.fallback_model or selected.resume or selected.plugins:
        raise RuntimeError("Fallback, resume and plugins are excluded")
    attempts = []

    async def refuse(self):
        attempts.append(type(self).__name__)
        raise OfflineBoundary("Offline preparation forbids CLI transport startup")

    client = ClaudeSDKClient(options=selected)
    with patch.object(SubprocessCLITransport, "connect", refuse):
        try:
            await client.connect()
        except OfflineBoundary:
            pass
        else:
            raise RuntimeError("Transport guard did not fire")
        finally:
            await client.disconnect()
    if len(attempts) != 1:
        raise RuntimeError("Unexpected transport admission count")
    cli_version = subprocess.run(
        ["/opt/claude", "--version"],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    ).stdout.strip()
    print(
        json.dumps(
            {
                "status": "offline_prepared_live_disabled",
                "sdk_version": importlib.metadata.version("claude-agent-sdk"),
                "cli_version": cli_version,
                "cli_sha256": CLI_HASH,
                "prompt": PROMPT,
                "options": {
                    name: getattr(selected, name)
                    for name in (
                        "model",
                        "tools",
                        "allowed_tools",
                        "skills",
                        "setting_sources",
                        "mcp_servers",
                        "strict_mcp_config",
                        "permission_mode",
                        "max_turns",
                        "max_budget_usd",
                        "parallel_tool_recovery",
                        "env",
                        "extra_args",
                    )
                },
                "sdk_command": command,
                "guarded_transport_attempts": len(attempts),
                "model_cli_spawns": 0,
                "model_requests": 0,
                "required_login_mount": False,
                "probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "limits": [
                    "Configured controls are not runtime budget enforcement.",
                    "No input token, currency or phase aggregate cap is proved.",
                    "No SDK query, result recording or recovery is executed.",
                    "This file exposes no live execution mode.",
                    "Mount isolation is supplied by the recorded container invocation.",
                    "SDK version check is not fresh installed wheel provenance proof.",
                ],
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    asyncio.run(prepare())
