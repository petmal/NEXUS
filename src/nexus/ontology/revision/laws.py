"""Conservative primitive composition; complete behavioral classes, not fitted rows."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from types import MappingProxyType

from nexus.ontology.revision.schema import GenerationOptions, Investigation, Truth
from nexus.solver.finite_machine import FiniteMachine

INITIAL = (2, 1, 1, 1)
EDGES = tuple((a, b) for a in range(4) for b in range(4) if a != b)
STATES = tuple(q for q in product(range(6), repeat=4) if sum(q) == 5)
STATE_INDEX = MappingProxyType({q: i for i, q in enumerate(STATES)})
PROGRAMS = tuple(product(range(12), repeat=4))
PROGRAM_INDEX = MappingProxyType({p: i for i, p in enumerate(PROGRAMS)})
QUERIES = tuple(w for n in range(1, 9) for w in product(range(2), repeat=n))
QUERY_INDEX = MappingProxyType({q: i for i, q in enumerate(QUERIES)})


def transfer(state, edge):
    source, destination = EDGES[edge]
    amount = min(state[source], 1 + state[destination] % 2)
    result = list(state)
    result[source] -= amount
    result[destination] += amount
    return tuple(result)


def advance(program, state, mode):
    first, second = program[2 * mode : 2 * mode + 2]
    return transfer(transfer(state, first), second)


def display(state):
    return state[0] % 3


def read(program, word):
    state = INITIAL
    for mode in word:
        state = advance(program, state, mode)
    return (display(state),)


@lru_cache(maxsize=1)
def primitive_tables():
    single = tuple(tuple(STATE_INDEX[transfer(q, edge)] for q in STATES) for edge in range(12))
    return tuple(
        tuple(single[b][single[a][s]] for s in range(len(STATES)))
        for a, b in product(range(12), repeat=2)
    )


def machine(program):
    table = primitive_tables()
    return FiniteMachine(
        tuple(display(s) for s in STATES),
        (table[12 * program[0] + program[1]], table[12 * program[2] + program[3]]),
        STATE_INDEX[INITIAL],
    )


@dataclass(frozen=True)
class CompiledPrior:
    representatives: tuple[tuple[int, ...], ...]
    signatures: tuple[tuple[tuple[int, ...], ...], ...]
    program_classes: tuple[int, ...]
    rows: tuple[bytes, ...]
    partitions: tuple[tuple[int, ...], ...]


@lru_cache(maxsize=1)
def compiled():
    classes = {}
    representatives = []
    class_ids = []
    for program in PROGRAMS:
        signature = machine(program).signature()
        if signature not in classes:
            classes[signature] = len(classes)
            representatives.append(program)
        class_ids.append(classes[signature])
    rows = []
    # Compile only minimal observable behaviors, retaining the full construction
    # grammar for acceptance. Equivalent hidden wirings need no repeated inference.
    for program in representatives:
        m = machine(program)
        states = [m.initial]
        for node in range(1, len(QUERIES) + 1):
            states.append(m.transitions[(node - 1) % 2][states[(node - 1) // 2]])
        rows.append(bytes(m.outputs[s] for s in states[1:]))
    rows = tuple(rows)
    if len(set(rows)) != len(rows):
        raise ValueError("laboratory histories cannot distinguish all mission behaviors")
    partitions = tuple(
        tuple(sum(1 << i for i, row in enumerate(rows) if row[q] == value) for value in range(3))
        for q in range(len(QUERIES))
    )
    return CompiledPrior(tuple(representatives), tuple(classes), tuple(class_ids), rows, partitions)


def class_id(program):
    return compiled().program_classes[PROGRAM_INDEX[tuple(program)]]


def accepted(world, build):
    return validate_build(build) and class_id(world.program) == class_id(build)


def selection(seed):
    return Truth(program=PROGRAMS[seed % len(PROGRAMS)])


def specification(world, theory, discovery, options=None):
    options = options or GenerationOptions()
    archive = (read(world.program, (0,))[0], read(world.program, (1,))[0])
    provisional = None
    if options.guidance == "provisional":
        prior = compiled()
        candidates = [i for i, row in enumerate(prior.rows) if tuple(row[:2]) == archive]
        # A simple archive-consistent explanation is assistance, never a prior
        # constraint or a promise that every generated world needs revision.
        index = min(candidates, key=lambda i: (len(prior.signatures[i]), prior.representatives[i]))
        provisional = prior.representatives[index]
    return Investigation(
        theory=theory,
        discovery=discovery,
        archive=archive,
        guidance=options.guidance,
        provisional=provisional,
        resolved=world.program if theory == 0 else None,
        finish_policy=options.finish_policy,
        consistency_check=options.consistency_check,
    )


def generation_options(spec):
    return GenerationOptions(
        guidance=spec.guidance,
        finish_policy=spec.finish_policy,
        consistency_check=spec.consistency_check,
    )


def prior_mask(spec):
    if spec.resolved is not None:
        return 1 << class_id(spec.resolved)
    return sum(1 << i for i, row in enumerate(compiled().rows) if tuple(row[:2]) == spec.archive)


def valid_query(query):
    return 1 <= len(query) <= 8 and all(type(v) is int and v in (0, 1) for v in query)


def validate_build(build):
    return (
        isinstance(build, tuple)
        and len(build) == 4
        and all(type(v) is int and 0 <= v < 12 for v in build)
    )


def canonical_query(query):
    return tuple(query)


def read_world(world, query):
    return read(world.program, query)


def target(world):
    return world.program
