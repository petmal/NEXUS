"""Public apparatus contract and private compositional mechanisms for coupled networks."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

BENCH = (
    (0, 0),
    (0, 1),
    (1, 0),
    (0, 2),
    (2, 0),
    (1, 1),
    (1, 2),
    (2, 1),
    (2, 2),
    (1, 3),
    (3, 1),
    (3, 2),
)
FIELD = ((4, 1), (1, 4), (4, 3), (3, 4))


class NetworkExpression(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    op: Literal["variable", "add", "multiply"]
    variable: Literal["x", "y", "a", "b", "c", "d", "u", "v"] | None = None
    children: tuple[NetworkExpression, ...] = ()

    @model_validator(mode="after")
    def valid_shape(self):
        if self.op == "variable":
            if self.variable is None or self.children:
                raise ValueError("variable expression requires a name and no children")
        elif self.variable is not None or len(self.children) != 2:
            raise ValueError("binary expression requires two children and no variable")
        return self


class ResonanceLaw(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    alpha: int = Field(ge=1, le=3)
    beta: int = Field(ge=1, le=3)
    gate: int = Field(ge=0, le=2)


class NetworkTruth(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    a: int = Field(ge=1, le=3)
    b: int = Field(ge=1, le=3)
    c: int = Field(ge=1, le=3)
    d: int = Field(ge=1, le=3)
    gates: tuple[int, int, int]
    program: tuple[NetworkExpression, NetworkExpression, NetworkExpression]
    resonance: ResonanceLaw | None = Field(default=None, exclude_if=lambda v: v is None)

    @model_validator(mode="after")
    def bounded_gates(self):
        if any(type(v) is not int or not 0 <= v <= 2 for v in self.gates):
            raise ValueError("gate indices must be 0..2")
        return self


class NetworkSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    version: Literal["coupled-network-v1", "resonant-network-v1"] = "coupled-network-v1"
    theory: int = Field(ge=0, le=3)
    discovery: int = Field(ge=0, le=5)
    modulus: Literal[7] = 7
    controller_room: str
    supplied_measurements: tuple[tuple[str, int], ...] = ()
    resolved_settings: tuple[int, ...] | None = None


class NetworkSample(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: int = Field(ge=0, le=6)
    y: int = Field(ge=0, le=6)
    reading: int | None = Field(default=None, ge=0, le=6)
    signal: bool | None = Field(default=None, exclude_if=lambda v: v is None)


class NetworkStock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    location: str
    x: int = Field(ge=0, le=6)
    y: int = Field(ge=0, le=6)
    remaining: int | None = Field(default=None, ge=0)
