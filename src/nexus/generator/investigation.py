"""Versioned integrated scientific investigations with exact finite-prior certificates."""

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

from nexus.engine.investigation import measurement, settings
from nexus.generator.randomness import rng_for
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalPredicate
from nexus.models.investigation import (
    InvestigationSpec,
    InvestigationTruth,
    ScalarExpression,
    SpecimenStock,
)
from nexus.models.world import Machine, Resources, Room, WorldState
from nexus.solver.finite_experiments import FiniteExperimentProblem

LOG = logging.getLogger("nexus.generation")


def validate_profile(d: int, t: int, p: int, r: int) -> None:
    if d not in range(6) or t not in range(4) or p not in range(4) or r not in range(3):
        raise ValueError("axes-v2 requires D0..5/T0..3/P0..3/R0..2")
    if t == 0 and d != 0:
        raise ValueError("axes-v2 T0 is a resolved control and supports D0 only")
    if d == 1 and t != 1:
        raise ValueError("axes-v2 D1 currently supports T1 only; use D2+ for correction/structure")


@lru_cache(maxsize=48)
def response_expression(scale: int, exponent: int) -> ScalarExpression:
    def var(name):
        return ScalarExpression(op="variable", value=name)

    def const(value):
        return ScalarExpression(op="constant", value=value)

    def op(name, left, right):
        return ScalarExpression(op=name, children=(left, right))

    q = var("q")
    baseline = op("multiply", var("a"), op("multiply", q, op("add", q, const(-1))))
    correction = op("multiply", var("c"), op("power", q, const(exponent)))
    return op("multiply", const(scale), op("add", baseline, correction))


def make_spec(d: int, t: int, scale: int, controller_room: str) -> InvestigationSpec:
    return InvestigationSpec(
        theory=t,
        discovery=d,
        scale=scale,
        known_selector=None if d >= 4 else 0,
        known_coefficient=1 if t <= 1 else None,
        known_exponent=1 if t <= 2 else None,
        offset_unknown=d not in (1, 2),
        both_stocks=d == 2,
        material_meter=d == 2,
        preparation_required=d == 5,
        controller_room=controller_room,
    )


@lru_cache(maxsize=64)
def compile_problem(
    spec: InvestigationSpec,
) -> tuple[tuple[InvestigationTruth, ...], FiniteExperimentProblem]:
    """All worlds admitted by public theory; no filtering by hidden truth or mission success."""
    worlds = tuple(
        InvestigationTruth(
            selector=s,
            properties=(a0, a1),
            offset=b,
            coefficient=c,
            exponent=r,
            response=response_expression(spec.scale, r),
        )
        for s, a0, a1, b, c, r in product(
            (0, 1) if spec.known_selector is None else (spec.known_selector,),
            range(4),
            range(4),
            (0, 2) if spec.offset_unknown else (0,),
            (1, 2, 3) if spec.known_coefficient is None else (spec.known_coefficient,),
            (1, 2, 3) if spec.known_exponent is None else (spec.known_exponent,),
        )
    )
    names = ["selector"] if spec.known_selector is None else []
    names += [f"{source}:{q}" for source in ("reference", "0", "1") for q in range(3)]
    if spec.material_meter:
        names += ["0:property", "1:property"]
    rows = tuple(
        (name, tuple(measurement(spec, world, name) for world in worlds)) for name in names
    )
    answers = tuple(settings(spec, world) for world in worlds)
    labels = {answer: i for i, answer in enumerate(dict.fromkeys(answers))}
    problem = FiniteExperimentProblem(
        tuple(str(i) for i in range(len(worlds))), rows, tuple(labels[answer] for answer in answers)
    )
    return worlds, problem


def base_spec(spec: InvestigationSpec) -> InvestigationSpec:
    # Public evidence affects posterior, not the admitted theory. Physical room is irrelevant.
    return spec.model_copy(
        update={"supplied_measurements": (), "resolved_settings": None, "controller_room": ""}
    )


def prior(episode: PrivateEpisode):
    from nexus.models.network import NetworkSpec
    if isinstance(episode.public.investigation, NetworkSpec):
        if episode.public.investigation.version == "resonant-network-v1":
            raise ValueError("resonant worlds use the exact ResonantBelief factor posterior")
        from nexus.generator.network import compile_network
        return compile_network(3)
    return compile_problem(base_spec(episode.public.investigation))


def reference_plan(
    episode: PrivateEpisode, truth: InvestigationTruth | None = None
) -> tuple[dict, ...]:
    """Realizable public-information policy, with physical bookkeeping outside minimax."""
    spec = episode.public.investigation
    truth = truth or episode.investigation_truth
    worlds, problem = prior(episode)
    observations = spec.supplied_measurements
    plan: list[dict] = []
    room = episode.public.initial_state.agent_room
    samples: dict[tuple[str, int], str] = {}
    stocks = episode.public.initial_state.stocks
    machines = episode.public.initial_state.machines

    def move(destination):
        nonlocal room
        # v2 topology is a disclosed chain; no hidden-map oracle or physical search.
        while room != destination:
            index, target = int(room[1:]), int(destination[1:])
            room = f"R{index + (1 if target > index else -1)}"
            plan.append({"type": "move", "target": room})

    while spec.resolved_settings is None:
        name = problem.best_experiment(observations)
        if name is None:
            break
        source, context = ("reference", "selector") if name == "selector" else name.split(":")
        q = int(context) if context.isdigit() else 0
        machine = {"selector": "selector", "property": "material"}.get(context, "meter")
        key = (source, q)
        if key not in samples:
            stock = next(
                stock
                for stock in stocks.values()
                if stock.source == source and stock.q == (0 if spec.preparation_required else q)
            )
            move(stock.location)
            plan.append({"type": "take", "artifact": stock.id})
            artifact = f"{stock.id}.{len(plan)}"
            if spec.preparation_required:
                move(machines["prepare"].room_id)
                for _ in range(q):
                    plan.append({"type": "operate", "machine": "prepare", "artifact": artifact})
            samples[key] = artifact
        move(machines[machine].room_id)
        plan.append({"type": "probe", "machine": machine, "artifact": samples[key]})
        observations += ((name, measurement(spec, truth, name)),)
    if spec.resolved_settings is not None:
        answer = spec.resolved_settings
    else:
        candidates = problem.compatible(observations)
        answers = {settings(spec, worlds[i]) for i in candidates}
        if len(answers) != 1:
            raise ValueError("scientific reference policy did not identify controller settings")
        answer = next(iter(answers))
    move(spec.controller_room)
    plan.extend(
        (
            {"type": "configure", "machine": "controller", "settings": list(answer)},
            {"type": "finish"},
        )
    )
    return tuple(plan)


@lru_cache(maxsize=64)
def information_certificate(spec: InvestigationSpec) -> dict[str, object]:
    worlds, problem = compile_problem(spec)
    minimum = problem.minimum_guaranteed_measurements()
    fixed = problem.minimum_fixed_measurements()
    expected = 1 if spec.discovery == 1 else spec.theory + 1 + int(spec.discovery >= 4)
    if spec.discovery > 0 and minimum != expected:
        raise ValueError(f"profile information guarantee failed: {minimum} != {expected}")
    if spec.discovery >= 4 and fixed != minimum + 1:
        raise ValueError("adaptive experiment advantage was not established")
    raw = FiniteExperimentProblem(
        problem.hypotheses,
        tuple((name, row) for name, row in problem.experiments if not name.endswith(":2")),
        problem.predictions,
    )
    construction = raw.minimum_guaranteed_measurements() is None
    if spec.preparation_required and not construction:
        raise ValueError("raw measurements bypass specimen preparation")
    counts = Counter(problem.predictions)
    return {
        "axis_version": 2,
        "family": "shared-response-v1",
        "prior_worlds": len(worlds),
        "target_classes": len(counts),
        "minimum_measurements": minimum,
        "fixed_measurements": fixed,
        "adaptive_gap": fixed - minimum,
        "construction_required": spec.preparation_required and construction,
        "best_prior_guess_probability": max(counts.values()) / len(worlds),
        "exhaustive_guess_submissions": len(counts),
        "certificate_scope": "scientific inference before controller feedback",
        "physical_policy_kind": "realizable upper bound, not physical minimax optimum",
    }


def generate_investigation(
    seed: int,
    *,
    discovery_level: int,
    planning_level: int,
    resource_pressure: int,
    theory_level: int,
    verifier_secret: str | None = None,
) -> PrivateEpisode:
    start = perf_counter()
    d, p, r, t = discovery_level, planning_level, resource_pressure, theory_level
    validate_profile(d, t, p, r)
    rng = rng_for(seed, "scientific-v2-shared-response-v1")
    scale = rng.randrange(1, 17)
    room_count = p + 1
    controller_room = f"R{room_count - 1}"
    spec = make_spec(d, t, scale, controller_room)
    worlds, problem = compile_problem(base_spec(spec))
    truth = worlds[rng.randrange(len(worlds))]
    secret = verifier_secret or secrets.token_hex(32)
    # A fixed verifier secret makes seeded artifacts/receipts reproducible without
    # exposing a dictionary-checkable seed hash in the player-visible identifier.
    episode_id = hmac.new(
        secret.encode(), json.dumps(["scientific-v2", seed, d, t, p, r]).encode(), hashlib.sha256
    ).hexdigest()[:24]
    certificate = dict(information_certificate(base_spec(spec)))
    if d == 0:
        supplied = tuple((name, measurement(spec, truth, name)) for name, _ in problem.experiments)
        spec = spec.model_copy(
            update={
                "supplied_measurements": supplied,
                "resolved_settings": settings(spec, truth) if t == 0 else None,
            }
        )
        certificate.update(
            minimum_measurements=0,
            fixed_measurements=0,
            adaptive_gap=0,
            target_classes_after_evidence=1,
        )
    bench_room = "R0" if p == 0 else "R1"
    stocks = {
        f"S{source}-{q}": SpecimenStock(
            id=f"S{source}-{q}", location="R0", source=source, q=q, remaining=None if r == 0 else 4
        )
        for source in ("reference", "0", "1")
        for q in ((0,) if d == 5 else (0, 1, 2))
    }
    machine_ids = ["meter", "prepare", "controller"]
    if spec.known_selector is None:
        machine_ids.append("selector")
    if spec.material_meter:
        machine_ids.append("material")
    public = PublicEpisode(
        protocol_version="nexus-0.3",
        episode_id=episode_id,
        description="Calibrate the facility controller for its field conditions using the specimen laboratory. Read manual.md and theory.json.",
        rooms={
            f"R{i}": Room(
                id=f"R{i}",
                label=(
                    "Specimen stocks"
                    if i == 0
                    else "Laboratory"
                    if i == 1
                    else "Controller"
                    if i == room_count - 1
                    else "Transit"
                ),
            )
            for i in range(room_count)
        },
        edges=tuple((f"R{i}", f"R{i + 1}") for i in range(room_count - 1)),
        phase_modulus=1,
        initial_state=WorldState(
            agent_room="R0",
            artifacts={},
            stocks=stocks,
            machines={
                name: Machine(
                    id=name,
                    room_id=controller_room if name == "controller" else bench_room,
                    uses_remaining=None if r == 0 else 32,
                )
                for name in machine_ids
            },
            resources=Resources(actions_remaining=None),
        ),
        goal=GoalPredicate(kind="controller_accepted"),
        investigation=spec,
    )
    episode = PrivateEpisode(
        public=public,
        rules={},
        machine_rules={},
        verifier_secret=secret,
        construction_seed=seed,
        investigation_truth=truth,
    )
    # Policy upper bound includes movement, taking, construction, configuration and finish.
    # The finite truth family is independent of P/R. No physical BFS over infinite R0 copies.
    representatives = tuple((mask & -mask).bit_length() - 1 for mask in problem.policy_leaf_masks)
    max_actions = (
        max(len(reference_plan(episode, worlds[i])) for i in representatives)
        if d
        else len(reference_plan(episode))
    )
    budget = None if r == 0 else max_actions + (8 if r == 1 else 0)
    episode.public.initial_state.resources.actions_remaining = budget
    episode.reference_plan = reference_plan(episode)
    certificate.update(
        constructive_policy_action_bound=max_actions,
        action_budget=budget,
        initial_measurements=len(spec.supplied_measurements),
    )
    episode.generation_metadata = GenerationMetadata(
        theory_level=t,
        discovery_level=d,
        planning_level=p,
        resource_pressure=r,
        scenario_family_id="shared-response-v1",
        room_count=room_count,
        machine_count=len(machine_ids),
        optimal_action_count=p + 2,
        action_budget=budget or 0,
        required_probe_count=certificate["minimum_measurements"],
        guaranteed_policy_action_count=max_actions,
        recommended_tool_call_limit=max_actions + 12,
        investigation_certificate=certificate,
    )
    from nexus.generator.investigation_docs import evidence_files

    episode.public.evidence_files = evidence_files(episode)
    LOG.info(
        "investigation_generated axis_version=2 D=%s T=%s P=%s R=%s prior=%s measurements=%s fixed=%s policy_bound=%s total_seconds=%.6f",
        d,
        t,
        p,
        r,
        len(worlds),
        certificate["minimum_measurements"],
        certificate["fixed_measurements"],
        max_actions,
        perf_counter() - start,
    )
    return episode
