import pytest

from nexus.generator import generate_episode, qualify_episode
from nexus.generator.evidence import candidates_matching_csv
from nexus.generator.rules import enumerate_transformation_rules
from nexus.models.actions import ProbeAction
from nexus.models.world import Shape, TerminalStatus
from nexus.solver import solve
from nexus.solver.belief import solve_guaranteed_policy
from nexus.engine.replay import execute_with_trace


pytestmark = pytest.mark.slow


def _probe_value(result, artifact_id: str):
    for value in result.initial_action_values:
        if isinstance(value.action, ProbeAction) and value.action.artifact == artifact_id:
            return value
    raise AssertionError(f"missing initial probe for {artifact_id}")


def test_d4_selects_informative_auxiliary_context_over_predictable_distractor():
    episode = generate_episode(
        17,
        discovery_level=4,
        planning_level=1,
        verifier_secret="d4-proof-secret",
    )
    metadata = episode.generation_metadata

    assert metadata.discovery_level == 4
    assert metadata.machine_count == 1
    assert metadata.required_probe_count == 1
    assert metadata.epistemic_artifact_id == "A2"
    assert metadata.distractor_artifact_id == "A3"
    assert metadata.guaranteed_policy_action_count > 0

    artifacts = episode.public.initial_state.artifacts
    assert set(artifacts) == {"A1", "A2", "A3"}
    assert {artifact.shape for artifact in artifacts.values()} == set(Shape)
    assert all(artifact.location == "@inventory" for artifact in artifacts.values())
    assert episode.public.initial_state.machines["M1"].room_id == "R0"

    candidates = candidates_matching_csv(
        episode.public.evidence_files["measurements.csv"],
        enumerate_transformation_rules(),
    )
    policy = solve_guaranteed_policy(
        episode,
        candidate_rules_by_machine={"M1": candidates},
        max_actions=metadata.guaranteed_policy_action_count + 2,
    )
    assert policy.solvable
    assert policy.viable_hypothesis_count >= 2
    assert policy.optimal_worst_case_actions == metadata.guaranteed_policy_action_count

    informative = _probe_value(policy, "A2")
    distractor = _probe_value(policy, "A3")
    mission_probe = _probe_value(policy, "A1")

    assert informative.discriminative is True
    assert informative.worst_case_total_actions == policy.optimal_worst_case_actions
    assert mission_probe.worst_case_total_actions == policy.optimal_worst_case_actions

    assert distractor.discriminative is False
    assert distractor.outcome_count == 1
    assert distractor.worst_case_total_actions == policy.optimal_worst_case_actions + 1

    report = qualify_episode(episode)
    assert report.passed, report.model_dump()
    assert report.checks["discovery_profile"]
    assert report.checks["guaranteed_policy"]


def test_d4_hidden_world_remains_independently_solver_winnable_and_replayable():
    episode = generate_episode(
        73,
        discovery_level=4,
        planning_level=2,
        verifier_secret="d4-proof-secret",
    )

    solved = solve(episode)
    assert solved.solvable
    assert solved.optimal_action_count == episode.generation_metadata.optimal_action_count

    final, trace = execute_with_trace(episode, list(solved.plan))
    assert final.terminal_status == TerminalStatus.WON
    assert trace
    assert qualify_episode(episode).passed



def test_d4_shape_roles_are_semantic_not_hardcoded():
    episode = generate_episode(
        17,
        discovery_level=4,
        planning_level=1,
        verifier_secret="d4-role-proof-secret",
    )

    assert {
        artifact.shape
        for artifact in episode.public.initial_state.artifacts.values()
    } == set(Shape)
