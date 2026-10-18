"""Finite shared mechanism; mission identity is behavior, not program spelling."""

from functools import lru_cache
from itertools import product

from nexus.ontology.compositional.laws import gate

QUERIES = tuple(product(range(2), *([range(3)] * 5)))
PROGRAMS = tuple(
    (graph, f, g, h, changed, replacement, shift)
    for graph, f, g, h, changed, replacement, shift in product(
        range(3), range(4), range(4), range(4), range(3), range(4), range(3)
    )
    if (f, g, h)[changed] != replacement
)
PROGRAM_INDEX = {program: i for i, program in enumerate(PROGRAMS)}
QUERY_INDEX = {query: i for i, query in enumerate(QUERIES)}


def components(program, settings):
    graph, f, g, h, changed, replacement, shift = program
    context, x, y, z, a, b = settings
    ops = [f, g, h]
    if context:
        ops[changed] = replacement
    first = (gate(ops[0], x, y) + a) % 3
    second = (gate(ops[1], y if graph == 1 else first, z) + b) % 3
    result = gate(ops[2], second if graph == 0 else first, x if graph == 0 else second)
    return (result + shift) % 3, second


def physical(program, settings):
    return components(program, settings)[0]


def extra(program, offset, settings):
    companion = (1 - settings[0], *settings[1:])
    return (components(program, companion)[1] + offset) % 3


def displayed(program, offset, settings, material, coupled):
    contribution = extra(program, offset, settings) if coupled else 0
    return (contribution + (physical(program, settings) if material == "survey" else 0)) % 3


@lru_cache(maxsize=1)
def signatures():
    return tuple(bytes(physical(program, query) for query in QUERIES) for program in PROGRAMS)


@lru_cache(maxsize=1)
def targets():
    first = {}
    return tuple(first.setdefault(row, i) for i, row in enumerate(signatures()))


def accepted(program, submitted):
    if submitted is None or tuple(submitted) not in PROGRAM_INDEX:
        return False
    # A mission checks one pair, not the entire prior. This also keeps acceptance
    # independent of the compiled policy/target cache.
    return all(physical(program, query) == physical(submitted, query) for query in QUERIES)


def selection(seed):
    # Full Cartesian sampler, no hidden solvability or difficulty filtering.
    return PROGRAMS[seed % len(PROGRAMS)], (seed // len(PROGRAMS)) % 3
