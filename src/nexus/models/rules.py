from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ConditionKind(StrEnum):
    ALWAYS = "always"
    EQUALS = "equals"
    PHASE_EQUALS = "phase_equals"
    PHASE_PARITY = "phase_parity"
    VALUE_MODULO = "value_modulo"
    AND = "and"
    OR = "or"
    NOT = "not"


class EffectKind(StrEnum):
    ADD_MOD = "add_mod"
    MULTIPLY_MOD = "multiply_mod"
    TOGGLE = "toggle"
    ROTATE = "rotate"
    SET = "set"
    SEQUENCE = "sequence"
    CONDITIONAL = "conditional"


class Condition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: ConditionKind
    field: str | None = None
    value: Any | None = None
    modulus: int | None = Field(default=None, ge=1)
    remainder: int | None = Field(default=None, ge=0)
    parity: str | None = None
    children: tuple["Condition", ...] = ()

    @model_validator(mode="after")
    def validate_shape(self) -> "Condition":
        if self.kind == ConditionKind.EQUALS and (self.field is None or self.value is None):
            raise ValueError("equals requires field and value")
        if self.kind == ConditionKind.PHASE_EQUALS and self.value is None:
            raise ValueError("phase_equals requires value")
        if self.kind == ConditionKind.PHASE_PARITY and self.parity not in {"even", "odd"}:
            raise ValueError("phase_parity requires parity even|odd")
        if self.kind == ConditionKind.VALUE_MODULO:
            if self.modulus is None or self.remainder is None or self.remainder >= self.modulus:
                raise ValueError("value_modulo requires 0 <= remainder < modulus")
        if self.kind in {ConditionKind.AND, ConditionKind.OR} and len(self.children) < 2:
            raise ValueError(f"{self.kind} requires at least two children")
        if self.kind == ConditionKind.NOT and len(self.children) != 1:
            raise ValueError("not requires exactly one child")
        return self


class Effect(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: EffectKind
    field: str | None = None
    value: Any | None = None
    amount: int | None = None
    multiplier: int | None = None
    modulus: int | None = Field(default=None, ge=1)
    condition: Condition | None = None
    effects: tuple["Effect", ...] = ()
    else_effects: tuple["Effect", ...] = ()

    @model_validator(mode="after")
    def validate_shape(self) -> "Effect":
        if self.kind == EffectKind.ADD_MOD:
            if self.field != "value" or self.amount is None or self.modulus is None:
                raise ValueError("add_mod requires field='value', amount, modulus")
        if self.kind == EffectKind.MULTIPLY_MOD:
            if self.field != "value" or self.multiplier is None or self.modulus is None:
                raise ValueError("multiply_mod requires field='value', multiplier, modulus")
        if self.kind == EffectKind.TOGGLE and self.field != "polarity":
            raise ValueError("toggle currently supports only polarity")
        if self.kind == EffectKind.ROTATE and self.amount is None:
            raise ValueError("rotate requires amount")
        if self.kind == EffectKind.SET and (self.field is None or self.value is None):
            raise ValueError("set requires field and value")
        if self.kind == EffectKind.SEQUENCE and not self.effects:
            raise ValueError("sequence requires effects")
        if self.kind == EffectKind.CONDITIONAL and (self.condition is None or not self.effects):
            raise ValueError("conditional requires condition and effects")
        return self


Condition.model_rebuild()
Effect.model_rebuild()
