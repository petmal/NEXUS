"""Unfiltered deterministic laws; qualification selects operator matrix rows separately."""

import logging
import secrets
from time import perf_counter

from nexus.generator.randomness import rng_for
from nexus.models.domain import DomainArtifact, DomainInvestigation, DomainTruth
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import Machine, Resources, Room, WorldState
from nexus.ontology.stateful.evidence import files
from nexus.ontology.stateful.laws import MODES, WORLDS, shortest
from nexus.ontology.stateful.policy import investigator
from nexus.ontology.stateful.schema import FAMILY, Investigation, Specimen

DESCRIPTION = "Investigate the original seal's coupled registers, preserve its viability, align the exact exit state, and finish."
TARGETS = ((1, 2, 1, 2), (1, 2, 3, 1), (2, 3, 1, 2))


def selection(seed):
    return WORLDS[rng_for(seed, FAMILY, "law").randrange(len(WORLDS))], TARGETS[
        rng_for(seed, FAMILY, "goal").randrange(len(TARGETS))
    ]


def certificate(spec, planning, resource, profile):
    if profile not in ("standard", "diagnostic-plus6"):
        raise ValueError("unsupported stateful budget profile")
    reference = (
        (
            len(spec.procedure) + 1
            if spec.procedure is not None
            else investigator(spec.target, spec.resolved).bound()
        )
        + 1
        + planning
    )  # take and optional move; policy already counts finish
    budget = 64 + (6 if profile == "diagnostic-plus6" else 0)
    if reference > budget:
        raise ValueError("public reference exceeds the common resource allowance")
    return {
        "family": FAMILY,
        "status": "experimental-stateful-reference-qualified",
        "deep_tier_admitted": False,
        "empirical_difficulty_calibrated": False,
        "prior_worlds": 256 if spec.resolved is None else 1,
        "physical_states": 626,
        "reference_action_upper": reference,
        "action_budget": budget if resource else None,
        "resource_allowance": budget - reference,
        "budget_profile": profile,
        "decision_meaning": "immediate finish on the original seal's committed physical history; diagnostic common_repairs is 0 or 1, not the number of future plans",
        "scope": "All-outcome public-policy upper bound, not an optimal action minimum. Exact trajectory and bounded-shortcut admission are separate operator preflight results. Handling/movement included; manifest/evidence/observe are free.",
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
        machines={
            name: Machine(id=name, room_id=spec.mission_room, uses_remaining=None) for name in MODES
        },
        resources=Resources(actions_remaining=budget),
    )


def rooms_for(spec):
    return {
        r: Room(id=r, label="Exit lattice" if r == "array" else "Seal chamber")
        for r in {spec.stock_room, spec.mission_room}
    }


def generate_episode(
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
        raise ValueError("stateful requires integer seed/axes, P0/P1 and R0/R1")
    if verifier_secret == "":
        raise ValueError("verifier secret must not be empty")
    world, target = selection(seed)
    spec = Investigation(
        theory=theory_level,
        discovery=discovery_level,
        target=target,
        stock_room="stores" if planning_level else "array",
        resolved=world if theory_level == 0 else None,
        procedure=shortest(world, target) if discovery_level == 0 else None,
    )
    proof = certificate(spec, planning_level, resource_pressure, budget_profile)
    rooms = rooms_for(spec)
    result = PrivateEpisode(
        public=PublicEpisode(
            episode_id=secrets.token_hex(16),
            description=DESCRIPTION,
            rooms=rooms,
            edges=() if planning_level == 0 else ((spec.stock_room, spec.mission_room),),
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
            machine_count=4,
            action_budget=proof["action_budget"] or 0,
            guaranteed_policy_action_count=proof["reference_action_upper"],
            resource_allowance=proof["resource_allowance"],
            budget_profile=budget_profile,
            recommended_tool_call_limit=120,
            investigation_certificate=proof,
        ),
    )
    logging.getLogger("nexus.generation").info(
        "stateful_generated T=%s D=%s P=%s R=%s public_policy_upper=%s seconds=%.6f empirical_difficulty_calibrated=false",
        theory_level,
        discovery_level,
        planning_level,
        resource_pressure,
        proof["reference_action_upper"],
        perf_counter() - started,
    )
    return result
