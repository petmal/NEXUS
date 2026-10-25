"""Matched laws/targets with public layouts and truth-independent T3 budgets."""

import secrets

from nexus.models.domain import DomainArtifact, DomainInvestigation, DomainTruth
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import Machine, Resources, Room, WorldState
from nexus.ontology.planning.evidence import files
from nexus.ontology.planning.layout import LAYOUTS
from nexus.ontology.planning.policy import reference_cost
from nexus.ontology.planning.schema import FAMILY, Investigation
from nexus.ontology.stateful.generation import selection
from nexus.ontology.stateful.laws import MODES
from nexus.ontology.stateful.schema import Specimen

DESCRIPTION = "Plan transformations and travel on a disclosed map; align the original seal and finish in array."


def certificate(spec, resource):
    reference = reference_cost(spec)
    slack = max(6, (reference + 1) // 2) if resource == 1 else 0
    return {
        "family": FAMILY,
        "status": "experimental-public-reference-qualified",
        "empirical_difficulty_calibrated": False,
        "map_visibility": "complete",
        "reference_kind": "exact-known-law-optimum"
        if spec.theory == 0
        else "public-policy-upper-bound",
        "reference_action_upper": reference,
        "action_budget": reference + slack if resource else None,
        "resource_allowance": slack,
        "scope": (
            "Includes take, moves, operations/probes and finish. T0 is an exact physical "
            "minimum. T3 is the worst-case cost of one public policy over all 256 laws, "
            "not an optimal minimum or proof of necessary experimentation. R2 has no "
            "slack above the respective reference; compare R within matched P/T/world."
        ),
    }


def initial_state(spec, budget):
    layout = LAYOUTS[spec.planning]
    return WorldState(
        agent_room=layout.start,
        artifacts={
            "seal": DomainArtifact(
                ontology=FAMILY,
                id="seal",
                location=layout.start,
                payload=Specimen().model_dump(mode="json"),
            )
        },
        machines={
            name: Machine(id=name, room_id=room, uses_remaining=None)
            for name, room in zip(MODES, layout.mode_rooms)
        },
        resources=Resources(actions_remaining=budget),
    )


def rooms_for(spec):
    return {
        room: Room(id=room, label="Exit lattice" if room == "array" else f"Mode room {room}")
        for room in LAYOUTS[spec.planning].rooms
    }


def metadata(spec, resource, proof):
    return GenerationMetadata(
        theory_level=spec.theory,
        discovery_level=5,
        planning_level=spec.planning,
        resource_pressure=resource,
        scenario_family_id=FAMILY,
        room_count=len(LAYOUTS[spec.planning].rooms),
        machine_count=4,
        action_budget=proof["action_budget"] or 0,
        guaranteed_policy_action_count=proof["reference_action_upper"],
        resource_allowance=proof["resource_allowance"],
        budget_profile="standard",
        recommended_tool_call_limit=max(
            120, 3 * (proof["action_budget"] or proof["reference_action_upper"]) + 20
        ),
        investigation_certificate=proof,
    )


def generate_episode(
    seed,
    *,
    discovery_level=5,
    theory_level=0,
    planning_level=0,
    resource_pressure=1,
    verifier_secret=None,
    budget_profile="standard",
):
    if (
        any(
            type(v) is not int
            for v in (seed, discovery_level, theory_level, planning_level, resource_pressure)
        )
        or theory_level not in (0, 3)
        or discovery_level != 5
        or planning_level not in range(4)
        or resource_pressure not in range(3)
        or budget_profile != "standard"
    ):
        raise ValueError(
            "stateful-planning requires integer axes: T0/T3, D5, P0..P3, R0..R2, standard budget"
        )
    if verifier_secret == "":
        raise ValueError("verifier secret must not be empty")
    world, target = selection(seed)
    spec = Investigation(
        theory=theory_level,
        planning=planning_level,
        target=target,
        resolved=world if theory_level == 0 else None,
    )
    proof = certificate(spec, resource_pressure)
    return PrivateEpisode(
        public=PublicEpisode(
            episode_id=secrets.token_hex(16),
            description=DESCRIPTION,
            rooms=rooms_for(spec),
            edges=LAYOUTS[planning_level].edges,
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
        generation_metadata=metadata(spec, resource_pressure, proof),
    )
