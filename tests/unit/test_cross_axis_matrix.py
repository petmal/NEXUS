"""Frozen controls, generic tasks and fail-closed source-bound exports."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from nexus.evaluation import cross_axis, interference
from nexus.evaluation.budget_diagnostic import science_projection
from nexus.evaluation.discovery import digest
from nexus.ontology.repair.qualification import source_binding
from nexus.provenance import source_digest

ROOT = Path(__file__).parents[2]


def matrix():
    return cross_axis.Pilot.model_validate_json((ROOT / "docs/cross-axis-matrix.json").read_text())


@pytest.mark.parametrize(
    ("index", "field", "value"),
    [
        (0, "seed", 79),
        (8, "suite", "rerun-core"),
        (32, "discovery", 5),
        (35, "resource", 1),
        (36, "source_id", "01"),
        (44, "expected_budget", 10),
        (54, "budget_profile", "standard"),
    ],
)
def test_frozen_inventory_rejects_changed_conditions(index, field, value):
    data = matrix().model_dump(mode="json")
    data["runs"][index][field] = value
    with pytest.raises(ValueError):
        cross_axis.Pilot.model_validate(data)


def test_suites_partition_all56_conditions_with_explicit_canary():
    pilot = matrix()
    groups = {suite: [c.id for c in pilot.runs if c.suite == suite] for suite in cross_axis.SUITES}
    assert [len(ids) for ids in groups.values()] == [4, 4, 12, 12, 16, 8]
    assert groups["canary-core"] == [f"interference-{i:02d}" for i in range(9, 13)]
    assert groups["canary-slack"] == [f"interference-{i:02d}" for i in range(25, 29)]
    assert len({row for ids in groups.values() for row in ids}) == 56
    assert groups["smoke-td"] == [f"S{i:02d}" for i in (*range(1, 13), *range(21, 25))]
    assert groups["smoke-pr"] == [f"S{i:02d}" for i in range(13, 21)]
    assert (pilot.recommended_tool_call_limit, pilot.max_turns) == (600, 650)


def test_original_interference_task_objects_are_exactly_preserved():
    pilot = matrix()
    original = interference.Pilot.model_validate_json(
        (ROOT / "docs/interference-matrix.json").read_text()
    )
    for cell, source in zip(pilot.runs[:32], original.runs, strict=True):
        assert cross_axis.task_for(cell, pilot) == interference.task_for(source, original)
        assert cell.source_id == source.id
        assert cell.ontology_options == source.options().model_dump()


def test_smoke_prompts_are_generic_and_service_inputs_preserve_each_condition():
    pilot = matrix()
    for cell in pilot.runs[32:]:
        task = cross_axis.task_for(cell, pilot)
        inputs = task["tool-selector"]["service-inputs"]["nexus"]
        assert task["name"] == f"NEXUS smoke-{cell.id}"
        assert task["prompt"] == cross_axis.PROMPT
        assert str(cell.seed) not in task["prompt"]
        assert "manifest and observe" in task["prompt"]
        assert "no external Python, source access or solver" in task["prompt"]
        assert "seal" not in task["prompt"] and "previews one operation" not in task["prompt"]
        assert inputs["science-family"] == cell.family
        assert inputs["seed"] == str(cell.seed)
        assert inputs["budget-profile"] == cell.budget_profile
        assert json.loads(inputs.get("ontology-options", "{}")) == cell.ontology_options


def test_dependency_matrix_bytes_are_bound(tmp_path, monkeypatch):
    pilot = matrix()
    paths = cross_axis.dependency_paths()
    changed = tmp_path / "interference.json"
    changed.write_text(paths["interference"].read_text() + "\n")
    monkeypatch.setattr(cross_axis, "dependency_paths", lambda: {**paths, "interference": changed})
    with pytest.raises(ValueError, match="matrix bytes"):
        cross_axis._dependencies(pilot)


def test_repair_controls_keep_obstruction_support_and_exact_budget_pair():
    pilot = matrix()
    results = {}
    for cell in pilot.runs[-4:]:
        ep = cell.generate()
        row, session = cross_axis._live_smoke(cell, ep)
        detail = cross_axis._repair_details(cell, ep, session)
        assert all(row["checks"].values()) and all(detail["checks"].values())
        assert detail["positive_reading_lower_bound"] == 3
        assert detail["untrimmed_common_repairs"] == 0
        assert detail["single_context_common_repairs"] == [0, 0]
        assert detail["live_acceptance_checks"] == 81
        results[cell.id] = ep, session
    left, ls = results["S22"]
    right, rs = results["S23"]
    assert (left.generation_metadata.action_budget, right.generation_metadata.action_budget) == (
        30,
        36,
    )
    assert science_projection(left) == science_projection(right)
    assert [r.action for r in ls.trace] == [r.action for r in rs.trace]
    assert [r.events for r in ls.trace] == [r.events for r in rs.trace]
    assert cross_axis._same_physics(results["S21"][0], left)


def fresh_fixture(pilot):
    """Only export's comparison boundary is mocked; real proof runs separately."""
    return {
        "version": cross_axis.VERSION,
        "status": "passed",
        "source_sha256": source_digest(),
        "sources": source_binding(),
        "matrix_sha256": digest(pilot.model_dump()),
        "dependency_matrix_sha256": pilot.dependency_matrix_sha256,
        "cells": [{"id": c.id, "checks": {"qualified": True}} for c in pilot.runs],
        "dependencies": {"stateful": {"kernel": {"independent_transition_checks": 641024}}},
        "scientific_contrasts": [{"checks": {"same_science_except_budget": True}}],
    }


def test_export_rejects_edited_nested_evidence_and_exports_complete_suites(tmp_path, monkeypatch):
    pilot = matrix()
    expected = fresh_fixture(pilot)
    monkeypatch.setattr(cross_axis, "_qualified", lambda unused: deepcopy(expected))
    report = deepcopy(expected)
    report["seconds"] = 12.5
    cross_axis.export_tasks(pilot, report, tmp_path)
    names = []
    for suite in cross_axis.SUITES:
        config = json.loads((tmp_path / f"nexus-cross-axis-{suite}-tasks.yaml").read_text())[
            "task-config"
        ]
        assert config["max-turns"] == 650
        assert config["tool-selector"]["tools"][0]["max-calls"] == 600
        names.extend(t["name"] for t in config["tasks"])
    assert len(names) == len(set(names)) == 56
    for change in ("source", "missing-cell", "selected-gate", "dependency", "contrast"):
        altered = deepcopy(report)
        if change == "source":
            altered["source_sha256"] = "0" * 64
        elif change == "missing-cell":
            altered["cells"].pop()
        elif change == "selected-gate":
            altered["cells"][55]["checks"].clear()
        elif change == "dependency":
            altered["dependencies"]["stateful"]["kernel"]["independent_transition_checks"] = 1
        else:
            altered["scientific_contrasts"][0]["checks"]["same_science_except_budget"] = False
        with pytest.raises(ValueError):
            cross_axis.export_tasks(pilot, altered, tmp_path)


@pytest.mark.slow
def test_full_current_source_preflight_and_export(tmp_path):
    pilot = matrix()
    report = cross_axis.preflight(pilot, tmp_path / "report.json")
    assert report["status"] == "passed"
    assert len(report["cells"]) == 56
    assert all(report["qualification_gates"].values())
    assert report["compositional_conformance"]["admitted_worlds"] == 615
    cross_axis.export_tasks(pilot, report, tmp_path)
    altered = deepcopy(report)
    altered["cells"][53]["qualification"]["untrimmed_common_repairs"] = 1
    with pytest.raises(ValueError, match="recomputed"):
        cross_axis.validate_report(pilot, altered)
