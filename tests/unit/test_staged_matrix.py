"""Matrix claims fail closed; no single-seed depth claim from a worst-case policy."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from nexus.evaluation.staged import Pilot, preflight

MATRIX = Path(__file__).parents[2] / "docs/staged-repair-matrix.json"


def test_matrix_verified_shortcuts_theory_controls_and_nonmonotone_information(tmp_path):
    report = preflight(Pilot.model_validate_json(MATRIX.read_text()), tmp_path / "report.json")
    assert report["status"] == "passed" and len(report["cells"]) == 10
    rows = {r["id"]: r for r in report["cells"]}
    assert rows["01"]["actions"] == 10
    assert (
        rows["02"]["mechanisms"]
        == rows["03"]["mechanisms"]
        == rows["04"]["mechanisms"]
        == rows["05"]["mechanisms"]
        == rows["10"]["mechanisms"]
    )
    assert rows["03"]["positive_certificate_readings"] == 6
    assert rows["04"]["positive_certificate_readings"] == 4
    assert rows["09"]["positive_certificate_readings"] == 3
    assert rows["10"]["budget"] - rows["04"]["budget"] == 6
    assert (
        len(
            {
                json.dumps(r["mechanisms"], sort_keys=True)
                for r in report["cells"]
                if "mechanisms" in r
            }
        )
        == 4
    )
    assert not report["deep_tier_admitted"]


def test_stale_pass_replaced_on_source_failure(tmp_path, monkeypatch):
    from nexus.ontology.repair import qualification

    output = tmp_path / "report.json"
    output.write_text('{"status":"passed"}')

    def fail():
        raise OSError("source unavailable")

    monkeypatch.setattr(qualification, "source_binding", fail)
    with pytest.raises(OSError):
        preflight(Pilot.model_validate_json(MATRIX.read_text()), output)
    assert json.loads(output.read_text())["status"] == "blocked"


def test_inflated_seed_certificate_is_rejected(tmp_path):
    raw = json.loads(MATRIX.read_text())
    raw["runs"] = [raw["runs"][8]]
    raw["runs"][0]["expected_certificate_readings"] = 6
    with pytest.raises(ValueError, match="failed checks"):
        preflight(Pilot.model_validate(raw), tmp_path / "report.json")
    assert json.loads((tmp_path / "report.json").read_text())["status"] == "blocked"


@pytest.mark.parametrize("content", [None, "{", '{"version":"staged-repair-pilot-v1"}'])
def test_cli_invalid_matrix_replaces_stale_pass(tmp_path, content):
    matrix, output = tmp_path / "matrix.json", tmp_path / "report.json"
    if content is not None:
        matrix.write_text(content)
    output.write_text('{"status":"passed","old":true}')
    result = subprocess.run(
        [
            sys.executable,
            str(MATRIX.parents[1] / "scripts/preflight_staged_repair.py"),
            "--matrix",
            str(matrix),
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode != 0
    report = json.loads(output.read_text())
    assert report["status"] == "blocked" and report["error"]
    assert "old" not in report
