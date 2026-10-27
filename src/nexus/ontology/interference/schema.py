"""Six public quinary registers; the target-selection stratum stays operator-only."""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

FAMILY = "stateful-interference-v1"
MODULUS = 5
COUNT = 6
SIZE = MODULUS**COUNT
Cell = Annotated[StrictInt, Field(ge=0, lt=MODULUS)]
Gain = Annotated[StrictInt, Field(ge=1, lt=MODULUS)]
Vector = tuple[Cell, ...]


class Payload(BaseModel, frozen=True):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Structure(Payload):
    coupling: Literal["independent", "coupled"] = "coupled"

    @property
    def count(self) -> int:
        return COUNT


class GenerationOptions(Structure):
    horizon: Literal["short", "long"] = "long"


class Truth(Payload):
    guards: tuple[Cell, ...] = Field(min_length=COUNT, max_length=COUNT)
    gains: tuple[Gain, ...] = Field(min_length=COUNT, max_length=COUNT)
    spill_gains: tuple[Gain, ...] = Field(min_length=COUNT, max_length=COUNT)


class Coordinate(Payload):
    machine: str
    guard_register: Annotated[StrictInt, Field(ge=0, lt=COUNT)]
    spill_register: Annotated[StrictInt, Field(ge=0, lt=COUNT)]


@lru_cache(maxsize=2)
def topology(coupling: str) -> tuple[Coordinate, ...]:
    if coupling not in ("independent", "coupled"):
        raise ValueError("unknown interference coupling")
    return tuple(
        Coordinate(
            machine=f"bank{bank}_r{register}",
            guard_register=bank * 3 + (register + 1) % 3,
            spill_register=(1 - bank) * 3
            if coupling == "coupled" and register == 2
            else bank * 3 + (register + 2) % 3,
        )
        for bank in range(2)
        for register in range(3)
    )


class Specimen(Payload):
    registers: Vector = Field(min_length=COUNT, max_length=COUNT)


class Investigation(Payload):
    theory: Annotated[StrictInt, Field(ge=0, le=0)] = 0
    discovery: Annotated[StrictInt, Field(ge=0, le=0)] = 0
    planning: Annotated[StrictInt, Field(ge=0, le=0)] = 0
    options: Structure
    topology: tuple[Coordinate, ...]
    resolved: Truth
    target: tuple[Gain, ...] = Field(min_length=COUNT, max_length=COUNT)
    experimental: Literal[True] = True

    @property
    def mission_room(self) -> str:
        return "array"

    @property
    def stock_room(self) -> str:
        return "array"

    @model_validator(mode="after")
    def contract(self):
        if self.topology != topology(self.options.coupling):
            raise ValueError("topology differs from the declared write-edge placement")
        return self


SCHEMAS = {"artifact": Specimen, "investigation": Investigation, "truth": Truth}
