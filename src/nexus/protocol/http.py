from __future__ import annotations

from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, ConfigDict

from nexus.models.actions import Action
from nexus.models.episode import PlayerManifest, PrivateEpisode
from nexus.protocol.session import Session


class ActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_turn: int
    action: Action


class SessionStore:
    def __init__(self, episode: PrivateEpisode):
        self.episode = episode
        self.sessions: dict[str, Session] = {}
        self._lock = Lock()

    def create(self) -> tuple[str, Session]:
        with self._lock:
            session_id = uuid4().hex
            session = Session(self.episode)
            self.sessions[session_id] = session
            return session_id, session

    def get(self, session_id: str) -> Session:
        try:
            return self.sessions[session_id]
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="session not found") from exc


def _player_manifest(episode: PrivateEpisode) -> dict:
    return PlayerManifest.from_episode(episode.public).model_dump(mode="json")


def _evidence(episode: PrivateEpisode, filename: str) -> str:
    try:
        return episode.public.evidence_files[filename]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="evidence file not found") from exc


def _health(episode: PrivateEpisode) -> dict[str, str]:
    return {"status": "ok", "episode_id": episode.public.episode_id}


def create_app(episode: PrivateEpisode) -> FastAPI:
    """Create the general multi-session HTTP application."""
    app = FastAPI(title="NEXUS", version=episode.public.protocol_version)
    store = SessionStore(episode)

    @app.get("/health")
    def health():
        return _health(store.episode)

    @app.get("/manifest")
    def manifest():
        return _player_manifest(store.episode)

    @app.get("/evidence/{filename}", response_class=PlainTextResponse)
    def evidence(filename: str):
        return _evidence(store.episode, filename)

    @app.post("/sessions")
    def create_session():
        session_id, session = store.create()
        return {
            "session_id": session_id,
            "manifest": _player_manifest(store.episode),
            "observation": session.observe().model_dump(mode="json", exclude_none=True),
        }

    @app.get("/sessions/{session_id}/observe")
    def observe_session(session_id: str):
        return store.get(session_id).observe().model_dump(mode="json", exclude_none=True)

    @app.post("/sessions/{session_id}/actions")
    def act(session_id: str, request: ActionRequest):
        return (
            store.get(session_id)
            .act(request.expected_turn, request.action)
            .model_dump(mode="json", exclude_none=True)
        )

    @app.get("/sessions/{session_id}/status")
    def status(session_id: str):
        return store.get(session_id).status().model_dump(mode="json")

    @app.get("/sessions/{session_id}/events")
    def events(session_id: str):
        return [record.model_dump(mode="json") for record in store.get(session_id).trace_snapshot()]

    return app


def create_single_session_app(episode: PrivateEpisode) -> FastAPI:
    """Create an HTTP application that owns exactly one non-resettable session."""
    app = FastAPI(title="NEXUS", version=episode.public.protocol_version)
    session = Session(episode)

    @app.get("/health")
    def health():
        return _health(episode)

    @app.get("/manifest")
    def manifest():
        return _player_manifest(episode)

    @app.get("/evidence/{filename}", response_class=PlainTextResponse)
    def evidence(filename: str):
        return _evidence(episode, filename)

    @app.get("/observe")
    def observe():
        return session.observe().model_dump(mode="json", exclude_none=True)

    @app.post("/action")
    def act(request: ActionRequest):
        return session.act(request.expected_turn, request.action).model_dump(mode="json", exclude_none=True)

    @app.get("/status")
    def status():
        return session.status().model_dump(mode="json")

    @app.get("/events")
    def events():
        return [record.model_dump(mode="json") for record in session.trace_snapshot()]

    return app
