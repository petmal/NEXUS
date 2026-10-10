"""Qualified coupled-network families, exact information policies and physical witnesses."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import secrets
from collections import Counter
from functools import lru_cache
from itertools import product
from time import perf_counter

from nexus.diagnostics import timed_stage
from nexus.engine.network import measurement, program, response, settings
from nexus.generator.network_world import NetworkWitness, build_network_world, preparation_route
from nexus.generator.randomness import rng_for
from nexus.models.episode import GenerationMetadata, PrivateEpisode
from nexus.models.network import BENCH, NetworkSpec, NetworkTruth
from nexus.solver.finite_experiments import FiniteExperimentProblem

__all__ = [
    "compile_network",
    "generate_network",
    "information_certificate",
    "policy_bound",
    "preparation_route",
    "reference_plan",
    "validate_profile",
]

LOG = logging.getLogger("nexus.generation")


@lru_cache(maxsize=3)
def compile_network(theory: int = 3):
    """T1/T2 are mathematical ablations, not additional unqualified runtime profiles."""
    if theory not in (1, 2, 3):
        raise ValueError("network mathematical prior requires T1..3")
    worlds = tuple(
        NetworkTruth(a=a, b=b, c=c, d=d, gates=(i, j, k), program=program((i, j, k)))
        for a, b, c, d, i, j, k in product(
            range(1, 4),
            range(1, 4),
            (1,) if theory == 1 else range(1, 4),
            (1,) if theory == 1 else range(1, 4),
            (0,) if theory < 3 else range(3),
            (0,) if theory < 3 else range(3),
            (0,) if theory < 3 else range(3),
        )
    )
    rows = tuple((f"{x}:{y}", tuple(response(w, x, y) for w in worlds)) for x, y in BENCH)
    answers = tuple(settings(w) for w in worlds)
    labels = {answer: i for i, answer in enumerate(dict.fromkeys(answers))}
    return worlds, FiniteExperimentProblem(
        tuple(str(i) for i in range(len(worlds))), rows, tuple(labels[a] for a in answers)
    )


@lru_cache(maxsize=1)
def information_certificate():
    worlds, problem = compile_network()
    minimum = problem.minimum_guaranteed_measurements()
    fixed = problem.minimum_fixed_measurements()
    if minimum != 5 or fixed != 8:
        raise ValueError("coupled network must retain its exact 5/8 adaptive advantage")
    axes = FiniteExperimentProblem(
        problem.hypotheses,
        tuple(row for row, point in zip(problem.experiments, BENCH, strict=True) if 0 in point),
        problem.predictions,
    )
    if axes.minimum_guaranteed_measurements() is not None:
        raise ValueError("homogeneous preparation bypasses mixed experiment construction")
    classes = Counter(problem.predictions)
    return {
        "axis_version": 2,
        "family": "coupled-network-v1",
        "prior_worlds": len(worlds),
        "structural_programs": len({w.gates for w in worlds}),
        "target_classes": len(classes),
        "minimum_measurements": minimum,
        "fixed_measurements": fixed,
        "adaptive_gap": fixed - minimum,
        "homogeneous_preparation_sufficient": False,
        "best_prior_guess_probability": max(classes.values()) / len(worlds),
        "exhaustive_guess_submissions": len(classes),
        "certificate_scope": "scientific inference before controller feedback",
        "physical_policy_kind": "realizable upper bound, not physical minimax optimum",
    }


def reference_plan(episode: PrivateEpisode, truth: NetworkTruth | None = None):
    spec = episode.public.investigation
    truth = truth or episode.investigation_truth
    worlds, problem = compile_network()
    observations = spec.supplied_measurements
    witness = NetworkWitness(episode)
    plan = witness.actions

    while spec.resolved_settings is None:
        name = problem.best_experiment(observations)
        if name is None:
            break
        x, y = map(int, name.split(":"))
        artifact = witness.prepare((x, y))
        plan.append({"type": "probe", "machine": "meter", "artifact": artifact})
        observations += ((name, measurement(truth, name)),)
    if spec.resolved_settings is None:
        answers = {settings(worlds[i]) for i in problem.compatible(observations)}
        if len(answers) != 1:
            raise ValueError("network reference failed to resolve the field response")
        answer = next(iter(answers))
    else:
        answer = spec.resolved_settings
    witness.move(spec.controller_room)
    plan.extend(
        (
            {"type": "configure", "machine": "controller", "settings": list(answer)},
            {"type": "finish"},
        )
    )
    return tuple(plan)


@lru_cache(maxsize=12)
def policy_bound(discovery: int, planning: int) -> int:
    """Uniform physical bound for a fixed public layout, independent of seed and R.

    Cache only an integer. Constructing an episode never shares mutable state or
    verifier material with another episode. Information-policy changes require a
    new process/family version, just like the cached prior and certificate.
    """
    validate_profile(discovery, 3, planning, 0)
    if discovery == 0:
        return planning + 2
    worlds, problem = compile_network()
    template = build_network_world(
        spec=NetworkSpec(theory=3, discovery=discovery, controller_room=f"R{planning}"),
        truth=worlds[0],
        planning=planning,
        pressure=0,
        seed=0,
        secret="bound-only",
        episode_id="bound-only",
        description="Policy witness template",
    )
    representatives = ((mask & -mask).bit_length() - 1 for mask in problem.policy_leaf_masks)
    return max(len(reference_plan(template, worlds[i])) for i in representatives)


def validate_profile(d: int, t: int, p: int, r: int):
    if p not in range(4) or r not in range(3):
        raise ValueError("coupled-network-v1 requires P0..3/R0..2")
    if not ((t == 3 and d in (0, 4, 5)) or (t == 0 and d == 0)):
        raise ValueError("coupled-network-v1 supports T3/D4-D5 and D0/T0,T3 controls only")


def generate_network(
    seed: int,
    *,
    discovery_level: int,
    theory_level: int,
    planning_level: int,
    resource_pressure: int,
    verifier_secret: str | None = None,
) -> PrivateEpisode:
    start = perf_counter()
    d, t, p, r = discovery_level, theory_level, planning_level, resource_pressure
    validate_profile(d, t, p, r)
    with timed_stage("network.prior") as metrics:
        metrics["prior_cache_entries_before"] = compile_network.cache_info().currsize
        worlds, problem = compile_network()
        metrics["prior_worlds"] = len(worlds)
    with timed_stage("network.information_policy") as metrics:
        certificate = dict(information_certificate())
        metrics["cached_beliefs"] = problem._cost.cache_info().currsize
        metrics["minimum_measurements"] = certificate["minimum_measurements"]
        metrics["fixed_measurements"] = certificate["fixed_measurements"]
    truth = worlds[rng_for(seed, "coupled-network-v1").randrange(len(worlds))]
    secret = verifier_secret or secrets.token_hex(32)
    episode_id = hmac.new(
        secret.encode(),
        json.dumps(["coupled-network-v1", seed, d, t, p, r]).encode(),
        hashlib.sha256,
    ).hexdigest()[:24]
    spec = NetworkSpec(theory=t, discovery=d, controller_room=f"R{p}")
    if d == 0:
        spec = spec.model_copy(
            update={
                "supplied_measurements": tuple(
                    (name, measurement(truth, name)) for name, _ in problem.experiments
                ),
                "resolved_settings": settings(truth) if t == 0 else None,
            }
        )
        certificate.update(
            minimum_measurements=0,
            fixed_measurements=0,
            adaptive_gap=0,
            target_classes_after_evidence=1,
        )
    episode = build_network_world(
        spec=spec,
        truth=truth,
        planning=p,
        pressure=r,
        seed=seed,
        secret=secret,
        episode_id=episode_id,
        description="Infer the coupled response network and calibrate its field controller. Read all evidence files.",
    )
    with timed_stage("network.physical_witnesses") as metrics:
        metrics["bound_cache_entries_before"] = policy_bound.cache_info().currsize
        bound = policy_bound(d, p)
        budget = None if r == 0 else bound + (8 if r == 1 else 0)
        episode.public.initial_state.resources.actions_remaining = budget
        episode.reference_plan = reference_plan(episode)
        metrics["policy_leaves"] = len(problem.policy_leaf_masks)
        metrics["policy_action_bound"] = bound
        metrics["reference_actions"] = len(episode.reference_plan)
    certificate.update(
        construction_required=d == 5,
        constructive_policy_action_bound=bound,
        action_budget=budget,
        initial_measurements=len(spec.supplied_measurements),
    )
    episode.generation_metadata = GenerationMetadata(
        theory_level=t,
        discovery_level=d,
        planning_level=p,
        resource_pressure=r,
        scenario_family_id="coupled-network-v1",
        room_count=p + 1,
        machine_count=4,
        optimal_action_count=p + 2,
        action_budget=budget or 0,
        required_probe_count=certificate["minimum_measurements"],
        guaranteed_policy_action_count=bound,
        recommended_tool_call_limit=bound + 12,
        investigation_certificate=certificate,
    )
    with timed_stage("network.public_evidence"):
        from nexus.generator.network_docs import evidence_files

        episode.public.evidence_files = evidence_files(episode)
    LOG.info(
        "network_generated family=coupled-network-v1 D=%s T=%s P=%s R=%s prior=%s target_classes=%s adaptive=%s fixed=%s policy_bound=%s total_seconds=%.6f",
        d,
        t,
        p,
        r,
        len(worlds),
        certificate["target_classes"],
        certificate["minimum_measurements"],
        certificate["fixed_measurements"],
        bound,
        perf_counter() - start,
    )
    return episode
