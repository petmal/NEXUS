"""Direct generation of both pilots; exhaustive difficulty audits run offline."""

import logging
import secrets
from time import perf_counter

from nexus.models.domain import DomainArtifact, DomainInvestigation, DomainStock, DomainTruth
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import Machine, Resources, Room, WorldState
from nexus.ontology.discovery.domains import ADAPTERS, module
from nexus.ontology.discovery.schema import Specimen

BUDGET = 64
REFERENCE_UPPER = 16  # proved public policies: <=6 readings, plus four construction actions
DESCRIPTIONS = {
    "coupled-memory-v1": "Reconstruct the transfer lattice's predictive cartridge to reopen the sealed facility.",
    "representation-discovery-v1": "Restore a predictive memory cartridge to open the sealed facility.",
    "uncertainty-construction-v1": "Build a disturbance-tolerant exit compensator in the sealed facility.",
}


def initial_state(family, budget):
    return WorldState(
        agent_room="workshop",
        artifacts={
            "carrier": DomainArtifact(
                ontology=family,
                id="carrier",
                location="workshop",
                payload=Specimen().model_dump(mode="json"),
            )
        },
        stocks={
            "blank-stock": DomainStock(
                ontology=family, id="blank-stock", location="workshop", remaining=None, payload={}
            )
        },
        machines={
            "reader": Machine(
                id="reader",
                room_id="workshop",
                uses_remaining=None,
                settings=ADAPTERS[family].reader,
            ),
            "assembler": Machine(
                id="assembler",
                room_id="workshop",
                uses_remaining=None,
                settings=ADAPTERS[family].assembler,
            ),
        },
        resources=Resources(actions_remaining=budget),
    )


def metadata(family, spec, resource, profile):
    if resource not in (0, 1) or profile != "standard":
        raise ValueError("discovery pilots support R0/R1 and standard budget only")
    law = module(family, "laws")
    prior = law.prior_mask(spec).bit_count()
    certificate = {
        "family": family,
        "status": "experimental-discovery-pilot",
        "deep_tier_admitted": False,
        "empirical_difficulty_calibrated": False,
        "prior_mechanism_programs": prior,
        "schedule_multiplicity": ADAPTERS[family].schedule_multiplicity,
        "action_budget": None if resource == 0 else BUDGET,
        "reference_action_upper": 4 if spec.theory == 0 else REFERENCE_UPPER,
        "budget_profile": profile,
        "qualification_scope": "Exact behavior and complete-build acceptance; offline shortcut/source/matrix preflight required. No cognitive-depth or model-failure claim.",
    }
    return GenerationMetadata(
        theory_level=spec.theory,
        discovery_level=spec.discovery,
        planning_level=0,
        resource_pressure=resource,
        scenario_family_id=family,
        room_count=1,
        machine_count=2,
        action_budget=certificate["action_budget"] or 0,
        guaranteed_policy_action_count=certificate["reference_action_upper"],
        resource_allowance=BUDGET - certificate["reference_action_upper"],
        budget_profile=profile,
        recommended_tool_call_limit=120,
        investigation_certificate=certificate,
    )


def generate(
    family,
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
    if (
        any(
            type(v) is not int
            for v in (seed, discovery_level, theory_level, planning_level, resource_pressure)
        )
        or planning_level != 0
    ):
        raise ValueError("discovery pilots require integer seed/axes and P0")
    if verifier_secret == "":
        raise ValueError("verifier secret must not be empty")
    laws = module(family, "laws")
    world = laws.selection(seed)
    spec = laws.specification(world, theory_level, discovery_level)
    meta = metadata(family, spec, resource_pressure, budget_profile)
    episode = PrivateEpisode(
        public=PublicEpisode(
            episode_id=secrets.token_hex(16),
            description=DESCRIPTIONS[family],
            rooms={"workshop": Room(id="workshop", label="Sealed facility workshop")},
            edges=(),
            phase_modulus=1,
            initial_state=initial_state(family, meta.investigation_certificate["action_budget"]),
            goal=GoalPredicate(kind=GoalKind.MISSION_ACCEPTED),
            evidence_files=module(family, "evidence").files(spec),
            investigation=DomainInvestigation(
                ontology=family, payload=spec.model_dump(mode="json")
            ),
        ),
        rules={},
        machine_rules={},
        construction_seed=seed,
        verifier_secret=verifier_secret or secrets.token_hex(32),
        investigation_truth=DomainTruth(ontology=family, payload=world.model_dump(mode="json")),
        generation_metadata=meta,
    )
    logging.getLogger("nexus.generation").info(
        "discovery_generated family=%s T=%s D=%s R=%s seconds=%.6f qualification=offline-required",
        family,
        theory_level,
        discovery_level,
        resource_pressure,
        perf_counter() - start,
    )
    return episode
