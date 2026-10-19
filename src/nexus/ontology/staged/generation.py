"""Direct full-prior sampling with no per-seed search or hardness filtering."""

import logging
import secrets
from time import perf_counter

from nexus.evaluation.goal_information import feedback_success_ceiling
from nexus.models.domain import DomainArtifact, DomainInvestigation, DomainStock, DomainTruth
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import Machine, Resources, Room, WorldState
from nexus.ontology.staged.evidence import files
from nexus.ontology.staged.laws import WORLDS, repair
from nexus.ontology.staged.schema import FAMILY, SEALS, Investigation, Specimen

DESCRIPTION = (
    "Investigate linked artificial mechanisms and clear every hidden load on three exit seals."
)


def selection(seed):
    return WORLDS[seed % len(WORLDS)]


def certificate(spec, planning, resource, profile):
    if profile not in ("standard", "diagnostic-plus6"):
        raise ValueError("unknown staged budget profile")
    worlds = 1 if spec.resolved is not None else 27 if spec.known_exponents else 216
    readings = (
        0
        if spec.resolved
        else (3 + sum(e == 2 for e in spec.known_exponents))
        if spec.known_exponents
        else 6
    )
    # Configure reader once per stage, then use two different tags if needed.
    reference = 10 + planning + (3 + readings if readings else 0)
    full_reference = 19 + planning
    budget = full_reference + 20 + (6 if profile == "diagnostic-plus6" else 0)
    return {
        "family": FAMILY,
        "status": "experimental-full-prior-reference",
        "deep_tier_admitted": False,
        "empirical_difficulty_calibrated": False,
        "profile": "dependent-contexts" if spec.linked else "independent-contexts",
        "prior_worlds": worlds,
        "prior": "uniform over all mechanisms conditional on public exponent/exact-law disclosures",
        "sampler": "seed modulo 216; uniform residues give the stated prior, curated matrix rows do not",
        "mission_signatures": worlds,
        "reference_reading_upper": readings,
        "reference_action_upper": reference,
        "action_budget": None if resource == 0 else budget,
        "resource_allowance": budget - reference,
        "budget_profile": profile,
        "feedback_success_ceilings": [
            {
                "feedback_actions": k,
                "numerator": feedback_success_ceiling(worlds, 3, 1, k),
                "denominator": worlds,
            }
            for k in range(1, 8)
        ],
        "bound_scope": "Uniform conditional prior; feedback actions include every reading and every finish. Free configurations, treatments and logistics strengthen the player in this relaxation. Not a total-action optimum or a selected-seed/model failure probability.",
        "fixed_panel_scope": "Offline preflight checks exact reading-only fixed-panel identification. These minima exclude finish guesses and are not universal action lower bounds.",
        "decision_meaning": "The nine committed cumulative doses on all three actual seals; physically eligible in array. Complete repairs, not parameter guesses, are checked.",
        "limitations": "A fixed panel and direct baseline measurements remain legal; no mandatory investigation order. T2 may infer an upstream shift indirectly from downstream carrier activation. Full law identification is necessary for a guaranteed repair in this family only because mission-signature injectivity is proved.",
    }


def initial_state(spec, budget):
    return WorldState(
        agent_room=spec.stock_room,
        artifacts={
            name: DomainArtifact(
                ontology=FAMILY,
                id=name,
                location=spec.stock_room,
                payload=Specimen(tag=u).model_dump(mode="json"),
            )
            for u, name in enumerate(SEALS)
        },
        stocks={
            f"stock-{u}": DomainStock(
                ontology=FAMILY,
                id=f"stock-{u}",
                location=spec.stock_room,
                remaining=None,
                payload={"tag": u},
            )
            for u in range(3)
        },
        machines={
            "reader": Machine(id="reader", room_id="array", uses_remaining=None, settings=(0, 0)),
            "trimmer": Machine(
                id="trimmer", room_id="array", uses_remaining=None, settings=(0, 0, 0)
            ),
            "anneal": Machine(id="anneal", room_id="array", uses_remaining=None),
        },
        resources=Resources(actions_remaining=budget),
    )


def generate_staged(
    seed,
    *,
    discovery_level=4,
    theory_level=3,
    planning_level=1,
    resource_pressure=1,
    verifier_secret=None,
    budget_profile="standard",
):
    start = perf_counter()
    if (
        any(
            type(v) is not int
            for v in (seed, discovery_level, theory_level, planning_level, resource_pressure)
        )
        or planning_level not in (0, 1)
        or resource_pressure not in (0, 1)
    ):
        raise ValueError("staged repair requires integer seed, P0/P1 and R0/R1")
    if verifier_secret == "":
        raise ValueError("verifier secret must not be empty")
    world = selection(seed)
    spec = Investigation(
        theory=theory_level,
        discovery=discovery_level,
        stock_room="stores" if planning_level else "array",
        known_exponents=tuple(m.exponent for m in world.mechanisms) if theory_level == 2 else None,
        resolved=world if theory_level == 0 else None,
        repair=repair(world) if theory_level == 0 else None,
    )
    proof = certificate(spec, planning_level, resource_pressure, budget_profile)
    rooms = {spec.stock_room, spec.mission_room}
    result = PrivateEpisode(
        public=PublicEpisode(
            episode_id=secrets.token_hex(16),
            description=DESCRIPTION,
            rooms={
                r: Room(id=r, label="Staged array" if r == "array" else "Material stores")
                for r in rooms
            },
            edges=() if len(rooms) == 1 else ((spec.stock_room, "array"),),
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
        construction_seed=seed,
        verifier_secret=verifier_secret or secrets.token_hex(32),
        investigation_truth=DomainTruth(ontology=FAMILY, payload=world.model_dump(mode="json")),
        generation_metadata=GenerationMetadata(
            theory_level=theory_level,
            discovery_level=discovery_level,
            planning_level=planning_level,
            resource_pressure=resource_pressure,
            scenario_family_id=FAMILY,
            room_count=len(rooms),
            machine_count=3,
            action_budget=proof["action_budget"] or 0,
            guaranteed_policy_action_count=proof["reference_action_upper"],
            resource_allowance=proof["resource_allowance"],
            budget_profile=budget_profile,
            recommended_tool_call_limit=(proof["action_budget"] or 40) + 24,
            investigation_certificate=proof,
        ),
    )
    logging.getLogger("nexus.generation").info(
        "staged_generated T=%s D=%s P=%s R=%s prior_worlds=%s reference_actions=%s seconds=%.6f deep_tier_admitted=false",
        theory_level,
        discovery_level,
        planning_level,
        resource_pressure,
        proof["prior_worlds"],
        proof["reference_action_upper"],
        perf_counter() - start,
    )
    return result
