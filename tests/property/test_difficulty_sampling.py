from __future__ import annotations

import math
from collections import defaultdict
from statistics import median

from nexus.generator import GenerationError, generate_episode
from nexus.generator.difficulty import MAX_PHYSICAL_OPTIMAL_ACTIONS


SEEDS = (1, 17, 73, 211, 509, 1009, 4099, 16381, 65537, 104729)
MAX_ATTEMPTS = 250


def _p95(values: list[int]) -> int:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, math.ceil(len(ordered) * 0.95) - 1)]


def test_difficulty_profiles_are_stable_across_seed_sample(capsys):
    """Stress all public profiles across seeds and surface generation/solver outliers."""
    records: dict[tuple[int, int], list[dict[str, int]]] = defaultdict(list)
    failures: list[str] = []

    for discovery_level in range(6):
        for planning_level in range(3):
            for seed in SEEDS:
                try:
                    episode = generate_episode(
                        seed,
                        discovery_level=discovery_level,
                        planning_level=planning_level,
                        max_attempts=MAX_ATTEMPTS,
                        verifier_secret="sampling-secret",
                    )
                except GenerationError as exc:
                    failures.append(
                        f"d={discovery_level} p={planning_level} seed={seed}: {exc}"
                    )
                    continue

                metadata = episode.generation_metadata
                records[(discovery_level, planning_level)].append(
                    {
                        "seed": seed,
                        "attempts": metadata.generation_attempt + 1,
                        "solver_states": metadata.solver_visited_states,
                        "solver_frontier": metadata.solver_max_frontier_size,
                        "optimal_actions": metadata.optimal_action_count,
                        "action_budget": metadata.action_budget,
                        "guaranteed_actions": (
                            metadata.guaranteed_policy_action_count
                            or metadata.optimal_action_count + metadata.required_probe_count
                        ),
                        "tool_calls": metadata.recommended_tool_call_limit,
                    }
                )

                assert 0 < metadata.optimal_action_count <= MAX_PHYSICAL_OPTIMAL_ACTIONS
                assert metadata.action_budget >= metadata.optimal_action_count
                assert metadata.action_budget >= (
                    metadata.guaranteed_policy_action_count
                    or metadata.optimal_action_count + metadata.required_probe_count
                )
                assert metadata.recommended_tool_call_limit > metadata.action_budget

    lines = [
        "difficulty seed stress: "
        f"{len(SEEDS)} seeds x 18 profiles = {len(SEEDS) * 18} generated worlds",
        (
            "profile  success  attempts med/p95/max  solver-states med/p95/max  "
            "horizon med/p95/max  guaranteed med/p95/max  budget med/p95/max"
        ),
    ]
    all_records: list[dict[str, int]] = []

    for discovery_level in range(6):
        for planning_level in range(3):
            profile_records = records[(discovery_level, planning_level)]
            all_records.extend(profile_records)
            attempts = [record["attempts"] for record in profile_records]
            states = [record["solver_states"] for record in profile_records]
            horizons = [record["optimal_actions"] for record in profile_records]
            guaranteed = [record["guaranteed_actions"] for record in profile_records]
            budgets = [record["action_budget"] for record in profile_records]
            success = f"{len(profile_records)}/{len(SEEDS)}"

            if profile_records:
                lines.append(
                    f"d{discovery_level}/p{planning_level}   {success:>5}    "
                    f"{median(attempts):>4g}/{_p95(attempts):>3}/{max(attempts):>3}          "
                    f"{median(states):>7g}/{_p95(states):>6}/{max(states):>6}             "
                    f"{median(horizons):>4g}/{_p95(horizons):>3}/{max(horizons):>3}          "
                    f"{median(guaranteed):>4g}/{_p95(guaranteed):>3}/{max(guaranteed):>3}          "
                    f"{median(budgets):>4g}/{_p95(budgets):>3}/{max(budgets):>3}"
                )
            else:
                lines.append(f"d{discovery_level}/p{planning_level}   {success:>5}    no successes")

    if all_records:
        by_attempts = sorted(all_records, key=lambda record: record["attempts"], reverse=True)[:5]
        by_states = sorted(
            all_records, key=lambda record: record["solver_states"], reverse=True
        )[:5]
        by_horizon = sorted(
            all_records, key=lambda record: record["optimal_actions"], reverse=True
        )[:5]

        def format_outliers(key: str, rows: list[dict[str, int]]) -> str:
            return ", ".join(f"seed={row['seed']} {key}={row[key]}" for row in rows)

        lines.extend(
            [
                "top generation-attempt outliers: " + format_outliers("attempts", by_attempts),
                "top solver-state outliers: " + format_outliers("solver_states", by_states),
                "top horizon outliers: " + format_outliers("optimal_actions", by_horizon),
            ]
        )

    if failures:
        lines.append("generation failures:")
        lines.extend(f"  {failure}" for failure in failures)

    with capsys.disabled():
        print("\n".join(lines))

    assert not failures, "\n".join(failures)
    assert len(all_records) == len(SEEDS) * 18
