"""Composed finite-memory circuits, exact behavioral acceptance, cached read tables."""

from collections import deque
from functools import lru_cache
from itertools import product
from types import MappingProxyType

from nexus.ontology.representation.schema import Investigation, Truth

PROGRAMS = tuple(
    product(range(2), range(3), range(2), range(2), range(2), (1, 2), (1, 2), (1, 2), range(2))
)
PROGRAM_INDEX = MappingProxyType({p: i for i, p in enumerate(PROGRAMS)})
QUERIES = tuple(word for n in range(1, 7) for word in product(range(3), repeat=n))
QUERY_INDEX = MappingProxyType({q: i for i, q in enumerate(QUERIES)})


def skeleton(program):
    return (*program[:5], program[8])


def advance(program, state, pulse):
    sources = (pulse, (pulse, state[0])[program[0]], (pulse, state[0], state[1])[program[1]])
    return tuple((program[5 + i] * sources[i] + program[2 + i] * state[i]) % 3 for i in range(3))


def display(program, state):
    return state[2] if program[8] == 0 else (state[0] + state[1] * state[2]) % 3


def read(program, word):
    state = (0, 0, 0)
    for pulse in word:
        state = advance(program, state, pulse)
    return (display(program, state),)


def read_world(world, query):
    return read(world.program, query)


def canonical_query(query):
    return tuple(query)


@lru_cache(maxsize=16384)
def equivalent(left, right):
    """Full future behavior, including histories longer than any legal reader word."""
    pending = deque([((0, 0, 0), (0, 0, 0))])
    visited = set(pending)
    while pending:
        a, b = pending.popleft()
        if display(left, a) != display(right, b):
            return False
        for pulse in range(3):
            pair = (advance(left, a, pulse), advance(right, b, pulse))
            if pair not in visited:
                visited.add(pair)
                pending.append(pair)
    return True


def accepted(world, build):
    return build in PROGRAM_INDEX and equivalent(world.program, build)


def selection(seed):
    return Truth(program=PROGRAMS[seed % len(PROGRAMS)])


def specification(world, theory, discovery):
    return Investigation(
        theory=theory,
        discovery=discovery,
        known=skeleton(world.program) if theory == 2 else None,
        resolved=world.program if theory == 0 else None,
    )


def valid_query(query):
    return 1 <= len(query) <= 6 and all(type(v) is int and v in (0, 1, 2) for v in query)


def validate_build(build):
    return build in PROGRAM_INDEX


def target(world):
    return world.program


@lru_cache(maxsize=1)
def tables():
    from nexus.ontology.discovery.inference import DecisionTables

    # Reuse prefix transitions rather than re-running every word from zero.
    rows = []
    for program in PROGRAMS:
        states = {(): (0, 0, 0)}
        row = []
        for word in QUERIES:
            state = advance(program, states[word[:-1]], word[-1])
            states[word] = state
            row.append(display(program, state))
        rows.append(bytes(row))
    rows = tuple(rows)
    by_signature = {}
    for i, row in enumerate(rows):
        by_signature[row] = by_signature.get(row, 0) | (1 << i)
    accepting = tuple(by_signature[row] for row in rows)
    partitions = tuple(
        tuple(sum(1 << i for i, row in enumerate(rows) if row[q] == v) for v in range(3))
        for q in range(len(QUERIES))
    )
    return DecisionTables(PROGRAMS, accepting), rows, partitions


def prior_mask(spec):
    return sum(
        1 << i
        for i, p in enumerate(PROGRAMS)
        if (spec.resolved is None or spec.resolved == p)
        and (spec.known is None or spec.known == skeleton(p))
    )
