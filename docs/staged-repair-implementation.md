# Staged repair implementation ledger

Base: ca471a6702a4da8be9023b4846acef7cc24b2ae6 on feat/theory-prior-axis.
Purpose and contract: staged-repair-design.md. No paid evaluations or main merge.

## Phases

1. [complete] Inspect source; prove scalar mechanism, unique mission signatures,
   adaptive witness, fixed-panel comparison and finish-inclusive information bound.
   Add reusable finite-goal qualification helpers only where the history and new
   family both demonstrate a need. Persist proof outputs and regression witnesses.
2. [complete] Implement the opt-in ontology, strict schema/episode validation,
   public evidence, public-only policy, canonical physical goal and terminal tracker.
   Add semantic tests (transactionality, privacy, replay, finish feedback, recovery,
   prior/disclosure consistency, supported vs compatible wins).
3. [complete] Add source-bound preflight, ~10-run matrix and matching MindTrial YAML.
   Include old-family regressions, exact-law controls, multiple mechanisms and
   paired depth/theory comparisons with moderate P/R and no external Python.
4. [complete] Review actual diff independently, resolve findings, run focused and
   existing gates, refresh source-bound legacy artifacts through their generators,
   run full CI, and publish to the existing feature branch. Implementation commit:
   33c9181e5ef6256eace257f319c50e0f8bb7eb7c. All 770 local tests and every
   legacy/new preflight passed. Initial full CI passed behavior gates and caught
   the missing Docker build-context exception. Packaging commit e25887e fixes it;
   its independent image, proof/preflight, solver and fast gates passed. The full
   follow-up run 39300712416 is repeating unchanged extended/stress/CLI checks.

## Verification commands (extend as implemented)

- uv sync --frozen --all-extras
- uv run python scripts/staged_repair_oracle.py --output /tmp/staged-proof.json
- uv run pytest -q tests/unit/test_staged_repair.py tests/unit/test_goal_information.py
- uv run python scripts/preflight_staged_repair.py --output /tmp/staged-preflight.json
- Existing CI fast/proof/extended/stress and legacy immutable artifact checks.
- Actual single-session HTTP and CLI play, correct/incorrect receipt validation,
  deterministic replay, cold-process generation and terminal diagnostics timing.

## Completed / evidence

- Restored all 758 tracked files from pinned GitHub revision. Every blob SHA and
  the full tree SHA match upstream. Python 3.14.8 and frozen dependencies installed.
- Independent design review and scalar PoC passed. Full proof covers 20 conditional
  profiles. Live public-policy check passed all 216 worlds across all 5 supported
  T/D profiles (1,080 sessions). Fixed-panel live play fits the unchanged budget.
- Final local verification passed 770 tests (9 solver, 713 fast, 46 extended,
  2 stress). All legacy and staged preflights passed. The packaging-only follow-up
  adds one regression, which passed in CI; the corrected image also passed every
  preflight and OCI label verification.
- Important negative result: linked contexts leak useful upstream information.
  Their exact actual-world certificates need 3–4 readings; independent contexts
  range 3–6. Matrix includes qualified 6/5-reading independent cases, 4-reading linked
  cases, and a 3-reading shallow control. No claim of mandatory six-stage reasoning.
- Separate read-only implementation review completed; one stale-report finding
  fixed and verified. Legacy source bindings refreshed only after their original
  proof/witness identities and 15 prerequisite tests passed. A separate narrow
  review cleared the Docker/CI follow-up. See staged-repair-validation.md for
  exact source revisions, completed gates and the ongoing duplicate CI checks.

## Resume notes

- Workspace: /workspace/scratch/5185b9a844b2/NEXUS. It disconnected after local
  verification; GitHub is authoritative. Native clone is unavailable;
  GitHub connector works. Publish via create_tree/create_commit/update_ref with
  expected head; never force. Local Git root is reconstructed from exact objects.
- Keep old ontologies stable; source-bound qualification manifests need explicit
  refresh after verification. Do not weaken checks to make stale artifacts pass.
- Do not call hypothetical teaching example deep. New proofs measure mission
  information and experimental adaptation, not arbitrary cognition or failure rate.
