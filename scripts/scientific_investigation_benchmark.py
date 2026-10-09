"""Fresh-process generation timings and information-only shortcut baselines (no model calls)."""

from __future__ import annotations

import argparse
import json
import platform
import random
import subprocess
import sys
from collections import Counter
from pathlib import Path
from time import perf_counter

from nexus.generator import generate_episode
from nexus.generator.investigation import prior
from nexus.models.actions import ACTION_ADAPTER
from nexus.protocol.session import Session


def run_case(d, t, seed, family="shared-response-v1"):
    times = []
    for _ in range(2):
        start = perf_counter()
        episode = generate_episode(
            seed,
            axis_version=2,
            science_family=family,
            discovery_level=d,
            theory_level=t,
            planning_level=1,
            resource_pressure=1,
            verifier_secret="benchmark-only",
        )
        times.append(perf_counter() - start)
    _, problem = prior(episode)
    session = Session(episode)
    for action in episode.reference_plan:
        result = session.act(session.state.turn, ACTION_ADAPTER.validate_python(action))
        if not result.ok:
            raise RuntimeError("benchmark reference action rejected")
    if session.state.terminal_status != "won" or not result.victory_code:
        raise RuntimeError("benchmark reference did not win")
    count = len(problem.hypotheses)
    full = (1 << count) - 1
    partitions = tuple(dict(row) for row in problem.partitions)
    rng = random.Random(1729)
    random_costs = []
    # Uniform complete-world weighting, with an independent random experimental ordering.
    # This is a scientific-information baseline, not a physical navigation policy.
    for truth in range(count):
        order = list(range(len(problem.experiments)))
        rng.shuffle(order)
        belief, used = full, 0
        while not problem._resolved(belief):
            experiment = order.pop()
            value = problem.experiments[experiment][1][truth]
            belief &= partitions[experiment][value]
            used += 1
        random_costs.append(used)
    multiplicities = sorted(Counter(problem.predictions).values(), reverse=True)
    expected_guesses = sum(rank * size for rank, size in enumerate(multiplicities, 1)) / count
    return {
        "family": family,
        "reference_won": True,
        "reference_actions": session.state.turn,
        "D": d,
        "T": t,
        "P": 1,
        "R": 1,
        "seed": seed,
        "cold_generation_seconds": times[0],
        "warm_generation_seconds": times[1],
        "worlds": count,
        "policy_leaf_witnesses": len(problem.policy_leaf_masks),
        "adaptive_measurements": problem.minimum_guaranteed_measurements(),
        "fixed_measurements": problem.minimum_fixed_measurements(),
        "random_unique_experiments_mean": sum(random_costs) / len(random_costs),
        "random_unique_experiments_max": max(random_costs),
        "blind_guess_expected_submissions": expected_guesses,
        "blind_guess_worst_submissions": len(multiplicities),
        "blind_guess_worst_actions": 1 + 2 * len(multiplicities),
        "constructive_policy_action_bound": episode.generation_metadata.guaranteed_policy_action_count,
        "action_budget": episode.public.initial_state.resources.actions_remaining,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=int, nargs=3, metavar=("D", "T", "SEED"))
    parser.add_argument("--out", type=Path)
    parser.add_argument(
        "--family",
        choices=("shared-response-v1", "coupled-network-v1"),
        default="shared-response-v1",
    )
    args = parser.parse_args()
    if args.case:
        print(json.dumps(run_case(*args.case, family=args.family)))
        return
    if args.out is None:
        parser.error("--out is required")
    records = []
    seeds = (7, 17, 23, 41, 73) if args.family == "coupled-network-v1" else (7, 23)
    profiles = (
        ((4, 3), (5, 3))
        if args.family == "coupled-network-v1"
        else ((3, 1), (3, 2), (3, 3), (4, 3), (5, 3))
    )
    for seed in seeds:
        for d, t in profiles:
            start = perf_counter()
            child = subprocess.run(
                [
                    sys.executable,
                    __file__,
                    "--family",
                    args.family,
                    "--case",
                    str(d),
                    str(t),
                    str(seed),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            result = json.loads(child.stdout)
            result["process_wall_seconds_including_two_generations_and_baselines"] = (
                perf_counter() - start
            )
            records.append(result)
    data = {
        "python": platform.python_version(),
        "cases": records,
        "scope": "Exact generated family; no model/API calls; generation timing excludes imports",
        "notes": [
            "One action per configure and finish; blind guessing includes the P1 trip to controller",
            "Scientific measurement bounds exclude controller feedback and physical costs",
            "Hypothesis enumeration in Python is a valid model strategy",
            "R0 eventual guess success is not evidence of scientific inference",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.out.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n")
    temporary.replace(args.out)
    print(
        json.dumps(
            {
                "cases": len(records),
                "max_cold_seconds": max(r["cold_generation_seconds"] for r in records),
            }
        )
    )


if __name__ == "__main__":
    main()
