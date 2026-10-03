from __future__ import annotations

from dataclasses import dataclass

from nexus.engine.rules import apply_effect
from nexus.models.rules import Effect
from nexus.models.world import Artifact


MIN_DISCOVERY_LEVEL = 0
MAX_DISCOVERY_LEVEL = 5
MIN_PLANNING_LEVEL = 0
MAX_PLANNING_LEVEL = 3
MIN_RESOURCE_PRESSURE = 0
MAX_RESOURCE_PRESSURE = 2

GENERATION_SOLVER_BUDGET = 96
MAX_PHYSICAL_OPTIMAL_ACTIONS = 48
EXECUTION_SLACK = 2


@dataclass(frozen=True)
class PlanningProfile:
    min_rooms: int
    max_rooms: int


PLANNING_PROFILES = {
    0: PlanningProfile(min_rooms=4, max_rooms=5),
    1: PlanningProfile(min_rooms=5, max_rooms=7),
    2: PlanningProfile(min_rooms=7, max_rooms=9),
    # P3 deliberately keeps the P2 topology scale. Its extra burden is a mechanically proved
    # delivery dependency, not additional rooms.
    3: PlanningProfile(min_rooms=7, max_rooms=9),
}


def validate_difficulty_levels(
    discovery_level: int,
    planning_level: int,
    resource_pressure: int = 0,
) -> None:
    if not MIN_DISCOVERY_LEVEL <= discovery_level <= MAX_DISCOVERY_LEVEL:
        raise ValueError(
            f"discovery_level must be between {MIN_DISCOVERY_LEVEL} and {MAX_DISCOVERY_LEVEL}"
        )
    if not MIN_PLANNING_LEVEL <= planning_level <= MAX_PLANNING_LEVEL:
        raise ValueError(
            f"planning_level must be between {MIN_PLANNING_LEVEL} and {MAX_PLANNING_LEVEL}"
        )
    if not MIN_RESOURCE_PRESSURE <= resource_pressure <= MAX_RESOURCE_PRESSURE:
        raise ValueError(
            "resource_pressure must be between "
            f"{MIN_RESOURCE_PRESSURE} and {MAX_RESOURCE_PRESSURE}"
        )


def machine_count_for_discovery(discovery_level: int) -> int:
    if discovery_level == 5:
        return 3
    return 2 if discovery_level == 3 else 1


def required_probe_count(discovery_level: int) -> int:
    if discovery_level <= 1:
        return 0
    if discovery_level == 2:
        return 1
    if discovery_level == 3:
        return 2
    if discovery_level in {4, 5}:
        return 1
    raise ValueError(f"unsupported discovery level: {discovery_level}")


def room_bounds(planning_level: int, machine_count: int) -> tuple[int, int]:
    profile = PLANNING_PROFILES[planning_level]
    minimum_for_distinct_roles = machine_count + 3
    return (
        max(profile.min_rooms, minimum_for_distinct_roles),
        max(profile.max_rooms, minimum_for_distinct_roles),
    )


def exploration_allowance(room_count: int) -> int:
    """Conservative allowance for discovering a tree-shaped map and role locations."""
    return 2 * max(0, room_count - 1)


def resource_allowance(room_count: int, resource_pressure: int) -> int:
    """Extra actions beyond the exact guaranteed policy cost.

    R0 preserves the historical forgiving exploration+execution allowance. R1 keeps a smaller
    single-traversal cushion. R2 is exact-budget: a guaranteed optimal policy fits, but no
    additional action is available for avoidable exploration.
    """
    if resource_pressure == 0:
        return exploration_allowance(room_count) + EXECUTION_SLACK
    if resource_pressure == 1:
        return max(1, room_count - 1)
    if resource_pressure == 2:
        return 0
    raise ValueError(f"unsupported resource pressure: {resource_pressure}")


def recommended_tool_call_limit(action_budget: int, evidence_file_count: int) -> int:
    """Operator guidance; deliberately not player-visible."""
    return action_budget + evidence_file_count + 5


def artifact_projection(artifact: Artifact) -> tuple[int, str, str]:
    return artifact.value, artifact.polarity.value, artifact.orientation.value


def chain_requires_both_in_order(
    initial: Artifact,
    first_rule: Effect,
    second_rule: Effect,
    target: Artifact,
    *,
    phase_modulus: int,
) -> bool:
    """Prove the target projection cannot be reached by omitting a stage or reversing the chain.

    Machines have one use each in the generated level-3 family. We therefore enumerate every
    phase at which either single machine or the reverse M2->M1 order could be applied.
    """
    target_projection = artifact_projection(target)
    if artifact_projection(initial) == target_projection:
        return False

    for rule in (first_rule, second_rule):
        for phase in range(phase_modulus):
            if artifact_projection(apply_effect(rule, initial, phase)) == target_projection:
                return False

    for second_phase in range(phase_modulus):
        after_second = apply_effect(second_rule, initial, second_phase)
        for first_phase in range(phase_modulus):
            reversed_result = apply_effect(first_rule, after_second, first_phase)
            if artifact_projection(reversed_result) == target_projection:
                return False

    return True
