"""Finite composed laws, complete build acceptance and persistent mounting effects."""

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from types import MappingProxyType

from nexus.ontology.assembly.schema import Investigation, Specimen, Truth

Build = tuple[int, int, int, int, int]
Query = tuple[int, int, int]
WORLDS = tuple(
    Truth(gain_b=s, phase_b=a, gain_c=t, phase_c=b, kernel=h, offset=r)
    for s, a, t, b, h, r in product((1, 2), range(3), (1, 2), range(3), range(4), range(3))
)
WORLD_INDEX = MappingProxyType({w: i for i, w in enumerate(WORLDS)})
BUILDS: tuple[Build, ...] = tuple(product((1, 2), range(3), (1, 2), range(3), range(4)))
BUILD_INDEX = MappingProxyType({d: i for i, d in enumerate(BUILDS)})
POINTS = tuple(product(range(3), repeat=2))
QUERIES: tuple[Query, ...] = (
    *((0, x, 0) for x in range(3)),
    *((1, 0, y) for y in range(3)),
    *((2, x, y) for x, y in POINTS),
)
QUERY_INDEX = MappingProxyType({q: i for i, q in enumerate(QUERIES)})


def kernel(h: int, u: int, v: int) -> int:
    if h == 0:
        return (u + v) % 3
    if h == 1:
        return (u - v) % 3
    if h == 2:
        return u * v % 3
    if h == 3:
        return (u * u + v) % 3
    raise ValueError("unknown assembly kernel")


def target(world: Truth) -> Build:
    return world.gain_b, world.phase_b, world.gain_c, world.phase_c, world.kernel


def physical(build: Build, x: int, y: int) -> int:
    s, a, t, b, h = build
    return kernel(h, (s * x + a) % 3, (t * y + b) % 3)


def signature(build: Build) -> tuple[int, ...]:
    # Local gain contracts are part of the explicit complete mission.
    return build[0], build[2], *(physical(build, x, y) for x, y in POINTS)


def accepted(world: Truth, build: Build | None) -> bool:
    return (
        build is not None and build in BUILD_INDEX and signature(build) == signature(target(world))
    )


def normalize_query(channel: int, x: int, y: int) -> Query:
    return channel, x if channel != 1 else 0, y if channel != 0 else 0


def reading(world: Truth, query: Query, coupled: bool) -> int:
    channel, x, y = query
    u, v = (world.gain_b * x + world.phase_b) % 3, (world.gain_c * y + world.phase_c) % 3
    r = world.offset if coupled else 0
    if channel == 0:
        return (u + r) % 3
    if channel == 1:
        return (v - r) % 3
    return (kernel(world.kernel, u, v) + r) % 3


def prepare(sample: Specimen, slot: int, gain: int, phase: int) -> Specimen:
    """Mounting replaces one component and rotates an already mounted partner."""
    if slot == 0:
        return Specimen(
            b=(gain, phase),
            c=None if sample.c is None else (sample.c[0], (sample.c[1] + phase) % 3),
            kernel=sample.kernel,
        )
    return Specimen(
        c=(gain, phase),
        b=None if sample.b is None else (sample.b[0], (sample.b[1] + phase) % 3),
        kernel=sample.kernel,
    )


def submitted(sample: Specimen) -> Build | None:
    return (
        (*sample.b, *sample.c, sample.kernel)
        if sample.b is not None and sample.c is not None and sample.kernel is not None
        else None
    )


@dataclass(frozen=True)
class Tables:
    rows: tuple[bytes, ...]  # world-major, all legal observation equivalence classes
    partitions: tuple[tuple[int, ...], ...]
    accepting: tuple[int, ...]  # complete decision -> worlds accepting it
    signatures: tuple[tuple[int, ...], ...]


@lru_cache(maxsize=2)
def tables(coupled: bool) -> Tables:
    rows = tuple(bytes(reading(w, q, coupled) for q in QUERIES) for w in WORLDS)
    partitions = tuple(
        tuple(sum(1 << i for i, row in enumerate(rows) if row[q] == value) for value in range(3))
        for q in range(len(QUERIES))
    )
    signatures = tuple(signature(target(w)) for w in WORLDS)
    by_signature = {}
    for i, sig in enumerate(signatures):
        by_signature[sig] = by_signature.get(sig, 0) | (1 << i)
    return Tables(rows, partitions, tuple(by_signature[signature(d)] for d in BUILDS), signatures)


def prior_mask(spec: Investigation) -> int:
    if spec.resolved is not None:
        return 1 << WORLD_INDEX[spec.resolved]
    return sum(
        1 << i
        for i, w in enumerate(WORLDS)
        if spec.known_kernel is None or w.kernel == spec.known_kernel
    )
