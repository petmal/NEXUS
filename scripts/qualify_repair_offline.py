"""Bounded, restartable offline proof job; never part of per-episode generation.

Each output is an atomic checkpoint. Exact jobs contain a separately checked
proof; unknown jobs can be rerun with larger explicit caps. The current recursive
search cell restarts rather than serializing an unsafe Python stack. No paid
services or model calls are used.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def atomic(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-seconds", type=float, default=120)
    parser.add_argument("--memory-mib", type=int, default=512)
    parser.add_argument("--max-states", type=int, default=2_000_000)
    parser.add_argument("--budget", type=int, default=15)
    parser.add_argument(
        "--finite-model",
        type=Path,
        help="Optional compiled FiniteGame JSON instead of the repair relaxation",
    )
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.memory_mib < 64 or args.max_seconds <= 0 or args.max_states < 1:
        parser.error("positive limits and at least64MiB are required")
    if not args.finite_model and args.rounds != 2:
        parser.error("repair query mode supports exactly --rounds 2")
    config = {
        k: str(v) if isinstance(v, Path) else v
        for k, v in vars(args).items()
        if k not in ("output", "worker")
    }
    if not args.worker:
        atomic(
            args.output,
            {
                "status": "running",
                "configuration": config,
                "resume": "rerun this command; incomplete cells restart",
            },
        )
        command = [sys.executable, __file__, *sys.argv[1:], "--worker"]
        try:
            process = subprocess.run(command, timeout=args.max_seconds + 5, check=False)
            if process.returncode:
                atomic(
                    args.output,
                    {
                        "status": "unknown",
                        "configuration": config,
                        "reason": f"worker exit {process.returncode}",
                    },
                )
        except subprocess.TimeoutExpired:
            atomic(
                args.output,
                {"status": "unknown", "configuration": config, "reason": "parent wall-time cap"},
            )
        return
    started = time.monotonic()
    result: dict[str, Any]
    resource = None
    try:
        import resource

        resource.setrlimit(resource.RLIMIT_AS, (args.memory_mib * 1024**2,) * 2)
        from nexus.solver.finite_game import SearchBudget

        def limits():
            return SearchBudget(max_states=args.max_states, max_seconds=args.max_seconds / 2)

        if args.finite_model:
            from dataclasses import asdict

            from pydantic import TypeAdapter

            from nexus.solver.finite_game import FiniteGame, analyze
            from nexus.solver.policy_check import check_proof

            game = TypeAdapter(FiniteGame).validate_json(args.finite_model.read_text(), strict=True)
            analysis = analyze(game, budget=args.budget, rounds=args.rounds, limits=limits())
            if analysis.proof is None:
                result = {"status": "unknown", "reason": analysis.reason}
            else:
                check_proof(game, analysis.proof, limits=limits())
                result = {
                    "status": "exact",
                    "independently_checked": True,
                    "proof": asdict(analysis.proof),
                }
        else:
            from nexus.ontology.repair.proof import check, payload, prove

            proof = prove(budget=args.budget, limits=limits())
            check(proof, limits=limits())
            result = {"status": "exact", "independently_checked": True, "proof": payload(proof)}
    except (MemoryError, RecursionError, TimeoutError) as exc:
        result = {"status": "unknown", "reason": type(exc).__name__}
    except ImportError:
        result = {"status": "unknown", "reason": "OS memory cap unsupported"}
    except Exception as exc:  # noqa: BLE001 -- checkpoint an unknown result, never certify failure
        # Preserve unexpected implementation failure as failure, never qualification.
        result = {"status": "unknown", "reason": f"{type(exc).__name__}: {exc}"}
    result.update(
        configuration=config,
        seconds=time.monotonic() - started,
        process_peak_rss_kib_linux=(
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss if resource else None
        ),
    )
    atomic(args.output, result)
    print(json.dumps({k: v for k, v in result.items() if k != "proof"}))


if __name__ == "__main__":
    main()
