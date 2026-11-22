from itertools import product

import pytest
from pydantic import ValidationError

from nexus.engine import (
    apply_effect,
    canonical_hash,
    evaluate_condition,
    execute_with_trace,
    replay,
    step,
)
from nexus.engine.rules import ARTIFACT_FIELDS, ORIENTATIONS
from nexus.generator.rules import transformation_rule_catalog
from nexus.models import (
    Artifact,
    Condition,
    ConditionKind,
    Effect,
    EffectKind,
    FinishAction,
    GoalKind,
    GoalPredicate,
    Machine,
    MoveAction,
    OperateAction,
    Orientation,
    Pattern,
    Polarity,
    PrivateEpisode,
    PublicEpisode,
    Resources,
    Room,
    Shape,
    TakeAction,
    TerminalStatus,
    WorldState,
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


@pytest.mark.parametrize("payload", [
    {"kind": "phase_equals", "value": value} for value in (False, True, 0.5, "0")
] + [
    {"kind": "artifact_field", "artifact_id": "A1", "field": field, "value": 0}
    for field in ("missing", "location", "id", "sample")
] + [
    {"kind": "artifact_field", "artifact_id": "A1", "field": "value", "value": value}
    for value in (False, True, 0.5, "0")
] + [
    {"kind": "artifact_field", "artifact_id": "A1", "field": "shape", "value": "hexagon"},
    {"kind": "artifact_location", "artifact_id": "A1", "value": 0},
])
def test_invalid_goal_atoms_fail_before_play(payload):
    with pytest.raises(ValueError):
        GoalPredicate.model_validate(payload)


@pytest.mark.parametrize("value", [False, True, 0.5, "0"])
def test_rule_phase_conditions_do_not_coerce_the_declared_phase(value):
    with pytest.raises(ValueError):
        Condition(kind="phase_equals", value=value)


def _reference_apply_effect(effect: Effect, artifact: Artifact, phase: int) -> Artifact:
    """Pre-optimization recursive-copy semantics for differential proof."""
    result = artifact.model_copy(deep=True)
    kind = effect.kind
    if kind == EffectKind.ADD_MOD:
        assert effect.amount is not None and effect.modulus is not None
        result.value = (result.value + effect.amount) % effect.modulus
        return result
    if kind == EffectKind.MULTIPLY_MOD:
        assert effect.multiplier is not None and effect.modulus is not None
        result.value = (result.value * effect.multiplier) % effect.modulus
        return result
    if kind == EffectKind.TOGGLE:
        result.polarity = Polarity.NEGATIVE if result.polarity == Polarity.POSITIVE else Polarity.POSITIVE
        return result
    if kind == EffectKind.ROTATE:
        assert effect.amount is not None
        idx = ORIENTATIONS.index(result.orientation)
        result.orientation = ORIENTATIONS[(idx + effect.amount) % len(ORIENTATIONS)]
        return result
    if kind == EffectKind.SET:
        if effect.field not in ARTIFACT_FIELDS:
            raise ValueError(f"unsupported set field {effect.field!r}")
        setattr(result, effect.field, effect.value)
        return Artifact.model_validate(result.model_dump())
    if kind == EffectKind.SEQUENCE:
        for child in effect.effects:
            result = _reference_apply_effect(child, result, phase)
        return result
    if kind == EffectKind.CONDITIONAL:
        assert effect.condition is not None
        branch = effect.effects if evaluate_condition(effect.condition, result, phase) else effect.else_effects
        for child in branch:
            result = _reference_apply_effect(child, result, phase)
        return result
    raise ValueError(f"unsupported effect kind {kind}")


@pytest.mark.slow
def test_apply_effect_matches_recursive_copy_reference_over_generated_domain():
    for rule in transformation_rule_catalog():
        for shape, phase, value, orientation, polarity in product(
            tuple(Shape), (0, 1), range(11), tuple(Orientation), tuple(Polarity)
        ):
            artifact = Artifact(
                id="A", location="R0", shape=shape, pattern=Pattern.STRIPED,
                orientation=orientation, value=value, polarity=polarity,
            )
            before = artifact.model_copy(deep=True)
            expected = _reference_apply_effect(rule, artifact, phase)
            actual = apply_effect(rule, artifact, phase)
            assert actual == expected
            assert artifact == before
            assert actual is not artifact


def test_apply_effect_matches_reference_for_generic_nested_ast_and_set_normalization():
    conditions = (
        Condition(kind=ConditionKind.ALWAYS),
        Condition(kind=ConditionKind.PHASE_EQUALS, value=2),
        Condition(kind=ConditionKind.VALUE_MODULO, modulus=3, remainder=1),
        Condition(kind=ConditionKind.OR, children=(
            Condition(kind=ConditionKind.EQUALS, field="pattern", value=Pattern.DOTTED.value),
            Condition(kind=ConditionKind.NOT, children=(Condition(kind=ConditionKind.PHASE_PARITY, parity="odd"),)),
        )),
    )
    artifact = Artifact(
        id="A", location="R0", shape=Shape.SQUARE, pattern=Pattern.DOTTED,
        orientation=Orientation.WEST, value=4, polarity=Polarity.NEGATIVE,
    )
    for condition in conditions:
        rule = Effect(
            kind=EffectKind.CONDITIONAL,
            condition=condition,
            effects=(Effect(kind=EffectKind.SEQUENCE, effects=(
                Effect(kind=EffectKind.SET, field="shape", value=Shape.CIRCLE.value),
                Effect(kind=EffectKind.SET, field="pattern", value=Pattern.PLAIN.value),
                Effect(kind=EffectKind.ADD_MOD, field="value", amount=3, modulus=11),
            )),),
            else_effects=(Effect(kind=EffectKind.ROTATE, amount=2),),
        )
        for phase in range(4):
            assert apply_effect(rule, artifact, phase) == _reference_apply_effect(rule, artifact, phase)
    assert artifact.shape == Shape.SQUARE
    assert artifact.pattern == Pattern.DOTTED


@pytest.mark.parametrize("kind,parameter", [("add_mod", "amount"), ("multiply_mod", "multiplier")])
def test_arithmetic_rule_cannot_leave_declared_artifact_value_domain(kind, parameter):
    with pytest.raises(ValidationError, match="artifact domain"):
        Effect(kind=kind, field="value", modulus=100, **{parameter: 50})
    assert Effect(kind=kind, field="value", modulus=11, **{parameter: 50}).modulus == 11
