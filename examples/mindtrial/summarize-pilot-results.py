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
            if match := CALL_INPUT.search(line):
                if match[1] in block["calls"]:
                    block["ambiguous"] = True
                block["calls"][match[1]] = {}
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
    return first_task, blocks


def public_response(value):
    return isinstance(value, dict) and (
        "episode_id" in value
        or "observation" in value
        or {"filename", "content"} <= value.keys()
        or {"turn", "status", "actions_remaining"} <= value.keys()
    )


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
        complete = (
            calls is not None
            and ((telemetry.get("ToolUsage") or {}).get("nexus") or {}).get("CallCount")
            == len(calls)
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
        performance = block["performance"] or {}
        result.update(
            log_evidence="matched" if complete else "incomplete_tool_log",
            world_access=True if responses else False if complete else None,
            successful_nexus_responses_observed=len(responses),
            tool_log_complete=complete,
            terminal_status=performance.get("terminal_status"),
            termination_reason=performance.get("termination_reason"),
            accepted_world_actions=performance.get("actions_used"),
            last_observed_turn=max(turns) if turns else None,
            structure=block["structure"],
        )
    if record["Kind"] == "Error":
        message = record.get("Details", {}).get("Error", {}).get("Message", "")
        result["outcome"] = (
            "provider_interruption" if "failed to generate response:" in message else "result_error"
        )
    elif record["Kind"] == "Passed":
        result["outcome"] = "reported_win"
    elif result["world_access"] is False and result["accepted_world_actions"] == 0:
        result["outcome"] = "no_successful_world_access"
    elif result["termination_reason"] == "action_budget":
        result["outcome"] = "action_budget_exhausted"
    elif result["terminal_status"] == "won":
        result["outcome"] = "world_won_without_accepted_result"
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
        for r in p["runs"]
        if not r.get("disabled", False)
        for t in tasks
        if not t.get("disabled", False)
    }
    configured = {
        (p["name"], r["name"], r["model"]): r
        for p in config["providers"]
        for r in p["runs"]
        if not r.get("disabled", False)
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
            parameters = snapshot.get("ModelParameters") or {}
            if configured_run is not None and (
                any(
                    parameters.get(k) != v
                    for k, v in configured_run.get("model-parameters", {}).items()
                )
                or snapshot.get("MaxRequestsPerMinute")
                != configured_run.get("max-requests-per-minute")
            ):
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
                "request_seconds": sum(r["request_seconds"] for r in selected)
                if all(r["request_seconds"] is not None for r in selected)
                else None,
                "nexus_container_seconds": sum(r["nexus_container_seconds"] for r in selected)
                if all(r["nexus_container_seconds"] is not None for r in selected)
                else None,
            }
        )
    return {
        "version": "nexus-pilot-readout-v2",
        "app_version": result.get("AppVersion"),
        "result_file_status": result_file_status,
        "source_commit": manifest["source_commit"],
        "runtime_source_sha256": manifest["runtime_source_sha256"],
        "mindtrial_sha256": manifest["mindtrial_sha256"],
        "suite": manifest["suite"],
        "scope": "Reported results and conservative log diagnostics only; not public replay, private HMAC or receipt verification. Missing/ambiguous logs do not establish world access or absence of access. Error-record usage is partial recorded telemetry, not a complete account of an interrupted request. Never count failed/missing telemetry as zero effort. Output tokens may already include reasoning tokens; do not add them together.",
        "expected_attempts": len(expected),
        "recorded_attempts": len(rows),
        "matrix_complete": set(seen) == expected
        and all(v == 1 for v in seen.values())
        and not mismatches,
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
