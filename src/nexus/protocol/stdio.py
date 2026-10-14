from __future__ import annotations

import json
from typing import TextIO

from nexus.models.actions import ACTION_ADAPTER
from nexus.models.episode import PrivateEpisode
from nexus.protocol.public_transcript import BOUNDARY, PublicTranscript
from nexus.protocol.session import Session


def run_jsonl(
    episode: PrivateEpisode,
    input_stream: TextIO,
    output_stream: TextIO,
    *,
    transcript: PublicTranscript | None = None,
) -> None:
    session = Session(episode)
    transcript = transcript if transcript is not None else session.public_transcript

    def emit(request, output, effects, *, sort_keys=False):
        try:
            output_stream.write(json.dumps(output, sort_keys=sort_keys) + "\n")
            output_stream.flush()
        except Exception:
            transcript.append(request, output, effects=effects, transport="stdio", complete=False)
            raise
        transcript.append(request, output, effects=effects, transport="stdio")

    effects: list[dict] = []
    token = BOUNDARY.set(effects)
    try:
        initial = {"observation": session.observe().model_dump(mode="json", exclude_none=True)}
    finally:
        BOUNDARY.reset(token)
    emit({"operation": "observe", "initial": True}, initial, effects)
    for line in input_stream:
        if not line.strip():
            continue
        effects = []
        token = BOUNDARY.set(effects)
        request = {"raw": line}
        try:
            request = json.loads(line)
            action = ACTION_ADAPTER.validate_python(request["action"])
            expected_turn = int(request.get("expected_turn", session.state.turn))
            response = session.act(expected_turn, action)
            output = response.model_dump(mode="json", exclude_none=True)
        except Exception as exc:  # noqa: BLE001 -- preserve the JSONL error contract
            output = {"ok": False, "error": str(exc)}
        finally:
            BOUNDARY.reset(token)
        emit(request, output, effects, sort_keys=True)
