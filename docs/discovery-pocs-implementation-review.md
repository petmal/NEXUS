# Discovery PoCs: fresh-context implementation judgement

Date: 2026-10-20. Read-only review of the working tree at `/workspace/scratch/5185b9a844b2/NEXUS`. The reviewer changed no repository files. The implementation owner made fixes concurrently after receiving findings.

## Decision

No unresolved substantive runtime-correctness or privacy blocker found in the reviewed scope. The two experimental families implement the approved finite mechanisms and honestly retain their short observation policies. This judgement supports proceeding with the remaining release/package/CI gates and the bounded pilot; it does not establish a deep tier, model failure, or completed real-model executions.

Two actionable defects were found and accepted by the owner. Both are now corrected in the working tree; the T0 correction was independently exercised. One focused regression gap is noted below, with the underlying behavior independently verified as correct.

## Findings

### Medium: uncertainty T0 omitted the promised construction, weakening its execution-control meaning — corrected

Evidence: `docs/discovery-pocs-plan.md` decision 6 requires T0/D0 to disclose a correct law and construction. Initially, `uncertainty/evidence.py` supplied only resolved `Physics`, while representation T0 supplied a program already equal to assembler settings. An independent generation of matrix row 06 (seed 123841) exposed checks `[7,25]`, syndrome `[0,0]`, pattern `1`, but omitted the working assembler vector `[9,0,1]`. Deriving that vector still required translating the parity relation into a predictor. This was a real asymmetry in the intended controls, even though no measurements were necessary.

The owner added `resolved_construction` to both families' public theory evidence only for T0 and changed `discovery/policy.py` to execute it directly. It is null for T2/T3. Independent verification after the fix: both new `test_t0_discloses_a_literal_working_construction_without_inference` cases passed (2 passed, 38 deselected); both matrix T0 seeds also completed the corrected public policy in exactly four actions with zero measurements and a valid receipt. This finding is closed subject to the owner's final source-bound gates.

### Low: preflight elapsed time used a loop index instead of its start timestamp — corrected

Evidence: `evaluation/discovery.py::preflight` initially assigned `start = perf_counter()` and later reused `start` in `for start in (0, 5)`. Its final `seconds=perf_counter()-start` therefore measured clock uptime minus five, not preflight duration. An existing `/tmp/discovery-preflight.json` reported 1877.414 seconds despite the bounded test/proof timings. This could mislead performance comparisons and the CLI result.

The owner renamed the loop variable to `group_start` and added a deterministic fake-clock assertion to the full-matrix test (`seconds == 21`). The reviewer inspected the corrected code and regression; the owner owns rerunning the full matrix after concurrent edits.

### Low regression gap: uncertainty finish-information test used an already impossible build

Evidence: `tests/unit/test_discovery_pocs.py::test_finish_information_requires_carried_actual_build_and_recovery_is_supported` and `evaluation/discovery.py::recovery_check` initially chose the first build failing the actual world. For uncertainty, this is the constant/empty-mask build, which is accepted by zero public-prior mechanisms. Consequently, the test's eligible-finish exclusion assertion could pass without excluding any worlds. It did not protect the informative rejected-finish path.

The implementation itself behaves correctly. An independent live trace at seed 123841 installed `[3,0,0]`, accepted by 6 of the initial 120 mechanisms but false in this world. The first eligible rejection left 114 mechanisms; the repeated rejection left 114; the two pre-outcome submission classifications were `compatible` then `contradicted`. Recommendation already sent to owner: use a wrong build with positive public-prior acceptance mass and assert a strict first reduction plus idempotent repeat. This is a narrow regression improvement, not an observed runtime bug.

## Substantive checks

- **Complete behavioral acceptance:** representation finish uses product-automaton equivalence over reachable paired states, not a finite sample fit. The offline proof independently refines all 768 programs × 27 states and checks that the length-six reader signatures equal the complete initial-behavior classes. The 138 classes retain all syntactic prior multiplicities. Equivalent alternate programs are accepted.
- **Finite robust acceptance:** uncertainty checks every support point and both operational nuisance values, and allows wrong loading choices only when unused channels make them irrelevant. The dual-space oracle provides a separate acceptance characterization.
- **Factored posterior:** the 120-mechanism posterior and `(8-k)!` schedule multiplicity are sound for the actual allowed channels: fully joint indexed fixtures, calibration, and order-free moments. Full observations are injective within a mechanism; repeated IDs cannot gain schedule evidence; partial-channel queries are absent. Rejected builds remove mechanism acceptance sets and preserve the uniform remaining-schedule factor.
- **Finish and persistence:** tracker eligibility follows the carried actual carrier and committed build. Probe previews do not install; reader observations do not test a build; copies cannot replace the mission artifact. Independently exercised repeated rejections and action-budget exhaustion in both families, plus uncertainty calibration/summary canonicalization and repeated/joint fixture reads. These traces completed and produced consistent diagnostics.
- **Privacy and controls:** the stable apparatus grammar and exact acceptance conditions are public. Selected T3 structure/assignment remain private; observations contain readings and committed public state, without posterior or qualification hints during active play. Single-session HTTP integration retains the existing no-reset boundary; terminal diagnostics classify evidence before incorporating success.
- **Matrix and proof scope:** matched T0/T2/T3/R0 worlds, behavioral/skeleton contrasts, uncertainty rowspace contrast, exact selected certificates, common budgets, recoverability, replay, and stale-report rejection are checked. Reported certificate counts are explicitly actual-outcome oracle certificates rather than policy/cognitive lower bounds. Six-reading representation and five-reading uncertainty upper bounds remain visible. No source or proof paths are weakened to bypass the legacy release gate.
- **Modularity/performance:** grammar, read semantics, and acceptance stay in family-specific laws; common construction/runtime/diagnostic mechanics are shared across the two concrete users. Finite lookup tables and bounded caches are modest. Runtime generation does not execute the offline proofs. CI/Docker additions include the matrix and installed preflight; no local Docker execution was claimed or performed.

## Limits

This was a bounded implementation judgement, not a full regression rerun. Reviewed the relevant plans, design judgement, actual new source files, registry/CI/Docker diffs, tests, matrix, and MindTrial examples. The parent's reported 45-test run and proof/matrix runs were supporting context, not independently re-executed wholesale. No real-model run or image build was performed. Documentation checkpoints and the legacy source-bound manifest were being updated by the owner; their transient state was deliberately not treated as a feature defect.

## Owner triage

All three findings accepted and addressed. The informative-rejection regression now
selects a wrong build with positive public-prior acceptance, asserts strict posterior
reduction, repeats the rejection and checks unchanged posterior plus contradicted
classification. Four focused finish/T0 tests passed after these changes. The final
source-bound preflight reports 4.371 seconds, and the fake-clock regression protects
the corrected duration. Full regression and installed-package results are tracked in
`discovery-pocs-implementation.md`. No finding was deferred or rejected.
