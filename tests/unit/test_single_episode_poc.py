import pytest
from test_belief_policy import _artifact, _episode, _phase_rule

from nexus.models.world import Shape
from nexus.solver.belief import _POLICY_RESULT_CACHE, solve_guaranteed_policy
from nexus.solver.experiments import PLANNING_SEARCH, planning_experiment, solver_experiment
from nexus.solver.single_episode import budget_decision_worker


def fixture():
    return (
        _episode(artifacts={"A1": _artifact("A1", Shape.SQUARE)}, phase_modulus=2),
        {"M1": [_phase_rule(0), _phase_rule(1)]},
    )


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
                episode, candidate_rules_by_machine=rules, max_actions=8, expected_actions=claim
            )
            assert certificate.solvable is (claim == 4)
            final = solve_guaranteed_policy(
                episode, candidate_rules_by_machine=rules, max_actions=8
            )
    assert final.model_dump(exclude={"visited_belief_nodes"}) == ordinary.model_dump(
        exclude={"visited_belief_nodes"}
    )
    assert PLANNING_SEARCH.get() == "ordinary"


def test_spawned_worker_exception_is_not_a_negative_proof():
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor

    episode, rules = fixture()
    with ProcessPoolExecutor(
        max_workers=1, mp_context=multiprocessing.get_context("spawn")
    ) as pool:
        future = pool.submit(budget_decision_worker, episode, rules, 8, 3, 100_000, 1, "combined")
        with pytest.raises(ValueError, match="hypothesis count"):
            future.result(timeout=30)


@pytest.mark.parametrize("budget", [0, 3, 4, 5])
@pytest.mark.parametrize("parts", [2, 4])
def test_root_partition_union_equals_unsplit_decision(budget, parts):
    episode, rules = fixture()
    whole = budget_decision_worker(episode, rules, 8, budget, 100_000, 256, "combined")
    shards = [
        budget_decision_worker(episode, rules, 8, budget, 100_000, 256, "combined", (index, parts))
        for index in range(parts)
    ]
    assert any(shard.can_win for shard in shards) == whole.can_win


def test_parallel_root_certificate_preserves_witness_and_values():
    episode, rules = fixture()
    results = []
    for strategy in ("ordinary", "parallel-root"):
        _POLICY_RESULT_CACHE.clear()
        with solver_experiment("combined"), planning_experiment(strategy):
            result = solve_guaranteed_policy(
                episode,
                candidate_rules_by_machine=rules,
                max_actions=8,
                expected_actions=4 if strategy != "ordinary" else None,
            )
        results.append(result.model_dump(exclude={"visited_belief_nodes"}))
    assert results[0] == results[1]


@pytest.mark.parametrize("limit", [3, 4, 8])
@pytest.mark.parametrize("strategy", ["reuse", "reuse-certificate", "reuse-parallel"])
def test_transition_reuse_preserves_inputs_and_exact_results(limit, strategy):
    from test_solver_performance_invariants import _episode as larger_episode
    from test_solver_performance_invariants import _rule

    episode = larger_episode()
    rules = {"M1": [_rule(0, 4), _rule(1, 5), _rule(2, 6)]}
    before = episode.model_dump_json()
    results = []
    for variant in ("ordinary", strategy):
        _POLICY_RESULT_CACHE.clear()
        with solver_experiment("combined"), planning_experiment(variant):
            result = solve_guaranteed_policy(
                episode, candidate_rules_by_machine=rules, max_actions=limit
            )
        results.append(result.model_dump(exclude={"visited_belief_nodes"}))
        assert episode.model_dump_json() == before
    assert results[0] == results[1]


def test_transition_reuse_preserves_constructed_experiment_action_values():
    from test_belief_policy import (
        _constructed_experiment_episode,
        _diagnostic_phase_rule,
        _set_value,
    )

    episode = _constructed_experiment_episode()
    rules = {
        "M1": [_diagnostic_phase_rule(phase) for phase in range(4)],
        "M2": [_set_value(10)],
        "M3": [_set_value(7)],
    }
    results = []
    for variant in ("ordinary", "reuse", "reuse-parallel"):
        _POLICY_RESULT_CACHE.clear()
        with solver_experiment("combined"), planning_experiment(variant):
            result = solve_guaranteed_policy(
                episode,
                candidate_rules_by_machine=rules,
                max_actions=12,
                expected_actions=7 if variant == "reuse-parallel" else None,
            )
        results.append(result.model_dump(exclude={"visited_belief_nodes"}))
    assert all(result == results[0] for result in results)


def test_budget_decision_does_not_misreport_physical_exhaustion_as_unsolvable():
    episode, rules = fixture()
    with pytest.raises(RuntimeError, match="state limit exhausted"):
        budget_decision_worker(episode, rules, 8, 4, 0, 256, "combined")


@pytest.mark.parametrize("partition", [(0, 0), (-1, 2), (2, 2)])
def test_invalid_root_partitions_are_rejected(partition):
    episode, rules = fixture()
    with pytest.raises(ValueError, match="invalid root"):
        budget_decision_worker(episode, rules, 8, 4, 100_000, 256, "combined", partition)
