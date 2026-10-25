"""Recompute independent whole-mission arithmetic and shortcut proofs."""

import argparse
from pathlib import Path

from nexus.evaluation.artifacts import atomic_json
from nexus.ontology.assembly.proof import prove_all


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("/tmp/joint-assembly-proof.json"))
    args = parser.parse_args()
    atomic_json(args.output, {"status": "running"})
    try:
        report = prove_all()
        atomic_json(args.output, report)
    except Exception as exc:
        atomic_json(args.output, {"status": "blocked", "error": f"{type(exc).__name__}: {exc}"})
        raise
    print(
        f"joint assembly proof passed: {report['worlds']} worlds, {report['mission_signatures']} mission signatures"
    )


if __name__ == "__main__":
    main()
