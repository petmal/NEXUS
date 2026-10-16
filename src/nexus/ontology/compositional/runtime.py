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
from nexus.ontology.compositional.laws import REPAIRS, World, accepted, reading, world_for_seed
from nexus.ontology.compositional.schema import FAMILY, Specimen
from nexus.ontology.inference import Measurement
from nexus.ontology.mission import AppliedTreatmentTracker

performance_style = "mission"
requires_single_session = True


def world_for(episode):
    return World(**episode.investigation_truth.payload)


def validate_episode(episode):
    from nexus.ontology.compositional.evidence import files
    from nexus.ontology.compositional.generation import DESCRIPTION, certificate, initial_state

    spec = episode.public.investigation.data()
    metadata = episode.generation_metadata
    planning = int(spec.stock_room != spec.mission_room)
    proof = certificate(spec, planning)
    bound = proof["reference_action_upper"]
    if type(episode.construction_seed) is not int or world_for(episode) != world_for_seed(
        episode.construction_seed
    ):
        raise ValueError("compositional repair truth does not match seed")
    if spec.resolved is not None and spec.resolved != expected(episode):
        raise ValueError("T0 treatment contradicts the selected compositional repair")
    if episode.public.evidence_files != files(spec):
        raise ValueError("compositional repair evidence differs from the public contract")
    if episode.public.initial_state != initial_state(spec, bound + 3):
        raise ValueError("compositional repair initial state or resources differ from profile")
    rooms = {spec.stock_room, spec.mission_room}
    expected_rooms = {
        room: Room(id=room, label="Coupled array" if room == "array" else "Material stores")
        for room in rooms
    }
    edges = () if len(rooms) == 1 else ((spec.stock_room, spec.mission_room),)
    if episode.public.rooms != expected_rooms or episode.public.edges != edges:
        raise ValueError("compositional repair topology differs from profile")
    if (
        episode.public.description != DESCRIPTION
        or episode.public.phase_modulus != 1
        or episode.public.goal != GoalPredicate(kind=GoalKind.MISSION_ACCEPTED)
    ):
        raise ValueError("compositional repair mission or phase differs from profile")
    if episode.rules or episode.machine_rules:
        raise ValueError("compositional repair has no additional machine rules")
    if (
        metadata.theory_level,
        metadata.discovery_level,
        metadata.planning_level,
        metadata.resource_pressure,
    ) != (spec.theory, spec.discovery, planning, 1):
        raise ValueError("compositional repair axis metadata differs from profile")
    if (
        metadata.action_budget,
        metadata.guaranteed_policy_action_count,
        metadata.resource_allowance,
        metadata.room_count,
        metadata.machine_count,
    ) != (bound + 3, bound, 3, len(rooms), 3) or metadata.investigation_certificate != proof:
        raise ValueError("compositional repair certificate or budget metadata differs from profile")


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
            raise ValueError("configure stage before preparation")
        result = Specimen(settings=instrument_settings)
    elif machine == "sensor":
        result = Specimen(
            settings=specimen.settings, reading=reading(world_for(episode), specimen.settings)
        )
    else:
        raise ValueError("unknown compositional repair apparatus")
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
    size = 8 if action.machine == "stage" else 4
    if len(action.settings) != size or any(v < 0 or v > 2 for v in action.settings):
        raise ValueError(f"{action.machine} requires {size} selectors in 0..2")
    if action.machine == "stage" and action.settings[0] > 1:
        raise ValueError("context must be 0 or 1")
    machine.settings = action.settings
    state.mission_accepted = False


def expected(episode):
    return next(doses for doses in REPAIRS if accepted(world_for(episode), doses))


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
        and accepted(world_for(episode), submitted(state))
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
    if action.type not in ("operate", "probe") or action.machine != "sensor":
        return None
    event = next(e for e in record.events if "result" in e.details)
    sample = event.details["result"]["payload"]
    return Measurement(
        action.machine,
        sample,
        calibration=False,
        no_signal=sample["reading"] is None,
    )


def belief(spec):
    from nexus.ontology.compositional.inference import Belief

    return Belief(spec.data())


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
                "Stage: [context,x,y,z,a,b,c,d], context 0..1, other values 0..2. Doser: [a,b,c,d] each 0..2. Configure sets apparatus only; operate commits preparation or treatment."
            )
            item["example"] = {
                "type": "configure",
                "machine": "doser",
                "settings": [0, 1, 2, 0],
            }
    result["ontology"] = {
        "family": FAMILY,
        "experimental": True,
        "mission": "Treat seal, carry it into array, finish with all four cross-context residuals zero. Read all evidence.",
        "configuration": {
            "stage": {"arity": 8, "range": [0, 2], "context_range": [0, 1]},
            "doser": {"arity": 4, "range": [0, 2]},
        },
    }
    return result


def log_terminal(spec, calibration_count, no_signal_count, after_resolved_count, first_classes):
    logging.getLogger("nexus.diagnostics").info(
        "compositional_terminal theory=%s calibration_readings=%s insensitive_readings=%s after_target_resolved=%s first_submission_winning_set_signatures=%s empirical_difficulty=uncalibrated",
        spec.theory,
        calibration_count,
        no_signal_count,
        after_resolved_count,
        first_classes,
    )
