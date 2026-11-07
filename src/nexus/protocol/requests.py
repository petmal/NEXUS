"""Typed action and player request envelopes shared by the Python and wire interfaces."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, TypeAdapter, field_validator
from pydantic.json_schema import SkipJsonSchema

from nexus.models.actions import Action
from nexus.ontology.assistance import ConstructionCheckRequest

Turn = Annotated[StrictInt, Field(ge=0)]


class ActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_turn: Turn
    action: Action


class ObserveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    operation: Literal["observe"]


class StatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    operation: Literal["status"]


class ManifestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    operation: Literal["manifest"]


class EvidenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    operation: Literal["evidence"]
    filename: str


class ActionClientRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    operation: Literal["action"]
    action: Action
    # Omission selects the current turn; an explicitly supplied null is not a turn.
    expected_turn: Turn | SkipJsonSchema[None] = Field(
        default_factory=lambda: None, exclude_if=lambda v: v is None
    )

    @field_validator("expected_turn")
    @classmethod
    def reject_null_turn(cls, value):
        if value is None:
            raise ValueError("expected_turn must be a nonnegative integer")
        return value


class CheckClientRequest(ConstructionCheckRequest):
    operation: Literal["check"]


ServiceRequest = Annotated[
    ObserveRequest
    | StatusRequest
    | ManifestRequest
    | EvidenceRequest
    | ActionClientRequest
    | CheckClientRequest,
    Field(discriminator="operation"),
]
SERVICE_REQUEST_ADAPTER = TypeAdapter(ServiceRequest)
