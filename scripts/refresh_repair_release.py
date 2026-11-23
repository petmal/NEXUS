"""Requalify the current implementation before replacing its repair source binding.

Runs local proofs, finite conformance checks, and all 7,203 live policy/replay
cases. No model calls. A failing gate leaves the previous release manifest intact.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from nexus.evaluation.artifacts import atomic_json
from nexus.ontology.repair.qualification import (
    check_offline_proof, source_binding, witness_binding,
)

ROOT = Path(__file__).resolve().parents[1]
LIVE_TEST = "tests/unit/test_repair_runtime.py::test_every_truth_reaches_actual_victory_through_three_public_rounds"
CHECKS = (
    "tests/unit/test_repair_construction.py",
    "tests/unit/test_repair_conformance.py",
    "tests/unit/test_repair_qualification.py",
    "tests/unit/test_repair_runtime.py",
)


class Completion:
    """Only attest collected tests that finished, including the exhaustive loop."""

    def __init__(self):
        self.collected = set()
        self.passed = set()
        self.incomplete = False
        self.live_cases = None

    def pytest_collection_finish(self, session):
        self.collected = {item.nodeid for item in session.items}

    def pytest_deselected(self, items):
        self.incomplete |= bool(items)

    def pytest_runtest_logreport(self, report):
        self.incomplete |= report.failed or report.skipped
        if report.when == "call" and report.passed:
            self.passed.add(report.nodeid)
            if report.nodeid == LIVE_TEST:
                self.live_cases = dict(report.user_properties).get("live_policy_receipt_replay_cases")

    def evidence(self, exit_code):
        if (exit_code != 0 or self.incomplete or not self.collected
                or self.collected != self.passed or LIVE_TEST not in self.passed
                or self.live_cases != 7203):
            raise RuntimeError("Repair checks did not complete all tests and 7,203 live cases")
        return {"tests_passed": len(self.passed), "live_policy_receipt_replay_cases": self.live_cases}


def run_checks(report):
    import pytest

    completion = Completion()
    code = pytest.main(["-q", "-o", "addopts=", *CHECKS, "--maxfail=1"], plugins=[completion])
    atomic_json(report, completion.evidence(code))


def main():
    sources = source_binding()
    check_offline_proof()
    witnesses = witness_binding()
    env = dict(os.environ)
    env.pop("PYTEST_ADDOPTS", None)
    with tempfile.TemporaryDirectory(prefix="nexus-repair-checks-") as temporary:
        report = Path(temporary) / "completed.json"
        subprocess.run([
            sys.executable, str(Path(__file__).resolve()), "--checks-report", str(report),
        ], cwd=ROOT, env=env, check=True)
        completion = json.loads(report.read_text())
        if (completion.get("live_policy_receipt_replay_cases") != 7203
                or completion.get("tests_passed", 0) <= 0):
            raise RuntimeError("Missing repair completion evidence")
    if sources != source_binding() or witnesses != witness_binding():
        raise RuntimeError('source or witness changed during qualification; retry from a stable tree')
    directory = ROOT / 'src/nexus/ontology/repair'
    path = directory / 'qualified-release.json'
    original = path.read_bytes()
    payload = json.loads(original)
    payload.update(sources=sources, witnesses=witnesses,
                   proof_sha256=hashlib.sha256((directory / 'query-upper-proof.json').read_bytes()).hexdigest())
    payload['evidence']['completion'] = completion
    payload['evidence']['source_refresh'] = (
        f"{datetime.now(timezone.utc).date()}: independent stored-proof check, finite conformance, "
        'construction/qualification/runtime tests, and 7,203 live public-policy receipt/replay cases passed. '
        'See docs/release-readiness.md for current review scope and validation.'
    )
    atomic_json(path, payload)
    try:
        subprocess.run([sys.executable, 'scripts/preflight_repair.py'], cwd=ROOT, check=True)
    except BaseException:
        path.write_bytes(original)
        raise
    print('Repair release binding refreshed after proof and live conformance gates.')


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == "--checks-report":
        run_checks(Path(sys.argv[2]))
    else:
        main()
