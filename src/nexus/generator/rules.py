from __future__ import annotations

from functools import lru_cache
from itertools import product

from nexus.models.rules import Condition, ConditionKind, Effect, EffectKind
from nexus.models.world import Shape

ADD_AMOUNTS = (1, 2, 3, 4)
THEN_ROTATIONS = (1, 2, 3)
MULTIPLIERS = (2, 3, 4)
ELSE_ROTATIONS = (1, 2, 3)
PARITIES = ("even", "odd")


def transformation_rule(
    *,
    shape: Shape,
    parity: str,
    add_amount: int,
    then_rotation: int,
    multiplier: int,
    else_rotation: int,
) -> Effect:
    condition = Condition(
        kind=ConditionKind.AND,
        children=(
            Condition(kind=ConditionKind.EQUALS, field="shape", value=shape.value),
            Condition(kind=ConditionKind.PHASE_PARITY, parity=parity),
        ),
    )
    return Effect(
        kind=EffectKind.CONDITIONAL,
        condition=condition,
        effects=(
            Effect(
                kind=EffectKind.SEQUENCE,
                effects=(
                    Effect(kind=EffectKind.ADD_MOD, field="value", amount=add_amount, modulus=11),
                    Effect(kind=EffectKind.TOGGLE, field="polarity"),
                    Effect(kind=EffectKind.ROTATE, amount=then_rotation),
                ),
            ),
        ),
        else_effects=(
            Effect(
                kind=EffectKind.SEQUENCE,
                effects=(
                    Effect(
                        kind=EffectKind.MULTIPLY_MOD,
                        field="value",
                        multiplier=multiplier,
                        modulus=11,
                    ),
                    Effect(kind=EffectKind.ROTATE, amount=else_rotation),
                ),
            ),
        ),
    )


@lru_cache(maxsize=1)
def transformation_rule_catalog() -> tuple[Effect, ...]:
    return tuple(
        transformation_rule(
            shape=shape,
            parity=parity,
            add_amount=add_amount,
            then_rotation=then_rotation,
            multiplier=multiplier,
            else_rotation=else_rotation,
        )
        for shape, parity, add_amount, then_rotation, multiplier, else_rotation in product(
            tuple(Shape),
            PARITIES,
            ADD_AMOUNTS,
            THEN_ROTATIONS,
            MULTIPLIERS,
            ELSE_ROTATIONS,
        )
    )


def enumerate_transformation_rules() -> list[Effect]:
    return list(transformation_rule_catalog())
