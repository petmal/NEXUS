"""Exact categorical composition shared by generation and runtime."""

from functools import lru_cache
from itertools import permutations, product
from types import MappingProxyType

from nexus.ontology.graph import InvestigationGraph, Node

PERMUTATIONS = tuple(permutations(range(3)))
PRIMITIVES = MappingProxyType({"apply": lambda law, value: law[value]})


@lru_cache(maxsize=4)
def chain(depth: int) -> InvestigationGraph:
    if depth not in (0, 1, 2, 3):
        raise ValueError("unsupported categorical depth")
    return InvestigationGraph(
        ("x", *(f"law{i}" for i in range(depth))),
        tuple(
            Node(f"v{i}", "apply", (f"law{i}", "x" if i == 0 else f"v{i - 1}"))
            for i in range(depth)
        ),
        ("x" if depth == 0 else f"v{depth - 1}",),
    )


def prefix(laws: tuple, depth: int, value: int) -> int:
    return chain(depth).evaluate(
        {"x": value, **{f"law{i}": laws[i] for i in range(depth)}}, PRIMITIVES
    )[0]


def target(laws: tuple) -> tuple[int, ...]:
    return tuple(prefix(laws, len(laws), x) for x in range(3))


def reading(laws: tuple, stage: int, value: int, tuning: int | None) -> int | None:
    if stage and tuning != prefix(laws, stage, value):
        return None
    return laws[stage][value]


@lru_cache(maxsize=2)
def worlds(depth: int) -> tuple:
    if depth not in (2, 3):
        raise ValueError("unsupported categorical depth")
    return tuple(product(PERMUTATIONS, repeat=depth))
