# Dynamics cache/reference implementation judgement

Read-only review of the new working-tree implementation on `feat/theory-prior-axis`, based on HEAD `09fe7bb`, 2026-10-16. Inspected `reference_cache.py`, `reference_proof.py`, `reference_identity.py`, `inference.py`, `policy.py`, `scripts/compile_dynamics_reference.py`, the compiled artifact, and the design/implementation scope. No repository implementation files were changed.

## Verdict

No blocking correctness defect found in the reviewed cache and reference-policy changes. The implementation follows the bounded design: source-bound immutable cached old-policy nodes, exact computation on cache miss, and improved physical realization of the same scientific query sequence. Completion still requires committed regression coverage and release/package gates below; this judgement is not a full-family release approval.

## Findings

1. **Cache trust and stale safety are sound for an immutable installed process.** The artifact's exact bytes are pinned by a digest in reviewed Python code; the artifact's dependency map is compared against actual source bytes. Missing/stale/unreadable data falls back to an empty immutable map, after which the old inference path recomputes. The loader bounds file size and node/mask/index values. The identity module is excluded from the artifact source list, avoiding a digest cycle. The repair complete-package source identity will cover it once requalified. Do not expect an already-running process to detect subsequent on-disk edits: `load`, `choose`, and `policy_bound` intentionally cache results; tampering tests must use a fresh process or clear all relevant caches.

2. **The compiler bypasses artifact choices and checks the right mathematical object.** It recreates the exact old greedy tie breaks, reconstructs child partitions, requires strict refinement and reachable nodes, checks terminal target uniqueness and the two-part recurrence, then compares the whole node map against an independently recomputed map. The runtime digest is an identity check, not the mathematical proof; the offline checker supplies that proof. The old root remains `(8,52)` and generation certificates/budgets need not change.

3. **The reuse guarantee is valid.** Each old scientific query is executed on a compatible prefix or a still-unused survey. With eight surveys pre-taken and at most eight old queries, there is always a fresh fallback for the next query. The selected preparation minimizes actual preparation actions among compatible surveys; a fresh survey supplies an option no more expensive than the old materialization. Belief updates use actual public measurement payloads. The code correctly distinguishes global stage configuration from each specimen's current point and skips configuration/operation only when unnecessary. `reuse=False` retains the old executable policy.

4. **Minor missed optimization, not a correctness issue:** reference readings depend only on `e`, while the current planner resets the entire point to `(0,0,e)` even when an existing survey already has the same `e`. This is safe and the fresh-survey comparison still proves non-regression. An e-only optimization is optional; if implemented, retain the specimen's actual point in tracked state and measurement data. Do not count theoretical e-only savings until verified against the live engine.

5. **Timings remain incomplete in the reviewed snapshot.** Cache-hit load time and witness-partition time are logged. A cache miss reports its reason, but full uncached bound construction and total episode construction are not yet separately timed. This is an outstanding approved instrumentation requirement, not a cache-correctness blocker. Keep all such diagnostics operator-only.

6. **Release work is required, not optional.** Every new/changed Python module invalidates repair's all-package source binding. The artifact JSON also invalidates saved matrix source digests. Requalify through the established gates and regenerate the matrix report; do not hand-refresh hashes during packaging. The repair semantic package digest may change while its mathematical proof, witness, budgets and worlds remain unchanged.

## Executed evidence

The first quick load/generation observation used the available Python 3.12 runtime: 3,043 nodes loaded in 10.9 ms and first generation took 37.6 ms, with `witness_rows()` never called. This is advisory timing only. Subsequent semantic checks used the repository's newly available Python 3.14.8 environment.

- Checked all 3,043 artifact nodes using the offline checker, including its uncached original-greedy recomputation.
- Rejected truncated JSON, unsupported version, mismatched source map, malformed node shape, and altered bytes with the original pinned digest.
- Changed the root work bound and confirmed the offline recurrence checker rejected it.
- Replaced the loader with an empty map in memory, cleared inference caches, and confirmed exact recomputation still returns `(8,52)`.
- Ran 22 challenge profiles: both P0/P1 for seeds 128, 839, 1013, 649, 1509, 219, 0, 17, 1943, -1, and 10^20. Ran both old and improved policies for each profile, totaling 44 successful challenge executions with exact trace replay. Each improved execution used no more actions than the old one and stayed within the unchanged certificate bound.
- Ran four T0 controls (two seeds × P0/P1), all with exact `4+P` actions.

Selected P1 live-engine counts:

| Seed | Old | Improved |
| --- | --- | --- |
| 128 | 47 | 37 |
| 839 | 47 | 40 |
| 1013 | 50 | 45 |
| 649 | 50 | 43 |
| 1509 | 50 | 46 |
| 219 | 50 | 40 |
| 17 | 65 | 46 |
| 10^20 | 53 | 49 |

The bounded live execution/replay check took about 1.8 seconds; the full artifact/checker/negative/fallback exercise about 2.9 seconds on this host. These timings are observations, not performance thresholds.

## Recommended committed tests and final gates

- Cold installed-wheel subprocess, launched outside the checkout: verify artifact presence/load, unchanged certificate, and that cached generation does not invoke `witness_rows` or uncached root recursion. Cover saved-episode validation too.
- Negative loader cases in a copied package or temporary artifact path: missing/truncated/oversized file, digest mismatch, matching self-digest without the pinned identity, stale semantic source identity, malformed entries, missing root. Check fallback produces the original certificate, not merely that decoding raised.
- Negative offline proof cases: false terminal, incorrect work/readings, missing child, non-refining query, unreachable node, altered query/tie-break. Ensure check mode is read-only and detects stale bytes/identity.
- Exact generation compatibility for cache hit and forced fallback across T0/T3, P0/P1 and modulo-equivalent/negative/large seeds, with a fixed nonce source for complete dump comparisons. Ensure no new random draws were added.
- Extend the existing all-1,944-world test to record improved-versus-old action counts or another explicit no-regression invariant, with actual public victory and replay. Retain exact T0 action-count tests and the existing privacy tests.
- Focused reuse tests: matching point with different global stage setting, matching setting with different point, repeated pulse points, exact prefix, incompatible histories, and reference measurements on prepared surveys. Tests should assert action traces and public preparation, not internal data structure shape.
- Regenerate the cache after final formatting/source changes, then run its check command. Requalify repair, refresh ten-cell preflight, verify canonical newline/package handling and the installed wheel.

No paid API calls, sub-agents, or implementation edits were used in this review.
