"""Exercise only a confined loopback Messages route with synthetic admission.

The provider receipt protocol is a fixture control, not an Anthropic feature.
SQLite stores on one host and cooperating processes are the only topology.
"""

from __future__ import annotations

import asyncio
import hashlib
import http.client
import importlib.util
import json
import os
import signal
import sqlite3
import subprocess
import sys
import threading
import time
import uuid
from contextlib import closing
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from budget_ledger import BudgetLedger, BudgetLimits, LedgerBlocked, PhasePolicy
from claude_agent_sdk import ClaudeAgentOptions, query

MODEL = "claude-haiku-4-5-20251001"
CASES = (
    "ordinary",
    "internal-continuation",
    "internal-retry",
    "insufficient",
    "last-allowance-contention",
    "gateway-faults",
    "loss-after-admission",
    "bypass",
)
LIMITS = BudgetLimits(10000, 1000, 1000, 2000)
ENVELOPE = {"input": 12, "output": 64, "cost_microusd": 332}


def write(path, value):
    path.write_text(json.dumps(value, indent=2))


def helper():
    spec = importlib.util.spec_from_file_location(
        "fake_messages_fixture", "/fixtures/fake_messages_api.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def post(port, body, receipt=None):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
    try:
        headers = {"Content-Type": "application/json"}
        if receipt:
            headers["X-Fixture-Receipt"] = receipt
        connection.request(
            "POST", "/v1/messages", body=json.dumps(body), headers=headers
        )
        response = connection.getresponse()
        return response.status, response.getheader("content-type"), response.read()
    finally:
        connection.close()


def digest(body):
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


class Route:
    """Reserve request envelopes before a separate provider consumes receipts."""

    def __init__(self, root, name, allowance=3):
        self.root, self.name, self.allowance = root, name, allowance
        self.fault = None
        self.require_receipts = True
        self.provider_count = 0
        self.receipts = []
        self.receipt_lock = threading.Lock()
        self.db = root / "requests.sqlite3"
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute("PRAGMA synchronous=FULL")
            db.execute(
                "CREATE TABLE admissions (id TEXT PRIMARY KEY, body TEXT, binding TEXT, used INTEGER, admitted_ns INTEGER)"
            )
        self.binding = {
            "test": "offline-request-" + name,
            "segment": "segment-1",
            "phase": "synthetic-phase",
            "model": MODEL,
            "caps": asdict(LIMITS),
            "envelope": ENVELOPE,
        }
        write(root / "binding.json", self.binding)
        self.ledger = BudgetLedger(root / "ledger.sqlite3", create=True)
        self.ledger.configure_phase(
            "synthetic-phase", PhasePolicy(MODEL, LIMITS, 10000, 2000)
        )
        self.ledger.reserve(self.binding["test"], "synthetic-phase", MODEL, LIMITS)
        self.ledger.begin_segment(
            self.binding["test"], "segment-1", model=MODEL, limits=LIMITS
        )
        self.before = self.ledger.snapshot("synthetic-phase")
        self.fake = helper().FakeMessagesAPI(lambda body: [])
        route = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def send_json(self, payload, status=200):
                data = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_POST(self):
                body = json.loads(
                    self.rfile.read(int(self.headers.get("Content-Length", 0)))
                )
                if self.server.role == "provider":
                    return route.provider(self, body)
                if self.path.split("?")[0] != "/v1/messages":
                    return self.send_json({"error": "unsupported endpoint"}, 400)
                if route.fault in {"reject", "crash"}:
                    if route.fault == "crash":
                        self.close_connection = True
                        return
                    return self.send_json({"error": "admission unavailable"}, 403)
                if route.fault == "timeout":
                    time.sleep(0.2)
                    return self.send_json({"error": "admission timed out"}, 403)
                try:
                    receipt = route.admit(body)
                except ValueError as exc:
                    return self.send_json(
                        {
                            "type": "error",
                            "error": {
                                "type": "invalid_request_error",
                                "message": str(exc),
                            },
                        },
                        400,
                    )
                if route.fault == "loss":
                    self.close_connection = True
                    return
                status, content_type, data = post(
                    route.provider_server.server_port, body, receipt
                )
                self.send_response(status)
                self.send_header("Content-Type", content_type or "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self.provider_server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.provider_server.role = "provider"
        self.gateway_server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.gateway_server.role = "gateway"
        for server in (self.provider_server, self.gateway_server):
            threading.Thread(target=server.serve_forever, daemon=True).start()

    def admit(self, body):
        if (
            body.get("model") != MODEL
            or type(body.get("max_tokens")) is not int
            or not 0 < body["max_tokens"] <= 64
        ):
            raise ValueError("Model or output envelope mismatch")
        with closing(sqlite3.connect(self.db, timeout=2)) as db, db:
            db.execute("PRAGMA synchronous=FULL")
            db.execute("BEGIN IMMEDIATE")
            count = db.execute("SELECT count(*) FROM admissions").fetchone()[0]
            if count >= self.allowance:
                raise ValueError("Insufficient cumulative request envelope")
            request_id = str(uuid.uuid4())
            db.execute(
                "INSERT INTO admissions VALUES (?,?,?,?,?)",
                (
                    request_id,
                    digest(body),
                    json.dumps(self.binding, sort_keys=True),
                    0,
                    time.monotonic_ns(),
                ),
            )
        return request_id

    def provider(self, handler, body):
        received_ns = time.monotonic_ns()
        receipt = handler.headers.get("X-Fixture-Receipt")
        accepted = False
        admission = None
        with closing(sqlite3.connect(self.db, timeout=2)) as db, db:
            db.execute("BEGIN IMMEDIATE")
            admission = db.execute(
                "SELECT * FROM admissions WHERE id=?", (receipt,)
            ).fetchone()
            if (
                admission
                and admission[1] == digest(body)
                and admission[2] == json.dumps(self.binding, sort_keys=True)
                and admission[3] == 0
            ):
                db.execute("UPDATE admissions SET used=1 WHERE id=?", (receipt,))
                accepted = True
        with self.receipt_lock:
            if len(self.receipts) >= 40:
                raise RuntimeError("Fake provider receipt bound exceeded")
            self.receipts.append(
                {
                    "received_ns": received_ns,
                    "receipt": receipt,
                    "body": body,
                    "accepted": accepted,
                    "admitted_ns": admission[4] if admission else None,
                    "synthetic_input": 12 if accepted else None,
                    "synthetic_output": 20 if accepted else None,
                    "synthetic_price_basis": "input=1/output=5 micro USD per synthetic token",
                }
            )
            if accepted:
                self.provider_count += 1
            number = self.provider_count
        if not self.require_receipts:
            accepted = True
            self.receipts[-1]["accepted"] = True
            self.provider_count += 1
        if not accepted:
            return handler.send_json(
                {"error": "missing, forged, replayed or mismatched admission receipt"},
                403,
            )
        if self.name == "internal-retry" and number == 1:
            return handler.send_json(
                {
                    "type": "error",
                    "error": {"type": "overloaded_error", "message": "synthetic retry"},
                },
                529,
            )
        if self.name == "internal-continuation" and number == 1:
            events = [
                {
                    "type": "message_start",
                    "message": {
                        "id": "msg_limit",
                        "type": "message",
                        "role": "assistant",
                        "model": MODEL,
                        "content": [],
                        "stop_reason": None,
                        "stop_sequence": None,
                        "usage": {
                            "input_tokens": 12,
                            "output_tokens": 1,
                            "cache_creation_input_tokens": 0,
                            "cache_read_input_tokens": 0,
                        },
                    },
                },
                {
                    "type": "content_block_start",
                    "index": 0,
                    "content_block": {"type": "text", "text": ""},
                },
                {
                    "type": "content_block_delta",
                    "index": 0,
                    "delta": {"type": "text_delta", "text": "partial"},
                },
                {"type": "content_block_stop", "index": 0},
                {
                    "type": "message_delta",
                    "delta": {"stop_reason": "max_tokens", "stop_sequence": None},
                    "usage": {"output_tokens": 20},
                },
                {"type": "message_stop"},
            ]
            handler.send_response(200)
            handler.send_header("Content-Type", "text/event-stream")
            handler.send_header("Connection", "close")
            handler.end_headers()
            for event in events:
                handler.wfile.write(
                    f"event: {event['type']}\ndata: {json.dumps(event)}\n\n".encode()
                )
            handler.wfile.flush()
            handler.close_connection = True
            return
        self.fake.write(handler, body, [{"type": "text", "text": "OFFLINE_OK"}])

    def close(self):
        for server in (self.gateway_server, self.provider_server):
            server.shutdown()
            server.server_close()
        with closing(sqlite3.connect(self.db)) as db:
            admissions = [
                dict(
                    zip(
                        ("request", "body_digest", "binding", "used", "admitted_ns"),
                        row,
                        strict=True,
                    )
                )
                for row in db.execute("SELECT * FROM admissions ORDER BY admitted_ns")
            ]
        write(self.root / "admissions.json", admissions)
        write(self.root / "provider-receipts.json", self.receipts)
        write(
            self.root / "ledger.json",
            {"before": self.before, "after": self.ledger.snapshot("synthetic-phase")},
        )
        assert all(
            not receipt["accepted"]
            or receipt.get("negative_control")
            or receipt["admitted_ns"] < receipt["received_ns"]
            for receipt in self.receipts
        )
        try:
            BudgetLedger(self.ledger.path).begin_segment(
                self.binding["test"], "replacement", model=MODEL, limits=LIMITS
            )
        except LedgerBlocked:
            pass
        else:
            raise AssertionError("Unresolved request accounting allowed replacement")
        return admissions


async def cli_case(
    route, *, label="engine", endpoint_port=None, model=MODEL, inherited_selection=False
):
    root = route.root / label
    root.mkdir()
    for name in ("home", "config", "work"):
        (root / name).mkdir()
    env = {
        "PATH": "/opt/python/bin:/usr/bin:/bin",
        "HOME": str(root / "home"),
        "TMPDIR": "/tmp",
        "PYTHONPATH": "/opt/packages:/fixtures",
        "PYTHONDONTWRITEBYTECODE": "1",
        "UV_NO_SYNC": "1",
        "UV_NO_EDITABLE": "1",
        "CLAUDE_CONFIG_DIR": str(root / "config"),
        "ANTHROPIC_BASE_URL": f"http://127.0.0.1:{endpoint_port or route.gateway_server.server_port}",
        "ANTHROPIC_API_KEY": "offline-synthetic-not-a-key",
        "DISABLE_TELEMETRY": "1",
        "DISABLE_ERROR_REPORTING": "1",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "64",
        "CLAUDE_CODE_MAX_RETRIES": "1" if route.name == "internal-retry" else "0",
        "NO_PROXY": "127.0.0.1,localhost",
    }
    if inherited_selection:
        os.environ.update(
            {
                "ANTHROPIC_BASE_URL": f"http://127.0.0.1:{route.provider_server.server_port}",
                "CLAUDE_CODE_USE_BEDROCK": "1",
                "HTTPS_PROXY": "http://127.0.0.1:1",
            }
        )
    os.environ.clear()
    os.environ.update(env)
    stream, stderr = [], []
    options = ClaudeAgentOptions(
        cli_path="/opt/claude",
        cwd=str(root / "work"),
        model=model,
        tools=[],
        allowed_tools=[],
        skills=[],
        setting_sources=[],
        mcp_servers='{"mcpServers":{}}',
        strict_mcp_config=True,
        system_prompt="Return OFFLINE_OK.",
        permission_mode="default",
        max_turns=1,
        env=env,
        stderr=stderr.append,
        include_partial_messages=True,
        extra_args={
            "bare": None,
            "disable-slash-commands": None,
            "no-chrome": None,
            "no-session-persistence": None,
            "prompt-suggestions": "false",
        },
    )
    generator = query(prompt="Return OFFLINE_OK.", options=options)
    error = None
    try:
        async for message in generator:
            stream.append({"type": type(message).__name__, "data": asdict(message)})
    except Exception as exc:
        error = type(exc).__name__ + ": " + str(exc)
    finally:
        await generator.aclose()
        write(root / "stream.json", stream)
        write(root / "stderr.json", stderr)
    return {"sdk_error": error, "stream_events": len(stream)}


def run(root, *, loss_only=False, faults_only=False):
    """Run named cases sequentially; stop this arm on the first failed prevention."""
    root.mkdir()
    reports = []
    receipt_total = 0
    selected_cases = (
        ("loss-after-admission",)
        if loss_only
        else (("gateway-faults",) if faults_only else CASES)
    )
    for name in selected_cases:

        def case_timeout(signum, frame):
            raise TimeoutError("60 second request-case bound")

        signal.signal(signal.SIGALRM, case_timeout)
        signal.alarm(60)
        case_started = time.monotonic()
        directory = root / name
        directory.mkdir()
        route = Route(
            directory,
            name,
            allowance=0
            if name == "insufficient"
            else (1 if name == "last-allowance-contention" else 3),
        )
        outcome = {"name": name, "status": "passed", "synthetic_only": True}
        try:
            body = {
                "model": MODEL,
                "max_tokens": 64,
                "stream": False,
                "messages": [{"role": "user", "content": "offline"}],
            }
            if name in {
                "ordinary",
                "internal-continuation",
                "internal-retry",
                "insufficient",
            }:
                outcome.update(
                    asyncio.run(asyncio.wait_for(cli_case(route), timeout=55))
                )
                expected = {
                    "ordinary": 1,
                    "internal-continuation": 2,
                    "internal-retry": 2,
                    "insufficient": 0,
                }[name]
                assert route.provider_count == expected, (
                    "provider receipt count",
                    route.provider_count,
                    expected,
                )
                if name != "insufficient":
                    assert outcome["sdk_error"] is None, outcome
            elif name == "last-allowance-contention":
                children = [
                    subprocess.Popen(
                        [
                            sys.executable,
                            __file__,
                            "--post",
                            str(route.gateway_server.server_port),
                            json.dumps(body),
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    for _ in range(2)
                ]
                statuses = []
                for child in children:
                    stdout, stderr = child.communicate(timeout=10)
                    assert child.returncode == 0, stderr
                    statuses.append(int(stdout))
                assert sorted(statuses) == [200, 400] and route.provider_count == 1
                outcome["process_statuses"] = statuses
            elif name == "gateway-faults":
                refused = []
                for fault in ("reject", "timeout", "crash"):
                    route.fault = fault
                    try:
                        status, _, _ = post(route.gateway_server.server_port, body)
                        assert status == 403
                    except http.client.RemoteDisconnected:
                        assert fault == "crash"
                    refused.append(fault)
                with closing(__import__("socket").socket()) as unused:
                    unused.bind(("127.0.0.1", 0))
                    absent_port = unused.getsockname()[1]
                try:
                    post(absent_port, body)
                except ConnectionRefusedError:
                    refused.append("absent")
                assert len(refused) == 4 and route.provider_count == 0
                outcome["refusals"] = refused
                crash = subprocess.Popen(
                    [sys.executable, __file__, "--crash-gateway"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                crash_port = int(crash.stdout.readline())
                try:
                    post(crash_port, body)
                except http.client.RemoteDisconnected:
                    pass
                else:
                    raise AssertionError("Gateway process crash did not refuse")
                crash_stdout, crash_stderr = crash.communicate(timeout=5)
                assert crash.returncode == -signal.SIGKILL, crash_stderr
                connection = http.client.HTTPConnection(
                    "127.0.0.1", route.provider_server.server_port, timeout=3
                )
                try:
                    connection.request("GET", "/fixture-liveness")
                    liveness = connection.getresponse()
                    assert liveness.status == 501
                    liveness.read()
                finally:
                    connection.close()
                assert route.provider_count == 0 and route.receipts == []
                outcome["whole_gateway_process_crash"] = {
                    "exit_code": crash.returncode,
                    "independent_provider_alive": True,
                    "provider_receipts": 0,
                    "waited_before_next_case": True,
                }
            elif name == "loss-after-admission":
                child = subprocess.Popen(
                    [
                        sys.executable,
                        __file__,
                        "--admit-loss",
                        str(directory),
                        json.dumps(body),
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                stdout, stderr = child.communicate(timeout=10)
                assert child.returncode == -signal.SIGKILL and stdout.strip(), stderr
                with closing(sqlite3.connect(route.db)) as db:
                    retained = db.execute("SELECT id,used FROM admissions").fetchall()
                assert retained == [(stdout.strip(), 0)]
                outcome["lost_process"] = {
                    "exit_code": child.returncode,
                    "request": stdout.strip(),
                    "waited_before_replacement": True,
                    "durable_admission_retained": True,
                }
                assert route.provider_count == 0
            else:
                port = route.provider_server.server_port
                for receipt in (None, "forged"):
                    assert post(port, body, receipt)[0] == 403
                receipt = route.admit(body)
                assert post(port, {**body, "model": "haiku"}, receipt)[0] == 403
                assert post(port, body, receipt)[0] == 200
                assert post(port, body, receipt)[0] == 403
                assert (
                    post(route.gateway_server.server_port, {**body, "model": "haiku"})[
                        0
                    ]
                    == 400
                )
                direct = asyncio.run(
                    asyncio.wait_for(
                        cli_case(route, label="changed-endpoint", endpoint_port=port),
                        timeout=15,
                    )
                )
                assert direct["sdk_error"] and route.provider_count == 1
                changed_model = asyncio.run(
                    asyncio.wait_for(
                        cli_case(
                            route, label="changed-model", model="claude-sonnet-4-6"
                        ),
                        timeout=15,
                    )
                )
                assert changed_model["sdk_error"] and route.provider_count == 1
                inherited = asyncio.run(
                    asyncio.wait_for(
                        cli_case(
                            route, label="inherited-selection", inherited_selection=True
                        ),
                        timeout=15,
                    )
                )
                assert inherited["sdk_error"] is None and route.provider_count == 2
                outcome["endpoint_bypass"] = direct
                outcome["changed_model"] = changed_model
                outcome["inherited_selection"] = inherited
                negative_root = directory / "negative-control"
                negative_root.mkdir()
                negative_route = Route(
                    negative_root, "fresh-negative-control", allowance=0
                )
                negative_route.require_receipts = False
                assert post(negative_route.provider_server.server_port, body)[0] == 200
                negative = negative_route.receipts[-1]
                prevention_assertion_broken = (
                    negative["accepted"] and negative["admitted_ns"] is None
                )
                assert prevention_assertion_broken
                negative["negative_control"] = True
                negative_route.close()
                outcome["negative_control"] = (
                    "receipt requirement removed: provider accepted unadmitted work, prevention assertion broke"
                )
                outcome["negative_control_receipts"] = len(negative_route.receipts)
        except Exception as exc:
            outcome["status"] = "failed"
            outcome["reason"] = type(exc).__name__ + ": " + str(exc)
        finally:
            admissions = route.close()
            outcome["admissions"] = len(admissions)
            outcome["provider_receipts"] = len(route.receipts)
            outcome["accepted_provider_requests"] = route.provider_count
            outcome["cleanup"] = (
                "servers closed; unresolved ledger retained; no replacement admitted"
            )
            outcome["elapsed_seconds"] = time.monotonic() - case_started
            signal.alarm(0)
            write(directory / "report.json", outcome)
        reports.append(outcome)
        receipt_total += len(route.receipts) + outcome.get(
            "negative_control_receipts", 0
        )
        assert receipt_total <= 40
        if outcome["status"] != "passed":
            reports.extend(
                {
                    "name": later,
                    "status": "unexecuted",
                    "reason": "request arm stopped after failure",
                }
                for later in selected_cases[len(reports) :]
            )
            break
    report = {
        "status": "passed"
        if all(case["status"] == "passed" for case in reports)
        else "failed",
        "cases": reports,
        "provider_receipts": receipt_total,
        "limits": "Confined synthetic API route only; subscription routing, real tokens, currency and billing unproved.",
    }
    write(root / "report.json", report)
    return report


if __name__ == "__main__":
    if sys.argv[1] == "--post":
        print(post(int(sys.argv[2]), json.loads(sys.argv[3]))[0])
    elif sys.argv[1] == "--admit-loss":
        retained_root = Path(sys.argv[2])
        retained_route = Route.__new__(Route)
        retained_route.db = retained_root / "requests.sqlite3"
        retained_route.binding = json.loads(
            (retained_root / "binding.json").read_text()
        )
        retained_route.allowance = 3
        print(retained_route.admit(json.loads(sys.argv[3])), flush=True)
        os.kill(os.getpid(), signal.SIGKILL)
    elif sys.argv[1] == "--crash-gateway":

        class CrashGateway(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                os.kill(os.getpid(), signal.SIGKILL)

        crash_server = ThreadingHTTPServer(("127.0.0.1", 0), CrashGateway)
        print(crash_server.server_port, flush=True)
        crash_server.serve_forever()
    else:
        print(
            json.dumps(
                run(
                    Path(sys.argv[1]),
                    loss_only="--loss-only" in sys.argv[2:],
                    faults_only="--faults-only" in sys.argv[2:],
                )
            )
        )
