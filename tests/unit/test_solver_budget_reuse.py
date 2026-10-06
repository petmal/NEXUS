import pytest
from test_belief_policy import _artifact, _episode, _phase_rule

from nexus.models.world import Shape
from nexus.solver.belief import _POLICY_RESULT_CACHE, solve_guaranteed_policy
from nexus.solver.budget import BudgetMemo


def fixture():
    return (_episode(artifacts={"A1": _artifact("A1", Shape.SQUARE)}, phase_modulus=2),
            {"M1": [_phase_rule(0), _phase_rule(1)]})


def test_budget_bounds_preserve_unknown_interval_and_belief_identity():
    memo = BudgetMemo()
    memo[(7, frozenset({0, 1}), 4)] = False
    memo[(7, frozenset({0, 1}), 8)] = True
    assert [memo.get((7, frozenset({0, 1}), n)) for n in (3, 4, 5, 7, 8, 9)] == [
        False, False, None, None, True, True
    ]
    assert memo.get((7, frozenset({0}), 3)) is None
    assert memo.get((8, frozenset({0, 1}), 3)) is None
    with pytest.raises(AssertionError, match="contradictory"):
        memo[(7, frozenset({0, 1}), 8)] = False


@pytest.mark.parametrize("claim", [3, 4, 5])
def test_certificate_fallback_preserves_exact_optimizer_and_inputs(claim):
    episode, rules = fixture()
    before = episode.model_dump_json()
    _POLICY_RESULT_CACHE.clear()
    ordinary = solve_guaranteed_policy(episode, candidate_rules_by_machine=rules, max_actions=8)
    _POLICY_RESULT_CACHE.clear()
    certificate = solve_guaranteed_policy(
        episode, candidate_rules_by_machine=rules, max_actions=8, expected_actions=claim
    )
    assert certificate.solvable is (claim == 4)
    assert not certificate.exhausted_action_limit
    final = solve_guaranteed_policy(episode, candidate_rules_by_machine=rules, max_actions=8)
    assert final.model_dump(exclude={"visited_belief_nodes"}) == ordinary.model_dump(
        exclude={"visited_belief_nodes"}
    )
    warm = solve_guaranteed_policy(
        episode, candidate_rules_by_machine=rules, max_actions=8, expected_actions=claim
    )
    assert warm.solvable == certificate.solvable
    assert warm.exhausted_action_limit == certificate.exhausted_action_limit
    assert episode.model_dump_json() == before


def test_physical_exhaustion_cannot_remove_hypotheses_from_proof():
    episode, rules = fixture()
    _POLICY_RESULT_CACHE.clear()
    with pytest.raises(RuntimeError, match="physical state limit exhausted"):
        solve_guaranteed_policy(episode, candidate_rules_by_machine=rules,
                                max_actions=8, max_physical_states=0)


def test_richer_cached_proof_satisfies_no_action_value_query(monkeypatch):
    import nexus.solver.belief as solver
    episode, rules = fixture()
    _POLICY_RESULT_CACHE.clear()
    rich = solve_guaranteed_policy(episode, candidate_rules_by_machine=rules, max_actions=8)

    def unexpected(*args, **kwargs):
        raise AssertionError("recomputed existing exact proof")

    monkeypatch.setattr(solver, "solve_compressed_physical", unexpected)
    proof = solve_guaranteed_policy(episode, candidate_rules_by_machine=rules,
                                    max_actions=8, include_action_values=False)
    assert proof.witness == rich.witness
    assert proof.initial_action_values == ()


def test_exhausted_optimizer_does_not_change_certificate_status():
    episode, rules = fixture()
    _POLICY_RESULT_CACHE.clear()
    cold = solve_guaranteed_policy(episode, candidate_rules_by_machine=rules,
                                   max_actions=3, expected_actions=3, include_action_values=False)
    _POLICY_RESULT_CACHE.clear()
    exhausted = solve_guaranteed_policy(episode, candidate_rules_by_machine=rules,
                                        max_actions=3, include_action_values=False)
    assert exhausted.exhausted_action_limit
    warm = solve_guaranteed_policy(episode, candidate_rules_by_machine=rules,
                                   max_actions=3, expected_actions=3, include_action_values=False)
    assert warm.model_dump(exclude={"visited_belief_nodes"}) == cold.model_dump(
        exclude={"visited_belief_nodes"}
    )
