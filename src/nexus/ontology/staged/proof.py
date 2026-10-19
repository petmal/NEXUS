"""Offline independent scalar oracle and exact, conditional-prior panel proofs.

This module is never called during generation or ordinary play. Production law
functions are imported only for comparison against the independently built rows.
"""

from collections import Counter
from dataclasses import asdict
from itertools import combinations, product

from nexus.evaluation.goal_information import (
    feedback_success_ceiling,
    minimum_identifying_panel,
    minimum_supporting_certificate,
)

LOCAL = tuple(product(range(3), (1, 2)))


def oracle_read(world, stage, carrier, tag, linked=True):
    active = 0 if not linked or stage == 0 else (world[stage - 1][0] + world[stage - 1][1] - 1) % 3
    if carrier != active:
        return 0
    shift, exponent = world[stage]
    value = (tag + shift) % 3
    return value if exponent == 1 else value * value % 3


def oracle_loads(world, tag, doses):
    loads = [oracle_read(world, i, 0, tag, False) for i in range(len(world))]
    # Apply each treatment's effects directly, rather than invert a matrix.
    for i, dose in enumerate(doses):
        loads[i] -= dose
        if i + 1 < len(world):
            loads[i + 1] -= (world[i][0] + world[i][1] - 1) % 3 * dose
    return tuple(value % 3 for value in loads)


def oracle_repair(world):
    rows = []
    for tag in range(3):
        valid = [
            d for d in product(range(3), repeat=len(world)) if not any(oracle_loads(world, tag, d))
        ]
        if len(valid) != 1:
            raise ValueError("mission lacks a unique cumulative treatment for a fixed world")
        rows.extend(valid[0])
    return tuple(rows)


def oracle_policy(world, linked=True, exponents=None):
    known = []
    trace = []
    for stage in range(len(world)):
        carrier = (sum(known[-1]) - 1) % 3 if linked and stage else 0
        candidates = [m for m in LOCAL if exponents is None or m[1] == exponents[stage]]
        while len(candidates) > 1:
            tag = min(
                range(3),
                key=lambda u: (
                    max(Counter(oracle_read((m,), 0, 0, u) for m in candidates).values()),
                    u,
                ),
            )
            value = oracle_read(world, stage, carrier, tag, linked)
            trace.append((stage, carrier, tag, value))
            candidates = [m for m in candidates if oracle_read((m,), 0, 0, tag) == value]
            if not candidates:
                raise ValueError("public policy contradicts observation")
        known.append(candidates[0])
    if tuple(known) != world:
        raise ValueError("public adaptive witness does not identify the mechanism")
    return trace


def verify_panel_minimum(rows, result):
    """Check minimality using independent equivalence partitions, not constraint masks."""
    chosen = result.queries
    if len({tuple(row[q] for q in chosen) for row in rows}) != len(rows):
        raise ValueError("purported sufficient panel aliases worlds")
    forced = set(result.forced_queries)
    # A forced column must have a pair of worlds equal at EVERY other column.
    for q in forced:
        if not any(
            left[q] != right[q]
            and all(a == b for i, (a, b) in enumerate(zip(left, right)) if i != q)
            for left, right in combinations(rows, 2)
        ):
            raise ValueError("invalid forced-query witness")
    informative = [
        q for q in range(len(rows[0])) if len({r[q] for r in rows}) > 1 and q not in forced
    ]
    size = len(chosen) - len(forced) - 1
    checked = 0
    if size >= 0:
        for candidate in combinations(informative, size):
            panel = (*sorted(forced), *candidate)
            checked += 1
            if len({tuple(row[q] for q in panel) for row in rows}) == len(rows):
                raise ValueError("shorter identifying panel exists")
    return checked


def prove_profile(size, linked, exponents=None):
    worlds = tuple(
        w
        for w in product(LOCAL, repeat=size)
        if exponents is None or tuple(m[1] for m in w) == exponents
    )
    queries = tuple(product(range(size), range(3), range(3)))
    rows = tuple(tuple(oracle_read(w, *q, linked) for q in queries) for w in worlds)
    decisions = tuple(map(oracle_repair, worlds))
    if len(set(decisions)) != len(worlds):
        raise ValueError("distinct worlds admit a common complete repair")
    fixed = minimum_identifying_panel(rows)
    checked = verify_panel_minimum(rows, fixed)
    lengths = Counter(len(oracle_policy(w, linked, exponents)) for w in worlds)
    if max(lengths) > size * 2:
        raise ValueError("adaptive reference violates reading upper bound")
    parts = tuple(
        tuple(sum(1 << i for i, row in enumerate(rows) if row[q] == value) for value in range(3))
        for q in range(len(queries))
    )
    certificates = [
        minimum_supporting_certificate(
            (1 << len(worlds)) - 1, tuple(p[row[q]] for q, p in enumerate(parts)), (1 << i,)
        )
        for i, row in enumerate(rows)
    ]
    for i, panel in enumerate(certificates):
        compatible = [j for j, r in enumerate(rows) if all(r[q] == rows[i][q] for q in panel)]
        if compatible != [i]:
            raise ValueError("positive certificate does not establish a complete repair")
    if size == 3:
        from nexus.ontology.staged.laws import (
            WORLD_INDEX,
            WORLDS,
            decision,
            reading,
            remaining,
            tables,
        )
        from nexus.ontology.staged.schema import Mechanism, Truth

        table = tables(linked)
        for w, row, repair in zip(worlds, rows, decisions):
            truth = Truth(mechanisms=tuple(Mechanism(shift=k, exponent=e) for k, e in w))
            index = WORLD_INDEX[truth]
            if (
                WORLDS[index] != truth
                or tuple(table.rows[index]) != row
                or decision(truth) != repair
            ):
                raise ValueError("compiled observation/decision table differs from scalar oracle")
            for q, value in zip(queries, row):
                if reading(truth, *q, linked) != value or not table.partitions[
                    q[0] * 9 + q[1] * 3 + q[2]
                ][value] & (1 << index):
                    raise ValueError("runtime reading or posterior partition differs from oracle")
            for tag in range(3):
                for doses in product(range(3), repeat=3):
                    if remaining(truth, tag, doses) != oracle_loads(w, tag, doses):
                        raise ValueError(
                            "physical loads differ from independent treatment execution"
                        )
    return {
        "mechanisms": size,
        "linked": linked,
        "known_exponents": exponents,
        "worlds": len(worlds),
        "complete_mission_signatures": len(set(decisions)),
        "one_seal_signatures": len({d[:size] for d in decisions}),
        "two_seal_signatures": len({d[: 2 * size] for d in decisions}),
        "adaptive_reading_upper": max(lengths),
        "adaptive_reading_histogram": dict(sorted(lengths.items())),
        "positive_certificate_histogram": dict(sorted(Counter(map(len, certificates)).items())),
        "positive_certificates": certificates,
        "positive_certificate_scope": "Minimum actual-outcome reading certificate with oracle experiment choice, free setup and no finish feedback. Not a policy or cognitive depth.",
        "fixed_readings_exact": len(fixed.queries),
        "fixed_panel": [queries[q] for q in fixed.queries],
        "panel_certificate": asdict(fixed),
        "independent_shorter_panels_checked": checked,
        "feedback_success_ceilings": [
            {
                "feedback_actions": k,
                "numerator": feedback_success_ceiling(len(worlds), 3, 1, k),
                "denominator": len(worlds),
            }
            for k in range(1, 8)
        ],
    }


def prove_all():
    profiles = [prove_profile(n, True) for n in (1, 2, 3)]
    profiles.append(prove_profile(3, False))
    for linked, exponents in product((False, True), product((1, 2), repeat=3)):
        profiles.append(prove_profile(3, linked, exponents))
    return {
        "version": "staged-repair-proof-v1",
        "status": "passed",
        "profiles": profiles,
        "deep_tier_admitted": False,
        "scope": "Exact conditional-prior mission signatures and fixed-panel identification; constructive adaptive upper bounds; finish-inclusive relaxed success ceilings. No total-action optimum, forced investigation order, or model-failure guarantee.",
    }
