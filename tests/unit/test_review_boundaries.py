"""Operator measurements and requests checked at the actual player boundary."""

import io
import json
import logging

from fastapi.testclient import TestClient
import pytest

from nexus.engine.canonical import canonical_hash
from nexus.generator import generate_episode
from nexus.io import save_episode
from nexus.models.actions import WaitAction
from nexus.protocol import transport
from nexus.protocol.audit import AuditRecorder, verify_bundle
from nexus.protocol.client import SERVICE_REQUEST_ADAPTER, request_service
from nexus.protocol.http import create_single_session_app
from nexus.protocol.operator_diagnostics import OperatorDiagnostics
from nexus.protocol.operator_summary import compact_summary
from nexus.protocol.session import Session
from nexus.protocol.stdio import run_jsonl


def world(scientific):
    return generate_episode(
        17,
        axis_version=2 if scientific else 1,
        theory_level=0,
        discovery_level=0,
        planning_level=0,
        resource_pressure=0,
        verifier_secret="review-test",
    )


@pytest.mark.parametrize("scientific", [False, True])
def test_edits_to_an_action_example_do_not_change_other_players_instructions(scientific):
    ep = world(scientific)
    first, other = Session(ep), Session(ep)
    example = first.manifest().action_contract["reference"][0]["example"]
    pristine = other.manifest().action_contract
    try:
        example["annotation"] = "UI-only"
        assert "annotation" not in other.manifest().action_contract["reference"][0]["example"]
        assert "annotation" not in pristine["reference"][0]["example"]
    finally:
        example.pop("annotation", None)


@pytest.mark.parametrize("scientific", [False, True])
def test_bound_evidence_matches_files_actually_delivered_and_summary_matches_world(
    tmp_path, caplog, scientific
):
    ep = world(scientific)
    session = Session(ep)
    logger = OperatorDiagnostics(session)
    with caplog.at_level(logging.INFO, logger="nexus.operator"):
        logger.start()
    message = next(r.getMessage() for r in caplog.records if '"kind":"binding"' in r.getMessage())
    binding = json.loads(message.split("NEXUS operator diagnostic: ", 1)[1])
    save_episode(ep, tmp_path / "export")
    with TestClient(create_single_session_app(ep)) as service:
        manifest = service.get("/manifest").json()
        served = {
            name: service.get("/evidence/" + name).text for name in manifest["evidence_files"]
        }
    exported = {
        p.name: p.read_bytes().decode() for p in (tmp_path / "export/attachments").iterdir()
    }
    assert served == exported
    audit = tmp_path / "audit"
    AuditRecorder(session, audit).close()
    assert verify_bundle(audit)["game_metrics_verified"]
    private = json.loads((audit / "binding.json").read_text())
    assert (
        binding["public_evidence_sha256"]
        == private["public_evidence_sha256"]
        == canonical_hash(served)
    )
    assert (
        binding["player_manifest_sha256"]
        == private["player_manifest_sha256"]
        == canonical_hash(manifest)
    )
    assert binding["compiled_evidence_sha256"] == canonical_hash(ep.public.evidence_files)
    assert binding["presentation_version"] == manifest["presentation_version"]
    assert binding["initial_action_budget"] == ep.public.initial_state.resources.actions_remaining
    for terminal in (False, True):
        if terminal:
            session.finalize_attempt()
        summary = compact_summary(session.operator_snapshot(), session.trace_snapshot())
        assert (
            summary["family"]
            == binding["family"]
            == ("shared-response-v1" if scientific else "legacy")
        )
        assert summary["initial_action_budget"] == binding["initial_action_budget"]
        assert not summary["witnesses_available"] and summary["repeated_build_submissions"] is None


def test_file_and_python_clients_can_retry_a_committed_turn_without_spending_again(monkeypatch):
    session = Session(world(False))
    calls = []

    def send(base_url, method, path, payload=None, **options):
        calls.append(path)
        if path == "/status":
            return session.status().model_dump(mode="json")
        assert path == "/action" and payload["action"] == {"type": "wait"}
        return session.act(payload["expected_turn"], WaitAction()).model_dump(mode="json")

    monkeypatch.setattr(transport, "_json_request", send)
    pinned = {"operation": "action", "expected_turn": 0, "action": {"type": "wait"}}
    assert transport.request_service_payload(pinned)["current_turn"] == 1
    assert request_service(SERVICE_REQUEST_ADAPTER.validate_python(pinned))["duplicate"]
    assert calls == ["/action", "/action"] and session.state.turn == 1
    auto = SERVICE_REQUEST_ADAPTER.validate_python(
        {"operation": "action", "action": {"type": "wait"}}
    )
    assert request_service(auto)["current_turn"] == 2
    assert calls[-2:] == ["/status", "/action"]


@pytest.mark.parametrize("turn", [True, -1, 0.5, "0", None])
def test_invalid_pinned_turn_is_rejected_before_network_access(monkeypatch, turn):
    monkeypatch.setattr(
        transport, "_json_request", lambda *a, **kw: pytest.fail("unexpected request")
    )
    data = {"operation": "action", "action": {"type": "wait"}, "expected_turn": turn}
    with pytest.raises(ValueError):
        SERVICE_REQUEST_ADAPTER.validate_python(data)
    with pytest.raises(transport.ClientError):
        transport.request_service_payload(data)


def test_stdio_can_read_public_task_and_retry_without_private_files(tmp_path):
    ep = world(False)
    session = Session(ep)
    manifest = session.manifest()
    filename = manifest.evidence_files[0]
    action = {"operation": "action", "action": {"type": "wait"}, "expected_turn": 0}
    requests = [
        {"operation": "manifest"},
        {"operation": "evidence", "filename": filename},
        {"operation": "observe"},
        action,
        action,
        {"operation": "status"},
        {"operation": "finalize"},
        {"operation": "status"},
    ]
    out = io.StringIO()
    audit = tmp_path / "audit"
    run_jsonl(
        ep, io.StringIO("".join(json.dumps(r) + "\n" for r in requests)), out, audit_directory=audit
    )
    initial, mission, evidence, observation, first, retry, status, error, after = map(
        json.loads, out.getvalue().splitlines()
    )
    assert mission == manifest.model_dump(mode="json")
    assert evidence == {"filename": filename, "content": session.evidence(filename)}
    assert initial["observation"] == observation
    assert first["current_turn"] == 1 and retry["duplicate"]
    assert after == status and status["status"] == "active" and not error["ok"]
    report = verify_bundle(audit)
    assert report["accepted_actions"] == 1 and report["exchange_count"] == len(requests) + 1


def test_audit_rejects_different_mission_text_even_when_file_hashes_match(tmp_path):
    import hashlib

    root = tmp_path / "audit"
    AuditRecorder(Session(world(False)), root).close()
    private = root / "private.json"
    episode = json.loads(private.read_text())
    episode["public"]["description"] += " A different briefing."
    private.write_text(json.dumps(episode))
    manifest = root / "manifest.json"
    data = json.loads(manifest.read_text())
    data["files_sha256"]["private.json"] = hashlib.sha256(private.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="binding mismatch: player_manifest_sha256"):
        verify_bundle(root)


@pytest.mark.parametrize("enabled", [False, True])
def test_stdio_checker_respects_the_same_assistance_setting_as_http(enabled):
    ep = generate_episode(
        5866,
        axis_version=2,
        science_family="model-revision-v1",
        theory_level=3,
        discovery_level=5,
        planning_level=0,
        resource_pressure=1,
        ontology_options={"consistency_check": "readings"} if enabled else {},
    )
    build = [0, 0, 3, 0]
    with TestClient(create_single_session_app(ep)) as http:
        reply = http.post("/check", json={"build": build})
    output = io.StringIO()
    stream = [json.dumps({"operation": "check", "build": build}), '{"operation":"status"}']
    run_jsonl(ep, io.StringIO("\n".join(stream)), output)
    _, checked, status = map(json.loads, output.getvalue().splitlines())
    assert status["turn"] == 0
    if enabled:
        assert checked == reply.json() and checked["world_action_cost"] == 0
    else:
        assert reply.status_code == 404 and not checked["ok"]
