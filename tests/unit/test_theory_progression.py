import importlib.util
from pathlib import Path

import pytest

from nexus.models.theory import TheoryProgression, TheoryStage
from nexus.solver.finite_experiments import FiniteExperimentProblem

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/theory_progression_poc.py"
spec = importlib.util.spec_from_file_location("progression_poc", SCRIPT)
poc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(poc)


@pytest.mark.parametrize("seed", [0, 1, 2, 17, 2525])
def test_progression_proves_coupling_transfer_and_matched_controls(seed):
    result = poc.run_case(seed)
    assert result["minimum_measurements"] == result["independent_minimum_measurements"] == 2
    assert result["known_c_minimum_measurements"] == result["direct_target_bypass_measurements"] == 1
    public = result["public_problem"]
    assert "hypotheses" not in public and "predictions" not in public and "proofs" not in public
    graph = TheoryProgression.model_validate(public["progression"])
    assert TheoryProgression.model_validate_json(graph.model_dump_json()) == graph
    assert graph.stages[-1].requires == ("correct",)
    for proof in result["judge_only"]["proofs"]:
        assert len(proof["missing_c_predictions"]) == len(proof["missing_relationship_predictions"]) == 2


@pytest.mark.parametrize("dependencies", [("missing",), ("b",)])
def test_progression_rejects_missing_and_cyclic_dependencies(dependencies):
    with pytest.raises(ValueError, match="missing prerequisite|cycle"):
        TheoryProgression(stages=(
            TheoryStage(id="a", theory_level=1, requires=dependencies, description="a"),
            TheoryStage(id="b", theory_level=2, requires=("a",), description="b"),
        ), prediction_stage="b")


def test_finite_experiments_handle_impossibility_and_contradictory_measurements():
    problem = FiniteExperimentProblem(("a", "b", "c"), (("probe", (0, 0, 1)),), (0, 1, 2))
    assert problem.minimum_guaranteed_measurements() is None
    assert problem.minimum_guaranteed_measurements((("probe", 1),)) == 0
    with pytest.raises(ValueError, match="contradict"):
        problem.compatible((("probe", 0), ("probe", 1)))
    with pytest.raises(ValueError, match="unknown"):
        problem.compatible((("other", 1),))
    with pytest.raises(ValueError, match="align"):
        FiniteExperimentProblem(("a", "b"), (("probe", (0,)),), (0, 1))


def test_duplicate_experiments_do_not_change_exact_measurement_cost():
    problem = FiniteExperimentProblem(("a", "b", "c", "d"),
        (("left", (0, 0, 1, 1)), ("right", (0, 1, 0, 1)), ("again", (0, 0, 1, 1))), (0, 1, 2, 3))
    assert problem.minimum_guaranteed_measurements() == 2
    assert problem.minimum_guaranteed_measurements((("left", 0), ("again", 0))) == 1


def test_proof_command_cannot_certify_with_assertions_disabled(tmp_path):
    import subprocess
    import sys
    result = subprocess.run([sys.executable, "-O", str(SCRIPT), "--out", str(tmp_path)],
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert "requires Python assertions" in result.stderr
    assert not list(tmp_path.glob("*.json"))
