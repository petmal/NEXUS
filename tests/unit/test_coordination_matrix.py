"""Matrix admission/export checks preserve the planned paired experiment."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from nexus.evaluation.coordination import Pilot, export_tasks, preflight, task_for

ROOT = Path(__file__).parents[2]


def pilot():
    return Pilot.model_validate_json((ROOT / "docs/coordination-matrix.json").read_text())


def test_pilot_rejects_duplicate_and_missing_matched_conditions():
    data = pilot().model_dump(mode="json")
    data["runs"][1]["coupling"] = data["runs"][0]["coupling"]
    with pytest.raises(ValueError, match="matched core"):
        Pilot.model_validate(data)
    data = pilot().model_dump(mode="json")
    data["runs"][23]["banks"] = 2
    with pytest.raises(ValueError, match="matched spatial"):
        Pilot.model_validate(data)


def test_tasks_use_public_controls_and_operator_only_options():
    config = json.loads((ROOT / "examples/mindtrial/nexus-coordination-config.yaml").read_text())[
        "config"
    ]
    matrix = pilot()
    for cell in matrix.runs:
        task = task_for(cell, matrix)
        inputs = task["tool-selector"]["service-inputs"]["nexus"]
        assert json.loads(inputs["ontology-options"]) == cell.options().model_dump()
        assert inputs["theory-level"] == inputs["discovery-level"] == 0
        assert inputs.keys() <= config["services"][0]["input-env"].keys()
        assert str(cell.seed) not in task["prompt"]
        assert "reference" not in task["prompt"].lower()
    assert len([c for c in matrix.runs if c.suite == "core"]) == 16
    assert len([c for c in matrix.runs if c.suite == "spatial"]) == 8
    assert len([c for c in matrix.runs if c.suite == "slack"]) == 16
    assert all(
        config[k][0]["image"] == "nexus:coordination-v1"
        for k in ("tools", "services", "validators")
    )
    assert config["providers"][0]["retry-policy"]["max-retry-attempts"] == 0
    assert config["providers"][0]["client-config"]["api-key"] == ""


def test_export_requires_complete_current_proof_and_consistent_costs(tmp_path):
    matrix = pilot()
    report = preflight(matrix, tmp_path / "current-preflight.json")
    export_tasks(matrix, report, tmp_path)
    for suite in ("core", "spatial", "slack"):
        name = f"nexus-coordination-{suite}-tasks.yaml"
        assert (tmp_path / name).read_bytes() == (ROOT / "examples/mindtrial" / name).read_bytes()
    for change in ("source", "row", "proof", "budget", "gap"):
        altered = deepcopy(report)
        if change == "source":
            altered["sources"]["cli.py"] = "stale"
        elif change == "row":
            altered["cells"][0]["seed"] += 1
        elif change == "proof":
            altered["cells"][0]["checks"].pop("compiled_contract")
        elif change == "budget":
            altered["cells"][0]["action_budget"] += 1
        else:
            coupled = next(
                c for c in altered["cells"] if c["suite"] == "core" and c["coupling"] == "coupled"
            )
            coupled["bank_contiguous_minimum"] = coupled["physical_minimum"]
            coupled["interleaving_gap"] = 0
        with pytest.raises(ValueError):
            export_tasks(matrix, altered, tmp_path)
