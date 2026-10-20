"""Run both independent discovery pilot proofs; fail closed on any mismatch."""

import argparse
from pathlib import Path

from nexus.evaluation.matrix import atomic_json
from nexus.ontology.discovery.proof import prove_all


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("/tmp/discovery-proof.json"))
    args = parser.parse_args()
    atomic_json(args.output, {"status": "running"})
    try:
        report = prove_all()
        atomic_json(args.output, report)
    except Exception as exc:
        atomic_json(args.output, {"status": "blocked", "error": f"{type(exc).__name__}: {exc}"})
        raise
    print("discovery proofs passed; both experimental pilots, no deep tier admitted")


if __name__ == "__main__":
    main()
