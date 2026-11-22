"""Run the same explicit test groups locally and in GitHub Actions.

Only partition/run import pytest. The final status gate uses Python's standard
library and treats missing, skipped and cancelled dependencies as failures.
"""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
from time import perf_counter
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ("core", "scientific", "planning", "interfaces", "evaluation")
CONTAINERS = ("scientific", "planning", "panels")
REQUIRED_JOBS = {"quality", "host", "container"}


def read_groups(path=ROOT / "tests/ci-groups.json"):
    groups = json.loads(path.read_text())
    if not isinstance(groups, dict) or set(groups) != set(GROUPS):
        raise ValueError(f"Expected exactly these test groups: {GROUPS}")
    owners = {}
    for group, paths in groups.items():
        if not isinstance(paths, list) or not paths:
            raise ValueError(f"Empty or invalid group: {group}")
        for name in paths:
            if (not isinstance(name, str) or not name.startswith("tests/")
                    or ".." in Path(name).parts or not name.endswith(".py")):
                raise ValueError(f"Invalid test module: {name!r}")
            if name in owners:
                raise ValueError(f"Duplicate test module: {name}")
            if not (ROOT / name).is_file():
                raise ValueError(f"Missing test module: {name}")
            owners[name] = group
    return groups


def assign_tests(groups, nodeids):
    """Prove a disjoint, complete partition against actual pytest collection."""
    owners = {name: group for group, paths in groups.items() for name in paths}
    if len(owners) != sum(map(len, groups.values())):
        raise ValueError("Duplicate test module")
    if not nodeids or len(set(nodeids)) != len(nodeids):
        raise ValueError("Empty collection or duplicate test IDs")
    collected = {node.split("::", 1)[0] for node in nodeids}
    missing, stale = collected - owners.keys(), owners.keys() - collected
    if missing or stale:
        raise ValueError(f"Unassigned modules: {sorted(missing)}; empty/stale modules: {sorted(stale)}")
    result = {group: [] for group in groups}
    for node in nodeids:
        result[owners[node.split("::", 1)[0]]].append(node)
    if any(not cases for cases in result.values()):
        raise ValueError("Every group must collect tests")
    return result


def partition():
    import pytest

    class Collection:
        nodeids = []

        def pytest_collection_finish(self, session):
            self.nodeids = [item.nodeid for item in session.items]

    collected = Collection()
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        code = pytest.main(["--collect-only", "-q", "tests"], plugins=[collected])
    if code:
        raise ValueError(f"Test collection failed ({code}):\n{output.getvalue()}")
    return assign_tests(read_groups(), collected.nodeids)


def check_gate(needs):
    if not isinstance(needs, dict) or set(needs) != REQUIRED_JOBS:
        raise ValueError("Required job results are missing or unexpected")
    failed = {name: value.get("result") if isinstance(value, dict) else None
              for name, value in needs.items()
              if not isinstance(value, dict) or value.get("result") != "success"}
    if failed:
        raise ValueError(f"Required CI groups did not all succeed: {failed}")


def check_test_report(path):
    suites = ElementTree.parse(path).getroot().findall("testsuite")
    if not suites or sum(int(s.get("tests", "0")) for s in suites) == 0:
        raise ValueError("Required test group produced no test cases")
    if any(int(s.get(field, "0")) for s in suites for field in ("failures", "errors", "skipped")):
        raise ValueError("Required test group has failed, errored or skipped tests")


def command_output(command):
    return subprocess.check_output(command, cwd=ROOT, text=True).strip()


def run(group, output):
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "group": group,
        "tested_revision": command_output(["git", "rev-parse", "HEAD"]),
        "working_tree_dirty": bool(command_output(["git", "status", "--porcelain"])),
        "pr_head": os.environ.get("NEXUS_PR_HEAD"),
        "python": platform.python_version(),
        "uv": command_output(["uv", "--version"]),
        "runner_image": os.environ.get("ImageVersion"),
        "stress_seed_count": 10,
        "steps": [],
    }
    env = dict(os.environ, NEXUS_STRESS_SEED_COUNT="10")
    # Do not allow caller flags to deselect tests from a required group.
    env.pop("PYTEST_ADDOPTS", None)
    env.pop("NEXUS_STRESS_FAIL_FAST", None)
    started = perf_counter()
    result = 1
    try:
        with tempfile.TemporaryDirectory(prefix=f"nexus-ci-{group}-") as temporary:
            env["NEXUS_CI_TEMP"] = temporary
            commands = []
            if group in GROUPS:
                commands.append([sys.executable, "-m", "pytest", "-q", "--strict-markers",
                                 "--durations=20", f"--junitxml={output / 'pytest.xml'}",
                                 *read_groups()[group]])
                commands.append(["bash", "scripts/ci-host.sh", group])
            elif group == "quality":
                commands.append(["bash", "scripts/ci-host.sh", group])
            else:
                commands.append(["bash", "scripts/ci-container.sh", group.removeprefix("container-")])
            for command in commands:
                print("+", " ".join(command), flush=True)
                step_started = perf_counter()
                result = subprocess.run(command, cwd=ROOT, env=env, check=False).returncode
                report["steps"].append({"command": command, "seconds": perf_counter() - step_started,
                                        "exit_code": result})
                if result:
                    break
                if command[:3] == [sys.executable, "-m", "pytest"]:
                    # Pytest exits zero when tests are skipped; the full CI gate must not.
                    result = 1
                    check_test_report(output / "pytest.xml")
                    result = 0
    except BaseException:
        result = 1
        raise
    finally:
        report.update(seconds=perf_counter() - started, exit_code=result)
        (output / "timing.json").write_text(json.dumps(report, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    collect = sub.add_parser("partition", help="Verify that every collected test has exactly one owner")
    collect.add_argument("--output", type=Path)
    execute = sub.add_parser("run", help="Run a complete group, including its non-pytest checks")
    execute.add_argument("group", choices=("quality", *GROUPS, *(f"container-{g}" for g in CONTAINERS)))
    execute.add_argument("--output", type=Path)
    sub.add_parser("gate", help="Validate GitHub needs JSON from NEXUS_CI_NEEDS")
    args = parser.parse_args()
    os.chdir(ROOT)
    try:
        if args.command == "gate":
            check_gate(json.loads(os.environ["NEXUS_CI_NEEDS"]))
            print("All required CI groups passed.")
        elif args.command == "partition":
            groups = partition()
            print(json.dumps({"counts": {g: len(v) for g, v in groups.items()},
                              "total": sum(map(len, groups.values()))}, indent=2))
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(json.dumps(groups, indent=2) + "\n")
        else:
            return run(args.group, (args.output or Path("ci-results") / args.group).resolve())
    except (KeyError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"CI blocked: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
