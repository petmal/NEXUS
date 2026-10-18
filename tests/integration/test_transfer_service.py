"""New families work through the same public HTTP contract and live receipt boundary."""

import json

import pytest
from fastapi.testclient import TestClient

from nexus.engine.canonical import canonical_hash
from nexus.generator import generate_episode
from nexus.io import load_private, save_episode
from nexus.models.episode import PlayerManifest
from nexus.models.observation import Observation
from nexus.ontology.transfer.policy import public_policy
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import ActionResponse, SessionStatus


@pytest.mark.parametrize("family", ["coupled-transfer-v1", "coupled-evidence-v1"])
def test_http_public_evidence_privacy_receipt_and_save_load(tmp_path, family):
    episode = generate_episode(
        3550,
        axis_version=2,
        science_family=family,
        discovery_level=5,
        theory_level=3,
        planning_level=1,
        resource_pressure=1,
        verifier_secret="integration",
    )
    save_episode(episode, tmp_path)
    compiled = load_private(tmp_path / "private.json")
    assert canonical_hash(compiled) == canonical_hash(episode)
    client = TestClient(create_single_session_app(compiled))
    manifest = PlayerManifest.model_validate(client.get("/manifest").json())
    evidence = {name: client.get(f"/evidence/{name}").text for name in manifest.evidence_files}
    assert client.get("/evidence/reference.json").status_code == 404
    assert client.post("/sessions").status_code == 404
    transcript = [manifest.model_dump(mode="json"), evidence]

    class Player:
        def observe(self):
            data = client.get("/observe").json()
            transcript.append(data)
            return Observation.model_validate(data)

        def status(self):
            data = client.get("/status").json()
            transcript.append(data)
            return SessionStatus.model_validate(data)

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
    assert (
        result.victory_code
        and result.current_turn <= episode.generation_metadata.guaranteed_policy_action_count
    )
    assert client.get("/status").json()["status"] == "won"
    public = json.dumps(transcript)
    for key in (
        "construction_seed",
        "reader_offset",
        "program",
        "certificate",
        "semantic_digest",
        "reference_action_upper",
    ):
        assert f'"{key}"' not in public


@pytest.mark.parametrize("family", ["coupled-transfer-v1", "coupled-evidence-v1"])
@pytest.mark.parametrize("ending", ["win", "exhaust", "finalize"])
def test_cold_terminal_response_uses_verified_tables_without_scalar_compilation(family, ending):
    # A fresh process prevents a warm cache from hiding the production regression.
    import subprocess
    import sys

    script = r"""
import json, sys
from time import perf_counter
from fastapi.testclient import TestClient
from nexus.generator import generate_episode
from nexus.ontology.transfer.laws import signatures, targets
from nexus.ontology.transfer.policy import public_policy
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import ActionResponse, SessionStatus
from nexus.models.observation import Observation

ep = generate_episode(3550, axis_version=2, science_family=sys.argv[1],
    discovery_level=5, theory_level=3, planning_level=1, resource_pressure=1)
client = TestClient(create_single_session_app(ep))
class Player:
    def observe(self): return Observation.model_validate(client.get('/observe').json())
    def status(self): return SessionStatus.model_validate(client.get('/status').json())
    def act(self, expected_turn, action):
        response = client.post('/action', json=dict(expected_turn=expected_turn,
            action=action.model_dump(mode='json')))
        assert response.status_code == 200, response.text
        return ActionResponse.model_validate(response.json())
started = perf_counter()
if sys.argv[2] == 'win':
    result = public_policy(Player(), ep.public.evidence_files)
    assert result.victory_code and result.performance
elif sys.argv[2] == 'exhaust':
    for turn in range(ep.generation_metadata.action_budget):
        result = client.post('/action', json=dict(expected_turn=turn, action={'type':'wait'})).json()
        if turn + 1 < ep.generation_metadata.action_budget:
            assert result.get('performance') is None
    assert result['performance']['terminal_status'] == 'failed'
else:
    result = client.post('/finalize').json()
    assert result['performance']['terminal_status'] == 'failed'
assert signatures.cache_info().currsize == targets.cache_info().currsize == 0
print(json.dumps({'seconds':perf_counter()-started}))
"""
    result = subprocess.run(
        [sys.executable, "-c", script, family, ending],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    # Broad guard: far below the former 10s inner deadline; no microbenchmark gate.
    assert json.loads(result.stdout)["seconds"] < 8
