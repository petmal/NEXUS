"""Trusted exact primitives compose wiring, state transition and response graphs."""

from functools import lru_cache
from itertools import product
from typing import NamedTuple

from nexus.ontology.causal.schema import Experiment
from nexus.ontology.graph import InvestigationGraph, Node


class World(NamedTuple):
    a: int
    b: int
    delta: int
    initial: int
    wiring: int
    transition: int
    response: int


WORLDS = tuple(
    World(*v) for v in product((1, 2), (1, 2), range(3), range(3), range(2), range(3), range(3))
)
MISSION = tuple(
    Experiment(history=h, point=p)
    for h, p in (
        (((2, 0, 0), (0, 1, 1)), (2, 1, 2)),
        (((0, 2, 1), (1, 0, 0)), (1, 2, 1)),
        (((1, 1, 0), (2, 1, 2)), (0, 2, 2)),
        (((2, 1, 2), (1, 1, 0)), (0, 2, 2)),
        (((1, 2, 0),), (2, 0, 1)),
        (((2, 2, 1), (0, 1, 2)), (1, 1, 2)),
    )
)
POINTS = tuple((x, y, e) for x, y, e in product(range(3), repeat=3))
PULSES = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 1))
WITNESS_EXPERIMENTS = (
    *(
        Experiment(history=h, point=p)
        for h in ((), *((p,) for p in PULSES), *product(PULSES, repeat=2))
        for p in POINTS
        if Experiment(history=h, point=p) not in MISSION
    ),
    Experiment(instrument="reference"),
)

PRIMITIVES = {
    "add": lambda x, y: (x + y) % 3,
    "mul": lambda x, y: x * y % 3,
    "route": lambda x, y, e, p: y if p ^ (e == 1) else x,
}


@lru_cache(maxsize=18)
def graphs(wiring: int, transition: int, response: int):
    common = (Node("u", "route", ("x", "y", "e", "p")), Node("v", "route", ("y", "x", "e", "p")))
    transitions = (
        (
            Node("au", "mul", ("a", "u")),
            Node("bv", "mul", ("b", "v")),
            Node("sum", "add", ("au", "bv")),
            Node("next", "add", ("h", "sum")),
        ),
        (
            Node("ah", "mul", ("a", "h")),
            Node("bv", "mul", ("b", "v")),
            Node("sum", "add", ("u", "bv")),
            Node("next", "add", ("ah", "sum")),
        ),
        (
            Node("uv", "mul", ("u", "v")),
            Node("sum", "add", ("u", "v")),
            Node("asum", "mul", ("a", "sum")),
            Node("buv", "mul", ("b", "uv")),
            Node("inc", "add", ("asum", "buv")),
            Node("next", "add", ("h", "inc")),
        ),
    )
    responses = (
        (
            Node("au", "mul", ("a", "u")),
            Node("bv", "mul", ("b", "v")),
            Node("ue", "add", ("u", "e")),
            Node("ue1", "add", ("ue", "one")),
            Node("hu", "mul", ("h", "ue1")),
            Node("sum", "add", ("au", "bv")),
            Node("out", "add", ("sum", "hu")),
        ),
        (
            Node("uh", "add", ("u", "h")),
            Node("va", "add", ("v", "a")),
            Node("prod", "mul", ("uh", "va")),
            Node("be", "mul", ("b", "e")),
            Node("out", "add", ("prod", "be")),
        ),
        (
            Node("uv", "mul", ("u", "v")),
            Node("ah", "mul", ("a", "h")),
            Node("ue", "add", ("u", "e")),
            Node("bue", "mul", ("b", "ue")),
            Node("sum", "add", ("uv", "ah")),
            Node("out", "add", ("sum", "bue")),
        ),
    )
    inputs = ("x", "y", "e", "p", "a", "b", "h", "one")
    return (
        InvestigationGraph(inputs, common + transitions[transition], ("next",)),
        InvestigationGraph(inputs, common + responses[response], ("out",)),
    )


@lru_cache(maxsize=72)
def transition_response_tables(a: int, b: int, wiring: int, transition: int, response: int):
    """Compile the finite graph once per law; never cache mutable specimen state.

    Every mode/point combination is present, so arbitrary legal histories use the
    same exact interpreter semantics as the witness subset. Tables are immutable.
    """
    tg, rg = graphs(wiring, transition, response)
    rows = []
    for mode in range(3):
        for x, y, e in POINTS:
            values = {"p": wiring, "a": a, "b": b, "h": mode, "one": 1, "x": x, "y": y, "e": e}
            rows.append((tg.evaluate(values, PRIMITIVES)[0], rg.evaluate(values, PRIMITIVES)[0]))
    return tuple(rows)


def physical(world: World, experiment: Experiment) -> int:
    table = transition_response_tables(
        world.a, world.b, world.wiring, world.transition, world.response
    )
    mode = world.initial
    for x, y, e in experiment.history:
        mode = table[mode * 27 + x * 9 + y * 3 + e][0]
    x, y, e = experiment.point
    return table[mode * 27 + x * 9 + y * 3 + e][1]


def reading(world: World, experiment: Experiment) -> int:
    offset = world.delta * (experiment.point[2] + 1)
    return (offset + (physical(world, experiment) if experiment.instrument == "sensor" else 0)) % 3


def measurable(experiment: Experiment) -> bool:
    return experiment.instrument == "reference" or experiment not in MISSION


@lru_cache(maxsize=1)
def targets() -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(physical(world, experiment) for experiment in MISSION) for world in WORLDS)
