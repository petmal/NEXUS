from __future__ import annotations

from collections import Counter
from threading import RLock

from pydantic import BaseModel, ConfigDict, Field

from nexus.engine.canonical import canonical_hash
from nexus.engine.engine import step
from nexus.engine.goals import evaluate_goal
from nexus.models.actions import Action, FinishAction, MoveAction, ProbeAction
from nexus.models.episode import PrivateEpisode
from nexus.models.events import TraceRecord
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.observation import Observation
from nexus.models.world import TerminalStatus, WorldState
from nexus.render.text import observation


PERFORMANCE_SCHEMA_URL = (
    "https://raw.githubusercontent.com/petmal/NEXUS/"
    "49603fa023a9d38bd85c08b112c8f2f4ce1e051c/schemas/performance-v2.schema.json"
)


class PerformanceSummary(BaseModel):
    """Terminal-only evaluation telemetry derived from trusted episode data and the live trace."""

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    schema_url: str = Field(default=PERFORMANCE_SCHEMA_URL, alias="$schema")
    discovery_level: int
    planning_level: int
    resource_pressure: int
    terminal_status: TerminalStatus
    initial_action_budget: int
    resource_allowance: int
    planning_dependency_action_cost: int
    actions_used: int
    optimal_physical_actions: int
    minimum_guaranteed_probes: int
    guaranteed_policy_actions: int
    action_delta_from_guaranteed_policy: int
    probes_used: int
    probe_delta_from_guaranteed_minimum: int
    move_actions: int
    wait_actions: int
    take_actions: int
    drop_actions: int
    operate_actions: int
    finish_actions: int
    rooms_visited: int
    room_revisits: int
    reference_plan_move_actions: int
    move_delta_from_reference_plan: int
    goal_satisfied: bool
    goal_leaf_count: int
    satisfied_goal_leaf_count: int
    unsatisfied_goal_leaves: tuple[str, ...]
    budget_remaining: int
    invalid_actions: int
    failed_finishes: int
    duplicate_requests: int
    protocol_conflicts: int


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
    performance: PerformanceSummary | None = None


class SessionStatus(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    turn: int
    status: TerminalStatus
    actions_remaining: int
    victory_code: str | None = None


def _goal_leaves(goal: GoalPredicate) -> tuple[GoalPredicate, ...]:
    if goal.kind in {GoalKind.AND, GoalKind.OR, GoalKind.NOT}:
        return tuple(leaf for child in goal.children for leaf in _goal_leaves(child))
    return (goal,)


def _goal_leaf_label(goal: GoalPredicate) -> str:
    value = goal.value.value if hasattr(goal.value, "value") else goal.value
    if goal.kind == GoalKind.ARTIFACT_FIELD:
        return f"artifact_field:{goal.artifact_id}.{goal.field}={value}"
    if goal.kind == GoalKind.ARTIFACT_LOCATION:
        return f"artifact_location:{goal.artifact_id}={value}"
    if goal.kind == GoalKind.PHASE_EQUALS:
        return f"phase_equals:{value}"
    raise ValueError(f"unsupported atomic goal kind {goal.kind}")


class Session:
    def __init__(self, episode: PrivateEpisode):
        self.episode = episode
        self.state: WorldState = episode.public.initial_state.model_copy(deep=True)
        self.trace: list[TraceRecord] = []
        self._turn_cache: dict[int, tuple[Action, ActionResponse]] = {}
        self._invalid_actions = 0
        self._failed_finishes = 0
        self._duplicate_requests = 0
        self._protocol_conflicts = 0
        self._lock = RLock()

    def observe(self) -> Observation:
        with self._lock:
            return observation(self.episode.public, self.state)

    def trace_snapshot(self) -> tuple[TraceRecord, ...]:
        with self._lock:
            return tuple(record.model_copy(deep=True) for record in self.trace)

    def state_snapshot(self) -> WorldState:
        with self._lock:
            return self.state.model_copy(deep=True)

    def status(self) -> SessionStatus:
        with self._lock:
            victory_code = next(
                (record.victory_code for record in reversed(self.trace) if record.victory_code),
                None,
            )
            return SessionStatus(
                turn=self.state.turn,
                status=self.state.terminal_status,
                actions_remaining=self.state.resources.actions_remaining,
                victory_code=victory_code,
            )

    def _performance_summary(self) -> PerformanceSummary | None:
        if self.state.terminal_status == TerminalStatus.ACTIVE:
            return None

        metadata = self.episode.generation_metadata
        action_counts = Counter(record.action.type for record in self.trace)
        probes_used = action_counts["probe"]
        guaranteed_policy_actions = metadata.guaranteed_policy_action_count
        if guaranteed_policy_actions <= 0:
            raise RuntimeError("terminal performance requires exact guaranteed-policy metadata")

        visited_rooms = {self.episode.public.initial_state.agent_room}
        room_revisits = 0
        for record in self.trace:
            if not isinstance(record.action, MoveAction):
                continue
            if record.action.target in visited_rooms:
                room_revisits += 1
            visited_rooms.add(record.action.target)

        reference_plan_move_actions = sum(
            item.get("type") == "move" for item in self.episode.reference_plan
        )
        goal_leaves = _goal_leaves(self.episode.public.goal)
        unsatisfied_goal_leaves = tuple(
            _goal_leaf_label(leaf)
            for leaf in goal_leaves
            if not evaluate_goal(leaf, self.state)
        )

        return PerformanceSummary(
            discovery_level=metadata.discovery_level,
            planning_level=metadata.planning_level,
            resource_pressure=metadata.resource_pressure,
            terminal_status=self.state.terminal_status,
            initial_action_budget=metadata.action_budget,
            resource_allowance=metadata.resource_allowance,
            planning_dependency_action_cost=metadata.planning_dependency_action_cost,
            actions_used=self.state.turn,
            optimal_physical_actions=metadata.optimal_action_count,
            minimum_guaranteed_probes=metadata.required_probe_count,
            guaranteed_policy_actions=guaranteed_policy_actions,
            action_delta_from_guaranteed_policy=self.state.turn - guaranteed_policy_actions,
            probes_used=probes_used,
            probe_delta_from_guaranteed_minimum=probes_used - metadata.required_probe_count,
            move_actions=action_counts["move"],
            wait_actions=action_counts["wait"],
            take_actions=action_counts["take"],
            drop_actions=action_counts["drop"],
            operate_actions=action_counts["operate"],
            finish_actions=action_counts["finish"],
            rooms_visited=len(visited_rooms),
            room_revisits=room_revisits,
            reference_plan_move_actions=reference_plan_move_actions,
            move_delta_from_reference_plan=(
                action_counts["move"] - reference_plan_move_actions
            ),
            goal_satisfied=evaluate_goal(self.episode.public.goal, self.state),
            goal_leaf_count=len(goal_leaves),
            satisfied_goal_leaf_count=(
                len(goal_leaves) - len(unsatisfied_goal_leaves)
            ),
            unsatisfied_goal_leaves=unsatisfied_goal_leaves,
            budget_remaining=self.state.resources.actions_remaining,
            invalid_actions=self._invalid_actions,
            failed_finishes=self._failed_finishes,
            duplicate_requests=self._duplicate_requests,
            protocol_conflicts=self._protocol_conflicts,
        )

    def act(self, expected_turn: int, action: Action) -> ActionResponse:
        with self._lock:
            cached = self._turn_cache.get(expected_turn)
            if cached is not None:
                cached_action, cached_response = cached
                if cached_action == action:
                    self._duplicate_requests += 1
                    return cached_response.model_copy(
                        update={
                            "duplicate": True,
                            "performance": self._performance_summary(),
                        }
                    )
                self._protocol_conflicts += 1
                return ActionResponse(
                    ok=False,
                    expected_turn=expected_turn,
                    current_turn=self.state.turn,
                    observation=self.observe(),
                    message=(
                        f"turn {expected_turn} was already committed with a different action"
                    ),
                    performance=self._performance_summary(),
                )

            if expected_turn != self.state.turn:
                self._protocol_conflicts += 1
                return ActionResponse(
                    ok=False,
                    expected_turn=expected_turn,
                    current_turn=self.state.turn,
                    observation=self.observe(),
                    message=f"turn mismatch: expected {expected_turn}, current {self.state.turn}",
                    performance=self._performance_summary(),
                )

            before_hash = canonical_hash(self.state)
            result = step(self.state, action, self.episode)
            if not result.ok:
                self._invalid_actions += 1
                return ActionResponse(
                    ok=False,
                    expected_turn=expected_turn,
                    current_turn=self.state.turn,
                    observation=self.observe(),
                    message=result.message,
                    performance=self._performance_summary(),
                )

            previous_turn = self.state.turn
            self.state = result.state

            if (
                isinstance(action, FinishAction)
                and self.state.turn != previous_turn
                and self.state.terminal_status != TerminalStatus.WON
            ):
                self._failed_finishes += 1

            # Non-consuming observations intentionally do not occupy a turn index.
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

            response = ActionResponse(
                ok=True,
                expected_turn=expected_turn,
                current_turn=self.state.turn,
                observation=self.observe(),
                events=tuple(event.model_dump(mode="json") for event in result.events),
                message=result.message,
                victory_code=result.victory_code,
                performance=self._performance_summary(),
            )

            if self.state.turn != previous_turn:
                self._turn_cache[expected_turn] = (action, response)
            return response
