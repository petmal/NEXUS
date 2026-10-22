"""Pilot admission fails closed; operator YAML preserves the qualified controls."""

import json
import re
from pathlib import Path

import pytest

from nexus.evaluation.revision import Pilot, preflight, topology_key

ROOT = Path(__file__).parents[2]


def matrix():
    return json.loads((ROOT / "docs/model-revision-matrix.json").read_text())


def test_complete_preflight_and_supported_action_bounds(tmp_path):
    report = preflight(Pilot.model_validate(matrix()), tmp_path / "report.json")
    assert report["status"] == "passed"
    assert len(report["cells"]) == 10
    assert all(all(c["checks"].values()) for c in report["cells"])
    assert report["cells"][0]["minimum_supported_actions"] == 4
    assert report["cells"][8]["minimum_reading_only_certificate"] == 1
    assert report["empirical_difficulty_calibrated"] is False
    mixed = report["cells"][6]["mixed_feedback_witness"]
    assert (mixed["readings"], mixed["failed_finishes"], mixed["actions"]) == (3, 1, 13)
    assert mixed["actions"] > report["cells"][6]["minimum_supported_actions"]


@pytest.mark.parametrize("change", ["shallow", "duplicate"])
def test_unsuitable_worlds_are_blocked_with_checkpoint(tmp_path, change):
    raw = matrix()
    raw["runs"][7]["seed"] = 468 if change == "shallow" else raw["runs"][2]["seed"]
    with pytest.raises(ValueError, match="failed admission|duplicate behavioral"):
        preflight(Pilot.model_validate(raw), tmp_path / "report.json")
    assert json.loads((tmp_path / "report.json").read_text())["status"] == "blocked"


def test_pair_and_role_validation_blocks_confounded_comparisons():
    raw = matrix()
    raw["runs"][2]["seed"] += 1
    with pytest.raises(ValueError, match="identical physical"):
        Pilot.model_validate(raw)
    raw = matrix()
    raw["runs"][0]["theory"] = 3
    with pytest.raises(ValueError, match="disclosure mismatch"):
        Pilot.model_validate(raw)


def test_topology_coverage_ignores_mode_names_and_hidden_reservoir_names():
    from nexus.ontology.revision.laws import EDGES

    program = (3, 4, 8, 10)
    assert topology_key(program) == topology_key(program[2:] + program[:2])
    mapping = (0, 2, 3, 1)
    renamed = tuple(EDGES.index((mapping[a], mapping[b])) for a, b in (EDGES[e] for e in program))
    assert topology_key(program) == topology_key(renamed)


def test_exported_mindtrial_inputs_match_qualified_matrix():
    rows = matrix()["runs"]
    text = (ROOT / "examples/mindtrial/nexus-revision-tasks.yaml").read_text()
    blocks = text.split("service-inputs:")[1:]
    assert len(blocks) == len(rows) == 10
    for block, row in zip(blocks, rows):
        for field, value in {
            "science-family": row["family"],
            "seed": row["seed"],
            "theory-level": row["theory"],
            "discovery-level": row["discovery"],
            "resource-pressure": row["resource"],
            "planning-level": row["planning"],
        }.items():
            found = re.search(r"^\s+" + field + r": [\'\"]?([^\s\'\"]+)", block, re.MULTILINE)
            assert found and found.group(1) == str(value)
        if row["guidance"] is None:
            assert "ontology-options" not in block
        else:
            found = re.search(r"ontology-options: '(.*)'", block)
            assert found and json.loads(found.group(1)) == {"guidance": row["guidance"]}
    config = (ROOT / "examples/mindtrial/nexus-revision-config.yaml").read_text()
    assert "./nexus-revision-tasks.yaml" in config
    assert "ontology-options: NEXUS_ONTOLOGY_OPTIONS" in config
    assert re.findall(r"^\s+image: (\S+)", config, re.MULTILINE) == ["nexus:model-revision-v1"] * 3
    assert "max-calls: 120" in text and "max-turns: 160" in text
    assert "ignore-whitespace: false" in text and "trim-lines: false" in text


def test_source_read_failure_cannot_leave_an_old_passed_report(tmp_path, monkeypatch):
    from nexus.evaluation import revision

    path = tmp_path / "report.json"
    path.write_text('{"status":"passed"}')

    def fail():
        raise OSError("source unavailable")

    monkeypatch.setattr(revision, "source_digest", fail)
    with pytest.raises(OSError, match="source unavailable"):
        preflight(Pilot.model_validate(matrix()), path)
    assert json.loads(path.read_text())["status"] == "blocked"
