"""Data-only public preparations, complete prior contract, and separate truth."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

FAMILY = "compositional-repair-v1"
Trit = Annotated[StrictInt, Field(ge=0, le=2)]
Gate = Annotated[StrictInt, Field(ge=0, le=3)]
Mode = Annotated[StrictInt, Field(ge=0, le=1)]
Point = tuple[Trit, Trit, Trit]
Dose = tuple[Trit, Trit, Trit, Trit]
Settings = tuple[Mode, Trit, Trit, Trit, Trit, Trit, Trit, Trit]


class Payload(BaseModel, frozen=True):
    model_config = ConfigDict(extra="forbid")


class Specimen(Payload, frozen=True):
    material: Literal["survey", "seal"] = "survey"
    settings: Settings = (0, 0, 0, 0, 0, 0, 0, 0)
    reading: Trit | None = None
    doses: Dose | None = None

    @model_validator(mode="after")
    def roles(self):
        if self.material == "seal" and (any(self.settings) or self.reading is not None):
            raise ValueError("seal has no survey preparation or reading")
        if self.material == "survey" and self.doses is not None:
            raise ValueError("survey has no seal treatment")
        return self


class Stock(Payload, frozen=True):
    material: Literal["survey"] = "survey"


class Truth(Payload, frozen=True):
    topology: Trit
    f: Gate
    g: Gate
    h: Gate
    changed: Trit
    replacement: Gate


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
            raise ValueError("compositional repair supports T0/D0 and T3/D5")
        if (self.resolved is not None) != (self.theory == 0):
            raise ValueError("only the control discloses a valid repair")
        return self


SCHEMAS = {"artifact": Specimen, "stock": Stock, "investigation": Investigation, "truth": Truth}
