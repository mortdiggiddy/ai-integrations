"""Offline construction checks for the opt in engine harness.

Only a simulated SDK stream can run here. These records are not real model
evidence, and token accounting after a result is not a preventive token cap.
"""

from __future__ import annotations

import asyncio
import json
import math
import re
import threading
import uuid
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from decimal import ROUND_CEILING, Decimal
from importlib.metadata import version
from pathlib import Path
from typing import Any, Literal
from unittest.mock import AsyncMock, patch

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, SystemMessage

from temporalio.claude_agent_sdk import (
    ClaudeAgentSdkRunner,
    FileSessionStore,
    SegmentInput,
    _runner,
)
from tests.helpers.budget_ledger import (
    BudgetLedger,
    BudgetLimits,
    LedgerBlocked,
    PhasePolicy,
    TokenUsage,
)

ENGINE_PATH_ENV = "DURABILITY_ENGINE_PATH"
_SDK_PATCH_LOCK = threading.Lock()


@dataclass(frozen=True)
class HarnessConfig:
    """Explicit proposed settings; creating them does not authorize execution."""

    engine_path: Path
    model: str
    credential_reference: str
    spend_cap_usd: float
    token_cap: int
    input_token_cap: int = 100_000
    output_token_cap: int = 8_192
    phase_cost_microusd: int = 20_000_000
    phase_token_cap: int = 2_000_000

    @classmethod
    def from_environment(cls, env: Mapping[str, str]) -> HarnessConfig:
        """Read only the explicit harness configuration, without ambient fallback."""
        required = (
            ENGINE_PATH_ENV,
            "DURABILITY_MODEL",
            "DURABILITY_CREDENTIAL_ENV",
            "DURABILITY_SPEND_CAP_USD",
            "DURABILITY_TOKEN_CAP",
        )
        for name in required:
            if not env.get(name, "").strip():
                raise ValueError(f"Missing harness configuration: {name}")
        config = cls(
            engine_path=Path(env[ENGINE_PATH_ENV]),
            model=env["DURABILITY_MODEL"],
            credential_reference=env["DURABILITY_CREDENTIAL_ENV"],
            spend_cap_usd=float(env["DURABILITY_SPEND_CAP_USD"]),
            token_cap=int(env["DURABILITY_TOKEN_CAP"]),
        )
        config.validate()
        return config

    def validate(self) -> None:
        """Reject incomplete settings and invalid caps before constructing a runner."""
        if not self.engine_path.is_absolute():
            raise ValueError("Engine path must be absolute")
        if not self.engine_path.is_file():
            raise ValueError("Engine path must name an existing file")
        if not self.model.strip():
            raise ValueError("Model identifier is required")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", self.credential_reference):
            raise ValueError("Credential reference must name an environment variable")
        if (
            isinstance(self.spend_cap_usd, bool)
            or not math.isfinite(self.spend_cap_usd)
            or self.spend_cap_usd <= 0
        ):
            raise ValueError("Spend cap must be finite and positive")
        if (
            isinstance(self.token_cap, bool)
            or not isinstance(self.token_cap, int)
            or self.token_cap <= 0
        ):
            raise ValueError("Token cap must be a positive integer")
        self.budget_policy.validate()
        if (
            Decimal(str(self.spend_cap_usd)) * 1_000_000
            != self.budget_limits.cost_microusd
        ):
            raise ValueError("Spend cap requires exact micro USD precision")

    @property
    def budget_limits(self) -> BudgetLimits:
        """Return immutable logical test limits in integer units."""
        return BudgetLimits(
            int(Decimal(str(self.spend_cap_usd)) * 1_000_000),
            self.input_token_cap,
            self.output_token_cap,
            self.token_cap,
        )

    @property
    def budget_policy(self) -> PhasePolicy:
        """Return an offline phase policy without allocating live headroom."""
        return PhasePolicy(
            self.model,
            self.budget_limits,
            self.phase_cost_microusd,
            self.phase_token_cap,
        )

    def refuse_paid_execution(self, env: Mapping[str, str]) -> None:
        """Always refuse provider execution, even with complete configuration."""
        self.validate()
        if not env.get(self.credential_reference, "").strip():
            raise ValueError("Credential value is missing")
        raise PermissionError("Paid provider execution is disabled")


@dataclass(frozen=True)
class OfflineRecord:
    """Redacted accounting of one simulated SDK stream."""

    engine_version: str
    wheel_version: str
    model: str
    cost_usd: float | None
    input_tokens: int | None
    output_tokens: int | None
    transcript: tuple[str, ...]
    status: Literal["passed", "cap_reached", "failed", "cancelled"]
    evidence_kind: str = "offline_simulation"
    token_cap_enforcement: str = "observed_after_result_only"
    accounting_status: str = "unresolved"
    cumulative_usage: dict[str, int] | None = None
    phase_accounting: dict[str, Any] | None = None
    token_categories: dict[str, int] | None = None

    def to_json(self) -> str:
        """Serialize only record fields; no credential or runner environment is included."""
        return json.dumps(asdict(self), sort_keys=True, allow_nan=False)


class OfflineHarness:
    """Drive the production runner with a local simulated stream, never the SDK transport.

    A process lock refuses overlapping harness runs before SDK patches can overlap.
    Usage and transcript are simulated fixtures, not a measured model transcript.
    """

    def __init__(
        self,
        config: HarnessConfig,
        directory: Path,
        *,
        secrets: tuple[str, ...] = (),
        initialize_ledger: bool = False,
        ledger: BudgetLedger | None = None,
        logical_test_id: str = "offline-test",
        phase: str = "offline-proof",
    ) -> None:
        """Validate settings and retain a redaction list without exposing its values."""
        config.validate()
        self.config = config
        self.directory = directory
        if initialize_ledger:
            if ledger is not None:
                raise ValueError(
                    "Initialize disposable storage separately from shared storage"
                )
            directory.mkdir(parents=True, exist_ok=True)
        self.ledger = ledger or BudgetLedger(
            directory / "offline-budget.sqlite3", create=initialize_ledger
        )
        self.logical_test_id = logical_test_id
        self.phase = phase
        self.ledger.configure_phase(phase, config.budget_policy)
        if initialize_ledger:
            self.ledger.reserve(
                logical_test_id, phase, config.model, config.budget_limits
            )
        self.ledger.validate_test(
            logical_test_id, phase, config.model, config.budget_limits
        )
        self._secrets = tuple(secret for secret in secrets if secret)
        self.last_record: OfflineRecord | None = None
        self.observed_options: ClaudeAgentOptions | None = None

    def _redact(self, value: str) -> str:
        for secret in sorted(self._secrets, key=len, reverse=True):
            value = value.replace(secret, "[REDACTED]")
        return value

    async def run(
        self,
        *,
        prompt: str,
        response: str = "Offline answer",
        cost_usd: float = 0.01,
        input_tokens: int = 2,
        output_tokens: int = 3,
        cache_read_tokens: int = 0,
        cache_write_tokens: int = 0,
        thinking_tokens: int = 0,
        engine_cap_reached: bool = False,
        cancel: bool = False,
        timeout: bool = False,
        segment_id: str | None = None,
    ) -> OfflineRecord:
        """Run a deterministic local stream and classify accounting without provider calls."""
        if not _SDK_PATCH_LOCK.acquire(blocking=False):
            raise RuntimeError("An offline harness is already running")
        segment_id = segment_id or str(uuid.uuid4())
        try:
            self.ledger.begin_segment(
                self.logical_test_id,
                segment_id,
                model=self.config.model,
                limits=self.config.budget_limits,
            )
        except BaseException:
            _SDK_PATCH_LOCK.release()
            raise
        sid = str(uuid.uuid4())
        reported_version = "2.1.274 (simulated)"

        async def simulated_query(**kwargs: Any) -> Any:
            self.observed_options = kwargs["options"]
            await asyncio.sleep(0)
            yield SystemMessage(
                subtype="init", data={"claude_code_version": reported_version}
            )
            if cancel:
                raise asyncio.CancelledError
            if timeout:
                raise TimeoutError("Simulated missing final accounting")
            yield ResultMessage(
                subtype="error_max_budget_usd" if engine_cap_reached else "success",
                duration_ms=1,
                duration_api_ms=0,
                is_error=engine_cap_reached,
                num_turns=1,
                session_id=sid,
                result=response,
                total_cost_usd=cost_usd,
                usage={
                    "input_tokens": input_tokens,
                    "cache_read_input_tokens": cache_read_tokens,
                    "cache_creation_input_tokens": cache_write_tokens,
                    "output_tokens": output_tokens,
                    "thinking_tokens": thinking_tokens,
                },
            )

        status: Literal["passed", "cap_reached", "failed", "cancelled"] = "failed"
        accounted = False
        usage: TokenUsage | None = None
        try:
            runner = ClaudeAgentSdkRunner(
                session_store=FileSessionStore(self.directory / "sessions"),
                cwd=str(self.directory),
                cli_path=str(self.config.engine_path),
                model=self.config.model,
                max_budget_usd=self.config.spend_cap_usd,
                env={"ANTHROPIC_API_KEY": "offline-placeholder"},
            )
            try:
                if (
                    isinstance(cost_usd, bool)
                    or not math.isfinite(cost_usd)
                    or cost_usd < 0
                ):
                    raise ValueError("Invalid cost accounting")
                cost_microusd = int(
                    (Decimal(str(cost_usd)) * 1_000_000).to_integral_value(
                        rounding=ROUND_CEILING
                    )
                )
                usage = TokenUsage(
                    input_tokens,
                    cache_read_tokens,
                    cache_write_tokens,
                    output_tokens,
                    thinking_tokens,
                )
                usage.validate()
            except (ValueError, TypeError):
                self.ledger.reconcile(
                    self.logical_test_id,
                    segment_id,
                    model=self.config.model,
                    cost_microusd=None,
                    usage=None,
                )
                raise
            with (
                patch.object(_runner, "query", simulated_query),
                patch.object(
                    runner, "_engine_version", AsyncMock(return_value=reported_version)
                ),
                patch.object(
                    runner, "_checkpoint", AsyncMock(return_value="offline-checkpoint")
                ),
            ):
                out = await runner.run(
                    SegmentInput(session_id=sid, prompt=prompt, tools=[]), 1
                )
            try:
                self.ledger.reconcile(
                    self.logical_test_id,
                    segment_id,
                    model=self.config.model,
                    cost_microusd=cost_microusd,
                    usage=usage,
                )
            except LedgerBlocked:
                accounted = self.ledger.segment_accounted(
                    self.logical_test_id, segment_id
                )
                status = "cap_reached" if accounted else "failed"
                raise
            accounted = True
            totals = self.ledger.test_totals(self.logical_test_id)
            reached = engine_cap_reached or any(
                totals[key] >= cap
                for key, cap in asdict(self.config.budget_limits).items()
            )
            status = (
                "cap_reached" if reached else ("failed" if out.is_error else "passed")
            )
        except asyncio.CancelledError:
            status = "cancelled"
            raise
        except LedgerBlocked:
            if not accounted:
                raise
        finally:
            _SDK_PATCH_LOCK.release()
            self.last_record = OfflineRecord(
                engine_version=reported_version,
                wheel_version=version("claude-agent-sdk"),
                model=self._redact(self.config.model),
                cost_usd=cost_usd if accounted else None,
                input_tokens=usage.input if accounted and usage is not None else None,
                output_tokens=output_tokens if accounted else None,
                transcript=tuple(self._redact(text) for text in (prompt, response))
                if accounted
                else (self._redact(prompt),),
                status=status,
                accounting_status="reconciled" if accounted else "unresolved",
                cumulative_usage=self.ledger.test_totals(self.logical_test_id),
                phase_accounting=self.ledger.snapshot(self.phase),
                token_categories=asdict(usage)
                if accounted and usage is not None
                else None,
            )
        return self.last_record
