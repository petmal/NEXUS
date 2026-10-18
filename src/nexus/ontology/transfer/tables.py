"""Factored exact observations: retain correlation without 15 MB of byte rows."""

import logging
from dataclasses import dataclass
from functools import lru_cache
from time import perf_counter

from nexus.ontology.transfer.laws import PROGRAMS, QUERIES
from nexus.ontology.transfer.observations import load as load_observations
from nexus.ontology.transfer.reference import load as load_reference

N = len(PROGRAMS)


def partitions(kind):
    """Physical (0), raw survey (1), raw reference (2), with reader offset zero."""
    if kind not in (0, 1, 2):
        raise ValueError("unknown observation channel")
    return load_observations()[kind]


@dataclass(frozen=True)
class Tables:
    outcomes: tuple[tuple[int, ...], ...]
    target_by_world: tuple[int, ...]
    full: int

    def common(self, mask):
        if not mask:
            raise ValueError("observations contradict public prior")
        target = self.target_by_world[(mask & -mask).bit_length() - 1]
        return mask & target == mask


@lru_cache(maxsize=2)
def compile_tables(coupled):
    started = perf_counter()
    result = assemble_tables(coupled, load_reference()["targets"])
    logging.getLogger("nexus.generation").info(
        "transfer_compile coupled=%s worlds=%s queries=%s seconds=%.6f source=verified_asset",
        coupled,
        len(result.target_by_world),
        len(result.outcomes),
        perf_counter() - started,
    )
    return result


def assemble_tables(coupled, labels):
    """Assemble checked partitions with supplied labels, also used by offline proof.

    The reference compiler supplies independently evaluated labels so rebuilding a
    missing/stale policy never depends on loading that same policy artifact.
    """
    blocks = 3 if coupled else 1
    if N * blocks > 16384 or N * blocks * len(QUERIES) * (2 if coupled else 1) > 16_000_000:
        raise ValueError("transfer grammar exceeds reviewed finite-audit limits")
    groups = {}
    for i, label in enumerate(labels):
        groups[label] = groups.get(label, 0) | (1 << i)
    joint = {label: sum(mask << (N * b) for b in range(blocks)) for label, mask in groups.items()}
    by_world = tuple(joint[label] for _ in range(blocks) for label in labels)
    if coupled:
        outcomes = tuple(
            tuple(sum(p[(value - b) % 3] << (N * b) for b in range(3)) for value in range(3))
            for kind in (1, 2)
            for p in partitions(kind)
        )
    else:
        outcomes = partitions(0)
    return Tables(outcomes, by_world, (1 << (N * blocks)) - 1)
