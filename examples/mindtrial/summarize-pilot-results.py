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


def read(path):
    return json.loads(path.read_text())


def seconds(value):
    return value / 1_000_000_000 if isinstance(value, int) and not isinstance(value, bool) else None


def summarize(directory):
    manifest = read(directory / "manifest.json")
    result = read(directory / "mindtrial.json")
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
            answer = record.get("Details", {}).get("Answer") or {}
            usage = answer.get("Usage") or {}
            tool_usage = (answer.get("ToolUsage") or {}).get("nexus") or {}
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
                }
            )
    started, ended = (datetime.fromisoformat(manifest[k]) for k in ("started_at", "finished_at"))
    first_task = None
    log = directory / "mindtrial.log"
    if log.is_file():
        zone = parsedate_to_datetime(result["CreatedAt"]).tzinfo
        for line in log.read_text(errors="replace").splitlines():
            if re.search(r"NEXUS interference-\d+: starting task\.\.\.$", line):
                first_task = datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=zone)
                if not started.replace(microsecond=0) <= first_task <= ended:
                    raise ValueError("task timestamp outside run; cannot infer log timezone")
                first_task = max(started, first_task)
                break
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
                "request_seconds": sum(r["request_seconds"] for r in selected)
                if all(r["request_seconds"] is not None for r in selected)
                else None,
                "nexus_container_seconds": sum(r["nexus_container_seconds"] for r in selected)
                if all(r["nexus_container_seconds"] is not None for r in selected)
                else None,
            }
        )
    return {
        "version": "interference-readout-v1",
        "app_version": result.get("AppVersion"),
        "source_commit": manifest["source_commit"],
        "runtime_source_sha256": manifest["runtime_source_sha256"],
        "mindtrial_sha256": manifest["mindtrial_sha256"],
        "suite": manifest["suite"],
        "scope": "Reported results only; not public replay, private HMAC or receipt verification. Never count failed/missing telemetry as zero effort. Output tokens may already include reasoning tokens; do not add them together.",
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
            f"{directory.name}: {report['recorded_attempts']}/{report['expected_attempts']} attempts; complete={report['matrix_complete']}; {path}"
        )


if __name__ == "__main__":
    main()
