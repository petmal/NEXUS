"""Runtime boundary: new network physics, unchanged transactional game mechanics."""

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
from nexus.ontology.revision.schema import FAMILY


def public_contract(spec):
    return contract(FAMILY, spec)


def measurement_features(observed):
    from nexus.ontology.revision.laws import QUERY_INDEX

    return QUERY_INDEX[tuple(observed.sample["query"])], False


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
