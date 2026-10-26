"""Exact joint location/state planning and all-orders bank-contiguous baseline."""

from dataclasses import dataclass
from functools import cache, lru_cache
from heapq import heappop, heappush

from nexus.ontology.coordination.laws import encode, tables
from nexus.ontology.coordination.layout import layout_for, route
from nexus.ontology.coordination.schema import Investigation


@dataclass(frozen=True)
class Plan:
    actions: int
    modes: tuple[int, ...]
    moves: int
    explored: int


@lru_cache(maxsize=128)
def optimal(spec: Investigation) -> Plan:
    layout = layout_for(spec)
    transitions = tables(spec.resolved, spec.options)
    goal = encode(spec.target)
    initial = (0, layout.start)
    costs = {initial: 1}
    parents = {}
    queue = [(1, *initial)]
    best = None
    explored = 0
    while queue:
        cost, state, room = heappop(queue)
        node = state, room
        if cost != costs[node] or (best is not None and cost >= best[0]):
            continue
        explored += 1
        if state == goal:
            total = cost + len(route(spec.planning, room, layout.finish)) + 1
            if best is None or total < best[0]:
                best = total, node
            continue
        for mode, destination in enumerate(layout.mode_rooms):
            child = transitions[mode][state], destination
            total = cost + len(route(spec.planning, room, destination)) + 1
            if total < costs.get(child, 10**9):
                costs[child] = total
                parents[child] = node, mode
                heappush(queue, (total, *child))
    if best is None:
        raise ValueError("coordination target is unreachable")
    word = []
    node = best[1]
    while node != initial:
        node, mode = parents[node]
        word.append(mode)
    word.reverse()
    return Plan(best[0], tuple(word), best[0] - len(word) - 2, explored)


@lru_cache(maxsize=128)
def bank_contiguous_cost(spec: Investigation) -> int:
    """Minimum over every bank order and every within-bank word, with travel.

    Each coordinate writes only itself. On leaving a bank for the last time it
    must equal its target; unvisited banks remain zero. Consequently the mask of
    completed banks and current room completely describe block boundaries.
    Local Dijkstra explores all words, keeping every target-ending room. Walking
    between operations is compressed to shortest paths without changing physics.
    """
    options = spec.options
    width = options.registers_per_bank
    layout = layout_for(spec)
    transitions = tables(spec.resolved, options)
    target_parts = tuple(
        sum(spec.target[index] * 3**index for index in range(bank * width, (bank + 1) * width))
        for bank in range(options.banks)
    )

    @cache
    def continuation(mask, room):
        if mask == (1 << options.banks) - 1:
            return len(route(spec.planning, room, layout.finish)) + 1
        start = sum(part for bank, part in enumerate(target_parts) if mask & (1 << bank))
        best = 10**9
        for bank in range(options.banks):
            if mask & (1 << bank):
                continue
            goal = start + target_parts[bank]
            costs = {(start, room): 0}
            queue = [(0, start, room)]
            while queue:
                cost, state, here = heappop(queue)
                if cost != costs[state, here]:
                    continue
                if state == goal:
                    best = min(best, cost + continuation(mask | (1 << bank), here))
                    # A target-preserving extra word costs at least direct walking
                    # to its endpoint, already available to the continuation.
                    continue
                for mode in range(bank * width, (bank + 1) * width):
                    destination = layout.mode_rooms[mode]
                    after = transitions[mode][state]
                    total = cost + len(route(spec.planning, here, destination)) + 1
                    child = after, destination
                    if total < costs.get(child, 10**9):
                        costs[child] = total
                        heappush(queue, (total, *child))
        return best

    result = 1 + continuation(0, layout.start)
    if result >= 10**9:
        raise ValueError("no bank-contiguous solution exists")
    return result


def actions_for(spec: Investigation, modes: tuple[int, ...]):
    from nexus.models.actions import Action, FinishAction, MoveAction, OperateAction, TakeAction

    layout = layout_for(spec)
    result: list[Action] = [TakeAction(artifact="seal")]
    room = layout.start
    for mode in modes:
        if type(mode) is not int or not 0 <= mode < spec.options.count:
            raise ValueError("unknown coordinate mode")
        destination = layout.mode_rooms[mode]
        result.extend(MoveAction(target=item) for item in route(spec.planning, room, destination))
        result.append(OperateAction(machine=spec.topology[mode].machine, artifact="seal"))
        room = destination
    result.extend(MoveAction(target=item) for item in route(spec.planning, room, layout.finish))
    result.append(FinishAction())
    return tuple(result)
