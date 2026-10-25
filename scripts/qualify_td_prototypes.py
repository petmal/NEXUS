"""Execute bounded W4 and NW2 proof-of-concept gates; no models or new families."""

import argparse
from pathlib import Path

from nexus.evaluation.td_prototypes import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("/tmp/td-prototypes.json"))
    args = parser.parse_args()
    report = run(args.output)
    print(
        f"{report['status']}: W4 {report['W4']['seconds']:.2f}s, NW2 {report['NW2']['seconds']:.2f}s; no production admission"
    )
