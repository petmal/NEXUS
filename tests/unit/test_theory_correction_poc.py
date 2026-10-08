import importlib.util
from pathlib import Path
import sys
import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/theory_correction_poc.py"
spec = importlib.util.spec_from_file_location("theory_correction_poc", SCRIPT)
poc = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = poc
spec.loader.exec_module(poc)


def test_effective_theory_is_exact_on_whole_disclosed_validity_domain():
    assert poc.prove_domain(poc.CorrectionPrior()) > 10_000


def test_calibration_does_not_hide_corrections_and_true_law_belongs_to_public_prior():
    spec, world, candidates = poc.build_case(17)
    assert world.rules["law"] in candidates
    assert candidates == spec.hypotheses()
    assert len(candidates) == 9
    assert world.public.evidence_files["theory.json"] == spec.public_json()
    assert world.public.evidence_files["facility_manual.txt"] == spec.manual()
    spec2, world2, candidates2 = poc.build_case(17)
    assert (spec, world, candidates) == (spec2, world2, candidates2)


def test_complete_correction_policy_replay_and_budget_mismatch_rejection(monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPT.parent))
    from profile_theory import replay_policy
    from nexus.solver.belief import solve_guaranteed_policy
    result = poc.run_case(17)
    assert result["replayed"] == result["viable_candidates"] == 5
    _, world, candidates = poc.build_case(17)
    policy = solve_guaranteed_policy(world, candidate_rules_by_machine={"M1": candidates},
                                    max_actions=96, include_action_values=False)
    world.generation_metadata.guaranteed_policy_witness = policy.witness.model_dump(mode="json")
    world.generation_metadata.guaranteed_policy_action_count = policy.optimal_worst_case_actions - 1
    with pytest.raises(RuntimeError, match="root budget"):
        replay_policy(world, {"M1": candidates})
    world.generation_metadata.guaranteed_policy_action_count = policy.optimal_worst_case_actions
    world.generation_metadata.viable_causal_hypotheses = 6
    with pytest.raises(RuntimeError, match="every certified viable"):
        replay_policy(world, {"M1": candidates})
