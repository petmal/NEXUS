"""Requalify the current implementation before replacing its repair source binding.

Runs local proofs, finite conformance checks, and all 7,203 live policy/replay
cases. No model calls. A failing gate leaves the previous release manifest intact.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from nexus.evaluation.artifacts import atomic_json
from nexus.ontology.repair.qualification import (
    check_offline_proof, source_binding, witness_binding,
)

ROOT = Path(__file__).resolve().parents[1]


def main():
    sources = source_binding()
    check_offline_proof()
    witnesses = witness_binding()
    subprocess.run([
        sys.executable, '-m', 'pytest', '-q',
        'tests/unit/test_repair_construction.py',
        'tests/unit/test_repair_conformance.py',
        'tests/unit/test_repair_qualification.py',
        'tests/unit/test_repair_runtime.py', '--maxfail=1',
    ], cwd=ROOT, check=True)
    if sources != source_binding() or witnesses != witness_binding():
        raise RuntimeError('source or witness changed during qualification; retry from a stable tree')
    directory = ROOT / 'src/nexus/ontology/repair'
    path = directory / 'qualified-release.json'
    original = path.read_bytes()
    payload = json.loads(original)
    payload.update(sources=sources, witnesses=witnesses,
                   proof_sha256=hashlib.sha256((directory / 'query-upper-proof.json').read_bytes()).hexdigest())
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
    main()
