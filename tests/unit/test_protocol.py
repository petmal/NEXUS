from nexus.generator import generate_episode
from nexus.models import ACTION_ADAPTER
from nexus.protocol.session import Session


def test_session_retries_are_idempotent():
    episode = generate_episode(42)
    session = Session(episode)
    first_action = ACTION_ADAPTER.validate_python(episode.reference_plan[0])
    response = session.act(0, first_action)
    assert response.ok
    assert session.state.turn == 1
    duplicate = session.act(0, first_action)
    assert duplicate.ok and duplicate.duplicate
    assert session.state.turn == 1


def test_turn_mismatch_is_rejected():
    session = Session(generate_episode(43))
    action = ACTION_ADAPTER.validate_python({"type": "wait"})
    response = session.act(99, action)
    assert not response.ok
    assert session.state.turn == 0
