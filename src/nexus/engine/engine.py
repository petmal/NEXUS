from __future__ import annotations

from nexus.engine.goals import evaluate_goal
from nexus.engine.rules import apply_effect
from nexus.models.actions import (
    Action,
    ConfigureAction,
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
from nexus.models.world import INVENTORY, Artifact, TerminalStatus, WorldState
from nexus.models.investigation import SampleState
from nexus.models.network import NetworkSample, NetworkSpec, NetworkStock
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
    if state.resources.actions_remaining is not None:
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
            stock = next_state.stocks.get(action.artifact)
            if stock is not None:
                if stock.location != next_state.agent_room or stock.remaining == 0:
                    raise ValueError("specimen stock is unavailable")
                _consume_action(next_state)
                artifact_id = f"{stock.id}.{next_state.turn}"
                sample = (
                    NetworkSample(x=stock.x, y=stock.y) if isinstance(stock, NetworkStock)
                    else SampleState(source=stock.source, q=stock.q)
                )
                next_state.artifacts[artifact_id] = Artifact(
                    id=artifact_id, location=INVENTORY, shape="circle", pattern="plain",
                    orientation="north", polarity="positive",
                    value=0 if isinstance(stock, NetworkStock) else stock.q,
                    sample=sample,
                )
                if stock.remaining is not None:
                    stock.remaining -= 1
                events.append(EngineEvent(type="take", details={"stock": stock.id, "artifact": artifact_id}))
                _fail_if_exhausted(next_state, events)
                return StepResult(ok=True, state=next_state, events=tuple(events))
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
            if episode.public.investigation is not None:
                transformed = _scientific_transform(artifact, machine.id, episode)
                if isinstance(action, OperateAction):
                    if machine.uses_remaining == 0:
                        raise ValueError("machine has no uses remaining")
                    next_state.artifacts[artifact.id] = transformed
                    if machine.uses_remaining is not None:
                        machine.uses_remaining -= 1
                _consume_action(next_state)
                events.append(EngineEvent(type=action.type, details={
                    "machine": machine.id, "artifact": artifact.id,
                    "result": transformed.model_dump(mode="json"),
                }))
                _fail_if_exhausted(next_state, events)
                return StepResult(ok=True, state=next_state, events=tuple(events))
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

        elif isinstance(action, ConfigureAction):
            spec = episode.public.investigation
            if spec is None or action.machine != "controller":
                raise ValueError("no configurable controller")
            if next_state.agent_room != spec.controller_room:
                raise ValueError("controller is not in the current room")
            if isinstance(spec, NetworkSpec):
                if (len(action.settings) != 5 or action.settings[0] != 0
                        or any(v > 6 for v in action.settings)):
                    raise ValueError("network settings require port 0 and four field values in 0..6")
            else:
                size = 1 + len(spec.target_q) * (2 if spec.both_stocks else 1)
                if len(action.settings) != size or action.settings[0] not in (0, 1):
                    raise ValueError(f"settings require a port 0/1 and {size-1} values in 0..16")
            _consume_action(next_state)
            next_state.controller_settings = action.settings
            next_state.controller_accepted = False
            events.append(EngineEvent(type="configure", details={"machine": "controller", "settings": action.settings}))

        elif isinstance(action, FinishAction):
            _consume_action(next_state)
            if episode.public.investigation is not None:
                from nexus.engine.investigation import settings
                spec = episode.public.investigation
                next_state.controller_accepted = (
                    next_state.agent_room == spec.controller_room
                    and next_state.controller_settings == settings(spec, episode.investigation_truth)
                )
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


def _scientific_transform(artifact: Artifact, machine: str, episode: PrivateEpisode) -> Artifact:
    from nexus.engine.investigation import measurement
    spec, truth = episode.public.investigation, episode.investigation_truth
    sample = artifact.sample
    if spec is None or truth is None or sample is None:
        raise ValueError("apparatus requires a specimen")
    transformed = artifact.model_copy(deep=True)
    if isinstance(spec, NetworkSpec):
        from nexus.engine.network import measurement as network_measurement, prepare
        if not isinstance(sample, NetworkSample):
            raise ValueError("network apparatus requires a network specimen")
        if machine in ("shift", "shear"):
            transformed.sample.x, transformed.sample.y = prepare((sample.x, sample.y), machine)
            transformed.sample.reading = None
        elif machine == "meter":
            transformed.sample.reading = network_measurement(truth, f"{sample.x}:{sample.y}")
        else:
            raise ValueError("controller accepts configure and finish; it has no specimen preview")
        return transformed
    if not isinstance(sample, SampleState):
        raise ValueError("shared-response apparatus requires a shared-response specimen")
    if machine == "prepare":
        if sample.q >= 2:
            raise ValueError("preparation range is q=0..2")
        transformed.sample.q += 1
        transformed.sample.reading = None
        transformed.value = transformed.sample.q
    elif machine == "meter":
        transformed.sample.reading = measurement(spec, truth, f"{sample.source}:{sample.q}")
    elif machine == "selector":
        transformed.sample.reading = measurement(spec, truth, "selector")
    elif machine == "material":
        transformed.sample.reading = measurement(spec, truth, f"{sample.source}:property")
    else:
        raise ValueError("controller accepts configure and finish; it has no specimen preview")
    return transformed
