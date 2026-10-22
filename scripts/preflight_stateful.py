"""Pre-qualify the stateful pilot before spending model executions."""

import argparse
from pathlib import Path

from nexus.evaluation.matrix import atomic_json
from nexus.evaluation.stateful import Pilot, preflight


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("docs/stateful-matrix.json"))
    parser.add_argument("--output", type=Path, default=Path("/tmp/stateful-preflight.json"))
    args = parser.parse_args()
    atomic_json(args.output, {"status": "running"})
    try:
        pilot = Pilot.model_validate_json(args.matrix.read_text(encoding="utf-8"))
        result = preflight(pilot, args.output)
    except Exception as exc:
        # Preserve the richer checkpoint if preflight itself recorded the error.
        import json

        prior = json.loads(args.output.read_text())
        if prior.get("status") != "blocked":
            atomic_json(args.output, {"status": "blocked", "error": f"{type(exc).__name__}: {exc}"})
        raise
    print(
        f"stateful preflight passed: {len(result['cells'])} rows in {result['seconds']:.2f}s; empirical difficulty uncalibrated"
    )


if __name__ == "__main__":
    main()
