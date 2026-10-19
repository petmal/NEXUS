"""Stateless ontology adapter; canonical engine owns charging, replay and receipts."""

import logging
from dataclasses import dataclass

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
from nexus.ontology.staged.laws import decision, reading, remaining, repair
from nexus.ontology.staged.schema import FAMILY, SEALS, Specimen

performance_style = "mission"
requires_single_session = True


def validate_episode(episode):
    from nexus.ontology.staged.evidence import files
    from nexus.ontology.staged.generation import DESCRIPTION, certificate, initial_state, selection

    spec = episode.public.investigation.data()
    world = episode.investigation_truth.data()
    meta = episode.generation_metadata
    planning = int(spec.stock_room != spec.mission_room)
    if type(episode.construction_seed) is not int or world != selection(episode.construction_seed):
        raise ValueError("staged truth contradicts integer construction seed")
    if spec.resolved is not None and (spec.resolved != world or spec.repair != repair(world)):
        raise ValueError("staged control contradicts the selected mechanism")
    if spec.known_exponents is not None and spec.known_exponents != tuple(
        m.exponent for m in world.mechanisms
    ):
        raise ValueError("staged T2 disclosure contradicts mechanism")
    if meta.resource_pressure not in (0, 1):
        raise ValueError("unsupported staged resource profile")
    proof = certificate(spec, planning, meta.resource_pressure, meta.budget_profile)
    rooms = {spec.stock_room, spec.mission_room}
    if episode.public.evidence_files != files(
        spec
    ) or episode.public.initial_state != initial_state(spec, proof["action_budget"]):
        raise ValueError("staged evidence/initial state contradicts contract")
    if episode.public.rooms != {
        r: Room(id=r, label="Staged array" if r == "array" else "Material stores") for r in rooms
    } or episode.public.edges != (() if len(rooms) == 1 else ((spec.stock_room, "array"),)):
        raise ValueError("staged topology contradicts profile")
    if (
        episode.public.description != DESCRIPTION
        or episode.public.phase_modulus != 1
        or episode.public.goal != GoalPredicate(kind=GoalKind.MISSION_ACCEPTED)
        or episode.rules
        or episode.machine_rules
    ):
        raise ValueError("staged mission contradicts contract")
    if (
        meta.theory_level,
        meta.discovery_level,
        meta.planning_level,
        meta.scenario_family_id,
        meta.room_count,
        meta.machine_count,
        meta.action_budget,
        meta.guaranteed_policy_action_count,
        meta.resource_allowance,
        meta.recommended_tool_call_limit,
        meta.investigation_certificate,
    ) != (
        spec.theory,
        spec.discovery,
        planning,
        FAMILY,
        len(rooms),
        3,
        proof["action_budget"] or 0,
        proof["reference_action_upper"],
        proof["resource_allowance"],
        (proof["action_budget"] or 40) + 24,
        proof,
    ):
        raise ValueError("staged generation metadata contradicts profile")


def spawn(stock, artifact_id):
    return DomainArtifact(
        ontology=FAMILY,
        id=artifact_id,
        location=INVENTORY,
        payload=Specimen(tag=stock.data().tag).model_dump(mode="json"),
    )


def transform(artifact, machine, episode, instrument_settings=None):
    sample = artifact.data()
    if machine == "reader":
        if instrument_settings is None or len(instrument_settings) != 2:
            raise ValueError("reader requires [stage,carrier]")
        stage, carrier = instrument_settings
        result = Specimen(
            tag=sample.tag,
            doses=sample.doses,
            reading=reading(
                episode.investigation_truth.data(),
                stage,
                carrier,
                sample.tag,
                episode.public.investigation.data().linked,
            ),
            stage=stage,
            carrier=carrier,
        )
    elif machine == "trimmer":
        if instrument_settings is None or len(instrument_settings) != 3:
            raise ValueError("trimmer requires three doses")
        result = Specimen(
            tag=sample.tag,
            doses=tuple((d + v) % 3 for d, v in zip(sample.doses, instrument_settings)),
        )
    elif machine == "anneal":
        result = Specimen(tag=sample.tag)
    else:
        raise ValueError("unknown staged apparatus")
    return DomainArtifact(
        ontology=FAMILY,
        id=artifact.id,
        location=artifact.location,
        payload=result.model_dump(mode="json"),
    )


def configure(episode, state, action):
    arity = {"reader": 2, "trimmer": 3}.get(action.machine)
    if (
        arity is None
        or len(action.settings) != arity
        or any(v not in (0, 1, 2) for v in action.settings)
    ):
        raise ValueError(
            "reader requires [stage,carrier]; trimmer requires three doses; all selectors 0..2"
        )
    if state.machines[action.machine].room_id != state.agent_room:
        raise ValueError("apparatus is not in the current room")
    state.machines[action.machine].settings = action.settings


def expected(episode):
    return decision(episode.investigation_truth.data())


def submitted(state):
    return tuple(v for seal in SEALS for v in state.artifacts[seal].data().doses)


def mission_room(spec):
    return "array"


def mission_machine(spec):
    return "trimmer"


def assess_mission(episode, state):
    world = episode.investigation_truth.data()
    state.mission_accepted = state.agent_room == "array" and all(
        state.artifacts[name].location == INVENTORY
        and state.artifacts[name].data().tag == tag
        and remaining(world, tag, state.artifacts[name].data().doses) == (0, 0, 0)
        for tag, name in enumerate(SEALS)
    )


def physical_plan(episode):
    spec = episode.public.investigation.data()
    return (
        *(TakeAction(artifact=name) for name in SEALS),
        *((MoveAction(target="array"),) if spec.stock_room != "array" else ()),
        *(
            action
            for name, doses in zip(SEALS, repair(episode.investigation_truth.data()))
            for action in (
                ConfigureAction(machine="trimmer", settings=doses),
                OperateAction(machine="trimmer", artifact=name),
            )
        ),
        FinishAction(),
    )


def measurement(record):
    if record.action.type not in ("probe", "operate") or record.action.machine != "reader":
        return None
    payload = next(e.details["result"]["payload"] for e in record.events if "result" in e.details)
    return Measurement("reader", payload)


def measurement_features(measurement):
    return measurement.sample["stage"], True


def belief(spec):
    from nexus.ontology.staged.inference import Belief

    return Belief(spec.data())


@dataclass
class Tracker:
    room: str
    locations: dict[str, str]
    doses: dict[str, tuple[int, ...]]

    def observe(self, record):
        action = record.action
        if action.type == "move":
            self.room = action.target
        elif action.type in ("take", "drop") and action.artifact in SEALS:
            self.locations[action.artifact] = INVENTORY if action.type == "take" else self.room
        elif action.type == "operate" and action.artifact in SEALS:
            payload = next(
                e.details["result"]["payload"] for e in record.events if "result" in e.details
            )
            self.doses[action.artifact] = tuple(payload["doses"])

    def attempted(self):
        return (
            tuple(v for name in SEALS for v in self.doses[name])
            if self.room == "array" and all(self.locations[n] == INVENTORY for n in SEALS)
            else None
        )


def mission_tracker(public):
    state = public.initial_state
    return Tracker(
        state.agent_room,
        {n: state.artifacts[n].location for n in SEALS},
        {n: state.artifacts[n].data().doses for n in SEALS},
    )


def public_contract(spec):
    result = action_contract(scientific=True)
    for item in result["reference"]:
        if item["type"] == "configure":
            item["description"] = (
                "Reader: [stage,carrier]. Trimmer: three incremental doses. All selectors 0..2. Configure stores settings; operate applies them. No controller program or correctness preview."
            )
            item["example"] = {"type": "configure", "machine": "reader", "settings": [0, 0]}
    result["ontology"] = {
        "family": FAMILY,
        "experimental": True,
        "configuration": {
            "reader": {"arity": 2, "range": [0, 2]},
            "trimmer": {"arity": 3, "range": [0, 2]},
        },
        "mission": "Carry seal-0, seal-1, seal-2 in array with all nine hidden remaining loads zero, then finish.",
        "contract": "Read all evidence. Reader returns baseline-copy response, never remaining load. Doses are cumulative applied treatments. All experiments remain legal; finish returns binary success/rejection and can be retried. No controller program is submitted.",
    }
    return result


def log_terminal(spec, calibration_count, no_signal_count, after_resolved_count, first_classes):
    logging.getLogger("nexus.diagnostics").info(
        "staged_terminal T=%s D=%s first_submission_mission_signatures=%s readings_after_guaranteed_repair=%s deep_tier_admitted=false",
        spec.theory,
        spec.discovery,
        first_classes,
        after_resolved_count,
    )


def log_terminal_trace(state, trace, posterior):
    readings = [m for r in trace if (m := measurement(r)) is not None]
    logging.getLogger("nexus.diagnostics").info(
        "staged_operations reader_calls=%s stages_observed=%s zero_readings=%s committed_trims=%s anneals=%s remaining_worlds=%s known_complete_repair=%s zero_reading_is_not_no_signal=true",
        len(readings),
        sorted({m.sample["stage"] for m in readings}),
        sum(m.sample["reading"] == 0 for m in readings),
        sum(r.action.type == "operate" and r.action.machine == "trimmer" for r in trace),
        sum(r.action.type == "operate" and r.action.machine == "anneal" for r in trace),
        posterior.counts()[0],
        bool(posterior.common_decisions()),
    )
