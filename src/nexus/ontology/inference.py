"""Inference adapters consume public measurements, never the selected hidden law."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from nexus.models.actions import OperateAction, ProbeAction
from nexus.models.events import TraceRecord


@dataclass(frozen=True)
class Measurement:
    instrument: str
    sample: dict
    tuning: int | None = None
    calibration: bool = False
    no_signal: bool = False


class Belief(Protocol):
    def counts(self) -> tuple[int, int]: ...
    def observe(self, measurement: Measurement) -> None: ...
    def exclude_target(self, target: tuple[int, ...] | None) -> None: ...


class FlatBelief:
    def __init__(self, spec):
        from nexus.engine.investigation import settings
        from nexus.models.network import NetworkSpec

        if isinstance(spec, NetworkSpec):
            from nexus.generator.network import compile_network

            worlds, problem = compile_network(3)
        else:
            from nexus.generator.investigation import base_spec, compile_problem

            worlds, problem = compile_problem(base_spec(spec))  # pyright: ignore[reportArgumentType] -- frozen Pydantic model is hashable
        self.belief = set(problem.compatible(spec.supplied_measurements))
        self.predictions = tuple(settings(spec, world) for world in worlds)
        self.rows = dict(problem.experiments)
        if spec.resolved_settings is not None:
            self.belief = {i for i in self.belief if self.predictions[i] == spec.resolved_settings}

    def counts(self) -> tuple[int, int]:
        return len(self.belief), len({self.predictions[i] for i in self.belief})

    def observe(self, measurement: Measurement) -> None:
        sample, instrument = measurement.sample, measurement.instrument
        name = (
            f"{sample['x']}:{sample['y']}"
            if "x" in sample
            else "selector"
            if instrument == "selector"
            else f"{sample['source']}:property"
            if instrument == "material"
            else f"{sample['source']}:{sample['q']}"
        )
        if name not in self.rows:
            raise RuntimeError("runtime produced a measurement missing from the certified prior")
        row = self.rows[name]
        self.belief = {i for i in self.belief if row[i] == sample["reading"]}

    def exclude_target(self, target: tuple[int, ...] | None) -> None:
        self.belief = {i for i in self.belief if self.predictions[i] != target}


class ResonantBeliefAdapter:
    def __init__(self, spec):
        from nexus.generator.resonance import ResonantBelief

        self.belief = ResonantBelief(spec)

    def counts(self) -> tuple[int, int]:
        return self.belief.counts()

    def observe(self, measurement: Measurement) -> None:
        self.belief.measure(measurement.instrument, measurement.sample, measurement.tuning)

    def exclude_target(self, target: tuple[int, ...] | None) -> None:
        if target is not None:
            self.belief.excluded.add(target)


def legacy_measurement(record: TraceRecord) -> Measurement | None:
    action = record.action
    if not isinstance(action, (ProbeAction, OperateAction)) or action.machine not in (
        "meter",
        "selector",
        "material",
        "calibrator",
    ):
        return None
    event = next((e for e in record.events if "result" in e.details), None)
    if event is None:
        return None
    sample = event.details["result"]["sample"]
    tuning = event.details.get("instrument_settings")
    return Measurement(
        action.machine,
        sample,
        tuning[0] if tuning else None,
        action.machine == "calibrator",
        action.machine == "meter" and sample.get("signal") is False,
    )
