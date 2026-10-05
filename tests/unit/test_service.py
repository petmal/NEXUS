from fastapi.testclient import TestClient

from nexus.generator import generate_episode
import nexus.protocol.transport as service_transport
from nexus.protocol.client import (
    SERVICE_REQUEST_ADAPTER,
    ValidationResult,
    request_service,
    validate_candidate,
    validate_candidate_with_performance,
)
from nexus.protocol.http import create_single_session_app
from nexus.verification.receipt import victory_receipt


def test_generator_supports_fixed_verifier_secret():
    first = generate_episode(101, verifier_secret="fixed-secret")
    second = generate_episode(101, verifier_secret="fixed-secret")

    assert first.public == second.public
    assert victory_receipt(first) == victory_receipt(second)


def test_single_session_http_app_has_no_session_creation_and_can_win():
    episode = generate_episode(2029, verifier_secret="fixed-secret")
    client = TestClient(create_single_session_app(episode))

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    assert client.post("/sessions").status_code == 404

    status = client.get("/status").json()
    assert status["status"] == "active"
    assert status["victory_code"] is None

    for action in episode.reference_plan:
        status = client.get("/status").json()
        response = client.post(
            "/action",
            json={"expected_turn": status["turn"], "action": action},
        )
        assert response.status_code == 200
        assert response.json()["ok"] is True

    final_status = client.get("/status").json()
    assert final_status["status"] == "won"
    assert final_status["victory_code"] == victory_receipt(episode)


def test_evaluator_finalization_fails_closed_and_returns_terminal_diagnostics():
    episode = generate_episode(2030, verifier_secret="fixed-secret")
    client = TestClient(create_single_session_app(episode))

    assert client.get("/status").json()["status"] == "active"
    finalized = client.post("/finalize")
    assert finalized.status_code == 200
    payload = finalized.json()
    assert payload["status"] == "failed"
    assert payload["turn"] == 0
    assert payload["performance"]["terminal_status"] == "failed"
    assert payload["performance"]["actions_used"] == 0
    assert payload["performance"]["rooms_visited"] == 1
    assert payload["performance"]["unsatisfied_goal_leaves"]

    # Finalization is irreversible: it cannot be used to inspect diagnostics and continue play.
    action = episode.reference_plan[0]
    response = client.post("/action", json={"expected_turn": 0, "action": action}).json()
    assert response["ok"] is False
    assert response["performance"]["terminal_status"] == "failed"


def test_request_client_sets_current_turn_for_actions(monkeypatch):
    calls = []

    def fake_json_request(base_url, method, path, payload=None):
        calls.append((base_url, method, path, payload))
        if path == "/status":
            return {
                "turn": 4,
                "status": "active",
                "actions_remaining": 7,
                "victory_code": None,
            }
        assert path == "/action"
        return {"ok": True}

    monkeypatch.setattr(service_transport, "_json_request", fake_json_request)
    request = SERVICE_REQUEST_ADAPTER.validate_python(
        {"operation": "action", "action": {"type": "wait"}}
    )

    assert request_service(request, url="http://service:8000") == {"ok": True}
    assert calls[-1][3]["expected_turn"] == 4


def test_validate_candidate_finalizes_attempt_and_preserves_validator_contract(monkeypatch):
    performance = {
        "$schema": "https://example.test/performance-v2.schema.json",
        "terminal_status": "failed",
    }

    def finalized(status_value, victory_code):
        return {
            "turn": 9,
            "status": status_value,
            "actions_remaining": 2,
            "victory_code": victory_code,
            "performance": performance,
        }

    monkeypatch.setattr(
        service_transport,
        "_json_request",
        lambda *_args, **_kwargs: finalized("failed", None),
    )
    result, diagnostics = validate_candidate_with_performance("NX-NOPE")
    assert not result.correct
    assert diagnostics == performance

    monkeypatch.setattr(
        service_transport,
        "_json_request",
        lambda *_args, **_kwargs: finalized("won", "NX-ABCD-EFGH-IJKL"),
    )
    assert not validate_candidate("NX-NOPE").correct

    assert validate_candidate("  NX-ABCD-EFGH-IJKL\n") == ValidationResult(
        correct=True,
        title="Valid victory code",
        explanation="The session is won and the submitted victory code matches it.",
    )


def test_protocol_v02_keeps_static_context_in_manifest_not_state_responses():
    episode = generate_episode(3031, verifier_secret="fixed-secret")
    assert episode.public.protocol_version == "nexus-0.2"

    client = TestClient(create_single_session_app(episode))

    manifest = client.get("/manifest").json()
    assert "goal" in manifest
    assert manifest["evidence_files"]

    observed = client.get("/observe").json()
    assert "goal" not in observed
    assert "evidence_files" not in observed

    status = client.get("/status").json()
    first_action = episode.reference_plan[0]
    acted = client.post(
        "/action",
        json={"expected_turn": status["turn"], "action": first_action},
    ).json()
    assert acted["ok"] is True
    assert "goal" not in acted["observation"]
    assert "evidence_files" not in acted["observation"]


def test_protocol_v01_loaded_episode_retains_legacy_static_observation_context():
    episode = generate_episode(3032, verifier_secret="fixed-secret")
    episode.public.protocol_version = "nexus-0.1"

    client = TestClient(create_single_session_app(episode))
    observed = client.get("/observe").json()

    assert observed["goal"] == episode.public.goal.model_dump(mode="json")
    assert observed["evidence_files"] == sorted(episode.public.evidence_files)
