from __future__ import annotations

from pydantic import BaseModel, ConfigDict

# Keep the Python client import surface stable; JSONL also uses these envelopes.
from nexus.protocol.requests import (
    SERVICE_REQUEST_ADAPTER,
    ActionClientRequest as ActionClientRequest,
    CheckClientRequest as CheckClientRequest,
    EvidenceRequest as EvidenceRequest,
    ManifestRequest as ManifestRequest,
    ObserveRequest as ObserveRequest,
    ServiceRequest,
    StatusRequest as StatusRequest,
)
from nexus.protocol.transport import (
    ClientError,
    check_health,
    request_service_payload,
    service_url,
    validate_candidate_payload,
    validate_candidate_payload_with_performance,
)

__all__ = [
    "SERVICE_REQUEST_ADAPTER",
    "ClientError",
    "ServiceRequest",
    "ValidationResult",
    "check_health",
    "request_service",
    "service_url",
    "validate_candidate",
    "validate_candidate_with_performance",
]


class ValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    correct: bool
    title: str
    explanation: str


def request_service(request: ServiceRequest, *, url: str | None = None) -> object:
    return request_service_payload(request.model_dump(mode="json"), url=url)


def validate_candidate(candidate: str, *, url: str | None = None) -> ValidationResult:
    return ValidationResult.model_validate(validate_candidate_payload(candidate, url=url))


def validate_candidate_with_performance(
    candidate: str,
    *,
    url: str | None = None,
) -> tuple[ValidationResult, dict[str, object]]:
    result, performance = validate_candidate_payload_with_performance(candidate, url=url)
    return ValidationResult.model_validate(result), performance
