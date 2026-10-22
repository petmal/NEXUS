"""Public observations and private compositional laws; no latent state in payloads."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

FAMILY = "stateful-discovery-v1"
Cell = Annotated[StrictInt, Field(ge=0, le=4)]
Mode = Annotated[StrictInt, Field(ge=0, le=3)]
Choice = Annotated[StrictInt, Field(ge=1, le=2)]
Vector = tuple[Cell, Cell, Cell, Cell]


class Payload(BaseModel, frozen=True):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Truth(Payload):
    gains: tuple[Choice, Choice, Choice, Choice]
    powers: tuple[Choice, Choice, Choice, Choice]


class Specimen(Payload):
    history: tuple[Mode, ...] = ()
    reading: Annotated[StrictInt, Field(ge=0, le=5)] = 0


class Investigation(Payload):
    theory: Literal[0, 3]
    discovery: Literal[0, 5]
    target: Vector
    mission_room: Literal["array"] = "array"
    stock_room: Literal["array", "stores"] = "stores"
    resolved: Truth | None = None
    procedure: tuple[Mode, ...] | None = None
    experimental: Literal[True] = True

    @model_validator(mode="after")
    def controls(self):
        if (self.theory, self.discovery) not in ((0, 0), (0, 5), (3, 5)):
            raise ValueError("stateful discovery supports T0/D0, T0/D5 or T3/D5")
        if (self.resolved is not None) != (self.theory == 0):
            raise ValueError("only T0 discloses the laws")
        if (self.procedure is not None) != (self.discovery == 0):
            raise ValueError("only D0 supplies the procedure")
        if self.target in ((0, 0, 0, 0), (4, 4, 4, 4)):
            raise ValueError("target must be noninitial and noncollapsed")
        return self


SCHEMAS = {"artifact": Specimen, "investigation": Investigation, "truth": Truth}
