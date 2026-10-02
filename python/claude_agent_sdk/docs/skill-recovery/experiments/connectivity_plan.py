"""Print the proposed subscription connectivity command without executing it."""

import json

from login_container import container_args, image_id

MODEL = "claude-haiku-4-5-20251001"
PROMPT = "Reply with exactly CONNECTIVITY_OK."


def main():
    identity = image_id()
    command = container_args(network="bridge", login=True)
    command += [
        "--name",
        "claude-recovery-connectivity",
        "--env",
        "CLAUDE_CODE_MAX_RETRIES=0",
        "--env",
        "CLAUDE_CODE_MAX_OUTPUT_TOKENS=64",
        "--env",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1",
        identity,
        "--print",
        "--model",
        MODEL,
        "--max-turns",
        "1",
        "--max-budget-usd",
        "0.05",
        "--tools",
        "",
        "--strict-mcp-config",
        "--mcp-config",
        '{"mcpServers":{}}',
        "--setting-sources",
        "",
        "--disable-slash-commands",
        "--no-chrome",
        "--no-session-persistence",
        "--prompt-suggestions",
        "false",
        "--system-prompt",
        "Return the requested text without explanation.",
        "--output-format",
        "json",
        PROMPT,
    ]
    print(
        json.dumps(
            {
                "status": "proposed_not_executed",
                "image_id": identity,
                "model": MODEL,
                "prompt": PROMPT,
                "command_argv": command,
                "outer_timeout_seconds": 60,
                "on_timeout": "Kill the named container and retain complete output; do not retry.",
                "host_attempt_limit": 1,
                "api_retry_setting": 0,
                "output_token_setting": 64,
                "usd_budget_setting": 0.05,
                "limits": [
                    "Subscription entitlement and model access are unverified.",
                    "CLI retry/output/budget controls are configured, not runtime proved.",
                    "Turn count and timeout are not hard input-token or dollar caps.",
                    "Stop on quota, extra usage, model unavailability or unexpected output.",
                    "No alternate model, API credential, retry or extra usage opt in is authorized.",
                    "This is CLI connectivity, not SDK recovery or ticket completion.",
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
