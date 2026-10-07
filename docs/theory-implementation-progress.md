# T-axis implementation checkpoint

Integration base: remote `feat/epistemic-calibration` at `cd69107f02af30c10464b85b47fa343a3f96aaef`
(includes OCI revision label). Local worktree: `nexus-theory`, branch `feat/theory-prior-axis`.
Local snapshot commit IDs differ from remote; all base file contents were compared by Git blob SHA.
Publish using remote base tree and compare-and-swap branch updates; do not push local snapshot ancestry.

## Approved scope and invariants

Implement T0 compatibility and the bounded T1 structural prior; target D0–D3 first. T2 is a
separate gated PoC; T3+ and T1/D4–D5 remain unsupported without dedicated proofs. Do not change
MindTrial, retry/validation semantics, engine actions, map visibility, or T0 seeded worlds.
The structured public T1 prior must generate the same complete class used by evidence filtering
and exact policy qualification. Materialize only evidence survivors; never truncate the belief.

Decision: preserve the selected T0 scenario under T1, including topology, laws, goal and artifacts.
Reason: pairing plus unchanged historical T0 seeds preclude silently rerolling a rejected T1 seed.
Reject explicitly if bounded evidence search cannot certify the requested D; record acceptance
and supported seeds. Search failure is not proof that suitable evidence cannot exist.

## Phases and gates

1. OCI label: complete on integration branch; Docker/Podman unavailable locally, actual image
   label assertion added to the existing CI container gate.
2. Port compact prior and improve bounded evidence search. Prove 41,472 syntax forms / 27,120
   behaviors, all T0 rules included, representative/evaluator equivalence and sound CSV filtering.
3. Integrate T1 with metadata, public theory, CLI/service configuration, candidate reconstruction,
   qualification and terminal diagnostics. Qualify using full public prior; preserve T0 output.
4. Validate paired generation, D0–D3 probe guarantees, supported P/R combinations, every viable
   policy branch replay, tampered theory rejection, default T0 regression, and active secrecy.
5. Cold subprocess seed sweep with per-case atomic checkpoints and source fingerprint; document
   acceptance, runtime/RSS, limits and resume commands. Publish tested branch and reviewable PR.

## Current state

Implemented prior, bounded evidence planner, T1 generator/qualification, CLI/service option,
private metadata and terminal schema v4. The 22-seed T1 P2/R0 sweep passed 85/88 qualified
cases with 748 successful viable-hypothesis replays; D1 rejects 8/19, D3 rejects 73 explicitly.
Fast gate: 132 passed. Final cold dataset: 116 cases / 113 accepted / 865 replay paths,
19 matching T0/T1 physical-world pairs; all 16 P3/R2 cases passed. Extended/stress gate: 34 passed
in 216.75 seconds. All 166 collected tests pass. Full results are recorded in
`theory-implementation-results.md`. Do not claim all seeds are supported.

Independent review found a structural pairing risk. Fixed before the final sweep: T0 chooses
and qualifies the physical world/P3 cargo before T1 changes evidence/policy. No live mechanics
or MindTrial lifecycle semantics changed. Terminal diagnostics now use immutable v4 schema
commit `5feedd9b21a7160d29a5cfa4d7b9908014edd14d` (new theory dimension).
No model API calls. Use `uv sync --frozen --all-extras` and `.venv/bin/python` (Python 3.14.7);
the earlier integration venv pointed to an expired interpreter. Dependency locks unchanged. No credit-timer visibility;
completed experiment checkpoints are reusable only when inputs and source fingerprints match.


## Current remote checkpoints

- `cd69107`: OCI label on `feat/epistemic-calibration`.
- `5feedd9`: immutable terminal v4 schema on `feat/theory-prior-axis`.
- `28d814c`: T1 implementation and proof/integration tests, on `feat/theory-prior-axis`.
- Final docs/raw results recorded after all local gates. Review the T-axis PR against
  `feat/epistemic-calibration`; real-model calibration and container CI are the remaining validation steps.

Source files are frozen at fingerprint
`60f12c969e871cbe8cbd28a258cb536ba7dcbe8af5810353b5b8c088cc19b62a` for these measurements.
Resume the profiler using commands in the results document; completed matching cells are skipped.
