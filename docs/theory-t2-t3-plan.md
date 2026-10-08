# T2 integration and T3 feasibility checkpoint

Authorized 2026-10-08: integrate T2, build a T3 PoC, and improve operator timing.
Continue `feat/theory-prior-axis`, PR #6, remote parent
`ae3785574649f49b10f4dd8c303f91148c25e178`. Do not modify main or MindTrial.

## System design

Goal: measure recognition of theory limits and empirical law construction without
requiring expensive D5/P3 generation. Existing action semantics, exact receipts,
complete public priors and T0/T1 generated-world identity remain invariants.

T2 initially supports **D2/P0-P3/R0-R2**. Its separate, versioned family promotes
the nine-law correction PoC: an additive effective model is exact at phases 0/2;
phases 1/3 independently add a correction from {0,1,2}. A mission requires a
correction of 1, leaving five physically viable laws and one required guaranteed
probe. Do not claim physical seed pairing with T0/T1. P3 retains the established
delivery-dependency proof. Unsupported D/T combinations reject explicitly.
The public JSON and prose come from one validated prior. Qualification reconstructs
the entire family from that public prior, verifies calibration, membership,
mission uncertainty, effective-model insufficiency, and the usual exact policy.

T3 remains research-only: independent shape × phase-parity cells choose one of
three bounded additive effects. No shared conditional formula is disclosed.
Represent uncertainty as per-cell domains. Project to reachable cells only when
an invariant proves the others cannot affect any legal future observation/action;
report full-family cardinality and multiplicities. Compare this exact quotient
against all complete laws on the bounded fixture; never call a sampled subset
the complete prior. Use ordinary engine replay and fail closed on limits.

Timing remains opt-in stderr/operator logging. Add generation-wide wall/CPU totals
and an end summary with qualified nested stage names, counts and summed times.
The final summary must survive short log tails, retain repeated stages, and report
failure without exception text/private seed/rules/receipts. Add pre-solver family,
catalogue and evidence timings; no player-protocol or terminal-score changes.

## Implementation sequence and acceptance

1. Promote correction prior/building to package modules; add T2 dispatch and reuse
   existing qualification, P3/R transformations, CLI/environment and telemetry.
   Test public-prior tampering, unsupported combinations, deterministic generation,
   effective-theory limits and exact all-hypothesis policy replay.
2. Add hierarchical timing collector plus cold-start substage measurements. Test
   nested/repeated/error summaries, secrecy and unchanged generated episodes.
3. Build bounded T3 factorization PoC and deterministic exhaustive checks. Emit
   fingerprinted per-seed checkpoints, comparison counts/costs and limits.
4. Run targeted tests, T2 seed/profile sweep, T3 exhaustive oracle, full existing
   suite with three stress seeds, CLI qualification/solve/replay and diff checks.
   Obtain fresh review of public-prior completeness and qualification invariants.
5. Publish focused commits from verified remote parent/tree; update PR #6 and
   docs with support matrix, measurements and a small real-model test matrix.

## Resuming

Read this file, git status, and `docs/theory-t2-t3-results.md` when present.
Local snapshot ancestry differs from remote; publish using remote Git tree/parent,
not an ordinary push of local ancestry. Check remote head before updating it.
Raw sweeps belong under `docs/profiling/t2-integration` and `t3-structural-poc`.
Resume only matching source/runtime fingerprints. No paid model calls; account
allowance/reset status is not observable. Existing lint config is limited to Ruff
settings, with no installed lint/type gate; do not turn this feature into a
toolchain migration. Report that pre-existing gap.

Progress: remote head verified; working tree clean; design recorded before edits.

- T2 runtime checkpoint published: `86e6bb6ee4bb7fdc8b9801ad704cc5340e5139b0`
  (local `67ec3ae`, tree `5d7b4ec27c50e37cf807f4a313f1368e9a7c7325`).
  Immutable v5 schema parent: `c24f44f510df32453c6e2860ef86640ab3ac6f8e`.
- T2 focused profiles/tampering and all-law replay tests pass; T0/T1 regression
  checks pass. CLI P3/R2 generate/qualify/solve/replay passed. T3 five-seed oracle
  sweep passes (675 complete viable-law replays). Independent review found no
  blockers; full suite and final-source profiling records are being completed.
- Runtime source frozen at checkpoint above; remaining work is T3 script/tests,
  docs/raw validation and final publication. Earlier raw fingerprints may predate
  import-order cleanup; regenerate them with current source before finalizing.

- Final gates passed: 206-test full suite (445.05 s, three stress seeds), plus
  eight targeted checks covering the newly added unsupported-T3 case (207 current
  tests covered). T2 final-source sweep: 21/21, 105 policy replays. Model matrix:
  10/10, 123 replays. T3 isolated final-source sweep: five cases, 675 complete-law
  policy replays, 53,460 reachable-domain comparisons. See results and validation
  JSON for measurements and known limits. T3/docs checkpoint is ready for publication. Verify its remote tree and PR
  status after publishing; no main merge is authorized by this task.
