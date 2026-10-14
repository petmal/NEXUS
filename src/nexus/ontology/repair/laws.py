"""Exact public grammar; hidden constants and relation structure are immutable.

The missing relationship has AST z, z*z, or (z*z)*z, plus an unknown offset.
These are semantically different functions over F7, with distinct transfer pairs.
No private state is placed in a specimen: its public preparation/treatment is
sufficient to evaluate its hidden response in a fixed world.
"""

from functools import lru_cache
from itertools import product

from nexus.ontology.repair.schema import Q, Specimen, Truth


def relation(world: Truth, z: int) -> int:
    value = z
    if world.degree >= 2:
        value *= z
    if world.degree == 3:
        value *= z
    return (world.c + value) % Q


def response(world: Truth, context: tuple[int, int]) -> tuple[int, ...]:
    plane, x = context
    if plane == 0:
        return ((world.b + world.r * (world.a - x)) % Q,)
    mask = world.r * (world.b - x)
    return tuple((relation(world, z) + mask) % Q for z in (0, 2))


def residuals(world: Truth, doses: tuple[int, int, int, int]) -> tuple[int, ...]:
    u, v, w, z = doses
    f3, f4 = relation(world, 3), relation(world, 4)
    return (
        (world.a - u) % Q,
        (world.b + world.a * u - v) % Q,
        (f3 + world.b * v - w) % Q,
        (f4 + f3 * u * v - z) % Q,
    )


def solution(a: int, b: int, c: int, degree: int) -> tuple[int, int, int, int]:
    # A public calculation, also used by the reference investigator. No r needed.
    f3, f4 = (c + pow(3, degree, Q)) % Q, (c + pow(4, degree, Q)) % Q
    u, v = a, (b + a * a) % Q
    return u, v, (f3 + b * v) % Q, (f4 + f3 * u * v) % Q


def transform(world: Truth, specimen: Specimen, machine: str, settings=None) -> Specimen:
    clean = specimen.model_copy(update={"reading": None, "instrument": None})
    if machine == "stage":
        if settings is None:
            raise ValueError("stage must be configured before use")
        if specimen.material == "survey":
            return clean.model_copy(update={"context": tuple(settings), "charged": False})
    elif machine == "coupler":
        if specimen.material == "survey" and specimen.context is not None:
            return clean.model_copy(update={"charged": True})
    elif machine == "doser":
        if settings is None:
            raise ValueError("doser must be configured before use")
        if specimen.material == "seal":
            return clean.model_copy(update={"doses": tuple(settings)})
    elif machine in ("reference", "reader"):
        reading = None
        if specimen.material == "survey":
            if machine == "reference":
                reading = (world.a,)
            elif specimen.charged and specimen.context is not None:
                reading = response(world, specimen.context)
        return clean.model_copy(update={"reading": reading, "instrument": machine})
    else:
        raise ValueError("unknown apparatus")
    # Insensitive materials give the same public null response for every world.
    return clean


@lru_cache(maxsize=1)
def worlds() -> tuple[Truth, ...]:
    return tuple(
        Truth(a=a, b=b, c=c, degree=d, r=r)
        for a, b, c in product(range(Q), repeat=3)
        for d in (1, 2, 3)
        for r in range(Q)
    )


def world_at(seed: int) -> Truth:
    """Constant-space decoding of the declared truth-index sampler."""
    index = seed % (7**4 * 3)
    index, r = divmod(index, 7)
    index, degree = divmod(index, 3)
    index, c = divmod(index, 7)
    a, b = divmod(index, 7)
    return Truth(a=a, b=b, c=c, degree=(1, 2, 3)[degree], r=r)
