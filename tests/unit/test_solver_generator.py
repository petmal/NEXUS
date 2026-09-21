from nexus.engine.replay import execute_with_trace, replay
from nexus.generator import generate_episode, qualify_episode
from nexus.generator.evidence import candidates_matching_csv
from nexus.generator.rules import enumerate_transformation_rules
from nexus.models import ACTION_ADAPTER, ConditionKind, TerminalStatus
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
