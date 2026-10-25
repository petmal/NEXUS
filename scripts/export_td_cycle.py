"""Generate operator-controlled harness inputs, without invoking a provider."""

import argparse
from pathlib import Path

from nexus.evaluation.td_cycle import Cycle
from nexus.evaluation.td_export import export


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("docs/td-cycle-matrix.json"))
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument(
        "--template", type=Path, default=Path("examples/mindtrial/td-cycle-harness.json")
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--image", default="nexus:td-cycle-v1")
    args = parser.parse_args()
    result = export(
        Cycle.model_validate_json(args.matrix.read_text()),
        args.preflight,
        args.template,
        args.output,
        image=args.image,
    )
    print(f"Exported {len(result['executions'])} planned executions; no models called")


if __name__ == "__main__":
    main()
