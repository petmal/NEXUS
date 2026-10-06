import logging

import pytest

from nexus.diagnostics import timed_stage
from nexus.generator import generate_episode
from nexus.solver.belief import _POLICY_RESULT_CACHE


def test_stage_logs_failure_without_disclosing_exception_details(caplog):
    with caplog.at_level(logging.INFO, logger="nexus.generation"):
        with pytest.raises(ValueError, match="private detail"):
            with timed_stage("test.failure"):
                raise ValueError("private detail")
    assert "event=start" in caplog.text
    assert "event=error" in caplog.text
    assert "private detail" not in caplog.text
    assert caplog.records[-1].generation_timing["seconds"] >= 0


def test_timing_does_not_change_compiled_episode_or_disclose_private_data(caplog):
    options = dict(discovery_level=2, planning_level=0, verifier_secret="private-test-secret")
    _POLICY_RESULT_CACHE.clear()
    with caplog.at_level(logging.WARNING, logger="nexus.generation"):
        quiet = generate_episode(17017, **options)
    assert not caplog.records
    _POLICY_RESULT_CACHE.clear()
    with caplog.at_level(logging.INFO, logger="nexus.generation"):
        timed = generate_episode(17017, **options)
    assert timed.model_dump() == quiet.model_dump()
    stages = [r.generation_timing for r in caplog.records if hasattr(r, "generation_timing")]
    assert {s["stage"] for s in stages} >= {
        "generation.core", "policy.hypothesis_physical", "policy.minimax",
        "policy.witness", "policy.action_values",
    }
    assert "private-test-secret" not in caplog.text
    assert timed.public.episode_id not in caplog.text
    assert "17017" not in caplog.text
