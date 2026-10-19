"""Data-only schemas; public specimens contain treatments, never hidden loads."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

FAMILY = "staged-repair-v1"
Trit = Annotated[StrictInt, Field(ge=0, le=2)]
Exponent = Annotated[StrictInt, Field(ge=1, le=2)]
Vector = tuple[Trit, Trit, Trit]
SEALS = ("seal-0", "seal-1", "seal-2")


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Mechanism(Payload):
    shift: Trit
    exponent: Exponent


class Truth(Payload):
    mechanisms: tuple[Mechanism, Mechanism, Mechanism]


class Specimen(Payload):
    tag: Trit
    doses: Vector = (0, 0, 0)
    reading: Trit | None = None
    stage: Trit | None = None
    carrier: Trit | None = None

    @model_validator(mode="after")
    def complete_reading(self):
        if len({v is None for v in (self.reading, self.stage, self.carrier)}) != 1:
            raise ValueError("a reading requires stage and carrier, including zero readings")
        return self


class Stock(Payload):
    tag: Trit


class Investigation(Payload):
    theory: Literal[0, 2, 3]
    discovery: Literal[0, 3, 4]
    stock_room: Literal["stores", "array"] = "stores"
    mission_room: Literal["array"] = "array"
    known_exponents: tuple[Exponent, Exponent, Exponent] | None = None
    resolved: Truth | None = None
    repair: tuple[Vector, Vector, Vector] | None = None
    experimental: Literal[True] = True

    @property
    def linked(self) -> bool:
        return self.discovery != 3

    @model_validator(mode="after")
    def disclosure(self):
        if (self.theory == 0) != (self.discovery == 0):
            raise ValueError("staged control requires T0/D0; investigation requires T2/T3 D3/D4")
        if (self.known_exponents is not None) != (self.theory == 2):
            raise ValueError("only T2 discloses the operator exponents")
        if (self.resolved is not None) != (self.theory == 0) or (self.repair is not None) != (
            self.theory == 0
        ):
            raise ValueError("only T0 supplies exact mechanisms and repairs")
        return self


SCHEMAS = {"artifact": Specimen, "stock": Stock, "investigation": Investigation, "truth": Truth}
