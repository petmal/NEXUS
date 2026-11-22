"""CI must fail closed when coverage or a required result is missing."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
spec = importlib.util.spec_from_file_location("nexus_ci", ROOT / "scripts/ci.py")
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)


def test_partition_assigns_all_cases_without_duplicates():
    groups = {"first": ["tests/a.py"], "second": ["tests/b.py"]}
    cases = ["tests/b.py::test_b", "tests/a.py::test_a[0]", "tests/a.py::test_a[1]"]
    result = ci.assign_tests(groups, cases)
    assert result == {"first": cases[1:], "second": cases[:1]}


@pytest.mark.parametrize("groups,cases", [
    ({"first": ["tests/a.py"]}, ["tests/b.py::test_new"]),
    ({"first": ["tests/a.py", "tests/empty.py"]}, ["tests/a.py::test_a"]),
    ({"first": ["tests/a.py"], "second": ["tests/a.py"]}, ["tests/a.py::test_a"]),
    ({"first": ["tests/a.py"], "second": []}, ["tests/a.py::test_a"]),
    ({"first": ["tests/a.py"]}, []),
    ({"first": ["tests/a.py"]}, ["tests/a.py::test_a", "tests/a.py::test_a"]),
])
def test_partition_rejects_missing_empty_or_duplicate_coverage(groups, cases):
    with pytest.raises(ValueError):
        ci.assign_tests(groups, cases)


@pytest.mark.parametrize("damage", ["missing-group", "extra-group", "empty", "duplicate", "missing-file", "traversal"])
def test_manifest_rejects_invalid_ownership(tmp_path, monkeypatch, damage):
    monkeypatch.setattr(ci, "ROOT", tmp_path)
    groups = {g: [f"tests/{g}.py"] for g in ci.GROUPS}
    (tmp_path / "tests").mkdir()
    for paths in groups.values():
        (tmp_path / paths[0]).touch()
    if damage == "missing-group":
        del groups["core"]
    elif damage == "extra-group":
        groups["unknown"] = ["tests/core.py"]
    elif damage == "empty":
        groups["core"] = []
    elif damage == "duplicate":
        groups["core"] += groups["scientific"]
    elif damage == "missing-file":
        groups["core"] = ["tests/removed.py"]
    else:
        groups["core"] = ["tests/../outside.py"]
    path = tmp_path / "groups.json"
    path.write_text(json.dumps(groups))
    with pytest.raises(ValueError):
        ci.read_groups(path)


@pytest.mark.parametrize("status", ["failure", "skipped", "cancelled", "timed_out", "neutral", None])
@pytest.mark.parametrize("job", sorted(ci.REQUIRED_JOBS))
def test_aggregate_rejects_any_incomplete_dependency(job, status):
    needs = {g: {"result": "success"} for g in ci.REQUIRED_JOBS}
    needs[job]["result"] = status
    with pytest.raises(ValueError):
        ci.check_gate(needs)


def test_aggregate_requires_the_complete_successful_dependency_set():
    needs = {g: {"result": "success"} for g in ci.REQUIRED_JOBS}
    ci.check_gate(needs)
    for malformed in ({}, [], {**needs, "optional": {"result": "success"}},
                      {k: v for k, v in needs.items() if k != "container"}):
        with pytest.raises(ValueError):
            ci.check_gate(malformed)


@pytest.mark.parametrize("counts", [
    'tests="0"', 'tests="1" skipped="1"', 'tests="1" failures="1"', 'tests="1" errors="1"',
])
def test_zero_exit_does_not_hide_empty_or_skipped_tests(tmp_path, counts):
    path = tmp_path / "pytest.xml"
    path.write_text(f"<testsuites><testsuite {counts}/></testsuites>")
    with pytest.raises(ValueError):
        ci.check_test_report(path)


def test_complete_test_report_is_accepted(tmp_path):
    path = tmp_path / "pytest.xml"
    path.write_text('<testsuites><testsuite tests="2" skipped="0" failures="0" errors="0"/></testsuites>')
    ci.check_test_report(path)
