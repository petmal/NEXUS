"""Exact known-law reference constructed solely from public evidence."""

import json

from nexus.ontology.interference.planner import actions_for, optimal
from nexus.ontology.interference.schema import Investigation


def public_policy(player, evidence):
    spec = Investigation.model_validate(json.loads(evidence["theory.json"])["specification"])
    result = None
    for action in actions_for(spec, optimal(spec).modes):
        result = player.act(expected_turn=player.status().turn, action=action)
        if not result.ok:
            raise ValueError(f"interference public policy failed: {result.message}")
    if result is None:
        raise ValueError("interference public plan is empty")
    return result
