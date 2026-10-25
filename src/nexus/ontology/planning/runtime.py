"""Spatial adapter; reuse the unchanged stateful physics and belief semantics."""

from nexus.models.domain import DomainArtifact
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.ontology.planning.planner import actions_for, optimal
from nexus.ontology.planning.schema import FAMILY
from nexus.ontology.stateful import runtime as stateful
from nexus.ontology.stateful.laws import MODES, WORLD_INDEX, history_states, readout
from nexus.ontology.stateful.schema import Specimen

performance_style = "mission"
requires_single_session = True
spawn = stateful.spawn
configure = stateful.configure
mission_room = stateful.mission_room
mission_machine = stateful.mission_machine
submitted = stateful.submitted
expected = stateful.expected
assess_mission = stateful.assess_mission
measurement = stateful.measurement
measurement_features = stateful.measurement_features
belief = stateful.belief
mission_tracker = stateful.mission_tracker
log_terminal = stateful.log_terminal
log_terminal_trace = stateful.log_terminal_trace


def validate_episode(episode):
    from nexus.ontology.planning.evidence import files
    from nexus.ontology.planning.generation import (
        DESCRIPTION,
        certificate,
        initial_state,
        metadata,
        rooms_for,
        selection,
    )
    from nexus.ontology.planning.layout import LAYOUTS

    public = episode.public
    spec = public.investigation.data()
    truth = episode.investigation_truth.data()
    meta = episode.generation_metadata
    if type(episode.construction_seed) is not int or (truth, spec.target) != selection(
        episode.construction_seed
    ):
        raise ValueError("planning laws or target differ from construction seed")
    if spec.resolved is not None and spec.resolved != truth:
        raise ValueError("disclosed law contradicts physics")
    if meta.resource_pressure not in range(3) or meta.budget_profile != "standard":
        raise ValueError("unsupported planning budget profile")
    proof = certificate(spec, meta.resource_pressure)
    if (
        public.description != DESCRIPTION
        or public.evidence_files != files(spec)
        or public.initial_state != initial_state(spec, proof["action_budget"])
        or public.rooms != rooms_for(spec)
        or public.edges != LAYOUTS[spec.planning].edges
        or public.phase_modulus != 1
        or public.goal != GoalPredicate(kind=GoalKind.MISSION_ACCEPTED)
        or episode.rules
        or episode.machine_rules
    ):
        raise ValueError("planning public world differs from compiled contract")
    if meta != metadata(spec, meta.resource_pressure, proof):
        raise ValueError("planning metadata differs from compiled contract")


def transform(artifact, machine, episode, instrument_settings=None):
    if machine not in MODES or instrument_settings is not None:
        raise ValueError("unknown mode or unsupported mode settings")
    history = (*artifact.data().history, MODES.index(machine))
    state = history_states(history)[WORLD_INDEX[episode.investigation_truth.data()]]
    return DomainArtifact(
        ontology=FAMILY,
        id=artifact.id,
        location=artifact.location,
        payload=Specimen(history=history, reading=readout(state)).model_dump(mode="json"),
    )


def physical_plan(episode):
    spec = episode.public.investigation.data()
    plan = optimal(episode.investigation_truth.data(), spec.target, spec.planning)
    return actions_for(plan.modes, spec.planning)


def public_contract(spec):
    result = stateful.public_contract(spec)
    result["ontology"].update(
        family=FAMILY,
        contract="Read every evidence file, including the complete layout.json. Modes require the carried seal at their disclosed locations. Operations commit changes; one-step probes do not. Return to array and finish. No reset, stock or hidden map.",
    )
    return result
