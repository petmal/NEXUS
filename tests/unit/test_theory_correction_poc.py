import importlib.util
from pathlib import Path
import sys

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/theory_correction_poc.py"
spec = importlib.util.spec_from_file_location("theory_correction_poc", SCRIPT)
poc = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = poc
spec.loader.exec_module(poc)


def test_effective_theory_is_exact_on_whole_disclosed_validity_domain():
    assert poc.prove_domain(poc.CorrectionPrior()) > 10_000


def test_calibration_does_not_hide_corrections_and_true_law_belongs_to_public_prior():
    spec, world, candidates = poc.build_case(17)
    assert world.rules["law"] in candidates
    assert candidates == spec.hypotheses()
    assert len(candidates) == 9
    assert world.public.evidence_files["theory.json"] == spec.public_json()
    assert world.public.evidence_files["facility_manual.txt"] == spec.manual()
    spec2, world2, candidates2 = poc.build_case(17)
    assert (spec, world, candidates) == (spec2, world2, candidates2)
