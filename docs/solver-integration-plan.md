# Integration execution record

Status: implementation complete; final validation and merge/cleanup in progress. User authorized integration, final testing, matrix, and branch/PR cleanup.

1. Audit: canonical and research heads recorded in solver-integration-design.md; PR #3 is
   overlapping but has useful physical-action delta and Boolean-deficit handling.
2. Review branch: feat/solver-diagnostics-integration starts from archived PoC head. Preserve
   PR #3 as an additional parent when committing the selected integrated tree.
3. Production solver: remove mode switches/process workers, keep exact optimized algorithm,
   fix certificate cache boundaries, preserve deterministic output. Retain focused invariant tests.
4. Diagnostics: retain #2 lifecycle/timing, integrate selected #3 semantics, version schema v3,
   pin its URL after the schema commit. Validate aliases, active/terminal separation and Boolean goals.
5. Calibration: write a machine-readable 10-cell run manifest plus a concise operating guide with
   expected relative difficulties, paired/fresh seed policy and realistic tool-call ceilings.
6. Validation: frozen install; focused tests; full unit/integration; three-seed 24-profile stress;
   differential reference cases; D5/P3/R1/R2; live service/request/validate/replay; build smoke.
   No Docker daemon is installed locally; use a container CI smoke gate if available.
7. Review and merge only a tested tree into feat/epistemic-calibration. Record results and remaining
   limitations. Preserve history before closing superseded PRs and deleting expected branch heads.
8. Cleanup workflow: run only for this merged integration PR, use explicit ref leases, then remove
   temporary workflow. Verify final branch inventory, canonical head, clean tree and PR states.

The prior PoC checkout at ../nexus is retained as the read-only differential oracle. New work is
in ../nexus-integration. Do not edit the reference while tests are running. All long-running runs
write incremental evidence; update this record and checkpoint changes at phase boundaries.

## Checkpoint (2026-10-06)

- Review PR: https://github.com/petmal/NEXUS/pull/5; current code head
  `46fd17091a411998758de54ff4f08bed515ca3f7`.
- Schema v3 published at `15a252279da3da870fab354d92cb3e92726445d2`; remote bytes verified.
- Independent review found a warm/cold certificate exhaustion-flag inconsistency. Fixed and
  regression-tested. No new active-play hint or exact-result regression found in bounded review.
- Final local unit/integration: 127 passed, two existing fixture serializer warnings, 98.30 s.
- Property suite: 3 passed, including 72 generated D/P/seed cases and paired resource pressure;
  152.10 s. CLI generate/qualify/solve/replay passed; live HTTP/client/validator won/abandoned
  flows passed; wheel and sdist built; changed-file Ruff and whitespace checks passed.
- Final differential run: `docs/profiling/integration-final/`, all 30 cases passed, two independent case
  workers for correctness throughput. Do not use these concurrent timings as latency claims.
- CI full gate: https://github.com/petmal/NEXUS/actions/runs/37538266610 (passed, including container build/smoke).
- Final source was frozen before the final differential run. Earlier exploratory evidence in
  `docs/profiling/integration/` is superseded and will be removed after its process exits.
- Remaining:
  publish report/evidence; merge PR5 into canonical; retire #2/#3/#4 and only preserved heads;
  remove the one-use cleanup workflow and verify branch/PR inventories.
