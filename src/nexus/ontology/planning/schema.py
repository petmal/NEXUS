"""Versioned P/R experiment; previous stateful contracts remain unchanged."""

from __future__ import annotations

from typing import Literal

from pydantic import model_validator

from nexus.ontology.stateful.schema import Payload, Specimen, Truth, Vector

FAMILY = "stateful-planning-v1"


class Investigation(Payload):
    theory: Literal[0, 3]
    discovery: Literal[5] = 5
    planning: Literal[0, 1, 2, 3]
    target: Vector
    resolved: Truth | None = None
    experimental: Literal[True] = True

    @property
    def mission_room(self) -> str:
        return "array"

    @property
    def stock_room(self) -> str:
        return "array"

    @model_validator(mode="after")
    def controls(self):
        if (self.resolved is not None) != (self.theory == 0):
            raise ValueError("only T0 discloses the physical laws")
        if self.target in ((0, 0, 0, 0), (4, 4, 4, 4)):
            raise ValueError("target must be noninitial and noncollapsed")
        return self


SCHEMAS = {"artifact": Specimen, "investigation": Investigation, "truth": Truth}
