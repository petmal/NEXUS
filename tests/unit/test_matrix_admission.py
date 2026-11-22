"""A matrix is admitted by generated evidence and coverage, not optimistic labels."""

import copy
import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from nexus.evaluation.matrix import (
    Matrix,
    coverage,
    matrix_digest,
    preflight,
    verify_preflight_binding,
)

ROOT = Path(__file__).resolve().parents[2]


def matrix():
    return Matrix.model_validate_json((ROOT / "docs/difficulty-model-matrix.json").read_text())


def rows_for_coverage():
    rows = [
        {
            "role": "compact-control",
            "difficulty": {"law_degree": d, "selected_zero_coupling": False},
        }
        for d in (1, 2, 3)
    ]
    rows.append({"role": "execution-control", "difficulty": {"world_index": 0}})
    for i in range(6):
        rows.append(
            {
                "role": "history-transfer" if i == 5 else "structural-transfer",
                "target_fingerprint": str(i),
                "difficulty": {
                    "world_index": i,
                    "structure": {"transition": i % 3, "response": i % 3, "wiring": i % 2},
                    "certificate": {"lower_bound": 4},
                    "untreated_target_classes": 2,
                    "one_pulse_target_classes": 2 if i == 5 else 1,
                    "order_sensitive": bool(i % 2),
                },
            }
        )
    return rows


def test_cubic_only_duplicate_and_shallow_cases_fail_their_gates():
    rows = rows_for_coverage()
    assert all(coverage(rows).values())
    cubic = copy.deepcopy(rows)
    for row in cubic[:3]:
        row["difficulty"]["law_degree"] = 3
    assert not coverage(cubic)["repair_all_three_laws"]
    duplicate = copy.deepcopy(rows)
    duplicate[-1] = copy.deepcopy(duplicate[-2])
    assert not coverage(duplicate)["six_distinct_scientific_worlds"]
    assert not coverage(duplicate)["six_distinct_mission_targets"]
    shallow = copy.deepcopy(rows)
    shallow[-1]["difficulty"]["certificate"]["lower_bound"] = 3
    assert not coverage(shallow)["every_challenge_needs_four_measurements"]
    short = copy.deepcopy(rows)
    short[-1]["difficulty"]["one_pulse_target_classes"] = 1
    assert not coverage(short)["history_transfer_needs_longer_experiment"]


def test_matrix_rejects_mislabeled_cells_duplicate_ids_and_extreme_axes():
    original = matrix().model_dump(mode="json")
    for mutation in ("id", "role", "resource", "extra", "bool"):
        value = copy.deepcopy(original)
        if mutation == "id":
            value["runs"][1]["id"] = value["runs"][0]["id"]
        elif mutation == "role":
            value["runs"][0]["role"] = "structural-transfer"
        elif mutation == "resource":
            value["runs"][0]["environment"]["NEXUS_RESOURCE_PRESSURE"] = "2"
        elif mutation == "bool":
            value["recommended_tool_call_limit"] = True
        else:
            value["runs"][0]["environment"]["NEXUS_UNKNOWN"] = "1"
        with pytest.raises(ValidationError):
            Matrix.model_validate(value)


def test_report_binding_rejects_stale_or_incomplete_results():
    m = matrix()
    with pytest.raises(ValueError, match="incomplete"):
        verify_preflight_binding(m, {"status": "running"})
    with pytest.raises(ValueError, match="stale"):
        verify_preflight_binding(
            m,
            {
                "version": "difficulty-preflight-v1",
                "status": "pilot-ready",
                "matrix_sha256": matrix_digest(m),
                "source_sha256": "old",
            },
        )


def test_invalid_matrix_replaces_previous_ready_output_and_exits_nonzero(tmp_path):
    source, output = tmp_path / "matrix.json", tmp_path / "report.json"
    source.write_text("{}")
    output.write_text('{"status":"pilot-ready"}')
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/preflight_matrix.py"),
            "--matrix",
            str(source),
            "--output",
            str(output),
        ],
        capture_output=True,
        timeout=20,
        check=False,
    )
    assert result.returncode != 0
    assert json.loads(output.read_text())["status"] == "blocked"


@pytest.mark.slow
def test_real_matrix_preflight_and_stale_binding(tmp_path):
    m = matrix()
    output = tmp_path / "preflight.json"
    report = preflight(m, output)
    assert report["status"] == "pilot-ready" and len(report["rows"]) == 10
    assert report["full_rollout_ready"] is False
    verify_preflight_binding(m, report)
    report["rows"].pop()
    with pytest.raises(ValueError):
        verify_preflight_binding(m, report)


MATRIX_CONTRACTS = [
    ("assembly", "joint-assembly-matrix.json", "preflight_joint_assembly.py", "joint-assembly-pilot-v1"),
    ("discovery", "discovery-pocs-matrix.json", "preflight_discovery.py", "discovery-pocs-pilot-v1"),
    ("history", "history-diagnostic-matrix.json", "preflight_history.py", "history-coupled-pilot-v1"),
    ("staged", "staged-repair-matrix.json", "preflight_staged_repair.py", "staged-repair-pilot-v1"),
]

@pytest.mark.parametrize("module,matrix_name,script,version", MATRIX_CONTRACTS, ids=[r[0] for r in MATRIX_CONTRACTS])
def test_source_failure_replaces_stale_success(tmp_path, monkeypatch, module, matrix_name, script, version):
    from nexus.ontology.repair import qualification
    evaluation = importlib.import_module("nexus.evaluation." + module)
    pilot = evaluation.Pilot.model_validate_json((Path(__file__).parents[2] / "docs" / matrix_name).read_text())
    def fail():
        raise OSError("source unavailable")
    monkeypatch.setattr(qualification, "source_binding", fail)
    output = tmp_path / "report.json"
    output.write_text('{"status":"passed"}')
    with pytest.raises(OSError, match="source unavailable"):
        evaluation.preflight(pilot, output)
    assert json.loads(output.read_text())["status"] == "blocked"

@pytest.mark.parametrize("module,matrix_name,script,version", [r for r in MATRIX_CONTRACTS if r[0] != "history"], ids=[r[0] for r in MATRIX_CONTRACTS if r[0] != "history"])
@pytest.mark.parametrize("kind", ["missing", "malformed", "incomplete"])
def test_cli_invalid_input_removes_stale_success(tmp_path, module, matrix_name, script, version, kind):
    matrix, output = tmp_path / "matrix.json", tmp_path / "report.json"
    if kind != "missing":
        matrix.write_text("{" if kind == "malformed" else json.dumps({"version":version}))
    output.write_text('{"status":"passed","old":true}')
    result = subprocess.run([sys.executable, str(Path(__file__).parents[2] / "scripts" / script),
        "--matrix",str(matrix),"--output",str(output)],capture_output=True,text=True,timeout=15,check=False)
    assert result.returncode != 0
    report = json.loads(output.read_text())
    assert report["status"] == "blocked" and report["error"] and "old" not in report
