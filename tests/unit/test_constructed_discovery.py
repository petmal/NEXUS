import pytest

from nexus.engine.engine import step
from nexus.engine.rules import apply_effect
from nexus.engine.replay import execute_with_trace
from nexus.generator import generate_episode, qualify_episode
from nexus.generator.constructed import (
    CONSTRUCTOR_VALUE,
    DISTRACTOR_VALUE,
    constructed_mission_rules,
    constant_value_rule,
)
from nexus.models import ACTION_ADAPTER, TerminalStatus
from nexus.models.actions import OperateAction, ProbeAction
from nexus.solver import solve
from nexus.solver.belief import solve_guaranteed_policy


pytestmark = pytest.mark.slow


def _initial_action_value(result, action_type, machine_id: str, artifact_id: str):
    for value in result.initial_action_values:
        action = value.action
        if (
            isinstance(action, action_type)
            and action.machine == machine_id
            and action.artifact == artifact_id
        ):
            return value
    raise AssertionError(
        f"missing initial {action_type.__name__} for {machine_id}/{artifact_id}"
    )


def _candidate_rules(episode):
    diagnostic_shape = episode.public.initial_state.artifacts["A2"].shape
    return {
        "M1": list(constructed_mission_rules(diagnostic_shape)),
        "M2": [constant_value_rule(CONSTRUCTOR_VALUE)],
        "M3": [constant_value_rule(DISTRACTOR_VALUE)],
    }


def test_d5_constructs_a_strictly_lower_cost_diagnostic_experiment():
    episode = generate_episode(
        17,
        discovery_level=5,
        planning_level=1,
        verifier_secret="d5-proof-secret",
    )
    metadata = episode.generation_metadata

    assert metadata.discovery_level == 5
    assert metadata.machine_count == 3
    assert metadata.required_probe_count == 1
    assert metadata.epistemic_artifact_id == "A2"
    assert metadata.distractor_artifact_id == "A3"
    assert metadata.epistemic_machine_id == "M2"
    assert metadata.distractor_machine_id == "M3"
    assert metadata.guaranteed_policy_action_count > metadata.optimal_action_count
    assert metadata.constructed_probe_outcomes == 4

    assert set(episode.public.initial_state.artifacts) == {"A1", "A2", "A3"}
    assert set(episode.public.initial_state.machines) == {"M1", "M2", "M3"}
    assert all(
        artifact.location == "@inventory"
        for artifact in episode.public.initial_state.artifacts.values()
    )
    assert all(
        machine.room_id == "R0"
        for machine in episode.public.initial_state.machines.values()
    )

    policy = solve_guaranteed_policy(
        episode,
        candidate_rules_by_machine=_candidate_rules(episode),
        max_actions=metadata.guaranteed_policy_action_count + 2,
    )
    assert policy.solvable
    assert policy.viable_hypothesis_count == 4
    assert policy.optimal_worst_case_actions == metadata.guaranteed_policy_action_count

    constructor = _initial_action_value(policy, OperateAction, "M2", "A2")
    direct_probe = _initial_action_value(policy, ProbeAction, "M1", "A1")
    distractor = _initial_action_value(policy, OperateAction, "M3", "A3")

    assert constructor.worst_case_total_actions == policy.optimal_worst_case_actions
    assert direct_probe.worst_case_total_actions is not None
    assert direct_probe.worst_case_total_actions > policy.optimal_worst_case_actions
    assert distractor.worst_case_total_actions is not None
    assert distractor.worst_case_total_actions > policy.optimal_worst_case_actions

    report = qualify_episode(episode)
    assert report.passed, report.model_dump()
    assert report.checks["discovery_profile"]
    assert report.checks["guaranteed_policy"]
    assert report.checks["constructed_experiment"]


def test_d5_constructed_context_discriminates_all_winning_phases():
    episode = generate_episode(
        73,
        discovery_level=5,
        planning_level=1,
        verifier_secret="d5-proof-secret",
    )
    candidates = _candidate_rules(episode)

    constructor = ACTION_ADAPTER.validate_python(
        {"type": "operate", "machine": "M2", "artifact": "A2"}
    )
    constructed_results = set()
    for mission_rule in candidates["M1"]:
        world = episode.model_copy(deep=True)
        world.rules[world.machine_rules["M1"]] = mission_rule
        result = step(world.public.initial_state, constructor, world)
        assert result.ok
        artifact = result.state.artifacts["A2"]
        constructed_results.add(artifact.value)

    # M2 itself is deterministic; it constructs one public test context.
    assert constructed_results == {CONSTRUCTOR_VALUE}

    diagnostic_value = next(iter(constructed_results))
    assert diagnostic_value == CONSTRUCTOR_VALUE

    constructed = episode.public.initial_state.artifacts["A2"].model_copy(
        update={"value": CONSTRUCTOR_VALUE}
    )
    outputs = {
        apply_effect(mission_rule, constructed, 0).value
        for mission_rule in candidates["M1"]
    }
    assert outputs == {0, 1, 2, 3}

    # Qualification independently recomputes the same partition; metadata exposes only the count,
    # never the selected hidden winning phase.
    assert episode.generation_metadata.constructed_probe_outcomes == 4


def test_d5_hidden_world_is_independently_solver_winnable_and_replayable():
    episode = generate_episode(
        211,
        discovery_level=5,
        planning_level=2,
        verifier_secret="d5-proof-secret",
    )

    solved = solve(episode)
    assert solved.solvable
    assert solved.optimal_action_count == episode.generation_metadata.optimal_action_count

    final, trace = execute_with_trace(episode, list(solved.plan))
    assert final.terminal_status == TerminalStatus.WON
    assert trace
    assert qualify_episode(episode).passed
