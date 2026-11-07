from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from nexus.models.episode import PlayerManifest, PrivateEpisode, PublicEpisode
from nexus.models.events import TraceRecord
from nexus.presentation import evidence_files


def load_private(path: Path) -> PrivateEpisode:
    return PrivateEpisode.model_validate_json(path.read_text(encoding="utf-8"))


def load_public(path: Path) -> PublicEpisode:
    """Load trusted non-secret compiled episode data.

    This is not the player-facing manifest.
    """
    return PublicEpisode.model_validate_json(path.read_text(encoding="utf-8"))


class EpisodeDestinationError(ValueError):
    """The requested output cannot safely hold a fresh episode."""


def check_episode_destination(directory: Path) -> None:
    if directory.is_symlink() or (
        directory.exists() and (not directory.is_dir() or any(directory.iterdir()))
    ):
        raise EpisodeDestinationError(
            f"{directory}: choose a new or empty directory; existing files and symlinks are not replaced"
        )


def save_episode(episode: PrivateEpisode, directory: Path) -> None:
    # model_copy/update or direct mutation can bypass model validators.
    episode = PrivateEpisode.model_validate(episode.model_dump(mode="python"))
    check_episode_destination(directory)
    directory.mkdir(parents=True, exist_ok=True)
    attachments = directory / "attachments"
    # Claim this export before writing anything. Concurrent NEXUS writers must
    # never combine one private episode with another world's evidence.
    attachments.mkdir()
    manifest = PlayerManifest.from_episode(episode.public)
    (directory / "manifest.json").write_text(
        manifest.model_dump_json(indent=2), encoding="utf-8"
    )
    # Create with owner-only permissions, then replace atomically. Writing a
    # default-permission file and chmod-ing later would expose a short window.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(episode.model_dump_json(indent=2))
        os.replace(temporary, directory / "private.json")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)

    for filename, content in evidence_files(episode.public).items():
        (attachments / filename).write_text(content, encoding="utf-8")


def save_trace(records: list[TraceRecord], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(record.model_dump_json() + "\n")


def load_trace(path: Path) -> list[TraceRecord]:
    records: list[TraceRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(TraceRecord.model_validate(json.loads(line)))
    return records
