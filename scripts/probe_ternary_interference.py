"""Run the bounded three-bank feasibility probe; never exports live model tasks."""

import argparse
from pathlib import Path

from nexus.evaluation.ternary_feasibility import VARIANTS, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("/tmp/ternary-feasibility.json"))
    parser.add_argument("--variant", action="append", choices=VARIANTS)
    args = parser.parse_args()
    report = run(args.output, variants=tuple(args.variant or VARIANTS))
    print(f"Feasibility completed: {report['admission']}; no live tasks exported")


if __name__ == "__main__":
    main()
