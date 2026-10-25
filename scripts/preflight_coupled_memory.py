"""Fail closed before running the coupled-memory pilot on models."""

import argparse
from pathlib import Path

from nexus.evaluation.artifacts import atomic_json
from nexus.evaluation.coupled_memory import Pilot, preflight
from nexus.ontology.coupled_memory.proof import prove


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("docs/coupled-memory-matrix.json"))
    parser.add_argument("--output", type=Path, default=Path("/tmp/coupled-memory-preflight.json"))
    parser.add_argument("--proof-output", type=Path)
    args = parser.parse_args()
    atomic_json(args.output, {"status": "running"})
    if args.proof_output:
        atomic_json(args.proof_output, {"status": "running"})
    try:
        pilot = Pilot.model_validate_json(args.matrix.read_text(encoding="utf-8"))
        report = preflight(pilot, args.output)
        if args.proof_output:
            atomic_json(
                args.proof_output,
                {"status": "passed", "sources": report["sources"], "proof": prove()},
            )
    except Exception as exc:
        failure = {"status": "blocked", "error": f"{type(exc).__name__}: {exc}"}
        atomic_json(args.output, failure)
        if args.proof_output:
            atomic_json(args.proof_output, failure)
        raise
    print(
        f"coupled-memory preflight passed: {len(report['cells'])} cells, {report['seconds']:.3f}s; experimental only"
    )


if __name__ == "__main__":
    main()
