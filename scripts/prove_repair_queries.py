"""Independent exact audit of the stated immutable weighted-query abstraction.

This is NOT a live-interface certificate. Scope: F7; uniform a,b,c,r and,
when hidden, d in {1,2,3}; stateless A/B/C queries; fixed query batches;
at most two feedback rounds; atomic complete repair guesses with generic
failure and no effects on queries. The budget is AFTER one unavoidable take.

The final target is (a,b,c,d), bijective with (a,b,f(3),f(4)) in F7.
In the player-favoring variant d is granted free, and each conditional d
stratum is isomorphic to the (a,b,c,r) problem.

Normalization used: repeated identical stateless queries add no information;
queries commute within a batch; all generic rejected guesses may be deferred
to the final commitment, reserving their costs. Continue counterfactually as
if each deferred guess failed, then prepend those guesses to the final list.
If a later observation has no counterfactual branch, one of the deferred
targets must be true and the reserved guess list wins. Choosing the largest
posterior target masses at commitment dominates every such deferred list.

Live reuse, partial repairs, informative errors, preparation effects, and
cheaper previews require a separate causal abstraction proof.
"""

from __future__ import annotations

import argparse
import json
import resource
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from time import monotonic

Q = 7
SCENARIOS = ((3, 2, 11), (4, 3, 15))


def run(hide_d: bool, max_seconds: float) -> dict:
    began = monotonic()
    ds = (1, 2, 3) if hide_d else (1,)
    # Each target occupies exactly Q consecutive bits, one per nuisance r.
    worlds = [(*abc, d, r) for abc in product(range(Q), repeat=3) for d in ds for r in range(Q)]
    # Distinct (c,d) correspond to distinct declared mission response pairs.
    mission_pairs = [((c + pow(3, d, Q)) % Q, (c + pow(4, d, Q)) % Q) for c in range(Q) for d in ds]
    assert len(set(mission_pairs)) == Q * len(ds)
    assert len({pow(2, d, Q) for d in ds}) == len(ds)
    queries = [("A",)] + [("B", x) for x in range(Q)] + [("C", y) for y in range(Q)]
    partitions = []
    for query in queries:
        bins = {}
        for i, (a, b, c, d, r) in enumerate(worlds):
            if query[0] == "A":
                observation = a
            elif query[0] == "B":
                observation = (b + r * (a - query[1])) % Q
            else:
                value = (c + r * (b - query[1])) % Q
                # Equivalent to (value, value+2**d), with a checked bijection.
                observation = (value, d) if hide_d else value
            bins[observation] = bins.get(observation, 0) | (1 << i)
        partitions.append(tuple(bins.values()))
    full = (1 << len(worlds)) - 1

    def poll() -> None:
        if monotonic() - began > max_seconds:
            raise TimeoutError("UNKNOWN: declared scratch-audit time limit reached")

    # Refined partitions are cheap to recompute but expensive to retain: bound
    # this cache explicitly so the full model does not keep gigabytes of cells.
    @lru_cache(maxsize=1024)
    def refine(mask: int, selected: tuple[int, ...]) -> tuple[int, ...]:
        cells = (mask,)
        for i in selected:
            cells = tuple(value for cell in cells for p in partitions[i] if (value := cell & p))
        return cells

    @lru_cache(None)
    def cumulative_target_mass(mask: int) -> tuple[int, ...]:
        values = []
        while mask:
            low = mask & -mask
            target = (low.bit_length() - 1) // Q
            block = ((1 << Q) - 1) << (target * Q)
            values.append((mask & block).bit_count())
            mask &= ~block
        values.sort(reverse=True)
        sums = [0]
        for value in values:
            sums.append(sums[-1] + value)
        return tuple(sums)

    def guess_value(mask: int, count: int) -> int:
        sums = cumulative_target_mass(mask)
        return sums[min(count, len(sums) - 1)]

    results = []
    for bc_cost, guess_cost, budget in SCENARIOS:
        started = monotonic()
        costs = [1] + [bc_cost] * (2 * Q)
        cheapest = sorted(costs)
        max_count = max(
            n for n in range(len(queries) + 1) if sum(cheapest[:n]) + guess_cost <= budget
        )
        batches = [(0, ())]
        for n in range(1, max_count + 1):
            for selected in combinations(range(len(queries)), n):
                cost = sum(costs[i] for i in selected)
                if cost + guess_cost <= budget:
                    batches.append((cost, selected))

        @lru_cache(None)
        def last(
            mask: int, left: int, batches=tuple(batches), guess_cost=guess_cost
        ) -> tuple[int, tuple[int, ...]]:
            poll()
            best = (-1, ())
            for cost, selected in batches:
                if cost + guess_cost > left:
                    continue
                guesses = (left - cost) // guess_cost
                value = sum(guess_value(cell, guesses) for cell in refine(mask, selected))
                if value > best[0]:
                    best = (value, selected)
            return best

        best = (-1, ())
        for cost, selected in batches:
            poll()
            score = sum(last(cell, budget - cost)[0] for cell in refine(full, selected))
            if score > best[0]:
                best = (score, selected)
        example_cells = refine(full, best[1])[:2]
        first_cost = sum(costs[i] for i in best[1])
        examples = []
        for cell in example_cells:
            mass, selected = last(cell, budget - first_cost)
            examples.append(
                {
                    "second_batch": [queries[i] for i in selected],
                    "branch_mass": cell.bit_count(),
                    "success_mass": mass,
                }
            )
        results.append(
            {
                "bc_cost": bc_cost,
                "guess_cost": guess_cost,
                "budget_after_take": budget,
                "query_batch_subsets": len(batches),
                "maximum_query_count": max_count,
                "success_mass": best[0],
                "success_probability": str(Fraction(best[0], len(worlds))),
                "best_first_batch": [queries[i] for i in best[1]],
                "example_branches": examples,
                "last_batch_cache": last.cache_info()._asdict(),
                "seconds": round(monotonic() - started, 6),
            }
        )
    return {
        "scope": "immutable-weighted-query-and-generic-complete-guess-model-only",
        "field": "F7",
        "d_hidden": hide_d,
        "worlds": len(worlds),
        "mission_targets": len(worlds) // Q,
        "queries": len(queries),
        "results": results,
        "refinement_cache": refine.cache_info()._asdict(),
        "target_mass_cache": cumulative_target_mass.cache_info()._asdict(),
        "seconds": round(monotonic() - began, 6),
        "process_peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=("granted", "hidden", "both"), default="both")
    parser.add_argument("--max-seconds", type=float, default=60.0, help="per-model time limit")
    args = parser.parse_args()
    models = (False, True) if args.model == "both" else (args.model == "hidden",)
    print(json.dumps([run(hidden, args.max_seconds) for hidden in models], indent=2))
