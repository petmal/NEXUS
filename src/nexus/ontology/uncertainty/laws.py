"""Finite disturbances and exact robust acceptance; schedules are factored, not sampled."""

from functools import lru_cache
from itertools import combinations, product
from math import factorial
from types import MappingProxyType

from nexus.ontology.uncertainty.schema import Investigation, Physics, Truth


def read_world(world, query):
    return read(world, query)

SPACES = tuple(
    sorted(
        {
            tuple(sorted((a, b, a ^ b)))
            for a, b in combinations(range(1, 32), 2)
            if min(a.bit_count(), b.bit_count(), (a ^ b).bit_count()) >= 3
        }
    )
)
MODELS = tuple(
    Physics(checks=space[:2], syndrome=(c, d), pattern=p)
    for space in SPACES
    for c, d, p in product(range(2), repeat=3)
)
MODEL_INDEX = MappingProxyType({m: i for i, m in enumerate(MODELS)})
BUILDS = tuple(product(range(16), range(2), range(2)))
BUILD_INDEX = MappingProxyType({b: i for i, b in enumerate(BUILDS)})
QUERIES = (*((0, i) for i in range(8)), (1, 0), (2, 0))


def physics(world):
    return Physics(checks=world.checks, syndrome=world.syndrome, pattern=world.pattern)


@lru_cache(maxsize=120)
def support(model):
    a, b = model.checks
    c, d = model.syndrome
    return tuple(
        z for z in range(32) if (z & a).bit_count() % 2 == c and (z & b).bit_count() % 2 == d
    )


def loading(pattern, j):
    return -1 if pattern and j % 2 else 1


def exposure(model, z):
    return tuple((1 if not (z >> j & 1) else -1) + loading(model.pattern, j) for j in range(5))


def canonical_query(query):
    return query if query[0] == 0 else (query[0], 0)


def read(world, query):
    mode, fixture = canonical_query(query)
    if mode == 0:
        return exposure(world, support(physics(world))[world.order[fixture]])
    mean = tuple(loading(world.pattern, j) for j in range(5))
    if mode == 1:
        return mean
    # Exact balanced-panel means, variances and pairwise covariances. These never
    # encode ordering or higher moments; repeating them reveals nothing new.
    return (*mean, *(1 for _ in range(5)), *(0 for _ in range(10)))


def valid_query(query):
    return len(query) == 2 and query[0] in (0, 1, 2) and query[1] in range(8)


def validate_build(build):
    return build in BUILD_INDEX


def accepted(model, build):
    if not validate_build(build):
        return False
    mask, offset, pattern = build
    for z in support(physics(model)):
        for delta in (-1, 1):
            answer = -1 if offset else 1
            for j in range(4):
                if mask >> j & 1:
                    physical = -1 if z >> j & 1 else 1
                    corrected = physical + (loading(model.pattern, j) - loading(pattern, j)) * delta
                    if corrected not in (-1, 1):
                        return False
                    answer *= corrected
            if answer != (-1 if z >> 4 & 1 else 1):
                return False
    return True


def target(world):
    return next(build for build in BUILDS if accepted(world, build))


def selection(seed):
    model = MODELS[seed % len(MODELS)]
    rank = (seed // len(MODELS)) % factorial(8)
    remaining = list(range(8))
    order = []
    for n in range(7, -1, -1):
        index, rank = divmod(rank, factorial(n))
        order.append(remaining.pop(index))
    return Truth(**model.model_dump(), order=tuple(order))


def specification(world, theory, discovery):
    return Investigation(
        theory=theory,
        discovery=discovery,
        known_checks=world.checks if theory == 2 else None,
        known_pattern=world.pattern if theory == 2 else None,
        resolved=physics(world) if theory == 0 else None,
    )


@lru_cache(maxsize=1)
def tables():
    from nexus.ontology.discovery.inference import DecisionTables

    accepting = tuple(
        sum(1 << i for i, model in enumerate(MODELS) if accepted(model, build)) for build in BUILDS
    )
    exposures = tuple(frozenset(exposure(model, z) for z in support(model)) for model in MODELS)
    return DecisionTables(BUILDS, accepting), exposures


def prior_mask(spec):
    return sum(
        1 << i
        for i, model in enumerate(MODELS)
        if (spec.resolved is None or model == spec.resolved)
        and (
            spec.known_checks is None
            or model.checks == spec.known_checks
            and model.pattern == spec.known_pattern
        )
    )
