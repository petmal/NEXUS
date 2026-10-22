"""New ontology retains HTTP persistence, preview, rollback and private telemetry."""

import json
import logging

from fastapi.testclient import TestClient

from nexus.generator import generate_episode
from nexus.protocol.http import create_single_session_app


def test_revision_http_contract_and_compact_shutdown_report(caplog):
    ep = generate_episode(
        5866,
        axis_version=2,
        science_family="model-revision-v1",
        theory_level=3,
        discovery_level=5,
        planning_level=0,
        resource_pressure=1,
        verifier_secret="http-revision-secret",
    )
    caplog.set_level(logging.INFO, logger="nexus.operator")
    with TestClient(create_single_session_app(ep, extended_diagnostics=True)) as client:
        manifest = client.get("/manifest").json()
        assert "certificate_queries" not in json.dumps(manifest)
        assert client.get("/operator-diagnostics").status_code == 404
        take = client.post(
            "/action", json={"expected_turn": 0, "action": {"type": "take", "artifact": "carrier"}}
        ).json()
        assert take["ok"] and take.get("performance") is None
        invalid = client.post(
            "/action",
            json={
                "expected_turn": 1,
                "action": {"type": "configure", "machine": "reader", "settings": [2]},
            },
        ).json()
        assert not invalid["ok"] and invalid["current_turn"] == 1
        for turn, action in enumerate(
            (
                {"type": "configure", "machine": "reader", "settings": [0, 1, 0]},
                {"type": "probe", "machine": "reader", "artifact": "carrier"},
            ),
            start=1,
        ):
            result = client.post("/action", json={"expected_turn": turn, "action": action}).json()
            assert result["ok"] and result.get("performance") is None
        assert client.get("/status").json()["turn"] == 3
    prefix = "NEXUS operator summary: "
    summary = json.loads(caplog.records[-1].getMessage().split(prefix)[1])
    assert summary["status"] == "active" and summary["turn"] == 3
    assert summary["measurement_accounting"]["preview_readings"] == 1
    assert "http-revision-secret" not in caplog.text
    assert summary["receipt_validation"] == "not_observed_by_service"
