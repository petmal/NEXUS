"""Constructive public-only witness; no claim of minimum reading/action cost."""

import json
from collections import Counter

from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    MoveAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.ontology.staged.laws import MECHANISMS, repair, response, route
from nexus.ontology.staged.schema import SEALS, Investigation, Truth


def choose_tag(candidates) -> int:
    return min(
        range(3),
        key=lambda u: (max(Counter(response(m, u) for m in candidates).values()), u),
    )


def public_policy(player, evidence):
    spec = Investigation.model_validate(json.loads(evidence["theory.json"])["specification"])

    def act(action):
        result = player.act(expected_turn=player.status().turn, action=action)
        if not result.ok:
            raise ValueError(f"staged public investigator failed: {result.message}")
        return result

    for name in SEALS:
        act(TakeAction(artifact=name))
    if player.observe().room != spec.mission_room:
        act(MoveAction(target=spec.mission_room))
    known = []
    if spec.resolved is None:
        for stage in range(3):
            candidates = tuple(
                m
                for m in MECHANISMS
                if spec.known_exponents is None or m.exponent == spec.known_exponents[stage]
            )
            carrier = route(known[-1]) if stage and spec.linked else 0
            act(ConfigureAction(machine="reader", settings=(stage, carrier)))
            while len(candidates) > 1:
                tag = choose_tag(candidates)
                result = act(ProbeAction(machine="reader", artifact=SEALS[tag]))
                sample = next(
                    e["details"]["result"]["payload"]
                    for e in result.events
                    if "result" in e["details"]
                )
                candidates = tuple(m for m in candidates if response(m, tag) == sample["reading"])
                if not candidates:
                    raise ValueError("public observation contradicts disclosed prior")
            known.append(candidates[0])
    doses = spec.repair if spec.repair is not None else repair(Truth(mechanisms=tuple(known)))
    for seal, dose in zip(SEALS, doses):
        act(ConfigureAction(machine="trimmer", settings=dose))
        act(OperateAction(machine="trimmer", artifact=seal))
    return act(FinishAction())
