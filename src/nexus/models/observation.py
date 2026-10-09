from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_serializer
from nexus.models.investigation import SpecimenStock

from nexus.models.world import Artifact, Machine, TerminalStatus


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    episode_id: str
    turn: int
    room: str
    room_label: str
    exits: tuple[str, ...]
    phase: int
    actions_remaining: int | None
    visible_artifacts: tuple[Artifact, ...] = ()
    carried_artifacts: tuple[Artifact, ...] = ()
    visible_machines: tuple[Machine, ...] = ()
    terminal_status: TerminalStatus
    visible_stocks: tuple[SpecimenStock, ...] = Field(default=(), exclude_if=lambda v: not v)
    controller_settings: tuple[int, ...] | None = Field(default=None, exclude_if=lambda v: v is None)

    # v0.1 compatibility only. v0.2 keeps immutable goal/evidence context in the manifest.
    goal: dict | None = None
    evidence_files: tuple[str, ...] | None = None

    @model_serializer(mode="wrap")
    def explicit_unlimited_resources(self, handler):
        result = handler(self)
        # HTTP omits optional hint/receipt fields, but null resources have public semantics.
        if self.actions_remaining is None:
            result["actions_remaining"] = None
        for item in result.get("visible_stocks", ()):
            item.setdefault("remaining", None)
        for item in result.get("visible_machines", ()):
            item.setdefault("uses_remaining", None)
        return result
