"""Constant-size direct generation; exhaustive difficulty searches remain offline."""

import logging
import secrets
from time import perf_counter

from nexus.models.domain import DomainArtifact, DomainInvestigation, DomainStock, DomainTruth
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import Machine, Resources, Room, WorldState
from nexus.ontology.assembly.evidence import files
from nexus.ontology.assembly.laws import WORLDS
from nexus.ontology.assembly.schema import FAMILY, Investigation, Specimen

DESCRIPTION = "Prepare compatible components and assemble the exit compensator in an artificial phase workshop."


def selection(seed):
    return WORLDS[seed % len(WORLDS)]


def certificate(spec, resource, profile):
    if resource not in (0, 1) or profile not in ("standard", "diagnostic-plus6"):
        raise ValueError("assembly supports R0/R1 and standard/diagnostic-plus6 budgets")
    planning = int(spec.stock_room != "workshop")
    # Proven greedy upper bound: seven readings, each with its own configuration.
    # Take, two forge configure/operate pairs, assembler pair, finish = eight.
    reference = 8 + planning + (0 if spec.resolved is not None else 14)
    budget = 40 + planning + (6 if profile == "diagnostic-plus6" else 0)
    return {
        "family": FAMILY,
        "status": "experimental-joint-inference",
        "deep_tier_admitted": False,
        "empirical_difficulty_calibrated": False,
        "profile": "coupled-reader" if spec.coupled_reader else "calibrated-reader",
        "prior_worlds": 1
        if spec.resolved is not None
        else 108
        if spec.known_kernel is not None
        else 432,
        "sampler": "seed modulo 432 over full public prior; matrix seeds are curated, not random samples",
        "reference_reading_upper": 0 if spec.resolved is not None else 7,
        "reference_action_upper": reference,
        "action_budget": None if resource == 0 else budget,
        "resource_allowance": budget - reference,
        "budget_profile": profile,
        "decision_meaning": "Both committed component gains/phases and installed kernel on actual carrier; all nine joint outputs plus both local gain contracts.",
        "qualification_scope": "Offline preflight proves complete-build evidence certificates and channel-closure obstructions, audits all response classes and finish guesses, and executes public policies. No minimum total-action or deep-cognition claim.",
    }


def initial_state(spec, budget):
    return WorldState(
        agent_room=spec.stock_room,
        artifacts={
            "carrier": DomainArtifact(
                ontology=FAMILY,
                id="carrier",
                location=spec.stock_room,
                payload=Specimen().model_dump(mode="json"),
            )
        },
        stocks={
            "blank-stock": DomainStock(
                ontology=FAMILY,
                id="blank-stock",
                location=spec.stock_room,
                remaining=None,
                payload={},
            )
        },
        machines={
            "reader": Machine(
                id="reader", room_id="workshop", uses_remaining=None, settings=(0, 0, 0)
            ),
            "forge": Machine(
                id="forge", room_id="workshop", uses_remaining=None, settings=(0, 1, 0)
            ),
            "assembler": Machine(
                id="assembler", room_id="workshop", uses_remaining=None, settings=(0,)
            ),
        },
        resources=Resources(actions_remaining=budget),
    )


def metadata(spec, resource, profile):
    proof = certificate(spec, resource, profile)
    planning = int(spec.stock_room != "workshop")
    return GenerationMetadata(
        theory_level=spec.theory,
        discovery_level=spec.discovery,
        planning_level=planning,
        resource_pressure=resource,
        scenario_family_id=FAMILY,
        room_count=1 + planning,
        machine_count=3,
        action_budget=proof["action_budget"] or 0,
        guaranteed_policy_action_count=proof["reference_action_upper"],
        resource_allowance=proof["resource_allowance"],
        budget_profile=profile,
        recommended_tool_call_limit=(proof["action_budget"] or 40) + 24,
        investigation_certificate=proof,
    )


def topology(spec):
    rooms = {
        r: Room(id=r, label="Phase workshop" if r == "workshop" else "Carrier stores")
        for r in (spec.stock_room, "workshop")
    }
    return rooms, () if spec.stock_room == "workshop" else ((spec.stock_room, "workshop"),)


def generate_assembly(
    seed,
    *,
    discovery_level=4,
    theory_level=3,
    planning_level=0,
    resource_pressure=1,
    verifier_secret=None,
    budget_profile="standard",
):
    start = perf_counter()
    if any(
        type(v) is not int
        for v in (seed, discovery_level, theory_level, planning_level, resource_pressure)
    ) or planning_level not in (0, 1):
        raise ValueError("assembly requires integer seed/axes and P0/P1")
    if verifier_secret == "":
        raise ValueError("verifier secret must not be empty")
    world = selection(seed)
    spec = Investigation(
        theory=theory_level,
        discovery=discovery_level,
        stock_room="stores" if planning_level else "workshop",
        known_kernel=world.kernel if theory_level == 2 else None,
        resolved=world if theory_level == 0 else None,
    )
    meta = metadata(spec, resource_pressure, budget_profile)
    rooms, edges = topology(spec)
    episode = PrivateEpisode(
        public=PublicEpisode(
            episode_id=secrets.token_hex(16),
            description=DESCRIPTION,
            rooms=rooms,
            edges=edges,
            phase_modulus=1,
            initial_state=initial_state(spec, meta.investigation_certificate["action_budget"]),
            goal=GoalPredicate(kind=GoalKind.MISSION_ACCEPTED),
            evidence_files=files(spec),
            investigation=DomainInvestigation(
                ontology=FAMILY, payload=spec.model_dump(mode="json")
            ),
        ),
        rules={},
        machine_rules={},
        construction_seed=seed,
        verifier_secret=verifier_secret or secrets.token_hex(32),
        investigation_truth=DomainTruth(ontology=FAMILY, payload=world.model_dump(mode="json")),
        generation_metadata=meta,
    )
    logging.getLogger("nexus.generation").info(
        "assembly_generated T=%s D=%s P=%s R=%s seconds=%.6f reference_actions=%s qualification=offline-required",
        theory_level,
        discovery_level,
        planning_level,
        resource_pressure,
        perf_counter() - start,
        meta.guaranteed_policy_action_count,
    )
    return episode
