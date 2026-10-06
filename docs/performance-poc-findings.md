# Solver and T1 performance PoCs

Status: measurements in progress; see performance-poc-progress.md for the resumable checklist.
Base: diagnostics PR #2, `75d5bda`. Experimental code is opt-in; production CLI/service behavior
and supported difficulty profiles are unchanged. Do not merge as a production T-axis release.

## What was built

- Four solver modes: baseline, semantic-state interning, monotone budget bounds, combined.
  Interning keeps one normalized state object per semantic state and uses small IDs in memo
  and branch-cache keys. States are read-only after retention. Budget bounds retain strongest
  losing / weakest winning at-most-action facts for each state and belief.
- Fresh-process benchmark with atomic result files, source/lock fingerprint, full compiled
  episode hash, policy hashes excluding work counters, timings, work counts and peak RSS.
- T1 research prior from one structured specification. Compact six-cell branch signatures
  produce 41,472 syntax forms / 27,120 distinct behaviors without allocating 27,120 ASTs.
  Evidence filtering uses bitsets. Only survivors are materialized for the existing exact solver.
- D0/D1/D2 evidence gates and exact P2 policy/replay experiment, preserving the chosen T0
  family's laws, goal, topology and intrinsic artifacts. D3+ and production protocol integration
  are deliberately not implemented in this feasibility PoC.
- Independent-episode CPU batch experiment using standard-library ProcessPoolExecutor.

## Measurement discipline

The environment is recorded in profiling/poc-environment.json. This is shared managed hardware,
CPython 3.14.7, eight-CPU quota and 8 GiB memory; no GPU is exposed. Results are individual cold
measurements, not confidence intervals. Solver variants run sequentially. A separate worker-count
experiment measures batch throughput, not single-episode acceleration. Peak RSS is per child;
adding individual peaks is not a measurement of simultaneous aggregate peak memory.

An early pilot had inconsistent experimental cache reuse and is retained under
profiling/poc-solver-pilot for the audit trail only. A process interruption did not stop that
pilot immediately; some development work overlapped early seed-17 repeat measurements. Its
remaining outputs were quarantined by fingerprint. Use the corrected results and subsequent
isolated seed/batch measurements; do not treat a small timing difference as significant.

Correctness comparisons include full compiled episode identity, deterministic witness and
initial action-value outputs, exact optimum, exhausted bounds, and input mutation isolation.
The solver's visited count changes meaning in bounds mode (one interval per state/belief,
rather than one record per exact budget); it is a work/storage metric, not changed difficulty.

## Completed seed-17 solver ablation

| Profile | Baseline | Intern states | Budget bounds | Combined |
| --- | ---: | ---: | ---: | ---: |
| D5/P2 wall seconds | 17.60 | 12.61 | 14.96 | 9.88 |
| D5/P2 peak MiB | 528 | 116 | 516 | 115 |
| D5/P3 wall seconds | 157.04 | 109.29 | 142.38 | 99.12 |
| D5/P3 peak MiB | 4056 | 563 | 3906 | 544 |

All four modes produced identical full compiled episodes and policy hashes for each profile.
P3 interning retains 6,525 distinct semantic states despite 417,472 branch-cache entries.
Bounds reduce memo records from 180,409 exact-budget entries to about 41,794 intervals but
leave most transition work intact. This explains why interning drives memory savings while
budget bounds alone have modest benefit. Combined P3 is 1.58x as fast and uses 86.6% less
peak memory in this seed.

### Additional seeds, measured without other benchmark work

| Seed | Profile | Baseline seconds / MiB | Intern seconds / MiB | Combined seconds / MiB |
| --- | --- | ---: | ---: | ---: |
| 18 | D5/P2 | 14.75 / 528 | 10.28 / 116 | 9.94 / 115 |
| 19 | D5/P2 | 13.99 / 536 | 10.62 / 117 | 9.55 / 117 |
| 18 | D5/P3 | 178.96 / 4278 | 122.56 / 591 | 110.55 / 566 |
| 19 | D5/P3 | 170.60 / 4521 | 113.87 / 617 | 106.86 / 595 |

All 20 ablation cases completed; all six seed/profile groups had identical compiled episodes
and policy outputs across modes. Combined P3 generation is 37–38% faster with 86.6–86.8%
less peak memory across these three seeds. This is a meaningful improvement for fresh worlds,
especially where simultaneous 4-GiB services caused memory pressure; actual MindTrial startup
under contention has not been measured here. Generation still takes about 99–111 seconds.

Recommendation: promote state interning and monotone bounds together through a focused
production change after review. The PoC keeps both opt-in. Neither depends on reusing seeds.

## T1/P2 feasibility

The initial 20-seed sweep (0–19) accepted 20/20 D0, 18/20 D1 and 11/20 D2 cases. Every accepted
policy replayed against all viable hypotheses at its exact proved action budget. D0 retained one
behavior using four evidence rows; accepted D1 retained two with one mission prediction using
three rows; accepted D2 retained four evidence-consistent laws, of which three were physically
viable, using two rows. Rejected cases are retained rather than silently rerolled.

The important failure mode is semantic: a candidate set can have multiple mission predictions
yet admit a probe-free strategy after using the public goal and physical-solvability promise.
Nine D2 cases failed the actual minimum-probe check and were rejected. Two D1 cases failed
the non-direct evidence gate. These are failures of this bounded greedy evidence planner on
selected families, not proofs that T1/D1 or T1/D2 are impossible for those seeds.

The public research prior explicitly discloses the solvability promise used to eliminate
physically impossible hypotheses. Candidate counts before and after that filtering are separate.
The existing solver still knows the complete map and initial object locations; these results
do not establish an exploration-aware guarantee for the player's information state.

The sample uses the current T0-selected laws to preserve pairing. It is not a uniform sample
of true T1 laws, does not establish acceptance across all 27,120 behaviors, and has no LLM
capability results. A model could learn the narrower generating distribution over repeated
episodes. Production T1 needs a deliberate law-sampling policy as well as evidence selection.

## Parallelism

See parallelism-assessment.md. Process workers are suitable for independent fresh-seed episodes.
The shared recursive minimax is not cheaply parallelized by wrapping its branches in a library.
The pinned Pydantic core rejects subinterpreter imports. GPU execution would require a different
numeric search representation and exactness proofs; no GPU speedup is claimed.

## Resuming

Use performance-poc-progress.md. Completed case files are skipped only when their input and
code fingerprint match. Keep output directories distinct when comparing worker counts. Do not
edit measured code while a benchmark is running. A timeout/error is retained and retried on
the next invocation; incomplete temporary files are never treated as completed measurements.

The assistant cannot read credit balances or the allowance reset timer. These checkpoints let
work resume after a reset without repeating completed matching cases; they do not schedule or
control billing. No model API evaluations or repeated paid CI stress runs were launched.
