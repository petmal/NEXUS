import pytest

from nexus.solver.experiments import BudgetMemo, MODES, SEARCH_MODE, solver_experiment
from nexus.solver.belief import _POLICY_RESULT_CACHE, solve_guaranteed_policy
from test_solver_performance_invariants import _episode, _rule


def test_budget_bounds_preserve_unknown_interval():
    memo = BudgetMemo(True)
    memo[(7, frozenset({0, 1}), 4)] = False
    memo[(7, frozenset({0, 1}), 8)] = True
    assert [memo.get((7, frozenset({0, 1}), n)) for n in (3, 4, 5, 7, 8, 9)] == [False, False, None, None, True, True]
    assert memo.get((7, frozenset({0}), 3)) is None


@pytest.mark.parametrize("limit", [1, 4, 5, 8])
def test_experiments_match_baseline_and_preserve_inputs(limit):
    episode = _episode()
    initial = episode.model_dump_json()
    candidates = {"M1": [_rule(0, 4), _rule(1, 5), _rule(2, 6)]}
    results = []
    for mode in MODES:
        _POLICY_RESULT_CACHE.clear()
        with solver_experiment(mode):
            result = solve_guaranteed_policy(episode, candidate_rules_by_machine=candidates,
                                             max_actions=limit)
        results.append(result.model_dump(exclude={"visited_belief_nodes"}))
        assert episode.model_dump_json() == initial
    assert all(item == results[0] for item in results)
    assert SEARCH_MODE.get() == "baseline"


def test_context_restores_after_failure():
    with pytest.raises(RuntimeError), solver_experiment("combined"):
        raise RuntimeError("interrupted")
    assert SEARCH_MODE.get() == "baseline"


@pytest.mark.parametrize("mode", MODES)
def test_each_mode_reuses_richer_proof_without_resolving(monkeypatch, mode):
    import nexus.solver.belief as solver
    _POLICY_RESULT_CACHE.clear()
    episode = _episode()
    candidates = {"M1": [_rule(0, 4), _rule(1, 5), _rule(2, 6)]}
    with solver_experiment(mode):
        rich = solve_guaranteed_policy(episode, candidate_rules_by_machine=candidates, max_actions=8)
        def unexpected(*args, **kwargs):
            raise AssertionError("qualification recomputed an existing richer proof")
        monkeypatch.setattr(solver, "solve_compressed_physical", unexpected)
        proof = solve_guaranteed_policy(episode, candidate_rules_by_machine=candidates,
                                       max_actions=8, include_action_values=False)
    assert proof.witness == rich.witness


@pytest.mark.parametrize("expected", [3, 4, 5, 6])
def test_fixed_cost_certificates_match_in_every_mode(expected):
    episode = _episode()
    candidates = {"M1": [_rule(0, 4), _rule(1, 5), _rule(2, 6)]}
    results = []
    for mode in MODES:
        _POLICY_RESULT_CACHE.clear()
        with solver_experiment(mode):
            result = solve_guaranteed_policy(
                episode, candidate_rules_by_machine=candidates, max_actions=8,
                expected_actions=expected, include_action_values=False,
            )
        results.append(result.model_dump(exclude={"visited_belief_nodes"}))
    assert all(result == results[0] for result in results)
