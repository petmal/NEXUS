from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from nexus.models.world import Artifact, Machine, TerminalStatus


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    episode_id: str
    turn: int
    room: str
    room_label: str
    exits: tuple[str, ...]
    phase: int
    actions_remaining: int
    visible_artifacts: tuple[Artifact, ...] = ()
    carried_artifacts: tuple[Artifact, ...] = ()
    visible_machines: tuple[Machine, ...] = ()
    terminal_status: TerminalStatus
    goal: dict = Field(default_factory=dict)
    evidence_files: tuple[str, ...] = ()
