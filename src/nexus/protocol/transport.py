from __future__ import annotations

import hmac
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class ClientError(RuntimeError):
    pass


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
    payload: dict[str, object] | None = None,
    *,
    timeout: float = 10.0,
) -> object:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        base_url.rstrip("/") + path,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"} if body is not None else {},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ClientError(f"service returned HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ClientError(f"service request failed: {exc}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ClientError("service returned an invalid JSON response") from exc


def _text_request(
    base_url: str,
    method: str,
    path: str,
    *,
    timeout: float = 10.0,
) -> str:
    request = Request(base_url.rstrip("/") + path, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ClientError(f"service returned HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ClientError(f"service request failed: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise ClientError("service returned invalid UTF-8 text") from exc


def _object(value: object, description: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ClientError(f"{description} must be a JSON object")
    return value


def _exact_keys(value: dict[str, object], expected: set[str], description: str) -> None:
    missing = expected - value.keys()
    extra = value.keys() - expected
    if missing:
        raise ClientError(f"{description} missing field(s): {', '.join(sorted(missing))}")
    if extra:
        raise ClientError(f"{description} has unknown field(s): {', '.join(sorted(extra))}")


def _parse_status(
    payload: dict[str, object],
    *,
    description: str,
) -> tuple[int, str, int, str | None]:
    turn = payload["turn"]
    status = payload["status"]
    actions_remaining = payload["actions_remaining"]
    victory_code = payload["victory_code"]

    if isinstance(turn, bool) or not isinstance(turn, int):
        raise ClientError(f"{description} field 'turn' must be an integer")
    if not isinstance(status, str) or status not in {"active", "won", "failed"}:
        raise ClientError(f"{description} field 'status' is invalid")
    if isinstance(actions_remaining, bool) or not isinstance(actions_remaining, int):
        raise ClientError(f"{description} field 'actions_remaining' must be an integer")
    if victory_code is not None and not isinstance(victory_code, str):
        raise ClientError(f"{description} field 'victory_code' must be a string or null")

    return turn, status, actions_remaining, victory_code


def _status(base_url: str) -> tuple[int, str, int, str | None]:
    payload = _object(_json_request(base_url, "GET", "/status"), "service status")
    _exact_keys(
        payload,
        {"turn", "status", "actions_remaining", "victory_code"},
        "service status",
    )
    return _parse_status(payload, description="service status")


def _finalize(base_url: str) -> tuple[int, str, int, str | None, dict[str, object]]:
    payload = _object(
        _json_request(base_url, "POST", "/finalize"),
        "service finalization",
    )
    _exact_keys(
        payload,
        {"turn", "status", "actions_remaining", "victory_code", "performance"},
        "service finalization",
    )
    performance = _object(payload["performance"], "service finalization performance")
    status_payload = {key: payload[key] for key in ("turn", "status", "actions_remaining", "victory_code")}
    turn, status, actions_remaining, victory_code = _parse_status(
        status_payload,
        description="service finalization",
    )
    if status == "active":
        raise ClientError("service finalization left the session active")
    return turn, status, actions_remaining, victory_code, performance


def request_service_payload(request: object, *, url: str | None = None) -> object:
    payload = _object(request, "request")
    operation = payload.get("operation")
    if not isinstance(operation, str):
        raise ClientError("request field 'operation' must be a string")

    base_url = service_url(url)
    if operation in {"observe", "status", "manifest"}:
        _exact_keys(payload, {"operation"}, "request")
        return _json_request(base_url, "GET", f"/{operation}")

    if operation == "evidence":
        _exact_keys(payload, {"operation", "filename"}, "request")
        filename = payload["filename"]
        if not isinstance(filename, str):
            raise ClientError("request field 'filename' must be a string")
        content = _text_request(base_url, "GET", f"/evidence/{quote(filename, safe='')}")
        return {"filename": filename, "content": content}

    if operation == "action":
        _exact_keys(payload, {"operation", "action"}, "request")
        action = payload["action"]
        if not isinstance(action, dict):
            raise ClientError("request field 'action' must be a JSON object")
        turn, _, _, _ = _status(base_url)
        return _json_request(
            base_url,
            "POST",
            "/action",
            {"expected_turn": turn, "action": action},
        )

    raise ClientError(f"unsupported request operation: {operation!r}")


def check_health(*, url: str | None = None) -> None:
    payload = _json_request(service_url(url), "GET", "/health", timeout=1.0)
    if not isinstance(payload, dict) or payload.get("status") != "ok":
        raise ClientError("service health check did not report status=ok")


def _validation_result(candidate: str, status: str, victory_code: str | None) -> dict[str, object]:
    if status != "won":
        return {
            "correct": False,
            "title": "Mission not complete",
            "explanation": f"NEXUS is in terminal state {status!r}, not 'won'.",
        }
    if victory_code is None:
        raise ClientError("won session did not expose a victory code")

    supplied = candidate.strip().encode("utf-8")
    expected = victory_code.encode("utf-8")
    if hmac.compare_digest(supplied, expected):
        return {
            "correct": True,
            "title": "Valid victory code",
            "explanation": "The session is won and the submitted victory code matches it.",
        }
    return {
        "correct": False,
        "title": "Invalid victory code",
        "explanation": "The session is won, but the submitted victory code does not match it.",
    }


def validate_candidate_payload_with_performance(
    candidate: str,
    *,
    url: str | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    _, status, _, victory_code, performance = _finalize(service_url(url))
    return _validation_result(candidate, status, victory_code), performance


def validate_candidate_payload(candidate: str, *, url: str | None = None) -> dict[str, object]:
    result, _ = validate_candidate_payload_with_performance(candidate, url=url)
    return result
