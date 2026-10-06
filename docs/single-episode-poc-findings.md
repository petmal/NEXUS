# Single-episode generation optimization PoC

Completed 2026-10-06. This extends the existing solver PoC; production defaults remain unchanged.

## Result

Transition reuse is the high-value improvement. Direct certification adds a smaller gain. The tested process-based proof splits do not improve single-episode latency over the best sequential variant. These are fresh-seed, within-solve caches; they do not require repeated seeds or precompiled episodes.

All comparisons below use the previous combined interning/budget-bounds optimization as their starting point, not the original production baseline.

## Matched-source cold measurements

Each cell is full process wall time in seconds, including imports, generation, exact qualification, worker startup/shutdown where applicable, and interpreter exit. One episode runs at a time.

| Seed | Combined control | + transition reuse | + reuse and certificate | + reuse and parallel certificate |
| --- | ---: | ---: | ---: | ---: |
| 17 | 110.79 | 30.39 | 28.70 | 40.06 |
| 18 | 119.59 | 32.52 | 30.88 | 38.29 |
| 19 | 114.58 | 34.41 | 31.28 | 40.10 |

The best sequential variant is **3.66–3.87× faster**, or **72.7–74.2% less latency**, across these three seeds.

| Variant | Median wall s | Median accounted CPU s | Median sampled aggregate RSS MiB |
| --- | ---: | ---: | ---: |
| ordinary | 114.58 | 114.53 | 565.75 |
| reuse | 32.52 | 32.49 | 502.85 |
| reuse-certificate | 30.88 | 30.85 | 499.54 |
| reuse-parallel | 40.06 | 53.47 | 748.47 |

Seed 17 repeat reverses the order of the control and best sequential variant: 28.76 s optimized, then 109.32 s control. This is a repeatability check, not a confidence interval.

## What changed

1. Cache macro choices by normalized physical state. The legal choice list is independent of the belief set.
2. Cache movement results by normalized state and route. Movement does not consult hidden laws.
3. Cache probe/operate results by normalized state, route, action, and hypothesis; cache other actions without a hypothesis discriminator because their semantics are law-independent. Regroup outcomes for each belief set exactly as before.
4. Reuse the current solver-owned state for empty routes. The engine still copies before modifying a state.
5. For planning extension, directly certify the already-required expected cost K: winning within K, and not winning within K-1. A failed certificate falls back to ordinary optimization; no candidate acceptance rule is relaxed.

All reuse tables are local to a single solve. There is no shared mutable process cache and no seed-dependent precompilation.

## Why parallelism did not help here

The parent proves the K bound and retains its memo for deterministic witness/action-value construction. A spawned worker independently decides K-1. The root variant splits that negative decision into two deterministic first-action partitions while the parent works, using three search processes in total.

The winning and losing proofs overlap. Independent processes rebuild overlapping transitions and lose cross-proof memo reuse. Subsequent action-value checks in the parent also lack facts computed only by workers. The additional CPU work exceeds the latency benefit in these experiments.

The standard-library `ProcessPoolExecutor` uses explicit `spawn`; no new parallel framework dependency is needed. Fine-grained shared-dictionary IPC and GPU kernels were not implemented. These results reject the tested splits, not every possible parallel search algorithm.

## Pilot evidence and attribution

Exploratory seed-17 wall times: control 108.26 s; direct certificate 105.23 s; parallel certificate 119.55 s; two root shards plus parent 122.18 s. The latter used about 233 CPU seconds and 1152 MiB sampled aggregate RSS. Root sharding was not expanded to more seeds after this negative result.

A separate cProfile D5/P2 seed-17 run recorded 91.9 million calls, about 35.9 s under profiling, and about 21.6 s cumulative in deepcopy (~60%). These instrumented timings are attribution evidence, not comparable wall-time results. See `profiling/poc-single-profile.json`.

The first reuse pilot recorded roughly 581,000 transition cache hits versus 170,000 transition entries in the P3 solve. Its belief memo/branch counts and complete outputs matched the control: the gain comes from avoiding repeated computation and copying, not from weakening the search.

## Correctness and validation

- Every final case has the same complete compiled-episode hash and exact policy hashes as its paired control, and matches the earlier combined-solver evidence for that seed. Policy comparisons exclude only the diagnostic visited-node count.
- 136 fast unit/integration tests passed (32 slow/stress tests deselected); two pre-existing Pydantic fixture warnings remain. After final import/style edits, all 34 new tests passed again.
- New tests cover positive/negative at-most-budget decisions, invalid cost claims, cache isolation after failed certificates, root-partition equivalence, parallel witness/action-value equivalence, transition reuse, input immutability, physical-limit exhaustion, and spawned-worker error propagation.
- Fixed a certificate cache bug: rejecting a guessed exact cost does not prove there is no policy through max_actions. Failed certificates are no longer stored as exhausted optimizer searches.
- A forced 16 s timeout with four live processes (parent, two search workers, resource tracker) successfully cleaned the process group. Matching successful cases can be skipped; timeouts are retried.
- Ruff passes for changed solver/diagnostics files and the new runner/tests. The generator has only pre-existing lint findings. No ty/basedpyright CI gate is configured; a repository-wide tooling migration is outside this PoC.

## Measurement limits

- CPython 3.14.7; frozen dependencies; AMD EPYC 9V74; eight-CPU quota; 8 GiB memory. See `profiling/poc-single-environment.json`.
- Three seeds and one reversed-order repeat are evidence of a substantial improvement, not a release stress test or a precise speedup distribution.
- Stage timers are nested, so do not sum them. In a parallel proof, certificate_minimal is parent wait time; worker search durations are reported separately.
- RSS is a nominal 50 ms sampled sum of process-group RSS, including worker and tracker processes. It can miss brief peaks and double-count shared pages; it is not unique physical allocation.
- The first three pilot memory readings are invalid (zero) due to namespace PID mapping. The sampler was corrected and the final runs use validated mapping. Pilot CPU measurements precede interpreter shutdown; final CPU values come from supervisor child-rusage deltas after shutdown. Timeout CPU values are null.
- Result filename suffixes r0/r1 denote repeat indices, not the R difficulty axis. All timed cases use D5/P3/R0. R1/R2 share the expensive generation path and apply resource pressure afterward; separate cold R1/R2 runs were not measured.
- Measurements are standalone generation subprocesses, not end-to-end MindTrial model runs. HTTP/service orchestration overhead and concurrent MindTrial task contention are not measured.
- No theory-axis, public gameplay, action-budget, hint visibility, or production default changes.

## Recommendation

Promote transition/route/choice reuse together with the earlier interning/budget optimization after a broader differential seed/profile sweep. Treat direct expected-cost certification as a separately reviewable small improvement. Keep single-episode process splitting experimental and disabled; do not expose a production worker setting on this evidence.

Use episode-level multiprocessing only where batch throughput is the goal. If further startup reductions are required, profile the remaining unique transitions before investing in a shared-memory search redesign.

## Reproduction and resume

Commands and checkpoint chronology: `single-episode-poc-progress.md`. Runner: `scripts/benchmark_single_episode.py`. Final per-case evidence: `profiling/poc-single-episode/`. Pilot files are explicitly separated into `poc-single-episode-pilot`, `poc-single-root-pilot`, and `poc-single-reuse-pilot`.

Python executor documentation: https://docs.python.org/3.14/library/concurrent.futures.html
