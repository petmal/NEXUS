"""Physical support is separate from the private balanced-panel assignment."""

from typing import Annotated, Literal

from pydantic import Field, StrictInt, model_validator

from nexus.ontology.discovery.schema import Payload, Specimen, Stock

FAMILY = "uncertainty-construction-v1"
Bit = Annotated[StrictInt, Field(ge=0, le=1)]
Mask = Annotated[StrictInt, Field(ge=1, le=31)]
Slot = Annotated[StrictInt, Field(ge=0, le=7)]


class Physics(Payload):
    checks: tuple[Mask, Mask]
    syndrome: tuple[Bit, Bit]
    pattern: Bit

    @model_validator(mode="after")
    def independent_checks(self):
        a, b = self.checks
        if a >= b or b >= a ^ b or min(a.bit_count(), b.bit_count(), (a ^ b).bit_count()) < 3:
            raise ValueError(
                "checks must be the first two sorted nonzero masks of an admissible rowspace"
            )
        return self


class Truth(Physics):
    order: tuple[Slot, Slot, Slot, Slot, Slot, Slot, Slot, Slot]

    @model_validator(mode="after")
    def permutation(self):
        if len(set(self.order)) != 8:
            raise ValueError("panel assignment must be a permutation of eight slots")
        return self


class Investigation(Payload):
    experimental: Literal[True] = True
    theory: Literal[0, 2, 3]
    discovery: Literal[0, 4]
    known_checks: tuple[Mask, Mask] | None = None
    known_pattern: Bit | None = None
    resolved: Physics | None = None

    @model_validator(mode="after")
    def disclosure(self):
        if (self.theory == 0) != (self.discovery == 0):
            raise ValueError("uncertainty supports T0/D0 or T2/T3 D4")
        if (self.known_checks is not None) != (self.theory == 2) or (
            self.known_pattern is not None
        ) != (self.theory == 2):
            raise ValueError("T2 alone supplies dependence and loading shape")
        if (self.resolved is not None) != (self.theory == 0):
            raise ValueError("T0 alone supplies complete physical support")
        if self.known_checks is not None:
            Physics(checks=self.known_checks, syndrome=(0, 0), pattern=self.known_pattern)
        return self


SCHEMAS = {"artifact": Specimen, "stock": Stock, "investigation": Investigation, "truth": Truth}
