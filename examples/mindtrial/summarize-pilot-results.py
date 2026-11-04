#!/usr/bin/env python3
"""Summarize a collected MindTrial result folder without making model calls.

This is a convenience readout, not replay or receipt verification. Retain the
complete folder for the source-pinned audit. Compatible with host Python3.12+.
"""

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

LOG_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \w+ \[([^\]]+)\] ")
CALL_INPUT = re.compile(r": nexus\[([^\]]+)\]: parsed input arguments:")
CALL_OUTPUT = re.compile(r": nexus\[([^\]]+)\]: tool container .* stdout:$")
CALL_FINISH = re.compile(r": nexus\[([^\]]+)\]: call finished: status=([^ ]+)")
CALL_INVALID = re.compile(r": nexus\[([^\]]+)\]: failed to parse input arguments:")
STOP_REASON = re.compile(r': stop reason: "([^"\n]+)" \(terminal: (true|false)\)$')
HTTP_ERROR = re.compile(
    r"\b(?:HTTP(?:/\d(?:\.\d)?)?\s+|(?:API\s+)?(?:error|status)(?:\s+code)?\s*[:=]?\s*)"
    r"([45]\d{2})\b|\b(401|402|403|408|429|500|502|503|504)\s+"
    r"(?:Unauthorized|Payment Required|Forbidden|Request Timeout|Too Many Requests|"
    r"Internal Server Error|Bad Gateway|Service Unavailable|Gateway Timeout)\b",
    re.IGNORECASE,
)


def classify_provider_error(record):
    """Classify recorded transport failures, never model answers or bare numbers.

    A stop here is operational: it says nothing about whether earlier world
    actions already made the task unwinnable. Keep that independent evidence.
    """
    if record.get("Kind") != "Error":
        return None
    details = record.get("Details") or {}
    error = details.get("Error") or {}
    message = error.get("Message", "") if isinstance(error, dict) else ""
    if not isinstance(message, str):
        return None
    match = HTTP_ERROR.search(message)
    if match is None:
        return None
    status = int(match[1] or match[2])
    category = (
        "billing_or_quota" if status == 402
        else "rate_limited" if status == 429
        else "authentication" if status == 401
        else "permission_denied" if status == 403
        else "provider_unavailable" if status >= 500 or status == 408
        else "request_rejected"
    )
    return {"http_status": status, "category": category, "stop_batch": True}


def read(path):
    return json.loads(path.read_text())


def seconds(value):
    return value / 1_000_000_000 if isinstance(value, int) and not isinstance(value, bool) else None


def log_evidence(path, records):
    """Associate unprefixed container output only with unambiguous trace blocks.

    Interleaved tasks, duplicate starts and context mismatches are deliberately
    unknown: a convenience readout must not invent isolation or public access.
    """
    if not path.is_file():
        return None, {}
    suffixes = {r["TraceID"]: f"{provider}: {r['Run']}: {r['Task']}: " for provider, r in records}
    names = {r["Task"] for _, r in records}
    blocks, active = {}, set()
    context = pending = first_task = None
    for line in path.read_text(errors="replace").splitlines():
        if line.endswith(": starting task...") and any(
            line.endswith(f"{name}: starting task...") for name in names
        ):
            first_task = first_task or line[:19]
        if pending:
            trace, call_id = pending
            call = blocks[trace]["calls"][call_id]
            try:
                value = json.loads(line)
            except ValueError:
                value = None
            call["response"] = value if isinstance(value, dict) else None
            pending = None
        prefix = LOG_PREFIX.match(line)
        if prefix:
            trace = prefix[1]
            context = trace if trace in blocks else None
            if trace not in suffixes:
                if line.endswith(": starting task..."):
                    for other in active:
                        blocks[other]["ambiguous"] = True
                continue
            expected = suffixes[trace]
            matches_context = line[prefix.end() :].startswith(expected)
            if line.endswith(": starting task..."):
                if trace in blocks:
                    blocks[trace]["ambiguous"] = True
                else:
                    blocks[trace] = {
                        "ambiguous": not matches_context,
                        "finished": False,
                        "calls": {},
                        "performance": None,
                        "structure": None,
                        "last_stop": None,
                        "operator_report": None,
                        "operator_summary": None,
                    }
                if active:
                    for other in active | {trace}:
                        blocks[other]["ambiguous"] = True
                active.add(trace)
                context = trace
            if trace not in blocks:
                continue
            block = blocks[trace]
            if not matches_context:
                block["ambiguous"] = True
            if "task has finished in " in line:
                block["finished"] = True
                active.discard(trace)
            if match := STOP_REASON.search(line):
                block["last_stop"] = (match[1], match[2] == "true")
            if match := CALL_INPUT.search(line):
                if match[1] in block["calls"]:
                    block["ambiguous"] = True
                block["calls"][match[1]] = {}
            if match := CALL_INVALID.search(line):
                if match[1] in block["calls"]:
                    block["ambiguous"] = True
                block["calls"][match[1]] = {"response": None, "invalid_arguments": True}
            if match := CALL_OUTPUT.search(line):
                call = block["calls"].setdefault(match[1], {})
                if "response" in call:
                    block["ambiguous"] = True
                pending = trace, match[1]
            if match := CALL_FINISH.search(line):
                block["calls"].setdefault(match[1], {})["status"] = match[2]
        if context is not None:
            for marker, key in (
                ("NEXUS terminal performance: ", "performance"),
                ("interference_structure ", "structure"),
                ("NEXUS operator summary: ", "operator_summary"),
            ):
                if marker in line:
                    try:
                        value = json.loads(line.split(marker, 1)[1])
                    except ValueError:
                        blocks[context]["ambiguous"] = True
                    else:
                        if isinstance(value, dict):
                            blocks[context][key] = value
                        else:
                            blocks[context]["ambiguous"] = True
            marker = "NEXUS operator diagnostic: "
            if marker in line:
                try:
                    value = json.loads(line.split(marker, 1)[1])
                except ValueError:
                    blocks[context]["ambiguous"] = True
                else:
                    if isinstance(value, dict) and value.get("kind") == "report":
                        blocks[context]["operator_report"] = value
    return first_task, blocks


def public_response(value):
    return isinstance(value, dict) and (
        "episode_id" in value
        or "observation" in value
        or {"filename", "content"} <= value.keys()
        or {"turn", "status", "actions_remaining"} <= value.keys()
    )


def run_config_differences(configured, snapshot, retry_policy):
    """Compare effective settings, allowing the API's omitted zero/null defaults."""

    def parameters(values):
        # MindTrial serializes these concrete bool fields even when YAML omits
        # their false default (OpenAI; both fields on Google). Do not drop other
        # false/zero values: nullable provider parameters can change behavior.
        false_defaults = {"text-response-format", "text-response-format-with-tools"}
        return {
            k: v
            for k, v in (values or {}).items()
            if v is not None and v != [] and not (k in false_defaults and v is False)
        }

    differences = []
    if parameters(snapshot.get("ModelParameters")) != parameters(
        configured.get("model-parameters")
    ):
        differences.append("model_parameters")
    if snapshot.get("MaxRequestsPerMinute") != configured.get("max-requests-per-minute"):
        differences.append("max_requests_per_minute")
    if snapshot.get("DisableStructuredOutput", False) != configured.get(
        "disable-structured-output", False
    ):
        differences.append("disable_structured_output")
    actual_retry = snapshot.get("RetryPolicy") or {}
    for name, key in (
        ("max-retry-attempts", "MaxRetryAttempts"),
        ("initial-delay-seconds", "InitialDelaySeconds"),
    ):
        if name in retry_policy and actual_retry.get(key, 0) != retry_policy[name]:
            differences.append("retry_policy." + name)
    return differences


def attempt_diagnostics(record, telemetry, block, *, log_exists):
    tool_calls = telemetry.get("ToolCalls")
    calls = None if tool_calls is None else [c for c in tool_calls if c.get("Tool") == "nexus"]
    result = {
        "log_evidence": "missing_log" if not log_exists else "unmatched_trace",
        "world_access": None,
        "successful_nexus_responses_observed": None,
        "tool_log_complete": None,
        "terminal_status": None,
        "termination_reason": None,
        "accepted_world_actions": None,
        "last_observed_turn": None,
        "last_observed_world_state": None,
        "provider_stop_reason": None,
        "provider_stop_source": None,
        "provider_http_status": None,
        "provider_error": None,
        "world_win_observed": None,
        "physical_goal_satisfied": None,
        "evidence_support": None,
        "first_submission_evidence_support": None,
        "correct_state_without_successful_finish": None,
        "physical_continuation": None,
        "response_text_present": None,
        "tool_count_convention": None,
        "structure": None,
        "tool_call_status_counts": None
        if calls is None
        else dict(Counter(c.get("Status", "unknown") for c in calls)),
        "outcome": "unknown",
    }
    if block is not None and block["ambiguous"]:
        result["log_evidence"] = "ambiguous_trace"
    elif block is not None:
        logged = block["calls"]
        count = ((telemetry.get("ToolUsage") or {}).get("nexus") or {}).get("CallCount")
        invalid_count = sum(c.get("Status") == "invalid_arguments" for c in calls or [])
        # MindTrial versions differ on whether pre-execution argument failures
        # contribute to ToolUsage. Detailed identities must still all match.
        count_matches = calls is not None and count in (len(calls), len(calls) - invalid_count)
        complete = (
            calls is not None
            and count_matches
            and block["finished"]
            and len({c.get("CallID") for c in calls}) == len(calls)
            and set(logged) == {c.get("CallID") for c in calls}
            and all(
                logged[c["CallID"]].get("status") == c.get("Status")
                and "response" in logged[c["CallID"]]
                and (
                    c.get("Status") != "success" or public_response(logged[c["CallID"]]["response"])
                )
                for c in calls
            )
        )
        responses = [
            c["response"]
            for c in logged.values()
            if c.get("status") == "success" and public_response(c.get("response"))
        ]
        turns = [
            value
            for response in responses
            for value in (
                response.get("turn"),
                response.get("current_turn"),
                (response.get("observation") or {}).get("turn"),
            )
            if type(value) is int
        ]
        performance = block["performance"] or (block.get("operator_report") or {}).get("performance") or {}
        summary = block.get("operator_summary") or {}
        decision = performance.get("decision_diagnostics") or summary
        states = []
        for response in responses:
            state = response.get("observation", response)
            status = state.get("terminal_status", state.get("status"))
            if type(state.get("turn")) is int and status in ("active", "won", "failed"):
                states.append(
                    {
                        "turn": state["turn"],
                        "status": status,
                        "actions_remaining": state.get("actions_remaining"),
                    }
                )
        last_stop = block.get("last_stop")
        if block["finished"] and last_stop and last_stop[1]:
            result.update(provider_stop_reason=last_stop[0], provider_stop_source="trace_log")
        result.update(
            log_evidence="matched" if complete else "incomplete_tool_log",
            world_access=True if responses else False if complete else None,
            successful_nexus_responses_observed=len(responses),
            tool_log_complete=complete,
            terminal_status=performance.get("terminal_status", summary.get("status")),
            termination_reason=performance.get("termination_reason", summary.get("termination_reason")),
            accepted_world_actions=performance.get("actions_used", summary.get("turn")),
            last_observed_turn=max(turns) if turns else None,
            last_observed_world_state=states[-1] if states else None,
            tool_count_convention=(
                "all_detailed_calls"
                if count == len(calls or [])
                else "excludes_invalid_arguments"
                if count_matches
                else "unresolved"
            ),
            structure=block["structure"],
            world_win_observed=(performance.get("terminal_status", summary.get("status")) == "won")
            if performance.get("terminal_status", summary.get("status")) in ("active", "won", "failed") else None,
            physical_goal_satisfied=(decision["physical_goal_satisfied"]
                if decision.get("physical_goal_satisfied") is not None else performance.get("goal_satisfied")),
            evidence_support=decision.get("escape_classification"),
            first_submission_evidence_support=performance.get(
                "first_submission_supported_by_evidence", summary.get("first_submission_supported_by_evidence")
            ),
            correct_state_without_successful_finish=decision.get(
                "correct_state_without_successful_finish"
            ),
            physical_continuation=summary.get("physical_continuation") or (block.get("operator_report") or {}).get("physical_continuation"),
        )
    details = record.get("Details") or {}
    message = (details.get("Error") or {}).get("Message", "")
    answer = details.get("Answer") or {}
    if record["Kind"] == "Error":
        provider_error = classify_provider_error(record)
        result["provider_error"] = provider_error
        if provider_error is not None:
            result["provider_http_status"] = provider_error["http_status"]
        reason = ((details.get("Error") or {}).get("Details") or {}).get("Stop Reason")
        if isinstance(reason, list) and len(reason) == 1:
            reason = reason[0]
        if isinstance(reason, str) and reason:
            result.update(provider_stop_reason=reason, provider_stop_source="error_record_details")
    # An error message belongs to this exact record, even if logs are unavailable.
    if record["Kind"] == "Error" and re.search(r'stop reason:?\s*["\']?length\b', message):
        result.update(provider_stop_reason="length", provider_stop_source="error_record")
    if isinstance(answer.get("ActualAnswer"), str):
        result["response_text_present"] = bool(answer["ActualAnswer"].strip())
    elif isinstance(answer.get("ActualAnswer"), list) and all(
        isinstance(line, str) for line in answer["ActualAnswer"]
    ):
        result["response_text_present"] = any(line.strip() for line in answer["ActualAnswer"])
    elif "no actionable content" in message or "no response candidates" in message:
        result["response_text_present"] = False
    state = result["last_observed_world_state"] or {}
    if result["world_win_observed"] is None and state.get("status") in ("active", "won", "failed"):
        result["world_win_observed"] = state["status"] == "won"
    if record["Kind"] == "Passed":
        result["outcome"] = "reported_win"
    elif result["terminal_status"] == "won" or state.get("status") == "won":
        result["outcome"] = "world_won_without_accepted_result"
    elif (
        type((result["physical_continuation"] or {}).get("first_budget_infeasible_turn")) is int
    ):
        result["outcome"] = (
            "budget_infeasible_before_provider_error"
            if result["provider_error"] is not None else "budget_infeasible"
        )
    elif result["termination_reason"] == "action_budget" or (
        state.get("status") == "failed" and state.get("actions_remaining") == 0
    ):
        result["outcome"] = "action_budget_exhausted"
    elif result["provider_http_status"] == 429:
        result["outcome"] = "http_rate_limited"
    elif result["provider_error"] is not None:
        result["outcome"] = "http_" + result["provider_error"]["category"]
    elif result["provider_stop_reason"] == "length":
        result["outcome"] = (
            "response_length_with_text"
            if result["response_text_present"] is True
            else "response_length_without_text"
            if result["response_text_present"] is False
            else "response_length"
        )
    elif record["Kind"] == "Error" and "no response candidates" in message:
        result["outcome"] = "no_response_candidates"
    elif record["Kind"] == "Error" and "no actionable content" in message:
        result["outcome"] = "no_actionable_content"
    elif record["Kind"] == "Error":
        result["outcome"] = (
            "provider_interruption" if "failed to generate response:" in message else "result_error"
        )
    elif result["world_access"] is False and result["accepted_world_actions"] == 0:
        result["outcome"] = "no_successful_world_access"
    elif result["world_access"] is True and result["termination_reason"] == "harness_finalization":
        result["outcome"] = "stopped_after_world_access"
    return result


def summarize(directory):
    manifest = read(directory / "manifest.json")
    result_path = directory / "mindtrial.json"
    result_file_status = "present"
    if not result_path.is_file() or not result_path.stat().st_size:
        # Cancellation can leave zero bytes even when the process exits zero.
        # Keep every expected slot missing; logs are not invented result records.
        result_file_status = "missing_or_empty"
        result = {"FormatVersion": 1, "AppName": "MindTrial", "Results": {}}
    else:
        result = read(result_path)
    if result.get("FormatVersion") != 1 or result.get("AppName") != "MindTrial":
        raise ValueError("requires MindTrial results format1")
    for name, field in (("config.yaml", "effective_config_sha256"), ("tasks.yaml", "tasks_sha256")):
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != manifest[field]:
            raise ValueError(f"{name} checksum differs from the run manifest")
    config = read(directory / "config.yaml")["config"]
    tasks = read(directory / "tasks.yaml")["task-config"]["tasks"]
    expected = {
        (p["name"], r["name"], r["model"], t["name"])
        for p in config["providers"]
        if not p.get("disabled", False)
        for r in p["runs"]
        if not r.get("disabled", False)
        for t in tasks
        if not t.get("disabled", False)
    }
    configured = {
        (p["name"], r["name"], r["model"]): r
        for p in config["providers"]
        if not p.get("disabled", False)
        for r in p["runs"]
        if not r.get("disabled", False)
    }
    retry_policies = {
        (p["name"], r["name"], r["model"]): r.get("retry-policy", p.get("retry-policy", {}))
        for p in config["providers"]
        for r in p["runs"]
    }
    records_with_provider = [
        (provider, record) for provider, records in result["Results"].items() for record in records
    ]
    log = directory / "mindtrial.log"
    first_task_text, blocks = log_evidence(log, records_with_provider)
    rows, seen, trace_ids = [], Counter(), set()
    mismatches = []
    for provider, records in result["Results"].items():
        for record in records:
            trace = record["TraceID"]
            if trace in trace_ids:
                raise ValueError("duplicate result TraceID")
            trace_ids.add(trace)
            model = record.get("RunConfig", {}).get("Model")
            key = provider, record["Run"], model, record["Task"]
            seen[key] += 1
            configured_run = configured.get(key[:3])
            snapshot = record.get("RunConfig") or {}
            differences = (
                run_config_differences(configured_run, snapshot, retry_policies[key[:3]])
                if configured_run is not None
                else ["unconfigured_run"]
            )
            if differences:
                mismatches.append(trace)
            details = record.get("Details") or {}
            telemetry_key = "Error" if record["Kind"] == "Error" else "Answer"
            telemetry = details.get(telemetry_key) or {}
            usage = telemetry.get("Usage") or {}
            tool_usage = (telemetry.get("ToolUsage") or {}).get("nexus") or {}
            rows.append(
                {
                    "trace_id": trace,
                    "provider": provider,
                    "run": record["Run"],
                    "model": model,
                    "model_parameters": record.get("RunConfig", {}).get("ModelParameters"),
                    "disable_structured_output": snapshot.get("DisableStructuredOutput", False),
                    "configuration_differences": differences,
                    "run_config_sha256": hashlib.sha256(
                        json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode()
                    ).hexdigest(),
                    "task": record["Task"],
                    "reported_kind": record["Kind"],
                    "request_seconds": seconds(record.get("DurationNS")),
                    "nexus_container_seconds": seconds(tool_usage.get("TotalDurationNS")),
                    "tool_calls": tool_usage.get("CallCount"),
                    "usage": usage,
                    "usage_source": f"Details.{telemetry_key}" if telemetry else None,
                    "usage_partial": record["Kind"] == "Error",
                    "error_message": (details.get("Error") or {}).get("Message"),
                    "diagnostics": attempt_diagnostics(
                        record, telemetry, blocks.get(trace), log_exists=log.is_file()
                    ),
                }
            )
    started, ended = (datetime.fromisoformat(manifest[k]) for k in ("started_at", "finished_at"))
    first_task = None
    if first_task_text is not None:
        zone = parsedate_to_datetime(result["CreatedAt"]).tzinfo
        first_task = datetime.strptime(first_task_text, "%Y-%m-%d %H:%M:%S").replace(tzinfo=zone)
        if not started.replace(microsecond=0) <= first_task <= ended:
            raise ValueError("task timestamp outside run; cannot infer log timezone")
        first_task = max(started, first_task)
    groups = []
    for provider, run, model in sorted({(r["provider"], r["run"], r["model"]) for r in rows}):
        selected = [
            r for r in rows if (r["provider"], r["run"], r["model"]) == (provider, run, model)
        ]
        groups.append(
            {
                "provider": provider,
                "run": run,
                "model": model,
                "attempts": len(selected),
                "reported_kind_counts": dict(Counter(r["reported_kind"] for r in selected)),
                "diagnostic_outcome_counts": dict(
                    Counter(r["diagnostics"]["outcome"] for r in selected)
                ),
                "world_access_counts": {
                    label: sum(r["diagnostics"]["world_access"] is value for r in selected)
                    for label, value in (
                        ("confirmed", True),
                        ("no_response", False),
                        ("unknown", None),
                    )
                },
                "partial_telemetry_attempts": sum(r["usage_partial"] for r in selected),
                "reported_output_tokens": sum(r["usage"]["OutputTokens"] for r in selected)
                if all(type(r["usage"].get("OutputTokens")) is int for r in selected)
                else None,
                "reported_reasoning_tokens": sum(r["usage"]["ReasoningTokens"] for r in selected)
                if all(type(r["usage"].get("ReasoningTokens")) is int for r in selected)
                else None,
                "output_token_accounting": dict(
                    Counter(r["usage"].get("OutputTokenAccounting", "unknown") for r in selected)
                ),
                "request_seconds": sum(r["request_seconds"] for r in selected)
                if all(r["request_seconds"] is not None for r in selected)
                else None,
                "nexus_container_seconds": sum(r["nexus_container_seconds"] for r in selected)
                if all(r["nexus_container_seconds"] is not None for r in selected)
                else None,
            }
        )
    return {
        "version": "nexus-pilot-readout-v4",
        "app_version": result.get("AppVersion"),
        "result_file_status": result_file_status,
        "source_commit": manifest["source_commit"],
        "runtime_source_sha256": manifest["runtime_source_sha256"],
        "mindtrial_sha256": manifest["mindtrial_sha256"],
        "suite": manifest["suite"],
        "interactive": manifest.get("interactive"),
        "selection": manifest.get("selection"),
        "repetition": manifest.get("repetition"),
        "coverage_scope": "configured_file_crossing; further interactive deselection is unknown",
        "scope": "Reported results and conservative log diagnostics only; not public replay, private HMAC or receipt verification. Missing/ambiguous logs do not establish world access or absence of access. Error-record usage is partial recorded telemetry, not a complete account of an interrupted request. Never count failed/missing telemetry as zero effort. Output tokens may already include reasoning tokens; do not add them together.",
        "expected_attempts": len(expected),
        "recorded_attempts": len(rows),
        "matrix_complete": set(seen) == expected
        and all(v == 1 for v in seen.values())
        and not mismatches,
        "error_attempts": sum(r["reported_kind"] == "Error" for r in rows),
        "provider_error_attempts": sum(r["diagnostics"]["provider_error"] is not None for r in rows),
        "completed_without_provider_errors": set(seen) == expected
        and all(v == 1 for v in seen.values())
        and not mismatches and all(r["diagnostics"]["provider_error"] is None for r in rows),
        "configuration_mismatch_trace_ids": mismatches,
        "missing": [list(k) for k in sorted(expected - seen.keys())],
        "unexpected": [list(k) for k in sorted(seen.keys() - expected)],
        "repeated_conditions": [
            {"condition": list(k), "count": v} for k, v in seen.items() if v > 1
        ],
        "timing": {
            "launcher_wall_seconds": (ended - started).total_seconds(),
            "before_first_logged_task_seconds": None
            if first_task is None
            else (first_task - started).total_seconds(),
            "first_logged_task_to_exit_seconds": None
            if first_task is None
            else (ended - first_task).total_seconds(),
            "scope": "Log timestamps have one-second precision and use the result CreatedAt UTC offset; runs crossing an offset change need separate verification. Pre-task time includes interactive selection/startup. Request time includes network+inference, excludes tools/validation; tool time is container runtime. Neither sum is task wall time.",
        },
        "models": groups,
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_directory", type=Path, nargs="+")
    args = parser.parse_args()
    for directory in args.result_directory:
        report = summarize(directory)
        path = directory / "readout.json"
        path.write_text(json.dumps(report, indent=2) + "\n")
        print(
            f"{directory.name}: {report['recorded_attempts']}/{report['expected_attempts']} attempts; coverage_complete={report['matrix_complete']}; {path}"
        )
        for group in report["models"]:
            outcomes = ", ".join(
                f"{name}={count}" for name, count in group["diagnostic_outcome_counts"].items()
            )
            print(f"  {group['model']}: {outcomes}; world_access={group['world_access_counts']}")


if __name__ == "__main__":
    main()
