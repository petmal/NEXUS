"""Fresh-process comparison of interpreted graphs and compiled finite tables.

Runner-only benchmark. Both modes use the same public reference policy and fresh
random-seed generation. No evaluated model or paid API is invoked.
"""

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from time import perf_counter


def worker(mode, seed):
    from nexus.ontology.causal import laws
    from nexus.ontology.causal.generation import generate_causal
    from nexus.ontology.causal.policy import public_policy
    from nexus.protocol.session import Session

    if mode == "interpreted":

        def interpret(world, experiment):
            transition, response = laws.graphs(world.wiring, world.transition, world.response)
            values = {
                "p": world.wiring,
                "a": world.a,
                "b": world.b,
                "h": world.initial,
                "one": 1,
                "x": 0,
                "y": 0,
                "e": 0,
            }
            for x, y, e in experiment.history:
                values.update(x=x, y=y, e=e)
                values["h"] = transition.evaluate(values, laws.PRIMITIVES)[0]
            x, y, e = experiment.point
            values.update(x=x, y=y, e=e)
            return response.evaluate(values, laws.PRIMITIVES)[0]

        laws.physical = interpret
    start = perf_counter()
    episode = generate_causal(seed)
    cold = perf_counter() - start
    start = perf_counter()
    for fresh_seed in range(seed + 1, seed + 21):
        generate_causal(fresh_seed)
    warm = (perf_counter() - start) / 20
    session = Session(episode)
    start = perf_counter()
    result = public_policy(session, episode.public.evidence_files)
    if not result.victory_code:
        raise RuntimeError("public reference failed")
    return {
        "mode": mode,
        "seed": seed,
        "cold_seconds": cold,
        "warm_seconds": warm,
        "reference_seconds": perf_counter() - start,
        "reference_actions": session.state.turn,
        "won": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=("interpreted", "compiled"))
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--out", type=Path, default=Path("causal-benchmark.json"))
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(worker(args.worker, args.seed)))
        return
    rows = []
    for i in range(args.repeats):
        for mode in ("interpreted", "compiled"):
            result = subprocess.run(
                [sys.executable, __file__, "--worker", mode, "--seed", str(args.seed + i)],
                capture_output=True,
                text=True,
                check=True,
                env=os.environ,
            )
            rows.append(json.loads(result.stdout))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(
            {
                "python": platform.python_version(),
                "method": "interleaved fresh processes, same host/interpreter, imports excluded; 20 fresh warm seeds per process; T3/D5/P1/R1",
                "results": rows,
            },
            indent=2,
        )
        + "\n"
    )
    print(f"{len(rows)} successful reference runs saved to {args.out}")


if __name__ == "__main__":
    main()
