from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class GoalKind(StrEnum):
    CONTROLLER_ACCEPTED = "controller_accepted"
    ARTIFACT_FIELD = "artifact_field"
    ARTIFACT_LOCATION = "artifact_location"
    PHASE_EQUALS = "phase_equals"
    AND = "and"
    OR = "or"
    NOT = "not"


class GoalPredicate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: GoalKind
    artifact_id: str | None = None
    field: str | None = None
    value: Any | None = None
    children: tuple["GoalPredicate", ...] = ()

    @model_validator(mode="after")
    def validate_shape(self) -> "GoalPredicate":
        if self.kind == GoalKind.ARTIFACT_FIELD:
            if self.artifact_id is None or self.field is None or self.value is None:
                raise ValueError("artifact_field requires artifact_id, field, value")
        if self.kind == GoalKind.ARTIFACT_LOCATION:
            if self.artifact_id is None or self.value is None:
                raise ValueError("artifact_location requires artifact_id and value")
        if self.kind == GoalKind.PHASE_EQUALS and self.value is None:
            raise ValueError("phase_equals requires value")
        if self.kind in {GoalKind.AND, GoalKind.OR} and len(self.children) < 2:
            raise ValueError(f"{self.kind} requires at least two children")
        if self.kind == GoalKind.NOT and len(self.children) != 1:
            raise ValueError("not requires exactly one child")
        return self


GoalPredicate.model_rebuild()
