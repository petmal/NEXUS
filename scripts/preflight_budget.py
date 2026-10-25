"""Run the eight-execution budget matrix's operator qualification without model calls."""

import argparse
from pathlib import Path

from nexus.evaluation.artifacts import atomic_json
from nexus.evaluation.budget_diagnostic import BudgetDiagnostic, preflight


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("docs/budget-diagnostic-matrix.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    atomic_json(args.output, {"version": "budget-preflight-v1", "status": "running"})
    try:
        matrix = BudgetDiagnostic.model_validate_json(args.matrix.read_text())
        report = preflight(matrix, args.output)
    except Exception as exc:
        atomic_json(
            args.output, {"version": "budget-preflight-v1", "status": "blocked", "error": str(exc)}
        )
        raise
    print(report["status"], "eight executions; four controlled pairs; no model calls")


if __name__ == "__main__":
    main()
