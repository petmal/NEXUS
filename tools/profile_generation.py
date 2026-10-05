#!/usr/bin/env python3
from __future__ import annotations

import argparse
import cProfile
from dataclasses import dataclass
from functools import wraps
import json
from pathlib import Path
import pstats
import resource
import sys
from time import perf_counter
from typing import Any, Callable

import nexus.generator.generator as generator_module
import nexus.generator.qualify as qualify_module
from nexus.generator import generate_episode


@dataclass
class Timing:
    calls: int = 0
    wall_seconds: float = 0.0


def _timed(label: str, function: Callable[..., Any], timings: dict[str, Timing]):
    @wraps(function)
    def wrapper(*args, **kwargs):
        started = perf_counter()
        try:
            return function(*args, **kwargs)
        finally:
            timing = timings.setdefault(label, Timing())
            timing.calls += 1
            timing.wall_seconds += perf_counter() - started

    return wrapper


def _install_stage_timers(timings: dict[str, Timing]) -> None:
    # Generation-side exact work.
    generator_module.solve_compressed_physical = _timed(
        "generation.physical_solver",
        generator_module.solve_compressed_physical,
        timings,
    )
    generator_module.solve_guaranteed_policy = _timed(
        "generation.belief_solver",
        generator_module.solve_guaranteed_policy,
        timings,
    )
    generator_module._generate_episode_core = _timed(
        "generation.core",
        generator_module._generate_episode_core,
        timings,
    )
    generator_module._add_planning_dependency = _timed(
        "generation.p3_dependency",
        generator_module._add_planning_dependency,
        timings,
    )

    # Final qualification intentionally uses independent solver entry points. Timing them
    # separately shows whether the remaining cold-start cost is construction or proof.
    qualify_module.solve = _timed(
        "qualification.physical_bfs",
        qualify_module.solve,
        timings,
    )
    qualify_module.solve_guaranteed_policy = _timed(
        "qualification.belief_solver",
        qualify_module.solve_guaranteed_policy,
        timings,
    )
    qualify_module.prove_guaranteed_policy_cost = _timed(
        "qualification.policy_certificate",
        qualify_module.prove_guaranteed_policy_cost,
        timings,
    )
    qualify_module.qualify_episode = _timed(
        "qualification.total",
        qualify_module.qualify_episode,
        timings,
    )


def _max_rss_mb() -> float:
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux reports KiB; macOS reports bytes.
    divisor = 1024 * 1024 if sys.platform == "darwin" else 1024
    return raw / divisor


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Profile one cold NEXUS generation in-process. Start a fresh process for each "
            "measurement so module-level solver caches begin empty."
        )
    )
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--discovery", type=int, default=5)
    parser.add_argument("--planning", type=int, default=3)
    parser.add_argument("--resource", type=int, default=1)
    parser.add_argument("--max-attempts", type=int, default=250)
    parser.add_argument(
        "--cprofile",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Also collect function-level CPU profile data (adds profiling overhead).",
    )
    parser.add_argument(
        "--profile-output",
        type=Path,
        default=Path("generation.prof"),
        help="cProfile output path when --cprofile is enabled.",
    )
    parser.add_argument("--top", type=int, default=40)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    timings: dict[str, Timing] = {}
    _install_stage_timers(timings)

    profiler = cProfile.Profile() if args.cprofile else None
    started = perf_counter()
    if profiler is not None:
        profiler.enable()
    try:
        episode = generate_episode(
            args.seed,
            discovery_level=args.discovery,
            planning_level=args.planning,
            resource_pressure=args.resource,
            max_attempts=args.max_attempts,
            verifier_secret="generation-profile-only",
        )
    finally:
        if profiler is not None:
            profiler.disable()
    total = perf_counter() - started

    metadata = episode.generation_metadata
    summary = {
        "seed": args.seed,
        "profile": f"D{args.discovery}/P{args.planning}/R{args.resource}",
        "wall_seconds": round(total, 6),
        "max_rss_mb": round(_max_rss_mb(), 3),
        "topology_attempt": metadata.topology_attempt,
        "room_count": metadata.room_count,
        "optimal_physical_actions": metadata.optimal_action_count,
        "guaranteed_policy_actions": metadata.guaranteed_policy_action_count,
        "planning_dependency_action_cost": metadata.planning_dependency_action_cost,
        "stage_timings": {
            name: {
                "calls": timing.calls,
                "wall_seconds": round(timing.wall_seconds, 6),
                "average_seconds": round(timing.wall_seconds / timing.calls, 6),
            }
            for name, timing in sorted(
                timings.items(), key=lambda item: item[1].wall_seconds, reverse=True
            )
        },
    }
    print(json.dumps(summary, indent=2, sort_keys=True))

    if profiler is not None:
        profiler.dump_stats(args.profile_output)
        print(
            f"\nTop {args.top} cumulative CPU entries (full profile: {args.profile_output}):",
            file=sys.stderr,
        )
        stats = pstats.Stats(profiler, stream=sys.stderr).sort_stats("cumulative")
        stats.print_stats(args.top)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
