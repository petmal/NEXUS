#!/usr/bin/env python3
"""Independent finite-field oracle, shortcut witnesses, preparation and exact-cost proofs."""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from time import perf_counter

from nexus.engine.network import prepare, response, settings
from nexus.generator.network import compile_network, preparation_route
from nexus.models.network import BENCH, FIELD


def oracle(world, point):
    x, y = point
    i, j, k = world.gates
    a, b, c, d = world.a, world.b, world.c, world.d
    u = (x + a, x * a, x * x + a)[i] % 7
    v = (y + b, y * b, y * y + b)[j] % 7
    return (u * v + c * u * u + d * v * v, (u + c) * v * v + d * u, (u * u + c) * v + d * u * v)[
        k
    ] % 7


def rank(matrix):
    matrix = [list(row) for row in matrix]
    pivot = 0
    for column in range(len(matrix[0])):
        candidate = next((i for i in range(pivot, len(matrix)) if matrix[i][column] % 7), None)
        if candidate is None:
            continue
        matrix[pivot], matrix[candidate] = matrix[candidate], matrix[pivot]
        inverse = pow(matrix[pivot][column] % 7, -1, 7)
        matrix[pivot] = [x * inverse % 7 for x in matrix[pivot]]
        for i in range(len(matrix)):
            if i != pivot:
                factor = matrix[i][column]
                matrix[i] = [
                    (a - factor * b) % 7 for a, b in zip(matrix[i], matrix[pivot], strict=True)
                ]
        pivot += 1
        if pivot == len(matrix):
            break
    return pivot


def shortcut(worlds, points):
    groups = defaultdict(list)
    for i, w in enumerate(worlds):
        groups[tuple(oracle(w, point) for point in points)].append(i)
    ambiguous = [
        indices
        for indices in groups.values()
        if len({tuple(oracle(worlds[i], p) for p in FIELD) for i in indices}) > 1
    ]
    witness = None
    if ambiguous:
        left = ambiguous[0][0]
        right = next(i for i in ambiguous[0] if settings(worlds[i]) != settings(worlds[left]))
        witness = [
            {
                "parameters": {k: getattr(worlds[i], k) for k in ("a", "b", "c", "d", "gates")},
                "field_response": settings(worlds[i])[1:],
            }
            for i in (left, right)
        ]
    return {
        "ambiguous_transcripts": len(ambiguous),
        "ambiguous_worlds": sum(map(len, ambiguous)),
        "max_target_classes": max(
            (len({settings(worlds[i]) for i in g}) for g in ambiguous), default=1
        ),
        "admissible_world_witness": witness,
    }


def random_baseline(problem, permutations=32):
    rng = random.Random(81427)
    full = (1 << len(problem.hypotheses)) - 1
    totals = []
    partitions = [dict(row) for row in problem.partitions]
    for _ in range(permutations):
        order = list(range(len(problem.experiments)))
        rng.shuffle(order)
        for i in range(len(problem.hypotheses)):
            belief = full
            for used, index in enumerate(order, 1):
                belief &= partitions[index][problem.experiments[index][1][i]]
                if problem._resolved(belief):
                    totals.append(used)
                    break
            else:
                raise AssertionError("full random observation path remains ambiguous")
    return {
        "permutations": permutations,
        "seed": 81427,
        "world_paths": len(totals),
        "mean_measurements": sum(totals) / len(totals),
        "worst_measurements": max(totals),
    }


def prove():
    cases = []
    for t, expected in ((1, (9, 9, 2, 2)), (2, (81, 73, 3, 4)), (3, (2187, 1175, 5, 8))):
        started = perf_counter()
        worlds, problem = compile_network(t)
        for w in worlds:
            for x in range(7):
                for y in range(7):
                    assert response(w, x, y) == oracle(w, (x, y))
        cost_start = perf_counter()
        adaptive = problem.minimum_guaranteed_measurements()
        fixed = problem.minimum_fixed_measurements()
        cost_seconds = perf_counter() - cost_start
        assert (len(worlds), len(set(problem.predictions)), adaptive, fixed) == expected
        assert shortcut(worlds, BENCH)["ambiguous_transcripts"] == 0
        case = {
            "theory": t,
            "worlds": len(worlds),
            "target_classes": len(set(problem.predictions)),
            "adaptive": adaptive,
            "fixed": fixed,
            "solver_seconds": cost_seconds,
            "oracle_comparisons": len(worlds) * 49,
            "total_seconds": perf_counter() - started,
        }
        if t == 3:
            case["axes"] = shortcut(worlds, [p for p in BENCH if 0 in p])
            case["axes_and_diagonal"] = shortcut(
                worlds, [p for p in BENCH if 0 in p or p[0] == p[1]]
            )
            assert case["axes"]["ambiguous_transcripts"] == 271
            assert case["axes_and_diagonal"]["ambiguous_transcripts"] == 54
            case["random_fixed_order_baseline"] = random_baseline(problem)
        cases.append(case)
    support = sorted(
        {(x, y) for x in (0, 1, 2) for y in (0, 1, 2, 4)}
        | {(x, y) for x in (0, 1, 2, 4) for y in (0, 1, 2)}
    )

    def matrix(points):
        return [[pow(x, a, 7) * pow(y, b, 7) % 7 for a, b in support] for x, y in points]

    def null(point):
        x, y = point
        return (1 - x) * (y - y**4) % 7

    assert all(null(p) == 0 for p in BENCH)
    assert tuple(null(p) for p in FIELD) == (0, 0, 3, 0)
    assert (rank(matrix(BENCH)), rank(matrix((*BENCH, *FIELD)))) == (12, 14)
    routes = {}
    for x in range(7):
        for y in range(7):
            route = preparation_route((0, 0), (x, y))
            point = (0, 0)
            for machine in route:
                point = prepare(point, machine)
            assert point == (x, y)
            routes[f"{x}:{y}"] = list(route)
    assert prepare(prepare((0, 0), "shift"), "shear") != prepare(prepare((0, 0), "shear"), "shift")
    for machine in ("shift", "shear"):
        point = (0, 0)
        for _ in range(7):
            assert 0 in point
            point = prepare(point, machine)
    return {
        "family": "coupled-network-v1",
        "cases": cases,
        "union_polynomial_baseline": {
            "monomials": support,
            "bench_rank": 12,
            "bench_plus_field_rank": 14,
            "null_polynomial": "(1-x)*(y-y^4) mod7",
            "field_delta": [0, 0, 3, 0],
            "scope": "relaxed polynomial class; not a pair of admissible generated programs",
        },
        "preparation": {
            "reachable_states": 49,
            "noncommuting": True,
            "homogeneous_routes_only_axes": True,
            "max_origin_to_bench_operations": max(len(routes[f"{x}:{y}"]) for x, y in BENCH),
            "routes": routes,
        },
        "limitations": [
            "Information costs exclude movement and construction.",
            "GF7 readings carry less information than the prior GF17 family; cross-family counts are not a pure structure comparison.",
            "Finite enumeration is a valid strategy. Real-model difficulty is unmeasured.",
            "T1/T2 are PoC controls; live support is explicitly narrower.",
        ],
    }


if __name__ == "__main__":
    if not __debug__:
        raise SystemExit("proof requires Python assertions enabled")
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = prove()
    payload = json.dumps(result, indent=2)
    if args.out:
        args.out.write_text(payload + "\n")
    print(
        json.dumps(
            {
                "cases": [
                    {k: c[k] for k in ("theory", "worlds", "adaptive", "fixed", "solver_seconds")}
                    for c in result["cases"]
                ]
            }
        )
    )
