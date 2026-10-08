# Physical search and theory expansion: execution checkpoint

Authorized 2026-10-08: implement recommended physical-search optimizations, qualify
D4/T1, execute a bounded-correction T2 PoC, measure independent physical-hypothesis
parallelism, and assess D5/T1 feasibility. Work continues on `feat/theory-prior-axis`
(remote base `6a614a78be00dc554b951d98adf24bd170a267da`, PR #6).

## Design contract

The goal is greater scientific-reasoning discrimination at P2 with affordable
single-episode generation. Preserve deterministic action semantics, exact optimal
costs, complete public-prior hypothesis coverage, seed pairing where claimed, and
active-play secrecy. Never discard a hypothesis because a solver limit was hit.
No MindTrial changes, GPU backend, undocumented prior widening, or production T2
flag before its proof gates. D5/T1 remains gated on representability and experiment
value: the current nested, value-sensitive D5 family is outside the T1 grammar.

Physical changes: cost-only hypothesis screening; topology reuse; bounded exact
physical-result reuse keyed by all transition/goal inputs and search bounds; then
measure route/transition allocation. Measure process parallelism only after the
sequential improvements, using standard-library process pools and explicit bounds.

T2 PoC: disclose an effective model, exact validity region, complete finite
correction family and invariants from one structured source. Exhaustively prove
agreement throughout the validity region, true-law membership, mission-relevant
uncertainty outside it, and ordinary-action replay of an exact policy. T2 need not
be a superset of T1: report the changed task family and avoid claiming paired
physical identity when it is not established.

## Phases and recovery

1. Record cold baseline on D3/P2/R1 seeds 1, 2, 17 at T0/T1; retain source and
   runtime fingerprint, physical hash, exact costs and every viable policy replay.
2. Optimize `solver/belief.py`; add correctness/boundary tests; repeat baseline
   cases plus D4/D5 and R2. Commit only improvements justified by evidence.
3. Extend T1 evidence and exact qualification to D4; sweep seeds and R profiles.
   Create T2 PoC script/tests and proof report, keeping unsupported profiles closed.
4. Measure bounded independent-hypothesis process execution vs sequential; keep
   it PoC-only unless repeatable whole-generation wins justify operational cost.
   Document D5/T1 gate and a roughly ten-run model matrix.
5. Run existing CI-equivalent tests, review invariants, publish focused commits
   against the verified remote head and update PR #6 without merging.

Evidence is stored under `docs/profiling/physical-pass-*` and accompanying theory
PoC files. Cold subprocesses and atomic per-case checkpoints allow interrupted
sweeps to resume. Never reuse measurements across changed source fingerprints.
No paid model runs are part of this work; the account allowance reset is not
observable here.

## Progress

- Planning complete; baseline running. Python 3.14.7 restored, frozen dependency
  environment used. Local snapshot ancestry differs from remote; publishing must
  use the remote base tree/parent and compare file blobs.
