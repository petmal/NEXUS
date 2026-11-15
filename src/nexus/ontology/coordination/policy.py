"""Exact known-law reference constructed solely from public evidence."""


from nexus.ontology.coordination.planner import actions_for, optimal
from nexus.ontology.coordination.schema import Investigation


def public_policy(player, evidence):
    from nexus.ontology.player_records import specification

    spec = specification(Investigation, evidence, family="stateful-coordination-v1")
    result = None
    for action in actions_for(spec, optimal(spec).modes):
        result = player.act(expected_turn=player.status().turn, action=action)
        if not result.ok:
            raise ValueError(f"coordination public policy failed: {result.message}")
    if result is None:
        raise ValueError("coordination public plan is empty")
    return result
