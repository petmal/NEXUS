"""Uncertainty adapter over the common persistent discovery runtime."""

from nexus.ontology.discovery.runtime import (
    assess_mission,
    belief,
    configure,
    contract,
    expected,
    log_terminal,
    log_terminal_trace,
    measurement,
    mission_machine,
    mission_room,
    mission_tracker,
    performance_style,
    physical_plan,
    requires_single_session,
    spawn,
    submitted,
    transform,
    validate_episode,
)
from nexus.ontology.uncertainty.schema import FAMILY


def public_contract(spec):
    return contract(FAMILY, spec)


def measurement_features(observed):
    mode, fixture = observed.sample["query"]
    return 8 * mode + fixture, False


__all__ = [
    "assess_mission",
    "belief",
    "configure",
    "expected",
    "log_terminal",
    "log_terminal_trace",
    "measurement",
    "measurement_features",
    "mission_machine",
    "mission_room",
    "mission_tracker",
    "performance_style",
    "physical_plan",
    "public_contract",
    "requires_single_session",
    "spawn",
    "submitted",
    "transform",
    "validate_episode",
]
