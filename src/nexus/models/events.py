from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from nexus.models.actions import Action
from nexus.models.world import TerminalStatus, WorldState


class EngineEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    type: str
    details: dict[str, Any] = Field(default_factory=dict)


class StepResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    state: WorldState
    events: tuple[EngineEvent, ...] = ()
    message: str = ""
    victory_code: str | None = None


class TraceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    turn: int
    action: Action
    before_hash: str
    after_hash: str
    events: tuple[EngineEvent, ...] = ()
    terminal_status: TerminalStatus
    victory_code: str | None = None
