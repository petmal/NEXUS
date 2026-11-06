"""Presentation changes cannot alter laws, evidence values or operational success."""

import json
import hashlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from nexus.engine.canonical import canonical_hash
from nexus.generator import generate_episode
from nexus.io import load_private, save_episode
from nexus.models.actions import ACTION_ADAPTER
from nexus.models.episode import PlayerManifest
from nexus.ontology.categorical.generation import generate_categorical, public_policy
from nexus.ontology.catalog import BUILTINS
from nexus.presentation import CURRENT, attach, description, evidence_files, room_label
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
    sessions = [Session(e) for e in (old, attach(current, "sealed-facility-v1"), current)]
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
    for session in sessions[1:]:
        assert sessions[0].trace == session.trace
        assert canonical_hash(sessions[0].state) == canonical_hash(session.state)
        assert sessions[0].status() == session.status()
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


@pytest.mark.parametrize("family", ("coupled-network-v1", "resonant-network-v1"))
@pytest.mark.parametrize("version", (None, "sealed-facility-v1", CURRENT))
def test_recompiled_qualification_preserves_selected_presentation(family, version):
    from nexus.generator import qualify_episode

    episode = generate_episode(
        7,
        axis_version=2,
        science_family=family,
        theory_level=3,
        discovery_level=0,
        planning_level=0,
        resource_pressure=1,
        presentation_version=version,
    )
    assert qualify_episode(episode).passed


def story_episode(family):
    if family == "categorical-chain-poc-v1":
        return generate_categorical(7, depth=2, verifier_secret="story-review")
    theory, discovery = (3, 5) if family == "coupled-repair-v1" else (0, 0)
    if family == "stateful-planning-v1":
        discovery = 5
    return generate_episode(
        7, axis_version=1 if family == "legacy" else 2,
        science_family="shared-response-v1" if family == "legacy" else family,
        theory_level=theory, discovery_level=discovery, planning_level=0,
        resource_pressure=1, verifier_secret="story-review",
    )


@pytest.mark.parametrize("family", ["legacy", *BUILTINS])
def test_every_shipped_family_preserves_v1_text_and_shares_v2_player_records(family, tmp_path):
    """Golden v1 digests were recorded before v2, not generated from expected v2 output."""
    episode = story_episode(family)
    assert episode.public.presentation_version == CURRENT
    historical = attach(episode, "sealed-facility-v1").public
    old_text = {
        "description": description(historical),
        "evidence": evidence_files(historical),
        "rooms": {rid: room_label(historical, rid) for rid in historical.rooms},
    }
    snapshots = json.loads(
        (Path(__file__).parents[1] / "fixtures/presentation-v1.json").read_text()
    )
    assert set(snapshots) == {"legacy", *BUILTINS}
    actual = hashlib.sha256(
        json.dumps(old_text, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert actual == snapshots[family]["sha256"]

    before = episode.model_dump_json()
    session = Session(episode)
    client = TestClient(create_single_session_app(episode))
    assert client.get("/manifest").json()["description"] == session.manifest().description
    save_episode(episode, tmp_path)
    assert load_private(tmp_path / "private.json") == episode
    records = evidence_files(episode.public)
    orientation_files = {"facility.txt", "manual.txt", "manual.md", "facility_manual.txt"}
    assert orientation_files & records.keys(), "Every family needs a discoverable orientation"
    for filename, text in records.items():
        assert session.evidence(filename) == text
        assert client.get(f"/evidence/{filename}").text == text
        assert (tmp_path / "attachments" / filename).read_text() == text
        if filename in orientation_files:
            assert text.startswith("CONSOLE ORIENTATION\n")
        elif filename != "map.json":
            # Wording cannot rewrite numbers, formulas, measurements or legal controls.
            assert text == episode.public.evidence_files[filename]
    assert episode.model_dump_json() == before
    assert session.trace == []
    assert canonical_hash(session.state) == canonical_hash(episode.public.initial_state)


def test_revision_brief_does_not_claim_disclosed_routing_is_hidden_or_reveal_the_hidden_case():
    episodes = [generate_episode(
        2073, axis_version=2, science_family="model-revision-v1",
        theory_level=theory, discovery_level=discovery, planning_level=0,
        resource_pressure=1, verifier_secret="story-review",
    ) for theory, discovery in ((0, 0), (3, 5))]
    briefings = [Session(ep).evidence("facility.txt") for ep in episodes]
    assert briefings[0] == briefings[1]
    assert "composed routing is hidden" not in briefings[0]
    for ep in episodes:
        assert Session(ep).evidence("theory.json") == ep.public.evidence_files["theory.json"]
        assert "composed routing is hidden" in Session(
            attach(ep, "sealed-facility-v1")
        ).evidence("facility.txt")


def test_v2_map_keeps_existing_nested_room_functions_without_aliasing_labels():
    episode = story_episode("legacy")
    rid = next(iter(episode.public.rooms))
    rooms = {rid: {"label": "Public workshop", "public_note": "Control panel"}}
    episode.public.evidence_files["map.json"] = json.dumps({"rooms": rooms, "edges": []})
    before = episode.public.evidence_files["map.json"]
    rendered = json.loads(Session(episode).evidence("map.json"))
    assert rendered["sector_functions"] == rooms
    assert rendered["rooms"][rid]["label"] == f"Sector {rid}"
    assert rendered["rooms"][rid]["public_note"] == "Control panel"
    assert set(rendered["rooms"]) == set(rooms)
    assert episode.public.evidence_files["map.json"] == before


@pytest.mark.parametrize("family", (
    "coupled-transfer-v1", "coupled-evidence-v1", "history-coupled-v1", "staged-repair-v1",
))
def test_v2_portable_parts_are_not_described_as_the_exit_lock(family):
    episode = story_episode(family)
    original = episode.model_dump_json()
    text = Session(episode).manifest().description + Session(episode).evidence("facility.txt")
    for ambiguous in (
        "carried exit seal", "An exit seal must cancel", "construct an exit seal",
        "three exit seals", "Three exit seals",
    ):
        assert ambiguous not in text
    assert "seal component" in text
    assert Session(episode).evidence("theory.json") == episode.public.evidence_files["theory.json"]
    assert episode.model_dump_json() == original
