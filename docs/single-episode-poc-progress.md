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
