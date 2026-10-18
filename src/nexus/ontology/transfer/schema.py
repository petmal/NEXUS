"""Public preparations and controller programs; private parameters stay separate."""

from typing import Literal

from pydantic import model_validator

from nexus.ontology.compositional.schema import Gate, Mode, Payload, Trit

CALIBRATED = "coupled-transfer-v1"
COUPLED = "coupled-evidence-v1"
Program = tuple[Trit, Gate, Gate, Gate, Trit, Gate, Trit]
Settings = tuple[Mode, Trit, Trit, Trit, Trit, Trit]


def valid_program(program):
    return program is None or program[program[4] + 1] != program[5]


class Specimen(Payload, frozen=True):
    material: Literal["survey", "reference", "seal"] = "survey"
    settings: Settings = (0, 0, 0, 0, 0, 0)
    reading: Trit | None = None
    doses: Program | None = None

    @model_validator(mode="after")
    def roles(self):
        if self.material == "seal" and (any(self.settings) or self.reading is not None):
            raise ValueError("seal has no survey preparation or reader output")
        if self.material != "seal" and self.doses is not None:
            raise ValueError("only seal accepts a counterprogram")
        if not valid_program(self.doses):
            raise ValueError("replacement must differ from the selected context-0 primitive")
        return self


class Stock(Payload, frozen=True):
    material: Literal["survey", "reference"] = "survey"


class Truth(Payload, frozen=True):
    program: Program
    reader_offset: Trit

    @model_validator(mode="after")
    def replacement(self):
        if not valid_program(self.program):
            raise ValueError("replacement must differ")
        return self


class Investigation(Payload, frozen=True):
    theory: Literal[0, 3]
    discovery: Literal[0, 5]
    coupled: bool
    mission_room: Literal["array"] = "array"
    stock_room: Literal["array", "stores"]
    resolved: Program | None = None
    experimental: Literal[True] = True

    @model_validator(mode="after")
    def disclosure(self):
        if (self.theory, self.discovery) not in ((0, 0), (3, 5)):
            raise ValueError("transfer supports T0/D0 and experimental T3/D5")
        if (self.resolved is not None) != (self.theory == 0) or not valid_program(self.resolved):
            raise ValueError("only the execution control discloses a valid program")
        return self

    @property
    def family(self):
        return COUPLED if self.coupled else CALIBRATED


SCHEMAS = {"artifact": Specimen, "stock": Stock, "investigation": Investigation, "truth": Truth}
