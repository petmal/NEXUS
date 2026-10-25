"""Qualify the model-revision matrix before real-model executions."""

import argparse
from pathlib import Path

from nexus.evaluation.artifacts import atomic_json
from nexus.evaluation.revision import Pilot, preflight


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("docs/model-revision-matrix.json"))
    parser.add_argument("--output", type=Path, default=Path("/tmp/model-revision-preflight.json"))
    args = parser.parse_args()
    try:
        pilot = Pilot.model_validate_json(args.matrix.read_text(encoding="utf-8"))
    except Exception as exc:
        atomic_json(args.output, {"status": "blocked", "error": f"{type(exc).__name__}: {exc}"})
        raise
    report = preflight(pilot, args.output)
    print(
        f"Model-revision preflight passed: {len(report['cells'])} cells in {report['seconds']:.2f}s; empirical difficulty uncalibrated"
    )


if __name__ == "__main__":
    main()
