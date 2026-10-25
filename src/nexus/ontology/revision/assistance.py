"""Simulate a proposed construction only on evidence already available to the player."""

from __future__ import annotations

from collections.abc import Sequence

from nexus.ontology.inference import Measurement
from nexus.ontology.revision.laws import read, validate_build
from nexus.ontology.revision.schema import Investigation


def check_readings(
    spec: Investigation, observations: Sequence[Measurement], build: tuple[int, ...]
) -> tuple[bool, int]:
    if spec.consistency_check != "readings":
        raise ValueError("construction checker is not enabled")
    if not validate_build(build):
        raise ValueError("build must contain four integer link indices from 0 through 11")
    readings = {(0,): (spec.archive[0],), (1,): (spec.archive[1],)}
    for observation in observations:
        word = tuple(observation.sample["query"])
        value = tuple(observation.sample["values"])
        if word in readings and readings[word] != value:
            raise ValueError("recorded reader observations are inconsistent")
        readings[word] = value
    # No class enumeration, selected truth, hypothetical query or finish oracle.
    return all(read(build, word) == value for word, value in readings.items()), len(readings)
