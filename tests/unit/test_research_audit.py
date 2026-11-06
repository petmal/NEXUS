"""Research exports must replay exactly without granting the player extra data."""

import stat
import hashlib
import json
from io import StringIO

import pytest
from fastapi.testclient import TestClient

from nexus.generator import generate_episode
from nexus.models.actions import ACTION_ADAPTER, TakeAction, DropAction
from nexus.protocol.audit import AuditRecorder, verify_bundle
from nexus.protocol.http import create_single_session_app
from nexus.protocol.public_transcript import PublicTranscript
from nexus.protocol.session import Session
from nexus.protocol.stdio import run_jsonl
from nexus.render.player import render_player
from rich.console import Console


def legacy():
    return generate_episode(
        17, discovery_level=0, planning_level=0, verifier_secret="audit-test-secret"
    )


def test_direct_audit_replays_win_and_detects_changed_bytes(tmp_path):
    episode = legacy()
    session = Session(episode)
    root = tmp_path / "audit"
    recorder = AuditRecorder(session, root)
    session.manifest()
    for action in episode.reference_plan:
        assert session.act(session.state.turn, ACTION_ADAPTER.validate_python(action)).ok
        recorder.checkpoint()
    recorder.close()
    recorder.close()
    report = verify_bundle(root)
    assert report["world_status"] == "won"
    assert report["receipt_verification"] == "original_secret_verified"
    assert report["public_capture_complete"]
    assert not report["public_responses_semantically_verified"]
    assert stat.S_IMODE(root.stat().st_mode) == 0o700
    assert all(stat.S_IMODE(p.stat().st_mode) == 0o600 for p in root.iterdir())
    with pytest.raises(FileExistsError):
        AuditRecorder(Session(episode), root)
    with (root / "trace.jsonl").open("a") as f:
        f.write("\n")
    with pytest.raises(ValueError, match="checksum"):
        verify_bundle(root)


def test_partial_capture_never_claims_complete(tmp_path):
    session = Session(legacy())
    session.public_transcript = PublicTranscript(max_records=1)
    recorder = AuditRecorder(session, tmp_path / "audit")
    session.observe()
    session.observe()
    recorder.close()
    assert not verify_bundle(tmp_path / "audit")["public_capture_complete"]


def test_unclosed_export_is_partial(tmp_path):
    AuditRecorder(Session(legacy()), tmp_path / "audit")
    with pytest.raises(ValueError, match="not closed"):
        verify_bundle(tmp_path / "audit")


def test_http_audit_captures_validation_retry_and_evaluator_closure(tmp_path):
    root = tmp_path / "http"
    app = create_single_session_app(legacy(), audit_directory=root)
    with TestClient(app) as client:
        assert client.get("/observe").status_code == 200
        request = {"expected_turn": 0, "action": {"type": "wait"}}
        assert client.post("/action", json={**request, "expected_turn": 0.9}).status_code == 422
        first = client.post("/action", json=request).json()
        retry = client.post("/action", json=request).json()
        assert retry.pop("duplicate") is True
        first.pop("duplicate")
        assert retry == first
        assert client.get("/audit").status_code == 404
        assert client.post("/finalize").status_code == 200
    result = verify_bundle(root)
    assert result["accepted_actions"] == 1
    assert result["exchange_count"] == 6
    assert result["world_status"] == "failed"
    assert result["public_capture_complete"]
    exchanges = (root / "exchanges.jsonl").read_text()
    assert "audit-test-secret" not in exchanges
    assert "physical_continuation" not in exchanges


def test_stdio_audit_captures_invalid_input_without_finalizing_on_eof(tmp_path):
    output = StringIO()
    run_jsonl(
        legacy(),
        StringIO('not json\n{"action":{"type":"wait"}}\n'),
        output,
        audit_directory=tmp_path / "stdio",
    )
    report = verify_bundle(tmp_path / "stdio")
    assert report["world_status"] == "active"
    assert report["accepted_actions"] == 1
    assert report["exchange_count"] == 3
    assert "audit-test-secret" not in output.getvalue()


def test_player_renderer_uses_only_observation():
    episode = generate_episode(17, planning_level=3)
    session = Session(episode)
    observation = session.observe()
    output = StringIO()
    render_player(observation, console=Console(file=output, width=160, color_system=None))
    text = output.getvalue()
    hidden = [
        a for a in episode.public.initial_state.artifacts.values() if a.location != observation.room
    ]
    assert hidden
    assert all(a.id not in text for a in hidden)
    assert episode.verifier_secret not in text


@pytest.mark.parametrize(
    "family,planning", [("stateful-planning-v1", 3), ("stateful-interference-v1", 0)]
)
def test_exact_cost_tracks_shortest_plan_probe_waste_and_drop(family, planning):
    from nexus.ontology.catalog import runtime_for

    episode = generate_episode(
        31 if planning else 17,
        axis_version=2,
        science_family=family,
        theory_level=0,
        discovery_level=5 if planning else 0,
        planning_level=planning,
        resource_pressure=2,
    )
    session = Session(episode)
    initial = session.operator_snapshot()["physical_continuation"]
    assert initial["available"]
    from nexus.solver import solve

    assert initial["initial_minimum_actions"] == solve(episode).optimal_action_count
    plan = runtime_for(episode.public.investigation).physical_plan(episode)
    assert session.act(0, TakeAction(artifact="seal")).ok
    assert session.operator_snapshot()["physical_continuation"]["excess_actions"] == 0
    assert session.act(1, DropAction(artifact="seal")).ok
    report = session.operator_snapshot()["physical_continuation"]
    assert report["first_budget_infeasible_turn"] == 2
    assert report["excess_actions"] == 2
    # A fresh optimal trajectory has zero extra actions all the way to a win.
    session = Session(episode)
    for action in plan:
        response = session.act(session.state.turn, action)
        assert response.ok
        report = session.operator_snapshot()["physical_continuation"]
        assert report["excess_actions"] == 0
        assert report["first_budget_infeasible_turn"] is None
        assert "physical_continuation" not in response.model_dump_json()
    assert report["minimum_remaining_actions"] == 0
    assert session.state.terminal_status.value == "won"


def test_hidden_laws_do_not_claim_exact_public_continuation():
    episode = generate_episode(
        21,
        axis_version=2,
        science_family="stateful-planning-v1",
        theory_level=3,
        discovery_level=5,
        planning_level=0,
        resource_pressure=0,
    )
    report = Session(episode).operator_snapshot()["physical_continuation"]
    assert report["available"] is False
    assert report["reason"] == "laws_are_not_disclosed"


def rewrite_outcome(root, outcome):
    """Keep checksums consistent: semantic verification must catch wrong metrics."""
    path = root / "outcome.json"
    path.write_text(json.dumps(outcome))
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["files_sha256"]["outcome.json"] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))


@pytest.mark.parametrize("damage", ["status", "actions", "numeric_type", "missing_metric",
                                    "continuation", "witnesses", "finalized_type"])
def test_bundle_recomputes_game_metrics_instead_of_trusting_self_consistent_checksums(tmp_path, damage):
    episode = legacy()
    session = Session(episode)
    recorder = AuditRecorder(session, tmp_path / "audit")
    for action in episode.reference_plan:
        assert session.act(session.state.turn, ACTION_ADAPTER.validate_python(action)).ok
    recorder.close()
    outcome = json.loads((recorder.directory / "outcome.json").read_text())
    if damage == "status":
        outcome["status"]["status"] = "failed"
    elif damage == "actions":
        outcome["performance"]["actions_used"] += 1
    elif damage == "numeric_type":
        outcome["performance"]["actions_used"] = float(outcome["performance"]["actions_used"])
    elif damage == "missing_metric":
        del outcome["performance"]["actions_used"]
    elif damage == "continuation":
        outcome["physical_continuation"] = {"available": True, "excess_actions": 100}
    elif damage == "witnesses":
        outcome["evidence_witnesses"] = {"invented": True}
    else:
        outcome["evaluator_finalized"] = 1
    rewrite_outcome(recorder.directory, outcome)
    with pytest.raises(ValueError, match="audit .* (mismatch|boolean)"):
        verify_bundle(recorder.directory)


def test_verified_game_metrics_do_not_claim_request_counters_are_verified(tmp_path):
    session = Session(legacy())
    recorder = AuditRecorder(session, tmp_path / "audit")
    session.finalize_attempt()
    recorder.close()
    outcome = json.loads((recorder.directory / "outcome.json").read_text())
    outcome["performance"]["invalid_actions"] = 42
    rewrite_outcome(recorder.directory, outcome)
    report = verify_bundle(recorder.directory)
    assert report["game_metrics_verified"]
    assert not report["world_qualification_rechecked"]
    assert "performance.invalid_actions" in report["unverified_outcome_fields"]
    assert not report["public_responses_semantically_verified"]


def test_scientific_bundle_recomputes_continuation_and_evidence_metrics(tmp_path):
    from nexus.ontology.catalog import runtime_for

    episode = generate_episode(21, axis_version=2, science_family="stateful-planning-v1",
                               theory_level=0, discovery_level=5, planning_level=3,
                               resource_pressure=2)
    session = Session(episode)
    recorder = AuditRecorder(session, tmp_path / "audit")
    for action in runtime_for(episode.public.investigation).physical_plan(episode):
        assert session.act(session.state.turn, action).ok
    recorder.close()
    report = verify_bundle(recorder.directory)
    assert report["game_metrics_verified"] and report["physical_continuation"]["excess_actions"] == 0
    outcome = json.loads((recorder.directory / "outcome.json").read_text())
    outcome["performance"]["decision_diagnostics"]["escape_classification"] = "compatible_win"
    rewrite_outcome(recorder.directory, outcome)
    with pytest.raises(ValueError, match="audit performance mismatch"):
        verify_bundle(recorder.directory)
