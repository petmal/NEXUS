"""Bounded operator outcomes; independent of player response/schema versions.

The summary is emitted after verbose history so an 8 KiB service tail retains it.
Counts of non-informative readings describe information gain, never wasted work.
"""

from __future__ import annotations

from collections import Counter

SUMMARY_LIMIT_BYTES = 4096


def compact_summary(snapshot: dict, trace) -> dict:
    """Project a private snapshot without replaying inference or exposing secrets."""
    performance = snapshot.get("performance") or {}
    decision = performance.get("decision_diagnostics") or {}
    readings = decision.get("readings")
    accounting = None
    if readings is not None:
        actions = {record.turn: record.action.type for record in trace}
        counts = Counter()
        for reading in readings:
            action = actions.get(reading["turn"])
            kind = (
                "preview" if action == "probe" else "committed" if action == "operate" else "other"
            )
            counts[f"{kind}_readings"] += 1
            if reading["worlds_after"] == reading["worlds_before"]:
                counts[f"noninformative_{kind}_readings"] += 1
        accounting = {
            key: counts[key]
            for kind in ("preview", "committed", "other")
            for key in (f"{kind}_readings", f"noninformative_{kind}_readings")
        }
    evidence = decision.get("final_evidence") or {}
    # Legacy performance uses per-action fields; mission performance uses a map.
    # The canonical trace is complete in either format and excludes rejected and
    # duplicate requests. Keep their counters separate below.
    action_counts = Counter(record.action.type for record in trace)
    return {
        "version": "operator-summary-v1",
        "family": str(performance.get("ontology") or "legacy")[:128],
        "status": str(snapshot["status"]["status"])[:80],
        "termination_reason": str(performance.get("termination_reason") or "unknown")[:80],
        "turn": snapshot["status"]["turn"],
        "initial_action_budget": performance.get("initial_action_budget"),
        "actions_remaining": snapshot["status"]["actions_remaining"],
        "action_counts": {
            key: action_counts[key]
            for key in (
                "observe",
                "move",
                "take",
                "drop",
                "operate",
                "probe",
                "measure",
                "configure",
                "wait",
                "finish",
            )
        },
        "escape_classification": decision.get("escape_classification"),
        "physical_goal_satisfied": decision.get("physical_goal_satisfied"),
        "correct_state_without_successful_finish": decision.get(
            "correct_state_without_successful_finish"
        ),
        "final_evidence": {
            key: evidence.get(key)
            for key in ("classification", "remaining_worlds", "accepting_worlds", "common_repairs")
        },
        "measurements_used": performance.get("measurements_used"),
        "informative_measurements": performance.get("informative_measurements"),
        "noninformative_measurements": performance.get("redundant_measurements"),
        "measurement_accounting": accounting,
        "noninformative_meaning": "No candidate reduction; committed readings can be necessary control/preparation. Not wasted-action counts.",
        "mission_submissions": performance.get(
            "mission_submissions", performance.get("controller_submissions")
        ),
        "failed_finishes": performance.get("failed_finishes"),
        "invalid_actions": performance.get("invalid_actions"),
        "duplicate_requests": performance.get("duplicate_requests"),
        "protocol_conflicts": performance.get("protocol_conflicts"),
        "first_submission_supported_by_evidence": performance.get(
            "first_submission_supported_by_evidence"
        ),
        "first_guaranteed_repair_turn": decision.get("first_guaranteed_repair_turn"),
        "receipt_validation": "not_observed_by_service",
        "provider_completion": "not_observed_by_service",
    }
