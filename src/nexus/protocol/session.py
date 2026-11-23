from __future__ import annotations

from nexus.presentation import CONSOLE_VERSIONS

from collections import Counter
from threading import RLock

from pydantic import BaseModel, ConfigDict, Field

from nexus.engine.canonical import canonical_hash
from nexus.engine.engine import step
from nexus.engine.goals import evaluate_goal
from nexus.models.actions import Action, FinishAction, MoveAction
from nexus.models.episode import PrivateEpisode
from nexus.models.events import TraceRecord
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.observation import Observation
from nexus.models.world import TerminalStatus, WorldState
from nexus.protocol.investigation_metrics import (
    AuditedDecisionMissionPerformance,
    DecisionMissionPerformance,
    EligibleDecisionMissionPerformance,
    InvestigationPerformance,
    MissionPerformance,
)
from nexus.protocol.public_transcript import PublicTranscript
from nexus.protocol.public_transcript import record as record_exchange
from nexus.render.text import observation

PERFORMANCE_SCHEMA_URL = (
    "https://raw.githubusercontent.com/petmal/NEXUS/"
    "50ea40636bf46313fe5eef46973527dec097d17a/schemas/performance-v6.schema.json"
)


class PerformanceSummary(BaseModel):
    """Terminal-only evaluation telemetry derived from trusted episode data and the live trace."""

    model_config = ConfigDict(
        extra="forbid", frozen=True, populate_by_name=True, serialize_by_alias=True,
    )

    schema_url: str = Field(default=PERFORMANCE_SCHEMA_URL, alias="$schema")
    theory_level: int
    discovery_level: int
    planning_level: int
    resource_pressure: int
    terminal_status: TerminalStatus
    initial_action_budget: int
    resource_allowance: int
    planning_dependency_action_cost: int
    actions_used: int
    optimal_physical_actions: int
    action_delta_from_physical_optimum: int
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
    unsatisfied_goal_conditions: tuple[str, ...]
    budget_remaining: int
    invalid_actions: int
    failed_finishes: int
    duplicate_requests: int
    protocol_conflicts: int


TerminalPerformance = (
    PerformanceSummary
    | InvestigationPerformance
    | EligibleDecisionMissionPerformance
    | AuditedDecisionMissionPerformance
    | DecisionMissionPerformance
    | MissionPerformance
)


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
    performance: TerminalPerformance | None = None


class SessionStatus(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    turn: int
    status: TerminalStatus
    actions_remaining: int | None
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
    if goal.kind in {GoalKind.AND, GoalKind.OR, GoalKind.NOT}:
        return f"{goal.kind.value}(" + ",".join(_goal_leaf_label(c) for c in goal.children) + ")"
    raise ValueError(f"unsupported goal kind {goal.kind}")


def _goal_deficits(goal: GoalPredicate, state: WorldState) -> tuple[str, ...]:
    """False required conditions; keep OR/NOT intact instead of inventing obligations."""
    if evaluate_goal(goal, state):
        return ()
    if goal.kind == GoalKind.AND:
        return tuple(label for child in goal.children for label in _goal_deficits(child, state))
    return (_goal_leaf_label(goal),)


class Session:
    def __init__(self, episode: PrivateEpisode):
        if (
            episode.public.investigation is None
            and episode.generation_metadata.guaranteed_policy_action_count <= 0
        ):
            raise ValueError("legacy sessions require qualified guaranteed-policy metadata")
        self.episode = episode
        self.state: WorldState = episode.public.initial_state.model_copy(deep=True)
        self.trace: list[TraceRecord] = []
        self.public_transcript = PublicTranscript()
        self._turn_cache: dict[int, tuple[Action, ActionResponse]] = {}
        self._invalid_actions = 0
        self._failed_finishes = 0
        self._duplicate_requests = 0
        self._protocol_conflicts = 0
        self._construction_checks = 0
        self._evaluator_finalized = False
        self._lock = RLock()

    def _public_effect(self):
        return {"turn": self.state.turn, "actions_remaining": self.state.resources.actions_remaining,
                "terminal_status": self.state.terminal_status.value}

    def _exchange(self, request, operation, *, exclude_none=True):
        with self._lock:
            before = self._public_effect()
            try:
                response = operation()
            except Exception as exc:
                record_exchange(self.public_transcript, request,
                       {"exception": type(exc).__name__, "message": str(exc)},
                       before, self._public_effect())
                raise
            projected = (response.model_dump(mode="json", exclude_none=exclude_none)
                         if isinstance(response, BaseModel) else response)
            record_exchange(self.public_transcript, request, projected, before, self._public_effect())
            return response

    def manifest(self):
        from nexus.models.episode import PlayerManifest
        return self._exchange({"operation": "manifest"},
                              lambda: PlayerManifest.from_episode(self.episode.public), exclude_none=False)

    def evidence(self, filename: str):
        from nexus.presentation import evidence
        return self._exchange({"operation": "evidence", "filename": filename},
                              lambda: evidence(self.episode.public, filename))

    def observe(self) -> Observation:
        return self._exchange({"operation": "observe"}, self._observe)

    def status(self) -> SessionStatus:
        return self._exchange({"operation": "status"}, self._status, exclude_none=False)

    def act(self, expected_turn: int, action: Action, *, player_only: bool = False) -> ActionResponse:
        def apply():
            response = self._act(expected_turn, action)
            if player_only and self.episode.public.presentation_version in CONSOLE_VERSIONS:
                return response.model_copy(update={"performance": None})
            return response

        return self._exchange(
            {"operation": "action", "expected_turn": expected_turn,
             "action": action.model_dump(mode="json")},
            apply,
        )

    def can_check_construction(self) -> bool:
        spec = self.episode.public.investigation
        if spec is None:
            return False
        from nexus.ontology.catalog import runtime_for

        available = getattr(runtime_for(spec), "checker_available", None)
        return available is not None and available(spec)

    def check_construction(self, build: tuple[int, ...]):
        """Optional assistance using public observations, not a mission oracle."""
        from nexus.ontology.assistance import ConstructionCheckRequest, ConstructionCheckResult
        from nexus.ontology.catalog import runtime_for

        validated = ConstructionCheckRequest(build=build)

        def check():
            if not self.can_check_construction():
                raise ValueError("construction checker is not enabled")
            if self.state.terminal_status != TerminalStatus.ACTIVE:
                raise ValueError("construction checker requires an active attempt")
            spec = self.episode.public.investigation
            runtime = runtime_for(spec)
            observations = tuple(
                observed
                for record in self.trace
                if (observed := runtime.measurement(record)) is not None
            )
            consistent, count = runtime.check_construction(spec, observations, validated.build)
            self._construction_checks += 1
            return ConstructionCheckResult(
                consistent_with_readings=consistent,
                distinct_readings_checked=count,
                evidence_turn=self.state.turn,
            )

        return self._exchange({"operation": "check", "build": list(validated.build)}, check)

    def _observe(self) -> Observation:
        with self._lock:
            return observation(self.episode.public, self.state)

    def trace_snapshot(self, *, start: int = 0) -> tuple[TraceRecord, ...]:
        with self._lock:
            if type(start) is not int or start < 0:
                raise ValueError("trace start must be a nonnegative integer")
            return tuple(record.model_copy(deep=True) for record in self.trace[start:])

    def state_snapshot(self) -> WorldState:
        with self._lock:
            return self.state.model_copy(deep=True)

    def operator_snapshot(self) -> dict:
        """Private read-only snapshot, including an unfinished attempt at shutdown.

        Not available through the player transport or HTTP routes. In particular,
        this does not call finalize_attempt or label an active world as failed.
        """
        with self._lock:
            from nexus.protocol.operator_summary import world_profile
            from nexus.protocol.operator_witnesses import submission_witnesses
            from nexus.protocol.physical_cost import continuation_report

            if self.episode.public.investigation is not None:
                from nexus.protocol.investigation_metrics import summarize

                performance = summarize(
                    self.episode,
                    self.state,
                    self.trace,
                    invalid=self._invalid_actions,
                    duplicates=self._duplicate_requests,
                    conflicts=self._protocol_conflicts,
                    extended=True,
                )
            else:
                performance = self._performance_summary()
            status = self._status().model_dump(mode="json")
            status.pop("victory_code")
            witnesses = submission_witnesses(self.episode.public, self.trace)
            return {
                "world": world_profile(self.episode),
                "status": status,
                "performance": None if performance is None else performance.model_dump(mode="json"),
                "provider_stop_reason": None,
                "receipt_validation": "not_observed_by_service",
                "evidence_witnesses": None
                if witnesses is None
                else witnesses.model_dump(mode="json"),
                "assistance": {"construction_check_calls": self._construction_checks},
                "physical_continuation": continuation_report(self.episode, self.trace),
                "evaluator_finalized": self._evaluator_finalized,
            }

    def audit_snapshot(self):
        """One coherent private snapshot; never exposed by a player endpoint."""
        with self._lock:
            return self.state_snapshot(), self.trace_snapshot(), self.operator_snapshot()

    def _status(self) -> SessionStatus:
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

    def finalize_attempt(self) -> tuple[SessionStatus, TerminalPerformance]:
        """Irreversibly end an evaluator attempt and expose terminal-only diagnostics.

        This is deliberately not part of the player request contract. If called while the world is
        still active, the attempt becomes failed without consuming an environment action. That
        makes premature access fail closed rather than providing a usable mid-game hint channel.
        """
        with self._lock:
            self._evaluator_finalized = True
            if self.state.terminal_status == TerminalStatus.ACTIVE:
                self.state.terminal_status = TerminalStatus.FAILED
            performance = self._performance_summary()
            if performance is None:
                raise RuntimeError("finalized attempt did not produce terminal performance")
            return self._status(), performance

    def _performance_summary(self) -> TerminalPerformance | None:
        if self.state.terminal_status == TerminalStatus.ACTIVE:
            return None
        if self.episode.public.investigation is not None:
            from nexus.protocol.investigation_metrics import summarize
            return summarize(self.episode, self.state, self.trace, invalid=self._invalid_actions,
                             duplicates=self._duplicate_requests, conflicts=self._protocol_conflicts)

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
            theory_level=metadata.theory_level,
            discovery_level=metadata.discovery_level,
            planning_level=metadata.planning_level,
            resource_pressure=metadata.resource_pressure,
            terminal_status=self.state.terminal_status,
            initial_action_budget=metadata.action_budget,
            resource_allowance=metadata.resource_allowance,
            planning_dependency_action_cost=metadata.planning_dependency_action_cost,
            actions_used=self.state.turn,
            optimal_physical_actions=metadata.optimal_action_count,
            action_delta_from_physical_optimum=self.state.turn - metadata.optimal_action_count,
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
            unsatisfied_goal_conditions=_goal_deficits(self.episode.public.goal, self.state),
            budget_remaining=self.state.resources.actions_remaining,
            invalid_actions=self._invalid_actions,
            failed_finishes=self._failed_finishes,
            duplicate_requests=self._duplicate_requests,
            protocol_conflicts=self._protocol_conflicts,
        )

    def _act(self, expected_turn: int, action: Action) -> ActionResponse:
        with self._lock:
            if type(expected_turn) is not int or expected_turn < 0:
                raise ValueError("expected_turn must be a nonnegative integer")
            cached = self._turn_cache.get(expected_turn)
            if cached is not None:
                cached_action, cached_response = cached
                if cached_action == action:
                    self._duplicate_requests += 1
                    return cached_response.model_copy(
                        deep=True,
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
                    observation=self._observe(),
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
                    observation=self._observe(),
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
                    observation=self._observe(),
                    message=result.message,
                    performance=self._performance_summary(),
                )

            previous_state = self.state
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

            events = tuple(event.model_dump(mode="json") for event in result.events)
            message = result.message
            if self.episode.public.presentation_version in CONSOLE_VERSIONS:
                from nexus.presentation.console import action_result
                item = previous_state.artifacts.get(getattr(action, "artifact", ""))
                message = action_result(self.episode.public, action, events, message,
                                        already_collapsed=getattr(item, "payload", {}).get("reading") == 5)
            response = ActionResponse(
                ok=True,
                expected_turn=expected_turn,
                current_turn=self.state.turn,
                observation=self._observe(),
                events=events,
                message=message,
                victory_code=result.victory_code,
                performance=self._performance_summary(),
            )

            if self.state.turn != previous_turn:
                self._turn_cache[expected_turn] = (action, response.model_copy(deep=True))
            return response
