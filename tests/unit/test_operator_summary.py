"""Long histories retain a compact outcome without changing public schemas."""

import json
import logging

from nexus.generator import generate_episode
from nexus.models.actions import ConfigureAction, ProbeAction, TakeAction
from nexus.ontology.discovery.policy import public_policy
from nexus.protocol.operator_diagnostics import OperatorDiagnostics
from nexus.protocol.operator_summary import SUMMARY_LIMIT_BYTES, compact_summary
from nexus.protocol.session import Session


def test_physical_completion_survives_mission_v1_projection_without_awarding_a_win():
    from nexus.ontology.catalog import runtime_for

    episode = generate_episode(7, axis_version=2, science_family="coupled-repair-v1",
                               theory_level=3, discovery_level=5, planning_level=0, resource_pressure=1)
    session = Session(episode)
    for action in runtime_for(episode.public.investigation).physical_plan(episode)[:-1]:
        assert session.act(session.status().turn, action).ok
    _, performance = session.finalize_attempt()
    assert performance.final_submission_correct
    summary = compact_summary(session.operator_snapshot(), session.trace_snapshot())
    assert summary["physical_goal_satisfied"] is True
    assert summary["correct_state_without_successful_finish"] is True
    assert summary["status"] == "failed"


def test_first_eligible_metrics_preserve_early_procedural_error_and_unknown():
    from nexus.models.actions import FinishAction

    episode = generate_episode(2073, axis_version=2, science_family="model-revision-v1",
                               theory_level=0, discovery_level=0, planning_level=0, resource_pressure=1)
    for early_finish in (False, True):
        session = Session(episode)
        if early_finish:
            assert session.act(0, FinishAction()).ok
        _, result = session.finalize_attempt()
        assert result.first_eligible_submission_turn is None
        assert result.first_eligible_submission_correct is None
        assert result.first_eligible_submission_supported_by_evidence is None
        assert result.first_submission_correct is (False if early_finish else None)
    session = Session(episode)
    assert session.act(0, FinishAction()).ok
    won = public_policy(session, episode.public.evidence_files)
    assert won.victory_code
    result = won.performance
    assert result.version == "mission-performance-v4"
    assert result.first_submission_correct is False
    assert result.first_submission_supported_by_evidence is False
    assert result.first_eligible_submission_turn == 5
    assert result.first_eligible_submission_correct is True
    assert result.first_eligible_submission_supported_by_evidence is True
    serialized = won.model_dump(mode="json")["performance"]
    assert serialized["version"] == "mission-performance-v4"
    assert serialized["first_eligible_submission_turn"] == 5
    assert serialized["first_eligible_submission_correct"] is True
    assert serialized["first_eligible_submission_supported_by_evidence"] is True
    summary = compact_summary(session.operator_snapshot(), session.trace_snapshot())
    assert summary["first_eligible_submission_correct"] is True
    assert summary["first_eligible_submission_supported_by_evidence"] is True


def test_long_report_keeps_complete_summary_in_8192_byte_tail(caplog):
    episode = generate_episode(
        95,
        axis_version=2,
        science_family="coupled-memory-v1",
        theory_level=0,
        discovery_level=0,
        planning_level=0,
        resource_pressure=0,
        verifier_secret="summary-secret",
    )
    session = Session(episode)
    diagnostics = OperatorDiagnostics(session)
    caplog.set_level(logging.INFO, logger="nexus.operator")
    diagnostics.start()
    for action in (
        TakeAction(artifact="carrier"),
        ConfigureAction(machine="reader", settings=(1,)),
        *(ProbeAction(machine="reader", artifact="carrier") for _ in range(100)),
    ):
        assert session.act(expected_turn=session.status().turn, action=action).ok
        diagnostics.checkpoint()
    assert not any("operator summary:" in r.getMessage() for r in caplog.records)
    result = public_policy(session, episode.public.evidence_files)
    assert result.victory_code
    diagnostics.checkpoint()
    messages = [r.getMessage() for r in caplog.records]
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    tail = (
        "\n".join(formatter.format(r) for r in caplog.records)
        .encode()[-8192:]
        .decode(errors="replace")
    )
    prefix = "NEXUS operator summary: "
    encoded = tail.split(prefix)[-1]
    summary = json.loads(encoded)
    assert len(encoded.encode()) <= SUMMARY_LIMIT_BYTES
    assert summary["status"] == "won"
    assert summary["escape_classification"] == "supported_win"
    assert summary["measurement_accounting"]["noninformative_preview_readings"] == 100
    assert summary["receipt_validation"] == "not_observed_by_service"
    assert "summary-secret" not in tail and result.victory_code not in tail
    assert messages[-1].startswith(prefix)
    assert len(next(m for m in messages if '"kind":"report"' in m)) > 8192


def test_known_law_commits_are_not_called_wasted_actions():
    from nexus.ontology.stateful.policy import public_policy as stateful_policy

    episode = generate_episode(
        229,
        axis_version=2,
        science_family="stateful-discovery-v1",
        theory_level=0,
        discovery_level=0,
        planning_level=0,
        resource_pressure=1,
    )
    session = Session(episode)
    assert stateful_policy(session, episode.public.evidence_files).victory_code
    summary = compact_summary(session.operator_snapshot(), session.trace_snapshot())
    counts = summary["measurement_accounting"]
    assert counts["committed_readings"] > 0
    assert counts["noninformative_committed_readings"] == counts["committed_readings"]
    assert counts["preview_readings"] == 0
    assert summary["noninformative_measurements"] == counts["committed_readings"]


def test_trace_suffix_is_an_independent_snapshot():
    episode = generate_episode(17)
    session = Session(episode)
    assert session.trace_snapshot(start=10) == ()
    import pytest

    with pytest.raises(ValueError, match="nonnegative"):
        session.trace_snapshot(start=-1)


def test_legacy_summary_counts_committed_actions_from_trace():
    from nexus.models.actions import WaitAction

    session = Session(generate_episode(17))
    assert session.act(expected_turn=0, action=WaitAction()).ok
    session.finalize_attempt()
    summary = compact_summary(session.operator_snapshot(), session.trace_snapshot())
    assert summary["action_counts"]["wait"] == 1
    assert summary["turn"] == 1
    assert summary["rejected_equivalent_submissions"] is None


def test_archived_v1_witness_summary_does_not_invent_zero_behavioral_repeats():
    session = Session(generate_episode(17))
    snapshot = session.operator_snapshot()
    snapshot["evidence_witnesses"] = {
        "version": "evidence-witnesses-v1",
        "submissions": [{"repeated_build": True, "witness": None}],
    }
    summary = compact_summary(snapshot, session.trace_snapshot())
    assert summary["version"] == "operator-summary-v5"
    assert summary["repeated_build_submissions"] == 1
    assert summary["rejected_equivalent_submissions"] is None
