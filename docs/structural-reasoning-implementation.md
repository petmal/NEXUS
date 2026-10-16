# Structural reasoning implementation and resume ledger

Status: active. Baseline `09fe7bb`, `feat/theory-prior-axis`. Design authority:
[structural-reasoning-design.md](structural-reasoning-design.md). User request:
"Plan and implement the recommended changes."

## Phases and acceptance

| Phase | Work | Acceptance | State |
|---|---|---|---|
| 0 | Inspect branch, document design and methods, independent critical review | Source matches current feature head; invariants and scope recorded | in progress |
| 1 | Dynamics proof artifact, scoped timings, cost-aware public policy | Exact old episode contracts; all-world wins/replay; tamper/stale tests; cold benchmark | pending |
| 2 | Executable structural PoC and complete shortcut audit | Independently verified arithmetic/ambiguity/witness; failed candidates recorded | pending |
| 3 | Optional ontology and terminal metrics | Public protocol, privacy, schema, atomicity, replay, generated/loaded qualification | pending |
| 4 | Small pilot matrix and regression/package validation | Every cell wins/replays; current-source binding; old matrix remains valid | pending |
| 5 | Independent implementation judgement and publication | Valid findings fixed; feature-branch checkpoints; CI observed | pending |

## Concrete methods and expected areas

- Inspect `ontology/dynamics/{laws,inference,policy,generation,runtime}.py`,
  `evaluation/{difficulty,matrix}.py`, release packaging, and existing tests.
- Prototype proof reuse with a bounded data-only artifact and semantic identity;
  never pickle or execute cached data. Verify fresh-process loading and exact
  recomputation. Preserve the old resource/certificate contract.
- Model experiment preparation cost from public specimen histories and machine
  settings. Validate all posterior branches; account for travel/acquisition before
  using a more efficient policy as a reference.
- Prototype new scientific laws and audits outside the runtime first. Record
  negative tests as well as successful gates. Update the design before adding a
  code-registered family, data-only schema, public evidence, runtime adapter,
  inference, qualification and policy modules.
- Extend diagnostics only after terminal state; add generation stages only to
  operator logs. Maintain separate information, execution and receipt metrics.
- Preserve `docs/difficulty-model-matrix.json`; add a separate small experimental
  pilot with the existing controls and clearly scoped depth/coverage claims.
- Refresh the existing repair source binding through its qualification procedure
  after Python changes; never regenerate a bound manifest without its gates.

## Validation strategy

Use repository gates, not new repo-wide tooling churn:

1. Focused semantic tests for cache integrity, policy behavior and new law logic.
2. Exhaustive finite-domain crosschecks, public-policy victories and exact replay.
3. HTTP/CLI manifest/evidence/action/finish checks, save/load, privacy and failures.
4. Existing fast tests, slow tests, explicit property/stress partition and
   determinism test; preserve existing fixture behavior.
5. Focused Ruff/Pyright for changed/new Python modules, frozen lock, whitespace.
6. Installed-wheel/source-identity and preflight checks; actual Docker checks in CI
   if Docker is unavailable locally. Do not claim local container tests ran.
7. Fresh-context judgement of actual source/diff and proof artifacts, followed by
   triage and relevant revalidation.

No external model calls are part of these tests. Keep long commands asynchronous
and persist output under the analysis workspace. Commit useful checkpoints;
publication must verify the remote branch has not moved.

## Current checkpoint

- Local checkout clean and matches current PR6 head `09fe7bb`.
- Read `AGENTS.md`, existing matrix and dynamics implementation.
- Short Circuit workflow applied; fresh-context design reviewers are inspecting
  proof caching/reference planning and the structural PoC independently.
- Prior report: `NEXUS-run-13-22-12-analysis.md (previously delivered report; prior scratch copy expired)`.
- New temporary proofs/review outputs: `analysis/structural-next/` (workspace parent).
- No gameplay source changed yet. Next: finalize Phase 1 design, prove the new
  construction, update this ledger, then implement.

## Approved concrete construction and checkpoint

The independent enumeration in [structural-reasoning-proof.md](structural-reasoning-proof.md)
passes the query-level gate: 615 disclosed-solvable compositional worlds, 486
normalized queries, 81 overlapping repairs; a public witness needs at most seven
readings. Both contexts remain in the goal. Only 12 worlds have a complete
untrimmed-observation obstruction; target them separately from uniform sampling.
No mental revision, three-round, or model-failure guarantee is asserted.

Implement `compositional-repair-v1` as experimental T3/D5 and T0/D0, P0/P1 R1.
All experiment settings, including mission probes and internal trims, are legal
from the start. Seal acceptance checks the four residuals, not a canonical answer.
The public witness uses one reusable survey; 27 actions at P1 plus three recovery
actions gives a 30-action budget. Live conformance and full-world replay are gates.

Phase 1 now has an immutable 3,043-node dynamics reference artifact, bound to
semantic source and pinned digest; independent offline recurrence/tie-breaking
checker and safe exact fallback. Cold generation does not compile witness rows.
The reference reuses survey history prefixes and stage settings while preserving
query choices and the old episode budgets. Focused tests pass; exhaustive live
comparison/replay is running. No old family is removed.

## Implementation checkpoint — 2026-10-16

Phases 0–4 complete locally; independent final implementation judgement found no
unresolved blocker. The T0 posterior was corrected to match its disclosed
canonical valid-treatment sampler; edge regressions cover ineligible finish and
offset sensor operations. Versioned terminal metrics support overlapping goals.

- 640 tests pass in partitioned coverage (593 fast, 44 slow, 2 stress, 1 determinism).
- All 1,944 dynamics worlds win/replay and never exceed legacy actual reference
  actions. All 615 compositional worlds and 7,203 repair worlds win/replay.
- Old dynamics normalized episode contracts/budgets are unchanged. Repair's
  complete source binding was refreshed after proof, conformance and replay gates;
  mathematical proof and public witness remain identical.
- Eight new pilot cells and ten retained control cells pass current-source
  preflight. Installed-wheel source identity and cold cache/no-compilation pass.
- CLI, privacy/save-load, focused Ruff/Pyright, frozen lock and whitespace pass.
- Paired local cold generation median: 1.656s uncached versus 0.042s cached;
  imports excluded, shared host, no end-to-end harness speedup claim.
- Useful operator instructions: `docs/structural-model-matrix.md`; proof and
  conformance: `docs/structural-reasoning-proof.md` and
  `docs/compositional-live-conformance.md`; test record: `structural-validation.json`.

Resume: implementation is ready for feature-branch publication. After publishing,
observe CI (including Docker/OCI labels and both image preflights), fix any actual
failure, then update this ledger. No paid model calls or MindTrial changes are
required. The user should run the small pilot on the resulting image before a
broader evaluation. Keep `docs/difficulty-model-matrix.json` unchanged as controls.
