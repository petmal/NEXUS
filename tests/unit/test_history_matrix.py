"""Matrix admission fails closed without disguising experimental depth limits."""

import json
from pathlib import Path

import pytest

from nexus.evaluation.history import Cell, Pilot, preflight

MATRIX = Path(__file__).parents[2] / "docs/history-diagnostic-matrix.json"


def test_checked_matrix_and_private_pair_claims(tmp_path):
    pilot = Pilot.model_validate_json(MATRIX.read_text())
    report = preflight(pilot, tmp_path / "proof.json")
    assert report["status"] == "passed" and len(report["cells"]) == 10
    assert report["deep_tier_admitted"] is False
    rows = {row["id"]: row for row in report["cells"]}
    assert rows["02"]["law"] == rows["03"]["law"] == rows["04"]["law"]
    assert rows["02"]["budget"] == rows["03"]["budget"] == 43
    assert rows["04"]["budget"] == 49
    assert rows["05"]["checks"]["passive_orientation_rival"]
    assert len({tuple(row["law"]["gates"]) for row in rows.values() if "law" in row}) == 4


def test_wrong_rival_and_duplicate_identifiers_are_rejected(tmp_path):
    pilot = Pilot.model_validate_json(MATRIX.read_text())
    with pytest.raises(ValueError, match="duplicate"):
        Pilot.model_validate(pilot.model_dump() | {"runs": [pilot.runs[0].model_dump()] * 2})
    wrong = Cell(
        id="wrong",
        family="history-coupled-v1",
        seed=440,
        orientation_rival=216,
        purpose="invalid claim",
    )
    bad = pilot.model_copy(update={"runs": (wrong,)})
    output = tmp_path / "blocked.json"
    with pytest.raises(ValueError, match="failed checks"):
        preflight(bad, output)
    assert json.loads(output.read_text())["status"] == "blocked"


def test_initial_source_failure_replaces_stale_pass(tmp_path, monkeypatch):
    from nexus.ontology.repair import qualification

    pilot = Pilot.model_validate_json(MATRIX.read_text())
    output = tmp_path / "previous.json"
    output.write_text('{"status":"passed"}')

    def failed_read():
        raise OSError("source unavailable")

    monkeypatch.setattr(qualification, "source_binding", failed_read)
    with pytest.raises(OSError, match="source unavailable"):
        preflight(pilot, output)
    assert json.loads(output.read_text())["status"] == "blocked"
