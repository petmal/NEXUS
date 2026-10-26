"""Independent scalar physics, unit-edge BFS and exhaustive admitted-kernel checks."""

from collections import deque
from functools import lru_cache
from itertools import product

from nexus.ontology.coordination.layout import layout_for


def scalar_step(spec, state, mode):
    """Interpret dimensions directly, without compiled topology or transition tables."""
    width = spec.options.registers_per_bank
    bank, register = divmod(mode, width)
    local = state[bank * width + (register + 1) % width]
    cross = (
        state[((bank + 1) % spec.options.banks) * width]
        if spec.options.coupling == "coupled" and register == width - 1
        else 0
    )
    result = list(state)
    result[mode] = (
        state[mode] + spec.resolved.gains[mode] * (1 + local ** spec.resolved.powers[mode] + cross)
    ) % 3
    return tuple(result)


@lru_cache(maxsize=128)
def physical_minimum(spec):
    """Unit-edge BFS; movement and operations are separate equal-cost edges.

    Taking first costs one action. Drops, waits, probes and failed finishes do
    not improve a known-law plan: they reveal no information or change physics.
    """
    layout = layout_for(spec)
    initial = (0,) * spec.options.count, layout.start
    queue = deque([(*initial, 1)])
    seen = {initial}
    while queue:
        state, room, distance = queue.popleft()
        if state == spec.target and room == layout.finish:
            return distance + 1
        children = [
            (state, right if left == room else left)
            for left, right in layout.edges
            if room in (left, right)
        ]
        children.extend(
            (scalar_step(spec, state, mode), room)
            for mode, destination in enumerate(layout.mode_rooms)
            if destination == room
        )
        for child in children:
            if child not in seen:
                seen.add(child)
                queue.append((*child, distance + 1))
    raise ValueError("independent scalar checker found an unreachable target")


@lru_cache(maxsize=32)
def prove_kernel(spec) -> int:
    from nexus.ontology.coordination.laws import decode, encode, step, tables

    transitions = tables(spec.resolved, spec.options)
    count = 0
    for state in product(range(3), repeat=spec.options.count):
        encoded = encode(state)
        for mode, row in enumerate(transitions):
            expected = scalar_step(spec, state, mode)
            if (
                decode(row[encoded], spec.options.count) != expected
                or step(spec.resolved, spec.options, state, mode) != expected
            ):
                raise ValueError("compiled or runtime transition differs from scalar semantics")
            count += 1
    return count


def independent_bank_minima(spec) -> tuple[int, ...]:
    """Separate product-factorization proof using scalar per-bank BFS."""
    if spec.options.coupling != "independent":
        raise ValueError("bank factorization applies only to independent physics")
    width = spec.options.registers_per_bank
    result = []
    for bank in range(spec.options.banks):
        offset = bank * width
        initial = (0,) * spec.options.count
        target = spec.target[offset : offset + width]
        queue = deque([(initial, 0)])
        seen = {initial}
        while queue:
            state, distance = queue.popleft()
            if state[offset : offset + width] == target:
                result.append(distance)
                break
            for mode in range(offset, offset + width):
                after = scalar_step(spec, state, mode)
                if after not in seen:
                    seen.add(after)
                    queue.append((after, distance + 1))
        else:
            raise ValueError("independent bank target unreachable")
    return tuple(result)
