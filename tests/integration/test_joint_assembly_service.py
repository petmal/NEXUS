"""Live wire conformance to all legal measurement classes and private state boundaries."""

import json
from itertools import product

from fastapi.testclient import TestClient

from nexus.generator import generate_episode
from nexus.models.domain import DomainArtifact
from nexus.models.episode import PlayerManifest
from nexus.models.observation import Observation
from nexus.ontology.assembly.laws import WORLDS, target
from nexus.ontology.assembly.policy import public_policy
from nexus.ontology.assembly.proof import oracle_read
from nexus.ontology.assembly.runtime import transform
from nexus.ontology.assembly.schema import FAMILY, Specimen
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import ActionResponse, SessionStatus


def episode(seed=136):
    return generate_episode(
        seed,
        axis_version=2,
        science_family=FAMILY,
        theory_level=3,
        discovery_level=4,
        planning_level=0,
        resource_pressure=1,
    )


def test_http_receipt_and_no_active_posterior_or_private_qualification_hints():
    ep = episode()
    client = TestClient(create_single_session_app(ep, extended_diagnostics=True))
    manifest = PlayerManifest.model_validate(client.get("/manifest").json())
    evidence = {n: client.get("/evidence/" + n).text for n in manifest.evidence_files}
    assert client.post("/sessions").status_code == 404
    assert client.get("/evidence/joint-assembly-proof.json").status_code == 404
    public = [manifest.model_dump(mode="json"), evidence]

    class Player:
        def status(self):
            return SessionStatus.model_validate(client.get("/status").json())

        def observe(self):
            return Observation.model_validate(client.get("/observe").json())

        def act(self, expected_turn, action):
            response = client.post(
                "/action",
                json={"expected_turn": expected_turn, "action": action.model_dump(mode="json")},
            )
            assert response.status_code == 200
            data = response.json()
            if not data.get("victory_code"):
                assert data.get("performance") is None
                public.append(data)
            return ActionResponse.model_validate(data)

    result = public_policy(Player(), evidence)
    assert (
        result.victory_code
        and result.performance.decision_diagnostics.escape_classification == "supported_win"
    )
    assert client.get("/status").json()["victory_code"] == result.victory_code
    text = json.dumps(public)
    for name in (
        "construction_seed",
        "mission_signatures",
        "certificate",
        "reference_action_upper",
        "remaining_worlds",
        "accepting_worlds",
    ):
        assert '"' + name + '"' not in text


def test_every_live_reader_setting_matches_independent_oracle_without_extra_payload():
    for seed, world in enumerate(WORLDS):
        ep = episode(seed)
        for ch, x, y in product(range(3), repeat=3):
            sample = Specimen(b=(2, 1), c=(1, 2), kernel=3)
            artifact = DomainArtifact(
                ontology=FAMILY,
                id="survey",
                location="@inventory",
                payload=sample.model_dump(mode="json"),
            )
            actual = transform(artifact, "reader", ep, (ch, x, y)).model_dump(mode="json")
            expected = artifact.model_dump(mode="json")
            expected["payload"]["reading"] = {
                "channel": ch,
                "x": x if ch != 1 else 0,
                "y": y if ch != 0 else 0,
                "value": oracle_read((*target(world), world.offset), (ch, x, y)),
            }
            assert actual == expected
