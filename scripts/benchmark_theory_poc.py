#!/usr/bin/env python3
"""Measure T1 evidence and exact P2 policies without changing supported production profiles."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from benchmark_solver_poc import ROOT, atomic_json, fingerprint
from theory_prior_poc import SPEC, Universe


def replay_policy(episode, candidates, witness):
    from pydantic import TypeAdapter
    from nexus.engine.canonical import canonical_hash
    from nexus.engine.engine import step
    from nexus.models.actions import Action
    from nexus.models.world import TerminalStatus
    from nexus.solver.belief import _episode_for_hypothesis, solve_compressed_physical
    adapter = TypeAdapter(Action)
    replayed = 0
    for rule in candidates:
        world = _episode_for_hypothesis(episode, {"M1": rule}, search_budget=witness.remaining_budget)
        physical = solve_compressed_physical(world)
        if physical.exhausted_state_limit:
            raise RuntimeError("cannot certify hypothesis viability after physical state exhaustion")
        if not physical.solvable:
            continue
        state, node = world.public.initial_state, witness
        while node:
            action = adapter.validate_python(node.action)
            result = step(state, action, world)
            assert result.ok
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
            branch = next(branch for branch in node.branches if branch.outcome == outcome)
            node = branch.next
        assert state.terminal_status == TerminalStatus.WON
        replayed += 1
    return replayed


def run_case(case):
    from nexus.engine.canonical import canonical_hash
    from nexus.generator.discovery import analyze_discovery
    from nexus.generator.evidence import evidence_csv
    from nexus.generator.generator import _find_mechanics_family, generate_episode
    from nexus.solver.belief import solve_guaranteed_policy
    from nexus.solver.experiments import solver_experiment
    from profile_generation import _peak_rss_mb

    started = time.perf_counter()
    universe = Universe()
    family = _find_mechanics_family(case["seed"], "one-machine", 250)
    rule = family.selected_rules["M1"]
    planned = universe.choose_evidence(rule, family.initial_artifact, family.phases["M1"], case["d"])
    report = {key: value for key, value in planned.items() if key not in ("experiments", "indices")}
    report["rows"] = len(planned["experiments"])
    report["evidence_seconds"] = time.perf_counter() - started
    if not planned["accepted"]:
        return {**report, "status": "rejected_evidence", "seconds": time.perf_counter() - started}
    candidates = [universe.materialize(index) for index in planned["indices"]]
    analysis = analyze_discovery(candidate_rules_by_machine={"M1": candidates},
                                 initial_artifact=family.initial_artifact,
                                 target_artifact=family.target_artifact, phase_modulus=4)
    report["viable_hypotheses"] = analysis.viable_hypothesis_count
    report["minimum_guaranteed_probes"] = analysis.minimum_guaranteed_probes
    if analysis.minimum_guaranteed_probes != (1 if case["d"] == 2 else 0):
        return {**report, "status": "rejected_discovery", "seconds": time.perf_counter() - started}
    if case["exact"]:
        with solver_experiment("combined"):
            episode = generate_episode(case["seed"], discovery_level=case["d"], planning_level=2,
                                       resource_pressure=0, verifier_secret="theory-poc")
            payload = episode.model_dump(mode="json")
            paired = canonical_hash({"rules": payload["rules"], "rooms": payload["public"]["rooms"],
                                    "edges": payload["public"]["edges"], "goal": payload["public"]["goal"],
                                    "artifacts": payload["public"]["initial_state"]["artifacts"]})
            episode.public.evidence_files = {
                "facility_manual.txt": SPEC.manual(), "theory.json": SPEC.public_json(),
                "measurements.csv": evidence_csv(rule, planned["experiments"]),
            }
            solve_started = time.perf_counter()
            policy = solve_guaranteed_policy(episode, candidate_rules_by_machine={"M1": candidates},
                                             max_actions=48, include_action_values=False)
            report["policy_seconds"] = time.perf_counter() - solve_started
            report["solvable"] = policy.solvable
            report["guaranteed_actions"] = policy.optimal_worst_case_actions
            report["t0_guaranteed_actions"] = episode.generation_metadata.guaranteed_policy_action_count
            report["paired_world_hash"] = paired
            assert policy.solvable and policy.witness
            report["replayed_hypotheses"] = replay_policy(episode, candidates, policy.witness)
            assert report["replayed_hypotheses"] == policy.viable_hypothesis_count
    report.update(status="ok", seconds=time.perf_counter() - started, peak_rss_mib=_peak_rss_mb())
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help=argparse.SUPPRESS)
    parser.add_argument("--seeds", nargs="+", type=int, default=[17, 18, 19])
    parser.add_argument("--levels", nargs="+", type=int, choices=[0, 1, 2], default=[0, 1, 2])
    parser.add_argument("--exact", action="store_true")
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--out", type=Path, default=ROOT / "docs/profiling/poc-theory")
    args = parser.parse_args()
    if args.case:
        print(json.dumps(run_case(json.loads(args.case))))
        return
    code = hashlib.sha256((fingerprint() + Path(__file__).read_text() +
                           Path(__file__).with_name("theory_prior_poc.py").read_text()).encode()).hexdigest()
    for seed in args.seeds:
        for level in args.levels:
            case = {"seed": seed, "d": level, "exact": args.exact}
            path = args.out / f"s{seed}-d{level}.json"
            if path.exists():
                prior = json.loads(path.read_text())
                if prior.get("code") == code and prior.get("case") == case and prior.get("status") in ("ok", "rejected_evidence", "rejected_discovery"):
                    continue
            try:
                result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--case", json.dumps(case)],
                                        capture_output=True, text=True, timeout=args.timeout, check=True)
                report = json.loads(result.stdout)
            except subprocess.TimeoutExpired:
                report = {"status": "timeout"}
            except subprocess.CalledProcessError as error:
                report = {"status": "error", "stderr": error.stderr[-4000:]}
            report.update(case=case, code=code)
            atomic_json(path, report)
            print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
