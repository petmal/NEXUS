"""Qualify56 source-bound cross-axis conditions and export tasks; no model calls."""

import argparse
from pathlib import Path

from nexus.evaluation.cross_axis import Pilot, export_tasks, preflight


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("docs/cross-axis-matrix.json"))
    parser.add_argument("--output", type=Path, default=Path("/tmp/cross-axis-preflight.json"))
    parser.add_argument("--tasks-output", type=Path)
    args = parser.parse_args()
    pilot = Pilot.model_validate_json(args.matrix.read_text())
    report = preflight(pilot, args.output)
    if args.tasks_output:
        export_tasks(pilot, report, args.tasks_output)
    print(f"Cross-axis preflight passed: {len(report['cells'])} conditions; no model calls")


if __name__ == "__main__":
    main()
