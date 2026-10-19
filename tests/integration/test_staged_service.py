"""Live wire privacy/conformance: every observation channel respects the proof."""

import json
import subprocess
import sys

from fastapi.testclient import TestClient

from nexus.generator import generate_episode
from nexus.models.episode import PlayerManifest
from nexus.models.observation import Observation
from nexus.ontology.staged.policy import public_policy
from nexus.ontology.staged.proof import oracle_read
from nexus.ontology.staged.schema import FAMILY
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import ActionResponse, SessionStatus


def episode(seed=59):
    return generate_episode(
        seed,
        axis_version=2,
        science_family=FAMILY,
        theory_level=3,
        discovery_level=4,
        planning_level=1,
        resource_pressure=1,
    )


def test_http_public_contract_actual_receipt_and_no_active_diagnostic_hints():
    ep = episode()
    client = TestClient(create_single_session_app(ep, extended_diagnostics=True))
    manifest = PlayerManifest.model_validate(client.get("/manifest").json())
    evidence = {name: client.get("/evidence/" + name).text for name in manifest.evidence_files}
    assert client.post("/sessions").status_code == 404
    assert client.get("/evidence/staged-repair-proof.json").status_code == 404
    public = [manifest.model_dump(mode="json"), evidence]

    class Player:
        def observe(self):
            return Observation.model_validate(client.get("/observe").json())

        def status(self):
            return SessionStatus.model_validate(client.get("/status").json())

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
    assert result.victory_code and client.get("/status").json()["status"] == "won"
    assert result.performance.decision_diagnostics.escape_classification == "supported_win"
    text = json.dumps(public)
    for key in (
        "construction_seed",
        "certificate",
        "remaining_loads_actual",
        "mission_signatures",
        "reference_action_upper",
    ):
        assert '"' + key + '"' not in text
    assert client.get("/status").json()["victory_code"] == result.victory_code


def test_every_reader_configuration_has_only_the_disclosed_trit_information():
    # Full runtime adapter domain against independent oracle, including treated
    # copies and cached readings. Whole returned payload is checked, not just value.
    from itertools import product

    from nexus.models.domain import DomainArtifact
    from nexus.ontology.staged.runtime import transform
    from nexus.ontology.staged.schema import Specimen

    for seed in range(216):
        ep = episode(seed)
        world = tuple((m.shift, m.exponent) for m in ep.investigation_truth.data().mechanisms)
        for stage, carrier, tag in product(range(3), repeat=3):
            sample = Specimen(tag=tag, doses=(1, 2, 1), reading=2, stage=2, carrier=2)
            artifact = DomainArtifact(
                ontology=FAMILY,
                id="survey",
                location="inventory",
                payload=sample.model_dump(mode="json"),
            )
            result = transform(artifact, "reader", ep, (stage, carrier)).model_dump(mode="json")
            expected = artifact.model_dump(mode="json")
            expected["payload"].update(
                reading=oracle_read(world, stage, carrier, tag), stage=stage, carrier=carrier
            )
            assert result == expected


def test_cold_generation_and_terminal_diagnostics_have_no_search_cost():
    code = """
import json
from time import perf_counter
from nexus.generator import generate_episode
from nexus.protocol.session import Session
from nexus.ontology.staged.policy import public_policy
s=perf_counter()
ep=generate_episode(59,axis_version=2,science_family="staged-repair-v1",theory_level=3,discovery_level=4,planning_level=1,resource_pressure=1)
generation=perf_counter()-s
s=perf_counter()
r=public_policy(Session(ep),ep.public.evidence_files)
assert r.victory_code
print(json.dumps({"generation":generation,"play_and_terminal":perf_counter()-s}))
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=15, check=True
    )
    timing = json.loads(result.stdout)
    assert timing["generation"] < 3 and timing["play_and_terminal"] < 3
