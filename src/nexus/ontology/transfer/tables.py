"""Factored exact observations: retain correlation without 15 MB of byte rows."""

import logging
from dataclasses import dataclass
from functools import lru_cache
from time import perf_counter

from nexus.ontology.transfer.laws import PROGRAMS, QUERIES, components, signatures, targets

N = len(PROGRAMS)


@lru_cache(maxsize=1)
def companion_rows():
    # q never affects n2. Compile only the 1,728 upstream programs and share
    # their rows across three physical offsets and three reader offsets.
    return tuple(
        bytes(components(p, (1 - q[0], *q[1:]))[1] for q in QUERIES) for p in PROGRAMS[::3]
    )


@lru_cache(maxsize=3)
def partitions(kind):
    """Physical (0), raw survey (1), raw reference (2), with reader offset zero."""
    result = []
    if kind not in (0, 1, 2):
        raise ValueError("unknown observation channel")
    for query in range(len(QUERIES)):
        masks = [0, 0, 0]
        for i in range(N):
            value = signatures()[i][query] if kind != 2 else 0
            if kind:
                value += companion_rows()[i // 3][query]
            masks[value % 3] |= 1 << i
        result.append(tuple(masks))
    return tuple(result)


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
    blocks = 3 if coupled else 1
    if N * blocks > 16384 or N * blocks * len(QUERIES) * (2 if coupled else 1) > 16_000_000:
        raise ValueError("transfer grammar exceeds reviewed finite-audit limits")
    groups = {}
    for i, label in enumerate(targets()):
        groups[label] = groups.get(label, 0) | (1 << i)
    joint = {label: sum(mask << (N * b) for b in range(blocks)) for label, mask in groups.items()}
    by_world = tuple(joint[label] for _ in range(blocks) for label in targets())
    if coupled:
        outcomes = tuple(
            tuple(sum(p[(value - b) % 3] << (N * b) for b in range(3)) for value in range(3))
            for kind in (1, 2)
            for p in partitions(kind)
        )
    else:
        outcomes = partitions(0)
    result = Tables(outcomes, by_world, (1 << (N * blocks)) - 1)
    logging.getLogger("nexus.generation").info(
        "transfer_compile coupled=%s worlds=%s queries=%s seconds=%.6f",
        coupled,
        N * blocks,
        len(outcomes),
        perf_counter() - started,
    )
    return result
