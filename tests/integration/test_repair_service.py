"""Public HTTP, packaged profiles and interactive human help use the same adapter."""

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from nexus.cli import app
from nexus.generator import generate_episode
from nexus.io import load_private, save_episode
from nexus.models.episode import PlayerManifest
from nexus.ontology.repair.policy import public_policy
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import ActionResponse, SessionStatus


def episode():
    return generate_episode(
        3217,
        axis_version=2,
        science_family="coupled-repair-v1",
        discovery_level=5,
        theory_level=3,
        planning_level=1,
        resource_pressure=1,
        verifier_secret="integration",
    )


def test_http_public_policy_receipt_and_nonresettable_service():
    compiled = episode()
    client = TestClient(create_single_session_app(compiled))

    class Player:
        def manifest(self):
            return PlayerManifest.model_validate(client.get("/manifest").json())

        def evidence(self, filename):
            return client.get(f"/evidence/{filename}").text

        def observe(self):
            from nexus.models.observation import Observation

            return Observation.model_validate(client.get("/observe").json())

        def status(self):
            return SessionStatus.model_validate(client.get("/status").json())

        def act(self, expected_turn, action):
            return ActionResponse.model_validate(
                client.post(
                    "/action",
                    json={"expected_turn": expected_turn, "action": action.model_dump(mode="json")},
                ).json()
            )

    result = public_policy(Player())
    assert result.victory_code and result.current_turn == 15
    assert client.post("/finalize").json()["performance"]["certificate"]["status"] == "qualified"
    assert client.post("/sessions").status_code == 404
    assert client.get("/status").json()["status"] == "won"


def test_save_load_and_interactive_help_support_domain_payloads(tmp_path):
    compiled = episode()
    save_episode(compiled, tmp_path)
    restored = load_private(tmp_path / "private.json")
    assert restored == compiled
    result = CliRunner().invoke(app, ["play", str(tmp_path / "private.json")], # The initial stores do not reveal apparatus in the separate array room.
                                input='{"type":"move","target":"array"}\nhelp\nquit\n')
    assert result.exit_code == 0, result.exception
    assert "doser" in result.stdout and "stage" in result.stdout
