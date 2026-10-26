"""Deterministic mechanically admitted paired fixtures, without seed substitution."""

import secrets
from functools import lru_cache
from itertools import product
from random import Random

from nexus.models.domain import DomainArtifact, DomainInvestigation, DomainTruth
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import Machine, Resources, Room, WorldState
from nexus.ontology.coordination.evidence import files
from nexus.ontology.coordination.laws import distances, encode
from nexus.ontology.coordination.layout import layout_for
from nexus.ontology.coordination.planner import bank_contiguous_cost, optimal
from nexus.ontology.coordination.schema import (
    FAMILY,
    GenerationOptions,
    Investigation,
    Specimen,
    Truth,
    topology,
)

DESCRIPTION = (
    "Coordinate the original seal's disclosed register banks on a complete public map; "
    "hold every target simultaneously and finish in array."
)
DEFAULT_OPTIONS = GenerationOptions()


@lru_cache(maxsize=32, typed=True)
def selection(seed: int, banks: int, registers_per_bank: int):
    if type(seed) is not int:
        raise ValueError("construction seed must be an integer")
    independent = GenerationOptions(
        banks=banks, registers_per_bank=registers_per_bank, coupling="independent"
    )
    coupled = GenerationOptions(
        banks=banks, registers_per_bank=registers_per_bank, coupling="coupled"
    )
    rng = Random(f"nexus-coordination-v1:{seed}:{banks}:{registers_per_bank}")
    world = Truth(
        gains=tuple(rng.choice((1, 2)) for _ in range(coupled.count)),
        powers=tuple(rng.choice((1, 2)) for _ in range(coupled.count)),
    )
    independent_distances = distances(world, independent)
    coupled_distances = distances(world, coupled)
    targets = list(product((1, 2), repeat=coupled.count))
    rng.shuffle(targets)
    targets.sort(key=lambda target: coupled_distances[encode(target)], reverse=True)
    for target in targets:
        state = encode(target)
        if independent_distances[state] <= 0 or coupled_distances[state] <= 0:
            continue
        spec = Investigation(
            options=coupled, topology=topology(coupled), resolved=world, target=target
        )
        try:
            baseline = bank_contiguous_cost(spec)
        except ValueError:
            continue
        if coupled_distances[state] + 2 < baseline:
            return world, target
    raise ValueError(
        f"seed {seed} has no paired reachable target with a finite strict bank-interleaving gap "
        f"for {banks} banks of {registers_per_bank} registers"
    )


def certificate(spec, resource):
    reference = optimal(spec).actions
    slack = max(6, (reference + 1) // 2) if resource == 1 else 0
    return {
        "family": FAMILY,
        "status": "experimental-public-reference-qualified",
        "empirical_difficulty_calibrated": False,
        "map_visibility": "complete",
        "law_visibility": "complete",
        "state_visibility": "complete",
        "reference_kind": "exact-known-law-optimum",
        "reference_action_upper": reference,
        "action_budget": reference + slack if resource else None,
        "resource_allowance": slack,
        "scope": (
            "Exact joint state/location minimum including take, travel, operations and finish. "
            "R2 allows exactly that minimum; R1 adds max(6,ceil(minimum/2)); R0 is uncapped. "
            "Both paired targets are reachable and the coupled P0 optimum strictly beats "
            "every bank-contiguous solution. Structural sizes are not calibrated difficulty."
        ),
    }


def initial_state(spec, budget):
    layout = layout_for(spec)
    return WorldState(
        agent_room=layout.start,
        artifacts={
            "seal": DomainArtifact(
                ontology=FAMILY,
                id="seal",
                location=layout.start,
                payload=Specimen(registers=(0,) * spec.options.count).model_dump(mode="json"),
            )
        },
        machines={
            coordinate.machine: Machine(id=coordinate.machine, room_id=room, uses_remaining=None)
            for coordinate, room in zip(spec.topology, layout.mode_rooms, strict=True)
        },
        resources=Resources(actions_remaining=budget),
    )


def rooms_for(spec):
    return {
        room: Room(id=room, label="Exit array" if room == "array" else f"Mode room {room}")
        for room in layout_for(spec).rooms
    }


def metadata(spec, resource, proof):
    return GenerationMetadata(
        theory_level=0,
        discovery_level=0,
        planning_level=spec.planning,
        resource_pressure=resource,
        scenario_family_id=FAMILY,
        room_count=len(layout_for(spec).rooms),
        machine_count=spec.options.count,
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
    theory_level=0,
    discovery_level=0,
    planning_level=0,
    resource_pressure=2,
    budget_profile="standard",
    options=DEFAULT_OPTIONS,
    verifier_secret=None,
):
    if (
        any(
            type(v) is not int
            for v in (seed, theory_level, discovery_level, planning_level, resource_pressure)
        )
        or theory_level != 0
        or discovery_level != 0
        or planning_level not in (0, 3)
        or resource_pressure not in (0, 1, 2)
        or budget_profile != "standard"
    ):
        raise ValueError(
            "coordination requires integer axes T0/D0, P0/P3, R0..R2 and standard budget"
        )
    options = GenerationOptions.model_validate(options)
    if verifier_secret == "":
        raise ValueError("verifier secret must not be empty")
    world, target = selection(seed, options.banks, options.registers_per_bank)
    spec = Investigation(
        planning=planning_level,
        options=options,
        topology=topology(options),
        resolved=world,
        target=target,
    )
    proof = certificate(spec, resource_pressure)
    return PrivateEpisode(
        public=PublicEpisode(
            episode_id=secrets.token_hex(16),
            description=DESCRIPTION,
            rooms=rooms_for(spec),
            edges=layout_for(spec).edges,
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
