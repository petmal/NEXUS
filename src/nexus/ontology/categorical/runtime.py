"""Categorical adapter. Core engine owns accounting and transactional state."""

from typing import cast

from nexus.models.actions import ConfigureAction, FinishAction, action_contract
from nexus.models.domain import DomainArtifact, DomainStock
from nexus.models.world import INVENTORY
from nexus.ontology.categorical.laws import reading, target
from nexus.ontology.categorical.schema import SYMBOLS
from nexus.ontology.inference import Measurement

FAMILY = "categorical-chain-poc-v1"


def validate_episode(episode):
    spec = episode.public.investigation.data()
    truth = episode.investigation_truth.data()
    state = episode.public.initial_state
    if set(episode.public.rooms) != {spec.mission_room} or episode.public.edges:
        raise ValueError("categorical PoC currently supports a single room")
    if episode.public.goal.kind != "mission_accepted":
        raise ValueError("categorical PoC requires mission_accepted goal")
    if len(truth.laws) != spec.depth:
        raise ValueError("categorical truth depth does not match specification")
    if spec.mission_room not in episode.public.rooms:
        raise ValueError("unknown mission room")
    if "board" not in state.machines or state.machines["board"].room_id != spec.mission_room:
        raise ValueError("prediction board missing from mission room")
    expected_machines = {"board", *(f"instrument{i}" for i in range(spec.depth))}
    if set(state.machines) != expected_machines:
        raise ValueError("categorical apparatus does not match declared depth")
    for name, machine in state.machines.items():
        size = 3 if name == "board" else 1
        if machine.settings is not None and (
            len(machine.settings) != size
            or any(type(v) is not int or not 0 <= v <= 2 for v in machine.settings)
        ):
            raise ValueError("invalid initial categorical apparatus settings")
    if set(state.stocks) != {"S0", "S1", "S2"} or any(
        state.stocks[f"S{i}"].data().symbol != symbol for i, symbol in enumerate(SYMBOLS)
    ):
        raise ValueError("categorical PoC requires one declared stock per symbol")


def spawn(stock: DomainStock, artifact_id: str) -> DomainArtifact:
    return DomainArtifact(
        ontology=FAMILY, id=artifact_id, location=INVENTORY, payload={"symbol": stock.data().symbol}
    )


def transform(artifact, machine, episode, instrument_settings=None):
    spec = episode.public.investigation.data()
    if machine not in tuple(f"instrument{i}" for i in range(spec.depth)):
        raise ValueError("board accepts configure and finish; it has no specimen preview")
    stage = int(machine.removeprefix("instrument"))
    value = SYMBOLS.index(artifact.data().symbol)
    result = reading(
        episode.investigation_truth.data().laws,
        stage,
        value,
        instrument_settings[0] if instrument_settings else None,
    )
    return DomainArtifact(
        ontology=FAMILY,
        id=artifact.id,
        location=artifact.location,
        payload={
            "symbol": SYMBOLS[value],
            "signal": result is not None,
            "reading": SYMBOLS[result] if result is not None else None,
        },
    )


def configure(episode, state, action):
    spec = episode.public.investigation.data()
    valid = ("board", *(f"instrument{i}" for i in range(1, spec.depth)))
    if action.machine not in valid:
        raise ValueError("unknown configurable categorical apparatus")
    machine = state.machines.get(action.machine)
    if machine is None or machine.room_id != state.agent_room:
        raise ValueError("apparatus is not in the current room")
    size = 3 if action.machine == "board" else 1
    if len(action.settings) != size or any(v > 2 for v in action.settings):
        raise ValueError(f"apparatus requires {size} categorical selectors in 0..2")
    machine.settings = action.settings
    if action.machine == "board":
        state.mission_accepted = False


def expected(episode):
    return target(episode.investigation_truth.data().laws)


def submitted(state):
    return state.machines["board"].settings


def mission_room(spec):
    return spec.data().mission_room


def mission_machine(spec):
    return "board"


def assess_mission(episode, state):
    state.mission_accepted = state.agent_room == mission_room(
        episode.public.investigation
    ) and submitted(state) == expected(episode)


def public_contract(spec):
    result = action_contract(scientific=True)
    for item in cast(tuple[dict, ...], result["reference"]):
        if item["type"] == "configure":
            item["description"] = (
                "Configure board with three categorical selectors, or a later instrument with one selector. No correctness feedback."
            )
            item["example"] = {"type": "configure", "machine": "board", "settings": [0, 1, 2]}
    # Public specification only; no selected law or hidden target is read.
    result["ontology"] = {
        "family": FAMILY,
        "experimental": True,
        "symbol_order": list(SYMBOLS),
        "configuration": "board: three selectors 0..2; instrument1/instrument2 if present: one selector 0..2",
        "mission": "Submit composed law outputs for ka,tu,ve on board, then finish in its room.",
    }
    return result


def physical_plan(episode):
    # The explicitly experimental generator supports one-room P0 worlds only.
    return (ConfigureAction(machine="board", settings=expected(episode)), FinishAction())


def measurement(record):
    action = record.action
    if action.type not in ("probe", "operate") or not action.machine.startswith("instrument"):
        return None
    event = next((e for e in record.events if "result" in e.details), None)
    if event is None:
        return None
    payload = event.details["result"]["payload"]
    tuning = event.details.get("instrument_settings")
    return Measurement(
        action.machine,
        payload,
        tuning[0] if tuning else None,
        calibration=action.machine == "instrument0",
        no_signal=payload["signal"] is False,
    )


def belief(spec):
    from nexus.ontology.categorical.inference import CategoricalBelief

    return CategoricalBelief(spec.data().depth)


performance_style = "mission"


def log_terminal(spec, calibration_count, no_signal_count, after_resolved_count, first_classes):
    import logging

    logging.getLogger("nexus.diagnostics").info(
        "ontology_terminal family=%s calibration_measurements=%s no_signal_measurements=%s measurements_after_target_identified=%s first_submission_target_classes=%s",
        FAMILY,
        calibration_count,
        no_signal_count,
        after_resolved_count,
        first_classes,
    )
