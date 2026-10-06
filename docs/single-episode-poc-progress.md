# Single-episode generation PoC

Base: PR #4 head `28255ce5dd3a11131b590cf77bc3291771e8a935`.
Status: design checkpoint; implementation pending.

## Objective

Reduce cold, single-episode D5/P3 startup latency for per-task MindTrial services.
Keep production defaults unchanged. Preserve deterministic episodes, exact budgets,
policy witnesses, action values, private/public boundaries, and candidate acceptance.

## Experiments

1. Control: combined state interning / monotone bounds, existing iterative search.
2. Sequential: certify the expected planning-extension cost K directly with exact
   winning-at-K and losing-at-(K-1) checks. If certification fails, use the ordinary
   optimizer so rejected candidates and their diagnostics keep baseline semantics.
3. Parallel: evaluate losing-at-(K-1) in a spawned process while the parent proves
   winning-at-K, retaining the parent's winning memo for witness/action values.
4. If measurements justify it, split coarse root branches of the expensive decision
   proof across a bounded worker pool. Avoid shared hot-path Manager dictionaries.

Measure cold full-process latency (startup/shutdown included), internal generation
latency, per-proof timings/work, total process-tree CPU, sampled aggregate process-tree
RSS, and exact episode/policy hashes. Sampled RSS is not exact peak allocation and can
double-count shared pages. Run cases serially; only within-episode work is concurrent.
Use explicit spawn and the Python standard-library process executor, no new dependency.

Start with seed 17, then seeds 18/19 and a repeat if promising. Every case gets an
atomic result, source fingerprint, timeout, and safe process-tree cleanup. Failed and
partial cases remain visible and are retried; matching successful cases are skipped.

## Validation

Focused semantic tests: positive/negative budget decisions, too-low/too-high cost
claims, sequential/parallel equality, cache-bound isolation, deterministic witnesses,
and worker exception propagation. Run existing fast unit/integration gate after edits.
The existing repository has no installed Ruff/ty/basedpyright gates; toolchain migration
is deferred as outside this performance PoC. No full release/stress readiness claim.

## Resume

Read this file, `docs/performance-poc-progress.md`, and the current git diff first.
Do not rerun completed fingerprint-matching benchmarks or overlap independent timing
runs. Update this record with commands and evidence at each phase; commit to the
existing research branch, never main or the public MindTrial repository.

No balance/reset-time access exists; checkpoints make manual resumption independent
of allowance boundaries.

## Implementation checkpoint

Implemented ordinary / sequential certificate / parallel certificate variants. The
parallel variant runs the K-1 decision in one spawned worker while the parent computes
K and retains its memo for the witness and action values. Failed certificates are no
longer cached as exhausted optimization searches; generation falls back to ordinary
optimization on certificate failure.

Focused validation: 23 existing solver tests + 11 new decision/certificate/spawn tests
passed. Environment restored with `uv sync --frozen --all-extras` (Python 3.14.7).
Pilot command (currently running; no performance conclusions yet):

```sh
uv run python scripts/benchmark_single_episode.py --seeds 17 --timeout 300 \
  --out docs/profiling/poc-single-episode-pilot
```

The benchmark uses explicit process groups and kills the whole child group on timeout.
Measurements include worker shutdown. The result fingerprint covers source, runner,
shared runner helpers, and lockfile. Do not edit measured files during a running batch.

## Expanded implementation checkpoint

Pilots (seed 17; exploratory timings, not final matched-source comparisons):

- Ordinary combined: 108.26 s end to end.
- Sequential certificate: 105.23 s.
- Parallel certificate: 119.55 s; lost memo reuse increases CPU and follow-up work.
- Two root shards plus parent: 122.18 s; sampled aggregate RSS 1152 MiB.
- Transition/route/choice reuse: 29.35 s.
- Reuse + sequential certificate: 26.55 s.
- Reuse + parallel certificate: 32.56 s.

Episode and policy hashes match. The first three pilot RSS readings are INVALID (zero):
namespace PIDs differed from /proc PIDs. The sampler now resolves NSpid plus namespace
identity before measuring process groups. The later pilots have valid sampled memory;
pilot CPU counters are taken before interpreter shutdown. Final supervisor CPU counters
include completed child/descendant usage through shutdown. Timeout CPU is null because
killed grandchildren may not be accounted to their parent.

A cProfile D5/P2 run found deep copying at ~60% of cumulative runtime. A bounded cache
now reuses macro choices by normalized state, routes by state/route, and transitions
by state/route/action/hypothesis (law-independent actions share one result). Caches last
only for one solver call; belief-group assembly remains exact and separate. No-op routes
reuse the existing solver-owned state; engine.step continues copying before mutation.
No cached mutable state is mutated by this optimization.

Validation before final timings: 136 fast tests passed, 32 deselected, two existing
Pydantic fixture warnings. After import/style cleanup, all 34 new tests passed again.
Ruff checks pass for the solver, diagnostics, runner and new tests. The generator has
pre-existing lint findings (unused import, pairwise, unnecessary encoding arguments);
no unrelated cleanup/toolchain migration is included. No ty/basedpyright gate exists.

Final command (run cases serially; allow each case to use its own bounded processes):

```sh
uv run python scripts/benchmark_single_episode.py --seeds 17 18 19 \
  --variants ordinary reuse reuse-certificate reuse-parallel \
  --out docs/profiling/poc-single-episode
```

Then repeat the control and best serial variant in reversed order for seed 17:

```sh
uv run python scripts/benchmark_single_episode.py --seeds 17 \
  --variants ordinary reuse-certificate --repeat 2 \
  --out docs/profiling/poc-single-episode
```

The first repeat's existing cases should be skipped. Final findings and validation
record remain pending. Source and runner must remain frozen while these runs execute.

## Final-run checkpoint (in progress)

Final source fingerprint: `2b918cc6a9da64e4a110f144322c6441c57b8a9a3d14adbef686ea626f4c58b7`.
GitHub implementation checkpoint: `c8ad4c73920dbd142e5ca645aab46ab336c03671`.
CI run 229 passed for that checkpoint. Seed 17 has completed all four final variants;
seed 18 is in progress. Persisted results are individually complete and resumable.
A forced parallel-root timeout observed four processes and confirmed complete cleanup.
The timeout evidence is in `profiling/poc-single-timeout-validation.json`.
