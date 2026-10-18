"""Public-only witness traverses the offline tree using live raw observations."""

import json

from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    MoveAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.ontology.transfer.laws import PROGRAMS, QUERIES
from nexus.ontology.transfer.reference import load


def public_policy(player, evidence):
    theory = json.loads(evidence["theory.json"])
    resolved = theory["resolved"]
    coupled = theory["coupled_reader"]

    def act(action):
        result = player.act(expected_turn=player.status().turn, action=action)
        if not result.ok:
            raise ValueError(f"public investigator failed: {result.message}")
        return result

    act(TakeAction(artifact="seal"))
    specimens = []
    if resolved is None:
        for stock in ("stock", "reference-stock") if coupled else ("stock",):
            result = act(TakeAction(artifact=stock))
            specimens.append(
                next(e["details"]["artifact"] for e in result.events if e["type"] == "take")
            )
    if player.observe().room != "array":
        act(MoveAction(target="array"))
    if resolved is None:
        nodes = load()["coupled" if coupled else "calibrated"]["nodes"]
        node = 0
        while node >= 0:
            query, *children = nodes[node]
            material, index = divmod(query, len(QUERIES))
            specimen = specimens[material]
            act(ConfigureAction(machine="stage", settings=QUERIES[index]))
            act(OperateAction(machine="stage", artifact=specimen))
            result = act(ProbeAction(machine="sensor", artifact=specimen))
            sample = next(
                e["details"]["result"]["payload"] for e in result.events if "result" in e["details"]
            )
            node = children[sample["reading"]]
            if node is None:
                raise ValueError("live observation contradicts public policy")
        resolved = PROGRAMS[-node - 1]
    act(ConfigureAction(machine="doser", settings=tuple(resolved)))
    act(OperateAction(machine="doser", artifact="seal"))
    return act(FinishAction())
