"""Causal ontology adapter; no mutation or accounting outside the engine's copy."""

import logging
from typing import cast

from nexus.models.actions import ConfigureAction, FinishAction, MoveAction, action_contract
from nexus.models.domain import DomainArtifact
from nexus.models.world import INVENTORY
from nexus.ontology.causal.laws import MISSION, World, measurable, physical, reading
from nexus.ontology.causal.schema import FAMILY, Experiment, Specimen
from nexus.ontology.inference import Measurement

performance_style = "mission"


def world_for(episode) -> World:
    return World(**episode.investigation_truth.payload)


def validate_episode(episode):
    spec = episode.public.investigation.data()
    world = world_for(episode)
    from nexus.ontology.causal.evidence import files

    if episode.public.evidence_files != files(spec):
        raise ValueError("causal public evidence does not match specification")
    metadata = episode.generation_metadata
    if (metadata.theory_level, metadata.discovery_level) != (spec.theory, spec.discovery):
        raise ValueError("causal difficulty metadata does not match specification")
    if metadata.planning_level != int(spec.stock_room != spec.mission_room):
        raise ValueError("causal planning metadata does not match topology")
    state = episode.public.initial_state
    room_ids = {spec.mission_room, spec.stock_room}
    edges = () if len(room_ids) == 1 else ((spec.stock_room, spec.mission_room),)
    if set(episode.public.rooms) != room_ids or episode.public.edges != edges:
        raise ValueError("causal laboratory topology does not match specification")
    if state.agent_room != spec.stock_room or state.artifacts:
        raise ValueError("causal episode must start at fresh stock without specimens")
    if episode.public.goal.kind != "mission_accepted":
        raise ValueError("causal ontology requires mission_accepted")
    if set(state.machines) != {"board", "stage", "pulse", "sensor", "reference"}:
        raise ValueError("causal apparatus does not match specification")
    for name, machine in state.machines.items():
        if machine.room_id != spec.mission_room:
            raise ValueError("causal apparatus is outside laboratory")
        if name == "stage":
            valid = machine.settings is not None and len(machine.settings) == 3
        elif name == "board":
            valid = machine.settings is None or len(machine.settings) == 6
        else:
            valid = machine.settings is None
        if not valid or (machine.settings and any(v not in (0, 1, 2) for v in machine.settings)):
            raise ValueError("invalid initial causal apparatus settings")
    if set(state.stocks) != {"stock"} or state.stocks["stock"].location != spec.stock_room:
        raise ValueError("causal ontology requires the declared fresh stock")
    if any(getattr(world, k) != value for k, value in spec.known.items()):
        raise ValueError("private mechanism contradicts disclosed laws")
    if any(
        not measurable(r.experiment) or reading(world, r.experiment) != r.value
        for r in spec.supplied
    ):
        raise ValueError("supplied observations contradict mechanism or bench contract")
    from nexus.ontology.causal.inference import initial_mask, target_set

    possible = target_set(initial_mask(spec))
    if not possible or (spec.discovery == 0 and len(possible) != 1):
        raise ValueError("D0 evidence must resolve the mission")
    if expected(episode) not in possible:
        raise ValueError("resolved prediction contradicts private mechanism")
    from nexus.ontology.causal.qualification import certificate

    proof = certificate(initial_mask(spec), metadata.planning_level, spec.discovery != 2)
    bound = proof["reference_action_bound"]
    resource = metadata.resource_pressure
    if resource not in (0, 1, 2):
        raise ValueError("unsupported causal resource profile")
    budget = None if resource == 0 else bound + (8 if resource == 1 else 0)
    uses = None if resource == 0 else bound
    if (
        state.resources.actions_remaining != budget
        or state.stocks["stock"].remaining != uses
        or any(m.uses_remaining != uses for m in state.machines.values())
    ):
        raise ValueError("causal resource limits do not match profile")
    if state.turn != 0 or state.mission_accepted or state.terminal_status.value != "active":
        raise ValueError("causal initial state must be fresh and active")


def spawn(stock, artifact_id):
    return DomainArtifact(
        ontology=FAMILY,
        id=artifact_id,
        location=INVENTORY,
        payload=Specimen().model_dump(mode="json"),
    )


def transform(artifact, machine, episode, instrument_settings=None):
    specimen = artifact.data()
    if machine == "stage":
        if instrument_settings is None or len(instrument_settings) != 3:
            raise ValueError("stage requires three settings")
        result = Specimen(history=specimen.history, point=instrument_settings)
    elif machine == "pulse":
        if len(specimen.history) == 2:
            raise ValueError("specimen supports two pulses; take a fresh stock specimen")
        result = Specimen(history=(*specimen.history, specimen.point), point=specimen.point)
    elif machine in ("sensor", "reference"):
        experiment = Experiment(instrument=machine, history=specimen.history, point=specimen.point)
        if not measurable(experiment):
            raise ValueError("mission protocol is outside the measurement contract")
        result = Specimen(
            history=specimen.history,
            point=specimen.point,
            reading=reading(world_for(episode), experiment),
            instrument=machine,
        )
    else:
        raise ValueError("board accepts configure and finish; it has no specimen preview")
    return DomainArtifact(
        ontology=FAMILY,
        id=artifact.id,
        location=artifact.location,
        payload=result.model_dump(mode="json"),
    )


def configure(episode, state, action):
    if action.machine not in ("stage", "board"):
        raise ValueError("only stage and board accept settings")
    machine = state.machines[action.machine]
    if machine.room_id != state.agent_room:
        raise ValueError("apparatus is not in the current room")
    size = 3 if action.machine == "stage" else 6
    if len(action.settings) != size or any(v not in (0, 1, 2) for v in action.settings):
        raise ValueError(f"{action.machine} requires {size} selectors in 0..2")
    machine.settings = action.settings
    if action.machine == "board":
        state.mission_accepted = False


def expected(episode):
    return tuple(physical(world_for(episode), e) for e in MISSION)


def submitted(state):
    return state.machines["board"].settings


def mission_room(spec):
    return spec.data().mission_room


def mission_machine(spec):
    return "board"


def assess_mission(episode, state):
    state.mission_accepted = state.agent_room == mission_room(
        episode.public.investigation
    ) and submitted(state) == expected(episode)


def public_contract(spec):
    result = action_contract(scientific=True)
    for item in cast(tuple[dict, ...], result["reference"]):
        if item["type"] == "configure":
            item["description"] = (
                "Stage: [x,y,context]; board: six ordered physical responses. All selectors 0..2. No correctness feedback."
            )
            item["example"] = {
                "type": "configure",
                "machine": "board",
                "settings": [0, 1, 2, 0, 1, 2],
            }
    result["ontology"] = {
        "family": FAMILY,
        "experimental": True,
        "theory_level": spec.theory if spec is not None else None,
        "discovery_level": spec.discovery if spec is not None else None,
        "configuration": {
            "stage": {"arity": 3, "range": [0, 2]},
            "board": {"arity": 6, "range": [0, 2]},
        },
        "mission": "Predict physical responses for six protocols in theory.json, configure board, then finish.",
        "specimen": "Fresh stock starts at point [0,0,0] with empty history. Hidden mode is not observed.",
        "prepare": "Configure stage then operate stage to set specimen point. Operate pulse appends current point to its history; maximum two pulses.",
        "measure": "Probe sensor returns an offset-bearing reading; probe reference returns offset. Probe does not commit specimen changes.",
        "prior": "Read theory.json for complete bounded laws, disclosures, supplied data and mission exclusions.",
    }
    return result


def physical_plan(episode):
    spec = episode.public.investigation.data()
    move = () if spec.stock_room == spec.mission_room else (MoveAction(target=spec.mission_room),)
    return (*move, ConfigureAction(machine="board", settings=expected(episode)), FinishAction())


def measurement(record):
    action = record.action
    if action.type not in ("probe", "operate") or action.machine not in ("sensor", "reference"):
        return None
    event = next(e for e in record.events if "result" in e.details)
    return Measurement(
        action.machine,
        event.details["result"]["payload"],
        calibration=action.machine == "reference",
    )


def belief(spec):
    from nexus.ontology.causal.inference import CausalBelief

    return CausalBelief(spec.data())


def log_terminal(spec, calibration_count, no_signal_count, after_resolved_count, first_classes):
    logging.getLogger("nexus.diagnostics").info(
        "causal_terminal T=%s D=%s reference_measurements=%s measurements_after_target_identified=%s first_submission_target_classes=%s",
        spec.theory,
        spec.discovery,
        calibration_count,
        after_resolved_count,
        first_classes,
    )
