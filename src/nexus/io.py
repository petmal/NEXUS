from __future__ import annotations

import json
from pathlib import Path

from nexus.models.episode import PlayerManifest, PrivateEpisode, PublicEpisode
from nexus.models.events import TraceRecord


def load_private(path: Path) -> PrivateEpisode:
    return PrivateEpisode.model_validate_json(path.read_text(encoding="utf-8"))


def load_public(path: Path) -> PublicEpisode:
    """Load trusted non-secret compiled episode data.

    This is not the player-facing manifest.
    """
    return PublicEpisode.model_validate_json(path.read_text(encoding="utf-8"))


def save_episode(episode: PrivateEpisode, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)

    manifest = PlayerManifest.from_episode(episode.public)
    (directory / "manifest.json").write_text(
        manifest.model_dump_json(indent=2), encoding="utf-8"
    )
    (directory / "private.json").write_text(
        episode.model_dump_json(indent=2), encoding="utf-8"
    )

    attachments = directory / "attachments"
    attachments.mkdir(exist_ok=True)
    for filename, content in episode.public.evidence_files.items():
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
