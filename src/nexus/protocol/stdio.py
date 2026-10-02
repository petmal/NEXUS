from __future__ import annotations

import json
from typing import TextIO

from nexus.models.actions import ACTION_ADAPTER
from nexus.models.episode import PrivateEpisode
from nexus.protocol.session import Session


def run_jsonl(episode: PrivateEpisode, input_stream: TextIO, output_stream: TextIO) -> None:
    session = Session(episode)
    output_stream.write(json.dumps({"observation": session.observe().model_dump(mode="json", exclude_none=True)}) + "\n")
    output_stream.flush()
    for line in input_stream:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            action = ACTION_ADAPTER.validate_python(request["action"])
            expected_turn = int(request.get("expected_turn", session.state.turn))
            response = session.act(expected_turn, action)
            output = response.model_dump(mode="json", exclude_none=True)
        except Exception as exc:
            output = {"ok": False, "error": str(exc)}
        output_stream.write(json.dumps(output, sort_keys=True) + "\n")
        output_stream.flush()
