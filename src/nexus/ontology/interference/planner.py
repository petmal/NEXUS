"""Exact operation BFS, all-orders bank blocks and goal-preserving paths."""

from collections import deque
from dataclasses import dataclass
from functools import lru_cache

from nexus.models.actions import FinishAction, OperateAction, TakeAction
from nexus.ontology.interference.laws import decode, encode, tables
from nexus.ontology.interference.schema import COUNT, SIZE


@dataclass(frozen=True)
class Plan:
    actions: int
    modes: tuple[int, ...]
    explored: int


@lru_cache(maxsize=8)
def distances(world, coupling):
    rows = tables(world, coupling)
    distance = [-1] * SIZE
    distance[0] = 0
    queue = deque([0])
    while queue:
        state = queue.popleft()
        for row in rows:
            after = row[state]
            if distance[after] < 0:
                distance[after] = distance[state] + 1
                queue.append(after)
    return tuple(distance)


@lru_cache(maxsize=32)
def optimal(spec):
    rows = tables(spec.resolved, spec.options.coupling)
    goal = encode(spec.target)
    parents = {0: None}
    queue = deque([0])
    while queue:
        state = queue.popleft()
        if state == goal:
            word = []
            while parents[state] is not None:
                state, mode = parents[state]
                word.append(mode)
            return Plan(len(word) + 2, tuple(reversed(word)), len(parents))
        for mode, row in enumerate(rows):
            after = row[state]
            if after not in parents:
                parents[after] = state, mode
                queue.append(after)
    raise ValueError("interference target is unreachable")


@lru_cache(maxsize=8)
def bank_contiguous_distances(world, coupling):
    """All words using each bank in at most one block; switches cost zero.

    An earlier bank need not be finished when leaving it: later cross-bank writes
    may complete it. Unlike the old single-write family, no boundary state can
    be summarized by a mask of completed banks.
    """
    rows = tables(world, coupling)
    result = [None] * SIZE
    for first in (0, 1):
        costs = {(0, 0): 0}
        queue = deque([(0, 0)])
        while queue:
            state, stage = queue.popleft()
            cost = costs[state, stage]
            if stage == 0 and cost < costs.get((state, 1), SIZE * 2):
                costs[state, 1] = cost
                queue.appendleft((state, 1))
            bank = first if stage == 0 else 1 - first
            for row in rows[bank * 3 : bank * 3 + 3]:
                after = row[state]
                if cost + 1 < costs.get((after, stage), SIZE * 2):
                    costs[after, stage] = cost + 1
                    queue.append((after, stage))
        for (state, _), cost in costs.items():
            if result[state] is None or cost < result[state]:
                result[state] = cost
    return tuple(result)


@lru_cache(maxsize=32)
def minimum_goal_breaks(spec):
    """Minimum number of operations that unset at least one matched coordinate.

    Zero-one BFS minimizes breaks across all successful words, regardless of
    length. A positive result proves every solution must disturb a completed
    coordinate subgoal, not merely that a chosen reference happens to do so.
    """
    rows = tables(spec.resolved, spec.options.coupling)
    masks = [
        sum((v == t) << i for i, (v, t) in enumerate(zip(decode(s), spec.target)))
        for s in range(SIZE)
    ]
    costs = [SIZE] * SIZE
    costs[0] = 0
    queue = deque([0])
    while queue:
        state = queue.popleft()
        for row in rows:
            after = row[state]
            weight = int(bool(masks[state] & ~masks[after]))
            cost = costs[state] + weight
            if cost < costs[after]:
                costs[after] = cost
                if weight:
                    queue.append(after)
                else:
                    queue.appendleft(after)
    value = costs[encode(spec.target)]
    if value == SIZE:
        raise ValueError("goal-break minimum requested for unreachable target")
    return value


def goal_preserving_cost(spec):
    """Shortest word that never unsets a matched coordinate, or None."""
    rows = tables(spec.resolved, spec.options.coupling)
    masks = [
        sum((v == t) << i for i, (v, t) in enumerate(zip(decode(s), spec.target)))
        for s in range(SIZE)
    ]
    goal = encode(spec.target)
    queue = deque([(0, 0)])
    seen = {0}
    while queue:
        state, cost = queue.popleft()
        if state == goal:
            return cost
        for row in rows:
            after = row[state]
            if after not in seen and not masks[state] & ~masks[after]:
                seen.add(after)
                queue.append((after, cost + 1))
    return None


def actions_for(spec, modes):
    if any(type(mode) is not int or not 0 <= mode < COUNT for mode in modes):
        raise ValueError("unknown interference mode")
    return (
        TakeAction(artifact="seal"),
        *(OperateAction(machine=spec.topology[mode].machine, artifact="seal") for mode in modes),
        FinishAction(),
    )
