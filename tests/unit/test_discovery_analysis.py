from nexus.generator.discovery import analyze_discovery
from nexus.models.rules import Condition, ConditionKind, Effect, EffectKind
from nexus.models.world import Artifact, Orientation, Pattern, Polarity, Shape


def _artifact(value: int) -> Artifact:
    return Artifact(
        id="A1",
        location="@inventory",
        shape=Shape.SQUARE,
        pattern=Pattern.PLAIN,
        orientation=Orientation.NORTH,
        value=value,
        polarity=Polarity.POSITIVE,
    )


def _set_value(value: int) -> Effect:
    return Effect(kind=EffectKind.SET, field="value", value=value)


def _phase_rule(phase: int, then_value: int, else_value: int) -> Effect:
    return Effect(
        kind=EffectKind.CONDITIONAL,
        condition=Condition(kind=ConditionKind.PHASE_EQUALS, value=phase),
        effects=(_set_value(then_value),),
        else_effects=(_set_value(else_value),),
    )


def _experiments_by_phase(analysis):
    return {item.phase: item for item in analysis.experiments if item.machine_id == "M1"}


def _commitments_by_phase(analysis):
    return {item.phase: item for item in analysis.commitments if item.machine_id == "M1"}


def test_experiment_analysis_distinguishes_zero_information_and_mission_relevant_probes():
    # Both rules are individually winnable, but require different phases. Phase 2 produces the
    # same useless observation in both worlds. Phase 0/1 separates the worlds and permits a
    # guaranteed subsequent commitment.
    rules = [
        _phase_rule(0, then_value=1, else_value=3),
        _phase_rule(1, then_value=1, else_value=3),
    ]
    analysis = analyze_discovery(
        candidate_rules_by_machine={"M1": rules},
        initial_artifact=_artifact(0),
        target_artifact=_artifact(1),
        phase_modulus=3,
    )

    assert analysis.minimum_guaranteed_probes == 1
    experiments = _experiments_by_phase(analysis)

    assert experiments[2].outcome_count == 1
    assert experiments[2].discriminative is False
    assert experiments[2].mission_relevant is False

    assert experiments[0].outcome_count == 2
    assert experiments[0].discriminative is True
    assert experiments[0].mission_relevant is True
    assert experiments[0].worst_case_remaining_probes == 0

    commitments = _commitments_by_phase(analysis)
    assert commitments[0].guaranteed_safe is False
    assert commitments[0].risky is True
    assert commitments[1].guaranteed_safe is False
    assert commitments[1].risky is True


def test_discriminative_probe_can_be_mission_irrelevant_when_a_safe_policy_needs_no_probe():
    # Both hypotheses reach the target at phase 0, so causal identity is irrelevant to the
    # mission. They disagree at phase 1, making that probe informative about the hidden law but
    # useless for improving the guaranteed winning policy.
    rules = [
        _phase_rule(1, then_value=2, else_value=1),
        _phase_rule(1, then_value=3, else_value=1),
    ]
    analysis = analyze_discovery(
        candidate_rules_by_machine={"M1": rules},
        initial_artifact=_artifact(0),
        target_artifact=_artifact(1),
        phase_modulus=2,
    )

    assert analysis.minimum_guaranteed_probes == 0
    experiments = _experiments_by_phase(analysis)

    assert experiments[1].outcome_count == 2
    assert experiments[1].discriminative is True
    assert experiments[1].mission_relevant is False
    assert experiments[1].worst_case_remaining_probes == 0

    commitments = _commitments_by_phase(analysis)
    assert commitments[0].guaranteed_safe is True
    assert commitments[0].risky is False
    assert commitments[1].guaranteed_safe is False
    assert commitments[1].risky is True


def test_analysis_reports_no_decisions_when_no_hypothesis_is_viable():
    rules = [_phase_rule(0, then_value=2, else_value=3)]
    analysis = analyze_discovery(
        candidate_rules_by_machine={"M1": rules},
        initial_artifact=_artifact(0),
        target_artifact=_artifact(1),
        phase_modulus=2,
    )

    assert analysis.viable_hypothesis_count == 0
    assert analysis.minimum_guaranteed_probes is None
    assert analysis.experiments == ()
    assert analysis.commitments == ()
