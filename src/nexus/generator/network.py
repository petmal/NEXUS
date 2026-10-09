"""Qualified coupled-network families, exact information policies and physical witnesses."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import secrets
from collections import Counter, deque
from functools import lru_cache
from itertools import product
from time import perf_counter

from nexus.diagnostics import timed_stage
from nexus.engine.network import measurement, prepare, program, response, settings
from nexus.generator.randomness import rng_for
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalPredicate
from nexus.models.network import BENCH, NetworkSpec, NetworkStock, NetworkTruth
from nexus.models.world import Machine, Resources, Room, WorldState
from nexus.solver.finite_experiments import FiniteExperimentProblem

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
    if (minimum, fixed) != (5, 8):
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


@lru_cache(maxsize=49 * 49)
def preparation_route(start: tuple[int, int], target: tuple[int, int]) -> tuple[str, ...]:
    queue = deque(((start, ()),))
    seen = {start}
    while queue:
        point, path = queue.popleft()
        if point == target:
            return path
        for machine in ("shift", "shear"):
            other = prepare(point, machine)
            if other not in seen:
                seen.add(other)
                queue.append((other, path + (machine,)))
    raise ValueError("unreachable network preparation")


def reference_plan(episode: PrivateEpisode, truth: NetworkTruth | None = None):
    spec = episode.public.investigation
    truth = truth or episode.investigation_truth
    worlds, problem = compile_network()
    observations = spec.supplied_measurements
    plan = []
    room = "R0"
    bench_room = episode.public.initial_state.machines["meter"].room_id
    artifact, current = None, (0, 0)

    def move(destination):
        nonlocal room
        while room != destination:
            index, target = int(room[1:]), int(destination[1:])
            room = f"R{index + (1 if target > index else -1)}"
            plan.append({"type": "move", "target": room})

    while spec.resolved_settings is None:
        name = problem.best_experiment(observations)
        if name is None:
            break
        target = tuple(map(int, name.split(":")))
        if spec.discovery == 5:
            if artifact is None:
                move("R0")
                plan.append({"type": "take", "artifact": "S0-0"})
                artifact = f"S0-0.{len(plan)}"
            move(bench_room)
            for machine in preparation_route(current, target):
                plan.append({"type": "operate", "machine": machine, "artifact": artifact})
            current = target
        else:
            move("R0")
            stock = f"S{target[0]}-{target[1]}"
            plan.append({"type": "take", "artifact": stock})
            artifact = f"{stock}.{len(plan)}"
            move(bench_room)
        plan.append({"type": "probe", "machine": "meter", "artifact": artifact})
        observations += ((name, measurement(truth, name)),)
    if spec.resolved_settings is None:
        answers = {settings(worlds[i]) for i in problem.compatible(observations)}
        if len(answers) != 1:
            raise ValueError("network reference failed to resolve the field response")
        answer = next(iter(answers))
    else:
        answer = spec.resolved_settings
    move(spec.controller_room)
    plan.extend(
        (
            {"type": "configure", "machine": "controller", "settings": list(answer)},
            {"type": "finish"},
        )
    )
    return tuple(plan)


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
    stocks = {
        f"S{x}-{y}": NetworkStock(
            id=f"S{x}-{y}", location="R0", x=x, y=y, remaining=None if r == 0 else 16
        )
        for x, y in (((0, 0),) if d == 5 else BENCH)
    }
    bench_room = "R0" if p == 0 else "R1"
    episode = PrivateEpisode(
        public=PublicEpisode(
            protocol_version="nexus-0.3",
            episode_id=episode_id,
            description="Infer the coupled response network and calibrate its field controller. Read all evidence files.",
            rooms={
                f"R{i}": Room(
                    id=f"R{i}",
                    label="Laboratory"
                    if i == 0 and p == 0
                    else "Specimen stocks"
                    if i == 0
                    else "Laboratory"
                    if i == 1
                    else "Controller"
                    if i == p
                    else "Transit",
                )
                for i in range(p + 1)
            },
            edges=tuple((f"R{i}", f"R{i + 1}") for i in range(p)),
            phase_modulus=1,
            initial_state=WorldState(
                agent_room="R0",
                artifacts={},
                stocks=stocks,
                machines={
                    name: Machine(
                        id=name,
                        room_id=f"R{p}" if name == "controller" else bench_room,
                        uses_remaining=None if r == 0 else 128,
                    )
                    for name in ("meter", "shift", "shear", "controller")
                },
                resources=Resources(actions_remaining=None),
            ),
            goal=GoalPredicate(kind="controller_accepted"),
            investigation=spec,
        ),
        rules={},
        machine_rules={},
        verifier_secret=secret,
        construction_seed=seed,
        investigation_truth=truth,
    )
    with timed_stage("network.physical_witnesses") as metrics:
        representatives = ((mask & -mask).bit_length() - 1 for mask in problem.policy_leaf_masks)
        bound = (
            max(len(reference_plan(episode, worlds[i])) for i in representatives)
            if d
            else len(reference_plan(episode))
        )
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
