import hashlib

import pytest

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import execute_with_trace, replay
from nexus.generator import generate_episode, qualify_episode
from nexus.generator.evidence import candidates_matching_csv
from nexus.generator.rules import enumerate_transformation_rules
from nexus.models import ACTION_ADAPTER, ConditionKind, TerminalStatus
from nexus.models.actions import DropAction
from nexus.models.goals import GoalPredicate
from nexus.models.world import Artifact
from nexus.solver import solve


def test_rule_catalog_has_structural_variety():
    rules = enumerate_transformation_rules()
    assert len(rules) == 288
    assert len({rule.model_dump_json() for rule in rules}) == len(rules)

    top_condition_kinds = {rule.condition.kind for rule in rules if rule.condition is not None}
    assert ConditionKind.AND in top_condition_kinds
    assert ConditionKind.OR in top_condition_kinds
    assert any(
        child.kind == ConditionKind.NOT
        for rule in rules
        if rule.condition is not None
        for child in rule.condition.children
    )


def test_generated_evidence_is_unique():
    episode = generate_episode(12345)
    candidates = candidates_matching_csv(
        episode.public.evidence_files["measurements.csv"], enumerate_transformation_rules()
    )
    assert len(candidates) == 1
    assert candidates[0] == episode.rules["machine-rule"]


def test_generator_solver_replay_and_qualification():
    episode = generate_episode(7)
    solved = solve(episode)
    assert solved.solvable
    assert 8 <= solved.optimal_action_count <= 15
    final, trace = execute_with_trace(episode, list(solved.plan))
    assert final.terminal_status == TerminalStatus.WON
    assert replay(episode, trace) == final

    report = qualify_episode(episode)
    assert report.passed, report.model_dump()
    assert report.checks["evidence_matches_hidden_rule"]
    assert report.checks["compositional_rule"]
    assert report.metrics["rule_ast_nodes"] >= 8
    assert report.metrics["rule_ast_depth"] >= 3


def test_reference_plan_is_structured_actions():
    episode = generate_episode(99)
    actions = [ACTION_ADAPTER.validate_python(item) for item in episode.reference_plan]
    assert actions


def test_solver_prunes_drops_that_cannot_satisfy_any_location_goal():
    from nexus.models.world import Artifact, Orientation, Pattern, Polarity, Shape
    from nexus.solver.search import legal_solver_actions

    episode = generate_episode(6060, discovery_level=0, planning_level=1)
    episode.public.initial_state.artifacts["A2"] = Artifact(
        id="A2",
        location="@inventory",
        shape=Shape.CIRCLE,
        pattern=Pattern.PLAIN,
        orientation=Orientation.NORTH,
        value=0,
        polarity=Polarity.POSITIVE,
    )
    state = episode.public.initial_state.model_copy(deep=True)

    drops = [
        action.artifact
        for action in legal_solver_actions(episode, state)
        if isinstance(action, DropAction)
    ]

    assert "A2" not in drops


def test_solver_prunes_operations_on_artifacts_absent_from_goal():
    from nexus.models.actions import OperateAction
    from nexus.models.world import Orientation, Pattern, Polarity, Shape
    from nexus.solver.search import legal_solver_actions

    episode = generate_episode(6061, discovery_level=0, planning_level=1)
    episode.public.initial_state.artifacts["A2"] = Artifact(
        id="A2",
        location="@inventory",
        shape=Shape.CIRCLE,
        pattern=Pattern.PLAIN,
        orientation=Orientation.NORTH,
        value=0,
        polarity=Polarity.POSITIVE,
    )
    machine = next(iter(episode.public.initial_state.machines.values()))
    state = episode.public.initial_state.model_copy(deep=True)
    state.agent_room = machine.room_id
    state.artifacts["A1"].location = "@inventory"

    operations = [
        action.artifact
        for action in legal_solver_actions(episode, state)
        if isinstance(action, OperateAction)
    ]

    assert "A1" in operations
    assert "A2" not in operations


def test_solver_prunes_operations_on_location_only_goal_artifacts():
    from nexus.models.actions import OperateAction
    from nexus.models.goals import GoalKind
    from nexus.models.world import Artifact, Orientation, Pattern, Polarity, Shape
    from nexus.solver.search import legal_solver_actions

    episode = generate_episode(6062, discovery_level=0, planning_level=1)
    episode.public.initial_state.artifacts["A2"] = Artifact(
        id="A2",
        location="@inventory",
        shape=Shape.CIRCLE,
        pattern=Pattern.PLAIN,
        orientation=Orientation.NORTH,
        value=0,
        polarity=Polarity.POSITIVE,
    )
    episode.public.goal = GoalPredicate(
        kind=GoalKind.AND,
        children=(
            episode.public.goal,
            GoalPredicate(
                kind=GoalKind.ARTIFACT_LOCATION,
                artifact_id="A2",
                value=episode.public.initial_state.agent_room,
            ),
        ),
    )

    machine = next(iter(episode.public.initial_state.machines.values()))
    state = episode.public.initial_state.model_copy(deep=True)
    state.agent_room = machine.room_id
    state.artifacts["A1"].location = "@inventory"

    operations = [
        action.artifact
        for action in legal_solver_actions(episode, state)
        if isinstance(action, OperateAction)
    ]

    assert "A1" in operations
    assert "A2" not in operations


@pytest.mark.parametrize("damage", ["waits", "illegal", "empty", "schema", "after_win"])
def test_qualification_executes_the_stored_reference_plan(damage):
    episode = generate_episode(17, planning_level=0)
    assert qualify_episode(episode).passed
    if damage == "waits":
        episode.reference_plan = tuple({"type": "wait"} for _ in episode.reference_plan)
    elif damage == "illegal":
        episode.reference_plan = ({"type": "take", "artifact": "missing"}, *episode.reference_plan[1:])
    elif damage == "empty":
        episode.reference_plan = ()
    elif damage == "schema":
        episode.reference_plan = ({"type": "unknown"}, *episode.reference_plan[1:])
    else:
        episode.reference_plan = (*episode.reference_plan, {"type": "wait"})
    report = qualify_episode(episode)
    assert not report.passed
    assert not report.checks["reference_plan_wins"]
    assert not report.checks["victory_receipt_present"]


def test_legacy_public_identity_is_secret_backed_without_changing_world(hardened_episode):
    same = generate_episode(42, verifier_secret="hardening-test")
    other = generate_episode(42, verifier_secret="different-secret")
    assert hardened_episode.public.episode_id == same.public.episode_id
    assert hardened_episode.public.episode_id != other.public.episode_id
    assert canonical_hash(hardened_episode.public.initial_state) == canonical_hash(
        other.public.initial_state
    )
    meta = hardened_episode.generation_metadata
    known_family = meta.scenario_family_id
    public_id = hardened_episode.public.episode_id
    # All old public IDs were 16 hex characters; new IDs are HMAC-derived.
    assert len(public_id) == 32
    assert public_id != hashlib.sha256(known_family.encode()).hexdigest()[:16]
