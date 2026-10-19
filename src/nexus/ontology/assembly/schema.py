"""Data-only schemas; prepared components expose settings, never hidden law values."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

FAMILY = "joint-assembly-v1"
Trit = Annotated[StrictInt, Field(ge=0, le=2)]
Gain = Annotated[StrictInt, Field(ge=1, le=2)]
Kernel = Annotated[StrictInt, Field(ge=0, le=3)]
Component = tuple[Gain, Trit]


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Truth(Payload):
    gain_b: Gain
    phase_b: Trit
    gain_c: Gain
    phase_c: Trit
    kernel: Kernel
    offset: Trit


class Reading(Payload):
    channel: Trit
    x: Trit
    y: Trit
    value: Trit


class Specimen(Payload):
    b: Component | None = None
    c: Component | None = None
    kernel: Kernel | None = None
    reading: Reading | None = None

    @model_validator(mode="after")
    def assembled_components(self):
        if self.kernel is not None and (self.b is None or self.c is None):
            raise ValueError("an assembled device requires both prepared components")
        return self


class Stock(Payload):
    kind: Literal["blank-carrier"] = "blank-carrier"


class Investigation(Payload):
    theory: Literal[0, 2, 3]
    discovery: Literal[0, 3, 4]
    stock_room: Literal["stores", "workshop"] = "workshop"
    known_kernel: Kernel | None = None
    resolved: Truth | None = None
    experimental: Literal[True] = True

    @property
    def coupled_reader(self) -> bool:
        return self.discovery != 3

    @model_validator(mode="after")
    def disclosure(self):
        if (self.theory == 0) != (self.discovery == 0):
            raise ValueError("assembly control requires T0/D0; science requires T2/T3 D3/D4")
        if (self.known_kernel is not None) != (self.theory == 2):
            raise ValueError("only T2 discloses the joint kernel")
        if (self.resolved is not None) != (self.theory == 0):
            raise ValueError("only T0 supplies exact laws")
        return self


SCHEMAS = {"artifact": Specimen, "stock": Stock, "investigation": Investigation, "truth": Truth}
