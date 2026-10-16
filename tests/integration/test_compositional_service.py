"""The evaluated HTTP interface supplies no seed, audit, or live solver hints."""

import json

from fastapi.testclient import TestClient

from nexus.engine.canonical import canonical_hash
from nexus.generator import generate_episode
from nexus.io import load_private, save_episode
from nexus.models.episode import PlayerManifest
from nexus.models.observation import Observation
from nexus.ontology.compositional.policy import public_policy
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import ActionResponse, SessionStatus


def test_http_public_policy_privacy_receipt_and_save_load(tmp_path):
    episode = generate_episode(
        219,
        axis_version=2,
        science_family="compositional-repair-v1",
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
    assert client.get("/evidence/qualification.json").status_code == 404
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
            # Terminal analytics may be supplied after the attempt; no live hints.
            if not data.get("victory_code"):
                assert data.get("performance") is None
                transcript.append(data)
            return ActionResponse.model_validate(data)

    result = public_policy(Player(), evidence)
    assert result.victory_code and result.current_turn <= 27
    assert client.get("/status").json()["status"] == "won"
    public = json.dumps(transcript)
    for key in (
        "construction_seed",
        "world_index",
        "witness_rows",
        "certificate",
        "replacement",
        "changed",
        "target_fingerprint",
    ):
        assert f'"{key}"' not in public
