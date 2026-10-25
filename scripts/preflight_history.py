"""Validate the opt-in history pilot; success does not certify deep-tier admission."""

import argparse
from pathlib import Path

from nexus.evaluation.artifacts import atomic_json
from nexus.evaluation.history import Pilot, preflight

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("docs/history-diagnostic-matrix.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        pilot = Pilot.model_validate_json(args.matrix.read_text())
    except Exception as exc:
        atomic_json(
            args.output, {"version": "history-preflight-v1", "status": "blocked", "error": str(exc)}
        )
        raise
    report = preflight(pilot, args.output)
    print(
        report["status"], f"{len(report['cells'])} cells; experimental PoC, deep tier NOT admitted"
    )
