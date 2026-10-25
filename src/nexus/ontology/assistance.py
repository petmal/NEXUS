"""Explicit public-evidence assistance, separate from world actions and auditing."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt


class ConstructionCheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    build: tuple[StrictInt, ...] = Field(min_length=1, max_length=64)


class ConstructionCheckResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    scope: Literal["archive_and_observed_reader_outputs_only"] = (
        "archive_and_observed_reader_outputs_only"
    )
    consistent_with_readings: bool
    distinct_readings_checked: int
    evidence_turn: int
    world_action_cost: Literal[0] = 0


__all__ = ["ConstructionCheckRequest", "ConstructionCheckResult"]
