from __future__ import annotations

import nexus.solver.belief as belief_module
from nexus.models.actions import ProbeAction
from nexus.models.episode import PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.rules import Condition, ConditionKind, Effect, EffectKind
from nexus.models.world import (
    Artifact,
    Machine,
    Orientation,
    Pattern,
    Polarity,
    Resources,
    Room,
    Shape,
    TerminalStatus,
    WorldState,
)
from nexus.solver.belief import (
    _POLICY_RESULT_CACHE,
    _POLICY_RESULT_CACHE_LIMIT,
    BeliefPolicyResult,
    _cache_result,
    _episode_for_hypothesis,
    _normalize_fresh_state,
    _normalize_state,
    solve_compressed_physical,
    solve_guaranteed_policy,
)
from nexus.solver.search import search_state_key, solve


def _artifact(artifact_id: str, shape: Shape = Shape.SQUARE) -> Artifact:
    return Artifact(
        id=artifact_id,
        location="@inventory",
        shape=shape,
        pattern=Pattern.PLAIN,
        orientation=Orientation.NORTH,
        value=0,
        polarity=Polarity.POSITIVE,
    )


def _set(value: int) -> Effect:
    return Effect(kind=EffectKind.SET, field="value", value=value)


def _rule(phase: int, circle_code: int = 5) -> Effect:
    phase_effect = Effect(
        kind=EffectKind.CONDITIONAL,
        condition=Condition(kind=ConditionKind.PHASE_EQUALS, value=phase),
        effects=(_set(1),),
        else_effects=(_set(3),),
    )
    return Effect(
        kind=EffectKind.CONDITIONAL,
        condition=Condition(kind=ConditionKind.EQUALS, field="shape", value=Shape.CIRCLE.value),
        effects=(_set(circle_code),),
        else_effects=(phase_effect,),
    )


def _episode() -> PrivateEpisode:
    public = PublicEpisode(
        episode_id="performance-proof",
        description="proof",
        rooms={"R0": Room(id="R0", label="Lab")},
        edges=(),
        phase_modulus=3,
        initial_state=WorldState(
            phase=0,
            agent_room="R0",
            artifacts={
                "A1": _artifact("A1"),
                "A2": _artifact("A2", Shape.CIRCLE),
                "A3": _artifact("A3", Shape.TRIANGLE),
            },
            machines={"M1": Machine(id="M1", room_id="R0", uses_remaining=1)},
            resources=Resources(actions_remaining=32),
        ),
        goal=GoalPredicate(kind=GoalKind.ARTIFACT_FIELD, artifact_id="A1", field="value", value=1),
    )
    return PrivateEpisode(
        public=public,
        rules={"r": _rule(0)},
        machine_rules={"M1": "r"},
        verifier_secret="proof-secret",
    )


def test_search_state_key_ignores_only_path_cost_fields():
    state = _episode().public.initial_state
    key = search_state_key(state)

    turn = state.model_copy(deep=True)
    turn.turn += 7
    budget = state.model_copy(deep=True)
    budget.resources.actions_remaining -= 1
    reordered = state.model_copy(deep=True)
    reordered.artifacts = dict(reversed(tuple(reordered.artifacts.items())))
    assert search_state_key(turn) == key
    assert search_state_key(budget) == key
    assert search_state_key(reordered) == key

    mutations = []
    changed = state.model_copy(deep=True)
    changed.phase = 1
    mutations.append(changed)
    changed = state.model_copy(deep=True)
    changed.agent_room = "R9"
    mutations.append(changed)
    changed = state.model_copy(deep=True)
    changed.artifacts["A1"].location = "R9"
    mutations.append(changed)
    changed = state.model_copy(deep=True)
    changed.artifacts["A1"].shape = Shape.CIRCLE
    mutations.append(changed)
    changed = state.model_copy(deep=True)
    changed.artifacts["A1"].pattern = Pattern.DOTTED
    mutations.append(changed)
    changed = state.model_copy(deep=True)
    changed.artifacts["A1"].orientation = Orientation.EAST
    mutations.append(changed)
    changed = state.model_copy(deep=True)
    changed.artifacts["A1"].value = 4
    mutations.append(changed)
    changed = state.model_copy(deep=True)
    changed.artifacts["A1"].polarity = Polarity.NEGATIVE
    mutations.append(changed)
    changed = state.model_copy(deep=True)
    changed.artifacts["A4"] = _artifact("A4")
    mutations.append(changed)
    changed = state.model_copy(deep=True)
    changed.machines["M1"].room_id = "R9"
    mutations.append(changed)
    changed = state.model_copy(deep=True)
    changed.machines["M1"].uses_remaining = 0
    mutations.append(changed)
    changed = state.model_copy(deep=True)
    changed.machines["M2"] = Machine(id="M2", room_id="R0")
    mutations.append(changed)
    changed = state.model_copy(deep=True)
    changed.terminal_status = TerminalStatus.FAILED
    mutations.append(changed)

    assert all(search_state_key(changed) != key for changed in mutations)


def test_requested_action_values_are_a_projection_not_a_policy_restriction():
    episode = _episode()
    candidates = {"M1": [_rule(0, 4), _rule(1, 5), _rule(2, 6)]}
    requested = (
        ProbeAction(machine="M1", artifact="A1"),
        ProbeAction(machine="M1", artifact="A2"),
    )
    full = solve_guaranteed_policy(episode, candidate_rules_by_machine=candidates, max_actions=10)
    subset = solve_guaranteed_policy(
        episode,
        candidate_rules_by_machine=candidates,
        max_actions=10,
        requested_action_values=requested,
    )
    none = solve_guaranteed_policy(
        episode,
        candidate_rules_by_machine=candidates,
        max_actions=10,
        include_action_values=False,
    )

    assert subset.solvable == full.solvable == none.solvable
    assert (
        subset.optimal_worst_case_actions
        == full.optimal_worst_case_actions
        == none.optimal_worst_case_actions
    )
    assert subset.witness == full.witness == none.witness
    assert none.initial_action_values == ()
    full_by_action = {value.action: value for value in full.initial_action_values}
    assert len(subset.initial_action_values) == 2
    for value in subset.initial_action_values:
        assert value == full_by_action[value.action]


def test_policy_cache_is_lru_bounded_and_stores_copies():
    _POLICY_RESULT_CACHE.clear()
    result = BeliefPolicyResult(
        solvable=True, viable_hypothesis_count=1, optimal_worst_case_actions=1
    )
    keys = []
    for index in range(_POLICY_RESULT_CACHE_LIMIT + 2):
        key = (f"semantic-{index}", 100, 8, ("none",))
        keys.append(key)
        _cache_result(key, 8, result)
    assert len(_POLICY_RESULT_CACHE) == _POLICY_RESULT_CACHE_LIMIT
    assert keys[0] not in _POLICY_RESULT_CACHE
    assert keys[-1] in _POLICY_RESULT_CACHE

    result.solvable = False
    assert _POLICY_RESULT_CACHE[keys[-1]].result.solvable is True
    _POLICY_RESULT_CACHE.clear()


def test_compressed_generation_solver_remains_exact_against_bfs():
    episode = _episode()
    episode.public.rooms["R1"] = Room(id="R1", label="Machine")
    episode.public.edges = (("R0", "R1"),)
    episode.public.initial_state.machines["M1"].room_id = "R1"
    ordinary = solve(episode)
    compressed = solve_compressed_physical(episode)
    assert ordinary.solvable and compressed.solvable
    assert compressed.optimal_action_count == ordinary.optimal_action_count
    assert len(compressed.plan) == ordinary.optimal_action_count
    assert compressed.max_frontier_size >= 1


def test_fresh_state_normalization_matches_copying_normalization_without_source_mutation():
    source = _episode().public.initial_state
    before = source.model_copy(deep=True)
    fresh = source.model_copy(deep=True)
    fresh.turn = 9
    fresh.resources.actions_remaining = 1
    expected = _normalize_state(fresh, 777)
    actual = _normalize_fresh_state(fresh, 777)
    assert actual == expected
    assert actual is fresh
    assert source == before


def test_hypothesis_episode_targeted_copy_matches_deep_copy_and_is_isolated():
    episode = _episode()
    replacement = _rule(1, 9)
    reference = episode.model_copy(deep=True)
    reference.public.initial_state.resources.actions_remaining = 777
    reference.rules[reference.machine_rules["M1"]] = replacement

    candidate = _episode_for_hypothesis(episode, {"M1": replacement}, search_budget=777)
    sibling = _episode_for_hypothesis(episode, {"M1": _rule(2, 8)}, search_budget=888)
    assert candidate.model_dump(mode="python") == reference.model_dump(mode="python")

    candidate.public.initial_state.agent_room = "mutated"
    candidate.rules["extra"] = _set(7)
    assert episode.public.initial_state.agent_room == "R0"
    assert "extra" not in episode.rules
    assert sibling.public.initial_state.agent_room == "R0"
    assert "extra" not in sibling.rules
    assert sibling.public.initial_state.resources.actions_remaining == 888


def test_rich_policy_cache_can_satisfy_weaker_exact_query(monkeypatch):
    _POLICY_RESULT_CACHE.clear()
    episode = _episode()
    candidates = {"M1": [_rule(0, 4), _rule(1, 5), _rule(2, 6)]}
    rich = solve_guaranteed_policy(
        episode,
        candidate_rules_by_machine=candidates,
        max_actions=10,
        requested_action_values=(ProbeAction(machine="M1", artifact="A1"),),
    )
    assert rich.solvable and rich.optimal_worst_case_actions is not None
    cache_size = len(_POLICY_RESULT_CACHE)

    def fail_physical(*args, **kwargs):
        raise AssertionError("weaker query recomputed instead of reusing richer exact result")

    monkeypatch.setattr(belief_module, "solve_compressed_physical", fail_physical)
    weaker = solve_guaranteed_policy(
        episode,
        candidate_rules_by_machine=candidates,
        max_actions=rich.optimal_worst_case_actions,
        expected_actions=rich.optimal_worst_case_actions,
        include_action_values=False,
    )
    assert weaker.solvable
    assert weaker.optimal_worst_case_actions == rich.optimal_worst_case_actions
    assert weaker.witness == rich.witness
    assert weaker.initial_action_values == ()
    assert len(_POLICY_RESULT_CACHE) == cache_size
    _POLICY_RESULT_CACHE.clear()


def test_exhausted_rich_cache_does_not_overstate_larger_proof_bound(monkeypatch):
    _POLICY_RESULT_CACHE.clear()
    episode = _episode()
    candidates = {"M1": [_rule(0, 4), _rule(1, 5), _rule(2, 6)]}
    too_small = solve_guaranteed_policy(
        episode,
        candidate_rules_by_machine=candidates,
        max_actions=1,
        requested_action_values=(ProbeAction(machine="M1", artifact="A1"),),
    )
    assert not too_small.solvable
    calls = 0
    original = belief_module.solve_compressed_physical

    def counted(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(belief_module, "solve_compressed_physical", counted)
    larger = solve_guaranteed_policy(
        episode,
        candidate_rules_by_machine=candidates,
        max_actions=10,
        include_action_values=False,
    )
    assert larger.solvable
    assert calls > 0
    _POLICY_RESULT_CACHE.clear()
