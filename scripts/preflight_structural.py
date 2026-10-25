"""Validate experimental structural pilot before any model calls; fail closed."""

import argparse
from pathlib import Path

from nexus.evaluation.artifacts import atomic_json
from nexus.evaluation.structural import Pilot, preflight


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("docs/structural-model-matrix.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    atomic_json(args.output, {"version": "structural-preflight-v1", "status": "running"})
    try:
        pilot = Pilot.model_validate_json(args.matrix.read_text())
        result = preflight(pilot, args.output)
    except Exception as exc:
        atomic_json(
            args.output,
            {"version": "structural-preflight-v1", "status": "blocked", "error": str(exc)},
        )
        raise
    print(result["status"], "empirical difficulty uncalibrated; no broad rollout")


if __name__ == "__main__":
    main()
