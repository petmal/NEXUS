"""Data-only ontology schemas; hidden state is never a specimen payload."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

FAMILY = "causal-mechanisms-v1"
Trit = Annotated[StrictInt, Field(ge=0, le=2)]
Point = tuple[Trit, Trit, Trit]
History = Annotated[tuple[Point, ...], Field(max_length=2)]


class Payload(BaseModel, frozen=True):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Experiment(Payload, frozen=True):
    instrument: Literal["sensor", "reference"] = "sensor"
    history: History = ()
    point: Point = (0, 0, 0)


class Reading(Payload, frozen=True):
    experiment: Experiment
    value: Trit


class Specimen(Payload, frozen=True):
    history: History = ()
    point: Point = (0, 0, 0)
    reading: Trit | None = None
    instrument: Literal["sensor", "reference"] | None = None


class Stock(Payload, frozen=True):
    origin: Literal["fresh"] = "fresh"


class Truth(Payload, frozen=True):
    a: Annotated[StrictInt, Field(ge=1, le=2)]
    b: Annotated[StrictInt, Field(ge=1, le=2)]
    delta: Trit
    initial: Trit
    wiring: Annotated[StrictInt, Field(ge=0, le=1)]
    transition: Trit
    response: Trit


LAW_FIELDS = ("a", "b", "delta", "wiring", "transition", "response")
STRUCTURE_FIELDS = ("wiring", "transition", "response")


class Investigation(Payload, frozen=True):
    theory: Literal[0, 1, 2, 3]
    discovery: Literal[0, 1, 2, 5]
    mission_room: str
    stock_room: str
    known: dict[str, StrictInt] = Field(default_factory=dict)
    supplied: tuple[Reading, ...] = ()
    resolved: tuple[Trit, Trit, Trit, Trit, Trit, Trit] | None = None
    experimental: Literal[True] = True  # Real-model difficulty is not calibrated.

    @model_validator(mode="after")
    def disclosure(self):
        expected = set(
            LAW_FIELDS if self.theory == 1 else STRUCTURE_FIELDS if self.theory == 2 else ()
        )
        if set(self.known) != expected:
            raise ValueError("known laws do not match theory disclosure")
        for name, value in self.known.items():
            if value not in (
                (1, 2) if name in ("a", "b") else (0, 1) if name == "wiring" else (0, 1, 2)
            ):
                raise ValueError("known law value outside public grammar")
        if self.discovery != 0 and (self.theory, self.discovery) not in ((1, 1), (2, 2), (3, 5)):
            raise ValueError("unsupported causal D/T combination")
        if (self.resolved is not None) != (self.theory == 0):
            raise ValueError("only T0 discloses resolved predictions")
        if self.theory == 0 and self.discovery != 0:
            raise ValueError("T0 requires D0")
        if self.discovery == 2 and self.known.get("response") == 2:
            raise ValueError(
                "D2 requires disclosed response form 0 or 1 for untreated identifiability"
            )
        if self.discovery != 0 and self.supplied:
            raise ValueError("live discovery starts without supplied measurements")
        return self


SCHEMAS = {"artifact": Specimen, "stock": Stock, "investigation": Investigation, "truth": Truth}
