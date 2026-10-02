"""Exercise a disposable same-host lease and owned-process recovery gate."""

import argparse
import asyncio
import base64
import fcntl
import hashlib
import importlib.metadata
import json
import os
import signal
import socket
import sqlite3
import subprocess
import sys
import traceback
from pathlib import Path

import main_recovery
import native_replay


def save(path, value):
    path.write_text(json.dumps(value, indent=2))


def live(identities):
    result = []
    for old in identities:
        now = native_replay.identity(old["pid"])
        if now and now["start_ticks"] == old["start_ticks"] and now["state"] != "Z":
            result.append(now)
    return result


class Lease:
    """Serialize admission and refuse recorded surviving processes."""

    def __init__(self, root):
        self.root = root
        self.file = None

    def acquire(self):
        self.file = (self.root / "session.lock").open("a+")
        try:
            fcntl.flock(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.file.close()
            self.file = None
            return "lease-held"
        registry = self.root / "owned-processes.json"
        if registry.exists() and live(json.loads(registry.read_text())):
            self.file.close()
            self.file = None
            return "owned-processes-unresolved"
        return None

    def release(self):
        if self.file:
            self.file.close()
            self.file = None


async def inventory(root):
    known = {}
    while True:
        known.update(
            {
                (p["pid"], p["start_ticks"]): p
                for p in native_replay.descendants(os.getpid())
            }
        )
        save(root / "owned-processes.json", list(known.values()))
        await asyncio.sleep(0.01)


async def leased_worker(args):
    root = Path(args.root)
    lease = Lease(root)
    refusal = lease.acquire()
    if refusal:
        save(
            root / ("refusal-" + str(args.worker_number) + ".json"),
            {"refused": refusal},
        )
        return 23
    observer = asyncio.create_task(inventory(root))
    try:
        if args.mode == "owner":
            from tests.hybrid.engine import Burst
            from tests.hybrid.models import Attempt
            from tests.hybrid.store import TranscriptStore

            async def forbidden(call):
                raise AssertionError("Completed transcript invoked tool")

            env = {
                k: v
                for k, v in os.environ.items()
                if k.startswith(("ANTHROPIC_", "CLAUDE_", "DISABLE_"))
                or k.lower() == "no_proxy"
            }
            burst = Burst(
                root,
                env,
                TranscriptStore(root / "store.db"),
                args.session,
                Attempt(0, args.worker_number, "local-owner"),
                forbidden,
                resume=True,
                recovery=True,
            )
            try:
                await burst.open()
                save(
                    root / ("ready-" + str(args.worker_number) + ".json"),
                    {"cli": native_replay.identity(burst.pid)},
                )
                while not (root / "release").exists():
                    await asyncio.sleep(0.02)
                result = await asyncio.wait_for(burst.query("continue"), 35)
                save(root / "owner-result.json", {"result": result.result})
                while not (root / "teardown").exists():
                    await asyncio.sleep(0.02)
            finally:
                await burst.close()
        else:
            child = subprocess.Popen(
                [sys.executable, "-c", "import time; time.sleep(300)"]
            )
            save(
                root / "controlled-tool-descendant.json",
                native_replay.identity(child.pid),
            )
            await main_recovery.temporal_worker(args)
    finally:
        observer.cancel()
        try:
            await observer
        except asyncio.CancelledError:
            pass
        owned = (
            json.loads((root / "owned-processes.json").read_text())
            if (root / "owned-processes.json").exists()
            else []
        )
        if live(owned):
            save(root / "teardown-unresolved.json", live(owned))
        lease.release()
    return 0


def gate_probe(root):
    lease = Lease(root)
    refusal = lease.acquire()
    lease.release()
    return refusal


async def stop(proc):
    root = proc._root
    if proc.poll() is None:
        old_owner = native_replay.identity(proc.pid)
        proc.kill()
        proc.wait()
        registry = root / "owned-processes.json"
        known = json.loads(registry.read_text()) if registry.exists() else []
        known.extend(proc._owned_children)
        before = live(known)
        frozen = []
        for owned in before:
            if proc._contain and live([owned]):
                os.kill(owned["pid"], signal.SIGSTOP)
                frozen.append(owned)
        refusal = gate_probe(root)
        assert before and refusal == "owned-processes-unresolved", (before, refusal)
        requests_before = len(proc._api.requests)
        cli_count_before = len(main_recovery.read_records(root / "cli-pids.jsonl"))
        argv = list(proc._argv)
        argv[argv.index("--worker-number") + 1] = "99"
        with (root / "blocked-replacement.log").open("wb") as log:
            contender = subprocess.Popen(
                argv, env=proc._env, stdout=log, stderr=subprocess.STDOUT
            )
        deadline = asyncio.get_running_loop().time() + 15
        while contender.poll() is None:
            if asyncio.get_running_loop().time() > deadline:
                contender.kill()
                contender.wait()
                raise TimeoutError("Blocked replacement did not refuse admission")
            await asyncio.sleep(0.02)
        assert contender.returncode == 23
        assert json.loads((root / "refusal-99.json").read_text())["refused"] == refusal
        orphan_requests = len(proc._api.requests) - requests_before
        assert (
            len(main_recovery.read_records(root / "cli-pids.jsonl")) == cli_count_before
        )
        result = await native_replay.stop(proc)
        assert live(known) == []
        assert gate_probe(root) is None
        result.update(
            owner_before_loss=old_owner,
            replacement_before_cleanup=refusal,
            blocked_worker_exit=contender.returncode,
            orphan_model_requests_during_admission_probe=orphan_requests,
            contained_during_admission_probe=frozen,
            blocked_worker_reached_sdk=False,
            blocked_worker_new_cli_starts=0,
            replacement_after_cleanup="allowed",
            controlled_descendant=json.loads(
                (root / "controlled-tool-descendant.json").read_text()
            ),
        )
        return result
    return await native_replay.stop(proc)


async def launch(args, root, api, mode, number=1, address=None, queue=None):
    from tests.helpers.fake_messages_api import engine_env

    argv = [
        args.python,
        str(Path(__file__).resolve()),
        "--worker",
        "--source-root",
        args.source_root,
        "--root",
        str(root),
        "--cli-path",
        args.cli_path,
        "--mode",
        mode,
        "--worker-number",
        str(number),
    ]
    if address:
        argv.extend(["--address", address, "--queue", queue])
    if getattr(args, "session", None):
        argv.extend(["--session", args.session])
    env = {**os.environ, **engine_env(api, str(root / ("config-" + str(number))))}
    with (root / (mode + "-" + str(number) + ".log")).open("wb") as log:
        proc = subprocess.Popen(argv, env=env, stdout=log, stderr=subprocess.STDOUT)
    proc._root = root
    proc._argv, proc._env, proc._api = argv, env, api
    proc._contain = not args.accounting_only
    args.active_api = api
    proc._owned_children = []
    proc._monitor = asyncio.create_task(native_replay.monitor_children(proc))
    return proc, sys.modules[__name__]


async def concurrent(args, base):
    from claude_agent_sdk import project_key_for_directory
    from claude_agent_sdk._internal.main_agent_recovery import pending_tool_uses

    from tests.helpers.fake_messages_api import FakeMessagesAPI
    from tests.hybrid.store import TranscriptStore

    root = base / "concurrent"
    root.mkdir()
    with sqlite3.connect(
        "file:" + str(Path(args.seed_store).resolve()) + "?mode=ro", uri=True
    ) as db:
        keys = db.execute(
            "SELECT DISTINCT project,session FROM entries WHERE subpath=''"
        ).fetchall()
        assert len(keys) == 1
        entries = [
            json.loads(row[0])
            for row in db.execute(
                "SELECT data FROM entries WHERE project=? AND session=? AND subpath='' ORDER BY seq",
                keys[0],
            )
        ]
    args.session = keys[0][1]
    key = {
        "project_key": project_key_for_directory(str(root)),
        "session_id": args.session,
    }
    pending, _ = pending_tool_uses(key, entries)
    assert entries and pending == []
    await TranscriptStore(root / "store.db").append(key, entries)
    api = FakeMessagesAPI(
        lambda body: [{"type": "text", "text": "DONE exclusive continuation"}]
    ).start()
    procs = []
    report = {"status": "FAILED"}
    try:
        first, _ = await launch(args, root, api, "owner", 1)
        procs.append(first)

        async def ready():
            if first.poll() is not None:
                raise RuntimeError((root / "owner-1.log").read_text())
            return (root / "ready-1.json").exists()

        await main_recovery.until(ready, 40)
        second, _ = await launch(args, root, api, "owner", 2)
        procs.append(second)
        while second.poll() is None:
            await asyncio.sleep(0.02)
        assert second.returncode == 23
        assert len(api.requests) == 0
        assert (
            json.loads((root / "refusal-2.json").read_text())["refused"] == "lease-held"
        )
        (root / "release").touch()

        async def completed():
            return (root / "owner-result.json").exists()

        await main_recovery.until(completed, 40)
        assert gate_probe(root) == "lease-held"
        (root / "teardown").touch()
        while first.poll() is None:
            await asyncio.sleep(0.02)
        assert first.returncode == 0 and len(api.requests) == 1 and api.errors == []
        assert gate_probe(root) is None
        report = {
            "status": "PASS",
            "competing_resume": "refused before CLI or model",
            "model_requests": 1,
            "lease_through_teardown": "PASS",
            "after_teardown": "allowed",
            "cli_owner": json.loads((root / "ready-1.json").read_text()),
            "scope": "Same-host Linux flock admission. Lease spans CLI open, query and close; transcript append is independent. No distributed fencing.",
        }
    except Exception:
        report["traceback"] = traceback.format_exc()
        raise
    finally:
        for proc in procs:
            await native_replay.stop(proc)
        save(root / "report.json", report)
        main_recovery.record(root / "model-requests.json", api.requests, base)
        api.stop()


async def run(args):
    root = Path(args.root).resolve()
    if root.exists():
        raise ValueError("Fresh output directory required")
    root.mkdir(parents=True)
    manifest_path = (
        Path(__file__).resolve().parent / "results/native-source-manifest.json"
    )
    manifest = json.loads(manifest_path.read_text())
    assert manifest["revision"] == "2ab873cc23a1b3224531a5634c1f6d1c8ef0ea1f"
    for entry in manifest["files"]:
        source_file = Path(args.source_root) / entry["relative_path"]
        assert hashlib.sha256(source_file.read_bytes()).hexdigest() == entry["sha256"]
    versions = {
        name: importlib.metadata.version(name)
        for name in ("claude-agent-sdk", "temporalio")
    }
    assert versions == {"claude-agent-sdk": "0.2.162", "temporalio": "1.33.0"}
    assert (
        hashlib.sha256(Path(args.cli_path).read_bytes()).hexdigest()
        == "15e2d05148f801b5774032faad87e624ecd172e9903288bda448b892eb58fa07"
    )
    assert (
        hashlib.sha256(Path(args.server).read_bytes()).hexdigest()
        == "eff36463f7c0fbfcfd50f117370fc582fe964912a62cf271b91af05447d1fdfe"
    )
    save(
        root / "provenance.json",
        {
            "versions": versions,
            "python": sys.version.split()[0],
            "fixture_revision": manifest["revision"],
            "fixture_files_verified": len(manifest["files"]),
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "seed_store_sha256": hashlib.sha256(
                Path(args.seed_store).read_bytes()
            ).hexdigest(),
            "cli_sha256": hashlib.sha256(Path(args.cli_path).read_bytes()).hexdigest(),
            "server_sha256": hashlib.sha256(Path(args.server).read_bytes()).hexdigest(),
            "accounting_only": args.accounting_only,
        },
    )
    await concurrent(args, root)
    args.session = None
    main_recovery.launch_worker = launch
    main_recovery.load_supervision = lambda path: sys.modules[__name__]
    unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"])
    unrelated_identity = native_replay.identity(unrelated.pid)
    try:
        await main_recovery.temporal_case(args, root, "success")
        assert live([unrelated_identity])
        save(
            root / "supervision-control.json",
            {
                "status": "PASS",
                "unrelated_before": unrelated_identity,
                "unrelated_after": native_replay.identity(unrelated.pid),
                "scope": "Controlled tool descendant and actual CLI descendants inventoried by PID/start ticks. Replacement refuses until matching active processes are gone. No arbitrary daemon or remote-host containment claim.",
            },
        )
    except Exception:
        main_recovery.record(
            root / "failure-model-requests.json", args.active_api.requests, root
        )
        save(
            root / "summary.json",
            {
                "status": "FAILED; no completion claim",
                "accounting_only": args.accounting_only,
                "traceback": traceback.format_exc().replace(
                    str(Path(__file__).resolve().parent), "<experiments>"
                ),
            },
        )
        raise
    finally:
        if live([unrelated_identity]):
            unrelated.kill()
        unrelated.wait()
    save(
        root / "summary.json",
        {
            "status": "PASS",
            "history_replay": "PASS",
            "contracts": [
                "exclusive local admission",
                "lease through CLI teardown",
                "Worker loss orphan gate",
                "PID/start identity cleanup",
                "unrelated process survival",
                "replacement outcome reuse",
            ],
            "sdk_provided_lease": False,
            "distributed_fencing": "unexecuted",
            "arbitrary_daemon_containment": "unsupported",
        },
    )


async def main():
    parser = argparse.ArgumentParser()
    for name in ("source-root", "root", "cli-path"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--seed-store")
    parser.add_argument("--server")
    parser.add_argument("--supervision-helper")
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--mode", default="owner")
    parser.add_argument("--worker-number", type=int, default=1)
    parser.add_argument("--address")
    parser.add_argument("--queue")
    parser.add_argument("--session")
    parser.add_argument("--accounting-only", action="store_true")
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--normalize-archive", action="store_true")
    args = parser.parse_args()
    sys.path.insert(0, args.source_root)
    if args.worker:
        os.environ["HYBRID_CLI_PATH"] = args.cli_path
        sys.exit(await leased_worker(args))
    main_recovery.environment_scrub()
    if args.normalize_archive:
        if not args.archive or not Path(args.root).is_dir():
            parser.error("Normalization requires an existing scratch root and archive")
        archive_results(args, existing=True)
        return
    try:
        await run(args)
    finally:
        if args.archive:
            archive_results(args)


def archive_results(args, existing=False):
    """Normalize direct strings and JSON payloads without changing measurements."""
    archive = args.archive.resolve()
    location = Path(__file__).resolve()
    boundary = location.parent / "results/host-ownership"
    if not archive.is_relative_to(boundary.resolve()) or (
        archive.exists() and not existing
    ):
        raise ValueError("Archive must be a bounded fresh directory unless normalizing")
    archive.mkdir(parents=True, exist_ok=existing)
    scratch = Path(args.root).resolve()
    replacements = [
        (str(scratch), "<scratch>"),
        (str(location.parent), "<experiments>"),
        (str(location.parents[5]), "<repository>"),
        (str(Path(args.source_root).resolve()), "<fixture>"),
        (str(Path.home()), "<home>"),
        (socket.gethostname(), "<host>"),
    ]

    def normalize(value):
        if isinstance(value, str):
            for old, new in replacements:
                value = value.replace(old, new)
            return value
        if isinstance(value, list):
            return [normalize(item) for item in value]
        if isinstance(value, dict):
            if value.get("metadata", {}).get(
                "encoding"
            ) == "anNvbi9wbGFpbg==" and isinstance(value.get("data"), str):
                decoded = json.loads(base64.b64decode(value["data"]).decode())
                normalized = normalize(decoded)
                value = dict(value)
                if normalized != decoded:
                    value["data"] = base64.b64encode(
                        json.dumps(
                            normalized, separators=(",", ":"), sort_keys=True
                        ).encode()
                    ).decode()
            return {key: normalize(item) for key, item in value.items()}
        return value

    names = [
        "summary.json",
        "provenance.json",
        "supervision-control.json",
        "failure-model-requests.json",
        "concurrent/report.json",
        "concurrent/model-requests.json",
        "success/report.json",
        "success/history.json",
        "success/model-requests.json",
        "success/original-ledger.json",
        "success/original-pending-transcript.json",
        "success/published-transcript.json",
    ]
    for name in names:
        source = scratch / name
        if source.exists():
            destination = archive / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                json.dumps(normalize(json.loads(source.read_text())), indent=2)
            )


if __name__ == "__main__":
    asyncio.run(main())
