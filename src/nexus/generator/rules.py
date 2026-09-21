from __future__ import annotations

import random
from functools import lru_cache
from itertools import product

from nexus.models.rules import Condition, ConditionKind, Effect, EffectKind
from nexus.models.world import Shape

CONDITION_FORMS = (
    "shape_and_phase",
    "shape_or_phase",
    "not_shape_and_phase",
)

THEN_VARIANTS = (
    "add2_toggle_rotate1",
    "add3_rotate2",
    "multiply2_toggle_rotate3",
    "rotate1_toggle",
)

ELSE_VARIANTS = (
    "multiply3_rotate1",
    "add1_toggle",
    "rotate2",
    "multiply2_toggle_rotate1",
)

PARITIES = ("even", "odd")


def _shape_condition(shape: Shape) -> Condition:
    return Condition(kind=ConditionKind.EQUALS, field="shape", value=shape.value)


def _phase_condition(parity: str) -> Condition:
    return Condition(kind=ConditionKind.PHASE_PARITY, parity=parity)


def compose_condition(form: str, *, shape: Shape, parity: str) -> Condition:
    shape_condition = _shape_condition(shape)
    phase_condition = _phase_condition(parity)

    if form == "shape_and_phase":
        return Condition(
            kind=ConditionKind.AND,
            children=(shape_condition, phase_condition),
        )
    if form == "shape_or_phase":
        return Condition(
            kind=ConditionKind.OR,
            children=(shape_condition, phase_condition),
        )
    if form == "not_shape_and_phase":
        return Condition(
            kind=ConditionKind.AND,
            children=(
                Condition(kind=ConditionKind.NOT, children=(shape_condition,)),
                phase_condition,
            ),
        )
    raise ValueError(f"unknown condition form {form!r}")


def _sequence(*effects: Effect) -> tuple[Effect, ...]:
    return (Effect(kind=EffectKind.SEQUENCE, effects=effects),)


def compose_effect_variant(name: str) -> tuple[Effect, ...]:
    if name == "add2_toggle_rotate1":
        return _sequence(
            Effect(kind=EffectKind.ADD_MOD, field="value", amount=2, modulus=11),
            Effect(kind=EffectKind.TOGGLE, field="polarity"),
            Effect(kind=EffectKind.ROTATE, amount=1),
        )
    if name == "add3_rotate2":
        return _sequence(
            Effect(kind=EffectKind.ADD_MOD, field="value", amount=3, modulus=11),
            Effect(kind=EffectKind.ROTATE, amount=2),
        )
    if name == "multiply2_toggle_rotate3":
        return _sequence(
            Effect(kind=EffectKind.MULTIPLY_MOD, field="value", multiplier=2, modulus=11),
            Effect(kind=EffectKind.TOGGLE, field="polarity"),
            Effect(kind=EffectKind.ROTATE, amount=3),
        )
    if name == "rotate1_toggle":
        return _sequence(
            Effect(kind=EffectKind.ROTATE, amount=1),
            Effect(kind=EffectKind.TOGGLE, field="polarity"),
        )
    if name == "multiply3_rotate1":
        return _sequence(
            Effect(kind=EffectKind.MULTIPLY_MOD, field="value", multiplier=3, modulus=11),
            Effect(kind=EffectKind.ROTATE, amount=1),
        )
    if name == "add1_toggle":
        return _sequence(
            Effect(kind=EffectKind.ADD_MOD, field="value", amount=1, modulus=11),
            Effect(kind=EffectKind.TOGGLE, field="polarity"),
        )
    if name == "rotate2":
        return _sequence(Effect(kind=EffectKind.ROTATE, amount=2))
    if name == "multiply2_toggle_rotate1":
        return _sequence(
            Effect(kind=EffectKind.MULTIPLY_MOD, field="value", multiplier=2, modulus=11),
            Effect(kind=EffectKind.TOGGLE, field="polarity"),
            Effect(kind=EffectKind.ROTATE, amount=1),
        )
    raise ValueError(f"unknown effect variant {name!r}")


def transformation_rule(
    *,
    condition_form: str,
    shape: Shape,
    parity: str,
    then_variant: str,
    else_variant: str,
) -> Effect:
    return Effect(
        kind=EffectKind.CONDITIONAL,
        condition=compose_condition(condition_form, shape=shape, parity=parity),
        effects=compose_effect_variant(then_variant),
        else_effects=compose_effect_variant(else_variant),
    )


def sample_transformation_rule(rng: random.Random) -> Effect:
    """Sample independent grammar components and compose a complete latent law."""
    return transformation_rule(
        condition_form=rng.choice(CONDITION_FORMS),
        shape=rng.choice(tuple(Shape)),
        parity=rng.choice(PARITIES),
        then_variant=rng.choice(THEN_VARIANTS),
        else_variant=rng.choice(ELSE_VARIANTS),
    )


@lru_cache(maxsize=1)
def transformation_rule_catalog() -> tuple[Effect, ...]:
    """Finite hypothesis space used only for exact POC evidence validation."""
    return tuple(
        transformation_rule(
            condition_form=condition_form,
            shape=shape,
            parity=parity,
            then_variant=then_variant,
            else_variant=else_variant,
        )
        for condition_form, shape, parity, then_variant, else_variant in product(
            CONDITION_FORMS,
            tuple(Shape),
            PARITIES,
            THEN_VARIANTS,
            ELSE_VARIANTS,
        )
    )


def enumerate_transformation_rules() -> list[Effect]:
    return list(transformation_rule_catalog())


def rule_ast_metrics(effect: Effect) -> tuple[int, int]:
    """Return (node_count, max_depth) for qualification/diagnostics."""

    def condition_metrics(condition: Condition | None) -> tuple[int, int]:
        if condition is None:
            return 0, 0
        child_metrics = [condition_metrics(child) for child in condition.children]
        count = 1 + sum(item[0] for item in child_metrics)
        depth = 1 + max((item[1] for item in child_metrics), default=0)
        return count, depth

    effect_children = (*effect.effects, *effect.else_effects)
    child_metrics = [rule_ast_metrics(child) for child in effect_children]
    condition_count, condition_depth = condition_metrics(effect.condition)
    count = 1 + condition_count + sum(item[0] for item in child_metrics)
    child_depth = max((item[1] for item in child_metrics), default=0)
    depth = 1 + max(condition_depth, child_depth)
    return count, depth
