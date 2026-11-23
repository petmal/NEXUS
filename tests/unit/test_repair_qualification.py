"""Checkable success upper bounds, explicit scope and false-payload rejection."""

from dataclasses import replace
from fractions import Fraction

import pytest

from nexus.ontology.repair.proof import check
from nexus.ontology.repair.qualification import check_offline_proof, proof_payload
from nexus.solver.finite_game import SearchBudget, SearchLimit


def refresh_module():
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location(
        "repair_refresh", Path(__file__).parents[2] / "scripts/refresh_repair_release.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("damage", ["deselected", "skipped", "failed", "interrupted", "missing-test", "missing-count", "short-loop"])
def test_release_attestation_requires_actual_exhaustive_completion(damage):
    from types import SimpleNamespace

    module = refresh_module()
    evidence = module.Completion()
    nodes = [module.LIVE_TEST, "tests/unit/test_repair_conformance.py::finite"]
    evidence.pytest_collection_finish(SimpleNamespace(items=[SimpleNamespace(nodeid=n) for n in nodes]))
    for node in nodes:
        if damage == "missing-test" and node == nodes[-1]:
            continue
        evidence.pytest_runtest_logreport(SimpleNamespace(
            nodeid=node, when="call", failed=damage == "failed", skipped=damage == "skipped",
            passed=damage not in ("failed", "skipped"),
            user_properties=[] if damage == "missing-count" else [
                ("live_policy_receipt_replay_cases", 7202 if damage == "short-loop" else 7203)
            ],
        ))
    if damage == "deselected":
        evidence.pytest_deselected([object()])
    with pytest.raises(RuntimeError, match="did not complete"):
        evidence.evidence(2 if damage == "interrupted" else 0)


@pytest.mark.parametrize("outcome", ["success", "missing-report", "short-loop", "interrupted", "preflight-failed"])
def test_refresh_isolates_selection_and_preserves_manifest_on_incomplete_checks(tmp_path, monkeypatch, outcome):
    import json
    import subprocess

    module = refresh_module()
    directory = tmp_path / "src/nexus/ontology/repair"
    directory.mkdir(parents=True)
    path = directory / "qualified-release.json"
    original = b'{"evidence": {}}\n'
    path.write_bytes(original)
    (directory / "query-upper-proof.json").write_text('{}')
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "check_offline_proof", lambda: None)
    monkeypatch.setattr(module, "source_binding", lambda: {"source": "bound"})
    monkeypatch.setattr(module, "witness_binding", lambda: {"test": "bound"})
    monkeypatch.setenv("PYTEST_ADDOPTS", "-k test_release_identity_mismatch_fails_closed")

    def execute(command, **kwargs):
        if "--checks-report" in command:
            assert "PYTEST_ADDOPTS" not in kwargs["env"]
            if outcome == "interrupted":
                raise KeyboardInterrupt()
            if outcome != "missing-report":
                from pathlib import Path

                Path(command[-1]).write_text(json.dumps({"tests_passed": 30,
                    "live_policy_receipt_replay_cases": 7202 if outcome == "short-loop" else 7203}))
        elif outcome == "preflight-failed":
            raise subprocess.CalledProcessError(1, command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(module.subprocess, "run", execute)
    if outcome == "success":
        module.main()
        assert json.loads(path.read_text())["evidence"]["completion"]["live_policy_receipt_replay_cases"] == 7203
    else:
        with pytest.raises((OSError, RuntimeError, KeyboardInterrupt, subprocess.CalledProcessError)):
            module.main()
        assert path.read_bytes() == original


def test_checked_relaxation_meets_ceiling_and_has_complete_choice_payload():
    proof = check_offline_proof()
    assert Fraction(proof.upper_mass, proof.worlds) == Fraction(3, 7)
    assert len(proof.choices) == 576 and proof.feedback_rounds == 2


def test_missing_query_choice_and_forged_bound_are_rejected():
    proof = proof_payload()
    with pytest.raises(ValueError, match="coverage"):
        check(replace(proof, choices=proof.choices[:-1]))
    changed = ((proof.choices[0][0], -1), *proof.choices[1:])
    with pytest.raises(ValueError, match="independent enumeration"):
        check(replace(proof, choices=changed))
    for changed in (
        replace(proof, query_costs=(4,) * 15),
        replace(proof, prior="skewed"),
        replace(proof, feedback_rounds=3),
        replace(proof, worlds=7203),
    ):
        with pytest.raises(ValueError, match="scope"):
            check(changed)
    with pytest.raises(SearchLimit):
        check(proof, limits=SearchBudget(max_states=1))


def test_release_identity_mismatch_fails_closed(monkeypatch):
    import json
    from pathlib import Path

    from nexus.ontology.repair import qualification as q

    original = Path.read_text

    def forged(path, *args, **kwargs):
        if path.name == "qualified-release.json":
            return json.dumps(
                {
                    "version": "repair-live-conformance-v1",
                    "sources": {},
                    "witnesses": {},
                    "proof_sha256": "wrong",
                }
            )
        return original(path, *args, **kwargs)

    q.release_matches.cache_clear()
    monkeypatch.setattr(Path, "read_text", forged)
    try:
        assert not q.release_matches()
        with pytest.raises(ValueError, match="stale"):
            q.require_release()
    finally:
        q.release_matches.cache_clear()


def test_offline_runner_rejects_wrong_rounds_and_preserves_unknown(tmp_path):
    import json
    import subprocess
    import sys
    from pathlib import Path

    script = Path(__file__).parents[2] / "scripts" / "qualify_repair_offline.py"
    output = tmp_path / "proof.json"
    wrong = subprocess.run(
        [sys.executable, str(script), "--output", str(output), "--rounds", "0"],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert wrong.returncode != 0 and "exactly --rounds 2" in wrong.stderr
    assert not output.exists()
    capped = subprocess.run(
        [
            sys.executable,
            str(script),
            "--output",
            str(output),
            "--max-states",
            "1",
            "--max-seconds",
            "10",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert capped.returncode == 0
    result = json.loads(output.read_text())
    assert result["status"] == "unknown" and "proof" not in result
