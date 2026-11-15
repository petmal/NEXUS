"""Public-only constructive policy. Upper bound, never an optimality certificate."""

from __future__ import annotations

from functools import lru_cache
from itertools import product

from nexus.ontology.history.inference import Belief, common, indices, partitions
from nexus.ontology.history.laws import PULSES, READERS, words

# A small witness pool; every longer legal preparation still updates exactly.
QUERIES = tuple((h, c) for n in range(5) for h in product(range(4), repeat=n) for c in range(3))


@lru_cache(maxsize=2048)
def choose(mask: int):
    if common(mask):
        return None
    best = min(
        QUERIES,
        key=lambda query: (
            max((mask & m).bit_count() for m in partitions(*query)),
            sum((mask & m).bit_count() ** 2 for m in partitions(*query)),
            len(query[0]),
            query,
        ),
    )
    if any(mask & m == mask for m in partitions(*best)):
        raise ValueError("history witness pool cannot establish a winning procedure")
    return best


@lru_cache(maxsize=2048)
def bound(mask: int) -> tuple[int, int]:
    query = choose(mask)
    if query is None:
        return 0, len(words()[next(indices(common(mask)))])
    history, channel = query
    # Anneal one reusable survey, apply each pulse, read. This tree ignores
    # intermediate evidence. The live policy uses it: its separate all-world
    # conformance gate checks the same bound; greedy cost is not monotone.
    children = [bound(mask & m) for m in partitions(history, channel) if mask & m]
    return 1 + max(c[0] for c in children), len(history) + 2 + max(c[1] for c in children)


def public_policy(player, evidence):
    from nexus.models.actions import (
        FinishAction,
        MoveAction,
        OperateAction,
        ProbeAction,
        TakeAction,
    )
    from nexus.ontology.history.schema import Investigation
    from nexus.ontology.inference import Measurement

    from nexus.ontology.player_records import specification

    spec = specification(Investigation, evidence, family="history-coupled-v1")
    posterior = Belief(spec)

    def act(action):
        result = player.act(expected_turn=player.status().turn, action=action)
        if not result.ok:
            raise ValueError(f"history investigator failed: {result.message}")
        if action.type in ("probe", "operate") and action.machine != "anneal":
            payload = next(
                e["details"]["result"]["payload"] for e in result.events if "result" in e["details"]
            )
            posterior.observe(Measurement(action.machine, payload))
        return result

    act(TakeAction(artifact="seal"))
    survey = None
    if spec.resolved is None:
        result = act(TakeAction(artifact="stock"))
        survey = next(e["details"]["artifact"] for e in result.events if e["type"] == "take")
    if player.observe().room != spec.mission_room:
        act(MoveAction(target=spec.mission_room))
    while (query := choose(posterior.mask)) is not None:
        history, channel = query
        act(OperateAction(machine="anneal", artifact=survey))
        for mode in history:
            act(OperateAction(machine=PULSES[mode], artifact=survey))
        act(ProbeAction(machine=READERS[channel], artifact=survey))
    procedure = (
        spec.procedure
        if spec.procedure is not None
        else words()[next(indices(common(posterior.mask)))]
    )
    for mode in procedure:
        act(OperateAction(machine=PULSES[mode], artifact="seal"))
    return act(FinishAction())
