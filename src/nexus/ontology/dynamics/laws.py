"""Exact simultaneous coupled dynamics; tables are compiled from these primitives."""

from functools import lru_cache
from itertools import product
from typing import NamedTuple

from nexus.ontology.dynamics.schema import Experiment, Point


class World(NamedTuple):
    a: int
    b: int
    initial_h: int
    initial_k: int
    delta: int
    wiring: int
    transition: int
    response: int


WORLDS = tuple(
    World(*values)
    for values in product(
        (1, 2), (1, 2), range(3), range(3), range(3), range(2), range(3), range(3)
    )
)
POINTS: tuple[Point, ...] = tuple((x, y, e) for x, y, e in product(range(2), repeat=3))
MISSION = tuple(
    Experiment(history=h, point=p)
    for h, p in (
        (((1, 0, 0), (0, 1, 0)), (1, 1, 1)),
        (((0, 1, 0), (1, 0, 0)), (1, 1, 1)),
        (((0, 0, 0), (1, 1, 1)), (1, 0, 1)),
        (((1, 1, 1), (0, 0, 0)), (1, 0, 1)),
        (((1, 0, 0), (0, 1, 0), (1, 1, 0)), (0, 1, 1)),
        (((0, 1, 0), (1, 0, 0), (1, 1, 0)), (0, 1, 1)),
        (((1, 0, 1), (0, 1, 1), (1, 1, 0)), (0, 0, 1)),
        (((1, 1, 1), (0, 0, 0), (1, 0, 1)), (1, 1, 0)),
    )
)


def primitive(
    a: int,
    b: int,
    wiring: int,
    transition: int,
    response: int,
    h: int,
    k: int,
    point: Point,
) -> tuple[int, int, int]:
    """Both successors use the old h,k. Updating h in place would change the law."""
    x, y, e = point
    u, v = (y, x) if wiring ^ (e == 1) else (x, y)
    next_states = (
        (h + a * u + b * k, k + b * v + u * h),
        (a * h + u * k + v, b * k + v * h + u),
        (h + a * u + k * v, k + b * v + h * u + u * v),
    )
    responses = (
        a * u + b * v + h * (u + e + 1) + k * (v + 1),
        (u + h) * (v + k + a) + b * e,
        u * v + a * h + b * k + h * k * (e + 1) + u * k,
    )
    nh, nk = next_states[transition]
    return nh % 3, nk % 3, responses[response] % 3


@lru_cache(maxsize=72)
def table(
    a: int, b: int, wiring: int, transition: int, response: int
) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        primitive(a, b, wiring, transition, response, h, k, point)
        for h, k in product(range(3), repeat=2)
        for point in POINTS
    )


def physical(world: World, experiment: Experiment) -> int:
    rows = table(world.a, world.b, world.wiring, world.transition, world.response)
    h, k = world.initial_h, world.initial_k
    for x, y, e in experiment.history:
        h, k, _ = rows[(h * 3 + k) * 8 + x * 4 + y * 2 + e]
    x, y, e = experiment.point
    return rows[(h * 3 + k) * 8 + x * 4 + y * 2 + e][2]


def reading(world: World, experiment: Experiment) -> int:
    value = physical(world, experiment) if experiment.instrument == "sensor" else 0
    return (value + world.delta * (experiment.point[2] + 1)) % 3


def measurable(experiment: Experiment) -> bool:
    return experiment.instrument == "reference" or experiment not in MISSION


@lru_cache(maxsize=4)
def experiments(max_history: int = 3) -> tuple[Experiment, ...]:
    if max_history not in range(4):
        raise ValueError("history bound must be 0..3")
    # Reference depends only on e: its two representatives cover every legal history/point.
    return (
        *(Experiment(instrument="reference", point=(0, 0, e)) for e in (0, 1)),
        *(
            item
            for n in range(max_history + 1)
            for history in product(POINTS, repeat=n)
            for point in POINTS
            if measurable(item := Experiment(history=history, point=point))
        ),
    )


@lru_cache(maxsize=1)
def targets() -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(physical(w, e) for e in MISSION) for w in WORLDS)
