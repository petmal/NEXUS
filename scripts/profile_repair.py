"""Small reproducible cold/warm pilot; no LLM requests or proof search on startup."""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from time import perf_counter


def sample(p):
    from nexus.generator.generator import generate_episode
    from nexus.ontology.repair.policy import public_policy
    from nexus.protocol.session import Session

    timings = []
    for seed in (0, 42, 3217, 7202):
        start = perf_counter()
        episode = generate_episode(
            seed,
            axis_version=2,
            science_family="coupled-repair-v1",
            theory_level=3,
            discovery_level=5,
            planning_level=p,
            resource_pressure=1,
            verifier_secret="profile",
        )
        elapsed = perf_counter() - start
        begin = perf_counter()
        result = public_policy(Session(episode))
        play = perf_counter() - begin
        assert result.victory_code and result.current_turn == 14 + p
        timings.append(
            {
                "seed": seed,
                "generation_seconds": elapsed,
                "reference_play_seconds": play,
                "won": True,
            }
        )
    import resource

    return {
        "planning": p,
        "samples": timings,
        "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=int, choices=(0, 1))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.worker is not None:
        print(json.dumps(sample(args.worker)))
    else:
        results = []
        # Sequential fresh processes make this a timing comparison, not a CPU race.
        for _ in range(3):
            for p in (0, 1):
                process = subprocess.run(
                    [sys.executable, __file__, "--worker", str(p)],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=60,
                )
                results.append(json.loads(process.stdout))
        data = (
            json.dumps(
                {
                    "scope": "six fresh processes; first generation cold, next three warm; imports excluded; shared host uncontrolled",
                    "results": results,
                },
                indent=2,
            )
            + "\n"
        )
        if args.output:
            args.output.write_text(data)
        print(data, end="")
