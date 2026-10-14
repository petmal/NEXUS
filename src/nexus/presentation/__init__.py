"""Versioned public presentation, independent of scientific truth and execution.

Canonical evidence stays unchanged for ontology validation and historical replay.
Every player-facing reader projects it here. Text must not depend on selected laws,
qualification metadata or hidden state.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from nexus.models.episode import PrivateEpisode, PublicEpisode

type PresentationVersion = Literal["sealed-facility-v1"]
CURRENT: PresentationVersion = "sealed-facility-v1"
PREMISE = (
    "You are confined inside NEXUS, a sealed artificial facility. Its apparatus acts "
    "on artifacts and specimens according to consistent local laws. The exit seal "
    "opens only when the exact mission condition below is satisfied and finish "
    "returns a victory receipt. Investigate the supplied records, use observations "
    "to test your explanations, and produce the required concrete state."
)
GLOSSARY = (
    "FACILITY RECORD\n"
    "Rooms are sectors of the enclosure; use their exact identifiers for movement. "
    "Apparatus and artifact identifiers, settings, measurements, and goal fields "
    "retain the exact meanings in the action contract and records below. "
    "A turn records a committed action. The phase is a separate facility register; "
    "its changes follow the public contract, not elapsed wall time. "
    "A null allowance means unlimited; finite allowances are binding. "
    "The seal evaluates the stated goal only when you invoke finish. "
    "No narrative term introduces an additional action or hidden requirement.\n\n"
)


def attach(
    episode: PrivateEpisode, version: PresentationVersion | None = CURRENT
) -> PrivateEpisode:
    if version not in (None, CURRENT):
        raise ValueError("unsupported presentation version")
    if episode.public.presentation_version == version:
        return episode
    return episode.model_copy(
        update={"public": episode.public.model_copy(update={"presentation_version": version})}
    )


def description(public: PublicEpisode) -> str:
    return (
        f"{PREMISE}\n\nMISSION\n{public.description}"
        if public.presentation_version
        else public.description
    )


def room_label(public: PublicEpisode, room_id: str) -> str:
    # No role inference: it could reveal an unobserved machine or mission dependency.
    return f"Sector {room_id}" if public.presentation_version else public.rooms[room_id].label


def evidence(public: PublicEpisode, filename: str) -> str:
    content = public.evidence_files[filename]
    if not public.presentation_version:
        return content
    if filename in ("manual.txt", "manual.md"):
        return GLOSSARY + content
    if filename == "map.json":
        # Change labels only where the original public map already discloses rooms.
        data = json.loads(content)
        rooms = data.get("rooms")
        if isinstance(rooms, dict):
            data["sector_functions"] = dict(rooms)
            for room_id, value in rooms.items():
                if room_id in public.rooms:
                    if isinstance(value, str):
                        rooms[room_id] = room_label(public, room_id)
                    elif isinstance(value, dict) and "label" in value:
                        value["label"] = room_label(public, room_id)
        return json.dumps(data, indent=2) + "\n"
    return content


def evidence_files(public: PublicEpisode) -> dict[str, str]:
    return {filename: evidence(public, filename) for filename in public.evidence_files}
