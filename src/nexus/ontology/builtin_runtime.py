"""Compatibility adapter for the published scientific episode formats.

Functions may mutate only the engine-owned working state. They never consume
resources, advance turns, emit receipts, or expose private evaluation results.
"""

from __future__ import annotations

from nexus.models.actions import ConfigureAction, FinishAction, MoveAction, action_contract
from nexus.models.episode import PrivateEpisode
from nexus.models.investigation import (
    InvestigationSpec,
    InvestigationTruth,
    SampleState,
    SpecimenStock,
)
from nexus.models.network import NetworkSample, NetworkSpec, NetworkStock, NetworkTruth
from nexus.models.world import (
    INVENTORY,
    Artifact,
    Orientation,
    Pattern,
    Polarity,
    Shape,
    WorldState,
)


def spawn(stock: SpecimenStock | NetworkStock, artifact_id: str) -> Artifact:
    sample = (
        NetworkSample(x=stock.x, y=stock.y)
        if isinstance(stock, NetworkStock)
        else SampleState(source=stock.source, q=stock.q)
    )
    return Artifact(
        id=artifact_id,
        location=INVENTORY,
        shape=Shape.CIRCLE,
        pattern=Pattern.PLAIN,
        orientation=Orientation.NORTH,
        polarity=Polarity.POSITIVE,
        value=0 if isinstance(stock, NetworkStock) else stock.q,
        sample=sample,
    )


def transform(
    artifact: Artifact,
    machine: str,
    episode: PrivateEpisode,
    instrument_settings: tuple[int, ...] | None = None,
) -> Artifact:
    from nexus.engine.investigation import measurement

    spec, truth = episode.public.investigation, episode.investigation_truth
    sample = artifact.sample
    if spec is None or truth is None or sample is None:
        raise ValueError("apparatus requires a specimen")
    if isinstance(spec, NetworkSpec):
        from nexus.engine.network import measurement as network_measurement
        from nexus.engine.network import prepare

        if not isinstance(sample, NetworkSample) or not isinstance(truth, NetworkTruth):
            raise ValueError("network apparatus requires a network specimen")
        if spec.version == "resonant-network-v1":
            from nexus.engine.resonance import transform

            return transform(artifact, machine, truth, instrument_settings)
        new_sample = sample.model_copy(deep=True)
        transformed = artifact.model_copy(update={"sample": new_sample})
        if machine in ("shift", "shear"):
            new_sample.x, new_sample.y = prepare((sample.x, sample.y), machine)
            new_sample.reading = None
        elif machine == "meter":
            new_sample.reading = network_measurement(truth, f"{sample.x}:{sample.y}")
        else:
            raise ValueError("controller accepts configure and finish; it has no specimen preview")
        return transformed
    if (
        not isinstance(sample, SampleState)
        or not isinstance(spec, InvestigationSpec)
        or not isinstance(truth, InvestigationTruth)
    ):
        raise ValueError("shared-response apparatus requires a shared-response specimen")
    new_sample = sample.model_copy(deep=True)
    transformed = artifact.model_copy(update={"sample": new_sample})
    if machine == "prepare":
        if sample.q >= 2:
            raise ValueError("preparation range is q=0..2")
        new_sample.q += 1
        new_sample.reading = None
        transformed.value = new_sample.q
    elif machine == "meter":
        new_sample.reading = measurement(spec, truth, f"{sample.source}:{sample.q}")
    elif machine == "selector":
        new_sample.reading = measurement(spec, truth, "selector")
    elif machine == "material":
        new_sample.reading = measurement(spec, truth, f"{sample.source}:property")
    else:
        raise ValueError("controller accepts configure and finish; it has no specimen preview")
    return transformed


def configure(episode: PrivateEpisode, state: WorldState, action: ConfigureAction) -> None:
    spec = episode.public.investigation
    if (
        isinstance(spec, NetworkSpec)
        and spec.version == "resonant-network-v1"
        and action.machine == "meter"
    ):
        machine = state.machines.get("meter")
        if machine is None or machine.room_id != state.agent_room:
            raise ValueError("meter is not in the current room")
        if len(action.settings) != 1 or action.settings[0] > 6:
            raise ValueError("meter requires one resonance setting in 0..6")
        machine.settings = action.settings
        return
    if not isinstance(spec, (InvestigationSpec, NetworkSpec)) or action.machine != "controller":
        raise ValueError("no configurable controller")
    if state.agent_room != spec.controller_room:
        raise ValueError("controller is not in the current room")
    if isinstance(spec, NetworkSpec):
        if (
            len(action.settings) != 5
            or action.settings[0] != 0
            or any(v > 6 for v in action.settings)
        ):
            raise ValueError("network settings require port 0 and four field values in 0..6")
    else:
        size = 1 + len(spec.target_q) * (2 if spec.both_stocks else 1)
        if len(action.settings) != size or action.settings[0] not in (0, 1):
            raise ValueError(f"settings require a port 0/1 and {size - 1} values in 0..16")
    state.controller_settings = action.settings
    state.controller_accepted = False


def assess_mission(episode: PrivateEpisode, state: WorldState) -> None:
    spec = legacy_spec(episode)
    state.controller_accepted = (
        state.agent_room == spec.controller_room and state.controller_settings == expected(episode)
    )


def public_contract(spec) -> dict:
    return action_contract(scientific=True, resonant=spec.version == "resonant-network-v1")


def physical_plan(episode: PrivateEpisode) -> tuple:
    spec = legacy_spec(episode)
    return tuple(
        MoveAction(target=f"R{i}") for i in range(1, int(spec.controller_room[1:]) + 1)
    ) + (
        ConfigureAction(machine="controller", settings=expected(episode)),
        FinishAction(),
    )


def belief(spec):
    from nexus.ontology.inference import FlatBelief, ResonantBeliefAdapter

    if spec.version == "resonant-network-v1":
        return ResonantBeliefAdapter(spec)
    return FlatBelief(spec)


def measurement(record):
    from nexus.ontology.inference import legacy_measurement

    return legacy_measurement(record)


def mission_room(spec) -> str:
    return spec.controller_room


def mission_machine(spec) -> str:
    return "controller"


def legacy_spec(episode: PrivateEpisode) -> InvestigationSpec | NetworkSpec:
    spec = episode.public.investigation
    if not isinstance(spec, (InvestigationSpec, NetworkSpec)):
        raise ValueError("expected published scientific specification")
    return spec


def expected(episode: PrivateEpisode) -> tuple[int, ...]:
    from nexus.engine.investigation import settings

    truth = episode.investigation_truth
    if not isinstance(truth, (InvestigationTruth, NetworkTruth)):
        raise ValueError("expected published scientific truth")
    return settings(legacy_spec(episode), truth)


def submitted(state: WorldState) -> tuple[int, ...] | None:
    return state.controller_settings


performance_style = "controller"


def log_terminal(spec, calibration_count, no_signal_count, after_resolved_count, first_classes):
    if spec.version == "resonant-network-v1":
        import logging

        logging.getLogger("nexus.diagnostics").info(
            "resonance_terminal calibration_measurements=%s no_signal_measurements=%s measurements_after_target_identified=%s first_submission_target_classes=%s",
            calibration_count,
            no_signal_count,
            after_resolved_count,
            first_classes,
        )
