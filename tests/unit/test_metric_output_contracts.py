"""Validate actual producer output against the shipped schemas, with no network I/O."""

from functools import cache
import json
from pathlib import Path
import runpy

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
import pytest
from typer.testing import CliRunner

from nexus.cli import app
from nexus.generator import generate_episode
from nexus.io import save_episode
from nexus.models.actions import WaitAction
from nexus.ontology.catalog import runtime_for
from nexus.protocol.http import create_single_session_app
from nexus.protocol.investigation_metrics import (
    AuditedDecisionMissionPerformance,
    DecisionMissionPerformance,
    MissionPerformance,
    SCIENCE_SCHEMA_URL,
)
from nexus.protocol.session import PERFORMANCE_SCHEMA_URL, Session
from nexus.solver import solve

ROOT = Path(__file__).resolve().parents[2]
TERMINAL = "terminal-performance-v1"


SCHEMA_TOOL = runpy.run_path(str(ROOT / "scripts/metric_schemas.py"))
contracts = SCHEMA_TOOL["contracts"]


def test_published_schemas_and_operator_serialization_contracts():
    for validator in contracts().values():
        Draft202012Validator.check_schema(validator.schema)
    for name, model in SCHEMA_TOOL["MODELS"].items():
        assert contracts()[name].schema == SCHEMA_TOOL["output_schema"](name, model)
    for version, model in enumerate(
        (MissionPerformance, DecisionMissionPerformance, AuditedDecisionMissionPerformance), 1
    ):
        assert contracts()[f"performance-mission-v{version}"].schema == model.model_json_schema()


@cache
def episode(case):
    options = {
        "legacy": dict(planning_level=0),
        "controller": dict(
            axis_version=2, theory_level=0, discovery_level=0, planning_level=0, resource_pressure=0
        ),
        "mission": dict(
            axis_version=2,
            science_family="coupled-repair-v1",
            theory_level=3,
            discovery_level=5,
            planning_level=0,
            resource_pressure=1,
        ),
        "planning": dict(
            axis_version=2,
            science_family="stateful-interference-v1",
            planning_level=0,
            resource_pressure=2,
            ontology_options={"coupling": "independent", "horizon": "short"},
        ),
    }[case]
    return generate_episode(107 if case == "planning" else 17, **options)


@pytest.mark.parametrize(
    ("case", "key", "label"),
    [
        ("legacy", "$schema", PERFORMANCE_SCHEMA_URL),
        ("controller", "$schema", SCIENCE_SCHEMA_URL),
        ("mission", "version", "mission-performance-v1"),
        ("planning", "version", "mission-performance-v3"),
    ],
)
def test_real_performance_and_operator_log(case, key, label, caplog):
    ep = episode(case)
    caplog.set_level("INFO", logger="nexus.operator")
    with TestClient(create_single_session_app(ep, extended_diagnostics=True)) as client:
        plan = solve(ep).plan
        assert plan
        for turn, action in enumerate(plan):
            response = client.post(
                "/action", json={"expected_turn": turn, "action": action.model_dump(mode="json")}
            )
            response.raise_for_status()
            body = response.json()
            assert body["ok"]
            if turn < len(plan) - 1:
                assert "performance" not in body
        won = body["performance"]
        assert won[key] == label and won["terminal_status"] == "won"
        contracts()[TERMINAL].validate(won)
        assert client.post("/finalize").json()["performance"] == won
    # Capture the actual serialized log (the emitter adds episode_id and trigger).
    with TestClient(create_single_session_app(ep, extended_diagnostics=True)):
        pass
    with TestClient(create_single_session_app(ep, extended_diagnostics=True)) as client:
        failed = client.post("/finalize").json()["performance"]
        assert failed["terminal_status"] == "failed" and failed["actions_used"] == 0
        contracts()[TERMINAL].validate(failed)
    marker = "NEXUS operator summary: "
    summaries = [
        json.loads(r.getMessage()[len(marker) :])
        for r in caplog.records
        if r.getMessage().startswith(marker)
    ]
    assert {s["status"] for s in summaries} == {"won", "failed", "active"}
    for summary in summaries:
        contracts()["operator-summary-v4"].validate(summary)
    if case == "controller":
        assert all(s["initial_action_budget"] is None for s in summaries)
    if case != "legacy":
        snapshot = Session(ep).operator_snapshot()["performance"]
        assert snapshot["terminal_status"] == "active"
        assert not contracts()[TERMINAL].is_valid(snapshot)

    # A well-shaped object with the wrong version, or a snapshot that is still
    # active, must not silently enter a dataset of terminal model outcomes.
    for invalid in (
        {k: v for k, v in won.items() if k != key},
        {**won, key: "future-unknown"},
        {**won, "terminal_status": "active"},
    ):
        assert not contracts()[TERMINAL].is_valid(invalid)
    if case == "planning":
        diagnostic = won["decision_diagnostics"]
        assert diagnostic["readings"] is None
        for change in ({"first_intervention_turn": "never"}, {"readings": []}):
            assert not contracts()[TERMINAL].is_valid(
                {**won, "decision_diagnostics": {**diagnostic, **change}}
            )


def test_v2_output_from_decision_family_without_optional_audit_hook(monkeypatch):
    ep = episode("planning")
    monkeypatch.setattr(runtime_for(ep.public.investigation), "measurement_features", None)
    with TestClient(create_single_session_app(ep)) as client:
        result = client.post("/finalize").json()["performance"]
    assert result["version"] == "mission-performance-v2"
    assert "decision_diagnostics" not in result
    contracts()[TERMINAL].validate(result)
    assert not contracts()[TERMINAL].is_valid({**result, "version": "mission-performance-v3"})
    assert not contracts()[TERMINAL].is_valid({**result, "target_count_meaning": "world count"})


def test_failed_performance_from_exhausted_action_budget():
    session = Session(episode("planning"))
    budget = session.state.resources.actions_remaining
    assert budget and budget > 0
    for turn in range(budget):
        response = session.act(turn, WaitAction())
        assert response.ok
    record = response.model_dump(mode="json", exclude_none=True)["performance"]
    assert (record["terminal_status"], record["termination_reason"]) == ("failed", "action_budget")
    assert record["actions_used"] == budget and record["budget_remaining"] == 0
    contracts()[TERMINAL].validate(record)


@pytest.mark.parametrize("case", ["legacy", "controller", "mission", "planning"])
def test_serialized_cli_metric_outputs(case, tmp_path):
    save_episode(episode(case), tmp_path)
    private = str(tmp_path / "private.json")
    runner = CliRunner()
    inspected = runner.invoke(app, ["inspect", private])
    assert inspected.exit_code == 0, inspected.output
    metadata = json.loads(inspected.stdout)["generation_metadata"]
    assert metadata == json.loads(Path(private).read_text())["generation_metadata"]
    contracts()["generation-metadata-v1"].validate(metadata)
    solved = runner.invoke(app, ["solve", private])
    assert solved.exit_code == 0, solved.output
    result = json.loads(solved.stdout)
    validator = contracts()["solver-result-v1"]
    validator.validate(result)
    # Every action in the serialized plan must carry its type.
    del result["plan"][0]["type"]
    assert not validator.is_valid(result)
