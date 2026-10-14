"""The public transcript includes free, invalid, retry and transport responses."""

import io
import json

import pytest
from fastapi.testclient import TestClient

from nexus.engine.canonical import canonical_hash
from nexus.models.actions import ConfigureAction, ObserveAction, TakeAction
from nexus.ontology.categorical.generation import generate_categorical
from nexus.protocol.http import create_app, create_single_session_app
from nexus.protocol.public_transcript import PublicTranscript
from nexus.protocol.session import Session
from nexus.protocol.stdio import run_jsonl


@pytest.fixture
def episode():
    return generate_categorical(7, depth=2, verifier_secret="transcript")


def test_direct_calls_record_exact_responses_without_polluting_replay(episode):
    session = Session(episode)
    manifest = session.manifest()
    assert session.public_transcript.snapshot()["records"][0]["response"] == manifest.model_dump(
        mode="json"
    )
    session.evidence("manual.txt")
    session.observe()
    session.status()
    with pytest.raises(KeyError):
        session.evidence("unknown")
    session.act(0, ObserveAction())
    bad = session.act(0, ConfigureAction(machine="board", settings=(9,)))
    assert not bad.ok and not session.trace
    action = TakeAction(artifact="S0")
    first = session.act(0, action)
    duplicate = session.act(0, action)
    conflict = session.act(0, TakeAction(artifact="S1"))
    assert duplicate.duplicate and not conflict.ok
    snapshot = session.public_transcript.snapshot()
    assert snapshot["complete"] and len(snapshot["records"]) == 10
    assert len(session.trace) == 1
    assert snapshot["records"][-3]["response"] == first.model_dump(mode="json", exclude_none=True)
    assert (
        snapshot["records"][-2]["effects"][0]["before"]
        == snapshot["records"][-2]["effects"][0]["after"]
    )
    assert snapshot["records"][-3]["effects"][0]["after"]["turn"] == 1
    assert "verifier_secret" not in json.dumps(snapshot)
    snapshot["records"].clear()
    assert len(session.public_transcript.snapshot()["records"]) == 10


def test_http_records_validation_free_errors_and_full_response_projection(episode):
    app = create_single_session_app(episode)
    client = TestClient(app)
    replies = [
        client.get("/manifest"),
        client.get("/evidence/manual.txt"),
        client.get("/evidence/missing"),
        client.get("/observe"),
        client.get("/status"),
        client.post("/action", json={"expected_turn": 0, "action": {"type": "made-up"}}),
        client.post("/action", content="{malformed", headers={"content-type": "application/json"}),
        client.post(
            "/action", json={"expected_turn": 0, "action": {"type": "take", "artifact": "S0"}}
        ),
        client.post(
            "/action", json={"expected_turn": 0, "action": {"type": "take", "artifact": "S0"}}
        ),
        client.get("/events"),
    ]
    snapshot = app.state.public_transcript.snapshot()
    assert snapshot["complete"] and len(snapshot["records"]) == len(replies)
    for record, reply in zip(snapshot["records"], replies):
        assert record["response"]["status"] == reply.status_code
        expected = (
            reply.json() if "application/json" in reply.headers["content-type"] else reply.text
        )
        assert record["response"]["body"] == expected
    assert replies[5].status_code == replies[6].status_code == 422
    assert snapshot["records"][7]["effects"][0]["after"]["turn"] == 1
    assert snapshot["records"][8]["response"]["body"]["duplicate"]
    assert len(replies[-1].json()) == 1
    assert all(
        "performance" not in r["response"]["body"]
        for r in snapshot["records"]
        if isinstance(r["response"]["body"], dict)
    )


def test_multisession_validation_and_pre_session_evidence_are_captured(episode):
    app = create_app(episode)
    client = TestClient(app)
    client.get("/evidence/manual.txt")
    session_id = client.post("/sessions").json()["session_id"]
    client.post(f"/sessions/{session_id}/actions", json={})
    client.get("/sessions/missing/status")
    snapshot = app.state.public_transcript.snapshot()
    assert snapshot["complete"] and len(snapshot["records"]) == 4
    assert [r["response"]["status"] for r in snapshot["records"]] == [200, 200, 422, 404]


def test_stdio_records_parser_failures_and_preserves_output(episode):
    stream = io.StringIO('bad json\n{"action":{"type":"take","artifact":"S0"}}\n')
    output = io.StringIO()
    transcript = PublicTranscript()
    run_jsonl(episode, stream, output, transcript=transcript)
    rows = [json.loads(line) for line in output.getvalue().splitlines()]
    recorded = transcript.snapshot()["records"]
    assert [r["response"] for r in recorded] == rows
    assert rows[1]["ok"] is False and rows[2]["ok"] is True


def test_transcript_limits_fail_coverage_closed_without_changing_world(episode):
    session = Session(episode)
    session.public_transcript = PublicTranscript(max_records=1, max_bytes=1000)
    before = canonical_hash(session.state)
    session.status()
    session.status()
    snapshot = session.public_transcript.snapshot()
    assert not snapshot["complete"] and snapshot["exchanges_seen"] == 2
    assert len(snapshot["records"]) == 1 and snapshot["bytes_retained"] <= 1000
    assert canonical_hash(session.state) == before


def test_http_outer_capture_includes_unhandled_error_response(episode):
    app = create_single_session_app(episode)

    @app.get("/test-failure")
    def failed():
        raise RuntimeError("private diagnostic must not enter the player response")

    client = TestClient(app, raise_server_exceptions=False)
    reply = client.get("/test-failure")
    snapshot = app.state.public_transcript.snapshot()
    assert snapshot["complete"]
    assert snapshot["records"][0]["response"]["status"] == reply.status_code == 500
    assert snapshot["records"][0]["response"]["body"] == reply.text == "Internal Server Error"
    assert "private diagnostic" not in json.dumps(snapshot)


def test_broken_stdio_delivery_marks_coverage_incomplete(episode):
    class Broken(io.StringIO):
        def write(self, text):
            raise BrokenPipeError("closed")

    transcript = PublicTranscript()
    with pytest.raises(BrokenPipeError):
        run_jsonl(episode, io.StringIO(), Broken(), transcript=transcript)
    assert not transcript.snapshot()["complete"]


def test_json_looking_evidence_remains_plain_text(episode):
    episode.public.evidence_files["map.json"] = '{"rooms": {"lab": "Laboratory"}}'
    app = create_single_session_app(episode)
    reply = TestClient(app).get("/evidence/map.json")
    assert app.state.public_transcript.snapshot()["records"][0]["response"]["body"] == reply.text
