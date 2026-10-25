"""Qualify the matched planning/resource pilot without model calls."""

import argparse
from pathlib import Path

from nexus.evaluation.artifacts import atomic_json
from nexus.evaluation.planning import Pilot, export_tasks, preflight


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("docs/planning-resource-matrix.json"))
    parser.add_argument(
        "--output", type=Path, default=Path("/tmp/planning-resource-preflight.json")
    )
    parser.add_argument("--tasks-output", type=Path, help="Export tasks after successful preflight")
    args = parser.parse_args()
    try:
        pilot = Pilot.model_validate_json(args.matrix.read_text())
    except Exception as exc:
        atomic_json(args.output, {"status": "blocked", "error": f"{type(exc).__name__}: {exc}"})
        raise
    report = preflight(pilot, args.output)
    if args.tasks_output:
        export_tasks(pilot, report, args.tasks_output)
    print(f"P/R preflight passed: {len(report['cells'])} cells; model difficulty uncalibrated")


if __name__ == "__main__":
    main()
