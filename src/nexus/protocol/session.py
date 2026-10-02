from __future__ import annotations

from threading import RLock

from pydantic import BaseModel, ConfigDict

from nexus.engine.canonical import canonical_hash
from nexus.engine.engine import step
from nexus.models.actions import Action, FinishAction, ProbeAction
from nexus.models.episode import PrivateEpisode
from nexus.models.events import TraceRecord
from nexus.models.observation import Observation
from nexus.models.world import TerminalStatus, WorldState
from nexus.render.text import observation


class PerformanceSummary(BaseModel):
    """Terminal-only evaluation telemetry derived from trusted episode data and the live trace."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    actions_used: int
    optimal_physical_actions: int
    minimum_guaranteed_probes: int
    guaranteed_baseline_actions: int
    action_delta_from_guaranteed_baseline: int
    probes_used: int
    probe_delta_from_guaranteed_minimum: int
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
        probes_used = sum(isinstance(record.action, ProbeAction) for record in self.trace)
        guaranteed_baseline = metadata.optimal_action_count + metadata.required_probe_count
        return PerformanceSummary(
            actions_used=self.state.turn,
            optimal_physical_actions=metadata.optimal_action_count,
            minimum_guaranteed_probes=metadata.required_probe_count,
            guaranteed_baseline_actions=guaranteed_baseline,
            action_delta_from_guaranteed_baseline=self.state.turn - guaranteed_baseline,
            probes_used=probes_used,
            probe_delta_from_guaranteed_minimum=probes_used - metadata.required_probe_count,
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
