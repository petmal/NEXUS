"""Independent scalar-state proof of structural costs, with no compiled tables."""

from collections import deque
from functools import lru_cache
from heapq import heappop, heappush

from nexus.ontology.interference.proof import scalar_step
from nexus.ontology.interference.schema import COUNT


@lru_cache(maxsize=32)
def scalar_metrics(spec):
    initial = (0,) * COUNT
    # Each scalar operation has order five. Enumerate whole same-machine blocks
    # of lengths1..4; no (state,last-machine) graph is used by this oracle.
    blocks = {initial: 0}
    queue = deque([initial])
    while queue:
        state = queue.popleft()
        if state == spec.target:
            minimum_blocks = blocks[state]
            break
        for mode in range(COUNT):
            after = state
            for _ in range(4):
                after = scalar_step(spec, after, mode)
                if after not in blocks:
                    blocks[after] = blocks[state] + 1
                    queue.append(after)
    else:
        raise ValueError("unreachable structural target")

    # Lexicographic Dijkstra minimizes primitive actions first, then blocks.
    costs = {(initial, -1): (0, 0)}
    heap = [(0, 0, initial, -1)]
    while heap:
        actions, block_count, state, last = heappop(heap)
        if costs[state, last] != (actions, block_count):
            continue
        if state == spec.target:
            optimal_blocks = block_count
            break
        for mode in range(COUNT):
            after = scalar_step(spec, state, mode)
            value = (actions + 1, block_count + int(mode != last))
            key = after, mode
            if value < costs.get(key, (10**9, 10**9)):
                costs[key] = value
                heappush(heap, (*value, after, mode))

    # Heap Dijkstra over scalar vectors independently minimizes bank reopenings.
    costs = {initial: 0}
    heap = [(0, initial)]
    while heap:
        cost, state = heappop(heap)
        if costs[state] != cost:
            continue
        if state == spec.target:
            bank_breaks = cost
            break
        for mode in range(COUNT):
            after = scalar_step(spec, state, mode)
            weight = int(
                any(
                    state[b : b + 3] == spec.target[b : b + 3]
                    and after[b : b + 3] != spec.target[b : b + 3]
                    for b in (0, 3)
                )
            )
            if cost + weight < costs.get(after, 10**9):
                costs[after] = cost + weight
                heappush(heap, (cost + weight, after))
    return {
        "minimum_machine_blocks": minimum_blocks,
        "minimum_machine_blocks_on_optimal_paths": optimal_blocks,
        "minimum_whole_bank_reopening_operations": bank_breaks,
    }
