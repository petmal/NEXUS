#!/usr/bin/env python3
"""Bounded T2 effective-theory proof of concept; not a production difficulty profile.

Only reports are emitted. No unqualified episode is exported for benchmark scoring.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import time

from nexus.engine.canonical import canonical_hash
from nexus.engine.rules import apply_effect
from nexus.generator.discovery import analyze_discovery
from nexus.generator.evidence import Experiment, evidence_csv, candidates_matching_csv
from nexus.generator.generator import _random_tree, _role_rooms
from nexus.generator.randomness import rng_for
from nexus.models.episode import PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import Artifact, Machine, Orientation, Pattern, Polarity, Resources, Shape, WorldState
from nexus.solver.belief import _episode_for_hypothesis, solve_compressed_physical, solve_guaranteed_policy


from nexus.generator.correction import CorrectionPrior, prove_domain

def build_case(seed):
    rng = rng_for(seed, "t2-correction-poc-v1")
    spec = CorrectionPrior(effective_add=rng.choice((1, 2, 3)))
    rooms, edges = _random_tree(rng, 9)
    start, machines, destination, _ = _role_rooms(rooms, edges, machine_count=1)
    item = Artifact(id="A1", location=start, shape=rng.choice(tuple(Shape)),
                    pattern=rng.choice(tuple(Pattern)), value=rng.randrange(11),
                    orientation=rng.choice(tuple(Orientation)), polarity=rng.choice(tuple(Polarity)))
    goal = GoalPredicate(kind=GoalKind.AND, children=(
        GoalPredicate(kind=GoalKind.ARTIFACT_FIELD, artifact_id="A1", field="value",
                      value=(item.value + spec.effective_add + 1) % spec.modulus),
        GoalPredicate(kind=GoalKind.ARTIFACT_LOCATION, artifact_id="A1", value=destination),
    ))
    laws = spec.hypotheses()
    evidence = evidence_csv(laws[0], tuple(Experiment(phase=phase, artifact=item)
                                          for phase in spec.validity_phases))
    world = PrivateEpisode(
        public=PublicEpisode(episode_id=canonical_hash([spec.family, seed])[:16],
                             description="Research fixture: test the limits of an effective theory.",
                             rooms=rooms, edges=edges, phase_modulus=4, goal=goal,
                             initial_state=WorldState(phase=0, agent_room=start, artifacts={"A1": item},
                                 machines={"M1": Machine(id="M1", room_id=machines[0], uses_remaining=1)},
                                 resources=Resources(actions_remaining=96)),
                             evidence_files={"facility_manual.txt": spec.manual(),
                                             "theory.json": spec.public_json(), "measurements.csv": evidence}),
        rules={"law": laws[0]}, machine_rules={"M1": "law"}, verifier_secret="t2-poc-only",
        construction_seed=seed,
    )
    candidates = candidates_matching_csv(evidence, laws)
    assert candidates == laws
    viable = []
    for rule in candidates:
        candidate = _episode_for_hypothesis(world, {"M1": rule}, search_budget=96)
        result = solve_compressed_physical(candidate, include_plan=False)
        assert not result.exhausted_state_limit
        if result.solvable:
            viable.append(rule)
    assert len(viable) == 5
    world.rules["law"] = rng.choice(viable)
    return spec, world, candidates


def run_case(seed):
    from profile_theory import replay_policy
    started = time.perf_counter()
    spec, world, candidates = build_case(seed)
    target = world.public.initial_state.artifacts["A1"].model_copy(update={"value": world.public.goal.children[0].value})
    analysis = analyze_discovery(candidate_rules_by_machine={"M1": candidates},
                                 initial_artifact=world.public.initial_state.artifacts["A1"],
                                 target_artifact=target, phase_modulus=4)
    assert analysis.minimum_guaranteed_probes == 1
    policy = solve_guaranteed_policy(world, candidate_rules_by_machine={"M1": candidates},
                                    max_actions=96, include_action_values=False)
    assert policy.solvable and policy.witness is not None
    assert policy.viable_hypothesis_count == 5
    world.generation_metadata.guaranteed_policy_witness = policy.witness.model_dump(mode="json")
    world.generation_metadata.guaranteed_policy_action_count = policy.optimal_worst_case_actions
    world.generation_metadata.viable_causal_hypotheses = policy.viable_hypothesis_count
    world.public.initial_state.resources.actions_remaining = policy.optimal_worst_case_actions
    replayed = replay_policy(world, {"M1": candidates})
    assert replayed == policy.viable_hypothesis_count == 5
    effective_world = _episode_for_hypothesis(world, {"M1": spec.effective()}, search_budget=96)
    ignored = solve_compressed_physical(effective_world, include_plan=False)
    assert not ignored.solvable and not ignored.exhausted_state_limit
    return dict(seed=seed, status="ok", family=spec.family, public_prior=asdict(spec),
                full_candidates=len(candidates), viable_candidates=5,
                minimum_guaranteed_probes=analysis.minimum_guaranteed_probes,
                exact_actions=policy.optimal_worst_case_actions, replayed=replayed,
                effective_model_alone_solvable=False, seconds=time.perf_counter() - started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 17, 2525])
    parser.add_argument("--out", type=Path, default=Path("docs/profiling/t2-correction-poc"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(Path(__file__).read_bytes())
    root = Path(__file__).resolve().parents[1]
    for path in sorted((root / "src").rglob("*.py")) + [root / "scripts/profile_theory.py", root / "uv.lock"]:
        digest.update(path.read_bytes())
    digest.update(platform.python_version().encode())
    fingerprint = digest.hexdigest()
    # Exhaustive validity/invariance check once for each effective-model choice.
    checks = sum(prove_domain(CorrectionPrior(effective_add=amount)) for amount in (1, 2, 3))
    for seed in args.seeds:
        path = args.out / f"seed-{seed}.json"
        if path.exists() and json.loads(path.read_text()).get("code") == fingerprint:
            continue
        result = run_case(seed)
        result.update(code=fingerprint, python=platform.python_version(), exhaustive_domain_checks=checks)
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(result, indent=2) + "\n")
        temp.replace(path)
        print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
