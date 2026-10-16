"""Private shutdown reports preserve active gameplay and contain no receipt/secret."""

import json
import logging

from fastapi.testclient import TestClient

from nexus.generator import generate_episode
from nexus.protocol.http import create_single_session_app


def reports(caplog):
    prefix = "NEXUS operator diagnostic: "
    return [
        json.loads(r.getMessage()[len(prefix) :])
        for r in caplog.records
        if r.getMessage().startswith(prefix)
    ]


def test_extended_shutdown_is_read_only_and_not_a_public_endpoint(caplog):
    episode = generate_episode(
        438,
        axis_version=2,
        science_family="compositional-repair-v1",
        theory_level=3,
        discovery_level=5,
        planning_level=1,
        resource_pressure=1,
        verifier_secret="never-log-this-secret",
    )
    caplog.set_level(logging.INFO, logger="nexus.operator")
    with TestClient(create_single_session_app(episode, extended_diagnostics=True)) as client:
        body = {"expected_turn": 0, "action": {"type": "take", "artifact": "seal"}}
        first = client.post("/action", json=body).json()
        assert first.get("performance") is None
        assert client.post("/action", json=body).json()["duplicate"]
        assert (
            client.post(
                "/action",
                json={
                    "expected_turn": 1,
                    "action": {"type": "configure", "machine": "doser", "settings": [0, 0, 0, 0]},
                },
            ).json()["ok"]
            is False
        )  # Wrong room: no committed turn.
        assert client.get("/operator-diagnostics").status_code == 404
        assert not any("diagnostic" in p for p in client.get("/openapi.json").json()["paths"])
        before = client.get("/status").json()
        assert before["status"] == "active"
        assert [r["kind"] for r in reports(caplog)] == ["binding", "action"]
    report = reports(caplog)[-1]
    assert report["trigger"] == "shutdown"
    assert report["status"] == {k: v for k, v in before.items() if k != "victory_code"}
    assert report["performance"]["invalid_actions"] == 1
    assert report["performance"]["duplicate_requests"] == 1
    assert report["performance"]["decision_diagnostics"]["readings"] == []
    assert "never-log-this-secret" not in caplog.text
    assert "victory_code" not in json.dumps(reports(caplog))


def test_default_service_emits_no_extended_operator_journal(caplog):
    episode = generate_episode(
        0,
        axis_version=2,
        science_family="compositional-repair-v1",
        theory_level=0,
        discovery_level=0,
        planning_level=1,
        resource_pressure=1,
    )
    caplog.set_level(logging.INFO, logger="nexus.operator")
    with TestClient(create_single_session_app(episode)) as client:
        assert client.get("/status").json()["status"] == "active"
    assert not reports(caplog)


def test_terminal_http_preserves_nullable_diagnostics_and_round_trips():
    from nexus.protocol.session import ActionResponse

    episode = generate_episode(
        0,
        axis_version=2,
        science_family="compositional-repair-v1",
        theory_level=0,
        discovery_level=0,
        planning_level=1,
        resource_pressure=1,
    )
    with TestClient(create_single_session_app(episode)) as client:
        # Ineligible early finish, then the disclosed control recipe. No readings.
        for turn, action in enumerate(
            (
                {"type": "finish"},
                {"type": "take", "artifact": "seal"},
                {"type": "move", "target": "array"},
                {"type": "configure", "machine": "doser", "settings": [0, 0, 2, 0]},
                {"type": "operate", "machine": "doser", "artifact": "seal"},
                {"type": "finish"},
            )
        ):
            payload = client.post("/action", json={"expected_turn": turn, "action": action}).json()
            parsed = ActionResponse.model_validate(payload)
            assert parsed.ok
        assert parsed.victory_code
        diagnostics = payload["performance"]["decision_diagnostics"]
        assert diagnostics["first_intervention_turn"] is None
        assert diagnostics["first_intervention_measurement"] is None
        assert diagnostics["submissions"][0]["evidence"]["accepting_worlds"] is None
        assert diagnostics["readings"] is None
