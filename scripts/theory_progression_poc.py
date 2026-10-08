#!/usr/bin/env python3
"""Prove a bounded T1→T2→T3 information dependency and held-out prediction task."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import platform

from nexus.generator.randomness import rng_for
from nexus.models.theory import TheoryProgression, TheoryStage
from nexus.solver.finite_experiments import FiniteExperimentProblem

if not __debug__:
    raise RuntimeError("Proof execution requires Python assertions; do not use -O or PYTHONOPTIMIZE")

ROOT = Path(__file__).resolve().parents[1]


def build_case(seed: int):
    rng = rng_for(seed, "cumulative-theory-poc-v1")
    modulus = 11
    scale, offset = rng.choice((2, 3, 4)), rng.randrange(1, 5)
    corrections = rng.choice(tuple(combinations((1, 2, 3), 2)))
    observed_x = rng.randrange(5)
    # The response at this context has an alias between correction and operator.
    shift = (-2 * scale * observed_x - sum(corrections)) % modulus
    hypotheses = tuple(product(corrections, ("add", "negate")))
    def corrected(x, c):
        # T1: composition of supplied a=x+offset, b=scale*a, q=b-scale*offset.
        return (scale * (x + offset) - scale * offset + c) % modulus
    def response(x, c, law):
        u = corrected(x, c)
        return (u + shift if law == "add" else -u) % modulus
    targets = [x for x in range(modulus) if x != observed_x
               and len({response(x, *h) for h in hypotheses}) == len(hypotheses)]
    target_x = rng.choice(targets)
    predictions = tuple(response(target_x, *h) for h in hypotheses)
    calibration = tuple(corrected(0, c) for c, _ in hypotheses)
    coupled = tuple(response(observed_x, *h) for h in hypotheses)
    # Matched independent control: assay the unknown law with a disclosed input u.
    known_inputs = [u for u in range(modulus) if (u + shift) % modulus != (-u) % modulus]
    known_u = rng.choice(known_inputs)
    independent = tuple((known_u + shift if law == "add" else -known_u) % modulus
                        for _, law in hypotheses)
    names = tuple(f"c={c};law={law}" for c, law in hypotheses)
    problem = FiniteExperimentProblem(names, (("calibration", calibration), ("relationship", coupled)), predictions)
    control = FiniteExperimentProblem(names, (("calibration", calibration), ("relationship", independent)), predictions)
    progression = TheoryProgression(stages=(
        TheoryStage(id="derive", theory_level=1, description="Compose the exact supplied laws to derive q(x)."),
        TheoryStage(id="correct", theory_level=2, requires=("derive",), description="Infer c in u=q+c from calibration."),
        TheoryStage(id="discover", theory_level=3, requires=("correct",), description="Infer the missing operator on corrected u."),
    ), prediction_stage="discover")
    public = dict(family="cumulative-theory-poc-v1", modulus=modulus,
        progression=progression.model_dump(mode="json"),
        exact_laws=dict(a=f"x+{offset}", b=f"{scale}*a", q=f"b-{scale}*{offset}"),
        corrected_law="u=q+c", correction_choices=list(corrections),
        missing_relationship=dict(dependency="u", choices=[f"u+{shift}", "-u"]),
        available_experiments=dict(calibration="measure u at x=0", relationship=f"measure y at x={observed_x}"),
        prediction=dict(quantity="y", x=target_x),
        independent_control=dict(relationship_input_u=known_u),
        note="All arithmetic is modulo 11. No experiment at the prediction context is available.")
    return public, problem, control


def run_case(seed: int):
    public, problem, control = build_case(seed)
    rows = dict(problem.experiments)
    proofs = []
    for truth in range(len(problem.hypotheses)):
        calibration = (("calibration", rows["calibration"][truth]),)
        relationship = (("relationship", rows["relationship"][truth]),)
        both = calibration + relationship
        posterior = problem.compatible(both)
        assert posterior == (truth,)
        assert len(problem.possible_predictions(calibration)) == 2
        assert len(problem.possible_predictions(relationship)) == 2
        # Without c the relationship identity itself is ambiguous, not just the final value.
        assert len({problem.hypotheses[i].split("law=")[1] for i in problem.compatible(relationship)}) == 2
        assert len({control.hypotheses[i].split("law=")[1] for i in control.compatible(
            (("relationship", dict(control.experiments)["relationship"][truth]),))}) == 1
        wrong_c = next(value for value in set(rows["calibration"]) if value != rows["calibration"][truth])
        wrong = problem.possible_predictions((("calibration", wrong_c),) + relationship)
        assert problem.predictions[truth] not in wrong
        assert problem.minimum_guaranteed_measurements(calibration) == 1
        proofs.append(dict(truth=truth, posterior=list(posterior),
                          missing_c_predictions=sorted(problem.possible_predictions(relationship)),
                          missing_relationship_predictions=sorted(problem.possible_predictions(calibration)),
                          wrong_c_predictions=sorted(wrong)))
    coupled_cost = problem.minimum_guaranteed_measurements()
    independent_cost = control.minimum_guaranteed_measurements()
    assert coupled_cost == independent_cost == 2
    bypass = FiniteExperimentProblem(problem.hypotheses,
        problem.experiments + (("direct_target", problem.predictions),), problem.predictions)
    bypass_cost = bypass.minimum_guaranteed_measurements()
    assert bypass_cost == 1
    return dict(status="ok", seed=seed, public_problem=public,
                judge_only=dict(problem=asdict(problem), independent_control=asdict(control), proofs=proofs),
                minimum_measurements=coupled_cost, independent_minimum_measurements=independent_cost,
                known_c_minimum_measurements=1, direct_target_bypass_measurements=bypass_cost,
                limitation="Static finite experiment PoC; no runtime mode, model scores, forced temporal order, or physical-world proof.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 17, 2525])
    parser.add_argument("--out", type=Path, default=ROOT / "docs/profiling/theory-progression")
    args = parser.parse_args()
    digest = hashlib.sha256()
    for path in [Path(__file__), ROOT / "src/nexus/models/theory.py", ROOT / "src/nexus/solver/finite_experiments.py", ROOT / "src/nexus/generator/randomness.py"]:
        digest.update(path.read_bytes())
    fingerprint = digest.hexdigest()
    args.out.mkdir(parents=True, exist_ok=True)
    for seed in args.seeds:
        path = args.out / f"seed-{seed}.json"
        if path.exists():
            previous = json.loads(path.read_text())
            if previous.get("code") == fingerprint and previous.get("status") == "ok":
                continue
        result = run_case(seed)
        result.update(code=fingerprint, python=platform.python_version())
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(result, indent=2) + "\n")
        temporary.replace(path)
        print(json.dumps(dict(seed=seed, status="ok", hypotheses=len(result["judge_only"]["proofs"]))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
