"""Cold single-episode latency experiments, with process-tree resource sampling."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import platform
import resource
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from benchmark_solver_poc import atomic_json

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = (
    "ordinary",
    "certificate",
    "parallel-certificate",
    "parallel-root",
    "reuse",
    "reuse-certificate",
    "reuse-parallel",
)


def fingerprint():
    digest = hashlib.sha256()
    paths = sorted((ROOT / "src").rglob("*.py")) + [
        Path(__file__),
        ROOT / "scripts/benchmark_solver_poc.py",
        ROOT / "uv.lock",
    ]
    for path in paths:
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def run_case(case):
    import nexus.generator.qualify as qualifier
    from nexus.diagnostics import logger
    from nexus.engine.canonical import canonical_hash
    from nexus.generator import generator
    from nexus.solver.experiments import planning_experiment, solver_experiment

    stages = []

    class CaptureStages(logging.Handler):
        def emit(self, record):
            value = getattr(record, "generation_timing", None)
            if value is not None:
                stages.append(value)

    logger.addHandler(CaptureStages())
    logger.setLevel(logging.INFO)
    logger.propagate = False
    original = generator.solve_guaranteed_policy
    policies = []
    failures = 0

    def capture(*args, **kwargs):
        nonlocal failures
        result = original(*args, **kwargs)
        if result.solvable:
            policies.append(
                canonical_hash(result.model_dump(mode="json", exclude={"visited_belief_nodes"}))
            )
        else:
            failures += 1
        return result

    generator.solve_guaranteed_policy = capture
    qualifier.solve_guaranteed_policy = capture
    started = time.perf_counter()
    with solver_experiment("combined"), planning_experiment(case["variant"]):
        episode = generator.generate_episode(
            case["seed"],
            discovery_level=case["d"],
            planning_level=case["p"],
            resource_pressure=0,
            verifier_secret="solver-poc-fixed-secret",
        )
    seconds = time.perf_counter() - started
    own = resource.getrusage(resource.RUSAGE_SELF)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {
        "generation_seconds": seconds,
        "generation_cpu_seconds": own.ru_utime
        + own.ru_stime
        + children.ru_utime
        + children.ru_stime,
        "parent_peak_rss_mib": own.ru_maxrss / 1024,
        "episode_hash": canonical_hash(episode),
        "policy_hashes": policies,
        "failed_policy_queries": failures,
        "physical_optimum": episode.generation_metadata.optimal_action_count,
        "guaranteed_optimum": episode.generation_metadata.guaranteed_policy_action_count,
        "solver_stages": stages,
        "python": platform.python_version(),
        "platform": platform.platform(),
    }


def proc_group_id(pid):
    # /proc can expose host PIDs while Popen returns a sandbox-namespace PID.
    namespace = os.readlink("/proc/self/ns/pid")
    for path in Path("/proc").glob("[0-9]*/status"):
        try:
            ids = next(
                (
                    line.split()[1:]
                    for line in path.read_text().splitlines()
                    if line.startswith("NSpid:")
                ),
                [],
            )
            if ids and int(ids[-1]) == pid and os.readlink(path.parent / "ns/pid") == namespace:
                fields = (path.parent / "stat").read_text().rsplit(")", 1)[1].split()
                return int(fields[2])
        except FileNotFoundError, ProcessLookupError, PermissionError:
            continue
    return None


def process_group_rss(group):
    """Linux-only sampled sum of resident pages, including spawned descendants."""
    rss = 0
    live = 0
    for path in Path("/proc").glob("[0-9]*/stat"):
        try:
            fields = path.read_text().rsplit(")", 1)[1].split()
            if int(fields[2]) == group and fields[0] != "Z":
                rss += int(fields[21]) * os.sysconf("SC_PAGE_SIZE")
                live += 1
        except FileNotFoundError, ProcessLookupError, PermissionError:
            continue
    return rss / (1024 * 1024), live


def dispatch(case, timeout):
    started = time.perf_counter()
    usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
    peak = 0
    peak_processes = 0
    timed_out = False
    with tempfile.TemporaryFile(mode="w+") as stdout, tempfile.TemporaryFile(mode="w+") as stderr:
        process = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--case", json.dumps(case)],
            stdout=stdout,
            stderr=stderr,
            text=True,
            start_new_session=True,
        )
        group = None
        try:
            while process.poll() is None:
                if group is None:
                    group = proc_group_id(process.pid)
                rss, live = process_group_rss(group) if group is not None else (0, 0)
                peak = max(peak, rss)
                peak_processes = max(peak_processes, live)
                if time.perf_counter() - started > timeout:
                    timed_out = True
                    break
                time.sleep(0.05)
        finally:
            # A group kill also reaps workers on timeout/interruption, unlike killing
            # only the generator. This supervisor never shares the child's group.
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if group is not None:
            cleanup_deadline = time.perf_counter() + 2
            while process_group_rss(group)[1] and time.perf_counter() < cleanup_deadline:
                time.sleep(0.01)
            if process_group_rss(group)[1]:
                raise RuntimeError("benchmark child process group did not terminate")
        usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
        stdout.seek(0)
        stderr.seek(0)
        result = {
            "case": case,
            "wall_seconds": time.perf_counter() - started,
            "sampled_tree_peak_rss_mib": peak,
            "peak_process_count": peak_processes,
            "rss_sampling_seconds": 0.05,
            "cpu_seconds": (
                usage_end.ru_utime
                + usage_end.ru_stime
                - usage_start.ru_utime
                - usage_start.ru_stime
            )
            if not timed_out
            else None,
            "process_group_cleaned": True,
        }
        if timed_out:
            return {**result, "status": "timeout"}
        if process.returncode:
            return {**result, "status": "error", "stderr": stderr.read()[-4000:]}
        if peak <= 0:
            raise RuntimeError("process-tree RSS measurement unavailable")
        return {**result, "status": "ok", **json.load(stdout)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help=argparse.SUPPRESS)
    parser.add_argument("--seeds", nargs="+", type=int, default=[17, 18, 19])
    parser.add_argument("--variants", nargs="+", choices=VARIANTS, default=list(VARIANTS))
    parser.add_argument("--discovery", type=int, choices=range(6), default=5)
    parser.add_argument("--planning", type=int, choices=range(4), default=3)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--out", type=Path, default=ROOT / "docs/profiling/poc-single-episode")
    args = parser.parse_args()
    if args.case:
        print(json.dumps(run_case(json.loads(args.case))))
        return
    if sys.platform != "linux":
        parser.error("resource supervisor currently requires Linux /proc")
    if args.timeout <= 0 or args.repeat < 1:
        parser.error("timeout and repeat must be positive")
    code = fingerprint()
    expected = {}
    for seed in args.seeds:
        for repeat in range(args.repeat):
            variants = list(args.variants)
            if repeat % 2:
                variants.reverse()
            for variant in variants:
                case = {
                    "seed": seed,
                    "d": args.discovery,
                    "p": args.planning,
                    "variant": variant,
                    "repeat": repeat,
                }
                path = (
                    args.out
                    / f"d{args.discovery}-p{args.planning}-s{seed}-{variant}-r{repeat}.json"
                )
                prior = json.loads(path.read_text()) if path.exists() else {}
                if (
                    prior.get("status") == "ok"
                    and prior.get("code") == code
                    and prior.get("case") == case
                ):
                    result = prior
                    print(json.dumps({"case": case, "status": "skipped"}), flush=True)
                else:
                    result = {**dispatch(case, args.timeout), "code": code}
                    atomic_json(path, result)
                    print(
                        json.dumps(
                            {
                                key: result.get(key)
                                for key in (
                                    "case",
                                    "status",
                                    "wall_seconds",
                                    "generation_seconds",
                                    "cpu_seconds",
                                    "sampled_tree_peak_rss_mib",
                                )
                            }
                        ),
                        flush=True,
                    )
                if result["status"] == "ok":
                    semantic = (result["episode_hash"], result["policy_hashes"])
                    if seed in expected and expected[seed] != semantic:
                        raise AssertionError(f"semantic mismatch for seed {seed}")
                    expected[seed] = semantic


if __name__ == "__main__":
    main()
