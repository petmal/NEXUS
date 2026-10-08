# T3 and cumulative discovery: execution checkpoint

## System design

Goal: measure learning a missing bounded relationship and composing discoveries while keeping
complete public priors, ordinary actions, exact verification, and affordable per-task generation.
Current published baseline: ccef8e27457b9e52f6e2ddb2741e7910b474ff97, tree
841f7ce589503be012d88948f6e68a553e832e90. Work stays on feat/theory-prior-axis (PR 6).

T3 runtime will support D2/P0–P3/R0–R2 as a separate bounded world family. Each
shape/parity context independently chooses an add-one, add-two, or multiply-two
operation modulo 11. No baseline relationship is supplied. Unlike the earlier
additive-only research fixture this permits a change of operator, with a complete
finite structural prior. A calibration on another shape leaves nine reachable
behavior classes; a proven quotient avoids enumeration of irrelevant cells.
Qualification must reconstruct the public prior, validate the actual full law,
validate the calibration, prove reachable-class completeness, and replay exact
policies. The bounded family is not a claim of arbitrary scientific law discovery
or that T3 must be harder than T1/T2. Existing T0/T1/T2 worlds remain stable.

Progression PoC is separate from the production generator: supplied derivation →
unknown correction → missing relationship → prediction in an unmeasured context.
It must prove information dependency, compare independent/known-intermediate
controls, and detect bypass by a direct target measurement. Groundwork is limited
to the actual finite dependency representation/proof helpers used by this PoC;
no unused runtime flag, new D meaning, forced probe, or hidden control semantics.

The latest run shows R2 confounds map discovery with causal reasoning. The new
model matrix uses forgiving R0 and modest planning, with explicit stress controls.
No stable R semantics or MindTrial code changes are in scope. Clarifying drop/finish
semantics is allowed; player-visible diagnostics/solutions are not.

## Implementation phases and acceptance

1. Baseline: cold T1 seeds 1/17, source fingerprint and paired-world hashes. Inspect
   repeated mechanics/evidence work. Existing uv/pytest/CI commands are canonical;
   missing ruff/ty/basedpyright/coverage gates remain a separate tooling gap.
2. Optimization: remove repeated identical AST evaluations/serialization in evidence
   selection, retain deterministic tie-breaking/evidence choices. Compare cold
   baseline/candidate and public-world hashes, targeted oracle equivalence tests.
3. T3: structural prior + bounded generator + qualification + CLI/env/profile support,
   immutable new terminal schema, documentation and all-P/R replay/tamper tests.
   Compare projection with exhaustive full prior and replay representative witnesses
   under complete viable laws. Preserve existing runtime behavior and schemas.
4. Progression: finite PoC, causal dependency and counterfactual/ablation proofs,
   held-out prediction, replayable report; add only exercised reusable primitives.
5. Matrix and integration: approximately ten prequalified runs, expected qualitative
   difficulty, caveats and controls; full tests, CLI smoke, independent review,
   focused fixes, GitData feature-branch publication with exact-head lease.

## Decisions and resume

- Production remains sequential; T2 is already sub-second. Profile T1 filtering
  before introducing workers. Service-readiness overhead belongs to MindTrial.
- No paid model executions; user runs the supplied matrix.
- Commit each accepted phase with measured results. Reports are fingerprinted and
  atomically checkpointed so completed cases can be reused after interruption.
- Do not claim access to credit balances/reset schedules; checkpoints limit rework.
- Status: baseline/design phase started. Update this section at each checkpoint.
