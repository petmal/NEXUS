from nexus.models.actions import OperateAction, ProbeAction
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
    WorldState,
)
from nexus.solver.belief import solve_guaranteed_policy


def _artifact(artifact_id: str, shape: Shape) -> Artifact:
    return Artifact(
        id=artifact_id,
        location="@inventory",
        shape=shape,
        pattern=Pattern.PLAIN,
        orientation=Orientation.NORTH,
        value=0,
        polarity=Polarity.POSITIVE,
    )


def _set_value(value: int) -> Effect:
    return Effect(kind=EffectKind.SET, field="value", value=value)


def _phase_rule(target_phase: int) -> Effect:
    return Effect(
        kind=EffectKind.CONDITIONAL,
        condition=Condition(kind=ConditionKind.PHASE_EQUALS, value=target_phase),
        effects=(_set_value(1),),
        else_effects=(_set_value(3),),
    )


def _selective_rule(target_phase: int, circle_code: int) -> Effect:
    square_phase = Effect(
        kind=EffectKind.CONDITIONAL,
        condition=Condition(kind=ConditionKind.PHASE_EQUALS, value=target_phase),
        effects=(_set_value(1),),
        else_effects=(_set_value(3),),
    )
    non_circle = Effect(
        kind=EffectKind.CONDITIONAL,
        condition=Condition(
            kind=ConditionKind.EQUALS,
            field="shape",
            value=Shape.TRIANGLE.value,
        ),
        effects=(_set_value(7),),
        else_effects=(square_phase,),
    )
    return Effect(
        kind=EffectKind.CONDITIONAL,
        condition=Condition(
            kind=ConditionKind.EQUALS,
            field="shape",
            value=Shape.CIRCLE.value,
        ),
        effects=(_set_value(circle_code),),
        else_effects=(non_circle,),
    )


def _episode(*, artifacts: dict[str, Artifact], phase_modulus: int) -> PrivateEpisode:
    rooms = {"R0": Room(id="R0", label="Lab")}
    public = PublicEpisode(
        episode_id="belief-proof",
        description="proof fixture",
        rooms=rooms,
        edges=(),
        phase_modulus=phase_modulus,
        initial_state=WorldState(
            phase=0,
            agent_room="R0",
            artifacts=artifacts,
            machines={"M1": Machine(id="M1", room_id="R0", uses_remaining=1)},
            resources=Resources(actions_remaining=96),
        ),
        goal=GoalPredicate(
            kind=GoalKind.ARTIFACT_FIELD,
            artifact_id="A1",
            field="value",
            value=1,
        ),
    )
    return PrivateEpisode(
        public=public,
        rules={"machine-rule": _phase_rule(0)},
        machine_rules={"M1": "machine-rule"},
        verifier_secret="belief-proof-secret",
    )


def _probe_value(result, artifact_id: str):
    for value in result.initial_action_values:
        if isinstance(value.action, ProbeAction) and value.action.artifact == artifact_id:
            return value
    raise AssertionError(f"missing probe action for {artifact_id}")


def _probe_cost(result, artifact_id: str) -> int | None:
    return _probe_value(result, artifact_id).worst_case_total_actions


def test_guaranteed_policy_solver_counts_total_action_cost_exactly():
    episode = _episode(
        artifacts={"A1": _artifact("A1", Shape.SQUARE)},
        phase_modulus=2,
    )
    candidates = {"M1": [_phase_rule(0), _phase_rule(1)]}

    result = solve_guaranteed_policy(
        episode,
        candidate_rules_by_machine=candidates,
        max_actions=8,
    )

    assert result.solvable
    assert result.viable_hypothesis_count == 2
    assert result.optimal_worst_case_actions == 4
    assert _probe_cost(result, "A1") == 4


def test_auxiliary_circle_probe_is_cheaper_than_square_bruteforce_and_triangle_is_useless():
    episode = _episode(
        artifacts={
            "A1": _artifact("A1", Shape.SQUARE),
            "A2": _artifact("A2", Shape.CIRCLE),
            "A3": _artifact("A3", Shape.TRIANGLE),
        },
        phase_modulus=3,
    )
    candidates = {
        "M1": [
            _selective_rule(0, 4),
            _selective_rule(1, 5),
            _selective_rule(2, 6),
        ]
    }

    result = solve_guaranteed_policy(
        episode,
        candidate_rules_by_machine=candidates,
        max_actions=10,
    )

    assert result.solvable
    assert result.viable_hypothesis_count == 3
    assert result.optimal_worst_case_actions == 5

    circle_cost = _probe_cost(result, "A2")
    square_cost = _probe_cost(result, "A1")
    triangle_cost = _probe_cost(result, "A3")

    assert circle_cost == 5
    assert square_cost == 6
    assert triangle_cost == 6
    assert circle_cost < square_cost
    assert _probe_value(result, "A2").outcome_count == 3
    assert _probe_value(result, "A2").discriminative is True
    assert _probe_value(result, "A3").outcome_count == 1
    assert _probe_value(result, "A3").discriminative is False



def _diagnostic_phase_rule(winning_phase: int) -> Effect:
    diagnostic = Condition(
        kind=ConditionKind.AND,
        children=(
            Condition(
                kind=ConditionKind.EQUALS,
                field="shape",
                value=Shape.CIRCLE.value,
            ),
            Condition(
                kind=ConditionKind.EQUALS,
                field="value",
                value=10,
            ),
        ),
    )
    mission_branch = Effect(
        kind=EffectKind.CONDITIONAL,
        condition=Condition(kind=ConditionKind.PHASE_EQUALS, value=winning_phase),
        effects=(_set_value(9),),
        else_effects=(_set_value(8),),
    )
    return Effect(
        kind=EffectKind.CONDITIONAL,
        condition=diagnostic,
        effects=(_set_value(winning_phase),),
        else_effects=(mission_branch,),
    )


def _constructed_experiment_episode() -> PrivateEpisode:
    rooms = {"R0": Room(id="R0", label="Lab")}
    public = PublicEpisode(
        episode_id="constructed-belief-proof",
        description="constructed experiment proof fixture",
        rooms=rooms,
        edges=(),
        phase_modulus=4,
        initial_state=WorldState(
            phase=0,
            agent_room="R0",
            artifacts={
                "A1": _artifact("A1", Shape.SQUARE),
                "A2": _artifact("A2", Shape.CIRCLE),
                "A3": _artifact("A3", Shape.TRIANGLE),
            },
            machines={
                "M1": Machine(id="M1", room_id="R0", uses_remaining=1),
                "M2": Machine(id="M2", room_id="R0", uses_remaining=1),
                "M3": Machine(id="M3", room_id="R0", uses_remaining=1),
            },
            resources=Resources(actions_remaining=96),
        ),
        goal=GoalPredicate(
            kind=GoalKind.ARTIFACT_FIELD,
            artifact_id="A1",
            field="value",
            value=9,
        ),
    )
    return PrivateEpisode(
        public=public,
        rules={
            "mission-rule": _diagnostic_phase_rule(2),
            "constructor-rule": _set_value(10),
            "distractor-rule": _set_value(7),
        },
        machine_rules={
            "M1": "mission-rule",
            "M2": "constructor-rule",
            "M3": "distractor-rule",
        },
        verifier_secret="constructed-belief-proof-secret",
    )


def _initial_action_value(result, action_type, machine_id: str, artifact_id: str):
    for value in result.initial_action_values:
        action = value.action
        if (
            isinstance(action, action_type)
            and action.machine == machine_id
            and action.artifact == artifact_id
        ):
            return value
    raise AssertionError(
        f"missing initial {action_type.__name__} for {machine_id}/{artifact_id}"
    )


def test_non_goal_operation_can_construct_the_unique_lower_cost_experiment():
    episode = _constructed_experiment_episode()
    candidates = {
        "M1": [_diagnostic_phase_rule(phase) for phase in range(4)],
        "M2": [_set_value(10)],
        "M3": [_set_value(7)],
    }

    result = solve_guaranteed_policy(
        episode,
        candidate_rules_by_machine=candidates,
        max_actions=12,
    )

    assert result.solvable
    assert result.viable_hypothesis_count == 4
    assert result.optimal_worst_case_actions == 7

    constructor = _initial_action_value(result, OperateAction, "M2", "A2")
    direct_probe = _initial_action_value(result, ProbeAction, "M1", "A1")
    distractor = _initial_action_value(result, OperateAction, "M3", "A3")

    assert constructor.worst_case_total_actions == 7
    assert direct_probe.worst_case_total_actions == 8
    assert distractor.worst_case_total_actions is not None
    assert distractor.worst_case_total_actions > 7
