#!/usr/bin/env python3
"""Cold, resumable T0/T1 qualification and ordinary-action policy replay sweep."""

from __future__ import annotations

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def replay_policy(episode, candidates) -> int:
    from nexus.engine.canonical import canonical_hash
    from nexus.engine.engine import step
    from nexus.models.actions import ACTION_ADAPTER
    from nexus.models.world import TerminalStatus
    from nexus.solver.belief import (
        PolicyWitnessNode, _episode_for_hypothesis, solve_compressed_physical,
    )

    witness = PolicyWitnessNode.model_validate(episode.generation_metadata.guaranteed_policy_witness)
    replayed = 0
    machines = sorted(candidates)
    for rules in product(*(candidates[machine] for machine in machines)):
        world = _episode_for_hypothesis(
            episode, dict(zip(machines, rules)), search_budget=witness.remaining_budget,
        )
        physical = solve_compressed_physical(world)
        if physical.exhausted_state_limit:
            raise RuntimeError("cannot certify hypothesis viability after physical state exhaustion")
        if not physical.solvable:
            continue
        state, node = world.public.initial_state, witness
        while node:
            action = ACTION_ADAPTER.validate_python(node.action)
            result = step(state, action, world)
            if not result.ok:
                raise RuntimeError("policy action rejected by ordinary engine")
            state = result.state
            if action.type == "move":
                outcome = f"move|{action.target}"
            elif action.type == "probe":
                event = next(event for event in result.events if event.type == "probe")
                outcome = "probe|" + json.dumps(event.details["result"], sort_keys=True, separators=(",", ":"))
            else:
                payload = state.model_dump(mode="json")
                payload.pop("turn")
                payload["resources"].pop("actions_remaining")
                outcome = "state|" + canonical_hash(payload)
            node = next(branch.next for branch in node.branches if branch.outcome == outcome)
        if state.terminal_status != TerminalStatus.WON:
            raise RuntimeError("policy did not end in victory")
        replayed += 1
    return replayed


def run_case(case: dict) -> dict:
    from nexus.engine.canonical import canonical_hash
    from nexus.generator.generator import GenerationError, generate_episode, _candidate_rules_for_episode

    started = time.perf_counter()
    try:
        episode = generate_episode(**case, verifier_secret="theory-profile")
    except GenerationError as exc:
        if "paired T1/" not in str(exc):
            raise
        return {"status": "rejected_evidence", "error": str(exc), "seconds": time.perf_counter() - started}
    generation_seconds = time.perf_counter() - started
    metadata = episode.generation_metadata
    state = episode.public.initial_state.model_dump(mode="json")
    state.pop("resources")
    paired = canonical_hash({
        "rules": {key: value.model_dump(mode="json") for key, value in episode.rules.items()},
        "rooms": {key: value.model_dump(mode="json") for key, value in episode.public.rooms.items()},
        "edges": episode.public.edges, "goal": episode.public.goal.model_dump(mode="json"),
        "state": state,
    })
    replayed = replay_policy(episode, _candidate_rules_for_episode(episode))
    return {
        "status": "ok", "generation_seconds": generation_seconds,
        "seconds": time.perf_counter() - started, "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 if sys.platform != "darwin" else 1024**2),
        "paired_world_hash": paired, "scenario_family_id": metadata.scenario_family_id,
        "candidates": metadata.evidence_candidate_counts, "evidence_rows": metadata.evidence_rows_by_machine,
        "viable_causal_hypotheses": metadata.viable_causal_hypotheses,
        "replayed_physical_hypotheses": replayed,
        "minimum_probes": metadata.required_probe_count,
        "physical_actions": metadata.optimal_action_count,
        "guaranteed_actions": metadata.guaranteed_policy_action_count,
        "budget": metadata.action_budget,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help=argparse.SUPPRESS)
    parser.add_argument("--seeds", type=int, nargs="+", default=[17, 73, 2525])
    parser.add_argument("--levels", type=int, choices=range(4), nargs="+", default=[0, 1, 2, 3])
    parser.add_argument("--theory-levels", type=int, choices=[0, 1], nargs="+", default=[0, 1])
    parser.add_argument("--planning-level", type=int, choices=range(4), default=2)
    parser.add_argument("--resource-pressure", type=int, choices=range(3), default=0)
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--out", type=Path, default=ROOT / "docs/profiling/theory-integration")
    args = parser.parse_args()
    if args.case:
        print(json.dumps(run_case(json.loads(args.case))))
        return 0
    digest = hashlib.sha256()
    for path in sorted((ROOT / "src").rglob("*.py")) + [Path(__file__), ROOT / "uv.lock"]:
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(path.read_bytes())
    digest.update(platform.python_version().encode())
    fingerprint = digest.hexdigest()
    args.out.mkdir(parents=True, exist_ok=True)
    failed = False
    for seed, d, t in product(args.seeds, args.levels, args.theory_levels):
        case = dict(seed=seed, discovery_level=d, planning_level=args.planning_level,
                    resource_pressure=args.resource_pressure, theory_level=t)
        path = args.out / f"s{seed}-d{d}-p{args.planning_level}-r{args.resource_pressure}-t{t}.json"
        if path.exists():
            prior = json.loads(path.read_text())
            if prior.get("case") == case and prior.get("code") == fingerprint and prior.get("status") in {"ok", "rejected_evidence"}:
                print(json.dumps({"case": case, "status": "cached"}), flush=True)
                continue
        try:
            result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--case", json.dumps(case)],
                                    capture_output=True, text=True, timeout=args.timeout, check=True)
            report = json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            report = {"status": "timeout"}
        except subprocess.CalledProcessError as exc:
            report = {"status": "error", "stderr": exc.stderr[-4000:]}
        report.update(case=case, code=fingerprint, python=platform.python_version())
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(report, indent=2) + "\n")
        temp.replace(path)
        failed |= report["status"] in {"error", "timeout"}
        print(json.dumps(report), flush=True)
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
