"""Spawn-safe research worker for one exact at-most-budget decision."""

from nexus.models.episode import PrivateEpisode
from nexus.models.rules import Effect
from nexus.solver.experiments import BudgetDecision, solver_experiment


def budget_decision_worker(
    episode: PrivateEpisode,
    candidates: dict[str, list[Effect]],
    max_actions: int,
    budget: int,
    max_physical_states: int,
    max_hypotheses: int,
    mode: str,
) -> BudgetDecision:
    from nexus.solver.belief import _solve_policy

    with solver_experiment(mode):
        result = _solve_policy(
            episode, candidate_rules_by_machine=candidates, max_actions=max_actions,
            max_physical_states=max_physical_states, max_hypotheses=max_hypotheses,
            include_action_values=False, decision_budget=budget,
        )
    assert isinstance(result, BudgetDecision)
    return result
