"""Versioned, strictly bounded physical and observational program grammar."""

from typing import Annotated, Literal

from pydantic import Field, StrictInt, model_validator

from nexus.ontology.discovery.schema import Payload, Specimen, Stock

FAMILY = "coupled-memory-v1"
Bit = Annotated[StrictInt, Field(ge=0, le=1)]
Wiring = Annotated[StrictInt, Field(ge=0, le=5)]
Gain = Annotated[StrictInt, Field(ge=1, le=2)]
Program = tuple[Wiring, Bit, Bit, Bit, Gain, Gain, Bit]
Dynamics = tuple[Wiring, Bit, Bit, Bit]


class Truth(Payload):
    program: Program


class Investigation(Payload):
    experimental: Literal[True] = True
    theory: Literal[0, 2, 3]
    discovery: Literal[0, 4]
    known: Dynamics | None = None
    resolved: Program | None = None

    @model_validator(mode="after")
    def disclosure(self):
        if (self.theory == 0) != (self.discovery == 0):
            raise ValueError("coupled memory supports T0/D0 or T2/T3 D4")
        if (self.known is not None) != (self.theory == 2):
            raise ValueError("T2 alone discloses physical dynamics")
        if (self.resolved is not None) != (self.theory == 0):
            raise ValueError("T0 alone supplies a complete construction")
        return self


SCHEMAS = {"artifact": Specimen, "stock": Stock, "investigation": Investigation, "truth": Truth}
