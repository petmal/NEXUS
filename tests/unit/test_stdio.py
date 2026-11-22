"""Behavioral regression contracts."""

import io
import json

import pytest
from fastapi.testclient import TestClient

from nexus.generator import generate_episode
from nexus.protocol.audit import verify_bundle
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import Session
from nexus.protocol.stdio import run_jsonl


def test_stdio_can_read_public_task_and_retry_without_private_files(boundary_world, tmp_path):
    ep = boundary_world(False)
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
