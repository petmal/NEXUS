"""Finite compositional transitions. All shared tables contain the entire prior."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from types import MappingProxyType

from nexus.ontology.history.schema import MAX_HISTORY, Truth

PULSES = ("vek", "nol", "tor", "sen")
READERS = ("surface", "h-scope", "k-scope")
LAWS = tuple(product(range(4), repeat=4))
STATES = tuple(product(range(3), repeat=4))
WORLDS = tuple(Truth(gates=g, a=a, b=b) for g in LAWS for a, b in product((1, 2), repeat=2))
WORLD_INDEX = MappingProxyType({w: i for i, w in enumerate(WORLDS)})
STATE_INDEX = MappingProxyType({s: i for i, s in enumerate(STATES)})


def pulse(gates: tuple[int, ...], state: tuple[int, ...], mode: int) -> tuple[int, ...]:
    h, k, x, _y = state
    u = (k, h, h + k, k + x)[mode]
    c, s = 1 + gates[mode] // 2, gates[mode] % 2
    values = list(state)
    values[mode] = (values[mode] + c * (1 + (u + s) ** 2)) % 3
    if mode == 2:
        values[1] = (values[1] + values[2]) % 3
    elif mode == 3:
        values[0] = (values[0] + values[3]) % 3
    return tuple(values)


def state_for(world: Truth, history: tuple[int, ...]) -> tuple[int, ...]:
    state = (0, 0, 0, 0)
    for mode in history:
        state = pulse(world.gates, state, mode)
    return state


def observed(world: Truth, history: tuple[int, ...], channel: int = 0) -> tuple[int, int]:
    state = state_for(world, history)
    if channel:
        h, k, x, y = state
        state = (world.a if channel == 1 else h, world.b if channel == 2 else k, x, y)
        state = pulse(world.gates, pulse(world.gates, state, 2), 3)
    return state[2], state[3]


def accepted(world: Truth, history: tuple[int, ...] | None) -> bool:
    return history is not None and state_for(world, history) == (world.a, 2 * world.b % 3, 1, 2)


def word_index(history: tuple[int, ...]) -> int:
    index = 0
    for mode in history:
        index = 4 * index + mode + 1
    return index


@lru_cache(maxsize=1)
def words() -> tuple[tuple[int, ...], ...]:
    return tuple(word for n in range(MAX_HISTORY + 1) for word in product(range(4), repeat=n))


@lru_cache(maxsize=1)
def transitions() -> tuple[tuple[bytes, ...], ...]:
    return tuple(
        tuple(bytes(STATE_INDEX[pulse(g, s, mode)] for s in STATES) for mode in range(4))
        for g in LAWS
    )


@lru_cache(maxsize=256)
def shortest_paths(law: int):
    paths = {0: ()}
    todo = deque([0])
    table = transitions()[law]
    while todo:
        state = todo.popleft()
        for mode in range(4):
            nxt = table[mode][state]
            if nxt not in paths:
                paths[nxt] = (*paths[state], mode)
                todo.append(nxt)
    return MappingProxyType(paths)


def shortest(world: Truth) -> tuple[int, ...]:
    return shortest_paths(WORLD_INDEX[world] // 4)[STATE_INDEX[(world.a, 2 * world.b % 3, 1, 2)]]


@dataclass(frozen=True)
class DecisionTable:
    accepting: tuple[int, ...]
    winning: tuple[int, ...]


@lru_cache(maxsize=1)
def decisions() -> DecisionTable:
    """Exact all-word winning sets; ~12 MiB bitsets, no transcript/world products.

    Compile per-law byte state arrays and discard each immediately. Runtime never
    materializes 87,381*1,024 scalar world-history objects.
    """
    import logging
    from time import perf_counter

    start = perf_counter()
    count = len(words())
    accepting = [0] * count
    winning = []
    goal_orientation = {
        STATE_INDEX[(a, 2 * b % 3, 1, 2)]: i for i, (a, b) in enumerate(product((1, 2), repeat=2))
    }
    for law, table in enumerate(transitions()):
        states = bytearray(count)
        bits = [bytearray((count + 7) // 8) for _ in range(4)]
        world_bits = tuple(1 << (law * 4 + i) for i in range(4))
        for index in range(1, count):
            parent, mode = divmod(index - 1, 4)
            state = table[mode][states[parent]]
            states[index] = state
            orientation = goal_orientation.get(state)
            if orientation is not None:
                accepting[index] |= world_bits[orientation]
                bits[orientation][index >> 3] |= 1 << (index & 7)
        winning.extend(int.from_bytes(row, "little") for row in bits)
    result = DecisionTable(tuple(accepting), tuple(winning))
    logging.getLogger("nexus.generation").info(
        "history_decisions worlds=%s histories=%s transition_bytes=%s seconds=%.6f",
        len(WORLDS),
        count,
        256 * 81 * 4,
        perf_counter() - start,
    )
    return result
