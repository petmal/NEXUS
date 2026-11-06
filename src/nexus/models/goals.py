from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

from nexus.models.world import Orientation, Pattern, Polarity, Shape

ARTIFACT_ENUM_FIELDS = {
    "shape": Shape, "pattern": Pattern, "orientation": Orientation, "polarity": Polarity,
}

class GoalKind(StrEnum):
    MISSION_ACCEPTED = "mission_accepted"
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
            if self.field == "value":
                if type(self.value) is not int:
                    raise ValueError("artifact value goal requires an integer")
            elif self.field in ARTIFACT_ENUM_FIELDS:
                ARTIFACT_ENUM_FIELDS[self.field](self.value)
            else:
                raise ValueError("artifact_field requires an intrinsic artifact field")
        if self.kind == GoalKind.ARTIFACT_LOCATION:
            if self.artifact_id is None or not isinstance(self.value, str) or not self.value:
                raise ValueError("artifact_location requires artifact_id and a nonempty location")
        if self.kind == GoalKind.PHASE_EQUALS:
            if type(self.value) is not int or self.value < 0:
                raise ValueError("phase_equals requires a nonnegative integer")
        if self.kind in {GoalKind.AND, GoalKind.OR} and len(self.children) < 2:
            raise ValueError(f"{self.kind} requires at least two children")
        if self.kind == GoalKind.NOT and len(self.children) != 1:
            raise ValueError("not requires exactly one child")
        return self


GoalPredicate.model_rebuild()
