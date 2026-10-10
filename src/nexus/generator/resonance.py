"""Composed public-information witnesses without a Cartesian-product minimax search."""

from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
from functools import lru_cache
from itertools import product
from types import MappingProxyType

from nexus.diagnostics import timed_stage
from nexus.engine.network import response
from nexus.engine.resonance import RESONANT_BENCH, resonance, settings
from nexus.generator.network import compile_network, validate_profile
from nexus.generator.network_world import NetworkWitness, build_network_world
from nexus.generator.randomness import rng_for
from nexus.models.episode import GenerationMetadata, PrivateEpisode
from nexus.models.network import FIELD, NetworkSpec, NetworkTruth, ResonanceLaw
from nexus.solver.finite_experiments import FiniteExperimentProblem

LOG = logging.getLogger("nexus.generation")
CALIBRATION_WITNESS = ((0, 6), (6, 0))


@lru_cache(maxsize=1)
def calibration_prior() -> tuple[tuple[ResonanceLaw, ...], FiniteExperimentProblem]:
    worlds = tuple(
        ResonanceLaw(alpha=a, beta=b, gate=g)
        for a, b, g in product(range(1, 4), range(1, 4), range(3))
    )
    problem = FiniteExperimentProblem(
        tuple(map(str, range(len(worlds)))),
        tuple(
            (f"{x}:{y}", tuple(resonance(w, x, y) for w in worlds)) for x, y in CALIBRATION_WITNESS
        ),
        tuple(range(len(worlds))),
    )
    if problem.minimum_guaranteed_measurements() != 2:
        raise ValueError("resonance calibration must be identifiable in two measurements")
    return worlds, problem


def _stage_plan(
    episode: PrivateEpisode, truth: NetworkTruth, calibration: bool, offset: int = 0
) -> tuple[tuple[dict, ...], tuple[int, ...] | ResonanceLaw]:
    """Truth supplies observations only; all experiment choices use public posteriors."""
    if truth.resonance is None:
        raise ValueError("stage witness requires a resonance law")
    spec = episode.public.investigation
    h_worlds, h_problem = calibration_prior()
    g_worlds, g_problem = compile_network()
    problem = h_problem if calibration else g_problem
    observations = ()
    witness = NetworkWitness(episode, offset=offset)
    actions = witness.actions

    while (name := problem.best_experiment(observations)) is not None:
        x, y = map(int, name.split(":"))
        target = (x, y)
        specimen = witness.prepare(target)
        if not calibration:
            # The caller has inferred H before this stage; this is not a hidden-truth query.
            actions.append(
                {
                    "type": "configure",
                    "machine": "meter",
                    "settings": [resonance(truth.resonance, *target)],
                }
            )
        actions.append(
            {
                "type": "probe",
                "machine": "calibrator" if calibration else "meter",
                "artifact": specimen,
            }
        )
        value = resonance(truth.resonance, *target) if calibration else response(truth, *target)
        observations += ((name, value),)
    remaining = problem.compatible(observations)
    if calibration:
        if len(remaining) != 1:
            raise ValueError("calibration witness does not identify H")
        witness.move("R0")
        answer = h_worlds[remaining[0]]
    else:
        answer_set = {tuple(response(g_worlds[i], *p) for p in FIELD) for i in remaining}
        if len(answer_set) != 1:
            raise ValueError("response witness does not identify field predictions")
        answer = next(iter(answer_set))
        witness.move(spec.controller_room)
    return tuple(actions), answer


def reference_plan(episode: PrivateEpisode, truth: NetworkTruth | None = None) -> tuple[dict, ...]:
    truth = truth or episode.investigation_truth
    if not isinstance(truth, NetworkTruth) or truth.resonance is None:
        raise ValueError("reference policy requires resonant truth")
    spec = episode.public.investigation
    if spec.discovery == 0:
        belief = ResonantBelief(spec)
        answers = belief.target_vectors()
        if len(answers) != 1:
            raise ValueError("D0 evidence does not resolve its mission")
        answer = next(iter(answers))
        plan = tuple(
            {"type": "move", "target": f"R{i}"} for i in range(1, int(spec.controller_room[1:]) + 1)
        )
    else:
        prefix, inferred = _stage_plan(episode, truth, True)
        learned_truth = truth.model_copy(update={"resonance": inferred})
        suffix, fields = _stage_plan(episode, learned_truth, False, len(prefix))
        answer = (
            0,
            *((v + resonance(inferred, *p)) % 7 for v, p in zip(fields, FIELD, strict=True)),
        )
        plan = prefix + suffix
    return plan + (
        {"type": "configure", "machine": "controller", "settings": list(answer)},
        {"type": "finish"},
    )


@lru_cache(maxsize=12)
def policy_bound(discovery: int, planning: int) -> int:
    # Stage lengths do not depend on the other factor's values. Each returns to
    # a public stage boundary; adding their maxima is a uniform realizable bound.
    validate_profile(discovery, 3, planning, 0)
    if discovery == 0:
        return planning + 2
    h_worlds, _ = calibration_prior()
    g_worlds, g_problem = compile_network()
    if g_problem.minimum_guaranteed_measurements() != 5:
        raise ValueError("resonant response witness must retain its five-measurement bound")
    template = build_network_world(
        spec=NetworkSpec(
            version="resonant-network-v1",
            theory=3,
            discovery=discovery,
            controller_room=f"R{planning}",
        ),
        truth=g_worlds[0].model_copy(update={"resonance": h_worlds[0]}),
        planning=planning,
        pressure=0,
        seed=0,
        secret="bound-only",
        episode_id="bound-only",
        description="Policy witness template",
    )
    prefix = max(
        len(_stage_plan(template, g_worlds[0].model_copy(update={"resonance": h}), True)[0])
        for h in h_worlds
    )
    representatives = ((mask & -mask).bit_length() - 1 for mask in g_problem.policy_leaf_masks)
    suffix = max(
        len(
            _stage_plan(template, g_worlds[i].model_copy(update={"resonance": h_worlds[0]}), False)[
                0
            ]
        )
        for i in representatives
    )
    return prefix + suffix + 2


@lru_cache(maxsize=1)
def tables():
    """Immutable factor tables; never allocate the 59,049-world experiment product."""
    hs, _ = calibration_prior()
    gs, _ = compile_network()
    return (
        MappingProxyType({p: tuple(resonance(h, *p) for h in hs) for p in RESONANT_BENCH}),
        MappingProxyType({p: tuple(response(g, *p) for g in gs) for p in RESONANT_BENCH}),
        tuple(tuple(resonance(h, *p) for p in FIELD) for h in hs),
        tuple(tuple(response(g, *p) for p in FIELD) for g in gs),
    )


class ResonantBelief:
    """Exact product of scientific factors plus exclusions from joint goal feedback."""

    def __init__(self, spec: NetworkSpec):
        self.excluded: set[tuple[int, ...]] = set()
        self.resolved = spec.resolved_settings
        self.h_rows, self.g_rows, self.h_fields, self.g_fields = tables()
        self.h = set(range(len(self.h_fields)))
        self.g = set(range(len(self.g_fields)))
        for name, value in spec.supplied_measurements:
            kind, x, y = name.split(":")
            point = (int(x), int(y))
            if kind == "cal":
                self.h = {i for i in self.h if self.h_rows[point][i] == value}
            elif kind == "response":
                self.g = {i for i in self.g if self.g_rows[point][i] == value}
            else:
                raise ValueError("unknown supplied resonance measurement")

    def vector(self, h: int, g: int) -> tuple[int, ...]:
        return (0, *((a + b) % 7 for a, b in zip(self.h_fields[h], self.g_fields[g], strict=True)))

    def compatible_pairs(self):
        for h in self.h:
            for g in self.g:
                v = self.vector(h, g)
                if v not in self.excluded and (self.resolved is None or v == self.resolved):
                    yield h, g, v

    def target_vectors(self) -> set[tuple[int, ...]]:
        return {v for _, _, v in self.compatible_pairs()}

    def counts(self) -> tuple[int, int]:
        if not self.excluded and self.resolved is None:
            # Only field signatures need a cross product; equivalent worlds share a target.
            h_values = {self.h_fields[i] for i in self.h}
            g_values = {self.g_fields[i] for i in self.g}
            targets = {
                tuple((a + b) % 7 for a, b in zip(h, g, strict=True))
                for h in h_values
                for g in g_values
            }
            return len(self.h) * len(self.g), len(targets)
        pairs = tuple(self.compatible_pairs())
        return len(pairs), len({v for _, _, v in pairs})

    def measure(self, machine: str, sample: dict, setting: int | None = None):
        point = (sample["x"], sample["y"])
        if machine == "calibrator":
            self.h = {i for i in self.h if self.h_rows[point][i] == sample["reading"]}
        elif machine == "meter":
            signal = sample["signal"]
            self.h = {i for i in self.h if (self.h_rows[point][i] == setting) == signal}
            if signal:
                self.g = {i for i in self.g if self.g_rows[point][i] == sample["reading"]}
        else:
            raise ValueError("unknown scientific measurement")


def generate_resonant(
    seed: int,
    *,
    discovery_level: int,
    theory_level: int,
    planning_level: int,
    resource_pressure: int,
    verifier_secret: str | None = None,
) -> PrivateEpisode:
    d, t, p, r = discovery_level, theory_level, planning_level, resource_pressure
    validate_profile(d, t, p, r)
    with timed_stage("resonance.factor_prior") as metrics:
        hs, _ = calibration_prior()
        gs, _ = compile_network()
        law = hs[rng_for(seed, "resonant-network-v1").randrange(len(hs))]
        base_truth = gs[rng_for(seed, "coupled-network-v1").randrange(len(gs))]
        truth = base_truth.model_copy(update={"resonance": law})
        spec = NetworkSpec(
            version="resonant-network-v1", theory=t, discovery=d, controller_room=f"R{p}"
        )
        if d == 0:
            _, problem = compile_network()
            supplied = tuple((f"cal:{x}:{y}", resonance(law, x, y)) for x, y in CALIBRATION_WITNESS)
            supplied += tuple(
                (f"response:{name}", response(truth, *map(int, name.split(":"))))
                for name, _ in problem.experiments
            )
            spec = spec.model_copy(
                update={
                    "supplied_measurements": supplied,
                    "resolved_settings": settings(truth) if t == 0 else None,
                }
            )
        metrics["calibration_worlds"] = len(hs)
        metrics["joint_worlds"] = len(hs) * len(compile_network()[0])
    # Preserve the published identity encoding and paired G seed stream.
    secret = verifier_secret or secrets.token_hex(32)
    episode_id = hmac.new(
        secret.encode(),
        f"resonant-network-v1:{seed}:{d}:{t}:{p}:{r}".encode(),
        hashlib.sha256,
    ).hexdigest()[:24]
    episode = build_network_world(
        spec=spec,
        truth=truth,
        planning=p,
        pressure=r,
        seed=seed,
        secret=secret,
        episode_id=episode_id,
        description="Discover resonance and response laws, combine them to predict the field, and finish the mission. Read all evidence files.",
    )
    initial = episode.public.initial_state
    with timed_stage("resonance.composed_witness") as metrics:
        metrics["bound_cache_entries_before"] = policy_bound.cache_info().currsize
        bound = policy_bound(d, p)
        budget = None if r == 0 else bound + (8 if r == 1 else 0)
        initial.resources.actions_remaining = budget
        episode.reference_plan = reference_plan(episode)
        metrics["policy_action_bound"] = bound
        metrics["reference_actions"] = len(episode.reference_plan)
        if d and p == 1 and r == 1 and budget is not None and budget >= 92:
            raise ValueError("moderate profile must exclude complete coordinate sweeps")
    certificate = {
        "axis_version": 2,
        "family": "resonant-network-v1",
        "prior_worlds": 59049,
        "calibration_worlds": 27,
        "response_worlds": 2187,
        "target_classes": 2401,
        "bench_coordinates": 45,
        "meter_experiments": 315,
        "construction_required": d == 5,
        "calibration_measurement_bound": 0 if d == 0 else 2,
        "response_measurement_bound": 0 if d == 0 else 5,
        "measurement_lower_bound": 0 if d == 0 else 4,
        "measurement_policy_bound": 0 if d == 0 else 7,
        "constructive_policy_action_bound": bound,
        "action_budget": budget,
        "complete_coordinate_sweep_action_lower_bound": 92,
        "initial_measurements": len(spec.supplied_measurements),
        "certificate_scope": "composed public-information policy, not expanded-domain or joint minimax",
        "physical_policy_kind": "realizable upper bound, not physical minimax optimum",
    }
    episode.generation_metadata = GenerationMetadata(
        theory_level=t,
        discovery_level=d,
        planning_level=p,
        resource_pressure=r,
        scenario_family_id="resonant-network-v1",
        room_count=p + 1,
        machine_count=5,
        optimal_action_count=p + 2,
        # At most8 outcomes per experiment; 8**3 < 2401 target classes.
        # This is a lower bound, not an exact joint minimum.
        required_probe_count=0 if d == 0 else 4,
        guaranteed_policy_action_count=bound,
        action_budget=budget or 0,
        recommended_tool_call_limit=bound + 20,
        investigation_certificate=certificate,
    )
    with timed_stage("resonance.public_evidence"):
        from nexus.generator.resonance_docs import evidence_files

        episode.public.evidence_files = evidence_files(episode)
    LOG.info(
        "resonance_generated D=%s T=%s P=%s R=%s factors=27x2187 bench=45 policy_bound=%s budget=%s",
        d,
        t,
        p,
        r,
        bound,
        budget,
    )
    return episode
