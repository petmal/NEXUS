"""Behavioral regression contracts."""

import pytest
from pydantic import ValidationError

from nexus.generator import generate_episode
from nexus.io import save_episode


@pytest.mark.parametrize(
    "filename",
    ["../../escaped.txt", "/tmp/escaped", "..\\escaped", "C:escape", "", "..", "bad\nname"],
)
def test_unsafe_attachment_name_rejected_before_output(hardened_episode, tmp_path, filename):
    hardened_episode.public.evidence_files[filename] = "must not escape"
    with pytest.raises(ValidationError, match="basenames"):
        save_episode(hardened_episode, tmp_path / "episode")
    assert list(tmp_path.iterdir()) == []


def test_existing_attachment_symlink_cannot_redirect_export(hardened_episode, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    directory = tmp_path / "episode"
    directory.mkdir()
    (directory / "attachments").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symlinks"):
        save_episode(hardened_episode, directory)
    assert list(outside.iterdir()) == []
    assert not (directory / "private.json").exists()


def test_private_episode_is_created_with_owner_only_permissions(tmp_path):
    import stat

    from nexus.generator import generate_episode
    from nexus.io import save_episode

    save_episode(generate_episode(17), tmp_path)
    assert stat.S_IMODE((tmp_path / 'private.json').stat().st_mode) == 0o600


def test_export_refuses_to_mix_evidence_with_an_existing_episode(hardened_episode, tmp_path):
    world = tmp_path / "world"
    save_episode(hardened_episode, world)
    stale = world / "attachments" / "old-reading.csv"
    stale.write_text("retained by operator")
    original = {p: p.read_bytes() for p in world.rglob("*") if p.is_file()}
    with pytest.raises(ValueError, match="empty directory"):
        save_episode(generate_episode(17), world)
    assert {p: p.read_bytes() for p in world.rglob("*") if p.is_file()} == original
