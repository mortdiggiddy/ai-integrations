"""Verify a fixed synthetic stream corpus against independent receipt fixtures.

This experiment does not parse an arbitrary CLI stream or establish billing.
All categories, epoch coverage and prices are explicit fixture declarations.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from budget_ledger import (
    BudgetLedger,
    BudgetLimits,
    LedgerBlocked,
    PhasePolicy,
    TokenUsage,
)

MODEL = "claude-haiku-4-5-20251001"
FIELDS = (
    "ordinary_input",
    "cache_read_input",
    "cache_write_input",
    "output",
    "thinking",
    "cost_microusd",
)
SEMANTICS = "synthetic-disjoint-input-output-includes-thinking-v1"


class Unresolved(ValueError):
    """Evidence cannot establish a complete segment delta."""


def quantities(value):
    """Require complete bounded integer accounting with known fixture semantics."""
    if not isinstance(value, dict) or set(value) != set(FIELDS):
        raise Unresolved("Incomplete or unknown charged categories")
    if any(type(n) is not int or n < 0 or n > 2**60 for n in value.values()):
        raise Unresolved("Unknown or invalid usage/currency")
    if value["thinking"] > value["output"]:
        raise Unresolved("Thinking is not an output subset")
    return value


def add(values):
    return {key: sum(value[key] for value in values) for key in FIELDS}


def normalize(state, events, receipts, *, verify_receipts=True):
    """Return deltas only for complete epochs bound to exact independent receipts."""
    identity = state["identity"]
    if state.get("semantics") != SEMANTICS or identity["model"] != MODEL:
        raise Unresolved("Unknown model/category/currency semantics")
    epochs = state["epochs"]
    seen = dict(state.get("seen", {}))
    finals = dict(state.get("finals", {}))
    for event in events:
        if event.get("identity") != identity:
            raise Unresolved("Event identity mismatch")
        event_id = event["event_id"]
        if event_id in seen:
            if seen[event_id] != event:
                raise Unresolved("Conflicting repeated response")
            continue
        seen[event_id] = event
        epoch = event.get("epoch")
        if epoch not in epochs:
            raise Unresolved("Unlabelled reset or unknown epoch")
        if event["kind"] == "preview":
            continue
        if event["kind"] != "final" or epoch in finals:
            raise Unresolved("Unknown event or conflicting final")
        if event.get("complete") is not True or event.get("crash") is not False:
            raise Unresolved("Incomplete final or crash-zero uncertainty")
        if event.get("model_usage") != [MODEL]:
            raise Unresolved("Incomplete per-model usage")
        finals[epoch] = event
    if set(finals) != set(epochs):
        raise Unresolved("Missing final/budget-crossing response or epoch coverage")
    request_ids = set()
    receipt_ids = set()
    for receipt in receipts:
        if receipt.get("identity") != identity or receipt.get("complete") is not True:
            raise Unresolved("Incomplete or misbound independent receipt")
        if receipt["request"] in receipt_ids or receipt["epoch"] not in epochs:
            raise Unresolved("Duplicate receipt or unknown epoch")
        receipt_ids.add(receipt["request"])
        quantities(receipt["delta"])
    deltas = []
    for epoch, declaration in epochs.items():
        if declaration.get("complete") is not True:
            raise Unresolved("Unproved epoch/reset coverage")
        baseline = quantities(declaration["baseline"])
        final = finals[epoch]
        ids = final["requests"]
        if len(ids) != len(set(ids)) or request_ids.intersection(ids):
            raise Unresolved("Request counted across multiple epochs")
        request_ids.update(ids)
        total = quantities(final["totals"])
        delta = {key: total[key] - baseline[key] for key in FIELDS}
        quantities(delta)
        epoch_receipts = [receipt for receipt in receipts if receipt["epoch"] == epoch]
        if verify_receipts and (
            set(ids) != {receipt["request"] for receipt in epoch_receipts}
            or delta != add([receipt["delta"] for receipt in epoch_receipts])
        ):
            raise Unresolved("Final delta differs from independent provider receipts")
        deltas.append(delta)
    if verify_receipts and request_ids != receipt_ids:
        raise Unresolved("Receipt inventory differs from final coverage")
    return add(deltas), {**state, "seen": seen, "finals": finals}


def corpus():
    """Build separate scripted stream and receipt expectations for twelve cases."""
    zero = dict.fromkeys(FIELDS, 0)
    usage = dict(zip(FIELDS, (12, 0, 0, 20, 0, 112), strict=True))
    baseline = dict(zip(FIELDS, (100, 2, 3, 40, 5, 400), strict=True))
    names = (
        "fresh-final",
        "restored-baseline",
        "streaming-cumulative",
        "identical-duplicate",
        "conflicting-duplicate",
        "complete-reset",
        "missing-reset-coverage",
        "cached-input-thinking",
        "incomplete-model-usage",
        "missing-final",
        "crash-zero",
        "unknown-semantics",
    )
    cases = []
    for name in names:
        identity = {
            "test": "offline-usage-" + name,
            "segment": "segment-1",
            "model": MODEL,
        }
        state = {
            "identity": identity,
            "semantics": SEMANTICS,
            "seen": {},
            "epochs": {"epoch-0": {"baseline": dict(zero), "complete": True}},
        }
        final = {
            "identity": identity,
            "event_id": "final-0",
            "epoch": "epoch-0",
            "kind": "final",
            "complete": True,
            "crash": False,
            "model_usage": [MODEL],
            "requests": ["request-0"],
            "totals": dict(usage),
        }
        receipt = {
            "identity": identity,
            "request": "request-0",
            "epoch": "epoch-0",
            "complete": True,
            "delta": dict(usage),
        }
        events, receipts = [final], [receipt]
        expected = dict(usage)
        if name == "restored-baseline":
            state["epochs"]["epoch-0"]["baseline"] = dict(baseline)
            final["totals"] = add([baseline, usage])
        elif name == "streaming-cumulative":
            events = [
                {**copy.deepcopy(final), "kind": "preview", "event_id": f"preview-{i}"}
                for i in range(3)
            ] + [final]
        elif name in {"identical-duplicate", "conflicting-duplicate"}:
            duplicate = copy.deepcopy(final)
            if name == "conflicting-duplicate":
                duplicate["totals"]["output"] += 1
            events.append(duplicate)
        elif name in {"complete-reset", "missing-reset-coverage"}:
            state["epochs"]["epoch-1"] = {"baseline": dict(zero), "complete": True}
            events.append(
                {
                    **copy.deepcopy(final),
                    "event_id": "final-1",
                    "epoch": "epoch-1",
                    "requests": ["request-1"],
                }
            )
            receipts.append(
                {**copy.deepcopy(receipt), "epoch": "epoch-1", "request": "request-1"}
            )
            expected = add([usage, usage])
            if name == "missing-reset-coverage":
                state["epochs"]["epoch-0"]["complete"] = False
        elif name == "cached-input-thinking":
            expected = dict(zip(FIELDS, (10, 20, 30, 40, 15, 390), strict=True))
            final["totals"] = dict(expected)
            receipt["delta"] = dict(expected)
        elif name == "incomplete-model-usage":
            final["model_usage"] = []
        elif name == "missing-final":
            events = [{**copy.deepcopy(final), "kind": "preview"}]
        elif name == "crash-zero":
            final["totals"] = dict(zero)
            final["crash"] = True
        elif name == "unknown-semantics":
            state["semantics"] = "unknown-price-category-basis"
        unresolved = name in {
            "conflicting-duplicate",
            "missing-reset-coverage",
            "incomplete-model-usage",
            "missing-final",
            "crash-zero",
            "unknown-semantics",
        }
        cases.append(
            {
                "name": name,
                "state": state,
                "events": events,
                "receipts": receipts,
                "expected": None if unresolved else expected,
            }
        )
    return cases


def worker(root):
    """Reopen durable baseline and ledger, then reconcile or retain uncertainty."""
    case = json.loads((root / "corpus.json").read_text())
    state = json.loads((root / "state.json").read_text())
    ledger = BudgetLedger(root / "ledger.sqlite3")
    identity = state["identity"]
    before = ledger.snapshot("synthetic-phase")
    delta = None
    reason = None
    try:
        delta, retained = normalize(state, case["events"], case["receipts"])
        (root / "state.json").write_text(json.dumps(retained, indent=2))
        ledger.reconcile(
            identity["test"],
            identity["segment"],
            model=MODEL,
            cost_microusd=delta["cost_microusd"],
            usage=TokenUsage(**{key: delta[key] for key in FIELDS[:-1]}),
        )
        ledger.finish(identity["test"])
        repeated, _ = normalize(
            json.loads((root / "state.json").read_text()),
            case["events"],
            case["receipts"],
        )
        assert repeated == delta
        BudgetLedger(ledger.path).reconcile(
            identity["test"],
            identity["segment"],
            model=MODEL,
            cost_microusd=repeated["cost_microusd"],
            usage=TokenUsage(**{key: repeated[key] for key in FIELDS[:-1]}),
        )
    except Unresolved as exc:
        reason = str(exc)
    blocked = False
    try:
        ledger.begin_segment(
            identity["test"],
            "replacement",
            model=MODEL,
            limits=BudgetLimits(10000, 1000, 1000, 2000),
        )
    except LedgerBlocked:
        blocked = True
    if not blocked:
        raise AssertionError("Closed or unresolved segment allowed continuation")
    assert delta == case["expected"], (case["name"], delta, case["expected"])
    after = ledger.snapshot("synthetic-phase")
    if delta is None:
        assert after == before and not ledger.segment_accounted(
            identity["test"], identity["segment"]
        )
    else:
        assert ledger.test_totals(identity["test"])["input_tokens"] == sum(
            delta[key] for key in FIELDS[:3]
        )
        assert ledger.test_totals(identity["test"])["output_tokens"] == delta["output"]
    return {
        "name": case["name"],
        "status": "passed",
        "accounting_status": "unresolved"
        if delta is None
        else "verified-synthetic-delta",
        "delta": delta,
        "reason": reason,
        "continuation_refused": blocked,
        "ledger_before": before,
        "ledger_after": after,
    }


def run(root):
    """Run the fixed corpus through replacement processes and independent controls."""
    root.mkdir()
    results = []
    for case in corpus():
        directory = root / case["name"]
        directory.mkdir()
        (directory / "corpus.json").write_text(json.dumps(case, indent=2))
        (directory / "state.json").write_text(json.dumps(case["state"], indent=2))
        ledger = BudgetLedger(directory / "ledger.sqlite3", create=True)
        limits = BudgetLimits(10000, 1000, 1000, 2000)
        ledger.configure_phase(
            "synthetic-phase", PhasePolicy(MODEL, limits, 10000, 2000)
        )
        ledger.reserve(
            case["state"]["identity"]["test"], "synthetic-phase", MODEL, limits
        )
        ledger.begin_segment(
            case["state"]["identity"]["test"], "segment-1", model=MODEL, limits=limits
        )
        child = subprocess.run(
            [sys.executable, __file__, "--worker", str(directory)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        (directory / "worker.log").write_text(child.stdout + child.stderr)
        assert child.returncode == 0, child.stderr
        result = json.loads(child.stdout)
        (directory / "report.json").write_text(json.dumps(result, indent=2))
        results.append(result)
    control = corpus()[0]
    altered = copy.deepcopy(control["events"])
    altered[0]["totals"]["cost_microusd"] += 1
    caught = False
    try:
        normalize(control["state"], altered, control["receipts"])
    except Unresolved:
        caught = True
    bypass_delta, _ = normalize(
        control["state"], altered, control["receipts"], verify_receipts=False
    )
    assert caught and bypass_delta != control["expected"]
    zero = copy.deepcopy(control)
    zero["events"][0]["requests"] = []
    zero["events"][0]["totals"] = dict.fromkeys(FIELDS, 0)
    zero_delta, _ = normalize(zero["state"], zero["events"], [])
    assert zero_delta == dict.fromkeys(FIELDS, 0)
    additional = []
    for field, value in (
        ("output", None),
        ("cost_microusd", None),
        ("ordinary_input", True),
    ):
        altered = copy.deepcopy(control["events"])
        altered[0]["totals"][field] = value
        try:
            normalize(control["state"], altered, control["receipts"])
        except Unresolved:
            additional.append(field)
        else:
            raise AssertionError("Unknown usage admitted")
    report = {
        "status": "passed",
        "cases": results,
        "synthetic_only": True,
        "controls": {
            "receipt_verification_removed_breaks_assertion": True,
            "verified_zero_without_work": True,
            "invalid_quantity_refusals": additional,
        },
        "limitations": "Fixture schema only; no arbitrary CLI adapter, provider enforcement or billing proof.",
    }
    (root / "report.json").write_text(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    if sys.argv[1] == "--worker":
        print(json.dumps(worker(Path(sys.argv[2]))))
    else:
        print(json.dumps(run(Path(sys.argv[1]))))
