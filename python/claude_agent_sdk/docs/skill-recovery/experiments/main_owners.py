"""Bounded completed-transcript ownership fault probe, fake model only."""

import argparse
import asyncio
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
import traceback
from pathlib import Path


def dump(path, value, root):
    path.write_text(json.dumps(value, indent=2).replace(str(root), "<scratch>"))


def helper(path):
    spec = importlib.util.spec_from_file_location("supervision", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scrub():
    for key in list(os.environ):
        if key.startswith(
            (
                "ANTHROPIC_",
                "CLAUDE_",
                "HYBRID_",
                "OPENAI_",
                "AWS_",
                "GOOGLE_",
                "AZURE_",
                "BEDROCK_",
            )
        ) or key.lower() in {
            "http_proxy",
            "https_proxy",
            "all_proxy",
            "pythonpath",
            "pythonhome",
        }:
            os.environ.pop(key, None)


async def owner(args):
    from tests.hybrid.engine import Burst
    from tests.hybrid.models import Attempt
    from tests.hybrid.store import TranscriptStore

    root = Path(args.root)
    env = {
        k: v
        for k, v in os.environ.items()
        if k.startswith(("ANTHROPIC_", "CLAUDE_", "DISABLE_"))
        or k.lower() == "no_proxy"
    }
    callbacks = []

    async def forbidden(call):
        callbacks.append(call.id)
        raise AssertionError("Completed transcript unexpectedly executes host callback")

    burst = Burst(
        root,
        env,
        TranscriptStore(root / "store.db"),
        args.session,
        Attempt(0, args.number, "owner-" + str(args.number)),
        forbidden,
        resume=True,
        recovery=True,
    )
    path = root / ("owner-" + str(args.number) + ".json")
    report = {"number": args.number}
    try:
        await burst.open()
        report.update(status="ready", cli_pid=burst.pid)
        dump(path, report, root)
        while not (root / "release").exists():
            await asyncio.sleep(0.02)
        result = await asyncio.wait_for(burst.query("continue"), 30)
        report.update(
            status="PASS",
            result=result.result,
            source_reported_cli=burst.version,
            callbacks=callbacks,
        )
        assert callbacks == []
    except Exception:
        report.update(
            status="FAILED", traceback=traceback.format_exc(), callbacks=callbacks
        )
        raise
    finally:
        await burst.close()
        dump(path, report, root)


async def run(args):
    from claude_agent_sdk import project_key_for_directory
    from claude_agent_sdk._internal.main_agent_recovery import pending_tool_uses

    from tests.helpers.fake_messages_api import FakeMessagesAPI, engine_env
    from tests.hybrid.store import TranscriptStore

    root = Path(args.root).resolve()
    source = Path(args.source_root).resolve()
    if root.exists() or root.is_relative_to(source) or source.is_relative_to(root):
        raise ValueError("Fresh output root must be separate from source closure")
    root.mkdir(parents=True)
    cli = Path(args.cli_path)
    digest = hashlib.sha256(cli.read_bytes()).hexdigest()
    assert digest == "15e2d05148f801b5774032faad87e624ecd172e9903288bda448b892eb58fa07"
    version = subprocess.check_output([str(cli), "--version"], text=True).strip()
    assert "2.1.274" in version
    with sqlite3.connect(
        "file:" + str(Path(args.seed_store).resolve()) + "?mode=ro", uri=True
    ) as db:
        keys = db.execute(
            "SELECT DISTINCT project,session FROM entries WHERE subpath='' "
        ).fetchall()
        assert len(keys) == 1
        original_project, session = keys[0]
        entries = [
            json.loads(r[0])
            for r in db.execute(
                "SELECT data FROM entries WHERE project=? AND session=? AND subpath='' ORDER BY seq",
                keys[0],
            )
        ]
    key = {"project_key": project_key_for_directory(str(root)), "session_id": session}
    pending, _ = pending_tool_uses(key, entries)
    assert pending == [] and entries
    store = TranscriptStore(root / "store.db")
    await store.append(key, entries)
    dump(root / "seed-transcript.json", entries, root)
    api = FakeMessagesAPI(
        lambda body: [{"type": "text", "text": "DONE owner continuation"}]
    ).start()
    assert api.base_url.startswith("http://127.0.0.1:")
    supervision = helper(args.supervision_helper)
    procs, cleanup, report = [], [], {"status": "FAILED; no completion claim"}
    try:
        for number in (1, 2):
            argv = [
                args.python,
                str(Path(__file__).resolve()),
                "--worker",
                "--source-root",
                str(source),
                "--root",
                str(root),
                "--cli-path",
                str(cli),
                "--number",
                str(number),
                "--session",
                session,
            ]
            with (root / ("owner-" + str(number) + ".log")).open("wb") as log:
                proc = subprocess.Popen(
                    argv,
                    env={
                        **os.environ,
                        **engine_env(api, str(root / ("config-" + str(number)))),
                    },
                    stdout=log,
                    stderr=subprocess.STDOUT,
                )
            proc._owned_children = []
            proc._monitor = asyncio.create_task(supervision.monitor_children(proc))
            procs.append(proc)
        deadline = asyncio.get_running_loop().time() + 35
        while not all((root / ("owner-" + str(n) + ".json")).exists() for n in (1, 2)):
            if (
                any(p.poll() is not None for p in procs)
                or asyncio.get_running_loop().time() > deadline
            ):
                raise RuntimeError("Owner failed before shared live-CLI barrier")
            await asyncio.sleep(0.05)
        ready = [
            json.loads((root / ("owner-" + str(n) + ".json")).read_text())
            for n in (1, 2)
        ]
        assert all(r["status"] == "ready" for r in ready)
        identities = [supervision.identity(r["cli_pid"]) for r in ready]
        assert all(i and i["state"] != "Z" for i in identities)
        assert identities[0]["pid"] != identities[1]["pid"]
        assert api.requests == []
        (root / "release").touch()
        deadline = asyncio.get_running_loop().time() + 40
        while any(p.poll() is None for p in procs):
            if asyncio.get_running_loop().time() > deadline:
                raise TimeoutError("Bounded owner continuations did not exit")
            await asyncio.sleep(0.05)
        outcomes = [
            json.loads((root / ("owner-" + str(n) + ".json")).read_text())
            for n in (1, 2)
        ]
        assert all(p.returncode == 0 for p in procs), outcomes
        assert len(api.requests) == 2 and api.errors == []
        assert all(r["callbacks"] == [] for r in outcomes)
        report = {
            "status": "PROBE PASS; exclusive ownership requirement FAILED",
            "live_cli_identities_before_release": identities,
            "model_requests_before_release": 0,
            "model_requests_after_release": len(api.requests),
            "owners": outcomes,
            "cli_version": version,
            "cli_sha256": digest,
            "versions": {
                n: importlib.metadata.version(n)
                for n in ("claude-agent-sdk", "temporalio")
            },
            "seed_disposition": "Completed actual-CLI transcript copied unchanged into a new project-key store; retained session ID and entry metadata",
            "original_project": original_project,
            "proof_scope": "Two completed-transcript resumes create simultaneous CLI processes and model continuations. No pending recovery callback or external effect; SDK missing-result CAS is not an ownership lease.",
        }
        dump(root / "final-transcript.json", await store.load(key), root)
    except Exception:
        report["traceback"] = traceback.format_exc()
        raise
    finally:
        for proc in procs:
            cleanup.append(await supervision.stop(proc))
        report["cleanup"] = cleanup
        dump(root / "report.json", report, root)
        dump(root / "model-requests.json", api.requests, root)
        api.stop()
    print(json.dumps(report), flush=True)


async def main():
    parser = argparse.ArgumentParser()
    for name in ("source-root", "root", "cli-path"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--supervision-helper")
    parser.add_argument("--seed-store")
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--number", type=int)
    parser.add_argument("--session")
    args = parser.parse_args()
    sys.path.insert(0, args.source_root)
    if args.worker:
        os.environ["HYBRID_CLI_PATH"] = args.cli_path
        await owner(args)
    else:
        scrub()
        if not args.seed_store or not args.supervision_helper:
            parser.error("Parent probe requires --seed-store and --supervision-helper")
        await run(args)


if __name__ == "__main__":
    asyncio.run(main())
