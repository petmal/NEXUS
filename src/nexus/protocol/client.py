from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from nexus.models.actions import Action
from nexus.protocol.transport import (
    ClientError,
    check_health,
    request_service_payload,
    service_url,
    validate_candidate_payload,
)


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


ServiceRequest = Annotated[
    ObserveRequest
    | StatusRequest
    | ManifestRequest
    | EvidenceRequest
    | ActionClientRequest,
    Field(discriminator="operation"),
]
SERVICE_REQUEST_ADAPTER = TypeAdapter(ServiceRequest)


class ValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    correct: bool
    title: str
    explanation: str


def request_service(request: ServiceRequest, *, url: str | None = None) -> object:
    return request_service_payload(request.model_dump(mode="json"), url=url)


def validate_candidate(candidate: str, *, url: str | None = None) -> ValidationResult:
    return ValidationResult.model_validate(validate_candidate_payload(candidate, url=url))
