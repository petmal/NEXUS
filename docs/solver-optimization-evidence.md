# Production optimization and archived evidence

The production solver now uses canonical state interning, monotone exact-budget intervals,
macro-choice/route/per-hypothesis transition reuse, and sequential exact-cost certification for
P3 with the ordinary optimizer as fallback. These caches work within an episode solve, including
fresh random seeds. No worker setting or precompilation is required.

The two certificate checks prove a winning policy at K and impossibility at K−1. Rejection of an
exact claim is not an exhausted optimization search and is not cached as one. Physical search
state-limit exhaustion fails qualification rather than removing a possibly viable hypothesis.
Retained interned states are read-only; engine transitions copy before mutation. Public actions,
seed mapping, goal acceptance, action-value analysis and deterministic witnesses are unchanged.
`visited_belief_nodes` now counts state/belief intervals rather than individual budget entries.

## Immutable research archive

The integration preserves both PoC and alternate diagnostics heads as commit ancestors. The
following links remain usable after branch deletion:

- [Completed single-episode PoC, source and findings](https://github.com/petmal/NEXUS/tree/49965c2128e187bae5be87224c7d02a5fed16b97)
- [Single-episode measurements](https://github.com/petmal/NEXUS/blob/49965c2128e187bae5be87224c7d02a5fed16b97/docs/single-episode-poc-findings.md)
- [Earlier storage/budget PoC](https://github.com/petmal/NEXUS/blob/49965c2128e187bae5be87224c7d02a5fed16b97/docs/performance-poc-findings.md)
- [Alternate diagnostics implementation](https://github.com/petmal/NEXUS/tree/2095a947b5eac34fef69418cf771006475e4b300)

The PoC measured 3.66–3.87× lower single-episode latency for reuse+certificate versus the already
optimized combined control on three D5/P3 seeds. Independent-process splits repeated overlapping
work and lost memo reuse, so they were slower than the best sequential implementation. Those
results do not rule out every parallel algorithm; they do not justify a production CPU/GPU rewrite.
Raw PoC scripts/results are archived in the commits above, rather than shipped in the current tree.
`poc/theory-prior-axis` remains intentionally separate research, with no production T-axis switch.

## Reproduce integration validation

Install with `uv sync --frozen --all-extras`. Run full unit/integration tests, then property stress:

```sh
uv run pytest -q -m 'not stress' tests/unit tests/integration
NEXUS_STRESS_SEED_COUNT=3 NEXUS_STRESS_FAIL_FAST=1 uv run pytest -q tests/property
```

Check out archive commit `49965c2128e187bae5be87224c7d02a5fed16b97` separately, then run:

```sh
uv run python scripts/verify_solver_integration.py --reference ../nexus-reference \
  --output docs/profiling/integration
```

The runner checks complete episode hashes and successful exact policy hashes (excluding only
visited-node diagnostics) on all 24 D/P combinations at seed 17 plus D5/P3/R1 and R2 at three
seeds. Each side runs cold in a separate subprocess. Checkpoints record source/runner fingerprints;
only exact matching successful checkpoints are skipped. Use the combined/ordinary archived solver
as the oracle; its equivalence to the former baseline is established in the earlier PoC.

The official operator profiler remains `scripts/profile_generation.py`. Run it in a fresh process
with `--json-out`, optionally `--cprofile`, for a deployment host. Nested stage timings must not be
summed. Never expose profiler output/private episode artifacts to a playing model.
