"""Restartable full-population Session/replay gate. No model calls or hidden solver input."""

import argparse
import json
from pathlib import Path
from time import perf_counter

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.evaluation.artifacts import atomic_json
from nexus.generator import generate_episode
from nexus.ontology.repair.qualification import source_binding
from nexus.ontology.transfer.policy import public_policy
from nexus.protocol.session import Session


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--family", choices=("coupled-transfer-v1", "coupled-evidence-v1"), required=True
    )
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    population = 15552 if args.family == "coupled-evidence-v1" else 5184
    if not 0 <= args.start < args.stop <= population:
        parser.error("range must be inside complete family population")
    identity = {
        "family": args.family,
        "start": args.start,
        "stop": args.stop,
        "sources": source_binding(),
    }
    report = {
        "identity": identity,
        "next_seed": args.start,
        "status": "running",
        "maximum_actions": 0,
    }
    if args.output.exists():
        report = json.loads(args.output.read_text())
        if report["identity"] != identity:
            raise ValueError("checkpoint source or range mismatch; choose a fresh output")
    started = perf_counter()
    for seed in range(report["next_seed"], args.stop):
        episode = generate_episode(
            seed,
            axis_version=2,
            science_family=args.family,
            theory_level=3,
            discovery_level=5,
            planning_level=1,
            resource_pressure=1,
            verifier_secret="live-transfer-proof",
        )
        session = Session(episode)
        result = public_policy(session, episode.public.evidence_files)
        if (
            not result.victory_code
            or result.current_turn > episode.generation_metadata.guaranteed_policy_action_count
            or result.performance.decision_diagnostics.escape_classification != "supported_win"
            or canonical_hash(replay(episode, session.trace)) != canonical_hash(session.state)
        ):
            raise ValueError(f"live proof failed at {seed}")
        report["next_seed"] = seed + 1
        report["maximum_actions"] = max(report["maximum_actions"], result.current_turn)
        if (seed + 1 - args.start) % 100 == 0:
            atomic_json(args.output, report)
            print(
                json.dumps(
                    {"next_seed": seed + 1, "seconds_this_process": perf_counter() - started}
                ),
                flush=True,
            )
    report["status"] = "passed"
    atomic_json(args.output, report)
    print(
        json.dumps({"status": "passed", "seconds_this_process": perf_counter() - started}),
        flush=True,
    )


if __name__ == "__main__":
    main()
