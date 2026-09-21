from __future__ import annotations

from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

from nexus.models.actions import Action
from nexus.models.episode import PrivateEpisode
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


def create_app(episode: PrivateEpisode) -> FastAPI:
    app = FastAPI(title="NEXUS", version=episode.public.protocol_version)
    store = SessionStore(episode)

    @app.post("/sessions")
    def create_session():
        session_id, session = store.create()
        return {"session_id": session_id, "observation": session.observe().model_dump(mode="json")}

    @app.get("/sessions/{session_id}/observe")
    def observe_session(session_id: str):
        return store.get(session_id).observe().model_dump(mode="json")

    @app.post("/sessions/{session_id}/actions")
    def act(session_id: str, request: ActionRequest):
        return store.get(session_id).act(request.expected_turn, request.action).model_dump(mode="json")

    @app.get("/sessions/{session_id}/status")
    def status(session_id: str):
        session = store.get(session_id)
        return {
            "turn": session.state.turn,
            "status": session.state.terminal_status.value,
            "actions_remaining": session.state.resources.actions_remaining,
        }

    @app.get("/sessions/{session_id}/events")
    def events(session_id: str):
        return [record.model_dump(mode="json") for record in store.get(session_id).trace]

    return app
