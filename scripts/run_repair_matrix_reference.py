"""Execute the published ten-cell pilot with public reference investigators."""

import json
from pathlib import Path
from time import perf_counter

from nexus.generator import generate_episode
from nexus.presentation import evidence_files
from nexus.protocol.session import Session


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("docs/repair-model-matrix.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for row in json.loads(args.matrix.read_text())["runs"]:
        e = row["environment"]
        start = perf_counter()
        episode = generate_episode(
            int(e["NEXUS_SEED"]),
            axis_version=2,
            science_family=e["NEXUS_SCIENCE_FAMILY"],
            theory_level=int(e["NEXUS_THEORY_LEVEL"]),
            discovery_level=int(e["NEXUS_DISCOVERY_LEVEL"]),
            planning_level=int(e["NEXUS_PLANNING_LEVEL"]),
            resource_pressure=1,
            verifier_secret="matrix",
        )
        generation = perf_counter() - start
        session = Session(episode)
        if e["NEXUS_SCIENCE_FAMILY"] == "coupled-repair-v1":
            from nexus.ontology.repair.policy import public_policy

            result = public_policy(session)
        else:
            from nexus.ontology.causal.policy import public_policy

            result = public_policy(session, evidence_files(episode.public))
        assert result.victory_code
        rows.append(
            {
                "id": row["id"],
                "won": True,
                "actions": result.current_turn,
                "generation_seconds": generation,
                "total_seconds": perf_counter() - start,
            }
        )
        # Completed rows survive an interrupted later cell; no paid calls.
        args.output.write_text(json.dumps({"status": "running", "rows": rows}, indent=2) + "\n")
    args.output.write_text(json.dumps({"status": "complete", "rows": rows}, indent=2) + "\n")
    print(f"{len(rows)} reference missions won")


if __name__ == "__main__":
    main()
