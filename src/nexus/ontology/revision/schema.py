"""Data-only public archive, optional provisional explanation and private wiring."""

from typing import Annotated, Literal

from pydantic import Field, StrictInt, model_validator

from nexus.ontology.discovery.schema import Payload, Stock

FAMILY = "model-revision-v1"
Edge = Annotated[StrictInt, Field(ge=0, le=11)]
Trit = Annotated[StrictInt, Field(ge=0, le=2)]
Program = tuple[Edge, Edge, Edge, Edge]
Mode = Annotated[StrictInt, Field(ge=0, le=1)]


class Reading(Payload):
    query: tuple[Mode, ...] = Field(min_length=1, max_length=8)
    values: tuple[Trit]


class Specimen(Payload):
    build: Program | None = None
    reading: Reading | None = None


class GenerationOptions(Payload):
    guidance: Literal["principles", "provisional"] = "provisional"
    finish_policy: Literal["recoverable", "single"] = "recoverable"
    consistency_check: Literal["off", "readings"] = "off"


class Truth(Payload):
    program: Program


class Investigation(Payload):
    experimental: Literal[True] = True
    theory: Literal[0, 3]
    discovery: Literal[0, 5]
    archive: tuple[Trit, Trit]
    guidance: Literal["principles", "provisional"] = "provisional"
    provisional: Program | None = None
    resolved: Program | None = None
    finish_policy: Literal["recoverable", "single"] = "recoverable"
    consistency_check: Literal["off", "readings"] = "off"

    @model_validator(mode="after")
    def disclosure(self):
        if (self.theory, self.discovery) not in ((0, 0), (3, 5)):
            raise ValueError("model revision supports T0/D0 or experimental T3/D5")
        if (self.resolved is not None) != (self.theory == 0):
            raise ValueError("only T0 supplies the resolved construction")
        if (self.provisional is not None) != (self.guidance == "provisional"):
            raise ValueError("guidance and provisional model disagree")
        return self


SCHEMAS = {"artifact": Specimen, "stock": Stock, "investigation": Investigation, "truth": Truth}
