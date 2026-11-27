"""Versioned public presentation, independent of scientific truth and execution.

Canonical evidence stays unchanged for ontology validation and historical replay.
Every player-facing reader projects it here. Text must not depend on selected laws,
qualification metadata or hidden state.
"""

from __future__ import annotations

import json
from copy import deepcopy
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from nexus.models.episode import PrivateEpisode, PublicEpisode

type PresentationVersion = Literal["sealed-facility-v1", "sealed-facility-v2", "sealed-facility-v3", "sealed-facility-v4", "sealed-facility-v5", "sealed-facility-v6", "sealed-facility-v7"]
SUPPORTED: tuple[PresentationVersion, ...] = ("sealed-facility-v1", "sealed-facility-v2", "sealed-facility-v3", "sealed-facility-v4", "sealed-facility-v5", "sealed-facility-v6", "sealed-facility-v7")
ORIENTATION_VERSIONS = SUPPORTED[1:]
CONSOLE_VERSIONS = SUPPORTED[2:]
LABORATORY_VERSIONS = SUPPORTED[3:]
DEVICE_VERSIONS = SUPPORTED[4:]
ROLE_VERSIONS = SUPPORTED[5:]
CURRENT: PresentationVersion = "sealed-facility-v7"
# Keep v1 text byte-for-byte stable for saved episodes and historical comparisons.
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
PREMISE_V2 = (
    "You are inside NEXUS, a sealed artificial facility of unknown origin. A translated "
    "console is your link to its machinery. The exit interlock is closed; the console "
    "offers clearance when you complete the mission below. Use the supplied records "
    "and apparatus to meet its exact requirements. Some records supply the laws or a "
    "design; others leave questions to investigate. A successful finish returns a "
    "victory receipt: clearance is granted and your visit ends. No further escape "
    "action is needed."
)
GLOSSARY_V2 = """CONSOLE ORIENTATION
The console translates local names into readable labels. They describe this
world's devices, not familiar physics or a word puzzle. The local records define
their exact behavior; a name alone is not a clue to an unknown law.

Sector means room; apparatus means machine or instrument. Always copy the exact
IDs shown by the interface. An artifact is an object you can manipulate; a specimen
is an object used for experiments. Stock supplies specimens under the stated rules.
An array is a work area or group of apparatus; a lattice is a system of connected
elements. Neither name adds a route, device or action beyond those listed.

The exit seal is the interlock that grants clearance. An object named seal or
seal-i is a portable mission part, not the door itself. A carrier holds a constructed
device. A cartridge is a programmed component; a compensator supplies the correction
required by its mission. Use the mission's named objects and acceptance conditions.

A register stores a state value. An excitation is an input setting; a residual is
the mismatch defined by the local records. Phase, charge, orientation and pulse
also have their stated local meanings, not assumed real-world effects.

The action allowance is the console's authorization budget, not an oxygen supply
or a real-time countdown. Reading and thinking do not spend it. Accepted actions
follow the stated costs; an unchanged result can still cost an action. A null
allowance means unlimited. Device-use and stock limits are separate. Phase changes
follow the action contract, not elapsed time. Follow the world's stated finish
policy: a rejection may leave another attempt possible or end the session.
Only a successful finish grants clearance. An ended attempt without a receipt
leaves the exit closed; there is no additional story requirement or penalty.

LOCAL RECORD
"""
REVISION_BRIEF_V2 = (
    "The exit's routing system needs a replacement cartridge. The supplied records "
    "define the transfer elements and state which construction details are known. "
    "Install a cartridge that meets the complete behavior requirement in theory.json. "
    "Read apparatus.txt for its controls."
)
# Fixed edits to public prose only: distinguish carried parts from the exit lock.
# Do not apply these to structured records, IDs, controls or historical wording.
PORTABLE_SEAL_TERMS_V2 = (
    ("carried exit seal", "carried seal component"),
    ("An exit seal must cancel", "A portable seal component must cancel"),
    ("construct an exit seal", "construct a seal component"),
    ("three exit seals", "three seal components"),
    ("Three exit seals", "Three seal components"),
)


def _prose_v2(text: str) -> str:
    for original, replacement in PORTABLE_SEAL_TERMS_V2:
        text = text.replace(original, replacement)
    return text


def attach(
    episode: PrivateEpisode, version: PresentationVersion | None = CURRENT
) -> PrivateEpisode:
    if version not in (None, *SUPPORTED):
        raise ValueError("unsupported presentation version")
    if episode.public.presentation_version == version:
        return episode
    return episode.model_copy(
        update={"public": episode.public.model_copy(update={"presentation_version": version})}
    )


def description(public: PublicEpisode) -> str:
    if public.presentation_version in DEVICE_VERSIONS:
        from nexus.presentation.laboratory_v5 import brief
        if task := brief(public):
            return f"{PREMISE_V2}\n\nYOUR TASK\n{task}"
    if public.presentation_version in ORIENTATION_VERSIONS:
        return f"{PREMISE_V2}\n\nMISSION\n{_prose_v2(public.description)}"
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
    if public.presentation_version in CONSOLE_VERSIONS:
        from nexus.presentation.console import local_record
        content = local_record(public, filename, content)
    if public.presentation_version in LABORATORY_VERSIONS:
        from nexus.presentation.laboratory_v4 import record
        content = record(public, filename, content)
    if public.presentation_version in DEVICE_VERSIONS:
        from nexus.presentation.laboratory_v5 import record
        content = record(public, filename, content)
    if public.presentation_version in ROLE_VERSIONS and filename != "facility.txt":
        from nexus.presentation.laboratory_v6 import record
        content = record(public, filename, content)
    if public.presentation_version == "sealed-facility-v7":
        from nexus.presentation.survey_instructions import record
        content = record(public, filename, content)
    if not public.presentation_version:
        return content
    if public.presentation_version in ORIENTATION_VERSIONS:
        if filename == "facility.txt":
            # Family identity is public; never branch on the selected hidden construction.
            if getattr(public.investigation, "ontology", None) == "model-revision-v1":
                content = REVISION_BRIEF_V2
            content = GLOSSARY_V2 + _prose_v2(content)
            if public.presentation_version in ROLE_VERSIONS:
                from nexus.presentation.laboratory_v6 import record
                content = record(public, filename, content)
            return content
        if filename in ("manual.txt", "manual.md", "facility_manual.txt"):
            return GLOSSARY_V2 + _prose_v2(content)
    if filename in ("manual.txt", "manual.md"):
        return GLOSSARY + content
    if filename == "map.json":
        # Change labels only where the original public map already discloses rooms.
        data = json.loads(content)
        rooms = data.get("rooms")
        if isinstance(rooms, dict):
            data["sector_functions"] = (
                deepcopy(rooms) if public.presentation_version in ORIENTATION_VERSIONS
                else dict(rooms)
            )
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


def evidence_binding(public: PublicEpisode) -> dict[str, str | None]:
    """Identify the compiled source and the exact filename-to-text map delivered to players."""
    from nexus.engine.canonical import canonical_hash

    return {
        "evidence_binding_version": "presented-evidence-v1",
        "presentation_version": public.presentation_version,
        "compiled_evidence_sha256": canonical_hash(public.evidence_files),
        "public_evidence_sha256": canonical_hash(evidence_files(public)),
    }


def public_input_binding(public: PublicEpisode) -> dict[str, str | None]:
    """Instance-specific identity; the player manifest includes its episode ID."""
    from nexus.engine.canonical import canonical_hash
    from nexus.models.episode import PlayerManifest

    return {
        **evidence_binding(public),
        "player_manifest_sha256": canonical_hash(PlayerManifest.from_episode(public)),
    }
