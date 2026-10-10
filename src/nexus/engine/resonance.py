"""Dependent measurement semantics; all arithmetic and instrument controls are public."""

from itertools import product

from nexus.engine.network import prepare, response
from nexus.models.network import FIELD, NetworkSample, NetworkTruth, ResonanceLaw
from nexus.models.world import Artifact

RESONANT_BENCH = tuple(p for p in product(range(7), repeat=2) if p not in FIELD)


def resonance(law: ResonanceLaw, x: int, y: int) -> int:
    left = x * x if law.gate == 1 else x
    right = y * y if law.gate == 2 else y
    return (law.alpha * left + law.beta * right) % 7


def settings(truth: NetworkTruth) -> tuple[int, ...]:
    if truth.resonance is None:
        raise ValueError("resonant truth requires a calibration law")
    return (0, *((response(truth, x, y) + resonance(truth.resonance, x, y)) % 7 for x, y in FIELD))


def transform(
    artifact: Artifact,
    machine: str,
    truth: NetworkTruth,
    instrument_settings: tuple[int, ...] | None,
) -> Artifact:
    sample = artifact.sample
    if not isinstance(sample, NetworkSample) or truth.resonance is None:
        raise ValueError("resonant apparatus requires matching specimen and truth")
    result = artifact.model_copy(deep=True)
    result.sample.reading = None
    result.sample.signal = None
    if machine in ("shift", "shear"):
        result.sample.x, result.sample.y = prepare((sample.x, sample.y), machine)
        return result
    if machine not in ("calibrator", "meter"):
        raise ValueError("controller accepts configure and finish; it has no specimen preview")
    if (sample.x, sample.y) not in RESONANT_BENCH:
        raise ValueError("field coordinates are outside both instruments' bench range")
    tuned = resonance(truth.resonance, sample.x, sample.y)
    if machine == "calibrator":
        result.sample.reading = tuned
    else:
        if instrument_settings is None or len(instrument_settings) != 1:
            raise ValueError("meter requires one configured resonance setting")
        result.sample.signal = instrument_settings[0] == tuned
        if result.sample.signal:
            result.sample.reading = response(truth, sample.x, sample.y)
    return result
