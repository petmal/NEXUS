import logging

import pytest

from nexus.diagnostics import generation_diagnostics, timed_stage
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


def test_generation_summary_retains_repeated_stages_and_failure_without_private_details(caplog):
    @generation_diagnostics
    def operation():
        with timed_stage("generation.core"):
            for _ in range(3):
                with timed_stage("policy.minimax"):
                    pass
        with timed_stage("generation.theory"):
            with timed_stage("policy.minimax"):
                raise RuntimeError("private-rule-secret")

    with caplog.at_level(logging.INFO, logger="nexus.generation"):
        with pytest.raises(RuntimeError):
            operation()
    summary = caplog.records[-1].generation_summary
    assert summary["event"] == "error"
    core = summary["stages"]["generation.core/policy.minimax"]
    theory = summary["stages"]["generation.theory/policy.minimax"]
    assert core["count"] == 3 and core["errors"] == 0
    assert theory["count"] == 1 and theory["errors"] == 1
    assert summary["wall_seconds"] >= core["wall_seconds"] >= 0
    assert summary["cpu_seconds"] >= core["cpu_seconds"] >= 0
    assert "private-rule-secret" not in caplog.text
    # Each generation has a fresh collector, including after an exception.
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="nexus.generation"):
        with pytest.raises(RuntimeError):
            operation()
    assert caplog.records[-1].generation_summary["stages"]["generation.core/policy.minimax"]["count"] == 3


def test_summary_survives_a_short_container_log_tail(caplog):
    @generation_diagnostics
    def operation():
        with timed_stage("generation.core"):
            pass
        for _ in range(60):
            with timed_stage("generation.qualification"):
                pass

    with caplog.at_level(logging.INFO, logger="nexus.generation"):
        operation()
    tail = caplog.text.splitlines()[-50:]
    assert "event=generation_summary" in tail[-1]
    assert '"generation.core"' in tail[-1]
    assert '"count": 60' in tail[-1]
