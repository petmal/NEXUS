"""Operator-only qualification before any paid model calls; nonzero on every failure."""

import argparse
from pathlib import Path

from nexus.evaluation.artifacts import atomic_json
from nexus.evaluation.matrix import Matrix, preflight


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("docs/difficulty-model-matrix.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-certificate-seconds", type=float, default=30)
    args = parser.parse_args()
    atomic_json(
        args.output,
        {"version": "difficulty-preflight-v1", "status": "running", "stage": "matrix-validation"},
    )
    try:
        matrix = Matrix.model_validate_json(args.matrix.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        atomic_json(
            args.output,
            {"version": "difficulty-preflight-v1", "status": "blocked", "error": str(exc)},
        )
        raise
    report = preflight(matrix, args.output, max_certificate_seconds=args.max_certificate_seconds)
    print(f"{report['status']}; empirical calibration pending; full rollout not yet recommended")


if __name__ == "__main__":
    main()
