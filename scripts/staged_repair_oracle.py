"""Independent offline proof; atomic output is a resumable validation checkpoint."""

import argparse
from pathlib import Path
from time import perf_counter

from nexus.evaluation.matrix import atomic_json
from nexus.ontology.staged.proof import prove_all


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    atomic_json(args.output, {"status": "running"})
    start = perf_counter()
    try:
        report = prove_all()
        report["seconds"] = perf_counter() - start
        atomic_json(args.output, report)
        print(
            f"staged proof passed: {len(report['profiles'])} conditional profiles, {report['seconds']:.3f}s"
        )
    except Exception as exc:
        atomic_json(args.output, {"status": "blocked", "error": f"{type(exc).__name__}: {exc}"})
        raise


if __name__ == "__main__":
    main()
