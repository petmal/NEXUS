"""Public joint inference; cached immutable tables, session-owned belief masks."""

import logging
from functools import lru_cache
from time import perf_counter

from nexus.ontology.dynamics.laws import WORLDS, experiments, reading, targets
from nexus.ontology.dynamics.schema import Experiment, Investigation


def indices(mask: int):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


@lru_cache(maxsize=8192)
def partitions(experiment: Experiment) -> tuple[int, int, int]:
    masks = [0, 0, 0]
    for i, world in enumerate(WORLDS):
        masks[reading(world, experiment)] |= 1 << i
    return masks[0], masks[1], masks[2]


@lru_cache(maxsize=1)
def witness_rows():
    started = perf_counter()
    # A subset is sufficient for a constructive upper bound, never a lower bound.
    rows = tuple(partitions(e) for e in experiments(2))
    logging.getLogger("nexus.generation").info(
        "dynamics_compile worlds=%s witness_queries=%s seconds=%.6f",
        len(WORLDS),
        len(rows),
        perf_counter() - started,
    )
    return rows


@lru_cache(maxsize=16384)
def target_set(mask: int) -> frozenset[tuple[int, ...]]:
    return frozenset(targets()[i] for i in indices(mask))


def initial_mask(spec: Investigation) -> int:
    return sum(
        1 << i
        for i, target in enumerate(targets())
        if spec.resolved is None or target == spec.resolved
    )


@lru_cache(maxsize=16384)
def choose(mask: int) -> int | None:
    if not mask:
        raise ValueError("observations contradict the disclosed dynamics prior")
    if len(target_set(mask)) == 1:
        return None
    rows = witness_rows()
    best = min(
        range(len(rows)),
        key=lambda j: (
            max((mask & m).bit_count() for m in rows[j]),
            sum((mask & m).bit_count() ** 2 for m in rows[j]),
            len(experiments(2)[j].history),
            j,
        ),
    )
    if any(mask & m == mask for m in rows[best]):
        raise ValueError("witness queries do not identify the mission")
    return best


def experiment_cost(experiment: Experiment) -> int:
    if experiment.instrument == "reference":
        return 2 if experiment.point == (0, 0, 0) else 4
    return 4 + 3 * len(experiment.history)


@lru_cache(maxsize=16384)
def policy_bound(mask: int) -> tuple[int, int]:
    selected = choose(mask)
    if selected is None:
        return 0, 0
    children = [policy_bound(mask & m) for m in witness_rows()[selected] if mask & m]
    # Take all specimens before moving: separately maximize takes and experiment work.
    return 1 + max(d for d, _ in children), experiment_cost(experiments(2)[selected]) - 1 + max(
        w for _, w in children
    )


class DynamicsBelief:
    def __init__(self, spec: Investigation):
        self.mask = initial_mask(spec)

    def counts(self) -> tuple[int, int]:
        return self.mask.bit_count(), len(target_set(self.mask))

    def observe(self, measurement):
        sample = measurement.sample
        if sample["reading"] is not None:
            experiment = Experiment(
                instrument=measurement.instrument, history=sample["history"], point=sample["point"]
            )
            self.mask &= partitions(experiment)[sample["reading"]]

    def exclude_target(self, target):
        self.mask &= ~sum(1 << i for i in indices(self.mask) if targets()[i] == target)
