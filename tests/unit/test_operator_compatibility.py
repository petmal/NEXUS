"""Packaged operator entry points run without NEXUS or site packages."""

import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).parents[2]
EXAMPLES = ROOT / "examples/mindtrial"


@pytest.mark.parametrize("entry", [
    "coordination-runner.py", "interference-runner.py", "interference-comparison-runner.py",
    "cross-axis-runner.py", "capability-smoke-runner.py", "fresh-world-runner.py",
    "summarize-pilot-results.py",
])
def test_packaged_entry_points_need_only_operator_standard_library(tmp_path, entry):
    python = os.environ.get("NEXUS_OPERATOR_PYTHON") or sys.executable
    # CI supplies Python 3.12; ordinary local pytest uses its current interpreter.
    for source, target in (
        ("coordination-runner.py", "pilot_runner.py"),
        ("summarize-pilot-results.py", "summarize_results.py"),
        ("audit_mounts.py", "audit_mounts.py"),
        (entry, "runner.py"),
    ):
        shutil.copyfile(EXAMPLES / source, tmp_path / target)
    check = subprocess.run(
        [python, "-I", "-S", "-c",
         "import importlib.util,sys; assert importlib.util.find_spec('nexus') is None; "
         "print('.'.join(map(str,sys.version_info[:2])))"],
        cwd=tmp_path, capture_output=True, text=True, check=True,
    )
    if os.environ.get("NEXUS_OPERATOR_PYTHON"):
        assert check.stdout.strip() == "3.12"
    result = subprocess.run(
        [python, "-I", "-S", str(tmp_path / "runner.py"), "--help"],
        cwd=tmp_path, capture_output=True, text=True, timeout=20, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "usage:" in result.stdout.lower()
