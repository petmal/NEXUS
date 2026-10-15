"""Finite public contracts and separate private truth; no latent specimen fields."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

FAMILY = "coupled-dynamics-v1"
Bit = Annotated[StrictInt, Field(ge=0, le=1)]
Trit = Annotated[StrictInt, Field(ge=0, le=2)]
Coefficient = Annotated[StrictInt, Field(ge=1, le=2)]
Point = tuple[Bit, Bit, Bit]
History = Annotated[tuple[Point, ...], Field(max_length=3)]
Dose = tuple[Trit, Trit, Trit, Trit, Trit, Trit, Trit, Trit]


class Payload(BaseModel, frozen=True):
    model_config = ConfigDict(extra="forbid")


class Experiment(Payload, frozen=True):
    instrument: Literal["sensor", "reference"] = "sensor"
    history: History = ()
    point: Point = (0, 0, 0)


class Specimen(Payload, frozen=True):
    material: Literal["survey", "seal"] = "survey"
    history: History = ()
    point: Point = (0, 0, 0)
    reading: Trit | None = None
    instrument: Literal["sensor", "reference"] | None = None
    doses: Dose | None = None

    @model_validator(mode="after")
    def material_roles(self):
        if self.material == "seal" and (self.history or self.point != (0, 0, 0)):
            raise ValueError("seal has no survey preparation")
        if self.material == "survey" and self.doses is not None:
            raise ValueError("survey cannot carry seal treatment")
        if self.material == "seal" and self.reading is not None:
            raise ValueError("seal does not expose a measured response")
        return self


class Stock(Payload, frozen=True):
    material: Literal["survey"] = "survey"


class Truth(Payload, frozen=True):
    a: Coefficient
    b: Coefficient
    initial_h: Trit
    initial_k: Trit
    delta: Trit
    wiring: Bit
    transition: Trit
    response: Trit


class Investigation(Payload, frozen=True):
    theory: Literal[0, 3]
    discovery: Literal[0, 5]
    mission_room: Literal["array"] = "array"
    stock_room: Literal["array", "stores"]
    resolved: Dose | None = None
    experimental: Literal[True] = True

    @model_validator(mode="after")
    def disclosure(self):
        if (self.theory, self.discovery) not in ((0, 0), (3, 5)):
            raise ValueError("dynamics supports only T0/D0 and T3/D5")
        if (self.resolved is not None) != (self.theory == 0):
            raise ValueError("only T0 supplies the exact treatment")
        return self


SCHEMAS = {"artifact": Specimen, "stock": Stock, "investigation": Investigation, "truth": Truth}
