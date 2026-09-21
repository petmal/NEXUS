from __future__ import annotations

from collections import deque

from pydantic import BaseModel, ConfigDict

from nexus.engine.canonical import canonical_hash
from nexus.engine.engine import step
from nexus.models.actions import (
    Action,
    DropAction,
    FinishAction,
    MoveAction,
    OperateAction,
    TakeAction,
    WaitAction,
)
from nexus.models.episode import PrivateEpisode
from nexus.models.world import INVENTORY, TerminalStatus, WorldState


class SolveResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    solvable: bool
    optimal_action_count: int | None = None
    plan: tuple[Action, ...] = ()
    visited_states: int = 0
    max_frontier_size: int = 0
    terminal_state_hash: str | None = None
    exhausted_state_limit: bool = False


def search_state_key(state: WorldState) -> str:
    """Hash semantic state while dropping path-cost fields dominated by BFS depth."""
    payload = state.model_dump(mode="json")
    payload.pop("turn", None)
    resources = payload.get("resources", {})
    resources.pop("actions_remaining", None)
    return canonical_hash(payload)


def neighbors(episode: PrivateEpisode, room_id: str) -> list[str]:
    result: list[str] = []
    for left, right in episode.public.edges:
        if left == room_id:
            result.append(right)
        elif right == room_id:
            result.append(left)
    return sorted(result)


def legal_solver_actions(episode: PrivateEpisode, state: WorldState) -> list[Action]:
    if state.terminal_status != TerminalStatus.ACTIVE or state.resources.actions_remaining <= 0:
        return []

    actions: list[Action] = [FinishAction()]
    actions.extend(MoveAction(target=room) for room in neighbors(episode, state.agent_room))

    for artifact in sorted(state.artifacts.values(), key=lambda a: a.id):
        if artifact.location == state.agent_room:
            actions.append(TakeAction(artifact=artifact.id))
        elif artifact.location == INVENTORY:
            actions.append(DropAction(artifact=artifact.id))

    carried = sorted((a.id for a in state.carried_artifacts()))
    for machine in sorted(state.machines.values(), key=lambda m: m.id):
        if machine.room_id == state.agent_room and machine.uses_remaining > 0:
            for artifact_id in carried:
                actions.append(OperateAction(machine=machine.id, artifact=artifact_id))

    if episode.public.phase_modulus > 1:
        actions.append(WaitAction())
    return actions


def solve(episode: PrivateEpisode, max_states: int = 100_000) -> SolveResult:
    initial = episode.public.initial_state.model_copy(deep=True)
    frontier: deque[tuple[WorldState, tuple[Action, ...]]] = deque([(initial, ())])
    visited = {search_state_key(initial)}
    max_frontier = 1

    while frontier:
        state, plan = frontier.popleft()
        if len(visited) >= max_states:
            return SolveResult(
                solvable=False,
                visited_states=len(visited),
                max_frontier_size=max_frontier,
                exhausted_state_limit=True,
            )

        for action in legal_solver_actions(episode, state):
            result = step(state, action, episode)
            if not result.ok:
                continue
            next_plan = plan + (action,)
            if result.state.terminal_status == TerminalStatus.WON:
                return SolveResult(
                    solvable=True,
                    optimal_action_count=len(next_plan),
                    plan=next_plan,
                    visited_states=len(visited),
                    max_frontier_size=max_frontier,
                    terminal_state_hash=canonical_hash(result.state),
                )
            if result.state.terminal_status != TerminalStatus.ACTIVE:
                continue
            key = search_state_key(result.state)
            if key in visited:
                continue
            visited.add(key)
            frontier.append((result.state, next_plan))
        max_frontier = max(max_frontier, len(frontier))

    return SolveResult(
        solvable=False,
        visited_states=len(visited),
        max_frontier_size=max_frontier,
    )
