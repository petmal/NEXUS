from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from functools import lru_cache
from itertools import product

from nexus.engine.rules import apply_effect
from nexus.generator.rules import transformation_rule_catalog
from nexus.models.rules import Effect
from nexus.models.world import Artifact, Orientation, Pattern, Polarity, Shape


@dataclass(frozen=True)
class Experiment:
    phase: int
    artifact: Artifact


def _projection(artifact: Artifact) -> tuple[int, str, str]:
    return artifact.value, artifact.polarity.value, artifact.orientation.value


@lru_cache(maxsize=1)
def experiment_pool() -> tuple[Experiment, ...]:
    experiments: list[Experiment] = []
    for shape, phase, value, orientation, polarity in product(
        tuple(Shape),
        (0, 1),
        (0, 1, 2, 4, 7),
        (Orientation.NORTH, Orientation.EAST),
        tuple(Polarity),
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
                    polarity=polarity,
                ),
            )
        )
    return tuple(experiments)


@lru_cache(maxsize=1)
def _catalog_signature_matrix() -> tuple[tuple[tuple[int, str, str], ...], ...]:
    """Return experiment-major signatures for the finite prototype grammar."""
    catalog = transformation_rule_catalog()
    return tuple(
        tuple(_projection(apply_effect(rule, experiment.artifact, experiment.phase)) for rule in catalog)
        for experiment in experiment_pool()
    )


def _catalog_indices(candidates: list[Effect]) -> list[int] | None:
    catalog = transformation_rule_catalog()
    index_by_json = {rule.model_dump_json(): index for index, rule in enumerate(catalog)}
    try:
        return [index_by_json[candidate.model_dump_json()] for candidate in candidates]
    except KeyError:
        return None


def choose_discriminating_evidence(
    target: Effect,
    candidates: list[Effect],
    max_rows: int = 12,
) -> tuple[list[Experiment], list[Effect]]:
    """Greedily choose experiments that uniquely discriminate the target law when possible."""
    candidate_indices = _catalog_indices(candidates)
    catalog = transformation_rule_catalog()
    target_json = target.model_dump_json()
    try:
        target_index = next(i for i, rule in enumerate(catalog) if rule.model_dump_json() == target_json)
    except StopIteration:
        candidate_indices = None
        target_index = -1

    if candidate_indices is None or target_index < 0:
        return _choose_discriminating_evidence_fallback(target, candidates, max_rows=max_rows)

    remaining = list(candidate_indices)
    chosen_indices: list[int] = []
    unused = set(range(len(experiment_pool())))
    matrix = _catalog_signature_matrix()

    while len(remaining) > 1 and len(chosen_indices) < max_rows:
        best_experiment: int | None = None
        best_matches: list[int] | None = None
        for experiment_index in sorted(unused):
            expected = matrix[experiment_index][target_index]
            matches = [index for index in remaining if matrix[experiment_index][index] == expected]
            if not matches:
                continue
            if best_matches is None or len(matches) < len(best_matches):
                best_experiment = experiment_index
                best_matches = matches
                if len(matches) == 1:
                    break
        if best_experiment is None or best_matches is None:
            break
        chosen_indices.append(best_experiment)
        unused.remove(best_experiment)
        remaining = best_matches

    experiments = experiment_pool()
    return [experiments[index] for index in chosen_indices], [catalog[index] for index in remaining]


def _choose_discriminating_evidence_fallback(
    target: Effect,
    candidates: list[Effect],
    *,
    max_rows: int,
) -> tuple[list[Experiment], list[Effect]]:
    remaining = list(candidates)
    chosen: list[Experiment] = []
    unused = list(experiment_pool())
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
