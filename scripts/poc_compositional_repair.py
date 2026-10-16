"""Independent finite design probe; no imports from NEXUS, no model calls.

All arithmetic F3. This is a query-level construction, not a live-game proof.
"""

import json
import random
import time
from collections import Counter
from functools import lru_cache
from itertools import product
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "analysis" / "compositional-poc"
OPS = ("add", "subtract", "multiply", "square-left-add")
POINTS = tuple(product(range(3), repeat=3))
TRIMS = tuple(product(range(3), repeat=2))
REPAIRS = tuple(product(range(3), repeat=4))
WORLDS = tuple(
    (t, f, g, h, changed, new)
    for t, f, g, h, changed, new in product(
        range(3), range(4), range(4), range(4), range(3), range(4)
    )
    if new != (f, g, h)[changed]
)
QUERIES = tuple(product(range(2), POINTS, TRIMS))


def gate(op, x, y):
    return (x + y, x - y, x * y, x * x + y)[op] % 3


def evaluate(w, mode, point, trims):
    topology, f, g, h, changed, new = w
    ops = [f, g, h]
    if mode:
        ops[changed] = new
    x, y, z = point
    a, b = trims
    n1 = (gate(ops[0], x, y) + a) % 3
    n2 = (gate(ops[1], y if topology == 1 else n1, z) + b) % 3
    n3 = gate(ops[2], n2, x) if topology == 0 else gate(ops[2], n1, n2)
    return n3


def repairs(w, mission):
    result = 0
    for a, b in TRIMS:
        y0, y1, y2, y3 = [evaluate(w, mode, p, (a, b)) for mode, p in mission]
        if y0 == y1 and y2 == y3:
            c = -y0 % 3
            d = (y0 - y2) % 3
            result |= 1 << REPAIRS.index((a, b, c, d))
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    # This public mission was chosen once from 120 independently sampled candidate
    # missions (Python Random(13)), then frozen. No private-truth-specific mission.
    # The complete admitted family is EXACTLY all grammar worlds that can repair it.
    mission = ((0, (2, 0, 0)), (0, (1, 1, 1)), (1, (2, 1, 0)), (1, (1, 0, 2)))
    accepted = [(w, r) for w in WORLDS if (r := repairs(w, mission))]
    worlds = [w for w, _ in accepted]
    wins = [r for _, r in accepted]
    n = len(worlds)
    original_rows = [tuple(evaluate(w, *q) for w in worlds) for q in QUERIES]
    unique = {}
    for q, row in zip(QUERIES, original_rows):
        unique.setdefault(row, q)
    queries = list(unique.values())
    rows = list(unique)
    partitions = [
        tuple(sum(1 << i for i, v in enumerate(row) if v == r) for r in range(3)) for row in rows
    ]
    win_masks = [sum(1 << i for i, r in enumerate(wins) if r >> a & 1) for a in range(81)]
    allmask = (1 << n) - 1

    def best_repair(mask):
        return max((mask & wm).bit_count() for wm in win_masks)

    @lru_cache(None)
    def common(mask):
        return next((a for a, wm in enumerate(win_masks) if mask & ~wm == 0), None)

    visited = Counter()

    @lru_cache(None)
    def greedy(mask):
        if common(mask) is not None:
            return 0
        split = min(
            partitions,
            key=lambda ps: (
                max((mask & p).bit_count() for p in ps),
                sum((mask & p).bit_count() ** 2 for p in ps),
            ),
        )
        children = [mask & p for p in split if mask & p]
        if len(children) == 1:
            raise AssertionError("unresolvable repair")
        return 1 + max(greedy(child) for child in children)

    def trace(mask, depth=0):
        if common(mask) is not None:
            visited[depth] += mask.bit_count()
            return
        split = min(
            partitions,
            key=lambda ps: (
                max((mask & p).bit_count() for p in ps),
                sum((mask & p).bit_count() ** 2 for p in ps),
            ),
        )
        for p in split:
            if child := mask & p:
                trace(child, depth + 1)

    depth = greedy(allmask)
    trace(allmask)
    # Serialize the public policy: a branch depends only on the sensor result.
    policy_nodes = []
    policy_ids = {}

    def serialize(mask):
        if mask in policy_ids:
            return policy_ids[mask]
        node_id = len(policy_nodes)
        policy_ids[mask] = node_id
        node = {"id": node_id}
        policy_nodes.append(node)
        if (a := common(mask)) is not None:
            node["repair"] = REPAIRS[a]
        else:
            query_id = min(
                range(len(partitions)),
                key=lambda j: (
                    max((mask & p).bit_count() for p in partitions[j]),
                    sum((mask & p).bit_count() ** 2 for p in partitions[j]),
                ),
            )
            node["query"] = queries[query_id]
            node["responses"] = {
                str(r): serialize(child)
                for r, p in enumerate(partitions[query_id])
                if (child := mask & p)
            }
        return node_id

    serialize(allmask)
    for i, w in enumerate(worlds):
        node = policy_nodes[0]
        length = 0
        while "query" in node:
            reading = evaluate(w, *node["query"])
            node = policy_nodes[node["responses"][str(reading)]]
            length += 1
        assert length <= depth and wins[i] >> REPAIRS.index(tuple(node["repair"])) & 1
    (OUT / "joint-repair-public-query-policy.json").write_text(
        json.dumps(
            {
                "status": "query-level public policy; not live executable actions",
                "mission": mission,
                "nodes": policy_nodes,
            },
            separators=(",", ":"),
        )
        + "\n"
    )
    # Exact one-query success, all legal queries, with best repair per outcome.
    one = max(sum(best_repair(allmask & p) for p in ps if allmask & p) for ps in partitions)

    # Exact two-query success, unrestricted adaptive choice, by caching first-query cells.
    @lru_cache(None)
    def one_success(mask):
        return max(sum(best_repair(mask & p) for p in ps if mask & p) for ps in partitions)

    two = max(sum(one_success(allmask & p) for p in ps if allmask & p) for ps in partitions)
    # A nonterminal rejected finish supplies binary membership feedback. With no
    # further measurements, two sequential guesses cover a union of repair sets.
    pair_wins = tuple({a | b for i, a in enumerate(win_masks) for b in win_masks[i:]})

    def best_two_guesses(mask):
        return max((mask & wm).bit_count() for wm in pair_wins)

    one_two_guesses = max(
        sum(best_two_guesses(allmask & p) for p in ps if allmask & p) for ps in partitions
    )
    guess_then_query = max(wm.bit_count() + one_success(allmask & ~wm) for wm in win_masks)
    # Complete shallow signatures: perfect untrimmed observational knowledge may
    # still leave an obstruction, showing why intervention cannot simply be omitted.
    shallow_ids = [i for i, q in enumerate(QUERIES) if q[2] == (0, 0)]
    shallow_groups = {}
    for i, w in enumerate(worlds):
        sig = tuple(original_rows[q][i] for q in shallow_ids)
        shallow_groups[sig] = shallow_groups.get(sig, 0) | (1 << i)
    bad_shallow = [m for m in shallow_groups.values() if common(m) is None]

    def obstruction_example(mask):
        ids = [i for i in range(n) if mask >> i & 1]

        def intersection(indices):
            result = (1 << 81) - 1
            for i in indices:
                result &= wins[i]
            return result

        for i in tuple(ids):
            remaining = [j for j in ids if j != i]
            if remaining and not intersection(remaining):
                ids = remaining
        return [
            {"world": worlds[i], "repairs": [r for a, r in enumerate(REPAIRS) if wins[i] >> a & 1]}
            for i in ids
        ]

    # Module replacement cannot be ignored: complete data from either single mode
    # may still leave no repair shared across the complete world belief.
    mode_stats = []
    for mode in range(2):
        ids = [i for i, q in enumerate(QUERIES) if q[0] == mode]
        groups = {}
        for i in range(n):
            sig = tuple(original_rows[q][i] for q in ids)
            groups[sig] = groups.get(sig, 0) | (1 << i)
        bad = [m for m in groups.values() if common(m) is None]
        mode_stats.append(
            {
                "mode": mode,
                "signature_classes": len(groups),
                "obstructed_classes": len(bad),
                "obstructed_worlds": sum(m.bit_count() for m in bad),
                "maximum_one_guess_success_after_complete_data": [
                    sum(best_repair(m) for m in groups.values()),
                    n,
                ],
                "example_obstruction": obstruction_example(bad[0]),
            }
        )
    signature_count = len({tuple(row[i] for row in original_rows) for i in range(n)})
    ineffective_changes = sum(
        all(evaluate(w, 0, p, t) == evaluate(w, 1, p, t) for p, t in product(POINTS, TRIMS))
        for w in worlds
    )
    hard_indices = sorted(i for m in bad_shallow for i in range(n) if m >> i & 1)
    fixture_seeds = {}
    for seed in range(10000):
        index = random.Random(seed).randrange(n)
        if index in hard_indices and index not in fixture_seeds:
            fixture_seeds[index] = seed
        if len(fixture_seeds) == len(hard_indices):
            break
    result = {
        "status": "query-level experimental; no live-game or round-budget certificate",
        "grammar": {
            "ops": OPS,
            "worlds_before_solvability_filter": len(WORLDS),
            "worlds_after_disclosed_filter": n,
            "mission": mission,
            "topology_counts": dict(Counter(w[0] for w in worlds)),
            "changed_module_counts": dict(Counter(w[4] for w in worlds)),
            "primitive_counts_by_module": [dict(Counter(w[m] for w in worlds)) for m in (1, 2, 3)],
            "semantically_ineffective_changes": ineffective_changes,
        },
        "complete_query_domain": len(QUERIES),
        "distinct_query_vectors": len(rows),
        "complete_observation_signature_classes": signature_count,
        "different_winning_repair_sets": len(set(wins)),
        "legal_repairs": 81,
        "winning_repairs_per_world": dict(sorted(Counter(r.bit_count() for r in wins).items())),
        "best_uniform_success": {
            "zero_queries": [best_repair(allmask), n],
            "one_query": [one, n],
            "two_queries": [two, n],
        },
        "finish_feedback_success": {
            "zero_queries_two_guesses": [best_two_guesses(allmask), n],
            "one_query_then_two_guesses": [one_two_guesses, n],
            "guess_then_query_then_guess": [guess_then_query, n],
            "one_query_two_guesses_arbitrary_order": [max(one_two_guesses, guess_then_query), n],
            "unlimited_guesses": "all 81 repairs guarantee eventual success if resources and terminal semantics allow",
        },
        "greedy_public_witness": {
            "worst_queries": depth,
            "worlds_by_queries": dict(sorted(visited.items())),
            "belief_nodes": greedy.cache_info().currsize,
        },
        "all_untrimmed_observations": {
            "classes": len(shallow_groups),
            "obstructed_classes": len(bad_shallow),
            "obstructed_worlds": sum(m.bit_count() for m in bad_shallow),
            "maximum_one_guess_success_after_complete_data": [
                sum(best_repair(m) for m in shallow_groups.values()),
                n,
            ],
            "example_obstruction": obstruction_example(bad_shallow[0]),
        },
        "all_single_mode_queries": mode_stats,
        "intervention_obstruction_fixtures": {
            "warning": "targeted fixtures are not uniform-prior random evaluations",
            "sampler": "random.Random(seed).randrange(615), indexing accepted WORLDS order in this script",
            "worlds": [
                {
                    "index": i,
                    "seed": fixture_seeds.get(i),
                    "world": worlds[i],
                    "repairs": [r for a, r in enumerate(REPAIRS) if wins[i] >> a & 1],
                }
                for i in hard_indices
            ],
        },
        "elapsed_seconds": time.monotonic() - started,
    }
    path = OUT / "joint-repair-probe-results.json"
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
