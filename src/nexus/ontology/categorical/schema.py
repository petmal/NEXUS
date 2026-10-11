"""Data-only schemas; no imports of episode/runtime/generation/inference."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

Symbol = Literal["ka", "tu", "ve"]
SYMBOLS: tuple[Symbol, ...] = ("ka", "tu", "ve")


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Specimen(Payload):
    symbol: Symbol
    reading: Symbol | None = None
    signal: bool | None = None


class Stock(Payload):
    symbol: Symbol


class Investigation(Payload):
    depth: Literal[2, 3]
    mission_room: str
    theory: Literal[3] = 3
    # Experimental depth is NOT a calibrated production D-level.
    discovery: Literal[0] = 0
    experimental: Literal[True] = True


class Truth(Payload):
    laws: tuple[tuple[StrictInt, StrictInt, StrictInt], ...] = Field(min_length=2, max_length=3)

    @model_validator(mode="after")
    def permutations(self):
        if any(sorted(law) != [0, 1, 2] for law in self.laws):
            raise ValueError("each categorical law must be a permutation of 0,1,2")
        return self


SCHEMAS = {"artifact": Specimen, "stock": Stock, "investigation": Investigation, "truth": Truth}
