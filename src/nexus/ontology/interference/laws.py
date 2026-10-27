"""Simultaneous two-register updates and bounded compiled transitions."""

from array import array
from functools import lru_cache

from nexus.ontology.interference.schema import COUNT, MODULUS, SIZE, Truth, Vector, topology

PLACES = tuple(MODULUS**index for index in range(COUNT))


def encode(vector: Vector) -> int:
    return sum(value * place for value, place in zip(vector, PLACES, strict=True))


def decode(state: int) -> Vector:
    return tuple(state // place % MODULUS for place in PLACES)


def step(world: Truth, options, vector: Vector, mode: int) -> Vector:
    if len(vector) != COUNT or any(type(v) is not int or not 0 <= v < MODULUS for v in vector):
        raise ValueError("expected six integer registers in 0..4")
    if type(mode) is not int or not 0 <= mode < COUNT:
        raise ValueError("unknown interference mode")
    coordinate = topology(options.coupling)[mode]
    if vector[coordinate.guard_register] != world.guards[mode]:
        return vector
    result = list(vector)
    result[mode] = (vector[mode] + world.gains[mode]) % MODULUS
    spill = coordinate.spill_register
    result[spill] = (vector[spill] + world.spill_gains[mode]) % MODULUS
    return tuple(result)


@lru_cache(maxsize=8)
def tables(world: Truth, coupling: str) -> tuple[array, ...]:
    result = []
    for mode, coordinate in enumerate(topology(coupling)):
        row = array("H")
        spill = coordinate.spill_register
        for state in range(SIZE):
            if state // PLACES[coordinate.guard_register] % MODULUS != world.guards[mode]:
                row.append(state)
                continue
            own, other = (state // PLACES[i] % MODULUS for i in (mode, spill))
            row.append(
                state
                + ((own + world.gains[mode]) % MODULUS - own) * PLACES[mode]
                + ((other + world.spill_gains[mode]) % MODULUS - other) * PLACES[spill]
            )
        result.append(row)
    return tuple(result)
