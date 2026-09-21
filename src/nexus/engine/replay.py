from __future__ import annotations

from nexus.engine.canonical import canonical_hash
from nexus.engine.engine import step
from nexus.models.actions import Action
from nexus.models.episode import PrivateEpisode
from nexus.models.events import TraceRecord
from nexus.models.world import WorldState


def execute_with_trace(
    episode: PrivateEpisode, actions: list[Action], initial_state: WorldState | None = None
) -> tuple[WorldState, list[TraceRecord]]:
    state = (initial_state or episode.public.initial_state).model_copy(deep=True)
    records: list[TraceRecord] = []
    for action in actions:
        before_hash = canonical_hash(state)
        result = step(state, action, episode)
        if not result.ok:
            raise ValueError(f"invalid action during trace: {result.message}")
        after_hash = canonical_hash(result.state)
        records.append(
            TraceRecord(
                turn=result.state.turn,
                action=action,
                before_hash=before_hash,
                after_hash=after_hash,
                events=result.events,
                terminal_status=result.state.terminal_status,
                victory_code=result.victory_code,
            )
        )
        state = result.state
    return state, records


def replay(episode: PrivateEpisode, records: list[TraceRecord]) -> WorldState:
    state = episode.public.initial_state.model_copy(deep=True)
    for record in records:
        if canonical_hash(state) != record.before_hash:
            raise ValueError(f"replay before-hash mismatch at turn {record.turn}")
        result = step(state, record.action, episode)
        if not result.ok:
            raise ValueError(f"replay action failed at turn {record.turn}: {result.message}")
        if canonical_hash(result.state) != record.after_hash:
            raise ValueError(f"replay after-hash mismatch at turn {record.turn}")
        if result.state.terminal_status != record.terminal_status:
            raise ValueError(f"replay terminal-status mismatch at turn {record.turn}")
        if result.victory_code != record.victory_code:
            raise ValueError(f"replay victory-code mismatch at turn {record.turn}")
        state = result.state
    return state
