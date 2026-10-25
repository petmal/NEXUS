"""Fresh-process cost measurements and constructive fixed-panel controls; no model calls."""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from time import perf_counter

from nexus.evaluation.artifacts import atomic_json

CODE = """
import json, resource
from time import perf_counter
from nexus.generator import generate_episode
from nexus.ontology.transfer.policy import public_policy
from nexus.protocol.session import Session
kwargs=dict(axis_version=2,science_family={family!r},theory_level=3,discovery_level=5,planning_level=1,resource_pressure=1)
started=perf_counter(); e=generate_episode(3550,**kwargs); cold=perf_counter()-started
started=perf_counter(); generate_episode(3550,**kwargs); warm=perf_counter()-started
started=perf_counter(); result=public_policy(Session(e),e.public.evidence_files); live=perf_counter()-started
assert result.victory_code
print(json.dumps(dict(cold_generation_seconds=cold,warm_generation_seconds=warm,first_live_policy_including_terminal_seconds=live,peak_rss_kib_linux=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)))
"""


def fixed_panel(coupled):
    from nexus.ontology.transfer.tables import compile_tables

    table = compile_tables(coupled)
    unresolved = [table.full]
    selected, progress = [], []
    started = perf_counter()
    while unresolved:
        if perf_counter() - started > 120:
            raise TimeoutError("fixed-panel search incomplete; no depth claim")
        query = min(
            (i for i in range(len(table.outcomes)) if i not in selected),
            key=lambda i: sum(
                (group & p).bit_count() ** 2 for group in unresolved for p in table.outcomes[i]
            ),
        )
        selected.append(query)
        unresolved = [
            part
            for group in unresolved
            for p in table.outcomes[query]
            if (part := group & p) and not table.common(part)
        ]
        progress.append(len(unresolved))
    return {
        "query_indices": selected,
        "readings": len(selected),
        "unresolved_groups_after_each": progress,
        "seconds": perf_counter() - started,
        "scope": "Constructive fixed nonadaptive panel over complete public grammar, not a minimal panel.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.repetitions <= 5:
        parser.error("repetitions must be 1..5")
    report = {
        "scope": "Fresh Linux process, imports excluded; shared host, no container timing/SLA or model-cost claim.",
        "samples": [],
        "fixed_panels": {},
    }
    for repetition in range(args.repetitions):
        for family in ("coupled-transfer-v1", "coupled-evidence-v1"):
            result = subprocess.run(
                [sys.executable, "-c", CODE.format(family=family)],
                capture_output=True,
                text=True,
                check=True,
            )
            report["samples"].append(
                {"family": family, "repetition": repetition, **json.loads(result.stdout)}
            )
            atomic_json(args.output, report)
    for coupled in (False, True):
        report["fixed_panels"]["coupled" if coupled else "calibrated"] = fixed_panel(coupled)
        atomic_json(args.output, report)
    from compile_transfer_reference import tree

    from nexus.ontology.transfer.laws import QUERIES

    passive = tree(
        True, tuple(i for i in range(2 * len(QUERIES)) if QUERIES[i % len(QUERIES)][4:] == (0, 0))
    )
    report["coupled_passive_only_witness"] = {
        "readings": passive["readings"],
        "p1_action_upper": 7 + 3 * passive["readings"],
        "scope": "Complete-prior public greedy upper, no intervention required; not an optimum.",
    }
    report["status"] = "passed"
    atomic_json(args.output, report)
    print(json.dumps({k: v["readings"] for k, v in report["fixed_panels"].items()}))
