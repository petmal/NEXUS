from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from nexus.engine.canonical import canonical_hash
from nexus.engine.engine import step
from nexus.models.actions import Action
from nexus.models.episode import PrivateEpisode
from nexus.models.events import TraceRecord
from nexus.models.observation import Observation
from nexus.models.world import WorldState
from nexus.render.text import observation


class ActionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    expected_turn: int
    current_turn: int
    observation: Observation
    events: tuple[dict, ...] = ()
    message: str = ""
    victory_code: str | None = None
    duplicate: bool = False


class Session:
    def __init__(self, episode: PrivateEpisode):
        self.episode = episode
        self.state: WorldState = episode.public.initial_state.model_copy(deep=True)
        self.trace: list[TraceRecord] = []
        self._turn_cache: dict[int, ActionResponse] = {}

    def observe(self) -> Observation:
        return observation(self.episode.public, self.state)

    def act(self, expected_turn: int, action: Action) -> ActionResponse:
        cached = self._turn_cache.get(expected_turn)
        if cached is not None:
            return cached.model_copy(update={"duplicate": True})
        if expected_turn != self.state.turn:
            return ActionResponse(
                ok=False,
                expected_turn=expected_turn,
                current_turn=self.state.turn,
                observation=self.observe(),
                message=f"turn mismatch: expected {expected_turn}, current {self.state.turn}",
            )

        before_hash = canonical_hash(self.state)
        result = step(self.state, action, self.episode)
        if not result.ok:
            return ActionResponse(
                ok=False,
                expected_turn=expected_turn,
                current_turn=self.state.turn,
                observation=self.observe(),
                message=result.message,
            )

        previous_turn = self.state.turn
        self.state = result.state
        response = ActionResponse(
            ok=True,
            expected_turn=expected_turn,
            current_turn=self.state.turn,
            observation=self.observe(),
            events=tuple(event.model_dump(mode="json") for event in result.events),
            message=result.message,
            victory_code=result.victory_code,
        )
        if self.state.turn != previous_turn:
            record = TraceRecord(
                turn=self.state.turn,
                action=action,
                before_hash=before_hash,
                after_hash=canonical_hash(self.state),
                events=result.events,
                terminal_status=self.state.terminal_status,
                victory_code=result.victory_code,
            )
            self.trace.append(record)
            self._turn_cache[expected_turn] = response
        return response
