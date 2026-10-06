# Solver and T1 performance PoCs

Status: bounded PoCs and measurements complete; see performance-poc-progress.md for commands.
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

The final 20-seed sweep (0–19) accepted 20/20 D0, 18/20 D1 and 11/20 D2 cases. Every accepted
policy replayed against all viable hypotheses at its exact proved action budget. D0 retained one
behavior using four evidence rows; accepted D1 retained two with one mission prediction using
three rows; accepted D2 retained four evidence-consistent laws, of which three were physically
viable, using two rows. Rejected cases are retained rather than silently rerolled.

| T1/P2 profile | Accepted / attempted | Median accepted case seconds | Median exact policy seconds |
| --- | ---: | ---: | ---: |
| D0 | 20 / 20 | 0.746 | 0.0134 |
| D1 | 18 / 20 | 0.766 | 0.0174 |
| D2 | 11 / 20 | 0.777 | 0.0417 |

Case time includes universe/evidence construction, T0 paired-world generation, T1 solve and
replay, but excludes interpreter startup. Peak RSS was about 60–61 MiB. All 49 accepted T1
cases had the same exact guaranteed action cost as their paired T0 case. Thus this sample
supports changing the supplied theory without adding physical action cost; it does not show
whether models find the T1 version harder. Across these cases, 89 viable-hypothesis paths
replayed successfully. State-limit exhaustion is an error, never a proof of physical impossibility.

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

| Same two cold D5/P3 episodes, combined mode | One worker | Two workers |
| --- | ---: | ---: |
| End-to-end batch seconds | 215.54 | 125.42 |
| Seed 17 generation seconds | 99.87 | 110.70 |
| Seed 18 generation seconds | 110.32 | 122.58 |
| Seed 17 child peak MiB | 544.16 | 544.21 |
| Seed 18 child peak MiB | 566.12 | 565.79 |

The two-worker batch has 1.72x throughput (41.8% less elapsed batch time), with identical
episode/policy hashes across worker counts. Individual episodes were about 11% slower under
concurrency. Use this for preparation throughput, not as a single-search latency optimization.
Per-child memory stayed stable; aggregate peak memory was not measured. No new dependency
was needed. The serial repetition also reproduced the earlier combined timings closely.

## Recommended next decisions

1. Promote the combined solver optimization through normal production review and broader
   stress coverage. It preserves exact semantics in the measured cases and removes most of
   the per-episode memory cost. Keep a baseline path for future differential tests.
2. For fresh-seed preparation batches, start with two process workers and an explicit memory
   budget. Sample seeds at run preparation time, compile once per task, then share the same
   compiled task across models. Different R seeds remain supported; cross-world cache hits
   are not assumed by these optimizations.
3. Continue T1 at P2 as a bounded integration project. Improve/review evidence selection and
   law-sampling bias before treating D1/D2 rejection rates as production-ready. Recompute
   budgets from T1 policies; do not serve the research copy with stale T0 metadata/qualification.
4. Run paired model evaluations only after that integration. Generator feasibility does not
   prove better discrimination between models. Retain a small P3 stress track for dependency
   coordination, which T1 tests do not replace.
5. Defer a GPU backend and fine-grained recursive parallelism. They require substantial
   representation/search work, whereas the measured compact-state and batch changes already
   provide useful gains without changing the engine or adding a distributed framework.

## Resuming

Use performance-poc-progress.md. Completed case files are skipped only when their input and
code fingerprint match. Keep output directories distinct when comparing worker counts. Do not
edit measured code while a benchmark is running. A timeout/error is retained and retried on
the next invocation; incomplete temporary files are never treated as completed measurements.
`batch.json` describes the latest invocation; a resume with skipped cases is not a fresh full
batch throughput measurement. Use a new output directory for timing repetitions and preserve
the original batch report. Per-case completed results remain intact when skipped.

The assistant cannot read credit balances or the allowance reset timer. These checkpoints let
work resume after a reset without repeating completed matching cases; they do not schedule or
control billing. No model API evaluations or repeated paid CI stress runs were launched.

## Verification

- 102 fast unit/integration tests passed in 50.28 seconds; 32 slow/stress tests deselected.
  The two Pydantic enum-serialization fixture warnings already existed on the diagnostic base.
- 20 solver ablation cases, six semantic comparison groups, all exact outputs matched.
- Two serial and two parallel cold cases, with cross-worker episode/policy equality verified.
- T1 compositional exhaustive branch/condition checks across the full domain, all 288 T0
  members, an independent ordinary-action minimax fixture, and 60 generation/evidence cases.
- Timeout/retry/resume smoke: timed-out case reran successfully, then matching success was
  skipped with zero new generation work. No changes to runtime code during final measurements.
- Full release stress and LLM capability evaluation are follow-on work, not claimed here.


## Single-episode follow-up

The additional [single-episode PoC](single-episode-poc-findings.md) finds a further
3.66–3.87x cold-generation speedup over the combined solver by reusing transitions,
routes, and choices, with direct expected-cost certification. Tested intra-episode
process splits were slower than the best sequential approach. This extends the original
results above; it does not change production defaults.
