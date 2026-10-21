"""Coupled-memory adapter over the common persistent discovery runtime."""

from nexus.ontology.discovery.runtime import (
    assess_mission,
    belief,
    configure,
    contract,
    expected,
    log_terminal,
    log_terminal_trace as shared_log_terminal_trace,
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
from nexus.ontology.coupled_memory.schema import FAMILY


def log_terminal_trace(state, trace, posterior):
    import logging
    from nexus.ontology.coupled_memory.laws import PROGRAMS

    shared_log_terminal_trace(state, trace, posterior)
    remaining = [p for i, p in enumerate(PROGRAMS) if posterior.mask >> i & 1]
    logging.getLogger("nexus.diagnostics").info(
        "coupled_memory_terminal remaining_dynamics=%s remaining_encoders=%s remaining_behavior_classes=%s parameter_identity_required=false conservation=exact_discrete deep_tier_admitted=false",
        len({p[:4] for p in remaining}),
        len({p[4:] for p in remaining}),
        posterior.counts()[1],
    )


def public_contract(spec):
    return contract(FAMILY, spec)


def measurement_features(observed):
    from nexus.ontology.coupled_memory.laws import QUERY_INDEX

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
