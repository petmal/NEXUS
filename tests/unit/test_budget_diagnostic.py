"""Qualification is preserved, budget is the only scientific pair difference."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from nexus.evaluation.budget_diagnostic import (
    BudgetDiagnostic,
    preflight,
    science_projection,
    verify_binding,
)
from nexus.generator import generate_episode, qualify_episode
from nexus.models.episode import PrivateEpisode


def matrix():
    return BudgetDiagnostic.model_validate_json(
        Path("docs/budget-diagnostic-matrix.json").read_text()
    )


def test_eight_controlled_live_executions_and_stale_report(tmp_path):
    diagnostic = matrix()
    report = preflight(diagnostic, tmp_path / "report.json")
    assert report["status"] == "diagnostic-ready"
    assert len(report["rows"]) == 8
    assert [r["reference_actions"] for r in report["rows"]] == [24] * 8
    verify_binding(diagnostic, report)
    for changed in ("pair", "model"):
        forged = deepcopy(report)
        forged["rows"][0][changed] = "wrong"
        with pytest.raises(ValueError, match="inventory"):
            verify_binding(diagnostic, forged)
    forged = deepcopy(report)
    forged["pairs"] = [forged["pairs"][0]] * 4
    with pytest.raises(ValueError, match="controlled"):
        verify_binding(diagnostic, forged)
    forged = deepcopy(report)
    forged["pairs"][0]["same_science"] = "yes"
    with pytest.raises(ValueError, match="controlled"):
        verify_binding(diagnostic, forged)
    report["source_sha256"] = "stale"
    with pytest.raises(ValueError, match="stale"):
        verify_binding(diagnostic, report)


def test_profile_is_named_qualified_and_does_not_change_science():
    standard, diagnostic = [cell.generate() for cell in matrix().runs[:2]]
    assert science_projection(standard) == science_projection(diagnostic)
    assert "budget_profile" not in standard.generation_metadata.model_dump()
    assert diagnostic.generation_metadata.action_budget == 36
    assert diagnostic.generation_metadata.resource_allowance == 9
    assert PrivateEpisode.model_validate_json(diagnostic.model_dump_json()) == diagnostic
    for episode in (standard, diagnostic):
        changed = episode.model_copy(deep=True)
        changed.public.initial_state.resources.actions_remaining += 1
        assert not qualify_episode(changed).passed
    changed = diagnostic.model_dump(mode="json")
    changed["generation_metadata"]["budget_profile"] = "standard"
    with pytest.raises(ValueError, match="resources"):
        PrivateEpisode.model_validate(changed)


@pytest.mark.parametrize(
    "overrides",
    [
        {"planning_level": 0},
        {"theory_level": 0, "discovery_level": 0},
        {"science_family": "coupled-dynamics-v1"},
        {"budget_profile": "plus99"},
    ],
)
def test_unsupported_profile_combinations_rejected(overrides):
    kwargs = {
        "axis_version": 2,
        "science_family": "compositional-repair-v1",
        "theory_level": 3,
        "discovery_level": 5,
        "planning_level": 1,
        "resource_pressure": 1,
        "budget_profile": "diagnostic-plus6",
    }
    kwargs.update(overrides)
    with pytest.raises(ValueError):
        generate_episode(438, **kwargs)


@pytest.mark.parametrize(
    "field,value", [("seed", 493), ("budget_profile", "standard"), ("model", "grok")]
)
def test_mismatched_pair_fails_closed(field, value):
    data = json.loads(matrix().model_dump_json())
    data["runs"][1][field] = value
    with pytest.raises(ValueError):
        BudgetDiagnostic.model_validate(data)


@pytest.mark.parametrize(
    "field,value",
    [("model", "different-model"), ("reasoning", "low"), ("max_completion_tokens", 1000)],
)
def test_different_model_conditions_require_a_new_matrix_design(field, value):
    data = json.loads(matrix().model_dump_json())
    data["models"]["gemini"][field] = value
    with pytest.raises(ValueError, match="pinned pilot"):
        BudgetDiagnostic.model_validate(data)


def test_service_cli_accepts_matrix_environment(monkeypatch):
    import uvicorn
    from fastapi.testclient import TestClient
    from typer.testing import CliRunner

    from nexus.cli import app

    seen = []

    def serve(application, **kwargs):
        with TestClient(application) as client:
            seen.append(client.get("/status").json()["actions_remaining"])

    monkeypatch.setattr(uvicorn, "run", serve)
    for key, value in matrix().runs[1].environment().items():
        monkeypatch.setenv(key, value)
    result = CliRunner().invoke(app, ["serve-session"])
    assert result.exit_code == 0, result.exception
    assert seen == [36]
