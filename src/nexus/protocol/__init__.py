from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "ActionResponse": ("nexus.protocol.session", "ActionResponse"),
    "ClientError": ("nexus.protocol.client", "ClientError"),
    "SERVICE_REQUEST_ADAPTER": ("nexus.protocol.client", "SERVICE_REQUEST_ADAPTER"),
    "ServiceRequest": ("nexus.protocol.client", "ServiceRequest"),
    "Session": ("nexus.protocol.session", "Session"),
    "SessionStatus": ("nexus.protocol.session", "SessionStatus"),
    "ValidationResult": ("nexus.protocol.client", "ValidationResult"),
    "check_health": ("nexus.protocol.client", "check_health"),
    "request_service": ("nexus.protocol.client", "request_service"),
    "run_jsonl": ("nexus.protocol.stdio", "run_jsonl"),
    "validate_candidate": ("nexus.protocol.client", "validate_candidate"),
}

__all__ = list(_EXPORTS)


def __getattr__(name: str):
    try:
        module_name, attribute = _EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc

    value = getattr(import_module(module_name), attribute)
    globals()[name] = value
    return value
