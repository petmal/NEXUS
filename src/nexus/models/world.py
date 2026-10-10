from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator
from nexus.models.investigation import SampleState, SpecimenStock
from nexus.models.network import NetworkSample, NetworkStock

INVENTORY = "@inventory"


class Shape(StrEnum):
    TRIANGLE = "triangle"
    SQUARE = "square"
    CIRCLE = "circle"


class Pattern(StrEnum):
    PLAIN = "plain"
    STRIPED = "striped"
    DOTTED = "dotted"


class Orientation(StrEnum):
    NORTH = "north"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"


class Polarity(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


class TerminalStatus(StrEnum):
    ACTIVE = "active"
    WON = "won"
    FAILED = "failed"


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Room(FrozenModel):
    id: str
    label: str


class Artifact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    location: str
    shape: Shape
    pattern: Pattern
    orientation: Orientation
    value: int = Field(ge=0, le=10)
    polarity: Polarity
    sample: SampleState | NetworkSample | None = Field(default=None, exclude_if=lambda v: v is None)


class Machine(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    room_id: str
    uses_remaining: int | None = Field(default=1, ge=0)
    settings: tuple[int, ...] | None = Field(default=None, exclude_if=lambda v: v is None)


class Resources(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actions_remaining: int | None = Field(ge=0)


class WorldState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    turn: int = Field(default=0, ge=0)
    phase: int = Field(default=0, ge=0)
    agent_room: str
    artifacts: dict[str, Artifact]
    machines: dict[str, Machine]
    resources: Resources
    terminal_status: TerminalStatus = TerminalStatus.ACTIVE
    stocks: dict[str, SpecimenStock | NetworkStock] = Field(default_factory=dict, exclude_if=lambda v: not v)
    controller_settings: tuple[int, ...] | None = Field(default=None, exclude_if=lambda v: v is None)
    controller_accepted: bool | None = Field(default=None, exclude_if=lambda v: v is None)

    @model_validator(mode="after")
    def validate_keys(self) -> "WorldState":
        for key, artifact in self.artifacts.items():
            if key != artifact.id:
                raise ValueError(f"artifact key {key!r} does not match id {artifact.id!r}")
        for key, machine in self.machines.items():
            if key != machine.id:
                raise ValueError(f"machine key {key!r} does not match id {machine.id!r}")
        return self

    def carried_artifacts(self) -> list[Artifact]:
        return [a for a in self.artifacts.values() if a.location == INVENTORY]
