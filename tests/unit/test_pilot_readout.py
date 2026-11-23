"""Readouts keep matrix coverage, missing telemetry and operator waits distinct."""

import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest


@pytest.mark.parametrize("key", ["text-response-format", "text-response-format-with-tools"])
@pytest.mark.parametrize(
    "configured_value,recorded_value,matches",
    [
        (None, False, True),
        (False, None, True),
        (False, False, True),
        (None, True, False),
        (True, False, False),
        (True, None, False),
        (None, 0, False),
        (None, "false", False),
    ],
)
def test_concrete_false_model_defaults_do_not_mask_enabled_or_invalid_values(
    key, configured_value, recorded_value, matches
):
    configured = {"model-parameters": {}}
    snapshot = {"ModelParameters": {}}
    if configured_value is not None:
        configured["model-parameters"][key] = configured_value
    if recorded_value is not None:
        snapshot["ModelParameters"][key] = recorded_value
    assert (readout.run_config_differences(configured, snapshot, {}) == []) is matches


@pytest.mark.parametrize(
    "key,value",
    [("parallel-tool-calls", False), ("temperature", 0), ("unknown-flag", False), ("seed", 0)],
)
def test_other_false_or_zero_parameters_remain_configuration_differences(key, value):
    assert readout.run_config_differences(
        {"model-parameters": {}}, {"ModelParameters": {key: value}}, {}
    ) == ["model_parameters"]


PATH = Path(__file__).parents[2] / "examples/mindtrial/summarize-pilot-results.py"
loader = importlib.util.spec_from_file_location("pilot_readout", PATH)
readout = importlib.util.module_from_spec(loader)
loader.loader.exec_module(readout)


def test_packaged_readout_remains_python312_syntax_compatible():
    ast.parse(PATH.read_text(), feature_version=(3, 12))


def test_reported_astra_config_matches_the_uploaded_control_fixture():
    data = json.loads(
        (PATH.parents[2] / "tests/fixtures/mindtrial-openai-default-parameters.json").read_text()
    )
    assert (
        readout.run_config_differences(data["configured"], data["recorded"], data["retry_policy"])
        == []
    )


@pytest.mark.parametrize("message,status,category", [
    ("Error 402, Message: Your prepayment credits are depleted.", 402, "billing_or_quota"),
    ("retryable error: 503 Service Unavailable", 503, "provider_unavailable"),
    ("HTTP/1.1 429 Too Many Requests", 429, "rate_limited"),
    ("API error: 401 Unauthorized", 401, "authentication"),
    ("HTTP status: 403 Forbidden", 403, "permission_denied"),
    ("status code=400 invalid model", 400, "request_rejected"),
    ("API error: 408 Request Timeout", 408, "provider_unavailable"),
])
def test_provider_status_is_typed_without_inventing_a_scientific_loss(message, status, category):
    record = {"Kind": "Error", "Details": {"Error": {"Message": message}}}
    assert readout.classify_provider_error(record) == {
        "http_status": status, "category": category, "stop_batch": True,
    }
    record["Kind"] = "Failed"
    assert readout.classify_provider_error(record) is None


@pytest.mark.parametrize("message", ["used 402 tokens", "stop reason: length", "no actionable content", None])
def test_provider_status_does_not_guess_from_numbers_or_completion_failures(message):
    assert readout.classify_provider_error(
        {"Kind": "Error", "Details": {"Error": {"Message": message}}}
    ) is None


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
        "evaluation_seed": "fixture-seed",
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
            "Evaluation": {"Seed": "fixture-seed"},
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


def test_transport_interruption_is_counted_without_changing_http_stop_policy(tmp_path):
    raw = fixture(tmp_path)
    record = raw["Results"]["openai"][0]
    record["Kind"] = "Error"
    record["Details"] = {"Error": {"Message": "failed to generate response: Post request: http2: timeout awaiting response headers"}}
    write(tmp_path, "mindtrial.json", raw)
    error = readout.classify_provider_error(record)
    assert error["http_status"] is None and error["stop_batch"] is False
    report = readout.summarize(tmp_path)
    assert report["rows"][0]["diagnostics"]["outcome"] == "provider_interruption"
    assert report["provider_error_attempts"] == 1
    assert not report["completed_without_provider_errors"]


def test_readout_verifies_completion_binding_and_marks_legacy_inputs(tmp_path):
    raw = fixture(tmp_path)
    assert readout.summarize(tmp_path)["result_binding_status"] == "legacy_unbound"
    manifest = readout.read(tmp_path / "manifest.json")
    manifest["run_id"] = "attempt-2"
    manifest["result_binding"] = readout.result_binding(tmp_path, manifest["run_id"])
    write(tmp_path, "manifest.json", manifest)
    report = readout.summarize(tmp_path)
    assert report["result_binding_status"] == "verified"
    assert report["source_files_sha256"]["mindtrial.json"] == manifest["result_binding"]["results_sha256"]
    raw["Results"]["openai"][0]["TraceID"] = "older-trace"
    write(tmp_path, "mindtrial.json", raw)
    with pytest.raises(ValueError, match="result binding"):
        readout.summarize(tmp_path)


def test_failed_readout_refresh_does_not_leave_a_stale_success(tmp_path):
    fixture(tmp_path)
    command = [sys.executable, str(PATH), str(tmp_path)]
    subprocess.run(command, check=True, capture_output=True)
    assert (tmp_path / "readout.json").is_file()
    (tmp_path / "mindtrial.json").write_text('{"Results":')
    failed = subprocess.run(command, check=False, capture_output=True)
    assert failed.returncode != 0
    assert not (tmp_path / "readout.json").exists()


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


@pytest.mark.parametrize("missing", [False, True])
def test_cancelled_run_without_json_retains_missing_slots(tmp_path, missing):
    fixture(tmp_path)
    result = tmp_path / "mindtrial.json"
    result.unlink() if missing else result.write_text("")
    report = readout.summarize(tmp_path)
    assert report["result_file_status"] == "missing_or_empty"
    assert report["recorded_attempts"] == 0
    assert report["expected_attempts"] == len(report["missing"]) == 2
    assert not report["matrix_complete"]
    assert report["rows"] == [] and report["models"] == []
    assert report["timing"]["first_logged_task_to_exit_seconds"] is None


@pytest.mark.parametrize("remaining", [46, 21])
def test_length_with_text_is_not_a_world_budget_failure(tmp_path, remaining):
    raw = fixture(tmp_path)
    record = raw["Results"]["openai"][0]
    record["Kind"] = "Failed"
    record["Details"]["Answer"].update(
        ActualAnswer=["An unfinished plan", ""],
        ToolCalls=[tool_call("last")],
        ToolUsage={"nexus": {"CallCount": 1}},
    )
    write(tmp_path, "mindtrial.json", raw)
    log = log_block(
        record,
        [
            (
                "last",
                "success",
                {
                    "observation": {
                        "episode_id": "world",
                        "turn": 7,
                        "terminal_status": "active",
                        "actions_remaining": remaining,
                    },
                },
            )
        ],
        performance={
            "terminal_status": "failed",
            "termination_reason": "harness_finalization",
            "actions_used": 7,
            "budget_remaining": remaining,
        },
    )
    marker = "task has finished in 1s."
    log = log.replace(
        marker,
        'stop reason: "length" (terminal: true)\n'
        + log.splitlines()[0].split("starting task...")[0]
        + marker,
    )
    (tmp_path / "mindtrial.log").write_text(log)
    row = readout.summarize(tmp_path)["rows"][0]
    d = row["diagnostics"]
    assert row["reported_kind"] == "Failed"
    assert d["outcome"] == "response_length_with_text"
    assert d["provider_stop_reason"] == "length"
    assert d["terminal_status"] == "failed"
    assert d["last_observed_world_state"] == {
        "turn": 7,
        "status": "active",
        "actions_remaining": remaining,
    }


@pytest.mark.parametrize(
    "message,outcome",
    [
        (
            "failed to generate response: model returned no actionable content (stop reason: length)",
            "response_length_without_text",
        ),
        (
            "failed to generate response: model response contained no response candidates",
            "no_response_candidates",
        ),
    ],
)
def test_error_record_distinguishes_length_and_empty_without_logs(tmp_path, message, outcome):
    raw = fixture(tmp_path)
    record = raw["Results"]["openai"][0]
    record.update(Kind="Error", Details={"Error": {"Message": message}})
    write(tmp_path, "mindtrial.json", raw)
    (tmp_path / "mindtrial.log").unlink()
    d = readout.summarize(tmp_path)["rows"][0]["diagnostics"]
    assert d["outcome"] == outcome
    assert d["world_access"] is None
    assert d["provider_stop_reason"] == (
        "length" if outcome.startswith("response_length") else None
    )


@pytest.mark.parametrize("count", [0, 1])
def test_invalid_arguments_are_complete_recorded_calls_without_container_output(tmp_path, count):
    raw = fixture(tmp_path)
    record = raw["Results"]["openai"][0]
    record.update(Kind="Failed")
    record["Details"]["Answer"].update(
        ToolCalls=[tool_call("bad", "invalid_arguments")],
        ToolUsage={"nexus": {"CallCount": count}},
    )
    write(tmp_path, "mindtrial.json", raw)
    prefix = f"2026-10-27 15:10:00 TRC [astra] openai: astra: {record['Task']}: "
    (tmp_path / "mindtrial.log").write_text(
        "\n".join(
            prefix + line
            for line in [
                "starting task...",
                'nexus[bad]: failed to parse input arguments: {"request":',
                "nexus[bad]: call finished: status=invalid_arguments wall_time=1ms",
                "task has finished in 1s.",
            ]
        )
    )
    d = readout.summarize(tmp_path)["rows"][0]["diagnostics"]
    assert d["tool_log_complete"] and d["world_access"] is False
    assert d["tool_count_convention"] == (
        "all_detailed_calls" if count else "excludes_invalid_arguments"
    )


def test_recovered_length_does_not_override_later_success(tmp_path):
    raw = fixture(tmp_path)
    record = raw["Results"]["openai"][0]
    record["Details"]["Answer"].update(ToolCalls=[], ToolUsage={"nexus": {"CallCount": 0}})
    write(tmp_path, "mindtrial.json", raw)
    prefix = f"2026-10-27 15:10:00 TRC [astra] openai: astra: {record['Task']}: "
    (tmp_path / "mindtrial.log").write_text(
        "\n".join(
            prefix + line
            for line in [
                "starting task...",
                'stop reason: "length" (terminal: true)',
                'stop reason: "stop" (terminal: true)',
                "task has finished in 1s.",
            ]
        )
    )
    d = readout.summarize(tmp_path)["rows"][0]["diagnostics"]
    assert d["provider_stop_reason"] == "stop" and d["outcome"] == "reported_win"


@pytest.mark.parametrize("change", ["output_mode", "extra_parameter", "retry"])
def test_readout_detects_additional_effective_configuration_drift(tmp_path, change):
    raw = fixture(tmp_path)
    snapshot = raw["Results"]["openai"][0]["RunConfig"]
    if change == "output_mode":
        snapshot["DisableStructuredOutput"] = True
    elif change == "extra_parameter":
        snapshot["ModelParameters"]["temperature"] = 0.7
    else:
        config = readout.read(tmp_path / "config.yaml")
        config["config"]["providers"][0]["retry-policy"] = {"max-retry-attempts": 0}
        manifest = readout.read(tmp_path / "manifest.json")
        manifest["effective_config_sha256"] = write(tmp_path, "config.yaml", config)
        write(tmp_path, "manifest.json", manifest)
        snapshot["RetryPolicy"] = {"MaxRetryAttempts": 1}
    write(tmp_path, "mindtrial.json", raw)
    result = readout.summarize(tmp_path)
    assert not result["matrix_complete"]
    assert result["configuration_mismatch_trace_ids"] == ["astra"]


@pytest.mark.parametrize(
    "message,stop,outcome",
    [
        (
            "retryable: failed to generate response: OpenAI API error: 429 Too Many Requests",
            None,
            "http_rate_limited",
        ),
        (
            "failed to generate response: model response contained no actionable content",
            "stop",
            "no_actionable_content",
        ),
        (
            "failed to generate response: model response contained no actionable content",
            "length",
            "response_length_without_text",
        ),
    ],
)
def test_http_error_and_structured_stop_reason_survive_without_log(
    tmp_path, message, stop, outcome
):
    raw = fixture(tmp_path)
    raw["Results"]["openai"][0].update(
        Kind="Error",
        Details={
            "Error": {
                "Message": message,
                "Details": {"Stop Reason": [stop]} if stop else {},
            }
        },
    )
    write(tmp_path, "mindtrial.json", raw)
    (tmp_path / "mindtrial.log").unlink()
    d = readout.summarize(tmp_path)["rows"][0]["diagnostics"]
    assert d["outcome"] == outcome and d["provider_stop_reason"] == stop
    assert d["provider_http_status"] == (429 if outcome == "http_rate_limited" else None)
    assert d["world_access"] is None


def test_compact_summary_survives_truncated_full_report_and_preserves_provider_error(tmp_path):
    raw = fixture(tmp_path)
    record = raw['Results']['openai'][0]
    record.update(Kind='Error', Details={'Error': {'Message': 'API error: 402 credits exhausted',
                  'ToolCalls': [], 'ToolUsage': {'nexus': {'CallCount': 0}}}})
    write(tmp_path, 'mindtrial.json', raw)
    summary = {'version': 'operator-summary-v3', 'status': 'failed', 'turn': 4,
               'physical_goal_satisfied': False, 'escape_classification': 'no_escape',
               'first_submission_supported_by_evidence': None,
               'physical_continuation': {'available': True, 'first_budget_infeasible_turn': 2}}
    log = log_block(record, [], finish=False) + 'NEXUS operator summary: ' + json.dumps(summary) + '\n'
    (tmp_path / 'mindtrial.log').write_text(log)
    result = readout.summarize(tmp_path)
    row = result['rows'][0]
    diagnostic = row['diagnostics']
    assert row['reported_kind'] == 'Error'
    assert diagnostic['provider_error']['http_status'] == 402
    assert diagnostic['accepted_world_actions'] == 4
    assert diagnostic['physical_goal_satisfied'] is False
    assert diagnostic['world_win_observed'] is False
    assert diagnostic['outcome'] == 'budget_infeasible_before_provider_error'
    assert not result['completed_without_provider_errors']


def test_disabled_provider_is_not_part_of_expected_denominator(tmp_path):
    fixture(tmp_path)
    config = json.loads((tmp_path / 'config.yaml').read_text())
    config['config']['providers'].append({'name': 'unused', 'disabled': True,
                                        'runs': [{'name': 'never', 'model': 'never'}]})
    digest = write(tmp_path, 'config.yaml', config)
    manifest = json.loads((tmp_path / 'manifest.json').read_text())
    manifest['effective_config_sha256'] = digest
    write(tmp_path, 'manifest.json', manifest)
    assert readout.summarize(tmp_path)['matrix_complete']


def test_summary_does_not_call_model_length_a_provider_error(tmp_path):
    raw = fixture(tmp_path)
    record = raw['Results']['openai'][0]
    record.update(Kind='Error', Details={'Error': {'Message': 'model returned no actionable content (stop reason: length)'}})
    write(tmp_path, 'mindtrial.json', raw)
    report = readout.summarize(tmp_path)
    assert report['error_attempts'] == 1
    assert report['provider_error_attempts'] == 0
    assert report['completed_without_provider_errors']


def test_old_summary_null_does_not_erase_legacy_physical_goal(tmp_path):
    raw = fixture(tmp_path)
    record = raw['Results']['openai'][0]
    log = log_block(record, [], performance={'terminal_status': 'won', 'goal_satisfied': True}, finish=False)
    log += 'NEXUS operator summary: ' + json.dumps({'status': 'won', 'physical_goal_satisfied': None}) + '\n'
    (tmp_path / 'mindtrial.log').write_text(log)
    assert readout.summarize(tmp_path)['rows'][0]['diagnostics']['physical_goal_satisfied'] is True


def test_boolean_settings_do_not_match_numbers_even_in_nested_json():
    configured = {"model-parameters": {"options": [0, {"flag": True}]},
                  "disable-structured-output": True, "max-requests-per-minute": 1}
    recorded = {"ModelParameters": {"options": [False, {"flag": 1}]},
                "DisableStructuredOutput": 1, "MaxRequestsPerMinute": True,
                "RetryPolicy": {"MaxRetryAttempts": False}}
    assert set(readout.run_config_differences(configured, recorded, {"max-retry-attempts": 0})) == {
        "model_parameters", "disable_structured_output", "max_requests_per_minute",
        "retry_policy.max-retry-attempts",
    }
    assert not readout.run_config_differences(
        {"model-parameters": {"temperature": 0}},
        {"ModelParameters": {"temperature": 0.0}}, {},
    )


def test_checker_confirms_access_but_not_a_world_outcome_or_action(tmp_path):
    raw = fixture(tmp_path)
    record = raw["Results"]["openai"][0]
    record["Kind"] = "Failed"
    answer = record["Details"]["Answer"]
    answer.update(ToolCalls=[tool_call("check")], ToolUsage={"nexus": {"CallCount": 1}})
    response = {"scope": "archive_and_observed_reader_outputs_only",
                "consistent_with_readings": False, "distinct_readings_checked": 2,
                "evidence_turn": 3, "world_action_cost": 0}
    write(tmp_path, "mindtrial.json", raw)
    (tmp_path / "mindtrial.log").write_text(log_block(record, [("check", "success", response)]))
    d = readout.summarize(tmp_path)["rows"][0]["diagnostics"]
    assert d["tool_log_complete"] and d["world_access"] is True
    assert d["last_observed_turn"] == 3 and d["accepted_world_actions"] is None
    assert d["world_win_observed"] is None
    assert not readout.public_response({**response, "world_action_cost": False})


@pytest.mark.parametrize("terminal,expected", [(None, None), ("won", True), ("failed", False)])
def test_state_evidence_uses_game_turn_even_when_a_cached_response_arrives_last(
    tmp_path, terminal, expected
):
    raw = fixture(tmp_path)
    row = raw["Results"]["openai"][0]
    row["Kind"] = "Failed"
    row["Details"]["Answer"].update(ToolCalls=[tool_call("new"), tool_call("retry")],
                                     ToolUsage={"nexus": {"CallCount": 2}})
    states = [("new", "success", {"turn": 8, "status": terminal or "active", "actions_remaining": 2}),
              ("retry", "success", {"turn": 4, "status": "active", "actions_remaining": 6})]
    write(tmp_path, "mindtrial.json", raw)
    (tmp_path / "mindtrial.log").write_text(log_block(row, states))
    d = readout.summarize(tmp_path)["rows"][0]["diagnostics"]
    assert d["last_observed_world_state"]["turn"] == d["last_observed_turn"] == 8
    assert d["world_win_observed"] is expected


@pytest.mark.parametrize("count", [False, 0.0])
def test_invalid_counter_cannot_establish_no_access(tmp_path, count):
    raw = fixture(tmp_path)
    row = raw["Results"]["openai"][0]
    row["Details"]["Answer"].update(ToolCalls=[], ToolUsage={"nexus": {"CallCount": count}})
    write(tmp_path, "mindtrial.json", raw)
    (tmp_path / "mindtrial.log").write_text(log_block(row, []))
    d = readout.summarize(tmp_path)["rows"][0]["diagnostics"]
    assert not d["tool_log_complete"] and d["world_access"] is None
    assert d["tool_count_convention"] == "unresolved"


def test_unreported_trace_starting_first_blocks_attribution_of_shared_log(tmp_path):
    raw = fixture(tmp_path)
    row = raw["Results"]["openai"][0]
    foreign = {**row, "TraceID": "unreported", "Task": "other task"}
    (tmp_path / "mindtrial.log").write_text(
        log_block(foreign, [], finish=False) + log_block(row, [], performance={"terminal_status": "won"})
    )
    d = readout.summarize(tmp_path)["rows"][0]["diagnostics"]
    assert d["log_evidence"] == "ambiguous_trace" and d["world_win_observed"] is None


def test_wrong_seed_fails_the_readout_even_with_a_full_crossing(tmp_path):
    raw = fixture(tmp_path)
    manifest = readout.read(tmp_path / "manifest.json")
    write(tmp_path, "manifest.json", {**manifest, "evaluation_seed": "selected"})
    for row in raw["Results"]["openai"]:
        row["Evaluation"] = {"Seed": "selected"}
    raw["Results"]["openai"][0]["Evaluation"]["Seed"] = "other"
    write(tmp_path, "mindtrial.json", raw)
    report = readout.summarize(tmp_path)
    assert not report["matrix_complete"]
    assert report["rows"][0]["configuration_differences"] == ["evaluation_seed"]


@pytest.mark.parametrize("summary_kind,public_status,conflicting_world,observed", [
    ("failed", "won", True, None), ("failed", "failed", False, False),
])
def test_contradictory_world_or_harness_verdict_is_visible(
    tmp_path, summary_kind, public_status, conflicting_world, observed
):
    raw = fixture(tmp_path)
    row = raw["Results"]["openai"][0]
    (tmp_path / "mindtrial.log").write_text(log_block(
        row, [("last", "success", {"turn": 4, "status": public_status, "actions_remaining": 0})],
        performance={"terminal_status": summary_kind},
    ))
    d = readout.summarize(tmp_path)["rows"][0]["diagnostics"]
    assert d["world_evidence_conflict"] is conflicting_world
    assert d["world_win_observed"] is observed and d["outcome"] == "conflicting_result_evidence"


@pytest.mark.parametrize("duplicate", ["run", "task"])
def test_ambiguous_condition_names_are_not_collapsed_into_a_smaller_denominator(tmp_path, duplicate):
    fixture(tmp_path)
    manifest = readout.read(tmp_path / "manifest.json")
    if duplicate == "run":
        config = readout.read(tmp_path / "config.yaml")
        runs = config["config"]["providers"][0]["runs"]
        runs.append({**runs[0], "model": "other"})
        manifest["effective_config_sha256"] = write(tmp_path, "config.yaml", config)
    else:
        config = readout.read(tmp_path / "tasks.yaml")
        config["task-config"]["tasks"] *= 2
        manifest["tasks_sha256"] = write(tmp_path, "tasks.yaml", config)
    write(tmp_path, "manifest.json", manifest)
    with pytest.raises(ValueError, match="duplicate configured"):
        readout.summarize(tmp_path)


def test_unusable_usage_and_error_text_are_not_numeric_effort_or_world_verdict(tmp_path):
    raw = fixture(tmp_path)
    raw["Results"]["openai"][0].update(Kind="Error", DurationNS=-1,
        Details={"Error": {"Message": None, "Usage": {"OutputTokens": -2, "ReasoningTokens": False}}})
    write(tmp_path, "mindtrial.json", raw)
    report = readout.summarize(tmp_path)
    group = report["models"][0]
    assert group["request_seconds"] is group["reported_output_tokens"] is group["reported_reasoning_tokens"] is None
    assert report["rows"][0]["diagnostics"]["outcome"] == "result_error"

def test_unbound_seed_retains_legacy_rows_without_certifying_the_condition(tmp_path):
    fixture(tmp_path)
    manifest = readout.read(tmp_path / "manifest.json")
    del manifest["evaluation_seed"]
    write(tmp_path, "manifest.json", manifest)
    result = readout.summarize(tmp_path)
    assert not result["matrix_complete"] and result["recorded_attempts"] == 2
    assert all(row["configuration_differences"] == ["unbound_evaluation_seed"] for row in result["rows"])


def test_cli_handles_mixed_preflight_and_run_folders_without_hiding_a_damaged_run(tmp_path):
    preflight, run = tmp_path / "a", tmp_path / "b"
    preflight.mkdir()
    run.mkdir()
    write(preflight, "manifest.json", {"status": "preflight-passed", "command": None})
    write(preflight, "preflight.json", {"status": "passed"})
    fixture(run)
    command = [sys.executable, str(PATH), str(preflight), str(run)]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    assert "preflight only; no model attempts" in result.stdout
    assert not (preflight / "readout.json").exists()
    assert readout.read(run / "readout.json")["recorded_attempts"] == 2

    write(preflight, "mindtrial.json", {})
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode != 0 and "conflicts with attempt artifacts" in result.stderr
    (preflight / "mindtrial.json").unlink()
    write(preflight, "manifest.json", {"status": "interrupted"})
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode != 0 and "cannot summarize" in result.stderr


def test_deleted_completed_results_do_not_mask_later_cancelled_folder(tmp_path):
    broken, cancelled = tmp_path / "broken", tmp_path / "cancelled"
    for folder in (broken, cancelled):
        folder.mkdir()
        fixture(folder)
        manifest = readout.read(folder / "manifest.json")
        manifest["run_id"] = folder.name
        if folder == broken:
            manifest.update(status="completed", result_binding=readout.result_binding(folder, folder.name))
        else:
            # Interrupted by the v6 launcher before it could bind a result.
            manifest.update(status="interrupted", result_binding_error="missing or invalid output identity")
        write(folder, "manifest.json", manifest)
        (folder / "mindtrial.json").unlink()
    cli = subprocess.run([sys.executable, str(PATH), str(broken), str(cancelled)], capture_output=True)
    assert cli.returncode == 1 and not (broken / "readout.json").exists()
    report = readout.read(cancelled / "readout.json")
    assert report["result_binding_status"] == "unverified_no_result"
    assert len(report["missing"]) == report["expected_attempts"] > 0 and not report["rows"]
