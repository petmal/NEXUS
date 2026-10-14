"""Thin adapter; the engine owns mutations, resources, terminal state and receipt."""

from dataclasses import dataclass
from typing import cast

from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    MoveAction,
    OperateAction,
    TakeAction,
    action_contract,
)
from nexus.models.domain import DomainArtifact
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import INVENTORY, Room
from nexus.ontology.inference import Measurement
from nexus.ontology.repair import laws
from nexus.ontology.repair.schema import FAMILY, Specimen

APPARATUS = ("reference", "stage", "coupler", "reader", "doser")


def validate_episode(episode):
    spec = episode.public.investigation.data()
    state = episode.public.initial_state
    from nexus.ontology.repair.evidence import files
    from nexus.ontology.repair.generation import DESCRIPTION, initial_state

    expected_state = initial_state(spec.stock_room, spec.mission_room)
    if state != expected_state:
        raise ValueError("repair initial state/resources are outside the proved profile")
    if (
        episode.public.goal != GoalPredicate(kind=GoalKind.MISSION_ACCEPTED)
        or episode.public.phase_modulus != 1
    ):
        raise ValueError("repair mission or phase contract mismatch")
    if episode.public.description != DESCRIPTION or episode.public.protocol_version != "nexus-0.2":
        raise ValueError("repair public presentation contract mismatch")
    if spec.mission_room != "array" or spec.stock_room not in ("array", "stores"):
        raise ValueError("repair room identifiers are outside the public template")
    rooms = {spec.stock_room, spec.mission_room}
    edges = () if len(rooms) == 1 else ((spec.stock_room, spec.mission_room),)
    expected_rooms = {
        room: Room(id=room, label="Sealed array" if room == "array" else "Material stores")
        for room in rooms
    }
    if episode.public.rooms != expected_rooms or episode.public.edges != edges:
        raise ValueError("repair topology is outside the proved profile")
    if episode.rules or episode.machine_rules:
        raise ValueError("repair profile does not admit extra latent machine rules")
    if episode.public.evidence_files != files(spec):
        raise ValueError("repair public disclosure differs from the proved grammar")
    if type(
        episode.construction_seed
    ) is not int or episode.investigation_truth.data() != laws.world_at(episode.construction_seed):
        raise ValueError("repair seed and selected truth disagree")
    metadata = episode.generation_metadata
    if (
        metadata.theory_level,
        metadata.discovery_level,
        metadata.planning_level,
        metadata.resource_pressure,
    ) != (3, 5, int(len(rooms) > 1), 1):
        raise ValueError("repair axis labels differ from the supported profile")

    from nexus.ontology.repair.qualification import certificate, release_matches

    p = int(len(rooms) > 1)
    if (
        metadata.investigation_certificate != certificate(p)
        or spec.experimental == release_matches()
    ):
        raise ValueError("repair qualification metadata is stale or inconsistent")
    if (
        metadata.action_budget,
        metadata.guaranteed_policy_action_count,
        metadata.resource_allowance,
        metadata.room_count,
        metadata.machine_count,
    ) != (17 + p, 14 + p, 3, 1 + p, 5):
        raise ValueError("repair generation claims differ from the proved profile")


def spawn(stock, artifact_id):
    return DomainArtifact(
        ontology=FAMILY,
        id=artifact_id,
        location=INVENTORY,
        payload=Specimen().model_dump(mode="json"),
    )


def transform(artifact, machine, episode, instrument_settings=None):
    result = laws.transform(
        episode.investigation_truth.data(), artifact.data(), machine, instrument_settings
    )
    return DomainArtifact(
        ontology=FAMILY,
        id=artifact.id,
        location=artifact.location,
        payload=result.model_dump(mode="json"),
    )


def configure(episode, state, action):
    if action.machine not in ("stage", "doser"):
        raise ValueError("only stage and doser accept settings")
    machine = state.machines[action.machine]
    if machine.room_id != state.agent_room:
        raise ValueError("apparatus is not in the current room")
    size = 2 if action.machine == "stage" else 4
    if len(action.settings) != size or any(v not in range(7) for v in action.settings):
        raise ValueError(f"{action.machine} requires {size} selectors in0..6")
    if action.machine == "stage" and action.settings[0] not in (0, 1):
        raise ValueError("stage mode must be0or1")
    machine.settings = action.settings
    state.mission_accepted = False


def expected(episode):
    w = episode.investigation_truth.data()
    return laws.solution(w.a, w.b, w.c, w.degree)


def submitted(state):
    return state.artifacts["seal"].data().doses


def mission_room(spec):
    return spec.data().mission_room


def mission_machine(spec):
    return "doser"


def assess_mission(episode, state):
    dose = submitted(state)
    state.mission_accepted = (
        dose is not None
        and state.artifacts["seal"].location == INVENTORY
        and state.agent_room == mission_room(episode.public.investigation)
        and not any(laws.residuals(episode.investigation_truth.data(), dose))
    )


def public_contract(spec):
    result = action_contract(scientific=True)
    for item in cast(tuple[dict, ...], result["reference"]):
        if item["type"] == "configure":
            item["description"] = (
                "Stage:[mode,x], mode0or1,x0..6. Doser:[u,v,w,z], each0..6. Configure changes apparatus settings only; operate commits a treatment."
            )
            item["example"] = {"type": "configure", "machine": "doser", "settings": [0, 1, 2, 3]}
    result["ontology"] = {
        "family": FAMILY,
        "experimental": spec.data().experimental if spec is not None else True,
        "profile": "stationary-three-round-v1",
        "qualification_scope": "uniform-family-fixed-resource-cell",
        "mission": "Apply a dose to seal, carry it into the array, and finish with every latent residual0.",
    }
    return result


def physical_plan(episode):
    spec = episode.public.investigation.data()
    return (
        TakeAction(artifact="seal"),
        *((MoveAction(target=spec.mission_room),) if spec.stock_room != spec.mission_room else ()),
        ConfigureAction(machine="doser", settings=expected(episode)),
        OperateAction(machine="doser", artifact="seal"),
        FinishAction(),
    )


def measurement(record):
    action = record.action
    if action.type not in ("probe", "operate") or action.machine not in ("reference", "reader"):
        return None
    event = next((e for e in record.events if "result" in e.details), None)
    if event is None:
        return None
    sample = event.details["result"]["payload"]
    return Measurement(
        action.machine,
        sample,
        calibration=action.machine == "reference",
        no_signal=sample["reading"] is None,
    )


def belief(spec):
    from nexus.ontology.repair.inference import RepairBelief

    return RepairBelief()


@dataclass
class RepairTracker:
    room: str
    mission_room: str
    seal_location: str
    dose: tuple[int, ...] | None = None

    def observe(self, record):
        a = record.action
        if a.type == "move":
            self.room = a.target
        elif a.type == "take" and a.artifact == "seal":
            self.seal_location = INVENTORY
        elif a.type == "drop" and a.artifact == "seal":
            self.seal_location = self.room
        elif a.type == "operate" and a.artifact == "seal":
            event = next(e for e in record.events if "result" in e.details)
            dose = event.details["result"]["payload"]["doses"]
            self.dose = None if dose is None else tuple(dose)

    def attempted(self):
        return (
            self.dose
            if self.room == self.mission_room and self.seal_location == INVENTORY
            else None
        )


def mission_tracker(public):
    return RepairTracker(
        public.initial_state.agent_room,
        mission_room(public.investigation),
        public.initial_state.artifacts["seal"].location,
    )


performance_style = "mission"


def log_terminal(spec, calibration_count, no_signal_count, after_resolved_count, first_classes):
    import logging

    logging.getLogger("nexus.diagnostics").info(
        "repair_terminal profile=%s reference_readings=%s insensitive_readings=%s after_decision_resolved=%s first_attempt_decisions=%s budget_cell=exact one_extra_action_breaks_shallow_ceiling=true",
        spec.data().profile,
        calibration_count,
        no_signal_count,
        after_resolved_count,
        first_classes,
    )


# Restarting the same hidden world invalidates the bounded-attempt prior.
requires_single_session = True
