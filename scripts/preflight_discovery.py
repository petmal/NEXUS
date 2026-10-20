"""Fail-closed preflight of the complete discovery pilots before real-model runs."""

import argparse
from pathlib import Path

from nexus.evaluation.discovery import Pilot, preflight
from nexus.evaluation.matrix import atomic_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("docs/discovery-pocs-matrix.json"))
    parser.add_argument("--output", type=Path, default=Path("/tmp/discovery-preflight.json"))
    args = parser.parse_args()
    atomic_json(args.output, {"status": "running"})
    try:
        pilot = Pilot.model_validate_json(args.matrix.read_text(encoding="utf-8"))
        result = preflight(pilot, args.output)
    except Exception as exc:
        atomic_json(args.output, {"status": "blocked", "error": f"{type(exc).__name__}: {exc}"})
        raise
    print(f"discovery matrix passed: {len(result['cells'])} executions, {result['seconds']:.3f}s")


if __name__ == "__main__":
    main()
