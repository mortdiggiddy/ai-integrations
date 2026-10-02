"""Probe installed SDK plugin loading with a local scripted Messages API."""

import argparse
import asyncio
import dataclasses
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

import claude_agent_sdk
from claude_agent_sdk import ClaudeAgentOptions, query
from claude_agent_sdk._internal.transport.subprocess_cli import SubprocessCLITransport
from claude_agent_sdk._version import __version__

parser = argparse.ArgumentParser()
parser.add_argument(
    "--root", type=Path, required=True, help="Isolated scratch output directory"
)
parser.add_argument("--repo", type=Path)
args = parser.parse_args()
ROOT = (args.repo or Path(__file__).resolve().parents[5]).resolve()
sys.path.insert(0, str(ROOT / "python/claude_agent_sdk"))
fake_api = importlib.import_module("tests.helpers.fake_messages_api")
FakeMessagesAPI, engine_env = fake_api.FakeMessagesAPI, fake_api.engine_env

HERE = args.root.resolve()
if HERE == ROOT or ROOT in HERE.parents:
    raise ValueError("Scratch output must be outside the repository")
for key in list(os.environ):
    if key.startswith(("CLAUDE", "ANTHROPIC", "AWS_", "GOOGLE_", "AZURE_")):
        del os.environ[key]
os.environ["CLAUDE_CONFIG_DIR"] = str(HERE / "isolated-config")
os.environ["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"
os.environ["DISABLE_TELEMETRY"] = "1"
os.environ["DISABLE_ERROR_REPORTING"] = "1"
CLI = Path(claude_agent_sdk.__file__).parent / "_bundled/claude"


class ReadAPI(FakeMessagesAPI):
    def write(self, handler, body, blocks):
        names = [tool.get("name") for tool in body.get("tools", [])]
        results = [
            block
            for message in body.get("messages", [])
            for block in message.get("content", [])
            if isinstance(block, dict) and block.get("type") == "tool_result"
        ]
        if "Read" in names:
            blocks = (
                [
                    {
                        "type": "tool_use",
                        "id": "toolu_mods_unique_read",
                        "name": "Read",
                        "input": {"file_path": str(HERE / "input.txt")},
                    }
                ]
                if not results
                else [{"type": "text", "text": "OFFLINE_DONE"}]
            )
        super().write(handler, body, blocks)


async def main():
    # These isolated fixtures are experiment outputs; no repository files change.
    (HERE / "plugin/.claude-plugin").mkdir(parents=True, exist_ok=True)
    (HERE / "plugin/hooks").mkdir(parents=True, exist_ok=True)
    (HERE / "plugin/.claude-plugin/plugin.json").write_text(
        json.dumps(
            {
                "name": "offline-mods-marker",
                "version": "0.1.0",
                "description": "Offline Mods loading probe",
            }
        )
    )
    (HERE / "plugin/hooks/hooks.json").write_text(
        json.dumps({"modules": ["./register.ts"]})
    )
    (HERE / "plugin/hooks/register.ts").write_text(
        'export function register(on) { on("tool.call", {tool: "Read"}, () => ({deny: "MODS_UNIQUE_DENY_20261001"})); }\n'
    )
    (HERE / "input.txt").write_text("HARMLESS_READ_EFFECT_20261001\n")
    validation = subprocess.run(
        [str(CLI), "plugin", "validate", str(HERE / "plugin")],
        capture_output=True,
        text=True,
        timeout=30,
    )
    api = ReadAPI(lambda body: []).start()
    env = engine_env(api, str(HERE / "isolated-config"))
    assert api.base_url.startswith("http://127.0.0.1:")
    env.update({"HTTP_PROXY": "", "HTTPS_PROXY": "", "ALL_PROXY": ""})
    options = ClaudeAgentOptions(
        cli_path=str(CLI),
        cwd=str(HERE),
        env=env,
        tools=["Read"],
        allowed_tools=["Read"],
        plugins=[{"type": "local", "path": str(HERE / "plugin")}],
        setting_sources=[],
        model="claude-sonnet-4-5",
        max_turns=2,
    )
    transport = SubprocessCLITransport(prompt="Read the input", options=options)
    record = {
        "python": sys.version.split()[0],
        "sdk": __version__,
        "cli": subprocess.check_output([str(CLI), "--version"], text=True).strip(),
        "mods_option": any(
            "mods" in field.name.lower()
            for field in dataclasses.fields(ClaudeAgentOptions)
        ),
        "plugin_forwarded": "--plugin-dir" in transport._build_command(),
        "paid_calls": False,
        "fake_endpoint": True,
        "read_request_id": "toolu_mods_unique_read",
        "plugin_listed": False,
        "result_request_ids": [],
        "message_types": [],
        "negative_controls": "unexecuted: interception unsupported for this invocation",
    }
    record["plugin_validation"] = {
        "returncode": validation.returncode,
        "output": (validation.stdout + validation.stderr).replace(
            str(HERE), "<scratch>"
        ),
    }
    transcript = []
    try:
        async with asyncio.timeout(30):
            async for message in query(
                prompt="Read the input file once.", options=options
            ):
                record["message_types"].append(type(message).__name__)
                transcript.append(
                    {
                        "type": type(message).__name__,
                        "message": dataclasses.asdict(message),
                    }
                )
                if (
                    type(message).__name__ == "SystemMessage"
                    and message.subtype == "init"
                ):
                    record["plugin_listed"] = any(
                        p.get("name") == "offline-mods-marker"
                        for p in message.data.get("plugins", [])
                    )
                if type(message).__name__ == "UserMessage" and isinstance(
                    message.content, list
                ):
                    record["result_request_ids"].extend(
                        getattr(block, "tool_use_id", None) for block in message.content
                    )
                if type(message).__name__ == "ResultMessage":
                    record["terminal_subtype"] = message.subtype
                    record["cli_reported_list_price_cost"] = message.total_cost_usd
    except Exception as exc:
        record["error"] = type(exc).__name__
        record["detail"] = (
            str(exc).replace(str(ROOT), "<repo>").replace(str(HERE), "<scratch>")
        )
    finally:
        record.update(
            {
                "requests": len(api.requests),
                "hook_marker": any(
                    "MODS_UNIQUE_DENY_20261001" in json.dumps(body)
                    for body in api.requests
                ),
                "read_result_marker": any(
                    "HARMLESS_READ_EFFECT_20261001" in json.dumps(body)
                    for body in api.requests
                ),
                "pairing_errors": api.errors,
            }
        )
        record["disposition"] = (
            "unsupported interception in tested invocation"
            if not record["hook_marker"] and record["read_result_marker"]
            else "inspect result"
        )

        def sanitize(value):
            encoded = (
                json.dumps(value, default=str)
                .replace(str(HERE), "<scratch>")
                .replace(str(ROOT), "<repo>")
            )
            for private_root, token in [
                (str(Path.home()), "<home>"),
                ("/run/user/", "<runtime>/"),
            ]:
                encoded = encoded.replace(private_root, token)
            return json.loads(encoded)

        (HERE / "transcript.json").write_text(
            json.dumps(sanitize(transcript), indent=2) + "\n"
        )
        (HERE / "model-requests.json").write_text(
            json.dumps(sanitize(api.requests), indent=2) + "\n"
        )
        # The machine neutral result is a reproducible experiment output.
        (HERE / "result.json").write_text(json.dumps(record, indent=2) + "\n")
        print(json.dumps(record))
        api.stop()
    assert "error" not in record, record
    assert record["plugin_listed"], record
    assert record["result_request_ids"] == [record["read_request_id"]], record
    assert record["pairing_errors"] == [], record
    assert record["requests"] == 2, record
    assert record["terminal_subtype"] == "success", record
    assert record["read_result_marker"] and not record["hook_marker"], record


asyncio.run(main())
