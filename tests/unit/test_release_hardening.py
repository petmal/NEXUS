"""Regression tests for malformed input and public identity boundaries."""

import hashlib
import io
import json

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from nexus.engine.canonical import canonical_hash
from nexus.generator import generate_episode
from nexus.io import save_episode
from nexus.models.episode import PrivateEpisode
from nexus.models.rules import Effect
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import Session
from nexus.protocol.stdio import run_jsonl


@pytest.fixture
def episode():
    return generate_episode(42, verifier_secret="hardening-test")


@pytest.mark.parametrize("turn", [0.9, True, "0", None, -1])
def test_turn_identifiers_are_strict_and_consistent_across_transports(episode, turn):
    request = {"expected_turn": turn, "action": episode.reference_plan[0]}
    app = create_single_session_app(episode)
    with TestClient(app) as client:
        assert client.post("/action", json=request).status_code == 422
        assert client.get("/status").json()["turn"] == 0
    output = io.StringIO()
    run_jsonl(episode, io.StringIO(json.dumps(request) + "\n"), output)
    rows = [json.loads(line) for line in output.getvalue().splitlines()]
    assert rows[0]["observation"]["turn"] == 0
    assert rows[1]["ok"] is False
    session = Session(episode)
    from nexus.models.actions import ACTION_ADAPTER

    with pytest.raises(ValueError, match="nonnegative integer"):
        session.act(turn, ACTION_ADAPTER.validate_python(episode.reference_plan[0]))
    assert not session.trace and session.state.turn == 0


def test_missing_legacy_qualification_is_rejected_before_starting_session(episode):
    data = episode.model_dump(mode="json")
    del data["generation_metadata"]
    malformed = PrivateEpisode.model_validate(data)
    with pytest.raises(ValueError, match="qualified guaranteed-policy metadata"):
        Session(malformed)


@pytest.mark.parametrize("kind,parameter", [("add_mod", "amount"), ("multiply_mod", "multiplier")])
def test_arithmetic_rule_cannot_leave_declared_artifact_value_domain(kind, parameter):
    with pytest.raises(ValidationError, match="artifact domain"):
        Effect(kind=kind, field="value", modulus=100, **{parameter: 50})
    assert Effect(kind=kind, field="value", modulus=11, **{parameter: 50}).modulus == 11


@pytest.mark.parametrize(
    "filename",
    ["../../escaped.txt", "/tmp/escaped", "..\\escaped", "C:escape", "", "..", "bad\nname"],
)
def test_unsafe_attachment_name_rejected_before_output(episode, tmp_path, filename):
    episode.public.evidence_files[filename] = "must not escape"
    with pytest.raises(ValidationError, match="basenames"):
        save_episode(episode, tmp_path / "episode")
    assert list(tmp_path.iterdir()) == []


def test_existing_attachment_symlink_cannot_redirect_export(episode, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    directory = tmp_path / "episode"
    directory.mkdir()
    (directory / "attachments").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symlinks"):
        save_episode(episode, directory)
    assert list(outside.iterdir()) == []
    assert not (directory / "private.json").exists()


def test_legacy_public_identity_is_secret_backed_without_changing_world(episode):
    same = generate_episode(42, verifier_secret="hardening-test")
    other = generate_episode(42, verifier_secret="different-secret")
    assert episode.public.episode_id == same.public.episode_id
    assert episode.public.episode_id != other.public.episode_id
    assert canonical_hash(episode.public.initial_state) == canonical_hash(
        other.public.initial_state
    )
    meta = episode.generation_metadata
    known_family = meta.scenario_family_id
    public_id = episode.public.episode_id
    # All old public IDs were 16 hex characters; new IDs are HMAC-derived.
    assert len(public_id) == 32
    assert public_id != hashlib.sha256(known_family.encode()).hexdigest()[:16]


def test_private_episode_is_created_with_owner_only_permissions(tmp_path):
    import stat
    from nexus.generator import generate_episode
    from nexus.io import save_episode

    save_episode(generate_episode(17), tmp_path)
    assert stat.S_IMODE((tmp_path / 'private.json').stat().st_mode) == 0o600


def test_export_refuses_to_mix_evidence_with_an_existing_episode(episode, tmp_path):
    world = tmp_path / "world"
    save_episode(episode, world)
    stale = world / "attachments" / "old-reading.csv"
    stale.write_text("retained by operator")
    original = {p: p.read_bytes() for p in world.rglob("*") if p.is_file()}
    with pytest.raises(ValueError, match="empty directory"):
        save_episode(generate_episode(17), world)
    assert {p: p.read_bytes() for p in world.rglob("*") if p.is_file()} == original
