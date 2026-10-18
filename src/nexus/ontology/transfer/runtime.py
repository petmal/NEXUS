"""Material operations use the canonical engine's transaction and receipt boundary."""

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
from nexus.ontology.inference import Measurement
from nexus.ontology.mission import AppliedTreatmentTracker
from nexus.ontology.transfer.laws import PROGRAMS, PROGRAM_INDEX, accepted, displayed, selection
from nexus.ontology.transfer.reference import load
from nexus.ontology.transfer.schema import CALIBRATED, COUPLED, Specimen, valid_program

performance_style = "mission"
requires_single_session = True


def validate_episode(episode):
    from nexus.ontology.transfer.evidence import files
    from nexus.ontology.transfer.generation import DESCRIPTION, certificate, initial_state

    spec = episode.public.investigation.data()
    truth = episode.investigation_truth.data()
    metadata = episode.generation_metadata
    planning = int(spec.stock_room != spec.mission_room)
    proof = certificate(spec, planning, metadata.budget_profile)
    bound, extra = proof["reference_action_upper"], proof["resource_allowance"]
    if type(episode.construction_seed) is not int:
        raise ValueError("transfer requires integer construction seed")
    program, offset = selection(episode.construction_seed)
    if spec.family != episode.public.investigation.ontology or (
        truth.program,
        truth.reader_offset,
    ) != (program, offset if spec.coupled else 0):
        raise ValueError("transfer family or truth differs from seed")
    if spec.resolved is not None and spec.resolved != expected(episode):
        raise ValueError("T0 program contradicts selected transfer behavior")
    if episode.public.evidence_files != files(
        spec
    ) or episode.public.initial_state != initial_state(spec, bound + extra):
        raise ValueError("transfer evidence or initial state differs from contract")
    rooms = {spec.stock_room, spec.mission_room}
    if episode.public.rooms != {
        r: Room(id=r, label="Coupled array" if r == "array" else "Material stores") for r in rooms
    } or episode.public.edges != (
        () if len(rooms) == 1 else ((spec.stock_room, spec.mission_room),)
    ):
        raise ValueError("transfer topology differs from profile")
    if (
        episode.public.description != DESCRIPTION
        or episode.public.phase_modulus != 1
        or episode.public.goal != GoalPredicate(kind=GoalKind.MISSION_ACCEPTED)
        or episode.rules
        or episode.machine_rules
    ):
        raise ValueError("transfer mission or rules differ from contract")
    if (
        metadata.theory_level,
        metadata.discovery_level,
        metadata.planning_level,
        metadata.resource_pressure,
        metadata.scenario_family_id,
    ) != (spec.theory, spec.discovery, planning, 1, spec.family):
        raise ValueError("transfer axes differ from profile")
    if (
        metadata.action_budget,
        metadata.guaranteed_policy_action_count,
        metadata.resource_allowance,
        metadata.room_count,
        metadata.machine_count,
        metadata.recommended_tool_call_limit,
    ) != (
        bound + extra,
        bound,
        extra,
        len(rooms),
        3,
        bound + extra + 24,
    ) or metadata.investigation_certificate != proof:
        raise ValueError("transfer budget or certificate differs from profile")


def spawn(stock, artifact_id):
    return DomainArtifact(
        ontology=stock.ontology,
        id=artifact_id,
        location=INVENTORY,
        payload=Specimen(material=stock.data().material).model_dump(mode="json"),
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
        result = Specimen(material=specimen.material, settings=instrument_settings)
    elif machine == "sensor":
        truth = episode.investigation_truth.data()
        result = Specimen(
            material=specimen.material,
            settings=specimen.settings,
            reading=displayed(
                truth.program,
                truth.reader_offset,
                specimen.settings,
                specimen.material,
                episode.public.investigation.data().coupled,
            ),
        )
    else:
        raise ValueError("unknown transfer apparatus")
    return DomainArtifact(
        ontology=artifact.ontology,
        id=artifact.id,
        location=artifact.location,
        payload=result.model_dump(mode="json"),
    )


def configure(episode, state, action):
    if action.machine not in ("stage", "doser"):
        raise ValueError("only stage and doser accept settings")
    if state.machines[action.machine].room_id != state.agent_room:
        raise ValueError("apparatus is not in this sector")
    if action.machine == "stage":
        if (
            len(action.settings) != 6
            or action.settings[0] not in (0, 1)
            or any(v not in (0, 1, 2) for v in action.settings[1:])
        ):
            raise ValueError("stage requires [context 0..1,x,y,z,a,b 0..2]")
    elif tuple(action.settings) not in PROGRAM_INDEX or not valid_program(action.settings):
        raise ValueError(
            "doser requires a valid [topology,f,g,h,changed,replacement,q] counterprogram; replacement must differ"
        )
    state.machines[action.machine].settings = action.settings
    state.mission_accepted = False


def expected(episode):
    index = PROGRAM_INDEX[episode.investigation_truth.data().program]
    return PROGRAMS[load()["targets"][index]]


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
        and accepted(episode.investigation_truth.data().program, submitted(state))
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
    sample = next(e.details["result"]["payload"] for e in record.events if "result" in e.details)
    return Measurement(
        "sensor",
        sample,
        calibration=sample["material"] == "reference",
        no_signal=sample["reading"] is None,
    )


def belief(spec):
    from nexus.ontology.transfer.inference import Belief

    return Belief(spec.data())


def measurement_features(measurement):
    if measurement.no_signal:
        return None, None
    setting = measurement.sample["settings"]
    return setting[0], bool(setting[4] or setting[5])


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
                "Stage [context,x,y,z,a,b] or doser [topology,f,g,h,changed,replacement,q]. Read the complete selector ranges and grammar in theory.json/apparatus.txt. Configure sets apparatus only; operate applies."
            )
            item["example"] = {
                "type": "configure",
                "machine": "stage",
                "settings": [0, 0, 0, 0, 0, 0],
            }
    result["ontology"] = {
        "families": [CALIBRATED, COUPLED],
        "experimental": True,
        "mission": "Apply a counterprogram to seal; carry it in array; finish with zero physical residual over all 486 conditions.",
        "configuration": {"stage": {"arity": 6}, "doser": {"arity": 7}},
    }
    return result


def log_terminal(spec, calibration_count, no_signal_count, after_resolved_count, first_classes):
    logging.getLogger("nexus.diagnostics").info(
        "transfer_terminal family=%s reference_readings=%s insensitive_readings=%s after_target_resolved=%s first_submission_behavior_classes=%s mission_conditions=486 empirical_difficulty=uncalibrated",
        spec.ontology,
        calibration_count,
        no_signal_count,
        after_resolved_count,
        first_classes,
    )


def log_terminal_belief(posterior):
    from nexus.ontology.transfer.tables import N

    offsets = sum(
        bool((posterior.mask >> (N * b)) & ((1 << N) - 1))
        for b in range(3 if posterior.coupled else 1)
    )
    worlds, behaviors = posterior.counts()
    logging.getLogger("nexus.diagnostics").info(
        "transfer_posterior joint_worlds=%s physical_behavior_classes=%s compatible_reader_offsets=%s reference_carries_upstream_information=%s",
        worlds,
        behaviors,
        offsets,
        posterior.coupled,
    )
