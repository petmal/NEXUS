from __future__ import annotations

from nexus.models.rules import Condition, ConditionKind, Effect, EffectKind
from nexus.models.world import Shape

CONSTRUCTOR_VALUE = 10
DISTRACTOR_VALUE = 7
MISSION_TARGET_VALUE = 9
MISSION_MISS_VALUE = 8


def _set_value(value: int) -> Effect:
    return Effect(kind=EffectKind.SET, field="value", value=value)


def constant_value_rule(value: int) -> Effect:
    """A deterministic calibration-machine law that sets only artifact value."""
    return _set_value(value)


def constructed_mission_rule(
    winning_phase: int,
    diagnostic_shape: Shape,
) -> Effect:
    """Compose one D5 M1 law.

    The law has a public diagnostic context plus one hidden winning phase. The diagnostic branch
    emits the winning phase as an observable marker. Outside that context, only operating at the
    hidden winning phase reaches the public target value.
    """
    if not 0 <= winning_phase < 4:
        raise ValueError("winning_phase must be in 0..3")

    diagnostic_condition = Condition(
        kind=ConditionKind.AND,
        children=(
            Condition(
                kind=ConditionKind.EQUALS,
                field="shape",
                value=diagnostic_shape.value,
            ),
            Condition(
                kind=ConditionKind.EQUALS,
                field="value",
                value=CONSTRUCTOR_VALUE,
            ),
        ),
    )
    mission_branch = Effect(
        kind=EffectKind.CONDITIONAL,
        condition=Condition(kind=ConditionKind.PHASE_EQUALS, value=winning_phase),
        effects=(_set_value(MISSION_TARGET_VALUE),),
        else_effects=(_set_value(MISSION_MISS_VALUE),),
    )
    return Effect(
        kind=EffectKind.CONDITIONAL,
        condition=diagnostic_condition,
        effects=(_set_value(winning_phase),),
        else_effects=(mission_branch,),
    )


def constructed_mission_rules(diagnostic_shape: Shape) -> tuple[Effect, ...]:
    """Enumerate the complete four-hypothesis D5 M1 family."""
    return tuple(
        constructed_mission_rule(winning_phase, diagnostic_shape)
        for winning_phase in range(4)
    )


def constructed_manual(diagnostic_shape: Shape) -> str:
    """Player-facing D5 grammar.

    This profile changes generated law content, not the interaction mechanics. Probe and operate
    retain exactly the same semantics as every earlier discovery level.
    """
    return f"""NEXUS TRANSFORMATION FACILITY — CONSTRUCTED EXPERIMENT REFERENCE

All ordinary NEXUS action semantics are unchanged. In particular, probe remains a non-destructive
one-action hypothetical machine application, and operate changes the real artifact and consumes a
machine use.

MISSION MACHINE M1

M1 has one hidden winning phase K, where K is exactly one of 0, 1, 2, 3.

M1 has a diagnostic input context:
- artifact shape is {diagnostic_shape.value}
- artifact value is {CONSTRUCTOR_VALUE}

On that diagnostic context, M1 sets artifact value to K and leaves the other artifact fields
unchanged. A probe of that context therefore identifies the hidden winning phase.

On every other input:
- at phase K, M1 sets artifact value to {MISSION_TARGET_VALUE};
- at every other phase, M1 sets artifact value to {MISSION_MISS_VALUE};
- other artifact fields are unchanged.

CALIBRATION MACHINES

M2 sets artifact value to {CONSTRUCTOR_VALUE} and leaves every other artifact field unchanged.
M3 sets artifact value to {DISTRACTOR_VALUE} and leaves every other artifact field unchanged.

The machines are deterministic. Their behavior does not depend on room, turn number, or prior
experiments. A machine may be probed or operated on any carried artifact subject to its remaining
uses.

MISSION

Only A1 contributes directly to the success predicate. A2 and A3 are ordinary auxiliary samples.
They may still be useful—or wasteful—because actions on them can change what future experiments
are possible.
"""
