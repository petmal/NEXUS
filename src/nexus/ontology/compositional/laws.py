"""Trusted bounded grammar: independent local mechanisms, shared graph and repair.

Every solvable grammar world is admitted. Equivalent worlds retain their mass;
acceptance is a set of repairs, not equality with a private preferred vector.
"""

from functools import lru_cache
from itertools import product
from typing import NamedTuple


class World(NamedTuple):
    topology: int
    f: int
    g: int
    h: int
    changed: int
    replacement: int


POINTS = tuple(product(range(3), repeat=3))
TRIMS = tuple(product(range(3), repeat=2))
REPAIRS = tuple(product(range(3), repeat=4))
QUERIES = tuple(product(range(2), POINTS, TRIMS))
MISSION = ((0, (2, 0, 0)), (0, (1, 1, 1)), (1, (2, 1, 0)), (1, (1, 0, 2)))


def gate(operation, left, right):
    if operation == 0:
        return (left + right) % 3
    if operation == 1:
        return (left - right) % 3
    if operation == 2:
        return left * right % 3
    if operation == 3:
        return (left * left + right) % 3
    raise ValueError("unknown primitive")


def response(world, mode, point, trims):
    operators = [world.f, world.g, world.h]
    if mode:
        operators[world.changed] = world.replacement
    x, y, z = point
    a, b = trims
    n1 = (gate(operators[0], x, y) + a) % 3
    n2 = (gate(operators[1], y if world.topology == 1 else n1, z) + b) % 3
    return gate(operators[2], n2, x) if world.topology == 0 else gate(operators[2], n1, n2)


def reading(world, settings):
    mode, x, y, z, a, b, c, d = settings
    return (response(world, mode, (x, y, z), (a, b)) + c + mode * d) % 3


def accepted(world, doses):
    if doses is None:
        return False
    a, b, c, d = doses
    return all(
        (response(world, mode, point, (a, b)) + c + mode * d) % 3 == 0 for mode, point in MISSION
    )


@lru_cache(maxsize=1)
def population():
    result = []
    for values in product(range(3), range(4), range(4), range(4), range(3), range(4)):
        world = World(*values)
        if world.replacement == (world.f, world.g, world.h)[world.changed]:
            continue
        winning = 0
        # Two output offsets can solve four constraints only when each pair agrees.
        for a, b in TRIMS:
            r0, r1, r2, r3 = (response(world, mode, point, (a, b)) for mode, point in MISSION)
            if r0 == r1 and r2 == r3:
                repair = (a, b, -r0 % 3, (r0 - r2) % 3)
                winning |= 1 << REPAIRS.index(repair)
        if winning:
            result.append((world, winning))
    return tuple(result)


def world_for_seed(seed):
    return population()[seed % len(population())][0]


@lru_cache(maxsize=1)
def rows():
    return tuple(bytes(response(world, *query) for world, _ in population()) for query in QUERIES)


@lru_cache(maxsize=1)
def winning_masks():
    return tuple(
        sum(1 << i for i, (_, wins) in enumerate(population()) if wins >> repair & 1)
        for repair in range(len(REPAIRS))
    )
