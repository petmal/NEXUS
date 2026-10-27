"""Independent tuple-state semantics and unit-edge constrained searches."""

from collections import deque
from functools import lru_cache
from heapq import heappop, heappush
from itertools import product

from nexus.ontology.interference.schema import COUNT, SIZE


def scalar_step(spec, state, mode):
    bank, coordinate = divmod(mode, 3)
    driver = bank * 3 + (coordinate + 1) % 3
    destination = (
        ((bank + 1) % 2) * 3
        if (spec.options.coupling == "coupled" and coordinate == 2)
        else bank * 3 + (coordinate + 2) % 3
    )
    if state[driver] != spec.resolved.guards[mode]:
        return state
    return tuple(
        (value + spec.resolved.gains[mode]) % 5
        if index == mode
        else (value + spec.resolved.spill_gains[mode]) % 5
        if index == destination
        else value
        for index, value in enumerate(state)
    )


@lru_cache(maxsize=32)
def scalar_cost(spec, restriction="free"):
    """Minimize operations; use explicit bank history for the restricted case."""
    if restriction not in ("free", "bank_contiguous", "goal_preserving"):
        raise ValueError("unknown proof restriction")
    initial = ((0,) * COUNT, -1, 0)
    queue = deque([(initial, 0)])
    seen = {initial}
    while queue:
        (state, previous, used), cost = queue.popleft()
        if state == spec.target:
            return cost
        for mode in range(COUNT):
            bank = mode // 3
            if restriction == "bank_contiguous" and bank != previous and used & (1 << bank):
                continue
            after = scalar_step(spec, state, mode)
            if restriction == "goal_preserving" and any(
                before == target and later != target
                for before, later, target in zip(state, after, spec.target, strict=True)
            ):
                continue
            child = (
                (after, bank, used | (1 << bank))
                if restriction == "bank_contiguous"
                else (after, -1, 0)
            )
            if child not in seen:
                seen.add(child)
                queue.append((child, cost + 1))
    return None


@lru_cache(maxsize=32)
def scalar_minimum_goal_breaks(spec):
    """Independent heap search minimizing coordinate-breaking operations."""
    initial = (0,) * COUNT
    costs = {initial: 0}
    queue = [(0, initial)]
    while queue:
        cost, state = heappop(queue)
        if cost != costs[state]:
            continue
        if state == spec.target:
            return cost
        for mode in range(COUNT):
            after = scalar_step(spec, state, mode)
            weight = int(
                any(
                    before == target and later != target
                    for before, later, target in zip(state, after, spec.target, strict=True)
                )
            )
            if cost + weight < costs.get(after, SIZE):
                costs[after] = cost + weight
                heappush(queue, (cost + weight, after))
    raise ValueError("unreachable target in scalar goal-break proof")


def independent_bank_minima(spec):
    if spec.options.coupling != "independent":
        raise ValueError("factorization applies only to independent banks")
    result = []
    for bank in range(2):
        initial = (0,) * COUNT
        queue = deque([(initial, 0)])
        seen = {initial}
        indices = slice(bank * 3, bank * 3 + 3)
        while queue:
            state, cost = queue.popleft()
            if state[indices] == spec.target[indices]:
                result.append(cost)
                break
            for mode in range(bank * 3, bank * 3 + 3):
                after = scalar_step(spec, state, mode)
                if after not in seen:
                    seen.add(after)
                    queue.append((after, cost + 1))
        else:
            raise ValueError("independent bank target is unreachable")
    return tuple(result)


@lru_cache(maxsize=8)
def prove_kernel(spec):
    from nexus.ontology.interference.laws import decode, encode, step, tables

    rows = tables(spec.resolved, spec.options.coupling)
    checked = 0
    for state in product(range(5), repeat=COUNT):
        encoded = encode(state)
        for mode, row in enumerate(rows):
            expected = scalar_step(spec, state, mode)
            if expected != decode(row[encoded]) or expected != step(
                spec.resolved, spec.options, state, mode
            ):
                raise ValueError("runtime or compiled transition disagrees with scalar semantics")
            # Every operator is a permutation: five repetitions restore state.
            restored = encoded
            for _ in range(5):
                restored = row[restored]
            if restored != encoded:
                raise ValueError("interference operation violates its reversibility contract")
            checked += 1
    return checked
