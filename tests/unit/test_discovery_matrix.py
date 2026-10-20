"""Preflight must reject inflated difficulty claims and stale successful reports."""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from nexus.evaluation.discovery import Pilot, preflight

ROOT = Path(__file__).parents[2]
MATRIX = ROOT / "docs/discovery-pocs-matrix.json"


def test_full_matrix_covers_distinct_mechanisms_and_controls_with_exact_claims(
    tmp_path, monkeypatch
):
    from nexus.evaluation import discovery

    ticks = iter(range(100))
    monkeypatch.setattr(discovery, "perf_counter", lambda: next(ticks))
    report = preflight(Pilot.model_validate_json(MATRIX.read_text()), tmp_path / "report.json")
    assert report["status"] == "passed" and len(report["cells"]) == 10
    assert report["seconds"] == 21
    rows = {r["id"]: r for r in report["cells"]}
    assert rows["03"]["certificate_reading_lower"] == rows["03"]["certificate_reading_upper"] == 3
    assert rows["04"]["certificate_reading_lower"] == 2
    assert rows["03"]["predictive_states"] == rows["04"]["predictive_states"] == 27
    assert rows["03"]["mechanism"] == rows["05"]["mechanism"]
    assert rows["08"]["mechanism"] == rows["10"]["mechanism"]
    assert rows["05"]["budget"] is None and rows["03"]["budget"] == 64
    assert rows["08"]["certificate_reading_lower"] == rows["09"]["certificate_reading_upper"] == 2
    assert all(r["recovery_actions_including_injected_failure"] <= 64 for r in report["cells"])
    assert not report["deep_tier_admitted"]


def test_source_failure_replaces_stale_success(tmp_path, monkeypatch):
    from nexus.ontology.repair import qualification

    def fail():
        raise OSError("source unavailable")

    monkeypatch.setattr(qualification, "source_binding", fail)
    out = tmp_path / "report.json"
    out.write_text('{"status":"passed"}')
    with pytest.raises(OSError):
        preflight(Pilot.model_validate_json(MATRIX.read_text()), out)
    assert json.loads(out.read_text())["status"] == "blocked"


def test_inflated_certificate_or_hidden_shortcut_cannot_be_admitted(tmp_path):
    raw = json.loads(MATRIX.read_text())
    raw["runs"][2]["expected_certificate_lower"] = 4
    raw["runs"][2]["expected_certificate_upper"] = 4
    out = tmp_path / "report.json"
    with pytest.raises(ValueError, match="failed checks"):
        preflight(Pilot.model_validate(raw), out)
    assert json.loads(out.read_text())["status"] == "blocked"


@pytest.mark.parametrize("content", [None, "{", '{"version":"discovery-pocs-pilot-v1"}'])
def test_cli_invalid_input_removes_stale_success(tmp_path, content):
    matrix, out = tmp_path / "input.json", tmp_path / "output.json"
    if content is not None:
        matrix.write_text(content)
    out.write_text('{"status":"passed","old":true}')
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/preflight_discovery.py"),
            "--matrix",
            str(matrix),
            "--output",
            str(out),
        ],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode != 0
    report = json.loads(out.read_text())
    assert report["status"] == "blocked" and "old" not in report


def test_committed_yaml_service_inputs_match_qualified_matrix():
    # Check the generated scalar service-input blocks without requiring a runtime
    # YAML dependency. Complete YAML parsing is also performed during export.
    text = (ROOT / "examples/mindtrial/nexus-discovery-tasks.yaml").read_text()
    blocks = text.split("service-inputs:")[1:]
    rows = json.loads(MATRIX.read_text())["runs"]
    assert len(blocks) == len(rows) == 10
    for block, row in zip(blocks, rows):
        expected = {
            "axis-version": 2,
            "science-family": row["family"],
            "seed": row["seed"],
            "theory-level": row["theory"],
            "discovery-level": row["discovery"],
            "planning-level": 0,
            "resource-pressure": row["resource"],
            "budget-profile": "standard",
        }
        for name, value in expected.items():
            found = re.search(r"^\s+" + name + r": ['\"]?([^\s'\"]+)", block, re.MULTILINE)
            assert found and found.group(1) == str(value)
    config = (ROOT / "examples/mindtrial/nexus-discovery-config.yaml").read_text()
    assert "nexus:discovery-pocs-v1" in config and "./nexus-discovery-tasks.yaml" in config
    assert re.findall(r"^\s+image: (\S+)", config, re.MULTILINE) == ["nexus:discovery-pocs-v1"] * 3
