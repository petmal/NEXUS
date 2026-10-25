"""Qualify the bounded T/D cycle without model calls."""

import argparse
from pathlib import Path

from nexus.evaluation.artifacts import atomic_json
from nexus.evaluation.td_cycle import Cycle, preflight


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("docs/td-cycle-matrix.json"))
    parser.add_argument("--output", type=Path, default=Path("/tmp/td-cycle-preflight.json"))
    args = parser.parse_args()
    try:
        cycle = Cycle.model_validate_json(args.matrix.read_text())
    except Exception as exc:
        atomic_json(args.output, {"status": "blocked", "error": f"{type(exc).__name__}: {exc}"})
        raise
    result = preflight(cycle, args.output)
    print(
        f"Passed {len(result['cells'])} conditions in {result['seconds']:.2f}s; live evaluation pending"
    )


if __name__ == "__main__":
    main()
