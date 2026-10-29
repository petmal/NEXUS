"""Readouts keep matrix coverage, missing telemetry and operator waits distinct."""

import ast
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


def test_packaged_readout_remains_python312_syntax_compatible():
    ast.parse(PATH.read_text(), feature_version=(3, 12))


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


def tool_call(call_id, status="success"):
    return {
        "Tool": "nexus",
        "CallID": call_id,
        "Status": status,
        "ExitCode": 0 if status == "success" else 2,
    }


def log_block(record, calls, *, performance=None, finish=True):
    prefix = (
        f"2026-10-27 15:10:00 TRC [{record['TraceID']}] openai: {record['Run']}: {record['Task']}: "
    )
    lines = [prefix + "starting task..."]
    for call_id, status, response in calls:
        lines.extend(
            [
                prefix
                + f"nexus[{call_id}]: parsed input arguments: map[request:map[operation:manifest]]",
                prefix + f'nexus[{call_id}]: tool container "example" stdout:',
                "" if response is None else json.dumps(response),
                prefix + f"nexus[{call_id}]: call finished: status={status} wall_time=1ms",
            ]
        )
    if performance is not None:
        lines.extend(["stderr:", "NEXUS terminal performance: " + json.dumps(performance)])
    if finish:
        lines.append(prefix + "task has finished in 1s.")
    return "\n".join(lines) + "\n"


def test_error_record_retains_partial_usage_and_tool_duration(tmp_path):
    raw = fixture(tmp_path)
    record = raw["Results"]["openai"][1]
    record["Kind"] = "Error"
    record["Details"] = {
        "Error": {
            "Message": "failed to generate response: timeout awaiting response headers",
            "Usage": {"ReasoningTokens": 123, "OutputTokens": 140},
            "ToolUsage": {"nexus": {"CallCount": 1, "TotalDurationNS": 3_000_000_000}},
            "ToolCalls": [tool_call("partial")],
        }
    }
    write(tmp_path, "mindtrial.json", raw)
    (tmp_path / "mindtrial.log").write_text(
        log_block(record, [("partial", "success", {"episode_id": "partial-world", "turn": 1})])
    )
    report = readout.summarize(tmp_path)
    row = report["rows"][1]
    assert row["usage"] == {"ReasoningTokens": 123, "OutputTokens": 140}
    assert row["usage_source"] == "Details.Error" and row["usage_partial"] is True
    assert row["nexus_container_seconds"] == 3
    assert row["diagnostics"]["outcome"] == "provider_interruption"
    assert row["diagnostics"]["world_access"] is True
    assert row["diagnostics"]["accepted_world_actions"] is None
    assert row["diagnostics"]["last_observed_turn"] == 1
    assert report["models"][1]["nexus_container_seconds"] == 3


def test_trace_ids_separate_same_task_models_and_interface_failure(tmp_path):
    raw = fixture(tmp_path)
    astra, luna = raw["Results"]["openai"]
    astra["Details"]["Answer"]["ToolCalls"] = [tool_call("good")]
    astra["Details"]["Answer"]["ToolUsage"]["nexus"]["CallCount"] = 1
    luna.update(Kind="Failed")
    luna["Details"]["Answer"]["ToolCalls"] = [tool_call("bad", "nonzero_exit")]
    luna["Details"]["Answer"]["ToolUsage"]["nexus"]["CallCount"] = 1
    write(tmp_path, "mindtrial.json", raw)
    (tmp_path / "mindtrial.log").write_text(
        log_block(
            astra,
            [("good", "success", {"episode_id": "world-A", "turn": 1})],
            performance={
                "terminal_status": "won",
                "termination_reason": "victory",
                "actions_used": 1,
            },
        )
        + log_block(
            luna,
            [("bad", "nonzero_exit", None)],
            performance={
                "terminal_status": "failed",
                "termination_reason": "harness_finalization",
                "actions_used": 0,
            },
        )
    )
    report = readout.summarize(tmp_path)
    good, bad = [r["diagnostics"] for r in report["rows"]]
    assert good["world_access"] is True and good["outcome"] == "reported_win"
    assert bad["world_access"] is False and bad["outcome"] == "no_successful_world_access"
    assert bad["accepted_world_actions"] == 0
    assert bad["tool_call_status_counts"] == {"nonzero_exit": 1}
    assert all(r["tool_log_complete"] for r in (good, bad))


def test_missing_incomplete_and_ambiguous_logs_do_not_invent_no_access(tmp_path):
    raw = fixture(tmp_path)
    astra, luna = raw["Results"]["openai"]
    for r in (astra, luna):
        r["Kind"] = "Failed"
        r["Details"]["Answer"]["ToolCalls"] = [tool_call(r["TraceID"], "nonzero_exit")]
        r["Details"]["Answer"]["ToolUsage"]["nexus"]["CallCount"] = 1
    write(tmp_path, "mindtrial.json", raw)
    log = tmp_path / "mindtrial.log"
    log.unlink()
    report = readout.summarize(tmp_path)
    assert all(r["diagnostics"]["world_access"] is None for r in report["rows"])
    assert all(r["diagnostics"]["outcome"] == "unknown" for r in report["rows"])
    assert all(r["diagnostics"]["log_evidence"] == "missing_log" for r in report["rows"])

    log.write_text(log_block(astra, [], performance={"actions_used": 0}))
    report = readout.summarize(tmp_path)
    assert report["rows"][0]["diagnostics"]["log_evidence"] == "incomplete_tool_log"
    assert report["rows"][0]["diagnostics"]["world_access"] is None

    log.write_text(
        log_block(astra, [("astra", "nonzero_exit", None)], finish=False)
        + log_block(luna, [("luna", "nonzero_exit", None)], performance={"actions_used": 0})
    )
    report = readout.summarize(tmp_path)
    assert all(r["diagnostics"]["log_evidence"] == "ambiguous_trace" for r in report["rows"])
    assert all(r["diagnostics"]["world_access"] is None for r in report["rows"])


def test_budget_failure_keeps_actual_termination_separate_from_harness_stop(tmp_path):
    raw = fixture(tmp_path)
    astra, luna = raw["Results"]["openai"]
    log = ""
    for record, reason in ((astra, "action_budget"), (luna, "harness_finalization")):
        record["Kind"] = "Failed"
        call_id = record["TraceID"]
        record["Details"]["Answer"]["ToolCalls"] = [tool_call(call_id)]
        record["Details"]["Answer"]["ToolUsage"]["nexus"]["CallCount"] = 1
        log += log_block(
            record,
            [(call_id, "success", {"observation": {"episode_id": call_id, "turn": 4}})],
            performance={
                "terminal_status": "failed",
                "termination_reason": reason,
                "actions_used": 4,
            },
        )
    write(tmp_path, "mindtrial.json", raw)
    (tmp_path / "mindtrial.log").write_text(log)
    report = readout.summarize(tmp_path)
    assert [r["diagnostics"]["outcome"] for r in report["rows"]] == [
        "action_budget_exhausted",
        "stopped_after_world_access",
    ]


def test_first_task_timing_supports_new_family_names(tmp_path):
    raw = fixture(tmp_path)
    name = "NEXUS small-model-smoke-stateful-03"
    for record in raw["Results"]["openai"]:
        record["Task"] = name
    write(tmp_path, "mindtrial.json", raw)
    manifest = readout.read(tmp_path / "manifest.json")
    manifest["tasks_sha256"] = write(
        tmp_path, "tasks.yaml", {"task-config": {"tasks": [{"name": name}]}}
    )
    write(tmp_path, "manifest.json", manifest)
    (tmp_path / "mindtrial.log").write_text(log_block(raw["Results"]["openai"][0], []))
    report = readout.summarize(tmp_path)
    assert report["timing"]["before_first_logged_task_seconds"] == 599.5
    assert report["matrix_complete"]


def test_explicit_zero_calls_can_establish_no_world_access(tmp_path):
    raw = fixture(tmp_path)
    record = raw["Results"]["openai"][1]
    record["Kind"] = "Failed"
    record["Details"]["Answer"]["ToolCalls"] = []
    record["Details"]["Answer"]["ToolUsage"]["nexus"]["CallCount"] = 0
    write(tmp_path, "mindtrial.json", raw)
    (tmp_path / "mindtrial.log").write_text(
        log_block(
            record,
            [],
            performance={
                "terminal_status": "failed",
                "termination_reason": "harness_finalization",
                "actions_used": 0,
            },
        )
    )
    diagnostics = readout.summarize(tmp_path)["rows"][1]["diagnostics"]
    assert diagnostics["world_access"] is False
    assert diagnostics["outcome"] == "no_successful_world_access"
