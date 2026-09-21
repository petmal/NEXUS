from io import StringIO

from nexus.generator import generate_episode, qualify_episode
from nexus.protocol.stdio import run_jsonl


def test_generate_qualify_and_stdio_bootstrap():
    episode = generate_episode(2026)
    assert qualify_episode(episode).passed
    output = StringIO()
    run_jsonl(episode, StringIO(""), output)
    assert '"observation"' in output.getvalue()
    assert episode.verifier_secret not in output.getvalue()


def test_http_session_round_trip_and_public_evidence():
    from fastapi.testclient import TestClient
    from nexus.protocol.http import create_app

    episode = generate_episode(2027)
    client = TestClient(create_app(episode))

    manifest = client.get("/manifest")
    assert manifest.status_code == 200
    manifest_payload = manifest.json()
    assert manifest_payload["episode_id"] == episode.public.episode_id
    assert manifest_payload["description"] == episode.public.description
    assert manifest_payload["evidence_files"] == ["measurements.csv"]
    assert episode.verifier_secret not in manifest.text

    evidence = client.get("/evidence/measurements.csv")
    assert evidence.status_code == 200
    assert evidence.text == episode.public.evidence_files["measurements.csv"]
    assert episode.verifier_secret not in evidence.text

    created = client.post("/sessions")
    assert created.status_code == 200
    payload = created.json()
    session_id = payload["session_id"]
    assert payload["manifest"] == manifest_payload

    action = episode.reference_plan[0]
    response = client.post(
        f"/sessions/{session_id}/actions",
        json={"expected_turn": 0, "action": action},
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True

    duplicate = client.post(
        f"/sessions/{session_id}/actions",
        json={"expected_turn": 0, "action": action},
    )
    assert duplicate.json()["duplicate"] is True
