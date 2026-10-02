from __future__ import annotations

from pydantic import BaseModel, ConfigDict

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

    # v0.1 compatibility only. v0.2 keeps immutable goal/evidence context in the manifest.
    goal: dict | None = None
    evidence_files: tuple[str, ...] | None = None
