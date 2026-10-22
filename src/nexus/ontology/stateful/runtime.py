"""Thin ontology adapter. Engine owns action charging, atomicity and receipts."""

import logging
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
from nexus.models.world import INVENTORY
from nexus.ontology.inference import Measurement
from nexus.ontology.stateful.laws import (
    MODES,
    WORLD_INDEX,
    encode,
    history_states,
    readout,
    shortest,
)
from nexus.ontology.stateful.schema import FAMILY, Specimen

performance_style = "mission"
requires_single_session = True


def validate_episode(episode):
    from nexus.ontology.stateful.evidence import files
    from nexus.ontology.stateful.generation import (
        DESCRIPTION,
        certificate,
        initial_state,
        rooms_for,
        selection,
    )

    spec = episode.public.investigation.data()
    truth = episode.investigation_truth.data()
    meta = episode.generation_metadata
    planning = int(spec.stock_room != spec.mission_room)
    if type(episode.construction_seed) is not int or (truth, spec.target) != selection(
        episode.construction_seed
    ):
        raise ValueError("stateful laws or target differ from construction seed")
    if spec.resolved is not None and spec.resolved != truth:
        raise ValueError("disclosed law contradicts the physical law")
    if spec.procedure is not None and spec.procedure != shortest(truth, spec.target):
        raise ValueError("supplied procedure differs from control")
    if meta.resource_pressure not in (0, 1):
        raise ValueError("unsupported stateful resource profile")
    proof = certificate(spec, planning, meta.resource_pressure, meta.budget_profile)
    public = episode.public
    if (
        public.description != DESCRIPTION
        or public.evidence_files != files(spec)
        or public.initial_state != initial_state(spec, proof["action_budget"])
        or public.rooms != rooms_for(spec)
        or public.edges != (() if planning == 0 else ((spec.stock_room, spec.mission_room),))
        or public.phase_modulus != 1
        or public.goal != GoalPredicate(kind=GoalKind.MISSION_ACCEPTED)
        or episode.rules
        or episode.machine_rules
    ):
        raise ValueError("stateful public world differs from compiled contract")
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
        len(public.rooms),
        4,
        proof["action_budget"] or 0,
        proof["reference_action_upper"],
        proof["resource_allowance"],
        120,
        proof,
    ):
        raise ValueError("stateful metadata differs from compiled contract")


def spawn(stock, artifact_id):
    raise ValueError("this world has one original seal and no specimen stock")


def configure(episode, state, action):
    raise ValueError("stateful modes accept operate/probe, not configure")


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


def mission_room(spec):
    return spec.data().mission_room


def mission_machine(spec):
    return MODES[0]


def expected(episode):
    return shortest(episode.investigation_truth.data(), episode.public.investigation.data().target)


def submitted(state):
    return state.artifacts["seal"].data().history


def assess_mission(episode, state):
    spec = episode.public.investigation.data()
    actual = history_states(submitted(state))[WORLD_INDEX[episode.investigation_truth.data()]]
    state.mission_accepted = (
        state.agent_room == spec.mission_room
        and state.artifacts["seal"].location == INVENTORY
        and actual == encode(spec.target)
    )


def physical_plan(episode):
    spec = episode.public.investigation.data()
    return (
        TakeAction(artifact="seal"),
        *((MoveAction(target=spec.mission_room),) if spec.stock_room != spec.mission_room else ()),
        *(OperateAction(machine=MODES[a], artifact="seal") for a in expected(episode)),
        FinishAction(),
    )


def measurement(record):
    action = record.action
    if action.type not in ("operate", "probe") or action.machine not in MODES:
        return None
    payload = next(e.details["result"]["payload"] for e in record.events if "result" in e.details)
    return Measurement(action.machine, {**payload, "committed": action.type == "operate"})


def measurement_features(item):
    return MODES.index(item.instrument), item.sample["committed"]


def belief(spec):
    from nexus.ontology.stateful.inference import Belief

    return Belief(spec.data())


@dataclass
class Tracker:
    room: str
    mission: str
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
            self.history = tuple(measurement(record).sample["history"])

    def attempted(self):
        return self.history if self.location == INVENTORY and self.room == self.mission else None


def mission_tracker(public):
    return Tracker(
        public.initial_state.agent_room,
        mission_room(public.investigation),
        public.initial_state.artifacts["seal"].location,
    )


def public_contract(spec):
    result = action_contract(scientific=True)
    result["schema"] = action_contract()["schema"]
    result["reference"] = tuple(
        r for r in result["reference"] if r["type"] not in ("configure", "measure")
    )
    result["ontology"] = {
        "family": FAMILY,
        "experimental": True,
        "modes": MODES,
        "configuration": {},
        "mission": "Align the original seal's four physical registers with the exact public target, carry it in array, and finish.",
        "contract": "Read every evidence file. Only x0 is visible. Every committed experiment changes the original exit seal. Ordinary one-step probes do not change it. No reset, duplicate stock or independent reference.",
    }
    return result


def log_terminal(spec, calibration_count, no_signal_count, after_resolved_count, first_classes):
    logging.getLogger("nexus.diagnostics").info(
        "stateful_terminal T=%s D=%s decision_scope=immediate_finish first_submission_acceptance_classes=%s operations_after_ready=%s",
        spec.theory,
        spec.discovery,
        first_classes,
        after_resolved_count,
    )


def log_terminal_trace(state, trace, posterior):
    committed = sum(r.action.type == "operate" for r in trace)
    probes = sum(r.action.type == "probe" for r in trace)
    logging.getLogger("nexus.diagnostics").info(
        "stateful_trajectory committed=%s counterfactual=%s remaining_laws=%s remaining_physical_states=%s collapsed=%s immediate_finish_supported=%s",
        committed,
        probes,
        len(posterior.worlds),
        len({history_states(posterior.history)[w] for w in posterior.worlds}),
        state.artifacts["seal"].data().reading == 5,
        posterior.supports(posterior.history),
    )
