"""Bounded deterministic kernel/target admission; no model-conditioned selection."""

import secrets
from dataclasses import dataclass
from functools import lru_cache
from random import Random

from nexus.models.domain import DomainArtifact, DomainInvestigation, DomainTruth
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import Machine, Resources, Room, WorldState
from nexus.ontology.interference.laws import decode, encode
from nexus.ontology.interference.planner import (
    bank_contiguous_distances,
    distances,
    goal_preserving_cost,
    minimum_goal_breaks,
    optimal,
)
from nexus.ontology.interference.schema import (
    COUNT,
    FAMILY,
    SIZE,
    GenerationOptions,
    Investigation,
    Specimen,
    Structure,
    Truth,
    topology,
)

DESCRIPTION = "Coordinate the original seal using disclosed prerequisites and simultaneous side effects; hold every target and finish in array."
MAX_KERNEL_ATTEMPTS = 32
DEFAULT_OPTIONS = GenerationOptions()


@dataclass(frozen=True)
class Selection:
    world: Truth
    short: tuple[int, ...]
    long: tuple[int, ...]
    attempt: int


def specification(world, target, coupling):
    return Investigation(
        options=Structure(coupling=coupling),
        topology=topology(coupling),
        resolved=world,
        target=target,
    )


@lru_cache(maxsize=8, typed=True)
def selection(seed: int) -> Selection:
    if type(seed) is not int:
        raise ValueError("construction seed must be an integer")
    rng = Random(f"nexus-interference-v1:{seed}")
    for attempt in range(1, MAX_KERNEL_ATTEMPTS + 1):
        guards = [rng.randrange(5) for _ in range(COUNT)]
        for bank in range(2):
            guards[bank * 3 + rng.randrange(3)] = 0
        world = Truth(
            guards=tuple(guards),
            gains=tuple(rng.randrange(1, 5) for _ in range(COUNT)),
            spill_gains=tuple(rng.randrange(1, 5) for _ in range(COUNT)),
        )
        independent, coupled = (distances(world, c) for c in ("independent", "coupled"))
        baseline = bank_contiguous_distances(world, "coupled")
        targets = [
            s
            for s in range(SIZE)
            if all(decode(s))
            and independent[s] >= 0
            and coupled[s] >= 0
            and (baseline[s] is None or coupled[s] < baseline[s])
        ]
        rng.shuffle(targets)
        longer = next(
            (
                s
                for s in sorted(targets, key=lambda s: coupled[s], reverse=True)
                if 30 <= coupled[s] <= 48
                and independent[s] >= 14
                and goal_preserving_cost(specification(world, decode(s), "coupled")) is None
            ),
            None,
        )
        if longer is None:
            continue
        shorter = next(
            (
                s
                for s in targets
                if 12 <= coupled[s] <= 20
                and independent[s] <= independent[longer] - 4
                and goal_preserving_cost(specification(world, decode(s), "coupled")) is None
            ),
            None,
        )
        if shorter is not None:
            return Selection(world, decode(shorter), decode(longer), attempt)
    raise ValueError(
        f"seed {seed} has no admitted paired short/long interference targets within {MAX_KERNEL_ATTEMPTS} kernels; no substitute seed used"
    )


def certificate(spec, resource, admitted):
    reference = optimal(spec).actions
    slack = max(6, (reference + 1) // 2) if resource == 1 else 0
    baseline = bank_contiguous_distances(spec.resolved, spec.options.coupling)[encode(spec.target)]
    return {
        "family": FAMILY,
        "status": "experimental-public-reference-qualified",
        "empirical_difficulty_calibrated": False,
        "map_visibility": "complete",
        "law_visibility": "complete",
        "state_visibility": "complete",
        "horizon_stratum": "short" if spec.target == admitted.short else "long",
        "kernel_attempt": admitted.attempt,
        "kernel_attempt_limit": MAX_KERNEL_ATTEMPTS,
        "physical_state_bound": SIZE,
        "reachable_states": sum(v >= 0 for v in distances(spec.resolved, spec.options.coupling)),
        "reference_kind": "exact-known-law-optimum",
        "minimum_operations": reference - 2,
        "reference_action_upper": reference,
        "action_budget": reference + slack if resource else None,
        "resource_allowance": slack,
        "bank_contiguous_operations": baseline,
        "bank_contiguous_reachable": baseline is not None,
        "minimum_coordinate_goal_breaks": minimum_goal_breaks(spec),
        "scope": "Exact P0 known-law minimum including take and finish. R2 equals minimum; R1 adds max(6,ceil(minimum/2)); R0 uncapped. Goal breaks count operations unsetting at least one matched coordinate, minimized over all successful words. Null restricted cost means unreachable under bank-contiguous words. Coupled optimum beats every bank-contiguous word; slack may permit such a word. Sizes and horizon strata are not empirical difficulty calibration.",
    }


def initial_state(spec, budget):
    return WorldState(
        agent_room="array",
        artifacts={
            "seal": DomainArtifact(
                ontology=FAMILY,
                id="seal",
                location="array",
                payload=Specimen(registers=(0,) * COUNT).model_dump(mode="json"),
            )
        },
        machines={
            c.machine: Machine(id=c.machine, room_id="array", uses_remaining=None)
            for c in spec.topology
        },
        resources=Resources(actions_remaining=budget),
    )


def rooms_for(spec):
    return {"array": Room(id="array", label="Exit array")}


def metadata(spec, resource, proof):
    return GenerationMetadata(
        theory_level=0,
        discovery_level=0,
        planning_level=0,
        resource_pressure=resource,
        scenario_family_id=FAMILY,
        generation_attempt=proof["kernel_attempt"],
        scenario_family_attempt=proof["kernel_attempt"],
        room_count=1,
        machine_count=COUNT,
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
    from nexus.ontology.interference.evidence import files

    if (
        any(
            type(v) is not int
            for v in (seed, theory_level, discovery_level, planning_level, resource_pressure)
        )
        or (theory_level, discovery_level, planning_level) != (0, 0, 0)
        or resource_pressure not in (0, 1, 2)
        or budget_profile != "standard"
    ):
        raise ValueError("interference requires integer axes T0/D0/P0, R0..R2 and standard budget")
    options = GenerationOptions.model_validate(options)
    if verifier_secret == "":
        raise ValueError("verifier secret must not be empty")
    admitted = selection(seed)
    target = admitted.short if options.horizon == "short" else admitted.long
    spec = specification(admitted.world, target, options.coupling)
    proof = certificate(spec, resource_pressure, admitted)
    return PrivateEpisode(
        public=PublicEpisode(
            episode_id=secrets.token_hex(16),
            description=DESCRIPTION,
            rooms=rooms_for(spec),
            edges=(),
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
        investigation_truth=DomainTruth(
            ontology=FAMILY, payload=admitted.world.model_dump(mode="json")
        ),
        generation_metadata=metadata(spec, resource_pressure, proof),
    )
