"""Public decision tracking for terminal diagnostics, independent of acceptance.

Existing prediction boards keep their exact-vector tracker. Stateful ontologies
may supply one tracker that follows committed public events. Acceptance remains
the runtime's mission predicate: there is no requirement of a unique repair.
"""

from dataclasses import dataclass
from typing import Protocol


class DecisionTracker(Protocol):
    def observe(self, record) -> None: ...
    def attempted(self) -> tuple[int, ...] | None: ...


@dataclass
class PredictionTracker:
    room: str
    mission_room: str
    machine: str
    settings: tuple[int, ...] | None

    def observe(self, record):
        action = record.action
        if action.type == "move":
            self.room = action.target
        elif action.type == "configure" and action.machine == self.machine:
            self.settings = action.settings

    def attempted(self):
        return self.settings if self.room == self.mission_room else None


def tracker_for(runtime, episode) -> DecisionTracker:
    factory = getattr(runtime, "mission_tracker", None)
    if factory is not None:
        return factory(episode.public)
    spec = episode.public.investigation
    state = episode.public.initial_state
    return PredictionTracker(
        state.agent_room,
        runtime.mission_room(spec),
        runtime.mission_machine(spec),
        runtime.submitted(state),
    )


def final_acceptance(runtime, episode, state):
    working = state.model_copy(deep=True)
    runtime.assess_mission(episode, working)
    return working.mission_accepted
