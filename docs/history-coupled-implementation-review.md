# History-coupled implementation review

2026-10-18. Read-only review of the actual new ontology modules, shared integration changes, independent oracle/tests, pilot matrix/preflight, and packaging/CI additions. No repository edits were made.

## Judgement

The implementation matches the narrowed experimental design. I found no hidden-state leak, transition error, counterfactual-commit confusion, incorrect goal predicate, or overlapping-winning-set error. Proceed after addressing the two small contract/fail-closed issues below and incorporating the actual-policy exhaustive check. The existing suite and final image checks remain the release gate; their in-progress status is not itself a review finding.

## Actionable findings

### Medium: configure remains advertised by the history JSON schema

`ontology/history/runtime.py:public_contract()` removes `configure` from the prose reference but obtains its schema from `action_contract(scientific=True)`. The schema's discriminator still includes `ConfigureAction`, contradicting the family contract that no apparatus accepts configuration.

Reproduced discriminator keys: configure, drop, finish, move, observe, operate, probe, take, wait.

Minimal fix: use the existing non-configure action-union schema for this family while preserving the scientific stock/operate/probe descriptions. Test both reference entries and schema discriminator mapping. Runtime rejection is already transactional; this is a public-contract clarity issue, not an unauthorized mutation.

### Medium: an early source-binding error can leave a stale passed preflight report

`evaluation/history.py:preflight()` obtains `source_binding()` before writing its initial running report and before entering its exception handler. If source reads fail, a previous passed report at the same output path survives untouched.

Reproduced by writing `{"status":"passed"}` to the output, patching `source_binding()` to raise `OSError`, and invoking preflight: the prior passed JSON remains.

Minimal fix: write a running/incomplete report before source inspection and include source inspection in the protected block, or wrap the whole invocation with blocked-output handling. Test this early-failure path explicitly. The existing cell failure and changed-source paths correctly fail closed once initialization succeeds.

### Proof gap: the analytical bound and live greedy policy consume different evidence

`policy.bound()` updates its hypothetical posterior only from the final reader outcome. `public_policy()` also incorporates each committed preparation pulse's visible x/y, and can then select a different greedy query. Extra evidence does not prove that a particular greedy policy's remaining cost decreases; the existing “conservatively ignored” comment alone is insufficient.

I independently simulated the actual policy over all 1024 worlds, incorporating every intermediate prefix observation:

- All worlds retain their true hypothesis and reach an accepted common preparation.
- Maximum conditional action cost is **30**, below the recorded conservative 31. This cost includes each survey anneal/preparation/readout and the final seal construction, but excludes taking the two specimens, movement, and finish.
- Maximum reader count is **5**, attained in four worlds: indices 81, 83, 913, 915.
- Therefore actual maximum total is 34 at P1, within the recorded P1 reference upper bound 35.

The current all-world test follows the final-reader-only policy. Extend it to cover the actual prefix-updating policy, retaining the current valid numerical upper bound. Scratch reproduction: `history-review/check_policy_actual.py`.

## Checks and evidence

Ran `.venv/bin/pytest -q tests/unit/test_history.py`: **13 passed in 5.79 seconds**.

Inspected and/or independently checked:

- Finite scalar equations, sequential use of new x/y, physical-coordinate clamps, table indexing, and all-word indexing.
- Compiled acceptance masks and world-winning bitsets represent exact complete histories; intersections preserve overlapping winning sets rather than incorrectly treating them as exclusive classes.
- Failed eligible finish excludes all worlds accepting the submitted history; wrong-room/missing-seal failures do not refute scientific hypotheses.
- Pulse probes reveal counterfactual history/x/y but do not modify the committed seal or tracker. Reader probes and reader operations preserve actual history/visible state; cached readouts remain separate.
- Every committed pulse and pulse probe is collected as evidence. Reader data adds its readout; actual visible values have already been emitted and processed by the corresponding preparation actions. Anneal's zero-state result is prior-known and adds no hidden-law evidence.
- Eight-pulse rejection occurs before mutation and action charging. Anneal is an ordinary charged recovery operation across resource profiles.
- Public specimen payload contains only public history, visible x/y, and optional reader result/channel. Latent H/K and generated gates/orientations remain private except in the intentional known-law control.
- Public mission success follows the actual carried `seal` history and exact physical target, not a counterfactual preview or configured program.
- Seed-independent immutable prior tables and bounded caches avoid per-session truth-specific cache leakage. Compilation is small enough that adding workers/GPU would not be justified.
- The diagnostic-budget registry capability preserves the existing admitted families and makes extension local. Repair's tracker deduplication is behaviorally identical to the removed class.
- Optional terminal trace logging is isolated to adapters that supply it, so legacy logging behavior is preserved. The new breakdown correctly warns that necessary construction pulses are not automatically wasted experiments.
- The matrix includes matched known/unknown and normal/generous controls, an orientation rival, varied gate laws, and a transfer regression sentinel.
- Dockerfile copies the new matrix and preflight script; `.dockerignore` explicitly admits the matrix; host and actual-image CI call the new preflight. The independent oracle runs on the CI host and is not needed by the image preflight.

## Scope cautions already addressed by the design

The new family remains a bounded parameterized dynamical-system investigation, with a disclosed graph and function grammar. It tests hidden-state reasoning, correlated inference, and executing a preparation; it does not establish that models must invent an unrestricted law form. The experimental/un-calibrated labels and failed deep-tier gate are appropriate.

The four-finish orientation-cover shortcut remains legal and is disclosed in the certificate. Do not reinterpret it as cheating or silently claim interventions are necessary for eventual escape. Likewise, the matrix's six-pulse case is physical depth, not a proof of six reasoning stages.

“Guaranteed repair” means a known fresh preparation. Anneal makes it executable from an altered carried seal at the array if sufficient actions remain. Terminal suffix/anneal fields are knowledge diagnostics; they are not a proof that the remaining action budget and current logistics permit recovery.

## Remaining release checks

Root is adding HTTP/preflight tests and will run the broader compatibility and actual-image gates. No request for additional optional tests beyond the specific public-schema, early-preflight-failure, and actual-policy proof checks above is made.

## Author disposition

All three actionable findings are resolved:

- The family now supplies the non-configure JSON action union while retaining
  scientific stock/operate/probe descriptions. A schema/reference parity test
  checks the actual discriminator mapping.
- Preflight replaces old output with `running` before reading source identity;
  initial source failures are caught and persisted as `blocked`. A regression
  starts from a stale `passed` file and injects a source-read failure.
- The all-world independent policy test now consumes every intermediate surface
  result before its final reader result, matching the live policy's decisions.
  The alternate tree bound is explicitly not justified by greedy monotonicity.

Final validation results are recorded in history-coupled-results.md.
