#!/usr/bin/env python3
"""Cold-process, resumable physical-search and single-episode multiprocessing PoC.

Production remains sequential. --workers only replaces the ordered independent
physical-screen batch, using a spawn ProcessPoolExecutor shared within one episode.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import hashlib
import json
import logging
import multiprocessing
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def physical_job(payload):
    from nexus.models.episode import PrivateEpisode
    from nexus.solver.belief import solve_compressed_physical
    episode, limit = payload
    result = solve_compressed_physical(PrivateEpisode.model_validate_json(episode),
                                       max_states=limit, include_plan=False)
    return result.model_dump(mode="json")


def run_case(case, workers):
    from nexus.generator.generator import generate_episode, _candidate_rules_for_episode
    from nexus.engine.canonical import canonical_hash
    from nexus.models.episode import GenerationMetadata
    import nexus.solver.belief as belief
    from profile_theory import replay_policy

    timings = []
    class Capture(logging.Handler):
        def emit(self, record):
            if hasattr(record, "generation_timing"):
                timings.append(record.generation_timing)
    logger = logging.getLogger("nexus.generation")
    logger.setLevel(logging.INFO)
    logger.addHandler(Capture())
    executor = None
    if workers:
        executor = ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn"))
        def batch(episodes, *, max_states):
            # Send only the physical problem. No evidence, reference witness or
            # generator metadata is read by the cost-only search.
            payloads = []
            for episode in episodes:
                world = episode.model_copy()
                world.public = episode.public.model_copy(update={"evidence_files": {}})
                world.generation_metadata = GenerationMetadata()
                world.reference_plan = ()
                payloads.append((world.model_dump_json(), max_states))
            return (belief.CompressedPhysicalResult.model_validate(result)
                    for result in executor.map(physical_job, payloads, chunksize=4, buffersize=workers * 2))
        belief._physical_results = batch
    started = time.perf_counter()
    try:
        episode = generate_episode(**case, verifier_secret="physical-profile")
        generation_seconds = time.perf_counter() - started
    finally:
        if executor is not None:
            executor.shutdown()
    shutdown_inclusive_seconds = time.perf_counter() - started
    m = episode.generation_metadata
    state = episode.public.initial_state.model_dump(mode="json")
    state.pop("resources")
    signature = canonical_hash({"rules": {k: v.model_dump(mode="json") for k, v in episode.rules.items()},
                                "state": state, "goal": episode.public.goal.model_dump(mode="json"),
                                "edges": episode.public.edges,
                                "rooms": {k: v.model_dump(mode="json") for k, v in episode.public.rooms.items()},
                                "phase_modulus": episode.public.phase_modulus,
                                "machine_rules": episode.machine_rules})
    replayed = replay_policy(episode, _candidate_rules_for_episode(episode))
    return dict(status="ok", generation_seconds=generation_seconds,
                shutdown_inclusive_seconds=shutdown_inclusive_seconds, timings=timings,
                physical_hash=signature, physical_actions=m.optimal_action_count,
                guaranteed_actions=m.guaranteed_policy_action_count, budget=m.action_budget,
                candidates=m.evidence_candidate_counts, replayed=replayed,
                parent_peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
                max_child_rss_mib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--case", help=argparse.SUPPRESS)
    parser.add_argument("--seeds", nargs="+", type=int, default=[1, 17])
    parser.add_argument("--discovery-level", type=int, default=3)
    parser.add_argument("--planning-level", type=int, default=2)
    parser.add_argument("--theory-level", type=int, default=1)
    parser.add_argument("--resource-pressure", type=int, default=1)
    parser.add_argument("--workers", type=int, choices=[0, 2, 4], default=0)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--concurrent-episodes", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--out", type=Path, default=ROOT / "docs/profiling/physical-pass-final")
    args = parser.parse_args()
    if args.case:
        print(json.dumps(run_case(json.loads(args.case), args.workers)))
        return 0
    digest = hashlib.sha256()
    for path in sorted((args.source_root / "src").rglob("*.py")):
        digest.update(str(path.relative_to(args.source_root)).encode())
        digest.update(path.read_bytes())
    for path in (Path(__file__), ROOT / "scripts/profile_theory.py", args.source_root / "uv.lock"):
        digest.update(path.read_bytes())
    digest.update(platform.python_version().encode())
    fingerprint = digest.hexdigest()
    args.out.mkdir(parents=True, exist_ok=True)
    host = {"cpu_count": os.cpu_count(), "affinity": len(os.sched_getaffinity(0)),
            "cpu_max": Path("/sys/fs/cgroup/cpu.max").read_text().strip()}
    env = dict(os.environ, PYTHONPATH=str(args.source_root.resolve() / "src"))
    def execute(item):
        seed, repeat = item
        case = dict(seed=seed, discovery_level=args.discovery_level, planning_level=args.planning_level,
                    theory_level=args.theory_level, resource_pressure=args.resource_pressure)
        path = args.out / f"s{seed}-d{args.discovery_level}-p{args.planning_level}-t{args.theory_level}-r{args.resource_pressure}-w{args.workers}-c{args.concurrent_episodes}-n{repeat}.json"
        if path.exists():
            prior = json.loads(path.read_text())
            if prior.get("code") == fingerprint and prior.get("status") == "ok":
                return prior
        started = time.perf_counter()
        command = [sys.executable, str(Path(__file__).resolve()), "--case", json.dumps(case),
                   "--workers", str(args.workers)]
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, env=env, start_new_session=True) as process:
            try:
                stdout, stderr = process.communicate(timeout=args.timeout)
                report = (json.loads(stdout) if process.returncode == 0
                          else {"status": "error", "stderr": stderr[-4000:]})
            except subprocess.TimeoutExpired:
                # Kill the entire session, including spawned physical workers.
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate()
                report = {"status": "timeout"}
        report.update(case=case, workers=args.workers, concurrent_episodes=args.concurrent_episodes,
                      repeat=repeat, code=fingerprint, python=platform.python_version(), host=host,
                      subprocess_seconds=time.perf_counter() - started)
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(report, indent=2) + "\n")
        temp.replace(path)
        return report
    with ThreadPoolExecutor(max_workers=args.concurrent_episodes) as pool:
        for result in pool.map(execute, [(s, r) for r in range(args.repeats) for s in args.seeds]):
            print(json.dumps({k: v for k, v in result.items() if k != "timings"}), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
