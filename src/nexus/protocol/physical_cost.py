"""Operator-only physical continuation costs for explicitly supported ontologies.

These costs assume the disclosed laws are known and ignore an evaluator's later
closure of the attempt. They are not cognitive complexity or discovery bounds.
"""

from collections.abc import Sequence

from nexus.engine.canonical import canonical_hash
from nexus.engine.engine import step
from nexus.models.episode import PrivateEpisode
from nexus.models.events import TraceRecord
from nexus.ontology.catalog import runtime_for


def continuation_report(episode: PrivateEpisode, trace: Sequence[TraceRecord]) -> dict:
    spec = episode.public.investigation
    cost = getattr(runtime_for(spec), "remaining_physical_actions", None) if spec else None
    if cost is None:
        return {
            "version": "physical-continuation-v1",
            "available": False,
            "reason": "family_has_no_exact_continuation_hook",
        }
    if getattr(spec.data(), "resolved", None) is None:
        return {
            "version": "physical-continuation-v1",
            "available": False,
            "reason": "laws_are_not_disclosed",
        }
    state = episode.public.initial_state.model_copy(deep=True)
    budget = state.resources.actions_remaining
    initial = cost(spec, state)
    if initial is None:
        raise ValueError("qualified initial world has no physical continuation")
    first = 0 if budget is not None and initial > budget else None
    unreachable = None
    remaining = initial
    excess = 0
    for record in trace:
        if canonical_hash(state) != record.before_hash:
            raise ValueError("continuation trace before-hash mismatch")
        result = step(state, record.action, episode)
        if not result.ok or canonical_hash(result.state) != record.after_hash:
            raise ValueError("continuation trace does not reproduce the committed state")
        state = result.state
        remaining = 0 if state.terminal_status.value == "won" else cost(spec, state)
        if remaining is None:
            unreachable = state.turn if unreachable is None else unreachable
            excess = None
        else:
            excess = state.turn + remaining - initial
        if first is None and (
            remaining is None or (budget is not None and state.turn + remaining > budget)
        ):
            first = state.turn
    return {
        "version": "physical-continuation-v1",
        "available": True,
        "scope": "Exact physical costs including take, travel and finish; ignores later evaluator closure. Not a reasoning or evidence bound.",
        "initial_minimum_actions": initial,
        "minimum_remaining_actions": remaining,
        "initial_action_budget": budget,
        "accepted_actions": state.turn,
        "first_budget_infeasible_turn": first,
        "first_unreachable_turn": unreachable,
        "excess_actions": excess,
    }
