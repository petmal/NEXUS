"""Independent unit-edge/tuple checks for spatial costs and all-prior policies."""

from collections import deque
from functools import lru_cache

from nexus.ontology.planning.layout import LAYOUTS
from nexus.ontology.planning.policy import reference_cost
from nexus.ontology.planning.schema import Investigation
from nexus.ontology.stateful.laws import WORLDS
from nexus.ontology.stateful.policy import investigator
from nexus.ontology.stateful.proof import scalar_step
from nexus.ontology.stateful.search import FINISH


def neighbors(layout, room):
    return tuple(b if a == room else a for a, b in layout.edges if room in (a, b))


@lru_cache(maxsize=256)
def walking_cost(planning, start, end):
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        room, distance = queue.popleft()
        if room == end:
            return distance
        for child in neighbors(LAYOUTS[planning], room):
            if child not in seen:
                seen.add(child)
                queue.append((child, distance + 1))
    raise ValueError("disconnected public layout")


@lru_cache(maxsize=1024)
def physical_minimum(world, target, planning):
    """Unit-action BFS, separate from the production weighted/compiled planner.

    The seal starts carried after one take. Dropping, waiting, probing or failed
    finishing cannot improve a known-law physical plan in these static worlds.
    """
    layout = LAYOUTS[planning]
    initial = ((0, 0, 0, 0), layout.start)
    queue = deque([(*initial, 1)])
    seen = {initial}
    while queue:
        state, room, distance = queue.popleft()
        if state == target and room == layout.finish:
            return distance + 1
        children = [(state, destination) for destination in neighbors(layout, room)]
        children.extend(
            (scalar_step(world, state, mode), room)
            for mode, destination in enumerate(layout.mode_rooms)
            if room == destination
        )
        for after, destination in children:
            child = (after, destination)
            if after is not None and child not in seen:
                seen.add(child)
                queue.append((*child, distance + 1))
    raise ValueError("physical goal unreachable")


@lru_cache(maxsize=12)
def all_world_policy(target, planning):
    """Replay every latent law with scalar physics and separately counted travel."""
    policy = investigator(target)
    layout = LAYOUTS[planning]
    bound = reference_cost(Investigation(theory=3, target=target, planning=planning))
    costs = []
    for world in WORLDS:
        belief, state, room, cost = policy.game.initial, (0, 0, 0, 0), layout.start, 1
        done = False
        while not done:
            kind, word = policy.decisions[belief]
            for action in (*word, FINISH if kind == "install" else 4):
                if action == FINISH:
                    if state != target or not policy.game.ready(belief):
                        raise ValueError("unsupported or physically wrong reference finish")
                    cost += walking_cost(planning, room, layout.finish) + 1
                    done = True
                    break
                destination = layout.mode_rooms[action % 4]
                cost += walking_cost(planning, room, destination) + 1
                room = destination
                after = scalar_step(world, state, action % 4)
                observation = 5 if after is None else after[0]
                if action < 4:
                    state = after
                    if state is None:
                        raise ValueError("public policy collapsed a possible seal")
                belief = dict(policy.game.branches(belief, action))[observation]
            if cost > bound:
                raise ValueError("policy exceeded routed public bound")
        costs.append(cost)
    if max(costs) != bound:
        raise ValueError("recursive bound differs from all-world scalar replay")
    return {
        "worlds": len(WORLDS),
        "minimum_actions": min(costs),
        "maximum_actions": max(costs),
        "all_finishes_supported": True,
        "reference_bound_exact_for_this_policy": True,
        "policy_optimality_proved": False,
    }
