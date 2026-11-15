from __future__ import annotations

import json
from pathlib import Path
from typing import TextIO

from nexus.models.episode import PrivateEpisode
from nexus.protocol.requests import (
    SERVICE_REQUEST_ADAPTER, ActionClientRequest, ActionRequest, CheckClientRequest,
    EvidenceRequest, ManifestRequest, ObserveRequest, StatusRequest,
)
from nexus.protocol.public_transcript import BOUNDARY, PublicTranscript
from nexus.protocol.session import Session


def run_jsonl(
    episode: PrivateEpisode,
    input_stream: TextIO,
    output_stream: TextIO,
    *,
    transcript: PublicTranscript | None = None,
    audit_directory: Path | None = None,
) -> None:
    session = Session(episode)
    transcript = transcript if transcript is not None else session.public_transcript
    from nexus.protocol.audit import AuditRecorder

    recorder = AuditRecorder(session, audit_directory, transcript) if audit_directory else None
    try:
        _run_jsonl(session, input_stream, output_stream, transcript, recorder)
    finally:
        if recorder is not None:
            recorder.close()


def _handle(session, request):
    if not isinstance(request, dict) or "operation" not in request:
        # Original action-only envelope, including its optional turn.
        envelope = (
            {"expected_turn": session.state.turn, **request} if isinstance(request, dict) else request
        )
        action = ActionRequest.model_validate(envelope)
        response = session.act(action.expected_turn, action.action, player_only=True)
        return response.model_dump(mode="json", exclude_none=True)

    op = SERVICE_REQUEST_ADAPTER.validate_python(request)
    if isinstance(op, ManifestRequest):
        return session.manifest().model_dump(mode="json")
    if isinstance(op, EvidenceRequest):
        return {"filename": op.filename, "content": session.evidence(op.filename)}
    if isinstance(op, ObserveRequest):
        return session.observe().model_dump(mode="json", exclude_none=True)
    if isinstance(op, StatusRequest):
        return session.status().model_dump(mode="json")
    if isinstance(op, CheckClientRequest):
        return session.check_construction(op.build).model_dump(mode="json")
    if isinstance(op, ActionClientRequest):
        turn = op.expected_turn if op.expected_turn is not None else session.state.turn
        return session.act(turn, op.action, player_only=True).model_dump(mode="json", exclude_none=True)
    raise ValueError("unsupported player operation")


def _run_jsonl(session, input_stream, output_stream, transcript, recorder):

    def emit(request, output, effects, *, sort_keys=False):
        try:
            output_stream.write(json.dumps(output, sort_keys=sort_keys) + "\n")
            output_stream.flush()
        except Exception:
            transcript.append(request, output, effects=effects, transport="stdio", complete=False)
            raise
        transcript.append(request, output, effects=effects, transport="stdio")
        if recorder is not None:
            recorder.checkpoint_safely()

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
            output = _handle(session, request)
        except Exception as exc:  # noqa: BLE001 -- preserve the JSONL error contract
            output = {"ok": False, "error": str(exc)}
        finally:
            BOUNDARY.reset(token)
        emit(request, output, effects, sort_keys=True)
