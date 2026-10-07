import pytest

from nexus.generator import generate_episode
from nexus.models import ACTION_ADAPTER
from nexus.protocol.session import Session


def test_session_retries_are_idempotent():
    episode = generate_episode(42)
    session = Session(episode)
    first_action = ACTION_ADAPTER.validate_python(episode.reference_plan[0])
    response = session.act(0, first_action)
    assert response.ok
    assert response.performance is None
    assert session.state.turn == 1

    duplicate = session.act(0, first_action)
    assert duplicate.ok and duplicate.duplicate
    assert duplicate.performance is None
    assert session.state.turn == 1


def test_stale_turn_with_different_action_is_rejected():
    episode = generate_episode(44)
    session = Session(episode)
    first_action = ACTION_ADAPTER.validate_python(episode.reference_plan[0])
    response = session.act(0, first_action)
    assert response.ok

    different = ACTION_ADAPTER.validate_python({"type": "finish"})
    stale = session.act(0, different)
    assert not stale.ok
    assert not stale.duplicate
    assert stale.performance is None
    assert "different action" in stale.message
    assert session.state.turn == 1


def test_turn_mismatch_is_rejected():
    session = Session(generate_episode(43))
    action = ACTION_ADAPTER.validate_python({"type": "wait"})
    response = session.act(99, action)
    assert not response.ok
    assert response.performance is None
    assert session.state.turn == 0


def test_terminal_performance_uses_signed_guaranteed_policy_deltas():
    episode = generate_episode(1702, discovery_level=2, planning_level=1)
    assert episode.generation_metadata.required_probe_count == 1

    session = Session(episode)
    terminal = None
    for raw_action in episode.reference_plan:
        action = ACTION_ADAPTER.validate_python(raw_action)
        terminal = session.act(session.state.turn, action)
        assert terminal.ok

    assert terminal is not None
    assert terminal.observation.terminal_status.value == "won"
    assert terminal.performance is not None

    performance = terminal.performance
    assert performance.actions_used == episode.generation_metadata.optimal_action_count
    assert performance.optimal_physical_actions == episode.generation_metadata.optimal_action_count
    assert performance.minimum_guaranteed_probes == 1
    assert (
        performance.guaranteed_policy_actions
        == episode.generation_metadata.guaranteed_policy_action_count
    )
    assert performance.guaranteed_policy_actions > performance.optimal_physical_actions
    assert performance.action_delta_from_guaranteed_policy == (
        performance.actions_used - performance.guaranteed_policy_actions
    )
    assert performance.action_delta_from_guaranteed_policy < 0
    assert performance.probes_used == 0
    assert performance.probe_delta_from_guaranteed_minimum == -1
    assert (
        performance.move_actions
        + performance.wait_actions
        + performance.take_actions
        + performance.drop_actions
        + performance.operate_actions
        + performance.probes_used
        + performance.finish_actions
        == performance.actions_used
    )
    reference_moves = sum(item.get("type") == "move" for item in episode.reference_plan)
    assert performance.reference_plan_move_actions == reference_moves
    assert performance.move_delta_from_reference_plan == (
        performance.move_actions - reference_moves
    )
    assert performance.rooms_visited >= 1
    assert performance.room_revisits >= 0
    assert performance.goal_satisfied
    assert performance.goal_leaf_count >= 1
    assert performance.satisfied_goal_leaf_count == performance.goal_leaf_count
    assert performance.unsatisfied_goal_leaves == ()
    assert performance.invalid_actions == 0
    assert performance.failed_finishes == 0
    assert performance.duplicate_requests == 0
    assert performance.protocol_conflicts == 0
    payload = performance.model_dump(mode="json", by_alias=True)
    assert payload["$schema"].startswith(
        "https://raw.githubusercontent.com/petmal/NEXUS/"
    )
    assert payload["$schema"].endswith("/schemas/performance-v4.schema.json")
    assert performance.discovery_level == 2
    assert performance.planning_level == 1
    assert performance.resource_pressure == 0
    assert performance.terminal_status == "won"
    assert performance.initial_action_budget == (
        performance.actions_used + performance.budget_remaining
    )


def test_terminal_performance_counts_runtime_inefficiencies_without_changing_state():
    episode = generate_episode(1711, discovery_level=0, planning_level=1)
    session = Session(episode)

    invalid = ACTION_ADAPTER.validate_python({"type": "move", "target": "R999"})
    rejected = session.act(0, invalid)
    assert not rejected.ok
    assert session.state.turn == 0

    first_action = ACTION_ADAPTER.validate_python(episode.reference_plan[0])
    first = session.act(0, first_action)
    assert first.ok

    duplicate = session.act(0, first_action)
    assert duplicate.ok and duplicate.duplicate

    conflict = session.act(0, ACTION_ADAPTER.validate_python({"type": "finish"}))
    assert not conflict.ok
    assert session.state.turn == 1

    terminal = None
    for raw_action in episode.reference_plan[1:]:
        terminal = session.act(
            session.state.turn,
            ACTION_ADAPTER.validate_python(raw_action),
        )
        assert terminal.ok

    assert terminal is not None and terminal.performance is not None
    performance = terminal.performance
    assert performance.invalid_actions == 1
    assert performance.duplicate_requests == 1
    assert performance.protocol_conflicts == 1
    assert performance.failed_finishes == 0
    assert performance.goal_satisfied


def test_terminal_performance_counts_rejected_finish_and_reports_failed_episode():
    episode = generate_episode(1719, discovery_level=0, planning_level=0)
    session = Session(episode)

    rejected_finish = session.act(
        0,
        ACTION_ADAPTER.validate_python({"type": "finish"}),
    )
    assert rejected_finish.ok
    assert rejected_finish.performance is None

    terminal = None
    for raw_action in episode.reference_plan:
        terminal = session.act(
            session.state.turn,
            ACTION_ADAPTER.validate_python(raw_action),
        )
        assert terminal.ok

    assert terminal is not None and terminal.performance is not None
    assert terminal.observation.terminal_status.value == "won"
    assert terminal.performance.failed_finishes == 1
    assert terminal.performance.finish_actions >= 2
    assert terminal.performance.action_delta_from_guaranteed_policy == 1
    assert terminal.performance.goal_satisfied

    failing_episode = generate_episode(1723, discovery_level=0, planning_level=0)
    failing_episode.public.initial_state.resources.actions_remaining = 1
    failing_session = Session(failing_episode)
    failed = failing_session.act(
        0,
        ACTION_ADAPTER.validate_python({"type": "wait"}),
    )

    assert failed.ok
    assert failed.observation.terminal_status.value == "failed"
    assert failed.performance is not None
    assert failed.performance.actions_used == 1
    assert failed.performance.wait_actions == 1
    assert failed.performance.move_actions == 0
    assert failed.performance.rooms_visited == 1
    assert failed.performance.room_revisits == 0
    assert failed.performance.budget_remaining == 0
    assert not failed.performance.goal_satisfied
    assert failed.performance.satisfied_goal_leaf_count < failed.performance.goal_leaf_count
    assert failed.performance.unsatisfied_goal_leaves


@pytest.mark.slow
def test_terminal_performance_uses_exact_policy_cost_for_higher_discovery():
    episode = generate_episode(
        17,
        discovery_level=5,
        planning_level=1,
        verifier_secret="performance-policy-secret",
    )
    session = Session(episode)

    terminal = None
    for raw_action in episode.reference_plan:
        terminal = session.act(
            session.state.turn,
            ACTION_ADAPTER.validate_python(raw_action),
        )
        assert terminal.ok

    assert terminal is not None and terminal.performance is not None
    performance = terminal.performance
    assert (
        performance.guaranteed_policy_actions
        == episode.generation_metadata.guaranteed_policy_action_count
    )
    assert performance.action_delta_from_guaranteed_policy == (
        performance.actions_used - performance.guaranteed_policy_actions
    )
