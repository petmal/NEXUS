from itertools import product

from nexus.engine.engine import step
from nexus.models.actions import MoveAction
from nexus.models.world import Room, Shape, TerminalStatus
from nexus.solver.belief import (
    _apply_route, _normalize_state, _solve_hypothesis_physical,
    solve_compressed_physical,
)
from test_belief_policy import _artifact, _episode, _set_value


def test_compressed_routes_match_ordinary_engine_and_do_not_mutate_input():
    episode = _episode(artifacts={"A1": _artifact("A1", Shape.SQUARE)}, phase_modulus=4)
    episode.public.rooms.update({f"R{i}": Room(id=f"R{i}", label=str(i)) for i in range(1, 4)})
    episode.public.edges = (("R0", "R1"), ("R1", "R2"), ("R2", "R3"))
    for phase, length, budget in product(range(4), range(4), (2, 512)):
        state = episode.public.initial_state.model_copy(deep=True)
        state.phase = phase
        state.resources.actions_remaining = budget
        original = state.model_dump_json()
        route = tuple(MoveAction(target=f"R{i}") for i in range(1, length + 1))
        expected = state
        for move in route:
            result = step(expected, move, episode)
            if not result.ok:
                expected = None
                break
            expected = result.state
        actual = _apply_route(state, route, episode, 512)
        assert actual == (_normalize_state(expected, 512) if expected else None)
        assert state.model_dump_json() == original


def test_cost_only_matches_plan_search_and_cache_isolates_rules_goals_and_limits():
    episode = _episode(artifacts={"A1": _artifact("A1", Shape.SQUARE)}, phase_modulus=2)
    full = solve_compressed_physical(episode)
    cost = _solve_hypothesis_physical(episode, max_states=100_000)
    assert cost.model_dump(exclude={"plan"}) == full.model_dump(exclude={"plan"})
    assert cost.plan == ()
    state = episode.public.initial_state
    for action in full.plan:
        state = step(state, action, episode).state
    assert state.terminal_status == TerminalStatus.WON
    cost.solvable = False
    assert _solve_hypothesis_physical(episode, max_states=100_000).solvable
    assert _solve_hypothesis_physical(episode, max_states=0).exhausted_state_limit
    assert _solve_hypothesis_physical(episode, max_states=100_000).solvable
    episode.rules["machine-rule"] = _set_value(3)
    assert not _solve_hypothesis_physical(episode, max_states=100_000).solvable
    episode.public.goal = episode.public.goal.model_copy(update={"value": 3})
    assert _solve_hypothesis_physical(episode, max_states=100_000).solvable


def test_explicit_initial_state_and_cost_only_keep_identical_search_bounds():
    episode = _episode(artifacts={"A1": _artifact("A1", Shape.SQUARE)}, phase_modulus=2)
    initial = episode.public.initial_state.model_copy(deep=True)
    initial.phase = 1
    for limit in (0, 1, 100_000):
        full = solve_compressed_physical(episode, initial_state=initial, max_states=limit)
        cost = solve_compressed_physical(episode, initial_state=initial, max_states=limit, include_plan=False)
        assert cost.model_dump(exclude={"plan"}) == full.model_dump(exclude={"plan"})
