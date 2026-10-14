"""Presentation changes cannot alter laws, evidence values or operational success."""

import json

import pytest
from fastapi.testclient import TestClient

from nexus.engine.canonical import canonical_hash
from nexus.generator import generate_episode
from nexus.io import load_private, save_episode
from nexus.models.actions import ACTION_ADAPTER
from nexus.models.episode import PlayerManifest
from nexus.ontology.categorical.generation import generate_categorical, public_policy
from nexus.presentation import CURRENT, attach, evidence_files
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import Session


@pytest.mark.parametrize(
    "family",
    [
        "legacy",
        "shared-response-v1",
        "coupled-network-v1",
        "resonant-network-v1",
        "causal-mechanisms-v1",
        "categorical-chain-poc-v1",
    ],
)
def test_shared_setting_preserves_every_family_execution_and_receipt(family, tmp_path):
    if family == "categorical-chain-poc-v1":
        current = generate_categorical(7, depth=2, verifier_secret="presentation")
    else:
        current = generate_episode(
            7,
            axis_version=1 if family == "legacy" else 2,
            science_family="shared-response-v1" if family == "legacy" else family,
            discovery_level=0,
            theory_level=0,
            planning_level=1,
            resource_pressure=0,
            verifier_secret="presentation",
        )
    assert current.public.presentation_version == CURRENT
    old = attach(current, None)
    assert "presentation_version" not in old.public.model_dump()
    assert "presentation_version" not in PlayerManifest.from_episode(old.public).model_dump()
    sessions = [Session(e) for e in (old, current)]
    for session in sessions:
        if family == "categorical-chain-poc-v1":
            result = public_policy(session)
        elif family == "causal-mechanisms-v1":
            from nexus.ontology.causal.policy import public_policy as causal_policy

            result = causal_policy(session, evidence_files(session.episode.public))
        else:
            for action in current.reference_plan:
                result = session.act(session.state.turn, ACTION_ADAPTER.validate_python(action))
                assert result.ok
        assert result.victory_code
    assert sessions[0].trace == sessions[1].trace
    assert canonical_hash(sessions[0].state) == canonical_hash(sessions[1].state)
    assert sessions[0].status() == sessions[1].status()
    assert current.public.evidence_files == old.public.evidence_files
    client = TestClient(create_single_session_app(current))
    assert "sealed artificial facility" in client.get("/manifest").json()["description"]
    assert client.get("/observe").json()["room_label"].startswith("Sector ")
    save_episode(current, tmp_path)
    assert load_private(tmp_path / "private.json") == current
    for filename, content in evidence_files(current.public).items():
        assert client.get(f"/evidence/{filename}").text == content
        assert (tmp_path / "attachments" / filename).read_text() == content
        if filename == "theory.json":
            assert content == old.public.evidence_files[filename]
        if filename == "map.json":
            assert all(v.startswith("Sector ") for v in json.loads(content)["rooms"].values())


def test_presentation_version_is_validated_before_expensive_generation():
    with pytest.raises(ValueError, match="presentation"):
        generate_episode(7, presentation_version="future-invalid")
