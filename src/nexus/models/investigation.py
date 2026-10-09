"""Declarative scientific apparatus and its separate public/private contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ScalarExpression(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    op: Literal["constant", "variable", "add", "multiply", "power"]
    value: int | str | None = None
    children: tuple[ScalarExpression, ...] = ()

    @model_validator(mode="after")
    def valid_shape(self):
        if self.op == "constant":
            if type(self.value) is not int or self.children:
                raise ValueError("constant requires an integer and no children")
        elif self.op == "variable":
            if self.value not in ("a", "q", "c") or self.children:
                raise ValueError("unknown scalar variable")
        elif self.value is not None or len(self.children) != 2:
            raise ValueError("scalar operator requires two children")
        return self


class InvestigationSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    version: Literal["scientific-v2"] = "scientific-v2"
    theory: int = Field(ge=0, le=3)
    discovery: int = Field(ge=0, le=5)
    scale: int = Field(ge=1, le=16)
    modulus: Literal[17] = 17
    target_q: tuple[int, ...] = (4, 5, 6, 7)
    known_selector: int | None = Field(default=0, ge=0, le=1)
    known_coefficient: int | None = Field(default=None, ge=1, le=3)
    known_exponent: int | None = Field(default=None, ge=1, le=3)
    offset_unknown: bool = True
    both_stocks: bool = False
    material_meter: bool = False
    preparation_required: bool = False
    controller_room: str
    supplied_measurements: tuple[tuple[str, int], ...] = ()
    resolved_settings: tuple[int, ...] | None = None


class InvestigationTruth(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    selector: int = Field(ge=0, le=1)
    properties: tuple[int, int]
    offset: Literal[0, 2]
    coefficient: int = Field(ge=1, le=3)
    exponent: int = Field(ge=1, le=3)
    response: ScalarExpression

    @model_validator(mode="after")
    def bounded_properties(self):
        if any(type(a) is not int or not 0 <= a <= 3 for a in self.properties):
            raise ValueError("specimen properties must be integers in 0..3")
        return self


class SampleState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source: Literal["reference", "0", "1"]
    q: int = Field(ge=0, le=2)
    reading: int | None = Field(default=None, ge=0, le=16)


class SpecimenStock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    location: str
    source: Literal["reference", "0", "1"]
    q: int = Field(ge=0, le=2)
    remaining: int | None = Field(default=None, ge=0)
