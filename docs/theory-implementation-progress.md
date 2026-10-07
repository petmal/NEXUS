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

Planning checkpoint committed before feature edits. Next: implement prior and evidence PoC.
No model API calls. Use existing Python 3.14 environment in `../nexus-integration/.venv` with
`PYTHONPATH=src`; avoid editing or regenerating dependency locks. No credit-timer visibility;
completed experiment checkpoints are reusable only when inputs and source fingerprints match.
