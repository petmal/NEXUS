from __future__ import annotations

from itertools import product

import pytest

import nexus.generator as generator_module
import nexus.solver.belief as belief_module
from nexus.cli import app
from nexus.engine.rules import ARTIFACT_FIELDS, ORIENTATIONS, apply_effect, evaluate_condition
from nexus.generator.generator import _generate_episode_core
from nexus.generator.rules import transformation_rule_catalog
from nexus.models.actions import ProbeAction
from nexus.models.rules import Condition, ConditionKind, Effect, EffectKind
from nexus.models.world import Artifact, Orientation, Pattern, Polarity, Shape
from nexus.solver.belief import (
    _POLICY_RESULT_CACHE,
    _episode_for_hypothesis,
    _normalize_fresh_state,
    _normalize_state,
    solve_guaranteed_policy,
)
from typer.testing import CliRunner

import importlib.util
from pathlib import Path

_helper_path = Path("tests/unit/test_solver_performance_invariants.py")
_spec = importlib.util.spec_from_file_location("nexus_solver_perf_helpers", _helper_path)
assert _spec is not None and _spec.loader is not None
_helpers = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_helpers)
_episode = _helpers._episode
_rule = _helpers._rule
_set = _helpers._set


runner = CliRunner()


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


def test_fresh_state_normalization_matches_copying_normalization_without_source_mutation():
    source = _episode().public.initial_state
    before = source.model_copy(deep=True)
    fresh = source.model_copy(deep=True)
    fresh.turn = 9
    fresh.resources.actions_remaining = 1
    expected = _normalize_state(fresh, 777)
    actual = _normalize_fresh_state(fresh, 777)
    assert actual == expected
    assert actual is fresh
    assert source == before


def test_hypothesis_episode_targeted_copy_matches_deep_copy_and_is_isolated():
    episode = _episode()
    replacement = _rule(1, 9)
    reference = episode.model_copy(deep=True)
    reference.public.initial_state.resources.actions_remaining = 777
    reference.rules[reference.machine_rules["M1"]] = replacement

    candidate = _episode_for_hypothesis(episode, {"M1": replacement}, search_budget=777)
    sibling = _episode_for_hypothesis(episode, {"M1": _rule(2, 8)}, search_budget=888)
    assert candidate.model_dump(mode="python") == reference.model_dump(mode="python")

    candidate.public.initial_state.agent_room = "mutated"
    candidate.rules["extra"] = _set(7)
    assert episode.public.initial_state.agent_room == "R0"
    assert "extra" not in episode.rules
    assert sibling.public.initial_state.agent_room == "R0"
    assert "extra" not in sibling.rules
    assert sibling.public.initial_state.resources.actions_remaining == 888


def test_rich_policy_cache_can_satisfy_weaker_exact_query(monkeypatch):
    _POLICY_RESULT_CACHE.clear()
    episode = _episode()
    candidates = {"M1": [_rule(0, 4), _rule(1, 5), _rule(2, 6)]}
    rich = solve_guaranteed_policy(
        episode,
        candidate_rules_by_machine=candidates,
        max_actions=10,
        requested_action_values=(ProbeAction(machine="M1", artifact="A1"),),
    )
    assert rich.solvable and rich.optimal_worst_case_actions is not None
    cache_size = len(_POLICY_RESULT_CACHE)

    def fail_physical(*args, **kwargs):
        raise AssertionError("weaker query recomputed instead of reusing richer exact result")

    monkeypatch.setattr(belief_module, "solve_compressed_physical", fail_physical)
    weaker = solve_guaranteed_policy(
        episode,
        candidate_rules_by_machine=candidates,
        max_actions=rich.optimal_worst_case_actions,
        expected_actions=rich.optimal_worst_case_actions,
        include_action_values=False,
    )
    assert weaker.solvable
    assert weaker.optimal_worst_case_actions == rich.optimal_worst_case_actions
    assert weaker.witness == rich.witness
    assert weaker.initial_action_values == ()
    assert len(_POLICY_RESULT_CACHE) == cache_size
    _POLICY_RESULT_CACHE.clear()


def test_exhausted_rich_cache_does_not_overstate_larger_proof_bound(monkeypatch):
    _POLICY_RESULT_CACHE.clear()
    episode = _episode()
    candidates = {"M1": [_rule(0, 4), _rule(1, 5), _rule(2, 6)]}
    too_small = solve_guaranteed_policy(
        episode,
        candidate_rules_by_machine=candidates,
        max_actions=1,
        requested_action_values=(ProbeAction(machine="M1", artifact="A1"),),
    )
    assert not too_small.solvable
    calls = 0
    original = belief_module.solve_compressed_physical

    def counted(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(belief_module, "solve_compressed_physical", counted)
    larger = solve_guaranteed_policy(
        episode,
        candidate_rules_by_machine=candidates,
        max_actions=10,
        include_action_values=False,
    )
    assert larger.solvable
    assert calls > 0
    _POLICY_RESULT_CACHE.clear()


def test_cli_generate_does_not_repeat_qualification(monkeypatch, tmp_path):
    # Build the qualified return value before replacing the public generator entry point.
    episode = _generate_episode_core(
        17017, discovery_level=2, planning_level=0, verifier_secret="proof"
    )
    monkeypatch.setattr(generator_module, "generate_episode", lambda *args, **kwargs: episode)

    def unexpected_qualification(*args, **kwargs):
        raise AssertionError("CLI repeated final qualification")

    monkeypatch.setattr(generator_module, "qualify_episode", unexpected_qualification)
    result = runner.invoke(app, ["generate", str(tmp_path / "episode"), "--seed", "1"])
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / "episode" / "private.json").exists()
