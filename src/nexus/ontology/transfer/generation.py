"""Paired full-prior worlds with offline bounded witnesses, no per-seed search."""

import secrets
from typing import Literal

from nexus.models.domain import DomainArtifact, DomainInvestigation, DomainStock, DomainTruth
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import Machine, Resources, Room, WorldState
from nexus.ontology.transfer.evidence import files
from nexus.ontology.transfer.laws import PROGRAMS, PROGRAM_INDEX, selection
from nexus.ontology.transfer.reference import load
from nexus.ontology.transfer.schema import Investigation, Specimen

APPARATUS = ("stage", "sensor", "doser")
DESCRIPTION = "Infer a counterphase mechanism and program a carried exit seal to cancel its physical response across the complete public context/input/trim domain."


def certificate(spec, planning, profile):
    if profile not in ("standard", "diagnostic-plus6"):
        raise ValueError("unknown transfer budget profile")
    readings = (
        0
        if spec.resolved is not None
        else load()["coupled" if spec.coupled else "calibrated"]["readings"]
    )
    bound = (
        4 + planning
        if spec.resolved is not None
        else 5 + int(spec.coupled) + planning + 3 * readings
    )
    extra = 6 if profile == "standard" else 12
    return {
        "family": spec.family,
        "status": "experimental-reference-qualified",
        "empirical_difficulty_calibrated": False,
        "prior_worlds": (15552 if spec.coupled else 5184) if spec.resolved is None else None,
        "mission_behavior_classes": 5016 if spec.resolved is None else 1,
        "mission_conditions": 486,
        "reference_reading_upper": readings,
        "reference_action_upper": bound,
        "budget_profile": profile,
        "resource_allowance": extra,
        "scope": "Full disclosed grammar; offline public-policy upper bound. No cognitive-depth/adaptive-round/model-failure claim. Matrix fixtures are targeted, not a uniform sample.",
    }


def initial_state(spec, budget):
    return WorldState(
        agent_room=spec.stock_room,
        artifacts={
            "seal": DomainArtifact(
                ontology=spec.family,
                id="seal",
                location=spec.stock_room,
                payload=Specimen(material="seal").model_dump(mode="json"),
            )
        },
        stocks={
            name: DomainStock(
                ontology=spec.family,
                id=name,
                location=spec.stock_room,
                remaining=None,
                payload={"material": material},
            )
            for name, material in (("stock", "survey"), ("reference-stock", "reference"))
        },
        machines={
            name: Machine(id=name, room_id=spec.mission_room, uses_remaining=None, settings=None)
            for name in APPARATUS
        },
        resources=Resources(actions_remaining=budget),
    )


def generate(
    seed,
    *,
    coupled,
    discovery_level: Literal[0, 5] = 5,
    theory_level: Literal[0, 3] = 3,
    planning_level=1,
    resource_pressure=1,
    verifier_secret=None,
    budget_profile: Literal["standard", "diagnostic-plus6"] = "standard",
):
    if (
        any(
            type(v) is not int
            for v in (seed, discovery_level, theory_level, planning_level, resource_pressure)
        )
        or planning_level not in (0, 1)
        or resource_pressure != 1
    ):
        raise ValueError("transfer requires integer seed and P0/P1,R1")
    if verifier_secret == "":
        raise ValueError("verifier secret must not be empty")
    program, offset = selection(seed)
    representative = PROGRAMS[load()["targets"][PROGRAM_INDEX[program]]]
    spec = Investigation(
        theory=theory_level,
        discovery=discovery_level,
        coupled=coupled,
        stock_room="stores" if planning_level else "array",
        resolved=representative if theory_level == 0 else None,
    )
    proof = certificate(spec, planning_level, budget_profile)
    bound, extra = proof["reference_action_upper"], proof["resource_allowance"]
    rooms = {spec.stock_room, spec.mission_room}
    return PrivateEpisode(
        public=PublicEpisode(
            episode_id=secrets.token_hex(16),
            description=DESCRIPTION,
            rooms={
                room: Room(id=room, label="Coupled array" if room == "array" else "Material stores")
                for room in rooms
            },
            edges=() if len(rooms) == 1 else ((spec.stock_room, spec.mission_room),),
            phase_modulus=1,
            initial_state=initial_state(spec, bound + extra),
            goal=GoalPredicate(kind=GoalKind.MISSION_ACCEPTED),
            evidence_files=files(spec),
            investigation=DomainInvestigation(
                ontology=spec.family, payload=spec.model_dump(mode="json")
            ),
        ),
        rules={},
        machine_rules={},
        verifier_secret=verifier_secret or secrets.token_hex(32),
        construction_seed=seed,
        investigation_truth=DomainTruth(
            ontology=spec.family,
            payload={"program": list(program), "reader_offset": offset if coupled else 0},
        ),
        generation_metadata=GenerationMetadata(
            theory_level=theory_level,
            discovery_level=discovery_level,
            planning_level=planning_level,
            resource_pressure=1,
            scenario_family_id=spec.family,
            room_count=len(rooms),
            machine_count=3,
            action_budget=bound + extra,
            guaranteed_policy_action_count=bound,
            resource_allowance=extra,
            budget_profile=budget_profile,
            recommended_tool_call_limit=bound + extra + 24,
            investigation_certificate=proof,
        ),
    )


def generate_transfer(seed, **kwargs):
    return generate(seed, coupled=False, **kwargs)


def generate_evidence(seed, **kwargs):
    return generate(seed, coupled=True, **kwargs)
