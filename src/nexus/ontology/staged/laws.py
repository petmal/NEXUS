"""Composed finite laws and small immutable, truth-independent tables."""

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from types import MappingProxyType

from nexus.ontology.staged.schema import Mechanism, Truth

MECHANISMS = tuple(Mechanism(shift=k, exponent=e) for k, e in product(range(3), (1, 2)))
WORLDS = tuple(Truth(mechanisms=m) for m in product(MECHANISMS, repeat=3))
WORLD_INDEX = MappingProxyType({world: i for i, world in enumerate(WORLDS)})
QUERIES = tuple(product(range(3), repeat=3))  # stage, carrier, specimen tag


def response(mechanism: Mechanism, tag: int) -> int:
    return pow((tag + mechanism.shift) % 3, mechanism.exponent, 3)


def route(mechanism: Mechanism) -> int:
    return (mechanism.shift + mechanism.exponent - 1) % 3


def reading(world: Truth, stage: int, carrier: int, tag: int, linked: bool) -> int:
    active = route(world.mechanisms[stage - 1]) if stage and linked else 0
    return response(world.mechanisms[stage], tag) if carrier == active else 0


def remaining(world: Truth, tag: int, doses: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        (
            response(mechanism, tag)
            - doses[i]
            - (route(world.mechanisms[i - 1]) * doses[i - 1] if i else 0)
        )
        % 3
        for i, mechanism in enumerate(world.mechanisms)
    )


def repair(world: Truth) -> tuple[tuple[int, ...], ...]:
    rows = []
    for tag in range(3):
        doses = []
        for i, mechanism in enumerate(world.mechanisms):
            coupling = route(world.mechanisms[i - 1]) * doses[i - 1] if i else 0
            doses.append((response(mechanism, tag) - coupling) % 3)
        rows.append(tuple(doses))
    return tuple(rows)


def decision(world: Truth) -> tuple[int, ...]:
    return tuple(value for row in repair(world) for value in row)


@dataclass(frozen=True)
class Tables:
    rows: tuple[bytes, ...]  # world-major observation rows, including inactive contexts
    partitions: tuple[tuple[int, ...], ...]
    decisions: tuple[tuple[int, ...], ...]
    accepting: MappingProxyType


@lru_cache(maxsize=2)
def tables(linked: bool) -> Tables:
    rows = tuple(bytes(reading(w, *q, linked) for q in QUERIES) for w in WORLDS)
    partitions = tuple(
        tuple(sum(1 << i for i, row in enumerate(rows) if row[q] == value) for value in range(3))
        for q in range(len(QUERIES))
    )
    decisions = tuple(map(decision, WORLDS))
    accepting = {}
    for i, d in enumerate(decisions):
        accepting[d] = accepting.get(d, 0) | (1 << i)
    return Tables(rows, partitions, decisions, MappingProxyType(accepting))


def prior_mask(spec) -> int:
    if spec.resolved is not None:
        return 1 << WORLD_INDEX[spec.resolved]
    return sum(
        1 << i
        for i, w in enumerate(WORLDS)
        if spec.known_exponents is None
        or tuple(m.exponent for m in w.mechanisms) == spec.known_exponents
    )
