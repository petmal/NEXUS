"""Stateless adapter; engine retains transactions, charging, replay and receipts."""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass

from nexus.models.actions import (
    FinishAction,
    MoveAction,
    OperateAction,
    TakeAction,
    action_contract,
)
from nexus.models.domain import DomainArtifact
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import INVENTORY, Room
from nexus.ontology.history.laws import PULSES, READERS, accepted, observed, shortest
from nexus.ontology.history.schema import FAMILY, MAX_HISTORY, Specimen
from nexus.ontology.inference import Measurement

performance_style = "mission"
requires_single_session = True


def validate_episode(episode):
    from nexus.ontology.history.evidence import files
    from nexus.ontology.history.generation import (
        APPARATUS,
        DESCRIPTION,
        certificate,
        initial_state,
        selection,
    )

    spec = episode.public.investigation.data()
    truth = episode.investigation_truth.data()
    metadata = episode.generation_metadata
    planning = int(spec.stock_room != spec.mission_room)
    if type(episode.construction_seed) is not int or truth != selection(episode.construction_seed):
        raise ValueError("history truth differs from integer construction seed")
    if spec.resolved is not None and (spec.resolved != truth or spec.procedure != shortest(truth)):
        raise ValueError("history control contradicts selected mechanism")
    if metadata.resource_pressure not in (0, 1):
        raise ValueError("unsupported history resource profile")
    proof = certificate(spec, planning, metadata.resource_pressure, metadata.budget_profile)
    if episode.public.evidence_files != files(
        spec
    ) or episode.public.initial_state != initial_state(spec, proof["action_budget"]):
        raise ValueError("history evidence or initial state differs from contract")
    rooms = {spec.stock_room, spec.mission_room}
    if episode.public.rooms != {
        r: Room(id=r, label="Coupled array" if r == "array" else "Material stores") for r in rooms
    } or episode.public.edges != (
        () if len(rooms) == 1 else ((spec.stock_room, spec.mission_room),)
    ):
        raise ValueError("history topology differs from profile")
    if (
        episode.public.description != DESCRIPTION
        or episode.public.phase_modulus != 1
        or episode.public.goal != GoalPredicate(kind=GoalKind.MISSION_ACCEPTED)
        or episode.rules
        or episode.machine_rules
    ):
        raise ValueError("history mission or rules differ from contract")
    if (
        metadata.theory_level,
        metadata.discovery_level,
        metadata.planning_level,
        metadata.scenario_family_id,
    ) != (spec.theory, spec.discovery, planning, FAMILY):
        raise ValueError("history axes differ from profile")
    if (
        metadata.action_budget,
        metadata.guaranteed_policy_action_count,
        metadata.resource_allowance,
        metadata.room_count,
        metadata.machine_count,
        metadata.recommended_tool_call_limit,
    ) != (
        proof["action_budget"] or 0,
        proof["reference_action_upper"],
        proof["resource_allowance"],
        len(rooms),
        len(APPARATUS),
        (proof["action_budget"] or proof["reference_action_upper"]) + 24,
    ) or metadata.investigation_certificate != proof:
        raise ValueError("history metadata or certificate differs from profile")


def spawn(stock, artifact_id):
    return DomainArtifact(
        ontology=FAMILY,
        id=artifact_id,
        location=INVENTORY,
        payload=Specimen().model_dump(mode="json"),
    )


def transform(artifact, machine, episode, instrument_settings=None):
    sample = artifact.data()
    world = episode.investigation_truth.data()
    if machine in PULSES:
        if len(sample.history) == MAX_HISTORY:
            raise ValueError("eight-pulse limit reached; operate anneal to recover the specimen")
        history = (*sample.history, PULSES.index(machine))
        result = Specimen(history=history, visible=observed(world, history))
    elif machine in READERS:
        result = Specimen(
            history=sample.history,
            visible=sample.visible,
            reading=observed(world, sample.history, READERS.index(machine)),
            channel=machine,
        )
    elif machine == "anneal":
        result = Specimen()
    else:
        raise ValueError("unknown history apparatus")
    return DomainArtifact(
        ontology=FAMILY,
        id=artifact.id,
        location=artifact.location,
        payload=result.model_dump(mode="json"),
    )


def configure(episode, state, action):
    raise ValueError("history apparatuses use operate or probe; none accepts configure")


def expected(episode):
    return shortest(episode.investigation_truth.data())


def submitted(state):
    return state.artifacts["seal"].data().history


def mission_room(spec):
    return spec.data().mission_room


def mission_machine(spec):
    return "sen"


def assess_mission(episode, state):
    state.mission_accepted = (
        state.agent_room == mission_room(episode.public.investigation)
        and state.artifacts["seal"].location == INVENTORY
        and accepted(episode.investigation_truth.data(), submitted(state))
    )


def physical_plan(episode):
    spec = episode.public.investigation.data()
    return (
        TakeAction(artifact="seal"),
        *((MoveAction(target=spec.mission_room),) if spec.stock_room != spec.mission_room else ()),
        *(OperateAction(machine=PULSES[m], artifact="seal") for m in expected(episode)),
        FinishAction(),
    )


def measurement(record):
    action = record.action
    if action.type not in ("operate", "probe") or action.machine not in (*PULSES, *READERS):
        return None
    payload = next(e.details["result"]["payload"] for e in record.events if "result" in e.details)
    return Measurement(action.machine, payload)


def measurement_features(measurement):
    channel = measurement.sample["channel"]
    return (0 if channel is None else READERS.index(channel)), channel in READERS[1:]


def belief(spec):
    from nexus.ontology.history.inference import Belief

    return Belief(spec.data())


@dataclass
class HistoryTracker:
    room: str
    mission_room: str
    location: str
    history: tuple[int, ...] = ()

    def observe(self, record):
        action = record.action
        if action.type == "move":
            self.room = action.target
        elif action.type == "take" and action.artifact == "seal":
            self.location = INVENTORY
        elif action.type == "drop" and action.artifact == "seal":
            self.location = self.room
        elif action.type == "operate" and action.artifact == "seal":
            payload = next(
                e.details["result"]["payload"] for e in record.events if "result" in e.details
            )
            self.history = tuple(payload["history"])

    def attempted(self):
        return (
            self.history if self.location == INVENTORY and self.room == self.mission_room else None
        )


def mission_tracker(public):
    return HistoryTracker(
        public.initial_state.agent_room,
        mission_room(public.investigation),
        public.initial_state.artifacts["seal"].location,
    )


def public_contract(spec):
    result = action_contract(scientific=True)
    result["schema"] = action_contract()["schema"]
    result["reference"] = tuple(
        item for item in result["reference"] if item["type"] not in ("configure", "measure")
    )
    result["ontology"] = {
        "family": FAMILY,
        "experimental": True,
        "mission": "Carry seal in array with physical (H,K,x,y)=(1,2,1,2), then finish.",
        "pulses": PULSES,
        "readers": READERS,
        "recovery": "operate anneal",
        "configuration": {},
        "contract": "Read every evidence file for the complete finite prior, sequential updates, physical-clamp readings and eight-pulse limit. No controller or configure action in this family.",
    }
    return result


def log_terminal(spec, calibration_count, no_signal_count, after_resolved_count, first_classes):
    logging.getLogger("nexus.diagnostics").info(
        "history_terminal T=%s D=%s first_submission_winning_signatures=%s post_resolution_evidence_events=%s deep_tier_admitted=false",
        spec.theory,
        spec.discovery,
        first_classes,
        after_resolved_count,
    )


def log_terminal_trace(state, trace, posterior):
    counts = Counter()
    for record in trace:
        action = record.action
        if action.type not in ("operate", "probe"):
            continue
        if action.machine in READERS:
            counts["reader_observations"] += 1
        elif action.machine in PULSES:
            counts["counterfactual_pulses" if action.type == "probe" else "committed_pulses"] += 1
            counts["committed_seal_pulses"] += (
                action.type == "operate" and action.artifact == "seal"
            )
        elif action.machine == "anneal" and action.type == "operate":
            counts["anneals"] += 1
    history = submitted(state)
    procedures = posterior.common_decisions()
    suffix = min(
        (len(word) - len(history) for word in procedures if word[: len(history)] == history),
        default=None,
    )
    logging.getLogger("nexus.diagnostics").info(
        "history_operations reader_observations=%s counterfactual_pulses=%s committed_pulses=%s committed_seal_pulses=%s anneals=%s guaranteed_current_suffix_pulses=%s anneal_recovery_known=%s post_resolution_construction_is_not_waste=true",
        counts["reader_observations"],
        counts["counterfactual_pulses"],
        counts["committed_pulses"],
        counts["committed_seal_pulses"],
        counts["anneals"],
        suffix,
        bool(procedures),
    )
