"""Constructive policy receives only player operations and public evidence."""

import json

from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    MoveAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.ontology.dynamics.inference import DynamicsBelief, choose, policy_bound, target_set
from nexus.ontology.dynamics.laws import experiments
from nexus.ontology.dynamics.schema import Investigation
from nexus.ontology.inference import Measurement


def public_policy(player, evidence):
    theory = json.loads(evidence["theory.json"])
    resolved = theory["resolved"]
    spec = Investigation(
        theory=0 if resolved is not None else 3,
        discovery=0 if resolved is not None else 5,
        stock_room=player.observe().room,
        resolved=resolved,
    )
    belief = DynamicsBelief(spec)

    def act(action):
        result = player.act(expected_turn=player.status().turn, action=action)
        if not result.ok:
            raise ValueError(f"public investigator action failed: {result.message}")
        return result

    act(TakeAction(artifact="seal"))
    specimens = []
    for _ in range(policy_bound(belief.mask)[0]):
        result = act(TakeAction(artifact="stock"))
        specimens.append(
            next(e["details"]["artifact"] for e in result.events if e["type"] == "take")
        )
    if spec.stock_room != spec.mission_room:
        act(MoveAction(target=spec.mission_room))
    while (selected := choose(belief.mask)) is not None:
        experiment = experiments(2)[selected]
        artifact = specimens.pop()
        for point in experiment.history:
            act(ConfigureAction(machine="stage", settings=point))
            act(OperateAction(machine="stage", artifact=artifact))
            act(OperateAction(machine="pulse", artifact=artifact))
        if experiment.instrument == "sensor" or experiment.point != (0, 0, 0):
            act(ConfigureAction(machine="stage", settings=experiment.point))
            act(OperateAction(machine="stage", artifact=artifact))
        result = act(ProbeAction(machine=experiment.instrument, artifact=artifact))
        sample = next(
            e["details"]["result"]["payload"] for e in result.events if "result" in e["details"]
        )
        belief.observe(Measurement(experiment.instrument, sample))
    act(ConfigureAction(machine="doser", settings=next(iter(target_set(belief.mask)))))
    act(OperateAction(machine="doser", artifact="seal"))
    return act(FinishAction())
