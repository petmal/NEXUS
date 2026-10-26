"""One selected law's integer transitions; no latent prior and no collapse."""

from array import array
from collections import deque
from functools import lru_cache

from nexus.ontology.coordination.schema import GenerationOptions, Truth, Vector, topology


def encode(vector: Vector) -> int:
    return sum(value * 3**index for index, value in enumerate(vector))


def decode(state: int, count: int) -> Vector:
    return tuple(state // 3**index % 3 for index in range(count))


def step(world: Truth, options: GenerationOptions, vector: Vector, mode: int) -> Vector:
    if len(vector) != options.count or len(world.gains) != options.count:
        raise ValueError("law and register dimensions differ")
    if type(mode) is not int or not 0 <= mode < options.count:
        raise ValueError("unknown coordinate mode")
    coordinate = topology(options)[mode]
    cross = 0 if coordinate.cross_first is None else vector[coordinate.cross_first]
    updated = (
        vector[mode]
        + world.gains[mode] * (1 + vector[coordinate.local_next] ** world.powers[mode] + cross)
    ) % 3
    return (*vector[:mode], updated, *vector[mode + 1 :])


@lru_cache(maxsize=32)
def tables(world: Truth, options: GenerationOptions) -> tuple[array, ...]:
    """Only the admitted selected law is compiled (at most nine by 19,683 entries)."""
    if len(world.gains) != options.count:
        raise ValueError("law and register dimensions differ")
    place = tuple(3**index for index in range(options.count))
    result = []
    for mode, coordinate in enumerate(topology(options)):
        row = array("H")
        for state in range(3**options.count):
            value = state // place[mode] % 3
            local = state // place[coordinate.local_next] % 3
            cross = (
                0 if coordinate.cross_first is None else state // place[coordinate.cross_first] % 3
            )
            after = (value + world.gains[mode] * (1 + local ** world.powers[mode] + cross)) % 3
            row.append(state + (after - value) * place[mode])
        result.append(row)
    return tuple(result)


def distances(world: Truth, options: GenerationOptions) -> list[int]:
    transitions = tables(world, options)
    distance = [-1] * (3**options.count)
    distance[0] = 0
    queue = deque([0])
    while queue:
        state = queue.popleft()
        for row in transitions:
            after = row[state]
            if distance[after] < 0:
                distance[after] = distance[state] + 1
                queue.append(after)
    return distance
