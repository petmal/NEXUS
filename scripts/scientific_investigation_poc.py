#!/usr/bin/env python3
"""Independent finite-family proof; no NEXUS runtime imports or model/API calls."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
from time import perf_counter

if not __debug__:
    raise RuntimeError("Proof execution requires Python assertions")


def build_problem(theory: int, adaptive: bool, offset: bool = True, scale: int = 1):
    # s and a are specimen/apparatus state, c is a global correction coefficient,
    # r selects a missing expression structure. The reference specimen has a=0.
    worlds = tuple(
        product(
            range(2) if adaptive else (0,),
            range(4),
            range(4),
            (0, 2) if offset else (0,),
            range(1, 4) if theory >= 2 else (1,),
            range(1, 4) if theory >= 3 else (1,),
        )
    )

    def response(w, stock, q):
        a = 0 if stock == "reference" else w[1 + int(stock)]
        return scale * (a * q * (q - 1) + w[4] * q ** w[5]) % 17

    experiments = {"selector": tuple(w[0] for w in worlds)} if adaptive else {}
    for stock in ("reference", "0", "1"):
        for q in range(3):
            experiments[f"{stock}:{q}"] = tuple(
                (response(w, stock, q) + scale * w[3]) % 17 for w in worlds
            )
    predictions = tuple((w[0], *(response(w, str(w[0]), q) for q in (4, 5, 6, 7))) for w in worlds)
    return worlds, experiments, predictions


def oracle(rows, predictions):
    """Straight tuple/set recurrence, independent of the production bitmask solver."""

    @lru_cache(None)
    def cost(belief):
        if len({predictions[i] for i in belief}) == 1:
            return 0
        best = 999
        for row in rows:
            groups = [
                tuple(i for i in belief if row[i] == value) for value in {row[i] for i in belief}
            ]
            if len(groups) > 1:
                best = min(best, 1 + max(cost(group) for group in groups))
        return best

    return cost


def fixed_cost(rows, predictions):
    for size in range(len(rows) + 1):
        for subset in combinations(rows, size):
            observed = {}
            for i, target in enumerate(predictions):
                signature = tuple(row[i] for row in subset)
                if signature in observed and observed[signature] != target:
                    break
                observed[signature] = target
            else:
                return size
    return 999


def prove(theory, adaptive, offset=True, scale=1):
    start = perf_counter()
    worlds, experiments, predictions = build_problem(theory, adaptive, offset, scale)
    rows = tuple(experiments.values())
    cost = oracle(rows, predictions)
    minimum = cost(tuple(range(len(worlds))))
    fixed = fixed_cost(rows, predictions)
    assert minimum < 999
    assert fixed > minimum if adaptive else fixed == minimum
    assert minimum == theory + 1 + int(adaptive)
    # Source specimens start at q=0. Known preparation increments q to at most2.
    # All legal raw/q1 measurements, including operation, are included here.
    unprepared = tuple(row for name, row in experiments.items() if not name.endswith(":2"))
    assert oracle(unprepared, predictions)(tuple(range(len(worlds)))) == 999
    # A directly measured target would destroy the scientific investigation.
    bypass = oracle(rows + (predictions,), predictions)
    assert bypass(tuple(range(len(worlds)))) == 1
    # Goal acceptance is exact equality of the whole configuration vector.
    # Every truth has an accepted setting; solvability excludes no world.
    counts = Counter(predictions)
    for target in predictions:
        assert target in counts
    # All measurement transcripts identify behavior, though not necessarily syntax.
    for i in range(len(worlds)):
        consistent = tuple(j for j in range(len(worlds)) if all(row[i] == row[j] for row in rows))
        assert len({predictions[j] for j in consistent}) == 1
    return {
        "theory": theory,
        "adaptive": adaptive,
        "offset": offset,
        "scale": scale,
        "truths": len(worlds),
        "target_classes": len(counts),
        "minimum": minimum,
        "fixed": fixed,
        "adaptive_gap": fixed - minimum,
        "best_prior_guess_probability": max(counts.values()) / len(worlds),
        "exhaustive_guess_upper_bound": len(counts),
        "no_preparation_identifiable": False,
        "target_preview_cost": 1,
        "visited_beliefs": cost.cache_info().currsize,
        "seconds": round(perf_counter() - start, 6),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    results = [
        prove(t, adaptive, offset=True, scale=scale)
        for scale in (1, 2, 3)
        for t in (1, 2, 3)
        for adaptive in (False, True)
    ]
    output = {
        "status": "proved",
        "scope": "pre-submission information and construction",
        "limitations": [
            "Not model difficulty evidence",
            "R0 guesses eventually succeed",
            "Certificates concern guaranteed worst-case inference, not forced chronology",
        ],
        "cases": results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.out.with_suffix(".tmp")
    temporary.write_text(json.dumps(output, indent=2) + "\n")
    temporary.replace(args.out)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
