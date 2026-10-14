# Deep investigation implementation checkpoint

Approved design: [deep-investigation-design.md](deep-investigation-design.md),
including the 14 October robustness revision. Falsification cases are retained in
semantic tests. Historical checkpoints below are superseded by this completion.

**Completed on 14 October 2026.** The qualified opt-in repair family, common
presentation, complete public transcript, terminal diagnostics, proof checks,
performance improvements and ten-run model matrix are integrated. The local-regime
PoC was completed and withheld after its required-revision gate failed.
Validated source commit: `53bedc7d83737af2ecf272fc80a7628e402d6e73`.
[Results and limitations](repair-results.md) · [Validation](repair-validation.json) ·
[Real-model matrix](repair-model-matrix.md).

## Anchor and invariants

- Existing feature branch: `feat/theory-prior-axis`; PR #6; no main merge.
- Exact remote base: `4f394126ee6d5943b62f09ab0b1d7ec8f48ec0dc`.
- Source tree: `e4c610f8718ed1c62fbe0792dc7eccf7d9a5d945`.
- The previous inspection checkout had identical files but a different local
  history. It is now anchored to the hash-verified remote commit as a shallow
  boundary, preserving the remote parent; publication must be a leased fast-forward.
- Preserve old mechanics, seeds, private/public separation and historical replay.
- Common facility presentation applies to every current ontology; repair is opt-in.
- Strict deep registration requires an executable public three-round witness,
  two-round success upper bound at most 1/2 at the actual recovery-inclusive budget,
  genuine scientific dependencies, and complete interface conformance.
- Experimental, qualified and calibrated are distinct statuses. Unknown fails closed.
- No paid model calls, public MindTrial changes, force push or unapproved dependency.

## Phases

| Phase | Status | Gate |
|---|---|---|
| 0 Baseline | Passed: 507 tests, 3 existing warnings | Existing full suite; exact remote/tree anchor |
| 1 Proof contract | Passed | Tiny oracle, serialized rounds, independent upper checker, resource caps/checkpoints, shortcut mutations |
| Shared presentation | Passed | Versioned public rendering across families, historical compatibility |
| 2 Stateful construction | Passed | Qualified T3/D5/P0-or-P1/R1; scientific dependence and coupled physical repair |
| 3 Runtime integration | Passed | Complete factored live conformance; 7,203 truths won and replayed; bound release identity |
| 4 Local regime | PoC complete; release deferred | 50,421 pairs; early-trigger counterpolicy falsifies required revision |
| 5 Hardening/evaluation | Passed | 572-test passing coverage, 10 reference missions, six-process profile, independent final review |

## Handoff

Implementation is complete; next run the real-model pilot using the exact
[environment blocks](repair-model-matrix.json). Build from the final feature head
and record its OCI revision. Choose public settings before independently sampling
truth; preserve one non-resettable attempt, exact budgets and private seed/source
separation. Model failure rates are uncalibrated. A three-round agent may always win.

For revalidation, use the commands in [results](repair-results.md), then the full
suite with `NEXUS_STRESS_SEED_COUNT=3 uv run --no-sync pytest -q`. Final local coverage was
partitioned: 100 + 421 + 49 + 2 = 572, with three existing warnings. Historical
snapshot hashes remain unchanged. No paid model calls or main merge were made.

## Historical execution log

The entries below are chronological evidence, not outstanding instructions.

## Phase 1 evidence

- Added exact weighted finite-state policy search with fixed batches, final open-loop
  commitments, absorbing terminal halt, zero-cost closure and explicit unknown.
- Independent checker replays the witness and checks all bounded Bellman choices.
  Its trust boundary is the supplied finite transition table, not the live API.
- Fourteen retained tests pass. Independent fresh-context review compared 2,100
  tiny stateful cases against separate enumeration and rejected 145 false proofs.
- Fixed duplicate-successor timeout bypass, queue allocation before deduplication,
  and recursion exhaustion. Focused Ruff and Pyright passed.
- Remaining resource gate: process-isolated offline memory limits and atomic
  job checkpoints. No live qualification or deep-family registration yet.
- Construction falsification: the original binary route gives 3/4 two-round
  success, and one extra reading solves it. Shared-mask F4 gives 7/16 with three
  readings but a fourth reading gives full two-round success. These are compiled
  model results, not live-game or T3 guarantees.

## Shared presentation evidence

- New current generation selects `sealed-facility-v1`; historical episodes default
  to absent presentation and retain their exact original serialization.
- Public-only renderer covers manifest, evidence, observations, CLI, human observer
  and saved attachments across all six ontology paths. Scientific JSON is unchanged.
- Map function labels remain explicitly available to public reference policies;
  changing display labels must not remove public room-role information.
- 42 existing compatibility/CLI/service tests and 18 presentation/ontology tests
  passed. Paired old/new presentation traces, final states and receipts match.

## Public boundary evidence

- Complete application projections now cover HTTP (including framework 500/422),
  JSONL, and typed Session calls alongside the unchanged action replay trace.
- Eight focused semantic tests pass. Fresh-context review found and closed four
  projection/delivery issues; 12 concurrent sessions retained isolated effects.
- Storage is bounded and incomplete coverage is explicit. Network timing and
  pre-ASGI transport errors are outside this documented boundary.

## Stateful construction checkpoint

- Pure laws/schema (not yet registered) cover 7,203 F7 worlds with a missing
  z/z²/z³ relation, shared calibration mask, and coupled four-channel key repair.
- Four exhaustive primitive tests pass: public three-round inference, target
  bijection, off-context responses, material insensitivity and reversible repair.
- Independent exact query abstraction: 19/49 shallow success; granting structure
  free gives a conservative 3/7 upper bound. Bounded-cache runs take ~2 s / 66 MiB
  for the relaxation and ~12 s / 423 MiB for the full query model.
- Still required: complete live cost/observation conformance, actual sampling
  contract, offline proof payload/checkpoint, runtime registration and final gates.
- A one-action budget increase permits guaranteed two-round success; no resource
  envelope may conceal this cliff.

## Execution interruption checkpoint — 14 October 2026

**The final plan is not complete. Do not enable the strict family yet.** The shell
execution service disconnected while final live qualification was in progress;
even `pwd` and a small file edit stopped returning. GitHub remained available, so
this checkpoint was published separately. No source was promoted on the strength
of an incomplete gate.

### Published, verified checkpoints

The five implementation commits through
`dc8f4fe5fcded7700e354fe0e261684f5f0d877a` contain the approved plan, exact finite
policy/checker core, common presentation, complete public transcript support,
and pure repair schema/laws/tests. Baseline: **507 passed**, three existing
warnings. Focused checks and independent reviews are recorded above.

### Additional work saved in the working directory, not yet published

Repository: `/workspace/scratch/5185b9a844b2/nexus-theory`.
Preserve the dirty worktree before updating it from this newer documentation
commit. The latest local source HEAD was the published SHA above.

- New repair modules: `evidence.py`, `generation.py`, `inference.py`,
  `policy.py`, `proof.py`, `qualification.py`, `runtime.py`,
  and `query-upper-proof.json`.
- Shared integration: `ontology/mission.py`, runtime-only catalog and payload
  registration, mission metrics based on applied key state, and the optional
  single-session HTTP restriction. The general generator remains disabled.
- Offline scripts: `prove_repair_queries.py`, `qualify_repair_offline.py`;
  construction proof/result documents; runtime and qualification tests.
- Constant-space seed decoder; whole-goal equality, seed/truth agreement and
  canonical resource/metadata checks. These close independently found
  qualification bypasses.
- The reference investigator was replaced by a serialized fixed-batch Program
  tree and interpreter. It makes scientific choices at three explicit feedback
  boundaries. Only expected-turn and opaque specimen-handle substitutions occur
  inside a batch. Serialization and declared round/action ceilings are checked.
- The offline query runner now rejects any requested round limit other than
  two, rather than silently reporting the two-round answer under another label.

### Confirmed results and their exact scope

- Independent abstract proof review: complete 576-choice upper payload regenerated
  and separately checked; **3/7** upper bound when the structural degree is
  supplied free. Full hidden-degree query model: **19/49**. Forged payload
  mutations were rejected. This is not yet a complete live-interface certificate.
- Offline isolated proof job: exact and independently checked, **9.106 s**,
  **82,252 KiB** peak RSS on Linux, with a 512 MiB cap. The independent full model
  rerun used **10.438 s / 440,852 KiB**. Jobs checkpoint atomically, but incomplete
  search cells restart; there is no serialized recursive frontier.
- Before the serialized-interpreter revision, all **7,203 truths** won through
  the actual Session engine at P1 in 15 actions, emitted actual receipts and
  replayed exactly (**72.39 s**). This exhaustive run must be repeated for the
  final serialized witness.
- **91 existing network/ontology/causal tests** passed with the new mission seam.
- After the serialized-policy and qualification fixes, **14 focused live tests**
  passed; the exhaustive test was deliberately excluded from that quick run.
- Latest focused Ruff and Pyright passed (run through cached `uvx --offline`;
  they are not dependencies of the repository environment).
- Earlier proof/construction checks: **7 passed**. Final full-suite regression,
  live conformance qualification, performance report and real-model matrix remain
  unfinished. Do not describe the intermediate results as the final test run.

### Review findings and remaining obligations

Review reports in `/workspace/scratch/5185b9a844b2/analysis/`:
`repair-live-judgement.md`, `repair-proof-judgement.md`,
`finite-policy-judgement.md`, `public-boundary-judgement.md`.

The live reviewer found no cheaper distinct contextual reading, cheaper distinct
key attempt, active-state hidden hint, recovery error, or mission-tracker
regression in the generated single-session mechanics. However:

1. Prove and test complete public-state/response factorization for every reachable
   action class; witness trajectories alone do not prove conformance. Include
   errors, free observations, cached replies, event hashes, previews, arbitrary
   legal vectors, multiple specimens, terminal/finalize behavior and transports.
2. Finish exact public-template validation, including complete room objects, not
   just labels. Verify the new whole-goal, seed and metadata rejection tests.
3. Scope qualification to **one non-resettable attempt**, no private-process
   access, uniform truth indices 0..7202, exact P0/P1 R1 budgets, and application
   responses rather than timing side channels. Test the multi-session rejection.
4. Re-run all 7,203 worlds through the serialized public witness; add false-program
   tests and the dropped-key/ineligible-finish/retake telemetry regression.
5. Bind checked proof and witness artifacts to the actual semantic implementation
   before cheap per-episode qualification. Digests establish identity, not proof.
   Missing/changed/unknown qualification must fail closed.
6. Complete the global action charging argument: each distinct B/C costs at least
   four across the whole history, each new tested dose at least three. Querying
   paths pay key + survey acquisition and required travel. Pure-guess paths can
   omit the survey, but still afford only five attempts. Do not subtract survey
   acquisition from every policy without this separate case.
7. Clarify deferred-guess normal form for counterfactual all-fail histories that
   become unreachable: truncate at the funded budget and commit the reserved
   guesses; those guesses already cover the otherwise missing successful paths.
8. Only after this gate may catalog generation be enabled for T3/D5/P0-or-P1/R1.
   Strict budgets are 17/18 actions, including one failed complete repair.
   One extra action allows a guaranteed shallow strategy; reject overrides and
   publish this cliff. This is not an empirical model-failure guarantee.
9. Attempt the bounded local-regime variant and paired stationary control. Ship
   it only if it adds real revision and passes its scope. Otherwise record its
   counterexample and defer as explicitly permitted by Phase 4.
10. Finish cold/warm generation profiling, terminal telemetry, evaluation matrix,
    final compatibility suite, documentation, focused commits and leased
    publication. Do not merge main or alter MindTrial behavior.

### Immediate resume commands

```sh
git status --short
uv sync --frozen --all-extras
uv run pytest -q tests/unit/test_repair_runtime.py --maxfail=1
uv run pytest -q tests/unit/test_repair_qualification.py tests/unit/test_repair_construction.py
uv run python scripts/qualify_repair_offline.py --output /tmp/repair-proof.json --max-seconds 120 --memory-mib 512
```

Then complete the interface/qualification obligations above. Final full regression:
`NEXUS_STRESS_SEED_COUNT=3 uv run pytest -q --maxfail=1 --durations=12`.

No paid model requests were made. No account credit/reset state was assumed.

## Resumed integration checkpoint — 14 October 2026

Execution recovered; unpublished work was preserved. Serialized public-policy
execution/replay passed all 7,203 truths (15 tests, 184.11 s). Component conformance and
independent query proof passed. Fresh review found no remaining live-proof blocker
under the explicit conditional-prior/single-attempt scope. Registration is now
opt-in and guarded by source/proof/witness identity; compiled episodes also bind
the semantic release. HTTP play, save/load, human help and packaged proof assets
pass. The final full regression is running; do not mistake earlier baseline counts
for its result. A legacy integration assertion was updated for the approved
versioned presentation while checking that exact mission text is retained.

Local regime: 50,421 paired cases checked; early treatment reduces it to a stationary
problem. Its required-revision gate fails, so it is deferred as permitted by Phase 4.
The ten-cell matrix and six-process timing pilot are implemented. Final tasks:
finish full regression, publish results/matrix and update the PR.


## Completion — 14 October 2026

- Final serialized public-policy replay: all 7,203 truths.
- 572 collected tests covered by passing groups; presentation regressions fixed
  without replacing historical fixture hashes. Three-seed legacy stress passed.
- CLI qualification/replay and the built wheel's 109 source/proof hashes verified.
- Independent upper proof/check: exact 3/7, 16.15 s, 79.2 MiB under a 512 MiB cap.
- Ten matrix reference missions won. Six fresh processes: 24/24 public-policy wins;
  cold generation 0.110–0.163 s, warm 0.00064–0.00124 s, about 61 MiB peak RSS.
- Focused Ruff, new-module Pyright and whitespace checks passed.
- Local-regime revision is deferred; no unqualified variant is exposed.
- No remaining implementation gate. Publication/CI is tracked on PR #6; the next
  scientific decision depends on the model pilot, not additional proof claims.

## Packaging follow-up — 14 October 2026

The Windows-built pilot image rejected all 42 repair startups. CRLF-only conversion
reproduced the stale qualification error. The focused correction enforces LF via
Git attributes and build-copy preparation, retains strict installed-package
verification, and adds bounded mismatch diagnostics plus an image-level P0/P1
victory/replay preflight. It does not change scientific mechanics or budgets.

41 focused tests passed; the independent bound checker and both public profiles
pass. A wheel built from a simulated CRLF checkout matches all 109 source hashes
and proof assets, and both profiles win/replay from the wheel in a fresh process.
Substantive edits still fail qualification. Ruff/Pyright/whitespace checks pass.
Rebuild the image, run its preflight, then repeat pilot cells 05–10. Do not interpret
the 42 startup failures as model reasoning failures or repair difficulty evidence.
