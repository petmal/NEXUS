"""Commitment policy and public-evidence assistance preserve the game boundary."""

import json

import pytest
from fastapi.testclient import TestClient

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.generator import generate_episode, qualify_episode
from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.models.episode import PrivateEpisode
from nexus.ontology.discovery.policy import public_policy
from nexus.protocol.client import SERVICE_REQUEST_ADAPTER
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import Session
from nexus.protocol.transport import ClientError, request_service_payload


def episode(**options):
    return generate_episode(
        5866,
        axis_version=2,
        science_family="model-revision-v1",
        theory_level=3,
        discovery_level=5,
        planning_level=0,
        resource_pressure=1,
        ontology_options=options,
        verifier_secret="intervention-secret",
    )


def act(s, action):
    response = s.act(s.state.turn, action)
    assert response.ok
    return response


def install(s, build):
    act(s, ConfigureAction(machine="assembler", settings=build))
    act(s, OperateAction(machine="assembler", artifact="carrier"))


@pytest.mark.parametrize("policy,expected", [("recoverable", "active"), ("single", "failed")])
def test_first_eligible_wrong_finish_obeys_disclosed_policy_and_replays(policy, expected):
    ep = episode(finish_policy=policy)
    s = Session(ep)
    act(s, TakeAction(artifact="carrier"))
    install(s, ep.public.investigation.data().provisional)
    result = act(s, FinishAction())
    assert s.state.terminal_status.value == expected
    assert s.state.resources.actions_remaining == 60
    assert result.victory_code is None
    if policy == "single":
        assert result.performance.termination_reason == "single_shot_rejection"
        assert (
            result.performance.decision_diagnostics.submissions[0].evidence.classification
            == "compatible"
        )
        assert not s.act(s.state.turn, FinishAction()).ok
    assert canonical_hash(replay(ep, s.trace)) == canonical_hash(s.state)


def test_single_ineligible_finishes_do_not_falsify_the_build_or_end_attempt():
    s = Session(episode(finish_policy="single"))
    act(s, FinishAction())
    act(s, TakeAction(artifact="carrier"))
    act(s, FinishAction())
    assert s.state.terminal_status.value == "active"
    assert all(
        x["classification"] == "ineligible"
        for x in s.operator_snapshot()["evidence_witnesses"]["submissions"]
    )
    assert public_policy(s, s.episode.public.evidence_files).victory_code


@pytest.mark.parametrize("policy", ["single", "recoverable"])
def test_variants_serialize_qualify_and_public_policy_wins(policy):
    ep = PrivateEpisode.model_validate_json(
        episode(finish_policy=policy, consistency_check="readings").model_dump_json()
    )
    assert qualify_episode(ep).passed
    s = Session(ep)
    assert public_policy(s, ep.public.evidence_files).victory_code
    assert (
        s.operator_snapshot()["performance"]["decision_diagnostics"]["escape_classification"]
        == "supported_win"
    )
    assert canonical_hash(replay(ep, s.trace)) == canonical_hash(s.state)


def test_checker_is_consistency_only_and_changes_no_world_state():
    ep = episode(consistency_check="readings")
    s = Session(ep)
    build = ep.public.investigation.data().provisional
    before = canonical_hash(s.state)
    checked = s.check_construction(build)
    assert checked.consistent_with_readings and checked.distinct_readings_checked == 2
    assert checked.evidence_turn == 0
    assert canonical_hash(s.state) == before and not s.trace
    act(s, TakeAction(artifact="carrier"))
    install(s, build)
    assert act(s, FinishAction()).victory_code is None
    # Finish feedback is intentionally outside this checker scope.
    assert s.check_construction(build).consistent_with_readings
    act(s, ConfigureAction(machine="reader", settings=(0, 1, 0)))
    act(s, ProbeAction(machine="reader", artifact="carrier"))
    assert not s.check_construction(build).consistent_with_readings
    snapshot = s.operator_snapshot()
    assert snapshot["assistance"]["construction_check_calls"] == 3
    assert s.check_construction(ep.investigation_truth.data().program).consistent_with_readings
    assert canonical_hash(replay(ep, s.trace)) == canonical_hash(s.state)


def test_checker_http_is_absent_when_disabled_and_strict_when_enabled():
    with TestClient(create_single_session_app(episode())) as client:
        assert client.post("/check", json={"build": [0, 0, 0, 0]}).status_code == 404
        assert "/check" not in client.get("/openapi.json").json()["paths"]
    with TestClient(create_single_session_app(episode(consistency_check="readings"))) as client:
        response = client.post("/check", json={"build": [0, 0, 3, 0]})
        assert response.status_code == 200 and response.json()["consistent_with_readings"]
        assert client.get("/status").json()["turn"] == 0
        for build in ([True, 0, 0, 0], ["0", 0, 0, 0], [0, 0], [12, 0, 0, 0]):
            assert client.post("/check", json={"build": build}).status_code == 422
        assert client.post("/check", json={"build": [0, 0, 0, 0], "truth": []}).status_code == 422
        client.post("/finalize")
        assert client.post("/check", json={"build": [0, 0, 0, 0]}).status_code == 422


def test_single_contract_contains_no_conflicting_recoverable_promise():
    s = Session(episode(finish_policy="single", consistency_check="readings"))
    manifest = s.manifest().model_dump_json()
    theory = json.loads(s.episode.public.evidence_files["theory.json"])
    assert theory["finish_policy"]["name"] == "single"
    assert "is recoverable while actions" not in s.episode.public.evidence_files["apparatus.txt"]
    assert "binary and recoverable while actions" not in manifest
    assert '"operation":"check"' in manifest


def test_checker_client_and_fast_transport_agree(monkeypatch):
    payload = {"operation": "check", "build": [0, 0, 3, 0]}
    assert SERVICE_REQUEST_ADAPTER.validate_python(payload).model_dump(mode="json") == payload
    seen = []

    def request(url, method, path, body):
        seen.append((method, path, body))
        return {"consistent_with_readings": True}

    monkeypatch.setattr("nexus.protocol.transport._json_request", request)
    assert request_service_payload(payload)["consistent_with_readings"]
    assert seen == [("POST", "/check", {"build": [0, 0, 3, 0]})]
    with pytest.raises(ClientError):
        request_service_payload({"operation": "check", "build": [True]})


def test_public_client_compatibility_exports_remain_available():
    from nexus.protocol import transport
    from nexus.protocol.client import ClientError, check_health, service_url

    assert ClientError is transport.ClientError
    assert check_health is transport.check_health
    assert service_url is transport.service_url


@pytest.mark.parametrize("enabled", [False, True])
def test_human_play_can_use_exactly_the_disclosed_checker(tmp_path, enabled):
    from typer.testing import CliRunner

    from nexus.cli import app
    from nexus.io import save_episode
    from nexus.protocol.audit import verify_bundle

    ep = episode(consistency_check="readings") if enabled else episode()
    save_episode(ep, tmp_path / "world")
    build = list(ep.public.investigation.data().provisional)
    request = json.dumps({"operation": "check", "build": build})
    audit = tmp_path / "attempt"
    transcript = CliRunner().invoke(
        app, ["play", str(tmp_path / "world/private.json"), "--audit-dir", str(audit)],
        input="help\n" + request + '\n{"operation":"check","build":[true]}\nquit\n',
        env={"COLUMNS": "160", "NO_COLOR": "1"},
    )
    assert transcript.exit_code == 0, transcript.output
    assert ("consistent_with_readings" in transcript.output) is enabled
    assert ('"operation":"check"' in transcript.output) is enabled
    outcome = json.loads((audit / "outcome.json").read_bytes())
    assert outcome["assistance"]["construction_check_calls"] == int(enabled)
    assert verify_bundle(audit)["accepted_actions"] == 0
