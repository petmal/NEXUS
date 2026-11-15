"""Versioned family through live HTTP, player privacy, persistence and termination."""

import json
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient

from nexus.engine.canonical import canonical_hash
from nexus.generator import generate_episode
from nexus.io import load_private, save_episode
from nexus.models.episode import PlayerManifest
from nexus.models.observation import Observation
from nexus.ontology.history.policy import public_policy
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import ActionResponse, SessionStatus


def test_http_history_contract_receipt_and_roundtrip(tmp_path):
    episode = generate_episode(
        440,
        axis_version=2,
        science_family="history-coupled-v1",
        theory_level=3,
        discovery_level=5,
        planning_level=1,
        resource_pressure=1,
    )
    save_episode(episode, tmp_path)
    loaded = load_private(tmp_path / "private.json")
    assert canonical_hash(loaded) == canonical_hash(episode)
    client = TestClient(create_single_session_app(loaded))
    manifest = PlayerManifest.model_validate(client.get("/manifest").json())
    evidence = {name: client.get(f"/evidence/{name}").text for name in manifest.evidence_files}
    assert client.post("/sessions").status_code == 404
    assert client.get("/evidence/history-coupled-proof.json").status_code == 404
    transcript = [manifest.model_dump(mode="json"), evidence]

    class Player:
        def observe(self):
            return Observation.model_validate(client.get("/observe").json())

        def status(self):
            return SessionStatus.model_validate(client.get("/status").json())

        def act(self, expected_turn, action):
            data = client.post(
                "/action",
                json={"expected_turn": expected_turn, "action": action.model_dump(mode="json")},
            ).json()
            if not data.get("victory_code"):
                assert data.get("performance") is None
                transcript.append(data)
            return ActionResponse.model_validate(data)

    result = public_policy(Player(), evidence)
    assert result.victory_code
    assert client.post("/finalize").json()["performance"]["decision_diagnostics"]["escape_classification"] == "supported_win"
    assert client.get("/status").json()["status"] == "won"
    public = json.dumps(transcript)
    for key in (
        "construction_seed",
        "certificate",
        "reference_action_upper",
        "winning",
        "gates",
        "a",
        "b",
    ):
        assert f'"{key}"' not in public


@pytest.mark.parametrize("ending", ["win", "exhaust", "finalize"])
def test_cold_process_history_generation_and_terminal_stay_bounded(ending):
    script = r"""
import json,sys
from time import perf_counter
from fastapi.testclient import TestClient
from nexus.generator import generate_episode
from nexus.ontology.history.policy import public_policy
from nexus.protocol.session import Session
from nexus.protocol.http import create_single_session_app
from nexus.models.actions import WaitAction
start=perf_counter()
ep=generate_episode(440,axis_version=2,science_family="history-coupled-v1",theory_level=3,discovery_level=5,planning_level=1,resource_pressure=1)
generation=perf_counter()-start
start=perf_counter()
if sys.argv[1]=="finalize":
    result=TestClient(create_single_session_app(ep)).post("/finalize").json()
    assert result["performance"]["terminal_status"]=="failed"
else:
    session=Session(ep)
    if sys.argv[1]=="win":
        result=public_policy(session,ep.public.evidence_files)
        assert result.victory_code
    else:
        for _ in range(ep.generation_metadata.action_budget):
            result=session.act(expected_turn=session.state.turn,action=WaitAction())
        assert result.performance.terminal_status=="failed"
print(json.dumps({"generation":generation,"terminal_including_play":perf_counter()-start}))
"""
    result = subprocess.run(
        [sys.executable, "-c", script, ending],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    timing = json.loads(result.stdout)
    assert timing["generation"] < 15 and timing["terminal_including_play"] < 8
