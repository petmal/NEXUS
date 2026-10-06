# Integration completion and resume record

Completed 2026-10-06. PR #5 integrated into `feat/epistemic-calibration` using the repository's
required rebase merge method. Integration commit: `3226d97ea78915fec5d0d97513bff6c327fd1e8d`.
`main` remains `bd39bcc5f59efc9cfd99e5ed1d7a803a042c8028`.

## Completed gates

- Production solver: interning, monotone budget bounds, transition reuse, sequential exact P3
  certificates with fallback; research process switches removed from runtime.
- Diagnostics: PR #2 lifecycle/timing/profiler plus selected #3 physical delta and Boolean deficits;
  immutable v3 schema `15a252279da3da870fab354d92cb3e92726445d2`, remote bytes verified.
- Review found one cache-status inconsistency; fixed and regression-tested.
- Final local tests: 127 unit/integration and 3 property tests passed. Stress covers 72 worlds.
- All 30 cold differential cases passed against final source fingerprints; exact episode and policy
  hashes match. Source files remained unchanged during the final run.
- Live HTTP/client/validator won and abandoned paths, CLI qualify/solve/replay, builds and Ruff passed.
- Full CI including container smoke passed: run `37538266610`, production code commit
  `46fd17091a411998758de54ff4f08bed515ca3f7`. Later changes affect workflow/docs/evidence only.

## Preservation and cleanup

Merge commits were disabled by repository policy. No settings were changed. A linear integration
commit was rebased; archive tag `archive/solver-diagnostics-2026-10-06` preserves original head
`a5280d42bcf88920b6c83105f8ed580e5ef0b970` and its complete diagnostics/PoC ancestry.
PRs #2/#3/#4 are closed as superseded. Cleanup run `37539650026` passed after verifying archive
ancestry, merged-tree equality, and exact branch-head leases. It deleted the two diagnostic heads,
PoC head, integration head, and temporary archive bridge atomically. The one-use workflow was
removed afterward. The remaining remote branches are `main`, `feat/epistemic-calibration`, and
`poc/theory-prior-axis` (intentionally retained unique theory design).

## Next use

Run [the ten-task matrix](model-testing-matrix.md) on real models. Expected difficulty is an
ordinal estimate; use fresh paired seeds and record harness failure separately. No real-model
calls were made here. Full results and limits are in [the integration report](solver-integration-results.md).
Reference PoC source/results remain available through immutable archive links in
[optimization evidence](solver-optimization-evidence.md). Local `../nexus` is a detached reference
snapshot; active development is in this checkout. Differential verification is resumable by
source/runner fingerprints. No implementation, merge, or cleanup steps remain open.
