"""Paired fresh-process generation benchmark; never calls an evaluated model."""

import argparse
import json
import statistics
import subprocess
import sys
from pathlib import Path

CODE = """
import json
from time import perf_counter
from types import MappingProxyType
from nexus.ontology.dynamics import reference_cache
from nexus.ontology.dynamics.generation import generate_dynamics
if {uncached!r}:
    reference_cache.load = lambda: MappingProxyType({{}})
started=perf_counter()
e=generate_dynamics(219)
print(json.dumps({{"generation_seconds":perf_counter()-started,"budget":e.generation_metadata.action_budget}}))
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--pairs", type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.pairs <= 10:
        parser.error("pairs must be 1..10")
    samples = []
    for pair in range(args.pairs):
        for uncached in (True, False) if pair % 2 == 0 else (False, True):
            result = subprocess.run(
                [sys.executable, "-c", CODE.format(uncached=uncached)],
                check=True,
                capture_output=True,
                text=True,
            )
            samples.append({"pair": pair, "cache": not uncached, **json.loads(result.stdout)})
    report = {
        "python": sys.version,
        "scope": "fresh process, imports excluded, same source with artifact load enabled/disabled; shared host, not container timings",
        "samples": samples,
        "median_seconds": {
            str(enabled): statistics.median(
                s["generation_seconds"] for s in samples if s["cache"] == enabled
            )
            for enabled in (False, True)
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["median_seconds"]))


if __name__ == "__main__":
    main()
