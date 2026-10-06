from nexus.generator import generate_episode
from nexus.models import ACTION_ADAPTER
from nexus.protocol.session import Session


def test_terminal_diagnostics_are_not_exposed_while_session_is_active():
    episode = generate_episode(24001, discovery_level=0, planning_level=0)
    session = Session(episode)

    first = session.act(
        0,
        ACTION_ADAPTER.validate_python(episode.reference_plan[0]),
    )

    assert first.ok
    assert first.observation.terminal_status.value == "active"
    assert first.performance is None


def test_failed_terminal_diagnostics_describe_goal_deficit_and_action_shape():
    episode = generate_episode(24002, discovery_level=0, planning_level=0)
    episode.public.initial_state.resources.actions_remaining = 1
    episode.generation_metadata.action_budget = 1
    session = Session(episode)

    failed = session.act(
        0,
        ACTION_ADAPTER.validate_python({"type": "wait"}),
    )

    assert failed.ok
    assert failed.observation.terminal_status.value == "failed"
    assert failed.performance is not None
    performance = failed.performance
    assert performance.goal_satisfied is False
    assert performance.unsatisfied_goal_conditions
    assert performance.wait_actions == 1
    assert performance.move_actions == 0
    assert performance.operate_actions == 0
    assert performance.take_actions == 0
    assert performance.drop_actions == 0
    assert performance.finish_actions == 0
    assert performance.rooms_visited == 1
    assert performance.room_revisits == 0
    assert performance.action_delta_from_physical_optimum == (
        performance.actions_used - performance.optimal_physical_actions
    )


def test_successful_terminal_diagnostics_report_no_goal_deficit_and_navigation_counts():
    episode = generate_episode(24003, discovery_level=0, planning_level=1)
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
    assert performance.goal_satisfied is True
    assert performance.unsatisfied_goal_conditions == ()
    assert performance.move_actions >= 1
    assert performance.rooms_visited >= 2
    assert performance.finish_actions == 1


def test_boolean_goal_deficits_preserve_required_expressions():
    from nexus.models.goals import GoalKind, GoalPredicate
    from nexus.protocol.session import _goal_deficits

    episode = generate_episode(24001, discovery_level=0, planning_level=0)
    state = episode.public.initial_state
    yes = GoalPredicate(kind=GoalKind.PHASE_EQUALS, value=state.phase)
    no = GoalPredicate(kind=GoalKind.PHASE_EQUALS, value=state.phase + 1)
    disjunction = GoalPredicate(kind=GoalKind.OR, children=(yes, no))
    assert _goal_deficits(disjunction, state) == ()
    negation = GoalPredicate(kind=GoalKind.NOT, children=(yes,))
    assert _goal_deficits(negation, state) == (f"not(phase_equals:{state.phase})",)
    false_or = GoalPredicate(kind=GoalKind.OR, children=(no, negation))
    conjunction = GoalPredicate(kind=GoalKind.AND, children=(disjunction, false_or))
    assert _goal_deficits(conjunction, state) == (
        f"or(phase_equals:{state.phase + 1},not(phase_equals:{state.phase}))",
    )
