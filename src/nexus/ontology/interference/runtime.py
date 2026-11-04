"""Canonical-vector adapter; generic engine owns charging, atomicity and receipts."""

import json
import logging
from dataclasses import dataclass

from nexus.models.actions import action_contract
from nexus.models.domain import DomainArtifact
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import INVENTORY
from nexus.ontology.inference import Measurement
from nexus.ontology.interference.laws import step
from nexus.ontology.interference.planner import actions_for, optimal
from nexus.ontology.interference.schema import FAMILY, Specimen

performance_style = "mission"
requires_single_session = True


def validate_episode(episode):
    from nexus.ontology.interference.evidence import files
    from nexus.ontology.interference.generation import (
        DESCRIPTION,
        certificate,
        initial_state,
        metadata,
        rooms_for,
        selection,
    )

    public = episode.public
    spec = public.investigation.data()
    truth = episode.investigation_truth.data()
    meta = episode.generation_metadata
    admitted = selection(episode.construction_seed)
    if truth != admitted.world or spec.target not in (admitted.short, admitted.long):
        raise ValueError("interference coefficients or target differ from construction seed")
    if spec.resolved != truth:
        raise ValueError("disclosed law contradicts physical truth")
    if meta.resource_pressure not in (0, 1, 2) or meta.budget_profile != "standard":
        raise ValueError("unsupported interference budget profile")
    proof = certificate(spec, meta.resource_pressure, admitted)
    if (
        public.description != DESCRIPTION
        or public.evidence_files != files(spec)
        or public.initial_state != initial_state(spec, proof["action_budget"])
        or public.rooms != rooms_for(spec)
        or public.edges != ()
        or public.phase_modulus != 1
        or public.goal != GoalPredicate(kind=GoalKind.MISSION_ACCEPTED)
        or public.protocol_version != "nexus-0.2"
        or episode.rules
        or episode.machine_rules
        or episode.reference_plan
        or not episode.verifier_secret
    ):
        raise ValueError("interference public world differs from compiled contract")
    if meta != metadata(spec, meta.resource_pressure, proof):
        raise ValueError("interference metadata differs from compiled contract")


def spawn(stock, artifact_id):
    raise ValueError("this world has one original seal and no specimen stock")


def configure(episode, state, action):
    raise ValueError("coordinate modes accept operate/probe, not configure")


def transform(artifact, machine, episode, instrument_settings=None):
    spec = episode.public.investigation.data()
    mode = next(
        (index for index, item in enumerate(spec.topology) if item.machine == machine), None
    )
    if mode is None or instrument_settings is not None or artifact.id != "seal":
        raise ValueError("unknown coordinate mode, specimen or unsupported settings")
    registers = step(
        episode.investigation_truth.data(), spec.options, artifact.data().registers, mode
    )
    return DomainArtifact(
        ontology=FAMILY,
        id=artifact.id,
        location=artifact.location,
        payload=Specimen(registers=registers).model_dump(mode="json"),
    )


def mission_room(spec):
    return spec.data().mission_room


def mission_machine(spec):
    return spec.data().topology[0].machine


def expected(episode):
    return episode.public.investigation.data().target


def submitted(state):
    return state.artifacts["seal"].data().registers


def assess_mission(episode, state):
    spec = episode.public.investigation.data()
    state.mission_accepted = (
        state.agent_room == spec.mission_room
        and state.artifacts["seal"].location == INVENTORY
        and submitted(state) == spec.target
    )


def physical_plan(episode):
    spec = episode.public.investigation.data()
    return actions_for(spec, optimal(spec).modes)


def remaining_physical_actions(public_spec, state):
    """Private diagnostic hook; all apparatus and the seal share one room."""
    from nexus.ontology.interference.laws import encode
    from nexus.ontology.interference.planner import continuation_distances

    spec = public_spec.data()
    artifact = state.artifacts["seal"]
    distance = continuation_distances(spec)[encode(artifact.data().registers)]
    return None if distance < 0 else distance + 1 + int(artifact.location != INVENTORY)


def measurement(record):
    action = record.action
    if action.type not in ("operate", "probe"):
        return None
    payload = next(
        event.details["result"]["payload"] for event in record.events if "result" in event.details
    )
    return Measurement(action.machine, {**payload, "committed": action.type == "operate"})


def measurement_features(item):
    bank, register = item.instrument.removeprefix("bank").split("_r")
    # Stable coordinate identifier across dimensions (not an array offset).
    return int(bank) * 3 + int(register), item.sample["committed"]


def belief(spec):
    from nexus.ontology.interference.inference import Belief

    return Belief(spec.data())


@dataclass
class Tracker:
    room: str
    mission: str
    location: str
    registers: tuple[int, ...]

    def observe(self, record):
        action = record.action
        if action.type == "move":
            self.room = action.target
        elif action.type == "take" and action.artifact == "seal":
            self.location = INVENTORY
        elif action.type == "drop" and action.artifact == "seal":
            self.location = self.room
        elif action.type == "operate" and action.artifact == "seal":
            item = measurement(record)
            if item is None:
                raise ValueError("committed coordinate operation lacks its public measurement")
            self.registers = tuple(item.sample["registers"])

    def attempted(self):
        return self.registers if self.location == INVENTORY and self.room == self.mission else None


def mission_tracker(public):
    return Tracker(
        public.initial_state.agent_room,
        mission_room(public.investigation),
        public.initial_state.artifacts["seal"].location,
        public.initial_state.artifacts["seal"].data().registers,
    )


def public_contract(spec):
    result = action_contract()
    result["ontology"] = {
        "family": FAMILY,
        "experimental": True,
        "modes": () if spec is None else tuple(item.machine for item in spec.data().topology),
        "configuration": {},
        "mission": "Carry the original seal in array with every public register at its target, then finish.",
        "contract": (
            "Read all evidence files. Every current register and update law is public. "
            "Modes and locations are in theory.json and layout.json. Operations commit "
            "a simultaneous two-register update when its public prerequisite holds; otherwise no change at the same action cost. Probes preview without changing state. No reset, "
            "collapse, stock, hidden map or supplied solution procedure."
        ),
    }
    return result


def log_terminal(spec, calibration_count, no_signal_count, after_resolved_count, first_classes):
    logging.getLogger("nexus.diagnostics").info(
        "interference_terminal known_laws=1 public_vector=true decision_scope=immediate_finish "
        "first_submission_acceptance_classes=%s operations_after_ready=%s",
        first_classes,
        after_resolved_count,
    )


def log_terminal_trace(state, trace, posterior):
    registers = (0,) * posterior.spec.options.count
    breaks = unchanged = blocks = 0
    previous_bank = None
    for record in trace:
        if record.action.type != "operate":
            continue
        item = measurement(record)
        after = tuple(item.sample["registers"])
        breaks += any(
            before == target and later != target
            for before, later, target in zip(registers, after, posterior.spec.target, strict=True)
        )
        unchanged += registers == after
        bank = record.action.machine.split("_", 1)[0]
        blocks += bank != previous_bank
        previous_bank, registers = bank, after
    logging.getLogger("nexus.diagnostics").info(
        "interference_trajectory committed=%s counterfactual=%s remaining_laws=1 "
        "remaining_physical_states=1 immediate_finish_supported=%s "
        "coordinate_goal_breaking_operations=%s unchanged_operations=%s bank_blocks=%s",
        sum(record.action.type == "operate" for record in trace),
        sum(record.action.type == "probe" for record in trace),
        state.agent_room == posterior.spec.mission_room
        and state.artifacts["seal"].location == INVENTORY
        and posterior.supports(posterior.registers),
        breaks,
        unchanged,
        blocks,
    )

    from nexus.ontology.interference.structure import trajectory

    logging.getLogger("nexus.diagnostics").info(
        "interference_structure %s",
        json.dumps(trajectory(posterior.spec, trace), sort_keys=True, separators=(",", ":")),
    )
