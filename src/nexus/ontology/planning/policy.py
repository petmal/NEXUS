"""Public reference with an all-outcome spatial cost, separate from physical optimum."""

from __future__ import annotations

from functools import lru_cache

from nexus.ontology.planning.layout import LAYOUTS, route
from nexus.ontology.planning.planner import actions_for, optimal
from nexus.ontology.planning.schema import Investigation
from nexus.ontology.stateful.laws import MODES
from nexus.ontology.stateful.policy import investigator
from nexus.ontology.stateful.search import FINISH


@lru_cache(maxsize=32)
def reference_cost(spec: Investigation) -> int:
    if spec.resolved is not None:
        return optimal(spec.resolved, spec.target, spec.planning).actions
    policy = investigator(spec.target)
    layout = LAYOUTS[spec.planning]

    @lru_cache(maxsize=None)
    def continuation(belief, room):
        kind, word = policy.decisions[belief]
        sequence = (*word, FINISH if kind == "install" else 4)

        def traverse(belief, room, offset):
            if offset == len(sequence):
                return continuation(belief, room)
            action = sequence[offset]
            if action == FINISH:
                if not policy.game.ready(belief):
                    raise ValueError("reference finish is not supported")
                return len(route(spec.planning, room, layout.finish)) + 1
            destination = layout.mode_rooms[action % 4]
            return (
                len(route(spec.planning, room, destination))
                + 1
                + max(
                    traverse(child, destination, offset + 1)
                    for _, child in policy.game.branches(belief, action)
                )
            )

        return traverse(belief, room, 0)

    return 1 + continuation(policy.game.initial, layout.start)


def public_policy(player, evidence):
    from nexus.models.actions import (
        FinishAction,
        MoveAction,
        OperateAction,
        ProbeAction,
        TakeAction,
    )

    from nexus.ontology.player_records import specification

    spec = specification(Investigation, evidence, family="stateful-planning-v1")
    layout = LAYOUTS[spec.planning]

    def act(action):
        result = player.act(expected_turn=player.status().turn, action=action)
        if not result.ok:
            raise ValueError(f"planning public policy failed: {result.message}")
        return result

    def travel(destination):
        for room in route(spec.planning, player.observe().room, destination):
            act(MoveAction(target=room))

    if spec.resolved is not None:
        plan = optimal(spec.resolved, spec.target, spec.planning)
        for action in actions_for(plan.modes, spec.planning):
            result = act(action)
        return result
    act(TakeAction(artifact="seal"))
    policy = investigator(spec.target)
    belief = policy.game.initial
    while True:
        kind, word = policy.decisions[belief]
        for a in (*word, FINISH if kind == "install" else 4):
            if a == FINISH:
                if not policy.game.ready(belief):
                    raise ValueError("reference attempted unsupported finish")
                travel(layout.finish)
                return act(FinishAction())
            travel(layout.mode_rooms[a % 4])
            action_type = OperateAction if a < 4 else ProbeAction
            result = act(action_type(machine=MODES[a % 4], artifact="seal"))
            payload = next(
                e["details"]["result"]["payload"] for e in result.events if "result" in e["details"]
            )
            belief = dict(policy.game.branches(belief, a))[payload["reading"]]
