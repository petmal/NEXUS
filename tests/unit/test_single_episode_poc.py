import pytest

from nexus.solver.belief import _POLICY_RESULT_CACHE, solve_guaranteed_policy
from nexus.solver.experiments import PLANNING_SEARCH, planning_experiment, solver_experiment
from nexus.solver.single_episode import budget_decision_worker
from test_belief_policy import _artifact, _episode, _phase_rule
from nexus.models.world import Shape


def fixture():
    return (_episode(artifacts={"A1": _artifact("A1", Shape.SQUARE)}, phase_modulus=2),
            {"M1": [_phase_rule(0), _phase_rule(1)]})


@pytest.mark.parametrize("budget,expected", [(0, False), (3, False), (4, True), (5, True)])
def test_budget_decision_is_at_most_not_exact_cost(budget, expected):
    episode, rules = fixture()
    result = budget_decision_worker(episode, rules, 8, budget, 100_000, 256, "combined")
    assert result.can_win is expected
    assert result.viable_hypotheses == 2


@pytest.mark.parametrize("claim", [3, 4, 5])
@pytest.mark.parametrize("strategy", ["certificate", "parallel-certificate"])
def test_certificate_and_fallback_preserve_exact_optimizer(claim, strategy):
    episode, rules = fixture()
    _POLICY_RESULT_CACHE.clear()
    with solver_experiment("combined"):
        ordinary = solve_guaranteed_policy(episode, candidate_rules_by_machine=rules, max_actions=8)
        _POLICY_RESULT_CACHE.clear()
        with planning_experiment(strategy):
            certificate = solve_guaranteed_policy(
                episode, candidate_rules_by_machine=rules, max_actions=8, expected_actions=claim)
            assert certificate.solvable is (claim == 4)
            final = solve_guaranteed_policy(episode, candidate_rules_by_machine=rules, max_actions=8)
    assert final.model_dump(exclude={"visited_belief_nodes"}) == ordinary.model_dump(
        exclude={"visited_belief_nodes"})
    assert PLANNING_SEARCH.get() == "ordinary"


def test_spawned_worker_exception_is_not_a_negative_proof():
    from concurrent.futures import ProcessPoolExecutor
    import multiprocessing
    episode, rules = fixture()
    with ProcessPoolExecutor(max_workers=1, mp_context=multiprocessing.get_context("spawn")) as pool:
        future = pool.submit(budget_decision_worker, episode, rules, 8, 3, 100_000, 1, "combined")
        with pytest.raises(ValueError, match="hypothesis count"):
            future.result(timeout=30)
