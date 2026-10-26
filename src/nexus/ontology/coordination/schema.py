"""Strict public finite-state specification; coefficients are intentionally public."""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

FAMILY = "stateful-coordination-v1"
Cell = Annotated[StrictInt, Field(ge=0, le=2)]
Choice = Annotated[StrictInt, Field(ge=1, le=2)]
Size = Annotated[StrictInt, Field(ge=2, le=3)]
Vector = tuple[Cell, ...]


class Payload(BaseModel, frozen=True):
    model_config = ConfigDict(extra="forbid", frozen=True)


class GenerationOptions(Payload, frozen=True):
    banks: Size = 2
    registers_per_bank: Size = 2
    coupling: Literal["independent", "coupled"] = "coupled"

    @property
    def count(self) -> int:
        return self.banks * self.registers_per_bank


class Truth(Payload, frozen=True):
    gains: tuple[Choice, ...] = Field(min_length=4, max_length=9)
    powers: tuple[Choice, ...] = Field(min_length=4, max_length=9)

    @model_validator(mode="after")
    def dimensions(self):
        if len(self.gains) != len(self.powers) or len(self.gains) not in (4, 6, 9):
            raise ValueError("coefficient dimensions must agree and contain 4, 6 or 9 entries")
        return self


class Coordinate(Payload, frozen=True):
    machine: str
    bank: Annotated[StrictInt, Field(ge=0, le=2)]
    register_index: Annotated[StrictInt, Field(ge=0, le=2)]
    local_next: Annotated[StrictInt, Field(ge=0, le=8)]
    cross_first: Annotated[StrictInt, Field(ge=0, le=8)] | None


@lru_cache(maxsize=8)
def topology(options: GenerationOptions) -> tuple[Coordinate, ...]:
    width = options.registers_per_bank
    return tuple(
        Coordinate(
            machine=f"bank{bank}_r{register}",
            bank=bank,
            register_index=register,
            local_next=bank * width + (register + 1) % width,
            cross_first=((bank + 1) % options.banks) * width
            if options.coupling == "coupled" and register == width - 1
            else None,
        )
        for bank in range(options.banks)
        for register in range(width)
    )


class Specimen(Payload, frozen=True):
    registers: Vector = Field(min_length=4, max_length=9)

    @model_validator(mode="after")
    def dimensions(self):
        if len(self.registers) not in (4, 6, 9):
            raise ValueError("seal must contain 4, 6 or 9 registers")
        return self


class Investigation(Payload, frozen=True):
    theory: Annotated[StrictInt, Field(ge=0, le=0)] = 0
    discovery: Annotated[StrictInt, Field(ge=0, le=0)] = 0
    planning: StrictInt = 0
    options: GenerationOptions
    topology: tuple[Coordinate, ...]
    resolved: Truth
    target: Vector
    experimental: Literal[True] = True

    @property
    def mission_room(self) -> str:
        return "array"

    @property
    def stock_room(self) -> str:
        return "array"

    @model_validator(mode="after")
    def contract(self):
        if self.planning not in (0, 3):
            raise ValueError("coordination supports only P0 or P3")
        if self.topology != topology(self.options):
            raise ValueError("topology differs from the declared bank structure")
        if len(self.target) != self.options.count or len(self.resolved.gains) != self.options.count:
            raise ValueError("target and coefficient dimensions must match the options")
        if not all(self.target):
            raise ValueError("every target coordinate must be nonzero")
        return self


SCHEMAS = {"artifact": Specimen, "investigation": Investigation, "truth": Truth}
