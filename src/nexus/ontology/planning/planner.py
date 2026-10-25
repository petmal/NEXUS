"""Exact joint planning and a separate science-shortest comparison.

Collapse each travel segment to a disclosed shortest route. This is exact:
movement has no other physical effect, and no information is hidden in the map.
Taking the only seal first is without loss for this known-law physical optimum.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from heapq import heappop, heappush

from nexus.ontology.planning.layout import LAYOUTS, route
from nexus.ontology.stateful.laws import DEAD, MODES, WORLD_INDEX, distances, encode, tables
from nexus.ontology.stateful.schema import Truth, Vector


@dataclass(frozen=True)
class Plan:
    actions: int
    modes: tuple[int, ...]
    moves: int


@lru_cache(maxsize=1024)
def optimal(world: Truth, target: Vector, planning: int) -> Plan:
    layout = LAYOUTS[planning]
    transitions = tables()[WORLD_INDEX[world]]
    goal = encode(target)
    initial = (0, layout.start)
    costs = {initial: 1}  # Take the original seal.
    parents: dict[tuple[int, str], tuple[tuple[int, str], int]] = {}
    queue = [(1, *initial)]
    best: tuple[int, tuple[int, str]] | None = None
    while queue:
        cost, state, room = heappop(queue)
        node = (state, room)
        if cost != costs[node] or (best is not None and cost >= best[0]):
            continue
        if state == goal:
            total = cost + len(route(planning, room, layout.finish)) + 1
            if best is None or total < best[0]:
                best = (total, node)
            continue
        for mode, destination in enumerate(layout.mode_rooms):
            after = transitions[mode][state]
            if after == DEAD:
                continue
            child = (after, destination)
            total = cost + len(route(planning, room, destination)) + 1
            if total < costs.get(child, 10**9):
                costs[child] = total
                parents[child] = (node, mode)
                heappush(queue, (total, *child))
    if best is None:
        raise ValueError("physical goal is unreachable")
    word = []
    node = best[1]
    while node != initial:
        node, mode = parents[node]
        word.append(mode)
    word.reverse()
    return Plan(best[0], tuple(word), best[0] - len(word) - 2)


@lru_cache(maxsize=1024)
def science_shortest_cost(world: Truth, target: Vector, planning: int) -> int:
    """Cheapest route among ALL minimum-operation solutions, including take/finish."""
    layout = LAYOUTS[planning]
    index = WORLD_INDEX[world]
    distance = distances(target)[index]
    transitions = tables()[index]

    @lru_cache(maxsize=None)
    def visit(state, room):
        if distance[state] == 0:
            return len(route(planning, room, layout.finish)) + 1
        return min(
            len(route(planning, room, destination)) + 1 + visit(after, destination)
            for mode, destination in enumerate(layout.mode_rooms)
            if distance[after := transitions[mode][state]] == distance[state] - 1
        )

    return 1 + visit(0, layout.start)


def actions_for(word: tuple[int, ...], planning: int):
    from nexus.models.actions import FinishAction, MoveAction, OperateAction, TakeAction

    layout = LAYOUTS[planning]
    result = [TakeAction(artifact="seal")]
    room = layout.start
    for mode in word:
        destination = layout.mode_rooms[mode]
        result.extend(MoveAction(target=r) for r in route(planning, room, destination))
        result.append(OperateAction(machine=MODES[mode], artifact="seal"))
        room = destination
    result.extend(MoveAction(target=r) for r in route(planning, room, layout.finish))
    result.append(FinishAction())
    return tuple(result)
