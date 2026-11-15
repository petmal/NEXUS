"""Public-only investigator; construction and evidence support remain separate."""

import json

from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.ontology.discovery.domains import module
from nexus.ontology.inference import Measurement
from nexus.ontology.player_records import discovery_family, specification


def public_policy(player, evidence):
    theory = json.loads(evidence["theory.json"])
    family = discovery_family(theory)
    spec = specification(module(family, "schema").Investigation, evidence, family=family)

    def act(action):
        response = player.act(expected_turn=player.status().turn, action=action)
        if not response.ok:
            raise ValueError(f"discovery public policy failed: {response.message}")
        return response

    if not any(a.id == "carrier" for a in player.observe().carried_artifacts):
        act(TakeAction(artifact="carrier"))
    construction = theory.get("resolved_construction")
    if construction is None:
        posterior = module(family, "inference").Belief(spec)
        while (query := posterior.choose_query()) is not None:
            act(ConfigureAction(machine="reader", settings=query))
            response = act(ProbeAction(machine="reader", artifact="carrier"))
            reading = next(
                e["details"]["result"]["payload"]["reading"]
                for e in response.events
                if "result" in e["details"]
            )
            posterior.observe(Measurement("reader", reading))
        construction = posterior.common_decisions()[0]
    act(ConfigureAction(machine="assembler", settings=construction))
    act(OperateAction(machine="assembler", artifact="carrier"))
    return act(FinishAction())
