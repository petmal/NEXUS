import pytest

from nexus.generator import generate_episode, qualify_episode
from nexus.generator.difficulty import MAX_PHYSICAL_OPTIMAL_ACTIONS


@pytest.mark.parametrize("seed", [17, 1009, 65537])
@pytest.mark.parametrize("discovery_level", [0, 1, 2, 3])
@pytest.mark.parametrize("planning_level", [0, 1, 2])
def test_difficulty_profiles_are_stable_across_seed_sample(
    seed, discovery_level, planning_level
):
    """Catch profile combinations that only work for hand-picked seeds."""
    episode = generate_episode(
        seed,
        discovery_level=discovery_level,
        planning_level=planning_level,
        max_attempts=96,
        verifier_secret="sampling-secret",
    )
    metadata = episode.generation_metadata

    assert metadata.generation_attempt < 96
    assert 0 < metadata.optimal_action_count <= MAX_PHYSICAL_OPTIMAL_ACTIONS
    assert metadata.action_budget >= metadata.optimal_action_count
    assert metadata.recommended_tool_call_limit > metadata.action_budget

    report = qualify_episode(episode)
    assert report.passed, report.model_dump()
