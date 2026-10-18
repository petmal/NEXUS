"""Seed-independent compiled prior; generation never searches a selected truth."""

from __future__ import annotations

import logging
import secrets
from time import perf_counter

from nexus.generator.randomness import rng_for
from nexus.models.domain import DomainArtifact, DomainInvestigation, DomainStock, DomainTruth
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import Machine, Resources, Room, WorldState
from nexus.ontology.history.evidence import files
from nexus.ontology.history.laws import PULSES, READERS, WORLDS, shortest
from nexus.ontology.history.policy import bound
from nexus.ontology.history.schema import FAMILY, Investigation, Specimen

DESCRIPTION = "Investigate a history-dependent array, construct an exit seal with exact physical registers, and finish."
APPARATUS = (*PULSES, *READERS, "anneal")


def selection(seed):
    return WORLDS[rng_for(seed, FAMILY, "mechanism").randrange(len(WORLDS))]


def certificate(spec, planning, resource, profile):
    if profile not in ("standard", "diagnostic-plus6"):
        raise ValueError("unknown history budget profile")
    readings, cost = bound((1 << len(WORLDS)) - 1)
    upper = 3 + planning + cost  # take seal, take survey, finish, move
    reference = 2 + planning + len(spec.procedure) if spec.procedure is not None else upper
    extra = 8 + (6 if profile == "diagnostic-plus6" else 0)
    return {
        "family": FAMILY,
        "status": "experimental-poc-reference-qualified",
        "empirical_difficulty_calibrated": False,
        "deep_tier_admitted": False,
        "prior_worlds": 1 if spec.resolved is not None else len(WORLDS),
        "legal_preparation_histories": 87381,
        "reference_reading_upper": 0 if spec.resolved is not None else readings,
        "reference_action_upper": reference,
        "resource_allowance": extra,
        "action_budget": None if resource == 0 else upper + extra,
        "budget_profile": profile,
        "decision_meaning": "complete pulse history from zero; a known fresh procedure remains recoverable by one charged anneal",
        "measurement_meaning": "all visible evidence events, including necessary physical construction; redundant or post-resolution pulses are not automatically waste",
        "intervention_guarantee": "both physical-clamp channels necessary for guaranteed first submission from measurements alone; excludes rejected-finish evidence",
        "shortcut": "after normalized law identification, <=8 pulses and <=4 finishes can guarantee escape without either intervention; fixed nine-query panel identifies full prior",
        "scope": "Exact overlapping winning-history sets. No mandatory adaptive-round or universal deep-reasoning claim. T0 uses identical physical laws, goal and action budget.",
    }


def initial_state(spec, budget):
    return WorldState(
        agent_room=spec.stock_room,
        artifacts={
            "seal": DomainArtifact(
                ontology=FAMILY,
                id="seal",
                location=spec.stock_room,
                payload=Specimen().model_dump(mode="json"),
            )
        },
        stocks={
            "stock": DomainStock(
                ontology=FAMILY, id="stock", location=spec.stock_room, remaining=None, payload={}
            )
        },
        machines={
            name: Machine(id=name, room_id=spec.mission_room, uses_remaining=None)
            for name in APPARATUS
        },
        resources=Resources(actions_remaining=budget),
    )


def generate_history(
    seed,
    *,
    discovery_level=5,
    theory_level=3,
    planning_level=1,
    resource_pressure=1,
    verifier_secret=None,
    budget_profile="standard",
):
    started = perf_counter()
    if (
        any(
            type(v) is not int
            for v in (seed, discovery_level, theory_level, planning_level, resource_pressure)
        )
        or planning_level not in (0, 1)
        or resource_pressure not in (0, 1)
    ):
        raise ValueError("history requires integer seed and P0/P1,R0/R1")
    if verifier_secret == "":
        raise ValueError("verifier secret must not be empty")
    world = selection(seed)
    spec = Investigation(
        theory=theory_level,
        discovery=discovery_level,
        stock_room="stores" if planning_level else "array",
        resolved=world if theory_level == 0 else None,
        procedure=shortest(world) if theory_level == 0 else None,
    )
    proof = certificate(spec, planning_level, resource_pressure, budget_profile)
    rooms = {spec.stock_room, spec.mission_room}
    result = PrivateEpisode(
        public=PublicEpisode(
            episode_id=secrets.token_hex(16),
            description=DESCRIPTION,
            rooms={
                r: Room(id=r, label="Coupled array" if r == "array" else "Material stores")
                for r in rooms
            },
            edges=() if len(rooms) == 1 else ((spec.stock_room, spec.mission_room),),
            phase_modulus=1,
            initial_state=initial_state(spec, proof["action_budget"]),
            goal=GoalPredicate(kind=GoalKind.MISSION_ACCEPTED),
            evidence_files=files(spec),
            investigation=DomainInvestigation(
                ontology=FAMILY, payload=spec.model_dump(mode="json")
            ),
        ),
        rules={},
        machine_rules={},
        verifier_secret=verifier_secret or secrets.token_hex(32),
        construction_seed=seed,
        investigation_truth=DomainTruth(ontology=FAMILY, payload=world.model_dump(mode="json")),
        generation_metadata=GenerationMetadata(
            theory_level=theory_level,
            discovery_level=discovery_level,
            planning_level=planning_level,
            resource_pressure=resource_pressure,
            scenario_family_id=FAMILY,
            room_count=len(rooms),
            machine_count=len(APPARATUS),
            action_budget=proof["action_budget"] or 0,
            guaranteed_policy_action_count=proof["reference_action_upper"],
            resource_allowance=proof["resource_allowance"],
            budget_profile=budget_profile,
            recommended_tool_call_limit=(proof["action_budget"] or proof["reference_action_upper"])
            + 24,
            investigation_certificate=proof,
        ),
    )
    logging.getLogger("nexus.generation").info(
        "history_generated T=%s D=%s P=%s R=%s shortest_physical_pulses=%s reference_actions=%s seconds=%.6f deep_tier_admitted=false",
        theory_level,
        discovery_level,
        planning_level,
        resource_pressure,
        len(shortest(world)),
        proof["reference_action_upper"],
        perf_counter() - started,
    )
    return result
