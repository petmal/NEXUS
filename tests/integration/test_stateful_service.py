"""The state-changing mission survives the HTTP boundary without resets or hints."""

import json

from fastapi.testclient import TestClient

from nexus.engine.canonical import canonical_hash
from nexus.generator import generate_episode
from nexus.io import load_private, save_episode
from nexus.models.episode import PlayerManifest
from nexus.models.observation import Observation
from nexus.ontology.stateful.policy import public_policy
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import ActionResponse, SessionStatus


def test_stateful_http_policy_privacy_and_saved_episode(tmp_path):
    episode = generate_episode(
        229,
        axis_version=2,
        science_family="stateful-discovery-v1",
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
    assert client.get("/evidence/stateful-preflight.json").status_code == 404
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
    assert result.performance.decision_diagnostics.escape_classification == "supported_win"
    assert client.get("/status").json()["status"] == "won"
    public = json.dumps(transcript)
    for key in (
        "construction_seed",
        "reference_action_upper",
        "leading_actions",
        "verifier_secret",
    ):
        assert f'"{key}"' not in public
