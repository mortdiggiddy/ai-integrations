"""Offline process contention, retained accounting and immutable admission checks."""

from __future__ import annotations

import multiprocessing
import os
import sqlite3
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from tests.helpers.budget_ledger import (
    BudgetLedger,
    BudgetLimits,
    LedgerBlocked,
    PhasePolicy,
    TokenUsage,
)
from tests.helpers.offline_harness import HarnessConfig, OfflineHarness

MODEL = "claude-haiku-4-5-20251001"
LIMITS = BudgetLimits(1_000_000, 100_000, 8_192, 108_192)
POLICY = PhasePolicy(MODEL, LIMITS, 1_000_000, 108_192)
USAGE = TokenUsage(10, 20, 30, 40, 15)


def _ledger(tmp_path: Path) -> BudgetLedger:
    ledger = BudgetLedger(tmp_path / "budget.sqlite3", create=True)
    ledger.configure_phase("proof", POLICY)
    return ledger


def _admit(ledger: BudgetLedger, test: str = "test", segment: str = "first") -> None:
    ledger.reserve(test, "proof", MODEL, LIMITS)
    ledger.begin_segment(test, segment, model=MODEL, limits=LIMITS)


def _reconcile(ledger: BudgetLedger, segment: str = "first", **kwargs: Any) -> None:
    values: dict[str, Any] = {"model": MODEL, "cost_microusd": 100, "usage": USAGE}
    values.update(kwargs)
    ledger.reconcile("test", segment, **values)


def _contender(path: Path, test: str, barrier: Any, results: Any) -> None:
    ledger = BudgetLedger(path)
    barrier.wait(timeout=10)
    try:
        ledger.reserve(test, "proof", MODEL, LIMITS)
        results.put("admitted")
    except LedgerBlocked:
        results.put("refused")


def _lost_process(path: Path, ready: Any) -> None:
    _admit(BudgetLedger(path))
    ready.set()
    os._exit(17)


def test_independent_processes_contend_for_last_allowance(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path)
    context = multiprocessing.get_context("spawn")
    barrier = context.Barrier(2)
    results = context.Queue()
    processes = [
        context.Process(target=_contender, args=(ledger.path, str(i), barrier, results))
        for i in range(2)
    ]
    try:
        for process in processes:
            process.start()
        assert sorted(results.get(timeout=15) for _ in processes) == [
            "admitted",
            "refused",
        ]
        for process in processes:
            process.join(timeout=15)
            assert process.exitcode == 0
    finally:
        for process in processes:
            if process.is_alive():
                process.kill()
                process.join()
        results.close()
    reopened = BudgetLedger(ledger.path)
    assert reopened.snapshot("proof")["unresolved_reserved_cost_microusd"] == 1_000_000
    with pytest.raises(LedgerBlocked, match="Phase allowance"):
        reopened.reserve("third", "proof", MODEL, LIMITS)


def test_process_loss_preserves_reservation_and_blocks_replacement(
    tmp_path: Path,
) -> None:
    ledger = _ledger(tmp_path)
    context = multiprocessing.get_context("spawn")
    ready = context.Event()
    process = context.Process(target=_lost_process, args=(ledger.path, ready))
    process.start()
    try:
        assert ready.wait(timeout=15)
        process.join(timeout=15)
        assert process.exitcode == 17
    finally:
        if process.is_alive():
            process.kill()
            process.join()
    reopened = BudgetLedger(ledger.path)
    with pytest.raises(LedgerBlocked, match="Unresolved"):
        reopened.begin_segment("test", "replacement", model=MODEL, limits=LIMITS)
    with pytest.raises(LedgerBlocked, match="unresolved"):
        reopened.finish("test")
    with pytest.raises(LedgerBlocked):
        reopened.reserve("replacement", "proof", MODEL, LIMITS)
    reopened.configure_phase("phase-5", POLICY)
    with pytest.raises(ValueError, match="already reserved"):
        reopened.reserve("test", "phase-5", MODEL, LIMITS)
    assert (
        reopened.snapshot("proof")["unresolved_reserved_tokens"] == LIMITS.total_tokens
    )
    assert reopened.snapshot("phase-5")["consumed_tokens"] == 0


def test_cumulative_segments_retries_and_duplicate_reconciliation(
    tmp_path: Path,
) -> None:
    ledger = _ledger(tmp_path)
    _admit(ledger)
    for segment in ("first", "resume", "retry"):
        ledger = BudgetLedger(ledger.path)
        if segment != "first":
            ledger.begin_segment("test", segment, model=MODEL, limits=LIMITS)
        _reconcile(ledger, segment)
        _reconcile(ledger, segment)
    assert ledger.test_totals("test") == {
        "cost_microusd": 300,
        "input_tokens": 180,
        "output_tokens": 120,
        "total_tokens": 300,
    }
    snapshot = ledger.snapshot("proof")
    assert snapshot["consumed_cost_microusd"] == 300
    assert snapshot["unresolved_reserved_cost_microusd"] == 999_700
    with pytest.raises(LedgerBlocked):
        ledger.reserve("other", "proof", MODEL, LIMITS)
    ledger.finish("test")
    ledger.finish("test")
    _reconcile(ledger, "retry")
    assert ledger.snapshot("proof")["unresolved_reserved_cost_microusd"] == 0
    with pytest.raises(LedgerBlocked, match="Closed"):
        ledger.begin_segment("test", "later", model=MODEL, limits=LIMITS)


@pytest.mark.parametrize(
    "accounting",
    [
        {"usage": None},
        {"cost_microusd": None},
        {"cost_microusd": True},
        {"cost_microusd": 1.5},
        {"cost_microusd": -1},
        {"usage": TokenUsage(0, 0, 0, 5, 6)},
        {"usage": TokenUsage(-1, 0, 0, 0, 0)},
        {"usage": TokenUsage(True, 0, 0, 0, 0)},
        {"model": "haiku"},
    ],
)
def test_invalid_accounting_durably_blocks_all_admission(
    tmp_path: Path, accounting: dict[str, Any]
) -> None:
    ledger = _ledger(tmp_path)
    _admit(ledger)
    with pytest.raises(LedgerBlocked, match="Malformed"):
        _reconcile(ledger, **accounting)
    reopened = BudgetLedger(ledger.path)
    assert reopened.snapshot("proof")["unresolved_reserved_cost_microusd"] == 1_000_000
    with pytest.raises(LedgerBlocked):
        reopened.configure_phase("phase-5", POLICY)
    with pytest.raises(LedgerBlocked):
        reopened.begin_segment("test", "retry", model=MODEL, limits=LIMITS)


def test_conflicting_reconciliation_remains_blocked_after_finish(
    tmp_path: Path,
) -> None:
    ledger = _ledger(tmp_path)
    _admit(ledger)
    _reconcile(ledger)
    ledger.finish("test")
    with pytest.raises(LedgerBlocked, match="Conflicting"):
        _reconcile(ledger, cost_microusd=101)
    reopened = BudgetLedger(ledger.path)
    _reconcile(reopened)
    assert reopened.test_totals("test")["cost_microusd"] == 100
    with pytest.raises(LedgerBlocked, match="Conflicting"):
        reopened.reserve("other", "proof", MODEL, LIMITS)


@pytest.mark.parametrize(
    "accounting",
    [
        {"cost_microusd": 1_000_001},
        {"usage": TokenUsage(100_001, 0, 0, 0, 0)},
        {"usage": TokenUsage(0, 0, 0, 8_193, 0)},
        {"usage": TokenUsage(100_000, 0, 0, 8_192, 0)},
    ],
)
def test_excess_accounting_is_recorded_in_full(
    tmp_path: Path, accounting: dict[str, Any]
) -> None:
    ledger = _ledger(tmp_path)
    if "usage" in accounting and accounting["usage"].input == 100_000:
        limits = replace(LIMITS, total_tokens=100_000)
        policy = replace(POLICY, limits=limits)
        ledger.configure_phase("tight", policy)
        ledger.reserve("test", "tight", MODEL, limits)
        ledger.begin_segment("test", "first", model=MODEL, limits=limits)
    else:
        _admit(ledger)
    with pytest.raises(LedgerBlocked, match="exceeds"):
        _reconcile(ledger, **accounting)
    reopened = BudgetLedger(ledger.path)
    if "cost_microusd" in accounting:
        assert reopened.test_totals("test")["cost_microusd"] == 1_000_001
    else:
        assert (
            reopened.test_totals("test")["total_tokens"]
            == accounting["usage"].input + accounting["usage"].output
        )
    with pytest.raises(LedgerBlocked):
        reopened.begin_segment("test", "retry", model=MODEL, limits=LIMITS)


def test_model_caps_and_phase_binding_cannot_change(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path)
    for model, limits in (
        ("haiku", LIMITS),
        (MODEL, replace(LIMITS, cost_microusd=2_000_000)),
    ):
        with pytest.raises(ValueError, match="Model or limits"):
            ledger.reserve("test", "proof", model, limits)
    _admit(ledger)
    with pytest.raises(ValueError, match="immutable"):
        ledger.configure_phase("proof", replace(POLICY, cost_microusd=20_000_000))
    with pytest.raises(ValueError, match="Model or limits"):
        ledger.begin_segment("test", "retry", model="haiku", limits=LIMITS)
    with pytest.raises(ValueError, match="already reserved"):
        ledger.reserve("test", "proof", MODEL, LIMITS)


def test_separate_phase_allocations_do_not_refund_old_reservations(
    tmp_path: Path,
) -> None:
    ledger = _ledger(tmp_path)
    _admit(ledger)
    ledger.configure_phase("phase-5", POLICY)
    ledger.reserve("acceptance", "phase-5", MODEL, LIMITS)
    assert ledger.snapshot("proof")["unresolved_reserved_cost_microusd"] == 1_000_000
    assert ledger.snapshot("phase-5")["unresolved_reserved_cost_microusd"] == 1_000_000


def test_missing_storage_is_not_recreated(tmp_path: Path) -> None:
    with pytest.raises(sqlite3.OperationalError):
        BudgetLedger(tmp_path / "missing.sqlite3")
    ledger = _ledger(tmp_path)
    with pytest.raises(FileExistsError):
        BudgetLedger(ledger.path, create=True)


async def test_harness_cumulative_cap_refuses_before_simulated_transport(
    tmp_path: Path,
) -> None:
    config = HarnessConfig(Path(__file__).resolve(), MODEL, "ANTHROPIC_API_KEY", 1, 100)
    harness = OfflineHarness(config, tmp_path, initialize_ledger=True)
    first = await harness.run(prompt="first", input_tokens=40, output_tokens=10)
    assert first.status == "passed"
    reopened = OfflineHarness(config, tmp_path)
    second = await reopened.run(prompt="retry", input_tokens=40, output_tokens=10)
    assert second.status == "cap_reached"
    assert (
        second.cumulative_usage is not None
        and second.cumulative_usage["total_tokens"] == 100
    )
    replacement = OfflineHarness(config, tmp_path)
    with pytest.raises(LedgerBlocked, match="exhausted"):
        await replacement.run(prompt="refused")
    assert replacement.observed_options is None
    assert replacement.last_record is None


async def test_timeout_retains_unknown_accounting(tmp_path: Path) -> None:
    config = HarnessConfig(Path(__file__).resolve(), MODEL, "ANTHROPIC_API_KEY", 1, 100)
    harness = OfflineHarness(config, tmp_path, initialize_ledger=True)
    with pytest.raises(TimeoutError):
        await harness.run(prompt="lost", timeout=True)
    assert harness.last_record is not None and harness.last_record.cost_usd is None
    assert (
        harness.ledger.snapshot("offline-proof")["unresolved_reserved_cost_microusd"]
        == 1_000_000
    )
    with pytest.raises(LedgerBlocked, match="Unresolved"):
        await OfflineHarness(config, tmp_path).run(prompt="replacement")


@pytest.mark.parametrize(
    "policy",
    [
        replace(POLICY, cost_microusd=999_999, total_tokens=1_000_000),
        replace(POLICY, cost_microusd=20_000_000, total_tokens=108_191),
    ],
)
def test_insufficient_phase_allowance_refuses_transport(
    tmp_path: Path, policy: PhasePolicy
) -> None:
    ledger = BudgetLedger(tmp_path / "budget.sqlite3", create=True)
    ledger.configure_phase("proof", policy)
    with pytest.raises(LedgerBlocked, match="Phase allowance"):
        ledger.reserve("test", "proof", MODEL, LIMITS)
    assert ledger.snapshot("proof")["consumed_tokens"] == 0
    assert ledger.snapshot("proof")["unresolved_reserved_tokens"] == 0


def test_harness_replacement_cannot_change_phase(tmp_path: Path) -> None:
    config = HarnessConfig(Path(__file__).resolve(), MODEL, "ANTHROPIC_API_KEY", 1, 100)
    OfflineHarness(config, tmp_path, initialize_ledger=True)
    with pytest.raises(ValueError, match="binding"):
        OfflineHarness(config, tmp_path, phase="phase-5")


async def test_harness_token_categories_and_thinking_subset(tmp_path: Path) -> None:
    config = HarnessConfig(Path(__file__).resolve(), MODEL, "ANTHROPIC_API_KEY", 1, 200)
    harness = OfflineHarness(config, tmp_path, initialize_ledger=True)
    record = await harness.run(
        prompt="categories",
        input_tokens=10,
        cache_read_tokens=20,
        cache_write_tokens=30,
        output_tokens=40,
        thinking_tokens=15,
    )
    assert record.input_tokens == 60
    assert record.output_tokens == 40
    assert record.token_categories == {
        "ordinary_input": 10,
        "cache_read_input": 20,
        "cache_write_input": 30,
        "output": 40,
        "thinking": 15,
    }
    assert (
        record.cumulative_usage is not None
        and record.cumulative_usage["total_tokens"] == 100
    )


async def test_malformed_harness_accounting_blocks_new_admission(
    tmp_path: Path,
) -> None:
    config = HarnessConfig(Path(__file__).resolve(), MODEL, "ANTHROPIC_API_KEY", 1, 100)
    harness = OfflineHarness(config, tmp_path, initialize_ledger=True)
    with pytest.raises(LedgerBlocked, match="Malformed"):
        await harness.run(prompt="bad", input_tokens=-1)
    assert harness.last_record is not None and harness.last_record.cost_usd is None
    assert harness.observed_options is None
    with pytest.raises(LedgerBlocked):
        OfflineHarness(config, tmp_path)


async def test_cost_conversion_rounds_up_without_losing_micro_units(
    tmp_path: Path,
) -> None:
    config = HarnessConfig(Path(__file__).resolve(), MODEL, "ANTHROPIC_API_KEY", 1, 100)
    harness = OfflineHarness(config, tmp_path, initialize_ledger=True)
    await harness.run(prompt="rounding", cost_usd=0.0000001)
    assert harness.ledger.test_totals("offline-test")["cost_microusd"] == 1


def test_unknown_reconciliation_identity_blocks_admission(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path)
    _admit(ledger)
    with pytest.raises(LedgerBlocked, match="Malformed"):
        ledger.reconcile("unknown", "first", model=MODEL, cost_microusd=1, usage=USAGE)
    with pytest.raises(LedgerBlocked):
        BudgetLedger(ledger.path).reserve("other", "proof", MODEL, LIMITS)
