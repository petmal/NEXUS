"""Exact conservative feedback, all-history acceptance and cached laboratory rows."""

from collections import deque
from functools import lru_cache
from itertools import permutations, product
from types import MappingProxyType

from nexus.ontology.discovery.inference import DecisionTables
from nexus.ontology.coupled_memory.schema import Investigation, Truth

WIRINGS = tuple(permutations(range(3)))
INITIAL = (2, 1, 1, 0, 0)
PROGRAMS = tuple(product(range(6), range(2), range(2), range(2), (1, 2), (1, 2), range(2)))
PROGRAM_INDEX = MappingProxyType({p: i for i, p in enumerate(PROGRAMS)})
QUERIES = tuple(w for n in range(1, 5) for w in product(range(3), repeat=n))
QUERY_INDEX = MappingProxyType({q: i for i, q in enumerate(QUERIES)})


def advance(program, state, pulse):
    q = list(state[:3])
    h, k = state[3:]
    wiring, rate, feedback, recurrence = program[:4]
    source = WIRINGS[wiring][pulse]
    destination = WIRINGS[wiring][(pulse + 1) % 3]
    old_destination = q[destination]
    flow = min(q[source], 1 + (k + (1 + rate) * old_destination + feedback * h) % 2)
    q[source] -= flow
    q[destination] += flow
    return (*q, (h + flow + recurrence * old_destination) % 3, (k + h + feedback * flow) % 3)


def signal(program, state):
    q0, q1, _q2, h, k = state
    return program[4] * q0 + q1 + program[5] * h + k + program[6] * q0 * k


def display(program, state):
    return signal(program, state) % 3


def read(program, word):
    state = INITIAL
    for pulse in word:
        state = advance(program, state, pulse)
    return (display(program, state),)


def read_world(world, query):
    return read(world.program, query)


def canonical_query(query):
    return tuple(query)


@lru_cache(maxsize=16384)
def equivalent(left, right):
    """Bisimulation from initial states; no query-horizon approximation."""
    pending = deque([(INITIAL, INITIAL)])
    seen = set(pending)
    while pending:
        a, b = pending.popleft()
        if display(left, a) != display(right, b):
            return False
        for pulse in range(3):
            pair = advance(left, a, pulse), advance(right, b, pulse)
            if pair not in seen:
                seen.add(pair)
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
        known=world.program[:4] if theory == 2 else None,
        resolved=world.program if theory == 0 else None,
    )


def valid_query(query):
    return 1 <= len(query) <= 4 and all(type(v) is int and v in (0, 1, 2) for v in query)


def validate_build(build):
    return build in PROGRAM_INDEX


def target(world):
    return world.program


def prior_mask(spec):
    return sum(
        1 << i
        for i, p in enumerate(PROGRAMS)
        if (spec.resolved is None or spec.resolved == p)
        and (spec.known is None or spec.known == p[:4])
    )


@lru_cache(maxsize=1)
def tables():
    rows = []
    for program in PROGRAMS:
        states = {(): INITIAL}
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
    # Offline independent partition refinement proves these finite signatures
    # coincide with all-history equivalence. Runtime finish still uses BFS.
    accepting = tuple(by_signature[row] for row in rows)
    parts = tuple(
        tuple(sum(1 << i for i, row in enumerate(rows) if row[q] == v) for v in range(3))
        for q in range(len(QUERIES))
    )
    return DecisionTables(PROGRAMS, accepting), rows, parts
