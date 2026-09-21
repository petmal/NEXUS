from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from itertools import product

from nexus.engine.rules import apply_effect
from nexus.models.rules import Effect
from nexus.models.world import Artifact, Orientation, Pattern, Polarity, Shape


@dataclass(frozen=True)
class Experiment:
    phase: int
    artifact: Artifact


def _projection(artifact: Artifact) -> tuple[int, str, str]:
    return artifact.value, artifact.polarity.value, artifact.orientation.value


def experiment_pool() -> list[Experiment]:
    experiments: list[Experiment] = []
    for shape, phase, value, orientation in product(
        tuple(Shape),
        (0, 1),
        (1, 2, 4, 7),
        (Orientation.NORTH, Orientation.EAST),
    ):
        experiments.append(
            Experiment(
                phase=phase,
                artifact=Artifact(
                    id="sample",
                    location="lab",
                    shape=shape,
                    pattern=Pattern.PLAIN,
                    orientation=orientation,
                    value=value,
                    polarity=Polarity.POSITIVE,
                ),
            )
        )
    return experiments


def choose_discriminating_evidence(
    target: Effect,
    candidates: list[Effect],
    max_rows: int = 12,
) -> tuple[list[Experiment], list[Effect]]:
    remaining = list(candidates)
    chosen: list[Experiment] = []
    unused = experiment_pool()

    while len(remaining) > 1 and len(chosen) < max_rows:
        best: tuple[int, Experiment, tuple[int, str, str]] | None = None
        for experiment in unused:
            target_out = _projection(apply_effect(target, experiment.artifact, experiment.phase))
            matches = sum(
                _projection(apply_effect(candidate, experiment.artifact, experiment.phase)) == target_out
                for candidate in remaining
            )
            if matches == 0:
                continue
            if best is None or matches < best[0]:
                best = (matches, experiment, target_out)
                if matches == 1:
                    break
        if best is None:
            break
        _, experiment, target_out = best
        chosen.append(experiment)
        unused.remove(experiment)
        remaining = [
            candidate
            for candidate in remaining
            if _projection(apply_effect(candidate, experiment.artifact, experiment.phase)) == target_out
        ]

    return chosen, remaining


def evidence_csv(target: Effect, experiments: list[Experiment]) -> str:
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        [
            "phase",
            "shape",
            "input_value",
            "input_polarity",
            "input_orientation",
            "output_value",
            "output_polarity",
            "output_orientation",
        ]
    )
    for experiment in experiments:
        before = experiment.artifact
        after = apply_effect(target, before, experiment.phase)
        writer.writerow(
            [
                experiment.phase,
                before.shape.value,
                before.value,
                before.polarity.value,
                before.orientation.value,
                after.value,
                after.polarity.value,
                after.orientation.value,
            ]
        )
    return output.getvalue()


def candidates_matching_csv(csv_text: str, candidates: list[Effect]) -> list[Effect]:
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    remaining = list(candidates)
    for row in rows:
        artifact = Artifact(
            id="sample",
            location="lab",
            shape=Shape(row["shape"]),
            pattern=Pattern.PLAIN,
            orientation=Orientation(row["input_orientation"]),
            value=int(row["input_value"]),
            polarity=Polarity(row["input_polarity"]),
        )
        expected = (
            int(row["output_value"]),
            row["output_polarity"],
            row["output_orientation"],
        )
        remaining = [
            candidate
            for candidate in remaining
            if _projection(apply_effect(candidate, artifact, int(row["phase"]))) == expected
        ]
    return remaining
