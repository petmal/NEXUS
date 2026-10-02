from __future__ import annotations

from nexus.models.episode import PublicEpisode
from nexus.models.observation import Observation
from nexus.models.world import INVENTORY, WorldState


def _neighbors(episode: PublicEpisode, room_id: str) -> tuple[str, ...]:
    result: set[str] = set()
    for left, right in episode.edges:
        if left == room_id:
            result.add(right)
        elif right == room_id:
            result.add(left)
    return tuple(sorted(result))


def observation(episode: PublicEpisode, state: WorldState) -> Observation:
    room_id = state.agent_room
    visible_artifacts = tuple(
        sorted(
            (a.model_copy(deep=True) for a in state.artifacts.values() if a.location == room_id),
            key=lambda a: a.id,
        )
    )
    carried = tuple(
        sorted(
            (a.model_copy(deep=True) for a in state.artifacts.values() if a.location == INVENTORY),
            key=lambda a: a.id,
        )
    )
    machines = tuple(
        sorted(
            (m.model_copy(deep=True) for m in state.machines.values() if m.room_id == room_id),
            key=lambda m: m.id,
        )
    )
    include_static_context = episode.protocol_version == "nexus-0.1"
    return Observation(
        episode_id=episode.episode_id,
        turn=state.turn,
        room=room_id,
        room_label=episode.rooms[room_id].label,
        exits=_neighbors(episode, room_id),
        phase=state.phase,
        actions_remaining=state.resources.actions_remaining,
        visible_artifacts=visible_artifacts,
        carried_artifacts=carried,
        visible_machines=machines,
        terminal_status=state.terminal_status,
        goal=episode.goal.model_dump(mode="json") if include_static_context else None,
        evidence_files=(
            tuple(sorted(episode.evidence_files)) if include_static_context else None
        ),
    )
