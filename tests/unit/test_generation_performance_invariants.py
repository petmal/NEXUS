from __future__ import annotations

import pytest

from nexus.generator import generate_episode, qualify_episode
from nexus.generator.generator import _generate_episode_core
from nexus.solver import solve


def test_internal_unqualified_core_is_still_a_valid_world():
    episode = _generate_episode_core(17017, discovery_level=2, planning_level=2, qualify_result=False, verifier_secret="proof")
    report = qualify_episode(episode)
    assert report.passed, report.model_dump()


def test_generation_solver_counters_are_diagnostics_not_semantic_invariants():
    episode = generate_episode(18181, discovery_level=1, planning_level=1, verifier_secret="proof")
    episode.generation_metadata.solver_visited_states += 123
    episode.generation_metadata.solver_max_frontier_size += 456
    assert qualify_episode(episode).passed


@pytest.mark.slow
def test_d5_p3_r1_returns_a_fully_qualified_exact_world():
    episode = generate_episode(17, discovery_level=5, planning_level=3, resource_pressure=1, verifier_secret="proof")
    report = qualify_episode(episode)
    assert report.passed, report.model_dump()
    ordinary = solve(episode)
    assert ordinary.solvable
    assert ordinary.optimal_action_count == episode.generation_metadata.optimal_action_count
    assert len(episode.reference_plan) == ordinary.optimal_action_count
