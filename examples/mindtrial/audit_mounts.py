"""Operator-only MindTrial v0.26 storage; never alter a qualified row or player tool."""

from pathlib import Path

TARGET = "/nexus-audits"
INPUT = "audit-dir"


def configure_service(settings, source):
    service, = (s for s in settings["services"] if s["name"] == "nexus")
    service.setdefault("bind-mounts", []).append(
        {"source": str(source), "target": TARGET, "writable": True}
    )
    service["input-env"][INPUT] = "NEXUS_AUDIT_DIR"


def configure_tasks(taskset):
    # MindTrial merges suite defaults with each row's seed and world settings.
    defaults = taskset.setdefault("tool-selector", {}).setdefault("service-inputs", {}).setdefault("nexus", {})
    defaults[INPUT] = TARGET + "/{{ .Service.InstanceID }}"


def panel_source(directory):
    # Beside results/, so the normal results archive does not include verifier secrets.
    return Path("..") / ".." / "private-audits" / directory.name
