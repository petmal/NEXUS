"""Checkable success upper bounds, explicit scope and false-payload rejection."""

from dataclasses import replace
from fractions import Fraction

import pytest

from nexus.ontology.repair.proof import check
from nexus.ontology.repair.qualification import check_offline_proof, proof_payload
from nexus.solver.finite_game import SearchBudget, SearchLimit


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
