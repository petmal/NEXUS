"""Independent small-world oracles for qualification and solver soundness."""

from collections import deque
from itertools import product

import pytest

from nexus.engine.engine import step
from nexus.engine.replay import execute_with_trace
from nexus.generator import generate_episode, qualify_episode
from nexus.models.actions import DropAction, FinishAction, MoveAction, TakeAction
from nexus.models.episode import PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalPredicate
from nexus.models.rules import Condition, Effect
from nexus.models.world import Artifact, Machine, Resources, Room, TerminalStatus, WorldState
from nexus.solver import solve
from nexus.solver.belief import solve_compressed_physical, solve_guaranteed_policy


@pytest.mark.parametrize("damage", ["waits", "illegal", "empty", "schema", "after_win"])
def test_qualification_executes_the_stored_reference_plan(damage):
    episode = generate_episode(17, planning_level=0)
    assert qualify_episode(episode).passed
    if damage == "waits":
        episode.reference_plan = tuple({"type": "wait"} for _ in episode.reference_plan)
    elif damage == "illegal":
        episode.reference_plan = ({"type": "take", "artifact": "missing"}, *episode.reference_plan[1:])
    elif damage == "empty":
        episode.reference_plan = ()
    elif damage == "schema":
        episode.reference_plan = ({"type": "unknown"}, *episode.reference_plan[1:])
    else:
        episode.reference_plan = (*episode.reference_plan, {"type": "wait"})
    report = qualify_episode(episode)
    assert not report.passed
    assert not report.checks["reference_plan_wins"]
    assert not report.checks["victory_receipt_present"]


def location_goal(location):
    return GoalPredicate(kind="artifact_location", artifact_id="A1", value=location)


def negate(goal):
    return GoalPredicate(kind="not", children=(goal,))


def location_episode(goal, location):
    return PrivateEpisode(
        public=PublicEpisode(
            episode_id="location-oracle",
            description="Two rooms and one portable artifact",
            rooms={r: Room(id=r, label=r) for r in ("R0", "R1")},
            edges=(("R0", "R1"),),
            phase_modulus=1,
            initial_state=WorldState(
                agent_room="R0",
                artifacts={"A1": Artifact(id="A1", location=location, shape="circle",
                                          pattern="plain", orientation="north", value=0,
                                          polarity="positive")},
                machines={"M1": Machine(id="M1", room_id="R0", uses_remaining=1)},
                resources=Resources(actions_remaining=8),
            ),
            goal=goal,
        ),
        rules={"identity": Effect(kind="add_mod", field="value", amount=0, modulus=11)},
        machine_rules={"M1": "identity"},
        verifier_secret="oracle-secret",
    )


def location_oracle(episode):
    """Unit-action BFS without goal-based pruning or production solver helpers.

    Only movement, inventory and finish can affect these goals. The identity
    machine, probe and wait leave every relevant state coordinate unchanged.
    """
    queue = deque([(episode.public.initial_state, 0)])
    seen = set()
    while queue:
        state, count = queue.popleft()
        key = state.agent_room, state.artifacts["A1"].location
        if key in seen:
            continue
        seen.add(key)
        actions = [FinishAction(), TakeAction(artifact="A1"), DropAction(artifact="A1")]
        actions += [MoveAction(target=r) for r in episode.public.rooms]
        for action in actions:
            result = step(state, action, episode)
            if not result.ok:
                continue
            if result.state.terminal_status == TerminalStatus.WON:
                return count + 1
            if result.state.terminal_status == TerminalStatus.ACTIVE:
                queue.append((result.state, count + 1))
    return None


LOCATION_GOALS = [location_goal(r) for r in ("R0", "R1", "@inventory")]
BOOLEAN_GOALS = (
    LOCATION_GOALS
    + [negate(g) for g in LOCATION_GOALS]
    + [negate(negate(g)) for g in LOCATION_GOALS]
    + [GoalPredicate(kind=kind, children=children)
       for kind in ("and", "or")
       for children in product(LOCATION_GOALS, [negate(g) for g in LOCATION_GOALS])]
    + [negate(GoalPredicate(kind="or", children=tuple(LOCATION_GOALS[:2])))]
)


@pytest.mark.parametrize("location", ["R0", "R1", "@inventory"])
@pytest.mark.parametrize("goal", BOOLEAN_GOALS)
def test_boolean_location_costs_match_unpruned_oracle(goal, location):
    episode = location_episode(goal, location)
    minimum = location_oracle(episode)
    for result in (solve(episode), solve_compressed_physical(episode)):
        assert result.solvable == (minimum is not None)
        assert result.optimal_action_count == minimum
        if result.solvable:
            final, trace = execute_with_trace(episode, list(result.plan))
            assert final.terminal_status == TerminalStatus.WON and trace[-1].victory_code
    result = solve_guaranteed_policy(
        episode, candidate_rules_by_machine={"M1": [episode.rules["identity"]]},
        max_actions=8, include_action_values=False,
    )
    assert result.solvable == (minimum is not None)
    assert result.optimal_worst_case_actions == minimum


@pytest.mark.parametrize("payload", [
    {"kind": "phase_equals", "value": value} for value in (False, True, 0.5, "0")
] + [
    {"kind": "artifact_field", "artifact_id": "A1", "field": field, "value": 0}
    for field in ("missing", "location", "id", "sample")
] + [
    {"kind": "artifact_field", "artifact_id": "A1", "field": "value", "value": value}
    for value in (False, True, 0.5, "0")
] + [
    {"kind": "artifact_field", "artifact_id": "A1", "field": "shape", "value": "hexagon"},
    {"kind": "artifact_location", "artifact_id": "A1", "value": 0},
])
def test_invalid_goal_atoms_fail_before_play(payload):
    with pytest.raises(ValueError):
        GoalPredicate.model_validate(payload)


@pytest.mark.parametrize("value", [False, True, 0.5, "0"])
def test_rule_phase_conditions_do_not_coerce_the_declared_phase(value):
    with pytest.raises(ValueError):
        Condition(kind="phase_equals", value=value)


@pytest.mark.parametrize("budget", [None, 5])
@pytest.mark.parametrize("uses", [None, 2])
def test_unlimited_resources_have_the_same_physical_and_guaranteed_cost(budget, uses):
    from nexus.models.actions import OperateAction

    episode = location_episode(
        GoalPredicate(kind="artifact_field", artifact_id="A1", field="value", value=2),
        "@inventory",
    )
    episode.rules["identity"] = Effect(kind="add_mod", field="value", amount=1, modulus=11)
    episode.public.initial_state.machines["M1"].uses_remaining = uses
    episode.public.initial_state.resources.actions_remaining = budget
    # This remains a schema-valid standalone compiled legacy world.
    episode = PrivateEpisode.model_validate_json(episode.model_dump_json())
    actions = [OperateAction(machine="M1", artifact="A1")] * 2 + [FinishAction()]
    final, trace = execute_with_trace(episode, actions)
    assert final.terminal_status == TerminalStatus.WON and trace[-1].victory_code
    assert final.resources.actions_remaining == (None if budget is None else budget - 3)
    assert final.machines["M1"].uses_remaining == (None if uses is None else 0)
    for result in (solve(episode), solve_compressed_physical(episode)):
        assert result.solvable and result.optimal_action_count == 3
    result = solve_guaranteed_policy(
        episode, candidate_rules_by_machine={"M1": [episode.rules["identity"]]},
        max_actions=4, include_action_values=False,
    )
    assert result.solvable and result.optimal_worst_case_actions == 3
