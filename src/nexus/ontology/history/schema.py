"""Data-only public histories and private mechanisms. No hidden specimen fields."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

FAMILY = "history-coupled-v1"
MAX_HISTORY = 8
Trit = Annotated[StrictInt, Field(ge=0, le=2)]
Gate = Annotated[StrictInt, Field(ge=0, le=3)]
Orientation = Annotated[StrictInt, Field(ge=1, le=2)]
History = Annotated[tuple[Gate, ...], Field(max_length=MAX_HISTORY)]
Pair = tuple[Trit, Trit]


class Payload(BaseModel, frozen=True):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Truth(Payload):
    gates: tuple[Gate, Gate, Gate, Gate]
    a: Orientation
    b: Orientation


class Specimen(Payload):
    history: History = ()
    visible: Pair = (0, 0)
    reading: Pair | None = None
    channel: Literal["surface", "h-scope", "k-scope"] | None = None

    @model_validator(mode="after")
    def coherent_reading(self):
        if (self.reading is None) != (self.channel is None):
            raise ValueError("a reading requires its channel")
        return self


class Stock(Payload):
    pass


class Investigation(Payload):
    theory: Literal[0, 3]
    discovery: Literal[0, 5]
    mission_room: Literal["array"] = "array"
    stock_room: Literal["array", "stores"] = "stores"
    resolved: Truth | None = None
    procedure: History | None = None
    experimental: Literal[True] = True

    @model_validator(mode="after")
    def disclosure(self):
        if (self.theory, self.discovery) not in ((0, 0), (3, 5)):
            raise ValueError("history supports T0/D0 control or experimental T3/D5")
        if (self.resolved is not None) != (self.theory == 0) or (self.procedure is not None) != (
            self.theory == 0
        ):
            raise ValueError("only T0 supplies the laws and a procedure")
        return self


SCHEMAS = {"artifact": Specimen, "stock": Stock, "investigation": Investigation, "truth": Truth}
