"""Persistent accounting for offline fixtures on one host with local SQLite storage.

This ledger admits simulated work only. It cannot enforce provider requests or
account spend, supervise processes, or recover a deleted/rolled back database.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, NoReturn


class LedgerBlocked(RuntimeError):
    """Accounting uncertainty or a limit prevents further admission."""


def _integer(value: Any, *, positive: bool = False) -> None:
    if type(value) is not int or not (int(positive) <= value <= 2**60):
        raise ValueError("Accounting requires bounded nonnegative integers")


def _identity(value: str) -> None:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError("An exact nonempty identity is required")


@dataclass(frozen=True)
class BudgetLimits:
    """Immutable logical test limits, in micro USD and cumulative tokens."""

    cost_microusd: int
    input_tokens: int
    output_tokens: int
    total_tokens: int

    def validate(self) -> None:
        """Reject invalid integer limits."""
        for value in asdict(self).values():
            _integer(value, positive=True)


@dataclass(frozen=True)
class PhasePolicy:
    """Offline example policy; this object grants no live allocation."""

    model: str
    limits: BudgetLimits
    cost_microusd: int
    total_tokens: int

    def validate(self) -> None:
        """Require exact model identity and positive integer phase limits."""
        _identity(self.model)
        self.limits.validate()
        _integer(self.cost_microusd, positive=True)
        _integer(self.total_tokens, positive=True)


@dataclass(frozen=True)
class TokenUsage:
    """Disjoint input categories and output inclusive of its thinking subset."""

    ordinary_input: int
    cache_read_input: int
    cache_write_input: int
    output: int
    thinking: int

    def validate(self) -> None:
        """Reject missing, negative or ambiguous category accounting."""
        for value in asdict(self).values():
            _integer(value)
        if self.thinking > self.output:
            raise ValueError("Thinking must be a subset of output")

    @property
    def input(self) -> int:
        """Return input charged once per disjoint category."""
        return self.ordinary_input + self.cache_read_input + self.cache_write_input


class BudgetLedger:
    """Serialize admissions with SQLite BEGIN IMMEDIATE and durable commits.

    All participants must use the same retained database on one host and a local
    filesystem with working SQLite locks/fsync. Network mounts, distributed
    fencing, hostile writers and storage rollback are outside this contract.
    """

    def __init__(self, path: Path, *, create: bool = False) -> None:
        """Open retained storage; initialization must be explicitly requested."""
        self.path = path.resolve()
        if create:
            with self.path.open("xb"):
                pass
        with (
            closing(sqlite3.connect(f"{self.path.as_uri()}?mode=rw", uri=True)) as db,
            db,
        ):
            db.execute("PRAGMA synchronous=FULL")
            db.execute("BEGIN IMMEDIATE")
            if create:
                db.execute(
                    "CREATE TABLE IF NOT EXISTS ledger "
                    "(id INTEGER PRIMARY KEY CHECK(id=1), state TEXT NOT NULL)"
                )
                db.execute(
                    "INSERT OR IGNORE INTO ledger VALUES (1, ?)",
                    (
                        json.dumps(
                            {"version": 1, "blocked": None, "phases": {}, "tests": {}}
                        ),
                    ),
                )
            self._read(db)

    @staticmethod
    def _read(db: sqlite3.Connection) -> dict[str, Any]:
        row = db.execute("SELECT state FROM ledger WHERE id=1").fetchone()
        if row is None:
            raise LedgerBlocked("Missing ledger state")
        state = json.loads(row[0])
        if (
            not isinstance(state, dict)
            or state.get("version") != 1
            or set(state) != {"version", "blocked", "phases", "tests"}
            or not isinstance(state["phases"], dict)
            or not isinstance(state["tests"], dict)
        ):
            raise LedgerBlocked("Invalid ledger state")
        return state

    @contextmanager
    def _transaction(self) -> Iterator[dict[str, Any]]:
        with (
            closing(
                sqlite3.connect(f"{self.path.as_uri()}?mode=rw", uri=True, timeout=10)
            ) as db,
            db,
        ):
            db.execute("PRAGMA synchronous=FULL")
            db.execute("BEGIN IMMEDIATE")
            state = self._read(db)
            try:
                yield state
            except LedgerBlocked:
                db.execute("UPDATE ledger SET state=? WHERE id=1", (json.dumps(state),))
                db.commit()
                raise
            db.execute("UPDATE ledger SET state=? WHERE id=1", (json.dumps(state),))

    @staticmethod
    def _ready(state: dict[str, Any]) -> None:
        if state["blocked"] is not None:
            raise LedgerBlocked(state["blocked"])

    @staticmethod
    def _block(state: dict[str, Any], reason: str) -> NoReturn:
        state["blocked"] = reason
        raise LedgerBlocked(reason)

    def configure_phase(self, phase: str, policy: PhasePolicy) -> None:
        """Register a separate phase once; changed limits or model refuse."""
        _identity(phase)
        policy.validate()
        payload = asdict(policy)
        with self._transaction() as state:
            self._ready(state)
            if phase in state["phases"] and state["phases"][phase] != payload:
                raise ValueError("Phase policy is immutable")
            state["phases"][phase] = payload

    @staticmethod
    def _totals(test: dict[str, Any]) -> dict[str, int]:
        total = {
            "cost_microusd": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }
        for segment in test["segments"].values():
            if segment is None:
                continue
            usage = TokenUsage(**segment["usage"])
            total["cost_microusd"] += segment["cost_microusd"]
            total["input_tokens"] += usage.input
            total["output_tokens"] += usage.output
            total["total_tokens"] += usage.input + usage.output
        return total

    @classmethod
    def _phase_totals(cls, state: dict[str, Any], phase: str) -> dict[str, int]:
        totals = {
            "consumed_cost_microusd": 0,
            "consumed_tokens": 0,
            "unresolved_reserved_cost_microusd": 0,
            "unresolved_reserved_tokens": 0,
        }
        for test in state["tests"].values():
            if test["phase"] != phase:
                continue
            used = cls._totals(test)
            totals["consumed_cost_microusd"] += used["cost_microusd"]
            totals["consumed_tokens"] += used["total_tokens"]
            if not test["closed"]:
                totals["unresolved_reserved_cost_microusd"] += max(
                    0, test["limits"]["cost_microusd"] - used["cost_microusd"]
                )
                totals["unresolved_reserved_tokens"] += max(
                    0, test["limits"]["total_tokens"] - used["total_tokens"]
                )
        return totals

    def reserve(
        self, test_id: str, phase: str, model: str, limits: BudgetLimits
    ) -> None:
        """Reserve a whole logical test once, without refunding unknown usage."""
        for identity in (test_id, phase, model):
            _identity(identity)
        limits.validate()
        with self._transaction() as state:
            self._ready(state)
            policy = state["phases"][phase]
            if model != policy["model"] or asdict(limits) != policy["limits"]:
                raise ValueError("Model or limits differ from immutable phase policy")
            if test_id in state["tests"]:
                raise ValueError("Logical test identity is already reserved")
            totals = self._phase_totals(state, phase)
            if (
                totals["consumed_cost_microusd"]
                + totals["unresolved_reserved_cost_microusd"]
                + limits.cost_microusd
                > policy["cost_microusd"]
                or totals["consumed_tokens"]
                + totals["unresolved_reserved_tokens"]
                + limits.total_tokens
                > policy["total_tokens"]
            ):
                raise LedgerBlocked("Phase allowance exhausted")
            state["tests"][test_id] = {
                "phase": phase,
                "model": model,
                "limits": asdict(limits),
                "closed": False,
                "segments": {},
            }

    def begin_segment(
        self, test_id: str, segment_id: str, *, model: str, limits: BudgetLimits
    ) -> None:
        """Admit a segment or retry only after all earlier usage is accounted."""
        _identity(test_id)
        _identity(segment_id)
        _identity(model)
        limits.validate()
        with self._transaction() as state:
            self._ready(state)
            test = state["tests"][test_id]
            if model != test["model"] or asdict(limits) != test["limits"]:
                raise ValueError("Model or limits differ from reservation")
            if test["closed"] or segment_id in test["segments"]:
                raise LedgerBlocked("Closed test or reused segment identity")
            if any(segment is None for segment in test["segments"].values()):
                raise LedgerBlocked("Unresolved segment accounting")
            if any(
                self._totals(test)[key] >= cap for key, cap in test["limits"].items()
            ):
                raise LedgerBlocked("Logical test allowance exhausted")
            test["segments"][segment_id] = None

    def validate_test(
        self, test_id: str, phase: str, model: str, limits: BudgetLimits
    ) -> None:
        """Refuse a replacement that changes the original phase or policy binding."""
        limits.validate()
        with self._transaction() as state:
            self._ready(state)
            test = state["tests"][test_id]
            if (phase, model, asdict(limits)) != (
                test["phase"],
                test["model"],
                test["limits"],
            ):
                raise ValueError("Replacement differs from reservation binding")

    def reconcile(
        self,
        test_id: str,
        segment_id: str,
        *,
        model: str,
        cost_microusd: int | None,
        usage: TokenUsage | None,
    ) -> None:
        """Record complete segment accounting once; bad accounting poisons admission."""
        with self._transaction() as state:
            try:
                test = state["tests"][test_id]
                _integer(cost_microusd)
                if not isinstance(usage, TokenUsage):
                    raise ValueError("Missing token accounting")
                usage.validate()
                if model != test["model"] or segment_id not in test["segments"]:
                    raise ValueError("Accounting identity mismatch")
            except (ValueError, TypeError, KeyError):
                self._block(state, "Malformed or incomplete accounting")
            assert usage is not None
            payload = {"cost_microusd": cost_microusd, "usage": asdict(usage)}
            previous = test["segments"][segment_id]
            if previous is not None:
                if previous == payload:
                    return
                self._block(state, "Conflicting reconciliation")
            self._ready(state)
            test["segments"][segment_id] = payload
            if any(
                self._totals(test)[key] > cap for key, cap in test["limits"].items()
            ):
                self._block(state, "Accounting exceeds reservation")

    def finish(self, test_id: str) -> None:
        """Release only unused allowance after explicitly complete accounting."""
        with self._transaction() as state:
            self._ready(state)
            test = state["tests"][test_id]
            if not test["segments"] or any(
                segment is None for segment in test["segments"].values()
            ):
                raise LedgerBlocked("Cannot finish unresolved accounting")
            test["closed"] = True

    def snapshot(self, phase: str) -> dict[str, Any]:
        """Report measured consumption and held remainder separately."""
        with self._transaction() as state:
            if phase not in state["phases"]:
                raise ValueError("Phase has no configured allocation")
            return {"blocked": state["blocked"], **self._phase_totals(state, phase)}

    def test_totals(self, test_id: str) -> dict[str, int]:
        """Return cumulative measured usage, excluding unknown segments."""
        with self._transaction() as state:
            return self._totals(state["tests"][test_id])

    def segment_accounted(self, test_id: str, segment_id: str) -> bool:
        """Report whether complete accounting was retained for a segment."""
        with self._transaction() as state:
            return state["tests"][test_id]["segments"][segment_id] is not None
