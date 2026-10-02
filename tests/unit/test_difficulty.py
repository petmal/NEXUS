import pytest

from nexus.engine.replay import execute_with_trace
from nexus.generator import generate_episode, qualify_episode
from nexus.models import TerminalStatus
from nexus.models.episode import PlayerManifest
from nexus.solver import solve


@pytest.mark.parametrize(
    ("discovery_level", "expected_probes", "machine_count"),
    [(0, 0, 1), (1, 0, 1), (2, 1, 1), (3, 2, 2)],
)
def test_discovery_profiles_are_mechanical_guarantees(
    discovery_level, expected_probes, machine_count
):
    episode = generate_episode(
        7000 + discovery_level,
        discovery_level=discovery_level,
        planning_level=1,
        verifier_secret="test-secret",
    )
    metadata = episode.generation_metadata

    assert metadata.discovery_level == discovery_level
    assert metadata.required_probe_count == expected_probes
    assert metadata.machine_count == machine_count
    assert metadata.action_budget == episode.public.initial_state.resources.actions_remaining
    assert metadata.recommended_tool_call_limit > metadata.action_budget

    if discovery_level == 0:
        assert metadata.direct_target_example is True
        assert metadata.mission_relevant_prediction_counts["M1"] == 1
    elif discovery_level == 1:
        assert metadata.direct_target_example is False
        assert metadata.mission_relevant_prediction_counts["M1"] == 1
    elif discovery_level == 2:
        assert metadata.direct_target_example is False
        assert metadata.mission_relevant_prediction_counts["M1"] > 1
    else:
        assert metadata.direct_target_example is False
        assert set(metadata.mission_relevant_prediction_counts) == {"M1", "M2"}
        assert all(value > 1 for value in metadata.mission_relevant_prediction_counts.values())
        assert metadata.requires_both_machines is True
        assert metadata.reverse_order_reaches_goal is False
        assert "measurements_M2.csv" in episode.public.evidence_files

    report = qualify_episode(episode)
    assert report.passed, report.model_dump()
    assert report.checks["discovery_profile"]
    assert report.checks["reference_plan_wins"]


@pytest.mark.parametrize("discovery_level", [0, 1, 2, 3])
@pytest.mark.parametrize("planning_level", [0, 1, 2])
def test_every_profile_combination_generates_a_winnable_world(
    discovery_level, planning_level
):
    episode = generate_episode(
        8100 + discovery_level * 10 + planning_level,
        discovery_level=discovery_level,
        planning_level=planning_level,
        verifier_secret="test-secret",
    )

    solved = solve(episode)
    assert solved.solvable
    assert solved.optimal_action_count == episode.generation_metadata.optimal_action_count
    assert solved.optimal_action_count <= episode.generation_metadata.action_budget

    final, _ = execute_with_trace(episode, list(solved.plan))
    assert final.terminal_status == TerminalStatus.WON
    assert qualify_episode(episode).passed


def test_level_three_reference_plan_uses_both_machines_in_order():
    episode = generate_episode(
        9303,
        discovery_level=3,
        planning_level=1,
        verifier_secret="test-secret",
    )
    operations = [
        action["machine"]
        for action in episode.reference_plan
        if action["type"] == "operate"
    ]
    assert operations == ["M1", "M2"]


def test_generation_is_deterministic_for_seed_and_difficulty_profile():
    kwargs = {
        "discovery_level": 3,
        "planning_level": 2,
        "verifier_secret": "fixed-secret",
    }
    first = generate_episode(10101, **kwargs)
    second = generate_episode(10101, **kwargs)

    assert first == second


@pytest.mark.parametrize(
    ("keyword", "value"),
    [("discovery_level", -1), ("discovery_level", 5), ("planning_level", -1), ("planning_level", 3)],
)
def test_invalid_public_difficulty_levels_fail_fast(keyword, value):
    kwargs = {"discovery_level": 0, "planning_level": 1}
    kwargs[keyword] = value
    with pytest.raises(ValueError):
        generate_episode(1, **kwargs)


def test_operator_metadata_is_not_player_visible():
    episode = generate_episode(4402, discovery_level=2, planning_level=1)
    manifest = PlayerManifest.from_episode(episode.public).model_dump(mode="json")

    assert "generation_metadata" not in manifest
    assert "optimal_action_count" not in str(manifest)
    assert "required_probe_count" not in str(manifest)



def _artifact_intrinsic_state(artifact):
    return (
        artifact.shape,
        artifact.pattern,
        artifact.orientation,
        artifact.value,
        artifact.polarity,
    )


def test_d0_d1_d2_share_one_machine_scenario_family_at_fixed_planning_level():
    episodes = [
        generate_episode(
            17,
            discovery_level=discovery_level,
            planning_level=1,
            verifier_secret="paired-secret",
        )
        for discovery_level in (0, 1, 2)
    ]

    family_ids = {episode.generation_metadata.scenario_family_id for episode in episodes}
    family_attempts = {
        episode.generation_metadata.scenario_family_attempt for episode in episodes
    }
    assert len(family_ids) == 1
    assert len(family_attempts) == 1

    first = episodes[0]
    for episode in episodes[1:]:
        assert episode.rules == first.rules
        assert episode.machine_rules == first.machine_rules
        assert (
            episode.generation_metadata.transformation_phases
            == first.generation_metadata.transformation_phases
        )
        assert episode.public.rooms == first.public.rooms
        assert episode.public.edges == first.public.edges
        assert episode.public.initial_state.artifacts["A1"] == first.public.initial_state.artifacts["A1"]
        assert episode.public.initial_state.machines == first.public.initial_state.machines
        assert episode.public.goal == first.public.goal

    evidence = [episode.public.evidence_files["measurements.csv"] for episode in episodes]
    assert len(set(evidence)) == 3


def test_planning_profiles_share_mechanics_and_evidence_but_not_role_placement_contract():
    episodes = [
        generate_episode(
            73,
            discovery_level=1,
            planning_level=planning_level,
            verifier_secret="paired-secret",
        )
        for planning_level in (0, 1, 2)
    ]

    assert len({episode.generation_metadata.scenario_family_id for episode in episodes}) == 1
    assert len(
        {episode.generation_metadata.scenario_family_attempt for episode in episodes}
    ) == 1

    first = episodes[0]
    first_artifact = first.public.initial_state.artifacts["A1"]
    for episode in episodes[1:]:
        artifact = episode.public.initial_state.artifacts["A1"]
        assert episode.rules == first.rules
        assert episode.machine_rules == first.machine_rules
        assert (
            episode.generation_metadata.transformation_phases
            == first.generation_metadata.transformation_phases
        )
        assert _artifact_intrinsic_state(artifact) == _artifact_intrinsic_state(first_artifact)
        assert episode.public.evidence_files == first.public.evidence_files

    assert all(
        episode.generation_metadata.topology_attempt >= 0
        for episode in episodes
    )


def test_d3_planning_profiles_share_two_machine_scenario_family():
    episodes = [
        generate_episode(
            211,
            discovery_level=3,
            planning_level=planning_level,
            verifier_secret="paired-secret",
        )
        for planning_level in (0, 1, 2)
    ]

    assert len({episode.generation_metadata.scenario_family_id for episode in episodes}) == 1
    assert len(
        {episode.generation_metadata.scenario_family_attempt for episode in episodes}
    ) == 1

    first = episodes[0]
    first_artifact = first.public.initial_state.artifacts["A1"]
    for episode in episodes[1:]:
        assert episode.rules == first.rules
        assert (
            episode.generation_metadata.transformation_phases
            == first.generation_metadata.transformation_phases
        )
        assert _artifact_intrinsic_state(
            episode.public.initial_state.artifacts["A1"]
        ) == _artifact_intrinsic_state(first_artifact)
        assert episode.public.evidence_files == first.public.evidence_files
