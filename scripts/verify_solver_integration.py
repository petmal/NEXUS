"""Resumable, cold-process differential check against the archived solver checkout.

Run from the integrated checkout with its frozen environment. The reference must
be the archived PoC with combined/ordinary modes available. Outputs are private
operator evidence, never mounted into a player container.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def fingerprint(root):
    digest = hashlib.sha256()
    for path in sorted((root / "src").rglob("*.py")) + [root / "uv.lock"]:
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def worker(root, case, reference):
    sys.path.insert(0, str(root / "src"))
    import resource
    from contextlib import ExitStack

    from nexus.engine.canonical import canonical_hash
    from nexus.generator import generator, qualify

    policies = []
    original = generator.solve_guaranteed_policy

    def capture(*args, **kwargs):
        result = original(*args, **kwargs)
        if result.solvable:
            policies.append(canonical_hash(result.model_dump(
                mode="json", exclude={"visited_belief_nodes"})))
        return result

    generator.solve_guaranteed_policy = capture
    qualify.solve_guaranteed_policy = capture
    start = time.perf_counter()
    with ExitStack() as stack:
        if reference:
            from nexus.solver.experiments import planning_experiment, solver_experiment
            stack.enter_context(solver_experiment("combined"))
            stack.enter_context(planning_experiment("ordinary"))
        episode = generator.generate_episode(
            case["seed"], discovery_level=case["d"], planning_level=case["p"],
            resource_pressure=case["r"], verifier_secret="integration-fixed-secret",
            max_attempts=250,
        )
    return {"episode_hash": canonical_hash(episode), "policy_hashes": policies,
            "seconds": time.perf_counter() - start,
            "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
            "episode_id": episode.public.episode_id,
            "physical": episode.generation_metadata.optimal_action_count,
            "guaranteed": episode.generation_metadata.guaranteed_policy_action_count,
            "action_budget": episode.generation_metadata.action_budget,
            "recommended_tool_calls": episode.generation_metadata.recommended_tool_call_limit}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("integration-results"))
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--jobs", type=int, choices=(1, 2), default=1,
                        help="Bounded independent case checks; use 1 for timing comparisons")
    parser.add_argument("--worker", choices=["reference", "product"])
    parser.add_argument("--case")
    args = parser.parse_args()
    product = Path(__file__).resolve().parents[1]
    args.reference = args.reference.resolve()
    if args.worker:
        root = args.reference if args.worker == "reference" else product
        print(json.dumps(worker(root, json.loads(args.case), args.worker == "reference")))
        return
    args.output.mkdir(parents=True, exist_ok=True)
    sources = {"product": fingerprint(product), "reference": fingerprint(args.reference),
               "runner": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    cases = [{"seed": 17, "d": d, "p": p, "r": 0} for d in range(6) for p in range(4)]
    cases += [{"seed": s, "d": 5, "p": 3, "r": r}
              for s in (17, 73, 211) for r in (1, 2)]
    def check_case(case):
        label = "s{seed}-d{d}-p{p}-r{r}".format(**case)
        path = args.output / f"{label}.json"
        if path.exists():
            old = json.loads(path.read_text())
            if old.get("sources") == sources and old.get("match") is True:
                print(f"{label}: verified checkpoint", flush=True)
                return
        record = {"case": case, "sources": sources}
        for variant in ("reference", "product"):
            result = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--reference", str(args.reference),
                 "--worker", variant, "--case", json.dumps(case)],
                text=True, capture_output=True, timeout=args.timeout, check=True,
                env={**os.environ, "PYTHONHASHSEED": "0"},
            )
            record[variant] = json.loads(result.stdout)
        record["match"] = all(record["reference"][k] == record["product"][k]
                              for k in ("episode_hash", "policy_hashes"))
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(record, indent=2) + "\n")
        temporary.replace(path)
        print(f"{label}: match={record['match']}", flush=True)
        if not record["match"]:
            raise SystemExit(f"differential mismatch: {path}")

    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        list(executor.map(check_case, cases))
    if sources["product"] != fingerprint(product) or sources["reference"] != fingerprint(args.reference):
        raise SystemExit("Sources changed during validation; rerun before accepting evidence")


if __name__ == "__main__":
    main()
