"""Constructive witness reads only public evidence and actual tool responses."""

import json

from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    MoveAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.ontology.compositional.inference import Belief, audit, choose
from nexus.ontology.compositional.laws import QUERIES, REPAIRS
from nexus.ontology.compositional.schema import Investigation
from nexus.ontology.inference import Measurement


def public_policy(player, evidence):
    resolved = json.loads(evidence["theory.json"])["resolved"]
    spec = Investigation(
        theory=0 if resolved is not None else 3,
        discovery=0 if resolved is not None else 5,
        stock_room=player.observe().room,
        resolved=resolved,
    )
    belief = Belief(spec)

    def act(action):
        result = player.act(expected_turn=player.status().turn, action=action)
        if not result.ok:
            raise ValueError(f"public investigator failed: {result.message}")
        return result

    act(TakeAction(artifact="seal"))
    survey = None
    if resolved is None:
        result = act(TakeAction(artifact="stock"))
        survey = next(e["details"]["artifact"] for e in result.events if e["type"] == "take")
    if spec.stock_room != spec.mission_room:
        act(MoveAction(target=spec.mission_room))
    while (selected := choose(belief.mask)) is not None:
        if survey is None:
            raise ValueError("unresolved control without a survey")
        mode, point, trims = QUERIES[selected]
        act(ConfigureAction(machine="stage", settings=(mode, *point, *trims, 0, 0)))
        act(OperateAction(machine="stage", artifact=survey))
        result = act(ProbeAction(machine="sensor", artifact=survey))
        payload = next(
            e["details"]["result"]["payload"] for e in result.events if "result" in e["details"]
        )
        belief.observe(Measurement("sensor", payload))
    doses = tuple(resolved) if resolved is not None else REPAIRS[audit().common(belief.mask)[0]]
    act(ConfigureAction(machine="doser", settings=doses))
    act(OperateAction(machine="doser", artifact="seal"))
    return act(FinishAction())
