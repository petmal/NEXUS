from __future__ import annotations

import json

from pydantic import BaseModel, ConfigDict, Field

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import execute_with_trace, replay
from nexus.generator.evidence import candidates_matching_csv
from nexus.generator.rules import enumerate_transformation_rules, rule_ast_metrics
from nexus.models.actions import ACTION_ADAPTER
from nexus.models.episode import PrivateEpisode
from nexus.models.world import TerminalStatus
from nexus.solver.search import solve


class QualificationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    passed: bool
    checks: dict[str, bool]
    metrics: dict[str, int | str | bool] = Field(default_factory=dict)
    errors: tuple[str, ...] = ()


def qualify_episode(
    episode: PrivateEpisode,
    *,
    min_optimal_actions: int = 8,
    max_optimal_actions: int = 15,
    max_states: int = 100_000,
) -> QualificationReport:
    checks: dict[str, bool] = {}
    errors: list[str] = []
    metrics: dict[str, int | str | bool] = {}

    public_json = episode.public.model_dump_json()
    serialized_rules = [rule.model_dump_json() for rule in episode.rules.values()]
    checks["public_private_separation"] = (
        episode.verifier_secret not in public_json
        and all(
            token not in public_json
            for token in ("construction_seed", "reference_plan", "machine_rules", "verifier_secret")
        )
        and all(serialized_rule not in public_json for serialized_rule in serialized_rules)
    )

    target_rule_id = episode.machine_rules.get("M1")
    target_rule = episode.rules.get(target_rule_id or "")
    evidence = episode.public.evidence_files.get("measurements.csv", "")
    matching = candidates_matching_csv(evidence, enumerate_transformation_rules()) if evidence else []
    checks["evidence_unique"] = len(matching) == 1
    checks["evidence_matches_hidden_rule"] = (
        target_rule is not None and len(matching) == 1 and matching[0] == target_rule
    )
    metrics["evidence_candidate_count"] = len(matching)

    if target_rule is not None:
        node_count, depth = rule_ast_metrics(target_rule)
        metrics["rule_ast_nodes"] = node_count
        metrics["rule_ast_depth"] = depth
        checks["compositional_rule"] = node_count >= 8 and depth >= 3
    else:
        checks["compositional_rule"] = False

    solved = solve(episode, max_states=max_states)
    checks["solver_found_win"] = solved.solvable
    metrics["solver_visited_states"] = solved.visited_states
    metrics["solver_max_frontier_size"] = solved.max_frontier_size
    if solved.optimal_action_count is not None:
        metrics["optimal_action_count"] = solved.optimal_action_count
        checks["difficulty_bounds"] = (
            min_optimal_actions <= solved.optimal_action_count <= max_optimal_actions
        )
    else:
        checks["difficulty_bounds"] = False

    if solved.solvable:
        try:
            final, trace = execute_with_trace(episode, list(solved.plan))
            checks["reference_plan_wins"] = final.terminal_status == TerminalStatus.WON
            replayed = replay(episode, trace)
            checks["replay_exact"] = canonical_hash(replayed) == canonical_hash(final)
            checks["victory_receipt_present"] = bool(trace and trace[-1].victory_code)
        except Exception as exc:
            errors.append(f"reference execution failed: {exc}")
            checks["reference_plan_wins"] = False
            checks["replay_exact"] = False
            checks["victory_receipt_present"] = False
    else:
        checks["reference_plan_wins"] = False
        checks["replay_exact"] = False
        checks["victory_receipt_present"] = False

    try:
        stored = tuple(ACTION_ADAPTER.validate_python(item) for item in episode.reference_plan)
        checks["reference_plan_schema"] = bool(stored)
        if solved.optimal_action_count is not None and stored:
            checks["stored_plan_length"] = len(stored) == solved.optimal_action_count
        else:
            checks["stored_plan_length"] = False
    except Exception as exc:
        errors.append(f"stored reference plan invalid: {exc}")
        checks["reference_plan_schema"] = False
        checks["stored_plan_length"] = False

    try:
        dumped = episode.public.model_dump(mode="json")
        checks["public_json_roundtrip"] = (
            episode.public.model_validate(json.loads(json.dumps(dumped))) == episode.public
        )
    except Exception as exc:
        errors.append(f"public JSON round trip failed: {exc}")
        checks["public_json_roundtrip"] = False

    return QualificationReport(
        passed=all(checks.values()) and not errors,
        checks=checks,
        metrics=metrics,
        errors=tuple(errors),
    )
