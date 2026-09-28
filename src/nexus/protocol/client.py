from __future__ import annotations

import hmac
import json
import os
from typing import Annotated, Literal
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from nexus.models.actions import Action
from nexus.models.world import TerminalStatus
from nexus.protocol.session import SessionStatus


class ClientError(RuntimeError):
    pass


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


def service_url(url: str | None = None) -> str:
    if url:
        return url.rstrip("/")
    configured = os.getenv("NEXUS_URL")
    if configured:
        return configured.rstrip("/")
    port = os.getenv("NEXUS_PORT", "8000")
    return f"http://127.0.0.1:{port}"


def _json_request(
    base_url: str,
    method: str,
    path: str,
    payload: dict | None = None,
) -> object:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        base_url.rstrip("/") + path,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"} if body is not None else {},
    )
    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ClientError(f"service returned HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ClientError(f"service request failed: {exc}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ClientError("service returned an invalid JSON response") from exc


def _text_request(base_url: str, method: str, path: str) -> str:
    request = Request(base_url.rstrip("/") + path, method=method)
    try:
        with urlopen(request, timeout=10) as response:
            return response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ClientError(f"service returned HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ClientError(f"service request failed: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise ClientError("service returned invalid UTF-8 text") from exc


def request_service(request: ServiceRequest, *, url: str | None = None) -> object:
    base_url = service_url(url)
    if isinstance(request, ObserveRequest):
        return _json_request(base_url, "GET", "/observe")
    if isinstance(request, StatusRequest):
        return _json_request(base_url, "GET", "/status")
    if isinstance(request, ManifestRequest):
        return _json_request(base_url, "GET", "/manifest")
    if isinstance(request, EvidenceRequest):
        text = _text_request(base_url, "GET", f"/evidence/{quote(request.filename, safe='')}")
        return {"filename": request.filename, "content": text}
    if isinstance(request, ActionClientRequest):
        status = SessionStatus.model_validate(_json_request(base_url, "GET", "/status"))
        return _json_request(
            base_url,
            "POST",
            "/action",
            {
                "expected_turn": status.turn,
                "action": request.action.model_dump(mode="json"),
            },
        )
    raise TypeError(f"unsupported request type: {type(request).__name__}")


def check_health(*, url: str | None = None) -> None:
    payload = _json_request(service_url(url), "GET", "/health")
    if not isinstance(payload, dict) or payload.get("status") != "ok":
        raise ClientError("service health check did not report status=ok")


def validate_candidate(candidate: str, *, url: str | None = None) -> ValidationResult:
    status = SessionStatus.model_validate(_json_request(service_url(url), "GET", "/status"))
    if status.status != TerminalStatus.WON:
        return ValidationResult(
            correct=False,
            title="Mission not complete",
            explanation=f"NEXUS is in terminal state {status.status.value!r}, not 'won'.",
        )
    if status.victory_code is None:
        raise ClientError("won session did not expose a victory code")

    supplied = candidate.strip().encode("utf-8")
    expected = status.victory_code.encode("utf-8")
    if hmac.compare_digest(supplied, expected):
        return ValidationResult(
            correct=True,
            title="Valid victory code",
            explanation="The session is won and the submitted victory code matches it.",
        )
    return ValidationResult(
        correct=False,
        title="Invalid victory code",
        explanation="The session is won, but the submitted victory code does not match it.",
    )
