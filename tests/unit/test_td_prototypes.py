"""Prototype admission stops at counterexamples; policy bounds are constructive."""

import pytest

from nexus.evaluation.td_prototypes import nw2, policy_summary, w4


def test_empty_support_is_not_a_common_decision():
    with pytest.raises(ValueError, match="every admitted world"):
        policy_summary((bytes([0, 0]),), (1,), 2)
    result = policy_summary((bytes([0, 0]),), (1, 2), 2)
    assert not result["public_policy_exists_within_declared_queries"]
    assert result["unresolved_classes_without_common_decision"] == [[0, 1]]


def test_w4_records_failed_solvability_and_all_history_scope():
    result = w4()
    assert len(result["worlds"]) == 45
    assert result["exact_state_targets_reachable_in_every_world"] == []
    assert all(
        not row["nontrivial_exact_targets"]
        for row in result["all_history_reachability_across_every_old_reachable_state"]
    )
    assert not result["production_family_admitted"]
    assert all(not row["individually_solvable"] for row in result["display_goal_candidates"])


def test_nw2_keeps_correlations_and_reports_separable_assistance():
    result = nw2()
    assert result["world_count"] == 89
    assert result["qualification_size"]["table_cells"] < 16_000_000
    counterexample = result["correlation_counterexample"]
    assert counterexample["actual_joint_worlds"] < counterexample["independent_product_worlds"]
    assert not result["end_to_end"]["public_policy_exists_within_declared_queries"]
    assert result["independent_modules_control"]["public_policy_exists_within_declared_queries"]
    assert result["tap_and_clamp_assistance"]["public_policy_exists_within_declared_queries"]
    assert not result["production_family_admitted"]
