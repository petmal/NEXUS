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
