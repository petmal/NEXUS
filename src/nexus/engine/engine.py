from __future__ import annotations

from nexus.engine.goals import evaluate_goal
from nexus.engine.rules import apply_effect
from nexus.models.actions import (
    Action,
    DropAction,
    FinishAction,
    MoveAction,
    ObserveAction,
    OperateAction,
    ProbeAction,
    TakeAction,
    WaitAction,
)
from nexus.models.episode import PrivateEpisode
from nexus.models.events import EngineEvent, StepResult
from nexus.models.world import INVENTORY, TerminalStatus, WorldState
from nexus.verification.receipt import victory_receipt


def _neighbors(episode: PrivateEpisode, room: str) -> set[str]:
    out: set[str] = set()
    for left, right in episode.public.edges:
        if left == room:
            out.add(right)
        elif right == room:
            out.add(left)
    return out


def _consume_action(state: WorldState) -> None:
    if state.resources.actions_remaining <= 0:
        raise ValueError("no actions remaining")
    state.resources.actions_remaining -= 1
    state.turn += 1


def _fail_if_exhausted(state: WorldState, events: list[EngineEvent]) -> None:
    if state.resources.actions_remaining == 0 and state.terminal_status == TerminalStatus.ACTIVE:
        state.terminal_status = TerminalStatus.FAILED
        events.append(EngineEvent(type="budget_exhausted"))


def step(state: WorldState, action: Action, episode: PrivateEpisode) -> StepResult:
    if state.terminal_status != TerminalStatus.ACTIVE:
        return StepResult(ok=False, state=state.model_copy(deep=True), message="episode is terminal")

    next_state = state.model_copy(deep=True)
    events: list[EngineEvent] = []

    try:
        if isinstance(action, ObserveAction):
            return StepResult(ok=True, state=next_state, events=(EngineEvent(type="observe"),))

        if isinstance(action, MoveAction):
            if action.target not in _neighbors(episode, next_state.agent_room):
                raise ValueError("target room is not adjacent")
            _consume_action(next_state)
            origin = next_state.agent_room
            next_state.agent_room = action.target
            events.append(EngineEvent(type="move", details={"from": origin, "to": action.target}))

        elif isinstance(action, TakeAction):
            artifact = next_state.artifacts.get(action.artifact)
            if artifact is None or artifact.location != next_state.agent_room:
                raise ValueError("artifact is not available in the current room")
            _consume_action(next_state)
            artifact.location = INVENTORY
            events.append(EngineEvent(type="take", details={"artifact": artifact.id}))

        elif isinstance(action, DropAction):
            artifact = next_state.artifacts.get(action.artifact)
            if artifact is None or artifact.location != INVENTORY:
                raise ValueError("artifact is not carried")
            _consume_action(next_state)
            artifact.location = next_state.agent_room
            events.append(
                EngineEvent(type="drop", details={"artifact": artifact.id, "room": next_state.agent_room})
            )

        elif isinstance(action, (OperateAction, ProbeAction)):
            machine = next_state.machines.get(action.machine)
            artifact = next_state.artifacts.get(action.artifact)
            if machine is None or machine.room_id != next_state.agent_room:
                raise ValueError("machine is not in the current room")
            if artifact is None or artifact.location != INVENTORY:
                raise ValueError("artifact is not carried")
            rule_id = episode.machine_rules.get(machine.id)
            if rule_id is None:
                raise ValueError("machine has no configured rule")
            rule = episode.rules[rule_id]
            _consume_action(next_state)
            transformed = apply_effect(rule, artifact, next_state.phase)
            if isinstance(action, OperateAction):
                if machine.uses_remaining <= 0:
                    raise ValueError("machine has no uses remaining")
                transformed.location = INVENTORY
                next_state.artifacts[artifact.id] = transformed
                machine.uses_remaining -= 1
                events.append(
                    EngineEvent(
                        type="operate",
                        details={"machine": machine.id, "artifact": artifact.id},
                    )
                )
            else:
                events.append(
                    EngineEvent(
                        type="probe",
                        details={
                            "machine": machine.id,
                            "artifact": artifact.id,
                            "result": transformed.model_dump(mode="json"),
                        },
                    )
                )

        elif isinstance(action, WaitAction):
            _consume_action(next_state)
            next_state.phase = (next_state.phase + 1) % episode.public.phase_modulus
            events.append(EngineEvent(type="wait", details={"phase": next_state.phase}))

        elif isinstance(action, FinishAction):
            _consume_action(next_state)
            if evaluate_goal(episode.public.goal, next_state):
                next_state.terminal_status = TerminalStatus.WON
                code = victory_receipt(episode)
                events.append(EngineEvent(type="victory"))
                return StepResult(
                    ok=True,
                    state=next_state,
                    events=tuple(events),
                    message="mission complete",
                    victory_code=code,
                )
            events.append(EngineEvent(type="finish_rejected"))

        else:
            raise ValueError(f"unsupported action type: {type(action).__name__}")

        _fail_if_exhausted(next_state, events)
        return StepResult(ok=True, state=next_state, events=tuple(events))
    except (KeyError, ValueError) as exc:
        return StepResult(ok=False, state=state.model_copy(deep=True), message=str(exc))
