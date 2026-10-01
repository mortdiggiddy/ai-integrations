"""Safety and production runner wiring checks for the offline harness."""

from __future__ import annotations

import asyncio
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from temporalio.claude_agent_sdk import _runner
from tests.helpers.offline_harness import (
    ENGINE_PATH_ENV,
    HarnessConfig,
    OfflineHarness,
)


def _environment() -> dict[str, str]:
    return {
        ENGINE_PATH_ENV: str(Path(__file__).resolve()),
        "DURABILITY_MODEL": "offline-model",
        "DURABILITY_CREDENTIAL_ENV": "ANTHROPIC_API_KEY",
        "DURABILITY_SPEND_CAP_USD": "1",
        "DURABILITY_TOKEN_CAP": "100",
    }


@pytest.mark.parametrize(
    "name",
    [
        ENGINE_PATH_ENV,
        "DURABILITY_MODEL",
        "DURABILITY_CREDENTIAL_ENV",
        "DURABILITY_SPEND_CAP_USD",
        "DURABILITY_TOKEN_CAP",
    ],
)
def test_missing_configuration_is_refused(name: str) -> None:
    env = _environment()
    del env[name]
    with pytest.raises(ValueError, match=name):
        HarnessConfig.from_environment(env)


@pytest.mark.parametrize("cap", ["nan", "inf", "-inf", "0", "-1"])
def test_invalid_spend_cap_is_refused(cap: str) -> None:
    env = _environment()
    env["DURABILITY_SPEND_CAP_USD"] = cap
    with pytest.raises(ValueError, match="Spend cap"):
        HarnessConfig.from_environment(env)


@pytest.mark.parametrize("cap", ["0", "-1", "1.5", "nan"])
def test_invalid_token_cap_is_refused(cap: str) -> None:
    env = _environment()
    env["DURABILITY_TOKEN_CAP"] = cap
    with pytest.raises(ValueError):
        HarnessConfig.from_environment(env)


def test_direct_configuration_cannot_bypass_validation(tmp_path: Path) -> None:
    config = HarnessConfig.from_environment(_environment())
    for field, value in (
        ("spend_cap_usd", float("nan")),
        ("spend_cap_usd", True),
        ("token_cap", True),
        ("token_cap", 1.5),
        ("model", " "),
        ("credential_reference", "secret=value"),
        ("engine_path", Path("relative-engine")),
        ("engine_path", tmp_path / "absent"),
    ):
        with pytest.raises(ValueError):
            OfflineHarness(replace(config, **{field: value}), tmp_path)  # type: ignore[arg-type]


def test_paid_execution_is_always_refused() -> None:
    config = HarnessConfig.from_environment(_environment())
    with pytest.raises(ValueError, match="Credential value"):
        config.refuse_paid_execution({})
    with pytest.raises(PermissionError, match="disabled"):
        config.refuse_paid_execution({"ANTHROPIC_API_KEY": "synthetic-secret"})


async def test_production_runner_receives_explicit_options_and_redacts(
    tmp_path: Path,
) -> None:
    config = HarnessConfig.from_environment(_environment())
    harness = OfflineHarness(config, tmp_path, secrets=("synthetic-secret",))
    record = await harness.run(
        prompt="Question synthetic-secret", response="Answer synthetic-secret"
    )
    assert record.status == "passed"
    assert harness.observed_options is not None
    assert harness.observed_options.cli_path == str(config.engine_path)
    assert harness.observed_options.model == config.model
    assert harness.observed_options.max_budget_usd == config.spend_cap_usd
    assert harness.observed_options.settings is not None
    assert record.cost_usd == 0.01
    assert record.input_tokens == 2 and record.output_tokens == 3
    assert record.engine_version.endswith("(simulated)") and record.wheel_version
    assert "synthetic-secret" not in record.to_json()
    assert "[REDACTED]" in record.to_json()
    assert record.evidence_kind == "offline_simulation"


@pytest.mark.parametrize(
    "reported",
    [
        {"engine_cap_reached": True, "cost_usd": 0.001},
        {"cost_usd": 1.0},
        {"cost_usd": 2.0},
        {"input_tokens": 100, "output_tokens": 0},
    ],
)
async def test_cap_observation_never_reports_pass(
    tmp_path: Path, reported: dict[str, Any]
) -> None:
    harness = OfflineHarness(HarnessConfig.from_environment(_environment()), tmp_path)
    record = await harness.run(prompt="Question", **reported)
    assert record.status == "cap_reached"
    assert record.token_cap_enforcement == "observed_after_result_only"


async def test_cancellation_propagates_and_records_no_pass(tmp_path: Path) -> None:
    harness = OfflineHarness(HarnessConfig.from_environment(_environment()), tmp_path)
    with pytest.raises(asyncio.CancelledError):
        await harness.run(prompt="Question", cancel=True)
    assert harness.last_record is not None
    assert harness.last_record.status == "cancelled"
    assert harness.last_record.cost_usd == 0


async def test_overlapping_runs_refuse_without_live_transport(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    live_calls: list[str] = []

    def forbidden_query(**kwargs: Any) -> Any:
        del kwargs
        live_calls.append("live")
        raise AssertionError("Live SDK transport must never run")

    monkeypatch.setattr(_runner, "query", forbidden_query)
    config = HarnessConfig.from_environment(_environment())
    first = OfflineHarness(config, tmp_path / "first")
    second = OfflineHarness(config, tmp_path / "second")
    results = await asyncio.gather(
        first.run(prompt="First"),
        second.run(prompt="Second"),
        return_exceptions=True,
    )
    assert first.last_record is not None
    assert first.last_record.status == "passed"
    assert isinstance(results[1], RuntimeError)
    assert "already running" in str(results[1])
    assert second.last_record is None
    assert getattr(_runner, "query") is forbidden_query
    assert live_calls == []
    later = await second.run(prompt="After completion")
    assert later.status == "passed"
    assert getattr(_runner, "query") is forbidden_query
    assert live_calls == []
