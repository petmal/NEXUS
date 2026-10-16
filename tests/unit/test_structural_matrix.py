"""Matrix admission is a separate, current-source operator gate."""

from pathlib import Path

import pytest

from nexus.evaluation.structural import Pilot, preflight, verify_binding


def test_validated_pilot_and_stale_binding(tmp_path):
    pilot = Pilot.model_validate_json(Path("docs/structural-model-matrix.json").read_text())
    report = preflight(pilot, tmp_path / "report.json")
    assert all(report["coverage"].values())
    verify_binding(pilot, report)
    report["source_sha256"] = "stale"
    with pytest.raises(ValueError, match="stale"):
        verify_binding(pilot, report)


def test_duplicate_world_and_wrong_fixture_fail_closed(tmp_path):
    data = Pilot.model_validate_json(
        Path("docs/structural-model-matrix.json").read_text()
    ).model_dump(mode="json")
    data["runs"][7]["seed"] = data["runs"][6]["seed"] + 615
    with pytest.raises(ValueError, match="duplicate"):
        Pilot.model_validate(data)
    data["runs"][7]["seed"] = 1
    pilot = Pilot.model_validate(data)
    with pytest.raises(ValueError, match="coverage"):
        preflight(pilot, tmp_path / "blocked.json")
    assert '"status": "blocked"' in (tmp_path / "blocked.json").read_text()
