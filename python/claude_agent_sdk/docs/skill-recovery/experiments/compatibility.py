"""Inspect installed SDK recovery options without starting a CLI or model."""

import importlib.metadata
import importlib.util
import json
import sys

from claude_agent_sdk import ClaudeAgentOptions


async def recorded_result(pending):
    raise AssertionError("Compatibility inspection must not invoke recovery")


fields = ClaudeAgentOptions.__dataclass_fields__
report = {
    "python_version": sys.version.split()[0],
    "sdk_version": importlib.metadata.version("claude-agent-sdk"),
    "temporal_version": importlib.metadata.version("temporalio"),
    "option_fields": {
        key: key in fields
        for key in (
            "session_store",
            "session_store_flush",
            "recover_pending_tool",
            "parallel_tool_recovery",
            "strict_mcp_config",
            "forward_subagent_text",
        )
    },
    "recovery_module": importlib.util.find_spec(
        "claude_agent_sdk._internal.main_agent_recovery"
    )
    is not None,
    "cli_spawns": 0,
    "model_requests": 0,
    "effects": 0,
}
try:
    ClaudeAgentOptions(recover_pending_tool=recorded_result)
except TypeError as exc:
    report["constructor_result"] = type(exc).__name__ + ": " + str(exc)
else:
    report["constructor_result"] = "accepted"
print(json.dumps(report, indent=2, sort_keys=True))
