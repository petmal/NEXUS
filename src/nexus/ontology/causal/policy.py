"""Reference investigator uses explicit public evidence and a player-only interface."""

import json

from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    MoveAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.ontology.causal.inference import CausalBelief, choose, policy_bound, target_set
from nexus.ontology.causal.laws import WITNESS_EXPERIMENTS
from nexus.ontology.causal.schema import Investigation
from nexus.ontology.inference import Measurement


def public_policy(player, evidence: dict[str, str]):
    theory = json.loads(evidence["theory.json"])
    map_data = json.loads(evidence["map.json"])
    stock = player.observe().room
    functions = map_data.get("sector_functions", map_data["rooms"])
    lab = next(room for room, label in functions.items() if label == "Causal laboratory")
    spec = Investigation(
        theory=theory["theory_level"],
        discovery=theory["discovery_level"],
        known=theory["known"],
        supplied=theory["supplied"],
        resolved=theory["resolved"],
        stock_room=stock,
        mission_room=lab,
    )
    belief = CausalBelief(spec)

    def act(action):
        result = player.act(expected_turn=player.status().turn, action=action)
        if not result.ok:
            raise ValueError(f"public reference action failed: {result.message}")
        return result

    allow_preparation = spec.discovery != 2
    specimens = []
    for _ in range(policy_bound(belief.mask, allow_preparation)[0]):
        result = act(TakeAction(artifact="stock"))
        specimens.append(
            next(e["details"]["artifact"] for e in result.events if e["type"] == "take")
        )
    if lab != stock:
        act(MoveAction(target=lab))
    while (selected := choose(belief.mask, allow_preparation)) is not None:
        experiment = WITNESS_EXPERIMENTS[selected]
        artifact = specimens.pop()
        if experiment.instrument == "sensor":
            for point in experiment.history:
                act(ConfigureAction(machine="stage", settings=point))
                act(OperateAction(machine="stage", artifact=artifact))
                act(OperateAction(machine="pulse", artifact=artifact))
            act(ConfigureAction(machine="stage", settings=experiment.point))
            act(OperateAction(machine="stage", artifact=artifact))
        result = act(ProbeAction(machine=experiment.instrument, artifact=artifact))
        sample = next(
            e["details"]["result"]["payload"] for e in result.events if "result" in e["details"]
        )
        belief.observe(Measurement(experiment.instrument, sample))
    act(ConfigureAction(machine="board", settings=next(iter(target_set(belief.mask)))))
    return act(FinishAction())
