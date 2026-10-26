"""Qualify the bounded coordination matrix and export source-bound tasks."""

import argparse
from pathlib import Path

from nexus.evaluation.artifacts import atomic_json
from nexus.evaluation.coordination import Pilot, export_tasks, preflight


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("docs/coordination-matrix.json"))
    parser.add_argument("--output", type=Path, default=Path("/tmp/coordination-preflight.json"))
    parser.add_argument(
        "--tasks-output", type=Path, help="Directory for qualified core/spatial task files"
    )
    args = parser.parse_args()
    try:
        pilot = Pilot.model_validate_json(args.matrix.read_text())
        report = preflight(pilot, args.output)
        if args.tasks_output:
            export_tasks(pilot, report, args.tasks_output)
    except Exception as exc:
        if not args.output.exists():
            atomic_json(args.output, {"status": "blocked", "error": f"{type(exc).__name__}: {exc}"})
        raise
    print(f"Coordination preflight passed: {len(report['cells'])} cells; no model calls")


if __name__ == "__main__":
    main()
