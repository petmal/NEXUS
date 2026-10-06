#!/usr/bin/env python3
"""Profile one cold NEXUS generation without changing generator semantics.

This developer PoC wraps the existing generation/qualification call sites to attribute wall time
and solver work. Optional cProfile output can then drill into a confirmed hot stage. Run it in a
fresh process to match serve-session cold-start behavior, for example:

    uv run python scripts/profile_generation.py --seed 17 --discovery-level 5 --planning-level 3

The JSON report contains no hidden rules or verifier secret. It is intended for trusted benchmark
engineering, not for the player-facing protocol.
"""

from __future__ import annotations

import argparse
import cProfile
import inspect
import io
import json
import logging
import platform
import sys
import pstats
import time
from collections import Counter
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import Any, Callable

try:
    import resource
except ImportError:  # pragma: no cover - resource is unavailable on Windows.
    resource = None  # type: ignore[assignment]

from nexus.diagnostics import logger
from nexus.engine.canonical import canonical_hash
import nexus.generator.generator as generator_module
import nexus.generator.qualify as qualify_module


@dataclass
class Event:
    stage: str
    call: int
    seconds: float
    result: dict[str, object] = field(default_factory=dict)


EVENTS: list[Event] = []
CALL_COUNTS: Counter[str] = Counter()
SOLVER_STAGES: list[dict[str, object]] = []


class TimingHandler(logging.StreamHandler):
    def emit(self, record: logging.LogRecord) -> None:
        timing = getattr(record, "generation_timing", None)
        if timing is not None:
            SOLVER_STAGES.append(timing)
        super().emit(record)


def _result_metrics(result: object) -> dict[str, object]:
    metrics: dict[str, object] = {}
    for name in (
        "solvable",
        "optimal_worst_case_actions",
        "optimal_action_count",
        "visited_belief_nodes",
        "visited_states",
        "max_frontier_size",
        "exhausted_action_limit",
        "exhausted_state_limit",
        "passed",
    ):
        value = getattr(result, name, None)
        if value is not None:
            metrics[name] = value
    return metrics


def _caller_name() -> str:
    frame = inspect.currentframe()
    if frame is None or frame.f_back is None or frame.f_back.f_back is None:
        return "unknown"
    return frame.f_back.f_back.f_code.co_name


def _timed(module_name: str, name: str, original: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(original)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        caller = _caller_name()
        stage = f"{module_name}.{caller}->{name}"
        CALL_COUNTS[stage] += 1
        call = CALL_COUNTS[stage]
        logger.info("stage=%s call=%d event=start", stage, call)
        started = time.perf_counter()
        try:
            result = original(*args, **kwargs)
        except BaseException:
            EVENTS.append(
                Event(stage=stage, call=call, seconds=time.perf_counter() - started)
            )
            raise
        EVENTS.append(
            Event(
                stage=stage,
                call=call,
                seconds=time.perf_counter() - started,
                result=_result_metrics(result),
            )
        )
        logger.info("stage=%s call=%d event=complete seconds=%.6f",
                    stage, call, EVENTS[-1].seconds)
        return result

    return wrapper


def _patch(module: object, module_name: str, names: tuple[str, ...]) -> None:
    for name in names:
        original = getattr(module, name)
        setattr(module, name, _timed(module_name, name, original))


def install_timing_wrappers() -> None:
    # Generator wrappers distinguish core D5 proof work from each P3 cargo candidate.
    _patch(
        generator_module,
        "generator",
        (
            "_generate_episode_core",
            "_generate_constructed_episode",
            "_add_planning_dependency",
            "_apply_resource_pressure",
            "solve_compressed_physical",
            "solve_guaranteed_policy",
        ),
    )
    # Qualification imports its own solver aliases, so wrap those separately. The caller name and
    # call index distinguish the D5 proof, P2 counterfactual proof, and final concrete BFS passes.
    _patch(
        qualify_module,
        "qualify",
        (
            "qualify_episode",
            "solve_guaranteed_policy",
            "prove_guaranteed_policy_cost",
            "solve",
            "execute_with_trace",
            "replay",
        ),
    )


def _peak_rss_mb() -> float | None:
    if resource is None:
        return None
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux reports KiB; macOS reports bytes.
    if sys.platform == "darwin":
        return value / (1024 * 1024)
    return value / 1024


def _aggregate_events() -> list[dict[str, object]]:
    totals: dict[str, dict[str, object]] = {}
    for event in EVENTS:
        item = totals.setdefault(
            event.stage,
            {"stage": event.stage, "calls": 0, "seconds": 0.0},
        )
        item["calls"] = int(item["calls"]) + 1
        item["seconds"] = float(item["seconds"]) + event.seconds
    return sorted(totals.values(), key=lambda item: float(item["seconds"]), reverse=True)


def _profile_text(profiler: cProfile.Profile, top: int) -> str:
    output = io.StringIO()
    stats = pstats.Stats(profiler, stream=output).strip_dirs().sort_stats("cumulative")
    stats.print_stats(top)
    return output.getvalue()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--discovery-level", type=int, default=5, choices=range(6))
    parser.add_argument("--planning-level", type=int, default=3, choices=range(4))
    parser.add_argument("--resource-pressure", type=int, default=0, choices=range(3))
    parser.add_argument("--max-attempts", type=int, default=250)
    parser.add_argument(
        "--cprofile",
        action="store_true",
        help="Enable function-level cProfile. Leave off for low-overhead stage timing.",
    )
    parser.add_argument("--top", type=int, default=40, help="cProfile rows to include")
    parser.add_argument("--profile-out", type=Path, help="Optional raw .prof output")
    parser.add_argument("--json-out", type=Path, help="Optional JSON report output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.profile_out is not None and not args.cprofile:
        raise SystemExit("--profile-out requires --cprofile")
    handler = TimingHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    install_timing_wrappers()

    profiler = cProfile.Profile()
    started = time.perf_counter()
    if args.cprofile:
        profiler.enable()
    episode = generator_module.generate_episode(
        args.seed,
        discovery_level=args.discovery_level,
        planning_level=args.planning_level,
        resource_pressure=args.resource_pressure,
        max_attempts=args.max_attempts,
        verifier_secret="generation-profile",
    )
    if args.cprofile:
        profiler.disable()
    elapsed = time.perf_counter() - started

    if args.profile_out is not None:
        args.profile_out.parent.mkdir(parents=True, exist_ok=True)
        profiler.dump_stats(args.profile_out)

    metadata = episode.generation_metadata
    report = {
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "episode_sha256": canonical_hash(episode),
        "timing_note": "Stages are inclusive and nested; do not sum their durations.",
        "solver_stages": SOLVER_STAGES,
        "profile": {
            "seed": args.seed,
            "discovery_level": args.discovery_level,
            "planning_level": args.planning_level,
            "resource_pressure": args.resource_pressure,
            "episode_id": episode.public.episode_id,
        },
        "generation": {
            "seconds": elapsed,
            "peak_rss_mb": _peak_rss_mb(),
            "topology_attempt": metadata.topology_attempt,
            "optimal_physical_actions": metadata.optimal_action_count,
            "guaranteed_policy_actions": metadata.guaranteed_policy_action_count,
            "planning_dependency_action_cost": metadata.planning_dependency_action_cost,
            "action_budget": metadata.action_budget,
        },
        "stage_totals": _aggregate_events(),
        "events": [
            {
                "stage": event.stage,
                "call": event.call,
                "seconds": event.seconds,
                **event.result,
            }
            for event in EVENTS
        ],
        "cprofile_top_cumulative": (
            _profile_text(profiler, args.top) if args.cprofile else None
        ),
    }

    text = json.dumps(report, indent=2, sort_keys=True)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
