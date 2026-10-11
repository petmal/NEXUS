"""Exact joint posterior and cached public-information witness, without minimax claims."""

import logging
from functools import lru_cache
from time import perf_counter

from nexus.ontology.causal.laws import WITNESS_EXPERIMENTS, WORLDS, reading, targets
from nexus.ontology.causal.schema import Experiment, Investigation, Reading


def indices(mask: int):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


@lru_cache(maxsize=4096)
def partitions(experiment: Experiment) -> tuple[int, int, int]:
    masks = [0, 0, 0]
    for i, world in enumerate(WORLDS):
        masks[reading(world, experiment)] |= 1 << i
    return masks[0], masks[1], masks[2]


@lru_cache(maxsize=1)
def witness_rows():
    start = perf_counter()
    rows = tuple(partitions(e) for e in WITNESS_EXPERIMENTS)
    logging.getLogger("nexus.generation").info(
        "causal_compile worlds=%s experiments=%s seconds=%.6f",
        len(WORLDS),
        len(rows),
        perf_counter() - start,
    )
    return rows


def initial_mask(spec: Investigation) -> int:
    mask = sum(
        1 << i
        for i, w in enumerate(WORLDS)
        if all(getattr(w, k) == v for k, v in spec.known.items())
        and (spec.resolved is None or targets()[i] == spec.resolved)
    )
    for observation in spec.supplied:
        mask &= partitions(observation.experiment)[observation.value]
    return mask


@lru_cache(maxsize=8192)
def target_set(mask: int) -> frozenset[tuple[int, ...]]:
    return frozenset(targets()[i] for i in indices(mask))


@lru_cache(maxsize=8192)
def choose(mask: int, allow_preparation: bool = True) -> int | None:
    if len(target_set(mask)) <= 1:
        return None
    rows = witness_rows()
    eligible = (j for j, e in enumerate(WITNESS_EXPERIMENTS) if allow_preparation or not e.history)
    best = min(
        eligible,
        key=lambda j: (
            max((mask & m).bit_count() for m in rows[j]),
            sum((mask & m).bit_count() ** 2 for m in rows[j]),
            j,
        ),
    )
    if any(mask & m == mask for m in rows[best]):
        raise ValueError("witness experiments cannot identify mission")
    return best


def experiment_cost(experiment: Experiment) -> int:
    # Always use a fresh carried specimen; take is counted here, even when preloaded.
    return 2 if experiment.instrument == "reference" else 4 + 3 * len(experiment.history)


@lru_cache(maxsize=8192)
def policy_bound(mask: int, allow_preparation: bool = True) -> tuple[int, int]:
    selected = choose(mask, allow_preparation)
    if selected is None:
        if not mask:
            raise ValueError("empty public posterior")
        return 0, 0
    experiment = WITNESS_EXPERIMENTS[selected]
    children = tuple(
        policy_bound(mask & m, allow_preparation) for m in witness_rows()[selected] if mask & m
    )
    return (
        1 + max(c[0] for c in children),
        (experiment_cost(experiment) - 1) + max(c[1] for c in children),
    )


def evidence_for(spec: Investigation, world_index: int) -> tuple[Reading, ...]:
    mask = initial_mask(spec)
    evidence = []
    while (selected := choose(mask)) is not None:
        experiment = WITNESS_EXPERIMENTS[selected]
        value = reading(WORLDS[world_index], experiment)
        evidence.append(Reading(experiment=experiment, value=value))
        mask &= witness_rows()[selected][value]
    return tuple(evidence)


class CausalBelief:
    def __init__(self, spec: Investigation):
        self.mask = initial_mask(spec)

    def counts(self) -> tuple[int, int]:
        return self.mask.bit_count(), len(target_set(self.mask))

    def observe(self, measurement):
        sample = measurement.sample
        experiment = Experiment(
            instrument=measurement.instrument, history=sample["history"], point=sample["point"]
        )
        self.mask &= partitions(experiment)[sample["reading"]]

    def exclude_target(self, target):
        self.mask &= ~sum(1 << i for i in indices(self.mask) if targets()[i] == target)
