from nexus.engine import apply_effect, canonical_hash, evaluate_condition, execute_with_trace, replay, step
from nexus.models import (
    Artifact, Condition, ConditionKind, Effect, EffectKind, FinishAction, GoalKind, GoalPredicate,
    Machine, MoveAction, OperateAction, Orientation, Pattern, Polarity, PrivateEpisode, PublicEpisode,
    Resources, Room, Shape, TakeAction, TerminalStatus, WorldState,
)


def build_episode() -> PrivateEpisode:
    artifact = Artifact(
        id="A1", location="R0", shape=Shape.TRIANGLE, pattern=Pattern.STRIPED,
        orientation=Orientation.NORTH, value=2, polarity=Polarity.NEGATIVE,
    )
    machine = Machine(id="M1", room_id="R1", uses_remaining=1)
    state = WorldState(
        agent_room="R0", artifacts={"A1": artifact}, machines={"M1": machine},
        resources=Resources(actions_remaining=8),
    )
    condition = Condition(
        kind=ConditionKind.AND,
        children=(
            Condition(kind=ConditionKind.EQUALS, field="shape", value="triangle"),
            Condition(kind=ConditionKind.PHASE_PARITY, parity="even"),
        ),
    )
    rule = Effect(
        kind=EffectKind.CONDITIONAL,
        condition=condition,
        effects=(Effect(kind=EffectKind.SEQUENCE, effects=(
            Effect(kind=EffectKind.ADD_MOD, field="value", amount=3, modulus=11),
            Effect(kind=EffectKind.TOGGLE, field="polarity"),
            Effect(kind=EffectKind.ROTATE, amount=1),
        )),),
        else_effects=(Effect(kind=EffectKind.MULTIPLY_MOD, field="value", multiplier=2, modulus=11),),
    )
    goal = GoalPredicate(
        kind=GoalKind.AND,
        children=(
            GoalPredicate(kind=GoalKind.ARTIFACT_FIELD, artifact_id="A1", field="value", value=5),
            GoalPredicate(kind=GoalKind.ARTIFACT_FIELD, artifact_id="A1", field="polarity", value="positive"),
            GoalPredicate(kind=GoalKind.ARTIFACT_FIELD, artifact_id="A1", field="orientation", value="east"),
        ),
    )
    public = PublicEpisode(
        episode_id="test", description="test", rooms={"R0": Room(id="R0", label="Start"), "R1": Room(id="R1", label="Lab")},
        edges=(("R0", "R1"),), initial_state=state, goal=goal,
    )
    return PrivateEpisode(public=public, rules={"rule": rule}, machine_rules={"M1": "rule"}, verifier_secret="secret")


def test_compositional_rule():
    episode = build_episode()
    artifact = episode.public.initial_state.artifacts["A1"]
    assert evaluate_condition(episode.rules["rule"].condition, artifact, 0)
    transformed = apply_effect(episode.rules["rule"], artifact, 0)
    assert (transformed.value, transformed.polarity, transformed.orientation) == (5, Polarity.POSITIVE, Orientation.EAST)


def test_invalid_action_does_not_mutate():
    episode = build_episode()
    state = episode.public.initial_state
    before = canonical_hash(state)
    result = step(state, OperateAction(machine="M1", artifact="A1"), episode)
    assert not result.ok
    assert canonical_hash(state) == before == canonical_hash(result.state)


def test_win_and_replay():
    episode = build_episode()
    actions = [TakeAction(artifact="A1"), MoveAction(target="R1"), OperateAction(machine="M1", artifact="A1"), FinishAction()]
    final, trace = execute_with_trace(episode, actions)
    assert final.terminal_status == TerminalStatus.WON
    assert trace[-1].victory_code and trace[-1].victory_code.startswith("NX-")
    assert canonical_hash(replay(episode, trace)) == canonical_hash(final)
