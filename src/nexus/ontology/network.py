"""Immutable apparatus definitions shared by the two finite-field network families.

These declarations contain public coordinates and controls only. Law evaluation,
priors and qualification remain in their respective engine/generator modules.
Changing a published definition changes the world contract: version the family
and requalify its witnesses rather than silently changing existing episodes.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Literal

type NetworkFamily = Literal["coupled-network-v1", "resonant-network-v1"]
type Point = tuple[int, int]

BENCH: tuple[Point, ...] = (
    (0, 0),
    (0, 1),
    (1, 0),
    (0, 2),
    (2, 0),
    (1, 1),
    (1, 2),
    (2, 1),
    (2, 2),
    (1, 3),
    (3, 1),
    (3, 2),
)
FIELD: tuple[Point, ...] = ((4, 1), (1, 4), (4, 3), (3, 4))
RESONANT_BENCH: tuple[Point, ...] = tuple(
    (x, y) for x, y in product(range(7), repeat=2) if (x, y) not in FIELD
)


@dataclass(frozen=True)
class NetworkApparatus:
    family: NetworkFamily
    bench: tuple[Point, ...]
    instruments: tuple[str, ...]
    initial_settings: tuple[tuple[str, tuple[int, ...]], ...] = ()
    preparations: tuple[str, ...] = ("shift", "shear")

    @property
    def machines(self) -> tuple[str, ...]:
        # Preserve the published ordering, including the later-added calibrator.
        return (self.instruments[0], *self.preparations, "controller", *self.instruments[1:])


COUPLED = NetworkApparatus("coupled-network-v1", BENCH, ("meter",))
RESONANT = NetworkApparatus(
    "resonant-network-v1", RESONANT_BENCH, ("meter", "calibrator"), (("meter", (0,)),)
)


def network_apparatus(family: NetworkFamily) -> NetworkApparatus:
    if family == COUPLED.family:
        return COUPLED
    if family == RESONANT.family:
        return RESONANT
    raise ValueError(f"unknown network family: {family}")
