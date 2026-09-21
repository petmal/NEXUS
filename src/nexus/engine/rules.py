from __future__ import annotations

from nexus.models.rules import Condition, ConditionKind, Effect, EffectKind
from nexus.models.world import Artifact, Orientation, Polarity

ORIENTATIONS = [Orientation.NORTH, Orientation.EAST, Orientation.SOUTH, Orientation.WEST]
ARTIFACT_FIELDS = {"shape", "pattern", "orientation", "value", "polarity"}


def _normalized(value):
    return value.value if hasattr(value, "value") else value


def evaluate_condition(condition: Condition, artifact: Artifact, phase: int) -> bool:
    kind = condition.kind
    if kind == ConditionKind.ALWAYS:
        return True
    if kind == ConditionKind.EQUALS:
        if condition.field not in ARTIFACT_FIELDS:
            raise ValueError(f"unsupported artifact field {condition.field!r}")
        return _normalized(getattr(artifact, condition.field)) == _normalized(condition.value)
    if kind == ConditionKind.PHASE_EQUALS:
        return phase == int(condition.value)
    if kind == ConditionKind.PHASE_PARITY:
        return (phase % 2 == 0) == (condition.parity == "even")
    if kind == ConditionKind.VALUE_MODULO:
        assert condition.modulus is not None and condition.remainder is not None
        return artifact.value % condition.modulus == condition.remainder
    if kind == ConditionKind.AND:
        return all(evaluate_condition(c, artifact, phase) for c in condition.children)
    if kind == ConditionKind.OR:
        return any(evaluate_condition(c, artifact, phase) for c in condition.children)
    if kind == ConditionKind.NOT:
        return not evaluate_condition(condition.children[0], artifact, phase)
    raise ValueError(f"unsupported condition kind {kind}")


def apply_effect(effect: Effect, artifact: Artifact, phase: int) -> Artifact:
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
        result.polarity = (
            Polarity.NEGATIVE if result.polarity == Polarity.POSITIVE else Polarity.POSITIVE
        )
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
            result = apply_effect(child, result, phase)
        return result
    if kind == EffectKind.CONDITIONAL:
        assert effect.condition is not None
        branch = effect.effects if evaluate_condition(effect.condition, result, phase) else effect.else_effects
        for child in branch:
            result = apply_effect(child, result, phase)
        return result
    raise ValueError(f"unsupported effect kind {kind}")
