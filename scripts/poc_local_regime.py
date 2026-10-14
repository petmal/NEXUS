"""Rejected release candidate: a specimen-local c offset after a public treatment.

Pure bounded PoC only; it does not register a live family or alter stationary play.
Shows useful selective repair, but falsifies any claim that revision is required:
an unrestricted player can treat first and investigate one stationary world.
"""

import json
from pathlib import Path

from nexus.ontology.repair.laws import residuals, response, solution, worlds


def audit():
    cases = revised = 0
    admitted = {tuple(w.model_dump().values()) for w in worlds()}
    for old in worlds():
        for delta in range(7):
            current = old.model_copy(update={"c": (old.c + delta) % 7})
            # A/B and structural degree remain valid; C is context-specific.
            assert response(old, (0, old.a)) == response(current, (0, old.a))
            c, other = response(current, (1, old.b))
            degree = {2: 1, 4: 2, 1: 3}[(other - c) % 7]
            assert degree == old.degree
            assert residuals(current, solution(old.a, old.b, c, degree)) == (0, 0, 0, 0)
            old_dose = solution(old.a, old.b, old.c, old.degree)
            assert (not any(residuals(current, old_dose))) == (delta == 0)
            # Early treatment gives exactly the original stationary family with
            # c'=c+delta. Its uniform marginal is unchanged. No old theory needed.
            assert (
                tuple(current.model_dump().values()) in admitted
            )  # Complete admitted stationary support.
            cases += 1
            revised += delta != 0
    return {
        "status": "deferred",
        "reason": "early treatment removes the need to revise a prior operational model",
        "pairs_checked": cases,
        "old_repair_invalidated_pairs": revised,
        "selective_repair": "retain a,b,d and A/B evidence; remeasure the treated C context",
        "counterpolicy": "treat relevant specimens before any observation, then execute stationary three-round policy",
        "release_gate": False,
        "future_requirement": "a separately proved transfer/revision objective; no hidden order lock or unexplained global drift",
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2) + "\n"
    if args.output:
        args.output.write_text(result)
    print(result, end="")
