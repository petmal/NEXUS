from __future__ import annotations

from collections import deque
from collections.abc import Iterable

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
from nexus.models.goals import GoalKind, GoalPredicate
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


SearchStateKey = tuple[object, ...]


def search_state_key(state: WorldState) -> SearchStateKey:
    """Return the immutable semantic search state, excluding path-cost-only fields.

    `turn` and `actions_remaining` are deliberately omitted because BFS/minimax depth already
    dominates them. Replay integrity continues to use canonical SHA-256 hashes separately.
    """
    artifacts = tuple(
        (
            artifact_id,
            artifact.location,
            artifact.shape.value,
            artifact.pattern.value,
            artifact.orientation.value,
            artifact.value,
            artifact.polarity.value,
        )
        for artifact_id, artifact in sorted(state.artifacts.items())
    )
    machines = tuple(
        (machine_id, machine.room_id, machine.uses_remaining)
        for machine_id, machine in sorted(state.machines.items())
    )
    return (
        state.phase,
        state.agent_room,
        artifacts,
        machines,
        state.terminal_status.value,
    )


def neighbors(episode: PrivateEpisode, room_id: str) -> list[str]:
    result: list[str] = []
    for left, right in episode.public.edges:
        if left == room_id:
            result.append(right)
        elif right == room_id:
            result.append(left)
    return sorted(result)


def goal_artifact_ids(goal: GoalPredicate) -> set[str]:
    """Collect artifacts that can affect the declarative goal.

    Artifact-local transitions cannot make progress through an artifact that the goal never
    references. The traversal is conservative across composite/negated predicates.
    """
    result: set[str] = set()

    def visit(predicate: GoalPredicate) -> None:
        if predicate.artifact_id is not None:
            result.add(predicate.artifact_id)
        for child in predicate.children:
            visit(child)

    visit(goal)
    return result



def goal_field_artifact_ids(goal: GoalPredicate) -> set[str]:
    """Collect artifacts whose intrinsic fields can affect the declarative goal.

    Machine operations only change intrinsic artifact fields, never artifact location. Therefore
    operating an artifact referenced solely by location predicates is dominated and can be
    excluded from physical-policy search without changing solvability or optimal cost.
    """
    result: set[str] = set()

    def visit(predicate: GoalPredicate) -> None:
        if (
            predicate.kind == GoalKind.ARTIFACT_FIELD
            and predicate.artifact_id is not None
        ):
            result.add(predicate.artifact_id)
        for child in predicate.children:
            visit(child)

    visit(goal)
    return result


def goal_location_rooms(goal: GoalPredicate, rooms: Iterable[str]) -> dict[str, set[str]]:
    """Collect rooms that can satisfy an explicit artifact-location goal.

    With unlimited inventory and the current mechanics, dropping an artifact anywhere else is
    dominated: movement has no carrying cost and probe/operate both require the artifact to be
    carried. A negated location predicate can instead require dropping in an
    unnamed room (in particular NOT in inventory). Retain all rooms under odd
    negation, including through AND/OR; double negation restores positive polarity.
    """
    result: dict[str, set[str]] = {}
    all_rooms = set(rooms)

    def visit(predicate: GoalPredicate, negated: bool = False) -> None:
        if (
            predicate.kind == GoalKind.ARTIFACT_LOCATION
            and predicate.artifact_id is not None
            and isinstance(predicate.value, str)
        ):
            result.setdefault(predicate.artifact_id, set()).update(
                all_rooms if negated else {predicate.value} & all_rooms
            )
        for child in predicate.children:
            visit(child, negated != (predicate.kind == GoalKind.NOT))

    visit(goal)
    return result


def legal_solver_actions(episode: PrivateEpisode, state: WorldState) -> list[Action]:
    if state.terminal_status != TerminalStatus.ACTIVE or state.resources.actions_remaining == 0:
        return []

    actions: list[Action] = [FinishAction()]
    actions.extend(MoveAction(target=room) for room in neighbors(episode, state.agent_room))

    goal_rooms = goal_location_rooms(episode.public.goal, episode.public.rooms)
    for artifact in sorted(state.artifacts.values(), key=lambda a: a.id):
        if artifact.location == state.agent_room:
            actions.append(TakeAction(artifact=artifact.id))
        elif (
            artifact.location == INVENTORY
            and state.agent_room in goal_rooms.get(artifact.id, set())
        ):
            actions.append(DropAction(artifact=artifact.id))

    carried = sorted((a.id for a in state.carried_artifacts()))
    goal_artifacts = goal_field_artifact_ids(episode.public.goal)
    for machine in sorted(state.machines.values(), key=lambda m: m.id):
        if machine.room_id == state.agent_room and machine.uses_remaining != 0:
            for artifact_id in carried:
                if artifact_id in goal_artifacts:
                    actions.append(OperateAction(machine=machine.id, artifact=artifact_id))

    if episode.public.phase_modulus > 1:
        actions.append(WaitAction())
    return actions


def solve(episode: PrivateEpisode, max_states: int = 100_000) -> SolveResult:
    if episode.public.investigation is not None:
        # Trusted perfect-knowledge physical optimum. Scientific policy is stored separately.
        from nexus.engine.replay import execute_with_trace
        from nexus.ontology.catalog import runtime_for
        plan = runtime_for(episode.public.investigation).physical_plan(episode)
        state, _ = execute_with_trace(episode, list(plan))
        return SolveResult(solvable=state.terminal_status == TerminalStatus.WON,
                           optimal_action_count=len(plan), plan=plan,
                           terminal_state_hash=canonical_hash(state))
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
