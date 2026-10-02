from __future__ import annotations

import csv
import io
import json

import networkx as nx
from pydantic import BaseModel, ConfigDict, Field

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import execute_with_trace, replay
from nexus.engine.rules import apply_effect
from nexus.generator.constructed import (
    CONSTRUCTOR_VALUE,
    DISTRACTOR_VALUE,
    MISSION_TARGET_VALUE,
    constant_value_rule,
    constructed_mission_rules,
)
from nexus.generator.difficulty import (
    EXECUTION_SLACK,
    MAX_PHYSICAL_OPTIMAL_ACTIONS,
    artifact_projection,
    chain_requires_both_in_order,
    exploration_allowance,
    machine_count_for_discovery,
    recommended_tool_call_limit,
    required_probe_count,
    room_bounds,
    validate_difficulty_levels,
)
from nexus.generator.discovery import DiscoveryBelief, analyze_discovery
from nexus.generator.evidence import (
    candidates_matching_csv,
    has_direct_context_csv,
    measurement_filename,
    mission_prediction_count,
)
from nexus.generator.randomness import scenario_family_id
from nexus.generator.rules import enumerate_transformation_rules, rule_ast_metrics
from nexus.models.actions import ACTION_ADAPTER, OperateAction, ProbeAction
from nexus.models.episode import PrivateEpisode
from nexus.models.goals import GoalKind
from nexus.models.world import Shape, TerminalStatus
from nexus.solver.belief import solve_guaranteed_policy
from nexus.solver.search import solve


class QualificationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    passed: bool
    checks: dict[str, bool]
    metrics: dict[str, int | str | bool] = Field(default_factory=dict)
    errors: tuple[str, ...] = ()


def _graph_diameter(episode: PrivateEpisode) -> int:
    graph = nx.Graph()
    graph.add_nodes_from(episode.public.rooms)
    graph.add_edges_from(episode.public.edges)
    return nx.diameter(graph)


def _csv_row_count(csv_text: str) -> int:
    return len(list(csv.DictReader(io.StringIO(csv_text))))


def _policy_operate_value(policy, machine_id: str, artifact_id: str):
    return next(
        (
            value
            for value in policy.initial_action_values
            if isinstance(value.action, OperateAction)
            and value.action.machine == machine_id
            and value.action.artifact == artifact_id
        ),
        None,
    )


def _goal_contains_kind(goal, kind: GoalKind) -> bool:
    if goal.kind == kind:
        return True
    return any(_goal_contains_kind(child, kind) for child in goal.children)


def _goal_field_value(goal, artifact_id: str, field: str):
    if (
        goal.kind == GoalKind.ARTIFACT_FIELD
        and goal.artifact_id == artifact_id
        and goal.field == field
    ):
        return goal.value
    for child in goal.children:
        value = _goal_field_value(child, artifact_id, field)
        if value is not None:
            return value
    return None


def _policy_probe_value(policy, artifact_id: str):
    return next(
        (
            value
            for value in policy.initial_action_values
            if isinstance(value.action, ProbeAction)
            and value.action.machine == "M1"
            and value.action.artifact == artifact_id
        ),
        None,
    )


def qualify_episode(
    episode: PrivateEpisode,
    *,
    max_states: int = 100_000,
) -> QualificationReport:
    checks: dict[str, bool] = {}
    errors: list[str] = []
    metrics: dict[str, int | str | bool] = {}
    metadata = episode.generation_metadata

    public_json = episode.public.model_dump_json()
    serialized_rules = [rule.model_dump_json() for rule in episode.rules.values()]
    checks["public_private_separation"] = (
        episode.verifier_secret not in public_json
        and all(
            token not in public_json
            for token in (
                "construction_seed",
                "reference_plan",
                "machine_rules",
                "verifier_secret",
                "generation_metadata",
                "optimal_action_count",
                "required_probe_count",
            )
        )
        and all(serialized_rule not in public_json for serialized_rule in serialized_rules)
    )

    checks["causal_grammar_disclosed"] = bool(
        episode.public.evidence_files.get("facility_manual.txt", "").strip()
    )

    try:
        validate_difficulty_levels(metadata.discovery_level, metadata.planning_level)
        expected_machine_count = machine_count_for_discovery(metadata.discovery_level)
        room_role_count = 1 if metadata.discovery_level == 5 else expected_machine_count
        min_rooms, max_rooms = room_bounds(metadata.planning_level, room_role_count)
        checks["planning_profile"] = (
            metadata.machine_count == expected_machine_count
            and len(episode.public.initial_state.machines) == expected_machine_count
            and min_rooms <= len(episode.public.rooms) <= max_rooms
        )
    except ValueError as exc:
        errors.append(str(exc))
        expected_machine_count = 0
        checks["planning_profile"] = False

    machine_ids = tuple(sorted(episode.public.initial_state.machines))
    initial_artifact = episode.public.initial_state.artifacts.get("A1")
    all_candidates = enumerate_transformation_rules()

    evidence_candidate_counts: dict[str, int] = {}
    prediction_counts: dict[str, int] = {}
    direct_examples: dict[str, bool] = {}
    evidence_rows_by_machine: dict[str, int] = {}
    candidate_rules_by_machine: dict[str, list] = {}
    hidden_rules_match = True
    stage_inputs = {}

    if metadata.discovery_level == 5:
        epistemic_artifact = episode.public.initial_state.artifacts.get("A2")
        distractor_artifact = episode.public.initial_state.artifacts.get("A3")
        profile_inputs_valid = (
            initial_artifact is not None
            and epistemic_artifact is not None
            and distractor_artifact is not None
            and machine_ids == ("M1", "M2", "M3")
            and episode.public.phase_modulus == 4
        )
        if profile_inputs_valid:
            assert epistemic_artifact is not None
            candidate_rules_by_machine = {
                "M1": list(constructed_mission_rules(epistemic_artifact.shape)),
                "M2": [constant_value_rule(CONSTRUCTOR_VALUE)],
                "M3": [constant_value_rule(DISTRACTOR_VALUE)],
            }
            evidence_candidate_counts = {"M1": 4, "M2": 1, "M3": 1}
            prediction_counts = {"M1": 2, "M2": 1, "M3": 1}
            direct_examples = {"M1": False, "M2": False, "M3": False}
            evidence_rows_by_machine = {"M1": 0, "M2": 0, "M3": 0}
            hidden_rules_match = all(
                episode.rules.get(episode.machine_rules.get(machine_id, ""))
                in candidate_rules_by_machine[machine_id]
                for machine_id in machine_ids
            )
        else:
            hidden_rules_match = False

        current = (
            initial_artifact.model_copy(update={"value": MISSION_TARGET_VALUE})
            if initial_artifact is not None
            else None
        )
        discovery_analysis = None
        exact_probe_count = 1 if profile_inputs_valid else None
    else:
        current = initial_artifact
        profile_inputs_valid = current is not None
        for machine_id in machine_ids:
            if current is None:
                profile_inputs_valid = False
                break
            phase = metadata.transformation_phases.get(machine_id)
            rule_id = episode.machine_rules.get(machine_id)
            rule = episode.rules.get(rule_id or "")
            evidence_text = episode.public.evidence_files.get(measurement_filename(machine_id))
            if phase is None or rule is None or evidence_text is None:
                profile_inputs_valid = False
                hidden_rules_match = False
                continue
            if not 0 <= phase < episode.public.phase_modulus:
                profile_inputs_valid = False
                continue

            stage_inputs[machine_id] = current
            matching = candidates_matching_csv(evidence_text, all_candidates)
            candidate_rules_by_machine[machine_id] = matching
            evidence_candidate_counts[machine_id] = len(matching)
            prediction_counts[machine_id] = mission_prediction_count(matching, current, phase)
            direct_examples[machine_id] = has_direct_context_csv(evidence_text, current, phase)
            evidence_rows_by_machine[machine_id] = _csv_row_count(evidence_text)
            hidden_rules_match = hidden_rules_match and rule in matching
            current = apply_effect(rule, current, phase)

        discovery_analysis = (
            analyze_discovery(
                candidate_rules_by_machine=candidate_rules_by_machine,
                initial_artifact=initial_artifact,
                target_artifact=current,
                phase_modulus=episode.public.phase_modulus,
            )
            if profile_inputs_valid
            and initial_artifact is not None
            and current is not None
            and len(candidate_rules_by_machine) == len(machine_ids)
            else None
        )
        exact_probe_count = (
            discovery_analysis.minimum_guaranteed_probes
            if discovery_analysis is not None
            else None
        )

    checks["evidence_matches_hidden_rule"] = hidden_rules_match and profile_inputs_valid

    d4_policy = None
    d4_epistemic = None
    d4_distractor = None
    d4_mission_probe = None
    if (
        metadata.discovery_level == 4
        and profile_inputs_valid
        and initial_artifact is not None
        and current is not None
        and machine_ids == ("M1",)
        and "M1" in candidate_rules_by_machine
    ):
        epistemic_artifact = episode.public.initial_state.artifacts.get("A2")
        distractor_artifact = episode.public.initial_state.artifacts.get("A3")
        if epistemic_artifact is not None and distractor_artifact is not None:
            belief = DiscoveryBelief(
                candidate_rules_by_machine=candidate_rules_by_machine,
                initial_artifact=initial_artifact,
                target_artifact=current,
                phase_modulus=episode.public.phase_modulus,
            )
            d4_epistemic = belief.analyze_probe_context(
                artifact=epistemic_artifact,
                machine_id="M1",
                phase=0,
            )
            d4_distractor = belief.analyze_probe_context(
                artifact=distractor_artifact,
                machine_id="M1",
                phase=0,
            )
            proof_bound = min(
                96,
                max(
                    8,
                    (metadata.guaranteed_policy_action_count or metadata.action_budget or 48) + 2,
                ),
            )
            d4_policy = solve_guaranteed_policy(
                episode,
                candidate_rules_by_machine=candidate_rules_by_machine,
                max_actions=proof_bound,
            )
            d4_mission_probe = _policy_probe_value(d4_policy, "A1")

    d5_policy = None
    d5_constructor = None
    d5_direct_probe = None
    d5_distractor = None
    d5_constructed_outcomes = 0
    if (
        metadata.discovery_level == 5
        and profile_inputs_valid
        and initial_artifact is not None
        and machine_ids == ("M1", "M2", "M3")
    ):
        epistemic_artifact = episode.public.initial_state.artifacts.get("A2")
        distractor_artifact = episode.public.initial_state.artifacts.get("A3")
        if epistemic_artifact is not None and distractor_artifact is not None:
            proof_bound = min(
                96,
                max(
                    10,
                    (metadata.guaranteed_policy_action_count or metadata.action_budget or 48) + 2,
                ),
            )
            d5_policy = solve_guaranteed_policy(
                episode,
                candidate_rules_by_machine=candidate_rules_by_machine,
                max_actions=proof_bound,
            )
            d5_constructor = _policy_operate_value(d5_policy, "M2", "A2")
            d5_direct_probe = _policy_probe_value(d5_policy, "A1")
            d5_distractor = _policy_operate_value(d5_policy, "M3", "A3")

            constructed_artifact = apply_effect(
                constant_value_rule(CONSTRUCTOR_VALUE),
                epistemic_artifact,
                0,
            )
            d5_constructed_outcomes = len(
                {
                    artifact_projection(apply_effect(rule, constructed_artifact, 0))
                    for rule in candidate_rules_by_machine["M1"]
                }
            )

    discovery_profile = (
        profile_inputs_valid
        and len(machine_ids) == expected_machine_count
        and exact_probe_count == required_probe_count(metadata.discovery_level)
    )
    if discovery_profile:
        if metadata.discovery_level == 0:
            discovery_profile = (
                machine_ids == ("M1",)
                and direct_examples.get("M1") is True
                and evidence_candidate_counts.get("M1") == 1
                and prediction_counts.get("M1") == 1
            )
        elif metadata.discovery_level == 1:
            discovery_profile = (
                machine_ids == ("M1",)
                and direct_examples.get("M1") is False
                and prediction_counts.get("M1") == 1
            )
        elif metadata.discovery_level == 2:
            discovery_profile = (
                machine_ids == ("M1",)
                and direct_examples.get("M1") is False
                and prediction_counts.get("M1", 0) > 1
            )
        elif metadata.discovery_level == 3:
            discovery_profile = (
                machine_ids == ("M1", "M2")
                and all(not direct_examples.get(machine_id, True) for machine_id in machine_ids)
                and all(prediction_counts.get(machine_id, 0) > 1 for machine_id in machine_ids)
            )
            if discovery_profile and initial_artifact is not None and current is not None:
                first_rule = episode.rules[episode.machine_rules["M1"]]
                second_rule = episode.rules[episode.machine_rules["M2"]]
                discovery_profile = chain_requires_both_in_order(
                    initial_artifact,
                    first_rule,
                    second_rule,
                    current,
                    phase_modulus=episode.public.phase_modulus,
                )
        elif metadata.discovery_level == 4:
            epistemic_artifact = episode.public.initial_state.artifacts.get("A2")
            distractor_artifact = episode.public.initial_state.artifacts.get("A3")
            epistemic_probe = (
                _policy_probe_value(d4_policy, "A2") if d4_policy is not None else None
            )
            distractor_probe = (
                _policy_probe_value(d4_policy, "A3") if d4_policy is not None else None
            )
            discovery_profile = (
                machine_ids == ("M1",)
                and direct_examples.get("M1") is False
                and prediction_counts.get("M1", 0) > 1
                and set(episode.public.initial_state.artifacts) == {"A1", "A2", "A3"}
                and epistemic_artifact is not None
                and distractor_artifact is not None
                and {
                    initial_artifact.shape,
                    epistemic_artifact.shape,
                    distractor_artifact.shape,
                }
                == set(Shape)
                and all(
                    artifact.location == "@inventory"
                    for artifact in episode.public.initial_state.artifacts.values()
                )
                and episode.public.initial_state.machines["M1"].room_id == "R0"
                and d4_epistemic is not None
                and d4_epistemic.discriminative
                and d4_epistemic.mission_relevant
                and d4_epistemic.worst_case_remaining_probes == 0
                and d4_distractor is not None
                and not d4_distractor.discriminative
                and d4_distractor.outcome_count == 1
                and d4_policy is not None
                and d4_policy.solvable
                and d4_policy.optimal_worst_case_actions is not None
                and d4_mission_probe is not None
                and d4_mission_probe.worst_case_total_actions
                == d4_policy.optimal_worst_case_actions
                and epistemic_probe is not None
                and epistemic_probe.discriminative
                and epistemic_probe.worst_case_total_actions
                == d4_policy.optimal_worst_case_actions
                and distractor_probe is not None
                and not distractor_probe.discriminative
                and distractor_probe.outcome_count == 1
                and distractor_probe.worst_case_total_actions
                == d4_policy.optimal_worst_case_actions + 1
            )
        elif metadata.discovery_level == 5:
            epistemic_artifact = episode.public.initial_state.artifacts.get("A2")
            distractor_artifact = episode.public.initial_state.artifacts.get("A3")
            discovery_profile = (
                machine_ids == ("M1", "M2", "M3")
                and set(episode.public.initial_state.artifacts) == {"A1", "A2", "A3"}
                and epistemic_artifact is not None
                and distractor_artifact is not None
                and {
                    initial_artifact.shape,
                    epistemic_artifact.shape,
                    distractor_artifact.shape,
                }
                == set(Shape)
                and all(
                    artifact.location == "@inventory"
                    for artifact in episode.public.initial_state.artifacts.values()
                )
                and all(
                    machine.room_id == "R0"
                    for machine in episode.public.initial_state.machines.values()
                )
                and not _goal_contains_kind(episode.public.goal, GoalKind.PHASE_EQUALS)
                and _goal_field_value(episode.public.goal, "A1", "value")
                == MISSION_TARGET_VALUE
                and d5_policy is not None
                and d5_policy.solvable
                and d5_policy.viable_hypothesis_count == 4
                and d5_policy.optimal_worst_case_actions is not None
                and d5_constructor is not None
                and d5_constructor.worst_case_total_actions
                == d5_policy.optimal_worst_case_actions
                and d5_direct_probe is not None
                and d5_direct_probe.worst_case_total_actions is not None
                and d5_direct_probe.worst_case_total_actions
                > d5_policy.optimal_worst_case_actions
                and d5_distractor is not None
                and d5_distractor.worst_case_total_actions is not None
                and d5_distractor.worst_case_total_actions
                > d5_policy.optimal_worst_case_actions
                and d5_constructed_outcomes == 4
            )

    checks["discovery_profile"] = discovery_profile
    checks["guaranteed_policy"] = (
        (
            metadata.discovery_level == 4
            and d4_policy is not None
            and d4_policy.solvable
            and d4_policy.optimal_worst_case_actions
            == metadata.guaranteed_policy_action_count
        )
        or (
            metadata.discovery_level == 5
            and d5_policy is not None
            and d5_policy.solvable
            and d5_policy.optimal_worst_case_actions
            == metadata.guaranteed_policy_action_count
        )
        or metadata.discovery_level not in {4, 5}
    )
    checks["constructed_experiment"] = (
        metadata.discovery_level != 5
        or (
            d5_policy is not None
            and d5_constructor is not None
            and d5_constructor.worst_case_total_actions
            == d5_policy.optimal_worst_case_actions
            and d5_direct_probe is not None
            and d5_direct_probe.worst_case_total_actions is not None
            and d5_direct_probe.worst_case_total_actions
            > d5_policy.optimal_worst_case_actions
            and d5_distractor is not None
            and d5_distractor.worst_case_total_actions is not None
            and d5_distractor.worst_case_total_actions
            > d5_policy.optimal_worst_case_actions
            and d5_constructed_outcomes == 4
        )
    )

    expected_probes = (
        required_probe_count(metadata.discovery_level)
        if 0 <= metadata.discovery_level <= 5
        else -1
    )
    expected_allowance = exploration_allowance(len(episode.public.rooms))
    family_kind = (
        "two-machine"
        if metadata.discovery_level == 3
        else "selective-one-machine"
        if metadata.discovery_level == 4
        else "constructed-three-machine"
        if metadata.discovery_level == 5
        else "one-machine"
    )
    expected_family_id = (
        scenario_family_id(
            episode.construction_seed,
            family_kind,
            metadata.scenario_family_attempt,
        )
        if episode.construction_seed is not None
        else ""
    )
    expected_viable_hypotheses = (
        4
        if metadata.discovery_level == 5
        else (discovery_analysis.viable_hypothesis_count if discovery_analysis is not None else 0)
    )
    expected_catalog_count = 4 if metadata.discovery_level == 5 else len(all_candidates)

    metadata_consistent = (
        metadata.generation_attempt == metadata.scenario_family_attempt
        and metadata.scenario_family_attempt >= 0
        and metadata.topology_attempt >= 0
        and metadata.scenario_family_id == expected_family_id
        and metadata.machine_count == len(machine_ids)
        and metadata.room_count == len(episode.public.rooms)
        and metadata.graph_diameter == _graph_diameter(episode)
        and metadata.required_probe_count == expected_probes
        and exact_probe_count == expected_probes
        and metadata.viable_causal_hypotheses == expected_viable_hypotheses
        and metadata.evidence_candidate_counts == evidence_candidate_counts
        and metadata.evidence_rows_by_machine == evidence_rows_by_machine
        and metadata.mission_relevant_prediction_counts == prediction_counts
        and metadata.direct_target_example == any(direct_examples.values())
        and metadata.candidate_rules_before_evidence == expected_catalog_count
        and metadata.candidate_rules_after_evidence == evidence_candidate_counts.get("M1", 0)
        and metadata.evidence_rows == evidence_rows_by_machine.get("M1", 0)
        and metadata.action_budget == episode.public.initial_state.resources.actions_remaining
        and metadata.exploration_allowance == expected_allowance
        and metadata.recommended_tool_call_limit
        == recommended_tool_call_limit(
            metadata.action_budget,
            len(episode.public.evidence_files),
        )
    )

    node_counts: dict[str, int] = {}
    depths: dict[str, int] = {}
    for machine_id in machine_ids:
        rule_id = episode.machine_rules.get(machine_id)
        rule = episode.rules.get(rule_id or "")
        if rule is None:
            continue
        nodes, depth = rule_ast_metrics(rule)
        node_counts[machine_id] = nodes
        depths[machine_id] = depth

    checks["compositional_rule"] = (
        len(node_counts) == len(machine_ids)
        and (
            (
                metadata.discovery_level == 5
                and node_counts.get("M1", 0) >= 8
                and depths.get("M1", 0) >= 3
                and node_counts.get("M2", 0) >= 1
                and node_counts.get("M3", 0) >= 1
            )
            or (
                metadata.discovery_level != 5
                and all(nodes >= 8 for nodes in node_counts.values())
                and all(depth >= 3 for depth in depths.values())
            )
        )
    )
    metadata_consistent = metadata_consistent and (
        metadata.rule_ast_nodes_by_machine == node_counts
        and metadata.rule_ast_depth_by_machine == depths
        and metadata.rule_ast_nodes == max(node_counts.values(), default=0)
        and metadata.rule_ast_depth == max(depths.values(), default=0)
    )

    if metadata.discovery_level == 3 and initial_artifact is not None and current is not None:
        computed_requires_both = chain_requires_both_in_order(
            initial_artifact,
            episode.rules[episode.machine_rules["M1"]],
            episode.rules[episode.machine_rules["M2"]],
            current,
            phase_modulus=episode.public.phase_modulus,
        )
        metadata_consistent = metadata_consistent and (
            metadata.requires_both_machines == computed_requires_both
            and metadata.reverse_order_reaches_goal is False
        )
    else:
        metadata_consistent = metadata_consistent and not metadata.requires_both_machines

    if metadata.discovery_level == 4:
        epistemic_probe = (
            _policy_probe_value(d4_policy, "A2") if d4_policy is not None else None
        )
        distractor_probe = (
            _policy_probe_value(d4_policy, "A3") if d4_policy is not None else None
        )
        metadata_consistent = metadata_consistent and (
            metadata.epistemic_artifact_id == "A2"
            and metadata.distractor_artifact_id == "A3"
            and metadata.epistemic_machine_id is None
            and metadata.distractor_machine_id is None
            and d4_policy is not None
            and d4_policy.optimal_worst_case_actions
            == metadata.guaranteed_policy_action_count
            and epistemic_probe is not None
            and epistemic_probe.outcome_count == metadata.epistemic_probe_outcomes
            and epistemic_probe.worst_case_total_actions
            == metadata.epistemic_probe_action_cost
            and distractor_probe is not None
            and distractor_probe.outcome_count == metadata.distractor_probe_outcomes
            and distractor_probe.worst_case_total_actions
            == metadata.distractor_probe_action_cost
            and metadata.constructed_probe_outcomes == 0
            and metadata.direct_probe_action_cost == 0
            and metadata.constructor_action_cost == 0
            and metadata.distractor_action_cost == 0
        )
    elif metadata.discovery_level == 5:
        selected_m1 = episode.rules.get(episode.machine_rules.get("M1", ""))
        winning_phase = next(
            (
                index
                for index, rule in enumerate(candidate_rules_by_machine.get("M1", []))
                if rule == selected_m1
            ),
            None,
        )
        metadata_consistent = metadata_consistent and (
            metadata.epistemic_artifact_id == "A2"
            and metadata.distractor_artifact_id == "A3"
            and metadata.epistemic_machine_id == "M2"
            and metadata.distractor_machine_id == "M3"
            and metadata.epistemic_probe_outcomes == 0
            and metadata.distractor_probe_outcomes == 0
            and metadata.epistemic_probe_action_cost == 0
            and metadata.distractor_probe_action_cost == 0
            and d5_policy is not None
            and d5_policy.optimal_worst_case_actions
            == metadata.guaranteed_policy_action_count
            and d5_constructed_outcomes == metadata.constructed_probe_outcomes
            and d5_direct_probe is not None
            and d5_direct_probe.worst_case_total_actions
            == metadata.direct_probe_action_cost
            and d5_constructor is not None
            and d5_constructor.worst_case_total_actions
            == metadata.constructor_action_cost
            and d5_distractor is not None
            and d5_distractor.worst_case_total_actions
            == metadata.distractor_action_cost
            and winning_phase is not None
            and metadata.transformation_phases
            == {"M1": winning_phase, "M2": 0, "M3": 0}
        )
    else:
        metadata_consistent = metadata_consistent and (
            metadata.guaranteed_policy_action_count == 0
            and metadata.epistemic_artifact_id is None
            and metadata.distractor_artifact_id is None
            and metadata.epistemic_machine_id is None
            and metadata.distractor_machine_id is None
            and metadata.epistemic_probe_outcomes == 0
            and metadata.distractor_probe_outcomes == 0
            and metadata.epistemic_probe_action_cost == 0
            and metadata.distractor_probe_action_cost == 0
            and metadata.constructed_probe_outcomes == 0
            and metadata.direct_probe_action_cost == 0
            and metadata.constructor_action_cost == 0
            and metadata.distractor_action_cost == 0
        )

    checks["generation_metadata_consistent"] = metadata_consistent

    metrics["evidence_candidate_count"] = evidence_candidate_counts.get("M1", 0)
    metrics["mission_relevant_prediction_count"] = prediction_counts.get("M1", 0)
    metrics["required_probe_count"] = metadata.required_probe_count
    if metadata.discovery_level == 4:
        metrics["guaranteed_policy_action_count"] = metadata.guaranteed_policy_action_count
        metrics["epistemic_probe_action_cost"] = metadata.epistemic_probe_action_cost
        metrics["distractor_probe_action_cost"] = metadata.distractor_probe_action_cost
    elif metadata.discovery_level == 5:
        metrics["guaranteed_policy_action_count"] = metadata.guaranteed_policy_action_count
        metrics["constructed_probe_outcomes"] = metadata.constructed_probe_outcomes
        metrics["direct_probe_action_cost"] = metadata.direct_probe_action_cost
        metrics["constructor_action_cost"] = metadata.constructor_action_cost
        metrics["distractor_action_cost"] = metadata.distractor_action_cost
    metrics["viable_causal_hypotheses"] = expected_viable_hypotheses
    metrics["rule_ast_nodes"] = max(node_counts.values(), default=0)
    metrics["rule_ast_depth"] = max(depths.values(), default=0)

    solved = solve(episode, max_states=max_states)
    checks["solver_found_win"] = solved.solvable
    metrics["solver_visited_states"] = solved.visited_states
    metrics["solver_max_frontier_size"] = solved.max_frontier_size
    if solved.optimal_action_count is not None:
        metrics["optimal_action_count"] = solved.optimal_action_count
        checks["difficulty_bounds"] = (
            0 < solved.optimal_action_count <= MAX_PHYSICAL_OPTIMAL_ACTIONS
        )
        expected_action_budget = (
            metadata.guaranteed_policy_action_count
            + expected_allowance
            + EXECUTION_SLACK
            if metadata.discovery_level in {4, 5}
            else solved.optimal_action_count
            + metadata.required_probe_count
            + expected_allowance
            + EXECUTION_SLACK
        )
        checks["action_budget_sufficient"] = (
            episode.public.initial_state.resources.actions_remaining
            == expected_action_budget
        )
        metadata_consistent = metadata_consistent and (
            metadata.optimal_action_count == solved.optimal_action_count
            and metadata.estimated_reference_actions == solved.optimal_action_count
            and metadata.solver_visited_states == solved.visited_states
            and metadata.solver_max_frontier_size == solved.max_frontier_size
        )
        checks["generation_metadata_consistent"] = metadata_consistent
    else:
        checks["difficulty_bounds"] = False
        checks["action_budget_sufficient"] = False

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
        if metadata.discovery_level == 3:
            operation_order = [
                action.machine
                for action in stored
                if getattr(action, "type", None) == "operate"
            ]
            checks["required_machine_order"] = operation_order == ["M1", "M2"]
        else:
            checks["required_machine_order"] = True
    except Exception as exc:
        errors.append(f"stored reference plan invalid: {exc}")
        checks["reference_plan_schema"] = False
        checks["stored_plan_length"] = False
        checks["required_machine_order"] = False

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
