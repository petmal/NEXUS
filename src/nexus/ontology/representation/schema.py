"""Finite memory-program grammar and explicit theory disclosures."""

from typing import Annotated, Literal

from pydantic import Field, StrictInt, model_validator

from nexus.ontology.discovery.schema import Payload, Specimen, Stock

FAMILY = "representation-discovery-v1"
Bit = Annotated[StrictInt, Field(ge=0, le=1)]
Source = Annotated[StrictInt, Field(ge=0, le=2)]
Gain = Annotated[StrictInt, Field(ge=1, le=2)]
Program = tuple[Bit, Source, Bit, Bit, Bit, Gain, Gain, Gain, Bit]
Skeleton = tuple[Bit, Source, Bit, Bit, Bit, Bit]


class Truth(Payload):
    program: Program


class Investigation(Payload):
    experimental: Literal[True] = True
    theory: Literal[0, 2, 3]
    discovery: Literal[0, 4]
    known: Skeleton | None = None
    resolved: Program | None = None

    @model_validator(mode="after")
    def disclosure(self):
        if (self.theory == 0) != (self.discovery == 0):
            raise ValueError("representation supports T0/D0 or T2/T3 D4")
        if (self.known is not None) != (self.theory == 2):
            raise ValueError("T2 alone supplies the memory skeleton")
        if (self.resolved is not None) != (self.theory == 0):
            raise ValueError("T0 alone supplies the complete memory program")
        return self


SCHEMAS = {"artifact": Specimen, "stock": Stock, "investigation": Investigation, "truth": Truth}
