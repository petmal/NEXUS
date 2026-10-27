"""Admission and export preserve the intended paired 32-cell pilot."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from nexus.evaluation.interference import Pilot, export_tasks, preflight, task_for

ROOT = Path(__file__).parents[2]


def matrix():
    return Pilot.model_validate_json((ROOT / "docs/interference-matrix.json").read_text())


def test_matrix_rejects_missing_pairs_wrong_seeds_and_budget_assignments():
    for field, value in (("seed", 41), ("resource", 1), ("coupling", "independent")):
        data = matrix().model_dump(mode="json")
        data["runs"][1][field] = value
        with pytest.raises(ValueError):
            Pilot.model_validate(data)


def test_tasks_keep_selection_labels_operator_only_and_preserve_model_settings():
    pilot = matrix()
    config = json.loads((ROOT / "examples/mindtrial/nexus-interference-config.yaml").read_text())[
        "config"
    ]
    for cell in pilot.runs:
        task = task_for(cell, pilot)
        inputs = task["tool-selector"]["service-inputs"]["nexus"]
        assert json.loads(inputs["ontology-options"]) == cell.options().model_dump()
        assert inputs["theory-level"] == inputs["discovery-level"] == inputs["planning-level"] == 0
        assert str(cell.seed) not in task["prompt"] and "horizon" not in task["prompt"]
        assert inputs.keys() <= config["services"][0]["input-env"].keys()
    assert config["providers"][0]["retry-policy"]["max-retry-attempts"] == 0
    assert all(
        config[k][0]["image"] == "nexus:interference-v1"
        for k in ("tools", "services", "validators")
    )


def test_preflight_export_recomputes_costs_and_all_proof_fields(tmp_path):
    pilot = matrix()
    report = preflight(pilot, tmp_path / "preflight.json")
    export_tasks(pilot, report, tmp_path)
    for suite in ("core", "slack"):
        name = f"nexus-interference-{suite}-tasks.yaml"
        assert (tmp_path / name).read_bytes() == (ROOT / "examples/mindtrial" / name).read_bytes()
    for kind in ("source", "checks", "minimum", "regression", "unreachable"):
        altered = deepcopy(report)
        if kind == "source":
            altered["sources"]["cli.py"] = "wrong"
        elif kind == "checks":
            altered["cells"][0]["checks"].pop("complete_transition_checks")
        elif kind == "minimum":
            altered["cells"][0]["physical_minimum"] += 1
        elif kind == "regression":
            altered["cells"][0]["minimum_coordinate_goal_breaks"] = 0
        else:
            altered["cells"][0]["bank_contiguous_operations"] = None
        with pytest.raises(ValueError):
            export_tasks(pilot, altered, tmp_path)
