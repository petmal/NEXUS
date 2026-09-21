import pytest

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import given, settings, strategies as st

from nexus.engine.canonical import canonical_hash
from nexus.engine.engine import step
from nexus.generator import generate_episode
from nexus.models import WaitAction


@settings(max_examples=10, deadline=None)
@given(st.integers(min_value=0, max_value=10_000))
def test_same_state_and_action_are_deterministic(seed):
    episode = generate_episode(seed)
    state = episode.public.initial_state
    left = step(state, WaitAction(), episode)
    right = step(state, WaitAction(), episode)
    assert left.ok == right.ok
    assert canonical_hash(left.state) == canonical_hash(right.state)
    assert canonical_hash(state) == canonical_hash(episode.public.initial_state)
