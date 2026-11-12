"""Check a one-row mount smoke, including the link from the harness row to its service(s)."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def linked_attempts(results, log, bundles):
    rows = [row for group in results["Results"].values() for row in group]
    if len(rows) != 1 or rows[0]["Task"] != "NEXUS fresh-F05":
        raise ValueError("expected exactly one F05 result")
    row = rows[0]
    instances = re.findall(
        rf'\[{re.escape(row["TraceID"])}\][^\n]*?service nexus: created service container "(mindtrial-service-[a-z0-9]+)"',
        log,
    )
    if not instances or set(instances) != set(bundles) or len(instances) != len(set(instances)):
        raise ValueError("service instances in the row's debug log do not match retained bundles")
    return row, instances


def check(run, image):
    parent = run / "private-audits"
    reports = {}
    for bundle in sorted(parent.glob("mindtrial-service-*")):
        # Read root-owned 0700 bundles through the exact generating image, read-only.
        proc = subprocess.run([
            "docker", "run", "--rm", "--network", "none", "-v", f"{parent}:/audits:ro",
            image, "verify-audit", f"/audits/{bundle.name}", "--json",
        ], capture_output=True, text=True, check=False)
        if proc.returncode:
            print(f"{bundle.name}: verification failed: {proc.stderr.strip()}", file=sys.stderr)
            reports[bundle.name] = None
            continue
        report = json.loads(proc.stdout)
        reports[bundle.name] = report
        print(f"{bundle.name}: {report['world_status']}, {report['accepted_actions']} accepted actions")
    (run / "verification.json").write_text(json.dumps(reports, indent=2) + "\n")
    json_files = list((run / "results").rglob("*.json"))
    logs = list((run / "results").rglob("*.log"))
    if len(json_files) != 1 or len(logs) != 1:
        raise ValueError("expected one MindTrial JSON report and one debug log; see the run folder")
    row, instances = linked_attempts(json.loads(json_files[0].read_bytes()), logs[0].read_text(), reports)
    if any(not r or not r["trace_replay_verified"] or not r["public_capture_complete"] for r in reports.values()):
        raise ValueError("partial or unverifiable export; keep all attempts for diagnosis")
    final = reports[instances[-1]]
    print(f"Harness {row['Kind']} (trace {row['TraceID']}); final service {instances[-1]}: {final['world_status']}.")
    if (row["Kind"] != "Passed" or row.get("Details", {}).get("Validation", {}).get("Title") != "Valid victory code"
            or final["world_status"] != "won" or final["receipt_verification"] != "original_secret_verified"):
        raise ValueError("storage verified, but F05 did not produce both a verified win and an accepted receipt")
    print("Live mount smoke passed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("image")
    args = parser.parse_args()
    try:
        check(args.run.resolve(), args.image)
    except (OSError, KeyError, ValueError) as exc:
        parser.exit(1, f"Mount smoke: {exc}\n")
