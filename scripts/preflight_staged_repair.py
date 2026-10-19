"""Fail-closed validation of the staged-repair real-model matrix."""

import argparse
from pathlib import Path

from nexus.evaluation.matrix import atomic_json
from nexus.evaluation.staged import Pilot, preflight


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("docs/staged-repair-matrix.json"))
    parser.add_argument("--output", type=Path, default=Path("/tmp/staged-repair-preflight.json"))
    args = parser.parse_args()
    # Invalidate a prior pass before even reading the matrix: missing/malformed
    # inputs must not leave a successful artifact from an earlier invocation.
    report = {"version": "staged-repair-preflight-v1", "status": "running"}
    atomic_json(args.output, report)
    try:
        pilot = Pilot.model_validate_json(args.matrix.read_text(encoding="utf-8"))
    except Exception as exc:
        atomic_json(args.output, {**report, "status": "blocked", "error": str(exc)})
        raise
    result = preflight(pilot, args.output)
    print(f"staged matrix passed: {len(result['cells'])} executions, {result['seconds']:.3f}s")


if __name__ == "__main__":
    main()
