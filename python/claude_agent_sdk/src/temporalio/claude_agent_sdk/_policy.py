"""Validated immutable policy for the supported built in tools."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Literal, cast

ToolClass = Literal["read", "effect", "ask"]
EffectMode = Literal["repeatable", "claimed"]

_RETAINED: dict[str, tuple[str, str | None]] = {
    "Read": ("read", None),
    "Grep": ("read", None),
    "Glob": ("read", None),
    "Skill": ("read", None),
    "Write": ("effect", "repeatable"),
    "Edit": ("effect", "repeatable"),
    "Bash": ("effect", "claimed"),
    "AskUserQuestion": ("ask", None),
}


@dataclass(frozen=True)
class ToolPolicyEntry:
    """One exact built in name and its retained execution classification.

    Attributes:
        name: Exact engine tool name.
        tool_class: Read, effect, or ask classification.
        mode: Repeatable or claimed for effects; absent for other classes.
        approval: Whether an effect needs an approval.
        start_to_close: Optional effect Activity execution timeout.
        heartbeat_timeout: Optional effect Activity heartbeat timeout.
        schedule_to_close: Optional total effect Activity timeout.
        schedule_to_start: Optional effect Activity queue timeout.
        silence_timeout: Optional process silence timeout.
        output_cap_bytes: Maximum effect result size.
    """

    name: str
    tool_class: ToolClass
    mode: EffectMode | None = None
    approval: Literal["none", "required"] = "none"
    start_to_close: timedelta | None = None
    heartbeat_timeout: timedelta | None = None
    schedule_to_close: timedelta | None = None
    schedule_to_start: timedelta | None = None
    silence_timeout: timedelta | None = None
    output_cap_bytes: int = 64 * 1024

    def __post_init__(self) -> None:
        """Reject unsupported names and classifications before offering a tool."""
        if _RETAINED.get(self.name) != (self.tool_class, self.mode):
            raise ValueError(f"Unsupported tool policy entry: {self.name!r}")
        if self.approval not in ("none", "required"):
            raise ValueError("approval must be none or required")
        if self.tool_class != "effect" and self.approval != "none":
            raise ValueError("Only effect tools can require approval")
        for value in (
            self.start_to_close,
            self.heartbeat_timeout,
            self.schedule_to_close,
            self.schedule_to_start,
            self.silence_timeout,
        ):
            if value is not None and (
                not isinstance(value, timedelta) or value.total_seconds() <= 0
            ):
                raise ValueError("Policy durations must be positive timedeltas")
        if (
            isinstance(self.output_cap_bytes, bool)
            or not isinstance(self.output_cap_bytes, int)
            or self.output_cap_bytes < 1
        ):
            raise ValueError("output_cap_bytes must be a positive integer")


@dataclass(frozen=True)
class ToolPolicy:
    """An immutable inventory; names outside it have no authority.

    Attributes:
        entries: Exact supported tool entries, with no duplicates.
    """

    entries: tuple[ToolPolicyEntry, ...]

    def __post_init__(self) -> None:
        """Copy the inventory and reject invalid or duplicate entries."""
        entries = tuple(self.entries)
        if any(not isinstance(entry, ToolPolicyEntry) for entry in entries):
            raise ValueError("entries must contain ToolPolicyEntry values")
        names = [entry.name for entry in entries]
        if len(names) != len(set(names)):
            raise ValueError("Tool policy names must be unique")
        object.__setattr__(self, "entries", entries)

    def lookup(self, name: str) -> ToolPolicyEntry:
        """Return an explicitly offered entry; reject every other name."""
        for entry in self.entries:
            if entry.name == name:
                return entry
        raise ValueError(f"Tool is not offered by policy: {name!r}")

    def canonical_json(self) -> str:
        """Serialize every policy field in stable name order."""
        rows = []
        for entry in sorted(self.entries, key=lambda item: item.name):
            row: dict[str, Any] = {
                "name": entry.name,
                "class": entry.tool_class,
                "mode": entry.mode,
                "approval": entry.approval,
                "output_cap_bytes": entry.output_cap_bytes,
            }
            for name in (
                "start_to_close",
                "heartbeat_timeout",
                "schedule_to_close",
                "schedule_to_start",
                "silence_timeout",
            ):
                value = getattr(entry, name)
                row[name] = value.total_seconds() if value is not None else None
            rows.append(row)
        return json.dumps(rows, sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_json(cls, payload: str) -> ToolPolicy:
        """Reconstruct and validate a canonical policy transported as JSON text."""
        try:
            rows = json.loads(payload)
            if not isinstance(rows, list):
                raise ValueError("Policy must be a list")
            entries = []
            durations = (
                "start_to_close",
                "heartbeat_timeout",
                "schedule_to_close",
                "schedule_to_start",
                "silence_timeout",
            )
            expected = {
                "name",
                "class",
                "mode",
                "approval",
                "output_cap_bytes",
                *durations,
            }
            for row in rows:
                if not isinstance(row, dict) or set(row) != expected:
                    raise ValueError("Policy entry fields do not match the schema")
                values: dict[str, timedelta | None] = {}
                for name in durations:
                    seconds = row[name]
                    if seconds is not None and (
                        isinstance(seconds, bool)
                        or not isinstance(seconds, (float, int))
                        or not math.isfinite(seconds)
                        or seconds <= 0
                    ):
                        raise ValueError(
                            "Wire durations must be positive finite seconds"
                        )
                    values[name] = (
                        timedelta(seconds=seconds) if seconds is not None else None
                    )
                entries.append(
                    ToolPolicyEntry(
                        name=row["name"],
                        tool_class=cast(ToolClass, row["class"]),
                        mode=cast(EffectMode | None, row["mode"]),
                        approval=row["approval"],
                        output_cap_bytes=row["output_cap_bytes"],
                        start_to_close=values["start_to_close"],
                        heartbeat_timeout=values["heartbeat_timeout"],
                        schedule_to_close=values["schedule_to_close"],
                        schedule_to_start=values["schedule_to_start"],
                        silence_timeout=values["silence_timeout"],
                    )
                )
            return cls(tuple(entries))
        except (TypeError, OverflowError, KeyError) as err:
            raise ValueError("Invalid wire policy") from err

    @property
    def policy_version(self) -> str:
        """Return the SHA256 digest of the canonical table."""
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def policy_extra_options(extra: dict[str, Any]) -> dict[str, Any]:
    """Validate the finite initial extension surface and return a fresh snapshot.

    Only prompt text and an empty raw flag mapping are admitted. Inference controls,
    diagnostic flags, settings, callbacks, and grants require separate engine proof.
    """
    unknown = set(extra) - {"system_prompt", "extra_args"}
    if unknown:
        raise ValueError(
            "Policy extra_options cannot set: " + ", ".join(sorted(unknown))
        )
    result: dict[str, Any] = {}
    if "system_prompt" in extra:
        if not isinstance(extra["system_prompt"], str):
            raise ValueError("Policy system_prompt must be a string")
        result["system_prompt"] = extra["system_prompt"]
    if "extra_args" in extra:
        if not isinstance(extra["extra_args"], dict) or extra["extra_args"]:
            raise ValueError("Policy extra_args must be an empty mapping")
        result["extra_args"] = {}
    return result
