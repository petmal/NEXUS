from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from functools import lru_cache
from itertools import product

from nexus.diagnostics import timed_call
from nexus.engine.rules import apply_effect
from nexus.generator.difficulty import artifact_projection
from nexus.generator.rules import transformation_rule_catalog
from nexus.models.rules import Effect
from nexus.models.world import Artifact, Orientation, Pattern, Polarity, Shape


class EvidencePlanningError(RuntimeError):
    pass


@dataclass(frozen=True)
class Experiment:
    phase: int
    artifact: Artifact


@dataclass(frozen=True)
class MissionEvidencePlan:
    experiments: tuple[Experiment, ...]
    candidate_count: int
    prediction_count: int
    direct_target_example: bool


def _projection(artifact: Artifact) -> tuple[int, str, str]:
    return artifact_projection(artifact)


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
@timed_call("core.catalogue_signature_matrix")
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


def _catalog_index(target: Effect) -> int:
    target_json = target.model_dump_json()
    for index, rule in enumerate(transformation_rule_catalog()):
        if rule.model_dump_json() == target_json:
            return index
    raise EvidencePlanningError("target rule is outside the finite prototype grammar")


def _filter_indices(
    remaining: list[int],
    experiment_index: int,
    target_index: int,
) -> list[int]:
    matrix = _catalog_signature_matrix()
    expected = matrix[experiment_index][target_index]
    return [index for index in remaining if matrix[experiment_index][index] == expected]


def _prediction_count(indices: list[int], artifact: Artifact, phase: int) -> int:
    catalog = transformation_rule_catalog()
    return len(
        {
            _projection(apply_effect(catalog[index], artifact, phase))
            for index in indices
        }
    )


def is_direct_context(experiment: Experiment, artifact: Artifact, phase: int) -> bool:
    """Whether evidence directly demonstrates the mission's branch-selection context.

    The current generated grammar selects a branch only from artifact shape and phase parity.
    Value, polarity, and orientation affect the result but not which branch is selected.
    """
    return (
        experiment.artifact.shape == artifact.shape
        and experiment.phase % 2 == phase % 2
    )


def mission_prediction_count(
    candidates: list[Effect],
    artifact: Artifact,
    phase: int,
) -> int:
    return len(
        {
            _projection(apply_effect(candidate, artifact, phase))
            for candidate in candidates
        }
    )


def measurement_filename(machine_id: str) -> str:
    return "measurements.csv" if machine_id == "M1" else f"measurements_{machine_id}.csv"


def choose_mission_evidence(
    target: Effect,
    candidates: list[Effect],
    artifact: Artifact,
    phase: int,
    *,
    discovery_level: int,
    max_rows: int = 12,
) -> MissionEvidencePlan:
    """Construct evidence with a mechanically verified mission-relevant information profile.

    Level 0 includes a direct branch-context example and fully identifies the rule.
    Level 1 excludes direct branch-context examples but makes the mission outcome inferable.
    Level 2 excludes direct examples and deliberately leaves multiple mission outcomes possible;
    probing the actual mission input then reveals the required outcome in one observation.

    Level 3 is composed by the episode generator from two independent level-2 stages.
    """
    if discovery_level not in {0, 1, 2}:
        raise ValueError("single-machine evidence discovery_level must be 0, 1, or 2")

    candidate_indices = _catalog_indices(candidates)
    if candidate_indices is None:
        raise EvidencePlanningError("mission evidence requires catalog rules")

    target_index = _catalog_index(target)
    if target_index not in candidate_indices:
        raise EvidencePlanningError("target rule is not in the candidate set")

    remaining = list(candidate_indices)
    chosen: list[int] = []
    pool = experiment_pool()

    if discovery_level == 0:
        direct_indices = [
            index
            for index, experiment in enumerate(pool)
            if is_direct_context(experiment, artifact, phase)
        ]
        if not direct_indices:
            raise EvidencePlanningError("no direct-context experiment is available")

        best_direct = min(
            direct_indices,
            key=lambda index: (len(_filter_indices(remaining, index, target_index)), index),
        )
        chosen.append(best_direct)
        remaining = _filter_indices(remaining, best_direct, target_index)

        while len(remaining) > 1 and len(chosen) < max_rows:
            best: tuple[int, int, list[int]] | None = None
            for index in range(len(pool)):
                if index in chosen:
                    continue
                filtered = _filter_indices(remaining, index, target_index)
                if len(filtered) >= len(remaining):
                    continue
                score = (len(filtered), index)
                if best is None or score < best[:2]:
                    best = (score[0], score[1], filtered)
            if best is None:
                break
            _, index, remaining = best
            chosen.append(index)

        if len(remaining) != 1:
            raise EvidencePlanningError("unable to construct uniquely identifying level-0 evidence")

    else:
        allowed = [
            index
            for index, experiment in enumerate(pool)
            if not is_direct_context(experiment, artifact, phase)
        ]

        if discovery_level == 1:
            while _prediction_count(remaining, artifact, phase) > 1 and len(chosen) < max_rows:
                best: tuple[tuple[int, int, int], int, list[int]] | None = None
                for index in allowed:
                    if index in chosen:
                        continue
                    filtered = _filter_indices(remaining, index, target_index)
                    if len(filtered) >= len(remaining):
                        continue
                    score = (
                        _prediction_count(filtered, artifact, phase),
                        len(filtered),
                        index,
                    )
                    if best is None or score < best[0]:
                        best = (score, index, filtered)
                if best is None:
                    break
                _, index, remaining = best
                chosen.append(index)

            if not chosen or _prediction_count(remaining, artifact, phase) != 1:
                raise EvidencePlanningError(
                    "unable to infer the mission outcome without direct-context evidence"
                )

        else:
            # Keep the evidence informative while preserving at least two different predictions
            # for the actual mission input. The one relevant probe therefore has information value.
            while len(chosen) < min(max_rows, 6):
                best: tuple[tuple[int, int, int], int, list[int]] | None = None
                for index in allowed:
                    if index in chosen:
                        continue
                    filtered = _filter_indices(remaining, index, target_index)
                    prediction_count = _prediction_count(filtered, artifact, phase)
                    if prediction_count <= 1 or len(filtered) >= len(remaining):
                        continue
                    score = (len(filtered), prediction_count, index)
                    if best is None or score < best[0]:
                        best = (score, index, filtered)
                if best is None:
                    break
                _, index, remaining = best
                chosen.append(index)
                if len(remaining) <= 8:
                    break

            if not chosen or _prediction_count(remaining, artifact, phase) <= 1:
                raise EvidencePlanningError(
                    "unable to preserve mission-relevant ambiguity with informative evidence"
                )

    experiments = tuple(pool[index] for index in chosen)
    return MissionEvidencePlan(
        experiments=experiments,
        candidate_count=len(remaining),
        prediction_count=_prediction_count(remaining, artifact, phase),
        direct_target_example=any(
            is_direct_context(experiment, artifact, phase) for experiment in experiments
        ),
    )


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


def evidence_csv(target: Effect, experiments: list[Experiment] | tuple[Experiment, ...]) -> str:
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


def _csv_rows(csv_text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(csv_text)))


def has_direct_context_csv(csv_text: str, artifact: Artifact, phase: int) -> bool:
    for row in _csv_rows(csv_text):
        if Shape(row["shape"]) == artifact.shape and int(row["phase"]) % 2 == phase % 2:
            return True
    return False


def candidates_matching_csv(csv_text: str, candidates: list[Effect]) -> list[Effect]:
    remaining = list(candidates)
    for row in _csv_rows(csv_text):
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
