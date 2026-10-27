# Structural qualification and comparison release validation

Date: 2026-10-27. This release implements the recommended exact structural metrics,
bounded three-bank feasibility investigation and a matched Astra/Luna experiment.
No live model evaluations were run by the implementation process.

The original spill-ring proposal and two crossguard variants fail the16-block
admission gate on the fixed128kernel cohort. A self-guard revision admits five
block-qualified targets but none requires two whole-bank reopening operations.
No stronger runtime family is admitted. The unchanged v1 task matrix is retained
for the two-model comparison. This is an explicit failed admission result, not a
relaxed or silently substituted stronger-world claim.

See `../interference-comparison-guide.md` for semantics, the64attempt matrix,
control limitations, model selection, run commands and interpretation plan.
The machine-readable reports preserve full numerical evidence and source hashes.

## Validation status

- Full fast regression: **1,242 passed**, 51 slow/stress cases deselected, three
  pre-existing Pydantic warnings. Final structural/feasibility/readout checks:
  **46 passed**, with an additional explicit budget-exhaustion regression passing.
  Final planning/coordination/comparison launcher and package checks: **120 passed**.
  These checks overlap; their counts must not be added as independent tests.
- All32 comparison cells pass exact scalar optimum/restricted-path/regression
  proofs, public-reference execution, canonical replay, independent structural
  costs, source identity and recomputed export checks. All original public
  evidence hashes, terminal certificates and task-file bytes are unchanged.
- The complete four-variant feasibility run covers512 kernel/variant records
  over128 fixed kernels. Each transition table checks177,147 edges against a
  separate scalar interpreter. Two independent and four coupled grammar tables
  are checked per kernel:136,048,896 transition comparisons in total. General
  same-machine orbit BFS independently agrees with the augmented0/1 block search.
  All five first-gate targets independently have minimum bank reopening zero.
  The report records timings as local measurements, not complexity guarantees.
- Six real subprocess/HTTP/stateless-CLI service cases passed: core01/02/11/12
  and slack27/28. Each reaches a supported win, accepts the actual receipt and
  rejects a wrong one; separate forged-receipt negative controls also pass.
  These are real NEXUS service tests, not live MindTrial/provider evaluations.
- Historical repair proof and public witnesses are unchanged. The release's
  complete Python source map was refreshed after checking those immutable
  proofs/witnesses. Both historical live repair profiles still win in14/15
  actions and replay exactly.
- Changed Python files pass Ruff lint and formatting checks; distribution builds
  pass. A broader lint comparison finds the same172 existing findings at base
  8b991a1 and the current tree, with zero new findings. Formal whole-repository
  type/coverage gate migration is outside this feature; no production-readiness
  claim is inferred from test counts.
- A fresh design review independently reproduced the five self-guard candidates
  and optimal zero-reopening witnesses. A fresh implementation review found no
  blocking proof, runtime, disclosure or two-model-contract defect. Its release
  evidence finding was fixed: packaging rejects partial, stale or inconsistent
  proof reports. Its trajectory-test suggestions are covered by no-op,
  drop/retake, rejected-request and budget-exhaustion regressions.

## Container and release gate

The configured GitHub workflows build the exact feature commit, qualify legacy
and comparison matrices in the image, exercise all packaged launchers with
`--preflight-only`, and sweep all32 comparison rows through real service/receipt
checks. A representative original interference profile is also retained.
The final downloadable package is issued only after those remote checks pass;
workflow run URLs are reported with delivery. Local Docker/Podman is unavailable.

No live model run has been performed in this implementation. The64attempt
Astra/Luna comparison is the next user-run experiment, not a measured result.
