"""Readouts keep matrix coverage, missing telemetry and operator waits distinct."""

import hashlib
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pytest

PATH = Path(__file__).parents[2] / "examples/mindtrial/summarize-pilot-results.py"
loader = importlib.util.spec_from_file_location("pilot_readout", PATH)
readout = importlib.util.module_from_spec(loader)
loader.loader.exec_module(readout)


def write(directory, name, value):
    raw = json.dumps(value).encode()
    (directory / name).write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def fixture(directory):
    runs = [
        {
            "name": m,
            "model": m,
            "model-parameters": {"reasoning-effort": "medium"},
            "max-requests-per-minute": 20,
        }
        for m in ("astra", "luna")
    ]
    manifest = {
        "started_at": "2026-10-27T19:00:00.500+00:00",
        "finished_at": "2026-10-27T19:11:00+00:00",
        "source_commit": "test",
        "runtime_source_sha256": "test",
        "mindtrial_sha256": "test",
        "suite": "core",
    }
    manifest["effective_config_sha256"] = write(
        directory, "config.yaml", {"config": {"providers": [{"name": "openai", "runs": runs}]}}
    )
    manifest["tasks_sha256"] = write(
        directory, "tasks.yaml", {"task-config": {"tasks": [{"name": "NEXUS interference-11"}]}}
    )
    write(directory, "manifest.json", manifest)
    records = [
        {
            "TraceID": m,
            "Run": m,
            "Task": "NEXUS interference-11",
            "Kind": "Passed",
            "RunConfig": {
                "Model": m,
                "MaxRequestsPerMinute": 20,
                "ModelParameters": {"reasoning-effort": "medium"},
            },
            "DurationNS": 2_000_000_000,
            "Details": {
                "Answer": {
                    "ToolUsage": {"nexus": {"CallCount": 8, "TotalDurationNS": 1_000_000_000}},
                    "Usage": {
                        "OutputTokens": 10,
                        "ReasoningTokens": 6,
                        "OutputTokenAccounting": "reasoning_tokens_included",
                    },
                }
            },
        }
        for m in ("astra", "luna")
    ]
    raw = {
        "FormatVersion": 1,
        "AppName": "MindTrial",
        "CreatedAt": "Tue, 27 Oct 2026 15:11:00 -0400",
        "Results": {"openai": records},
    }
    write(directory, "mindtrial.json", raw)
    (directory / "mindtrial.log").write_text(
        "2026-10-27 15:10:00 INF NEXUS interference-11: starting task...\n"
    )
    return raw


def test_complete_crossing_and_timing_separate_selection_from_requests(tmp_path):
    fixture(tmp_path)
    report = readout.summarize(tmp_path)
    assert report["matrix_complete"]
    assert report["expected_attempts"] == report["recorded_attempts"] == 2
    assert report["timing"]["before_first_logged_task_seconds"] == 599.5
    assert report["timing"]["first_logged_task_to_exit_seconds"] == 60
    assert [m["request_seconds"] for m in report["models"]] == [2, 2]
    assert [m["nexus_container_seconds"] for m in report["models"]] == [1, 1]
    assert report["rows"][0]["usage"]["OutputTokens"] == 10


def test_partial_failed_attempt_retains_missing_effort(tmp_path):
    raw = fixture(tmp_path)
    raw["Results"]["openai"] = raw["Results"]["openai"][:1]
    raw["Results"]["openai"][0].update(Kind="Error", Details={})
    raw["Results"]["openai"][0].pop("DurationNS")
    write(tmp_path, "mindtrial.json", raw)
    report = readout.summarize(tmp_path)
    assert not report["matrix_complete"]
    assert len(report["missing"]) == 1
    assert report["models"][0]["request_seconds"] is None
    assert report["models"][0]["nexus_container_seconds"] is None


def test_distinct_repeat_is_kept_and_parameter_drift_is_not_complete(tmp_path):
    raw = fixture(tmp_path)
    raw["Results"]["openai"][0]["RunConfig"]["ModelParameters"]["reasoning-effort"] = "high"
    write(tmp_path, "mindtrial.json", raw)
    report = readout.summarize(tmp_path)
    assert not report["matrix_complete"]
    assert report["configuration_mismatch_trace_ids"] == ["astra"]
    repeated = deepcopy(raw["Results"]["openai"][0])
    repeated["TraceID"] = "repeat"
    raw["Results"]["openai"].append(repeated)
    write(tmp_path, "mindtrial.json", raw)
    assert readout.summarize(tmp_path)["repeated_conditions"][0]["count"] == 2
    repeated["TraceID"] = "astra"
    write(tmp_path, "mindtrial.json", raw)
    with pytest.raises(ValueError, match="duplicate"):
        readout.summarize(tmp_path)


def test_checksum_change_and_invalid_timestamp_are_not_accepted(tmp_path):
    fixture(tmp_path)
    (tmp_path / "mindtrial.log").write_text(
        "2026-10-27 14:00:00 INF NEXUS interference-11: starting task...\n"
    )
    with pytest.raises(ValueError, match="timestamp"):
        readout.summarize(tmp_path)
    (tmp_path / "config.yaml").write_text("{}")
    with pytest.raises(ValueError, match="checksum"):
        readout.summarize(tmp_path)
