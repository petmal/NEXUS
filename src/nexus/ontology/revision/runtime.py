"""Runtime boundary: new network physics, unchanged transactional game mechanics."""

from nexus.models.world import INVENTORY, TerminalStatus
from nexus.ontology.discovery.runtime import (
    assess_mission as discovery_assess_mission,
)
from nexus.ontology.discovery.runtime import (
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
from nexus.ontology.revision.assistance import check_readings
from nexus.ontology.revision.diagnostics import (
    decision_equivalence_key,
    decision_witness,
)
from nexus.ontology.revision.schema import FAMILY


def public_contract(spec):
    result = contract(FAMILY, spec)
    finish_rule = "Failed eligible finishes are binary and recoverable while actions remain."
    if spec is None:
        # Family-level help has no selected finish policy or optional checker.
        result["ontology"]["contract"] = result["ontology"]["contract"].replace(
            finish_rule, "The episode manifest specifies the finish policy."
        )
        return result
    if spec.data().finish_policy == "single":
        result["ontology"]["contract"] = result["ontology"]["contract"].replace(
            finish_rule,
            "The first rejected eligible complete finish ends the attempt immediately. "
            "Ineligible finishes do not test a construction and remain recoverable.",
        )
    if checker_available(spec):
        result["ontology"]["assistance"] = {
            "operation": "check",
            "request": {"operation": "check", "build": [0, 0, 0, 0]},
            "scope": "Tests only archive and observed reader outputs; not full correctness, "
            "support, or prior failed finishes. No alternatives or new observations returned.",
            "cost": "No world action; consumes a harness tool call and records evidence_turn.",
        }
    return result


def assess_mission(episode, state):
    discovery_assess_mission(episode, state)
    if (
        episode.public.investigation.data().finish_policy == "single"
        and not state.mission_accepted
        and state.agent_room == "workshop"
        and state.artifacts["carrier"].location == INVENTORY
        and submitted(state) is not None
    ):
        state.terminal_status = TerminalStatus.FAILED


def termination_reason(spec, state, trace):
    if (
        spec.data().finish_policy == "single"
        and state.terminal_status == TerminalStatus.FAILED
        and trace
        and trace[-1].action.type == "finish"
        and state.agent_room == "workshop"
        and state.artifacts["carrier"].location == INVENTORY
        and submitted(state) is not None
    ):
        return "single_shot_rejection"
    return None


def checker_available(spec):
    return spec.data().consistency_check == "readings"


def check_construction(spec, observations, build):
    return check_readings(spec.data(), observations, build)


def measurement_features(observed):
    from nexus.ontology.revision.laws import QUERY_INDEX

    return QUERY_INDEX[tuple(observed.sample["query"])], False


__all__ = [
    "assess_mission",
    "belief",
    "check_construction",
    "checker_available",
    "configure",
    "decision_equivalence_key",
    "decision_witness",
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
    "termination_reason",
    "transform",
    "validate_episode",
]
