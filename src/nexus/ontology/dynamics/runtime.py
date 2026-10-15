"""Material adapter: ordinary engine commits state, resource charges and receipts."""

import logging
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
from nexus.ontology.dynamics.laws import WORLDS, World, measurable, reading, targets
from nexus.ontology.dynamics.schema import FAMILY, Experiment, Specimen
from nexus.ontology.inference import Measurement
from nexus.ontology.mission import AppliedTreatmentTracker

performance_style = "mission"
requires_single_session = True


def world_for(episode):
    return World(**episode.investigation_truth.payload)


def validate_episode(episode):
    from nexus.ontology.dynamics.evidence import files
    from nexus.ontology.dynamics.generation import DESCRIPTION, certificate, initial_state

    spec = episode.public.investigation.data()
    metadata = episode.generation_metadata
    planning = int(spec.stock_room != spec.mission_room)
    proof = certificate(spec, planning)
    bound = proof["reference_action_upper"]
    if (
        type(episode.construction_seed) is not int
        or world_for(episode) != WORLDS[episode.construction_seed % len(WORLDS)]
    ):
        raise ValueError("dynamics truth does not match seed")
    if spec.resolved is not None and spec.resolved != expected(episode):
        raise ValueError("T0 treatment contradicts the selected dynamics")
    if episode.public.evidence_files != files(spec):
        raise ValueError("dynamics evidence differs from the public contract")
    if episode.public.initial_state != initial_state(spec, bound + 8):
        raise ValueError("dynamics initial state or resources differ from profile")
    rooms = {spec.stock_room, spec.mission_room}
    expected_rooms = {
        room: Room(id=room, label="Coupled array" if room == "array" else "Material stores")
        for room in rooms
    }
    edges = () if len(rooms) == 1 else ((spec.stock_room, spec.mission_room),)
    if episode.public.rooms != expected_rooms or episode.public.edges != edges:
        raise ValueError("dynamics topology differs from profile")
    if (
        episode.public.description != DESCRIPTION
        or episode.public.phase_modulus != 1
        or episode.public.goal != GoalPredicate(kind=GoalKind.MISSION_ACCEPTED)
    ):
        raise ValueError("dynamics mission or phase differs from profile")
    if episode.rules or episode.machine_rules:
        raise ValueError("dynamics has no additional machine rules")
    if (
        metadata.theory_level,
        metadata.discovery_level,
        metadata.planning_level,
        metadata.resource_pressure,
    ) != (spec.theory, spec.discovery, planning, 1):
        raise ValueError("dynamics axis metadata differs from profile")
    if (
        metadata.action_budget,
        metadata.guaranteed_policy_action_count,
        metadata.resource_allowance,
        metadata.room_count,
        metadata.machine_count,
    ) != (bound + 8, bound, 8, len(rooms), 5) or metadata.investigation_certificate != proof:
        raise ValueError("dynamics certificate or budget metadata differs from profile")


def spawn(stock, artifact_id):
    return DomainArtifact(
        ontology=FAMILY,
        id=artifact_id,
        location=INVENTORY,
        payload=Specimen().model_dump(mode="json"),
    )


def transform(artifact, machine, episode, instrument_settings=None):
    specimen = artifact.data()
    if machine == "doser" and specimen.material == "seal":
        if instrument_settings is None:
            raise ValueError("configure doser before treatment")
        result = Specimen(material="seal", doses=instrument_settings)
    elif specimen.material == "seal" or machine == "doser":
        result = specimen
    elif machine == "stage":
        if instrument_settings is None:
            raise ValueError("configure stage before orientation")
        result = Specimen(history=specimen.history, point=instrument_settings)
    elif machine == "pulse":
        if len(specimen.history) == 3:
            raise ValueError("survey supports three pulses; take fresh stock")
        result = Specimen(history=(*specimen.history, specimen.point), point=specimen.point)
    elif machine in ("sensor", "reference"):
        experiment = Experiment(instrument=machine, history=specimen.history, point=specimen.point)
        if not measurable(experiment):
            raise ValueError("mission protocol is outside the sensor measurement contract")
        result = Specimen(
            history=specimen.history,
            point=specimen.point,
            instrument=machine,
            reading=reading(world_for(episode), experiment),
        )
    else:
        raise ValueError("unknown dynamics apparatus")
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
        raise ValueError("apparatus is not in this sector")
    size, maximum = (3, 1) if action.machine == "stage" else (8, 2)
    if len(action.settings) != size or any(v < 0 or v > maximum for v in action.settings):
        raise ValueError(f"{action.machine} requires {size} selectors in 0..{maximum}")
    machine.settings = action.settings
    state.mission_accepted = False


def expected(episode):
    return targets()[WORLDS.index(world_for(episode))]


def submitted(state):
    return state.artifacts["seal"].data().doses


def mission_room(spec):
    return spec.data().mission_room


def mission_machine(spec):
    return "doser"


def assess_mission(episode, state):
    state.mission_accepted = (
        state.agent_room == mission_room(episode.public.investigation)
        and state.artifacts["seal"].location == INVENTORY
        and submitted(state) == expected(episode)
    )


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
    if action.type not in ("operate", "probe") or action.machine not in ("sensor", "reference"):
        return None
    event = next(e for e in record.events if "result" in e.details)
    sample = event.details["result"]["payload"]
    return Measurement(
        action.machine,
        sample,
        calibration=action.machine == "reference",
        no_signal=sample["reading"] is None,
    )


def belief(spec):
    from nexus.ontology.dynamics.inference import DynamicsBelief

    return DynamicsBelief(spec.data())


def mission_tracker(public):
    return AppliedTreatmentTracker(
        public.initial_state.agent_room,
        mission_room(public.investigation),
        public.initial_state.artifacts["seal"].location,
    )


def public_contract(spec):
    result = action_contract(scientific=True)
    for item in cast(tuple[dict, ...], result["reference"]):
        if item["type"] == "configure":
            item["description"] = (
                "Stage: [x,y,e], each 0..1. Doser: eight ordered values 0..2. Configure sets apparatus only; operate commits preparation or treatment."
            )
            item["example"] = {
                "type": "configure",
                "machine": "doser",
                "settings": [0, 1, 2, 0, 1, 2, 0, 1],
            }
    result["ontology"] = {
        "family": FAMILY,
        "experimental": True,
        "mission": "Treat seal, carry it into array, finish with all eight residuals zero. Read all evidence.",
        "configuration": {
            "stage": {"arity": 3, "range": [0, 1]},
            "doser": {"arity": 8, "range": [0, 2]},
        },
    }
    return result


def log_terminal(spec, calibration_count, no_signal_count, after_resolved_count, first_classes):
    logging.getLogger("nexus.diagnostics").info(
        "dynamics_terminal theory=%s reference_readings=%s insensitive_readings=%s after_target_resolved=%s first_submission_target_classes=%s empirical_difficulty=uncalibrated",
        spec.theory,
        calibration_count,
        no_signal_count,
        after_resolved_count,
        first_classes,
    )
