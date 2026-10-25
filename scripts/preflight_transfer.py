"""Validate coupled transfer pilot before model runs; nonzero on any missing proof."""

import argparse
from pathlib import Path

from nexus.evaluation.artifacts import atomic_json
from nexus.evaluation.transfer import Pilot, preflight

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("docs/transfer-model-matrix.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = preflight(Pilot.model_validate_json(args.matrix.read_text()), args.output)
    except Exception as exc:
        atomic_json(
            args.output,
            {"version": "transfer-preflight-v1", "status": "blocked", "error": str(exc)},
        )
        raise
    print(
        report["status"], f"{len(report['cells'])} cells; empirical model difficulty uncalibrated"
    )
