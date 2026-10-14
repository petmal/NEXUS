"""Data-only public/hidden roles for the sealed-array construction."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

FAMILY = "coupled-repair-v1"
Q = 7
Scalar = Annotated[StrictInt, Field(ge=0, le=6)]
Dose = tuple[Scalar, Scalar, Scalar, Scalar]
Context = tuple[Literal[0, 1], Scalar]


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Specimen(Payload):
    material: Literal["survey", "seal"] = "survey"
    context: Context | None = None
    charged: bool = False
    doses: Dose | None = None
    reading: tuple[Scalar, ...] | None = None
    instrument: Literal["reference", "reader"] | None = None

    @model_validator(mode="after")
    def physical_roles(self):
        if self.material == "seal" and (self.context is not None or self.charged):
            raise ValueError("seal material has no survey orientation or charge")
        if self.material == "survey" and self.doses is not None:
            raise ValueError("survey material cannot hold seal doses")
        if self.charged and self.context is None:
            raise ValueError("charging requires an orientation")
        return self


class Stock(Payload):
    material: Literal["survey"] = "survey"


class Truth(Payload):
    a: Scalar
    b: Scalar
    c: Scalar
    r: Scalar
    degree: Literal[1, 2, 3]


class Investigation(Payload):
    theory: Literal[3] = 3
    discovery: Literal[5] = 5
    mission_room: str
    stock_room: str
    profile: Literal["stationary-three-round-v1"] = "stationary-three-round-v1"
    # Qualification is task structure, not a claim of empirically calibrated LLM failure.
    experimental: bool = True


SCHEMAS = {"artifact": Specimen, "stock": Stock, "investigation": Investigation, "truth": Truth}
