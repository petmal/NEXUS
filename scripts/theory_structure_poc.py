#!/usr/bin/env python3
"""T3 research only: factor a complete context-cell prior, then check an exhaustive oracle.

No T3 episode is exported or accepted by the production generator. This proves a
reachable-context quotient for a shape-invariant single-artifact fixture, not a
general symbolic solver for arbitrary interacting artifacts.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from itertools import product
import json
from math import prod
from pathlib import Path
import platform
import subprocess
import sys
import time

from nexus.engine.canonical import canonical_hash
from nexus.engine.rules import apply_effect
from nexus.generator.discovery import analyze_discovery
from nexus.generator.evidence import Experiment, candidates_matching_csv, evidence_csv
from nexus.generator.generator import _random_tree, _role_rooms
from nexus.generator.randomness import rng_for
from nexus.models.episode import PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.rules import Condition, ConditionKind, Effect, EffectKind
from nexus.models.world import Artifact, Machine, Orientation, Pattern, Polarity, Resources, Shape, WorldState
from nexus.solver.belief import solve_guaranteed_policy

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CellPrior:
    cells: tuple[tuple[Shape, int], ...] = tuple(product(Shape, (0, 1)))
    domains: tuple[tuple[int, ...], ...] = ((1, 2, 3),) * 6

    def __post_init__(self):
        if self.cells != tuple(product(Shape, (0, 1))) or len(self.domains) != 6:
            raise ValueError("unsupported cell partition")
        if any(not domain or len(set(domain)) != len(domain)
               or any(type(a) is not int or a not in (1, 2, 3) for a in domain)
               for domain in self.domains):
            raise ValueError("invalid bounded effect domain")

    @property
    def cardinality(self):
        return prod(map(len, self.domains))

    def observe(self, item, phase, output):
        index = self.cells.index((item.shape, phase % 2))
        domains = list(self.domains)
        domains[index] = tuple(a for a in domains[index] if (item.value + a) % 11 == output.value)
        if not domains[index]:
            raise ValueError("measurement contradicts the public cell prior")
        if any(getattr(item, f) != getattr(output, f) for f in ("shape", "pattern", "orientation", "polarity")):
            raise ValueError("measurement violates public invariants")
        return CellPrior(self.cells, tuple(domains))

    def law(self, choices):
        if len(choices) != len(self.cells) or any(a not in d for a, d in zip(choices, self.domains, strict=True)):
            raise ValueError("law choices outside disclosed domains")
        return Effect(kind=EffectKind.SEQUENCE, effects=tuple(
            Effect(kind=EffectKind.CONDITIONAL,
                   condition=Condition(kind=ConditionKind.AND, children=(
                       Condition(kind=ConditionKind.EQUALS, field="shape", value=shape.value),
                       Condition(kind=ConditionKind.PHASE_PARITY, parity="even" if parity == 0 else "odd"),
                   )),
                   effects=(Effect(kind=EffectKind.ADD_MOD, field="value", amount=amount, modulus=11),))
            for (shape, parity), amount in zip(self.cells, choices, strict=True)
        ))

    def full_laws(self):
        return [self.law(choices) for choices in product(*self.domains)]

    def project(self, world):
        """All legal future inputs retain A1's shape; quotient the unreachable cells exactly."""
        artifacts = world.public.initial_state.artifacts
        if set(artifacts) != {"A1"} or set(world.machine_rules) != {"M1"}:
            raise ValueError("PoC projection requires one artifact and one machine")
        shape = artifacts["A1"].shape
        indices = tuple(i for i, cell in enumerate(self.cells) if cell[0] == shape)
        multiplicity = prod(len(domain) for i, domain in enumerate(self.domains) if i not in indices)
        representatives = []
        for values in product(*(self.domains[i] for i in indices)):
            choices = [domain[0] for domain in self.domains]
            for i, value in zip(indices, values, strict=True):
                choices[i] = value
            representatives.append(self.law(choices))
        assert len(representatives) * multiplicity == self.cardinality
        return representatives, multiplicity

    def public_json(self):
        return json.dumps({
            "family": "t3-independent-shape-parity-cells-poc-v1",
            "deterministic": True, "stationary": True, "memoryless": True,
            "context": ["shape", "phase_parity"], "independent_cells": True,
            "cells": [{"shape": s.value, "parity": p, "add_choices": list(d)}
                      for (s, p), d in zip(self.cells, self.domains, strict=True)],
            "modulus": 11, "invariant_fields": ["shape", "pattern", "orientation", "polarity"],
        }, indent=2, sort_keys=True)


def build_case(seed):
    rng = rng_for(seed, "t3-independent-cells-poc-v1")
    prior = CellPrior()
    rooms, edges = _random_tree(rng, 5)
    artifact_room, machines, destination, _ = _role_rooms(rooms, edges, machine_count=1)
    item = Artifact(id="A1", location=artifact_room, shape=rng.choice(tuple(Shape)),
                    pattern=rng.choice(tuple(Pattern)), value=rng.randrange(11),
                    orientation=rng.choice(tuple(Orientation)), polarity=rng.choice(tuple(Polarity)))
    choices = [rng.choice(domain) for domain in prior.domains]
    relevant = [i for i, cell in enumerate(prior.cells) if cell[0] == item.shape]
    viable = [pair for pair in product((1, 2, 3), repeat=2) if 2 in pair]
    for i, amount in zip(relevant, rng.choice(viable), strict=True):
        choices[i] = amount
    truth = prior.law(choices)
    calibration_shape = next(shape for shape in Shape if shape != item.shape)
    calibration = item.model_copy(update={"shape": calibration_shape})
    measurement = Experiment(phase=0, artifact=calibration)
    observed = apply_effect(truth, calibration, 0)
    belief = prior.observe(calibration, 0, observed)
    world = PrivateEpisode(
        public=PublicEpisode(
            episode_id=canonical_hash(["t3-poc", seed])[:16],
            description="Research fixture: construct an empirical model and deliver A1.",
            rooms=rooms, edges=edges,
            initial_state=WorldState(agent_room="R0", phase=0, artifacts={"A1": item},
                machines={"M1": Machine(id="M1", room_id=machines[0], uses_remaining=1)},
                resources=Resources(actions_remaining=96)),
            goal=GoalPredicate(kind=GoalKind.AND, children=(
                GoalPredicate(kind=GoalKind.ARTIFACT_FIELD, artifact_id="A1", field="value", value=(item.value + 2) % 11),
                GoalPredicate(kind=GoalKind.ARTIFACT_LOCATION, artifact_id="A1", value=destination),
            )), evidence_files={
                "theory.json": prior.public_json(), "measurements.csv": evidence_csv(truth, (measurement,)),
                "facility_manual.txt": "T3 RESEARCH. Each shape/parity cell independently selects one fixed additive value shift modulo 11 from its disclosed choices. No cross-cell formula or correlation is promised. All other fields are invariant; no identity, room, turn or history dependence exists. Measurements are truthful; the actual mission is physically solvable.\n" + prior.public_json(),
            },
        ), rules={"law": truth}, machine_rules={"M1": "law"}, verifier_secret="t3-poc-only", construction_seed=seed,
    )
    return prior, belief, world


def run_case(seed):
    from profile_theory import replay_policy
    prior, belief, world = build_case(seed)
    started = time.perf_counter()
    reduced, multiplicity = belief.project(world)
    item = world.public.initial_state.artifacts["A1"]
    discovery = analyze_discovery(candidate_rules_by_machine={"M1": reduced},
                                 initial_artifact=item,
                                 target_artifact=item.model_copy(update={"value": (item.value + 2) % 11}),
                                 phase_modulus=4)
    assert discovery.minimum_guaranteed_probes == 1
    compressed = solve_guaranteed_policy(world, candidate_rules_by_machine={"M1": reduced},
                                        max_actions=96, include_action_values=False)
    reduced_seconds = time.perf_counter() - started
    # Oracle is bounded at 243 laws after one truthful calibration; production limits unchanged.
    started = time.perf_counter()
    full = candidates_matching_csv(world.public.evidence_files["measurements.csv"], prior.full_laws())
    assert full == belief.full_laws()
    assert world.rules["law"] in full
    oracle = solve_guaranteed_policy(world, candidate_rules_by_machine={"M1": full},
                                    max_actions=96, include_action_values=False)
    oracle_seconds = time.perf_counter() - started
    assert compressed.solvable and oracle.solvable
    assert compressed.optimal_worst_case_actions == oracle.optimal_worst_case_actions
    assert oracle.viable_hypothesis_count == compressed.viable_hypothesis_count * multiplicity
    # Check complete reachable value/phase behavior against one representative of every full law.
    item = world.public.initial_state.artifacts["A1"]
    signatures = {}
    def signature(law):
        return tuple(apply_effect(law, item.model_copy(update={"value": value}), phase).model_dump_json()
                     for value, phase in product(range(11), range(4)))
    for law in reduced:
        signatures[signature(law)] = 0
    for law in full:
        signatures[signature(law)] += 1
    assert set(signatures.values()) == {multiplicity}
    world.generation_metadata.guaranteed_policy_action_count = compressed.optimal_worst_case_actions
    world.generation_metadata.guaranteed_policy_witness = compressed.witness.model_dump(mode="json")
    world.generation_metadata.viable_causal_hypotheses = compressed.viable_hypothesis_count
    reduced_replays = replay_policy(world, {"M1": reduced})
    # Replay the factored witness under every complete viable law, not just representatives.
    world.generation_metadata.viable_causal_hypotheses = oracle.viable_hypothesis_count
    full_replays = replay_policy(world, {"M1": full})
    return dict(status="ok", seed=seed, full_prior=prior.cardinality,
                after_evidence=belief.cardinality, reachable_classes=len(reduced),
                multiplicity=multiplicity, viable_full=oracle.viable_hypothesis_count,
                reduced_replays=reduced_replays, full_replays=full_replays,
                exact_actions=compressed.optimal_worst_case_actions,
                minimum_guaranteed_probes=discovery.minimum_guaranteed_probes,
                reachable_domain_comparisons=len(full) * 11 * 4,
                reduced_seconds=reduced_seconds, oracle_seconds=oracle_seconds,
                limitation="One shape-invariant artifact; no claim of greater model difficulty or a general symbolic solver.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 17, 2525])
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--out", type=Path, default=ROOT / "docs/profiling/t3-structural-poc")
    args = parser.parse_args()
    if args.case is not None:
        print(json.dumps(run_case(args.case)))
        return 0
    digest = hashlib.sha256()
    for path in sorted((ROOT / "src").rglob("*.py")) + [Path(__file__), ROOT / "scripts/profile_theory.py", ROOT / "uv.lock"]:
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(path.read_bytes())
    digest.update(platform.python_version().encode())
    fingerprint = digest.hexdigest()
    args.out.mkdir(parents=True, exist_ok=True)
    failed = False
    for seed in args.seeds:
        path = args.out / f"seed-{seed}.json"
        if path.exists():
            old = json.loads(path.read_text())
            if old.get("code") == fingerprint and old.get("status") == "ok":
                continue
        try:
            result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--case", str(seed)],
                                    text=True, capture_output=True, timeout=args.timeout, check=True)
            report = json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            report = {"status": "timeout", "seed": seed}
        except subprocess.CalledProcessError as exc:
            report = {"status": "error", "seed": seed, "stderr": exc.stderr[-4000:]}
        report.update(code=fingerprint, python=platform.python_version())
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(report, indent=2) + "\n")
        temp.replace(path)
        failed |= report["status"] != "ok"
        print(json.dumps(report), flush=True)
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
