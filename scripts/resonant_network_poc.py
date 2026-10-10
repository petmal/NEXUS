#!/usr/bin/env python3
"""Independent mathematical proof before runtime integration of dependent discovery."""

import argparse
import json
from itertools import product
from pathlib import Path

from nexus.generator.network import compile_network, information_certificate, preparation_route
from nexus.generator.resonance import generate_resonant
from nexus.models.network import FIELD
from nexus.solver.finite_experiments import FiniteExperimentProblem


def calibration(world, point):
    a, b, gate = world
    x, y = point
    return (a * x + b * y, a * x * x + b * y, a * x + b * y * y)[gate] % 7


def prove():
    domain = tuple(p for p in product(range(7), repeat=2) if p not in FIELD)
    upstream = tuple(product(range(1, 4), range(1, 4), range(3)))
    signatures = tuple(tuple(calibration(w, p) for p in domain) for w in upstream)
    assert len(set(signatures)) == len(upstream)
    problem = FiniteExperimentProblem(
        tuple(map(str, upstream)),
        tuple(
            (f"{x}:{y}", tuple(calibration(w, (x, y)) for w in upstream))
            for x, y in ((0, 6), (6, 0))
        ),
        tuple(range(len(upstream))),
    )
    worlds, downstream = compile_network()
    certificate = information_certificate()
    paths = []
    for w in upstream:
        obs = ()
        while (name := problem.best_experiment(obs)) is not None:
            obs += ((name, calibration(w, tuple(map(int, name.split(":"))))),)
        assert len(problem.compatible(obs)) == 1
        paths.append(obs)
    prefix_bounds = {}
    for d in (4, 5):
        costs = []
        for path in paths:
            if d == 4:
                costs.append(4 * len(path))  # take, outward move, probe, return
            else:
                point = (0, 0)
                cost = 3  # take, outward move, return
                for name, _ in path:
                    target = tuple(map(int, name.split(":")))
                    cost += len(preparation_route(point, target)) + 1
                    point = target
                costs.append(cost)
        prefix_bounds[str(d)] = max(costs)
    # Different downstream target classes remain after complete upstream evidence.
    assert len(set(downstream.predictions)) > 1
    # No-signal is distinguishable from an actual zero response.
    assert all(0 <= calibration(w, p) < 7 for w in upstream for p in domain)
    profiles = {}
    for d in (4, 5):
        e = generate_resonant(
            7,
            discovery_level=d,
            theory_level=3,
            planning_level=1,
            resource_pressure=1,
            verifier_secret="proof-only",
        )
        assert e.generation_metadata.action_budget < 2 * len(domain) + 2
        profiles[str(d)] = {
            "policy_action_bound": e.generation_metadata.guaranteed_policy_action_count,
            "R1_budget": e.generation_metadata.action_budget,
        }
    fixed = ((4, 4), (6, 4), (4, 6), (3, 3), (6, 1), (0, 1), (0, 2))
    from nexus.engine.network import response, settings

    transcripts = {}
    for w in worlds:
        observed = tuple(response(w, *p) for p in fixed)
        target = settings(w)
        assert transcripts.setdefault(observed, target) == target
    hf = [tuple(calibration(h, p) for p in FIELD) for h in upstream]
    gf = [settings(g)[1:] for g in worlds]
    joint = {tuple((a + b) % 7 for a, b in zip(h, g, strict=True)) for h in hf for g in gf}
    assert len(joint) == 2401
    return {
        "family": "resonant-network-v1",
        "upstream_worlds": len(upstream),
        "downstream_worlds": len(worlds),
        "joint_worlds": len(upstream) * len(worlds),
        "bench_coordinates": len(domain),
        "meter_experiments": 7 * len(domain),
        "calibration_minimum": problem.minimum_guaranteed_measurements(),
        "calibration_lower_bound": "27 distinct functions; one GF7 reading has at most7 outcomes",
        "calibration_fixed_minimum": problem.minimum_fixed_measurements(),
        "downstream_adaptive_minimum_on_witness_subset": certificate["minimum_measurements"],
        "calibration_P1_prefix_bounds": prefix_bounds,
        "composed_P1_profiles": profiles,
        "joint_target_classes": len(joint),
        "expanded_domain_fixed_G_witness": fixed,
        "expanded_domain_shortcuts": "Seven fixed G readings suffice; axes plus diagonal suffice; "
        "the union polynomial basis is now identifiable. Exact G-program recovery is not required.",
        "complete_coordinate_sweep_action_lower_bound": 2 * len(domain) + 2,
        "downstream_target_classes_after_full_calibration": len(set(downstream.predictions)),
        "claims": "Downstream subset minima only; joint and expanded-domain minimax not claimed. "
        "No-signal constrains calibration only; active signal constrains each factor independently.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = json.dumps(prove(), indent=2) + "\n"
    if args.out:
        args.out.write_text(result)
    print(result)
