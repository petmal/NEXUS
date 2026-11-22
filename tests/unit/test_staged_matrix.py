"""Matrix claims fail closed; no single-seed depth claim from a worst-case policy."""

import json
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


def test_inflated_seed_certificate_is_rejected(tmp_path):
    raw = json.loads(MATRIX.read_text())
    raw["runs"] = [raw["runs"][8]]
    raw["runs"][0]["expected_certificate_readings"] = 6
    with pytest.raises(ValueError, match="failed checks"):
        preflight(Pilot.model_validate(raw), tmp_path / "report.json")
    assert json.loads((tmp_path / "report.json").read_text())["status"] == "blocked"
