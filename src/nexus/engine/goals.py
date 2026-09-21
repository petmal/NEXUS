from __future__ import annotations

from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import WorldState


def _normalized(value):
    return value.value if hasattr(value, "value") else value


def evaluate_goal(goal: GoalPredicate, state: WorldState) -> bool:
    if goal.kind == GoalKind.ARTIFACT_FIELD:
        artifact = state.artifacts.get(goal.artifact_id or "")
        if artifact is None or goal.field is None:
            return False
        return _normalized(getattr(artifact, goal.field)) == _normalized(goal.value)
    if goal.kind == GoalKind.ARTIFACT_LOCATION:
        artifact = state.artifacts.get(goal.artifact_id or "")
        return artifact is not None and artifact.location == goal.value
    if goal.kind == GoalKind.PHASE_EQUALS:
        return state.phase == int(goal.value)
    if goal.kind == GoalKind.AND:
        return all(evaluate_goal(child, state) for child in goal.children)
    if goal.kind == GoalKind.OR:
        return any(evaluate_goal(child, state) for child in goal.children)
    if goal.kind == GoalKind.NOT:
        return not evaluate_goal(goal.children[0], state)
    raise ValueError(f"unsupported goal kind {goal.kind}")
