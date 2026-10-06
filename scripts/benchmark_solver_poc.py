#!/usr/bin/env python3
"""Cold solver ablations with atomic, fingerprinted, resumable case results."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def fingerprint():
    digest = hashlib.sha256()
    for path in sorted((ROOT / "src").rglob("*.py")) + [Path(__file__), ROOT / "uv.lock"]:
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def run_case(case):
    from nexus.engine.canonical import canonical_hash
    import nexus.generator.generator as generator
    import nexus.generator.qualify as qualifier
    from nexus.solver.experiments import solver_experiment
    import profile_generation as profile

    policies = []
    original = generator.solve_guaranteed_policy

    def capture(*args, **kwargs):
        result = original(*args, **kwargs)
        payload = result.model_dump(mode="json", exclude={"visited_belief_nodes"})
        policies.append(canonical_hash(payload))
        return result

    generator.solve_guaranteed_policy = capture
    qualifier.solve_guaranteed_policy = capture
    started = time.perf_counter()
    with solver_experiment(case["mode"]):
        episode = generator.generate_episode(
            case["seed"], discovery_level=case["d"], planning_level=case["p"],
            resource_pressure=0, verifier_secret="solver-poc-fixed-secret",
        )
    metadata = episode.generation_metadata
    return {
        "seconds": time.perf_counter() - started,
        "peak_rss_mib": profile._peak_rss_mb(),
        "episode_hash": canonical_hash(episode),
        "policy_hashes": policies,
        "physical_optimum": metadata.optimal_action_count,
        "guaranteed_optimum": metadata.guaranteed_policy_action_count,
        "python": platform.python_version(), "platform": platform.platform(),
    }


def dispatch(job):
    case, timeout = job
    started = time.perf_counter()
    try:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--case", json.dumps(case)],
            capture_output=True, text=True, timeout=timeout, check=True,
        )
        return {"case": case, "status": "ok", **json.loads(result.stdout)}
    except subprocess.TimeoutExpired:
        return {"case": case, "status": "timeout", "seconds": time.perf_counter() - started}
    except subprocess.CalledProcessError as error:
        return {"case": case, "status": "error", "stderr": error.stderr[-4000:]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help=argparse.SUPPRESS)
    parser.add_argument("--seeds", nargs="+", type=int, default=[17, 18, 19])
    parser.add_argument("--modes", nargs="+", choices=["baseline", "intern", "bounds", "combined"],
                        default=["baseline", "intern", "bounds", "combined"])
    parser.add_argument("--planning", nargs="+", type=int, choices=range(4), default=[2, 3])
    parser.add_argument("--discovery", type=int, choices=range(6), default=5)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--out", type=Path, default=ROOT / "docs/profiling/poc-solver")
    args = parser.parse_args()
    if args.case:
        print(json.dumps(run_case(json.loads(args.case))))
        return
    if args.workers < 1 or args.timeout <= 0:
        parser.error("workers and timeout must be positive")
    code = fingerprint()
    cases = [{"seed": seed, "d": args.discovery, "p": p, "mode": mode}
             for seed in args.seeds for p in args.planning for mode in args.modes]
    pending = []
    def path_for(case):
        return args.out / f"d{case['d']}-p{case['p']}-s{case['seed']}-{case['mode']}.json"
    for case in cases:
        path = path_for(case)
        if path.exists():
            prior = json.loads(path.read_text())
            if prior.get("code") == code and prior.get("case") == case and prior.get("status") == "ok":
                continue
        pending.append((case, args.timeout))
    started = time.perf_counter()
    executor = None
    if args.workers == 1:
        results = map(dispatch, pending)
    else:
        executor = ProcessPoolExecutor(max_workers=args.workers,
                                       mp_context=multiprocessing.get_context("spawn"))
        results = executor.map(dispatch, pending)
    try:
        for result in results:
            result["code"] = code
            result["workers"] = args.workers
            atomic_json(path_for(result["case"]), result)
            print(json.dumps({k: result.get(k) for k in ("case", "status", "seconds", "peak_rss_mib")}), flush=True)
    finally:
        if executor:
            executor.shutdown(cancel_futures=True)
    atomic_json(args.out / "batch.json", {
        "code": code, "workers": args.workers, "completed_this_invocation": len(pending),
        "skipped": len(cases) - len(pending), "seconds": time.perf_counter() - started,
        "cpu_count": os.cpu_count(), "process_cpu_count": os.process_cpu_count(),
    })
    # Reject semantic disagreement rather than interpreting it as a performance gain.
    groups = {}
    for case in cases:
        report = json.loads(path_for(case).read_text())
        if report["status"] != "ok":
            continue
        key = (case["seed"], case["d"], case["p"])
        semantic = (report["episode_hash"], report["policy_hashes"])
        if key in groups and groups[key] != semantic:
            raise AssertionError(f"solver semantic mismatch: {key}")
        groups[key] = semantic


if __name__ == "__main__":
    main()
