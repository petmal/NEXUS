# Runtime efficiency pass 2 — execution plan

This plan implements only the proof-approved, low-risk optimizations from `docs/runtime-efficiency-pass-2-design.md`.

## Branch

Use `feat/runtime-efficiency-pass-2`, based on canonical `feat/epistemic-calibration` commit `6a8e6f2c`.

Do not modify `main`. Do not merge temporary validation workflow commits into the canonical feature history.

## Commit 1 — proof/design documents

Add the design/proof plan and this execution plan.

## Commit 2 — rule interpreter allocation reduction

Tests first:
- add a reference recursive-copy interpreter in tests;
- exhaustively compare current catalogue outputs across the complete finite generated domain;
- add focused generic AST cases (`SET`, modulo, logical condition forms, nested sequence/conditional);
- assert caller artifact is unchanged and returned object is independent.

Implementation:
- public `apply_effect()` copies once;
- private recursive helper mutates only the private working copy;
- retain field/type normalization/validation behavior.

Gate:
- rule/engine unit tests and exhaustive equivalence test green.

## Commit 3 — exact belief-search memory/cache improvements

Tests first:
- visited-count equality against a small reference count fixture;
- rich cached solve followed by no-action-value exact certificate must reuse without changing result;
- cache cannot reuse an insufficient proof bound;
- requested action-value selection still returns exactly the requested values.

Implementation:
- remove duplicate `visited_nodes` set and report `len(memo)`;
- add richer-cache fallback for no-action-value requests only;
- preserve LRU size and bound adaptation rules.

Gate:
- exact belief-policy proof suite green.

## Commit 4 — hypothesis episode and normalization copy reduction

Tests first:
- base episode mutation isolation;
- sibling hypothesis isolation;
- shallow optimized hypothesis episode serializes identically to the previous deep-copy construction;
- fresh-state in-place normalization equals copying normalization and never mutates source state;
- compressed physical and exact policy fixture results unchanged.

Implementation:
- replace whole-episode deep copy with targeted copies of only mutated state/maps;
- split normalization into copying external-state helper and in-place fresh-state helper;
- update only successful `step()` result call sites with proven ownership.

Gate:
- solver proof tests and generation-performance invariants green.

## Commit 5 — remove CLI duplicate qualification

Tests first:
- generation boundary remains fail-closed when final qualification fails;
- CLI `generate` invokes `generate_episode()` once and does not invoke an extra qualifier;
- saved episode remains loadable and explicit `nexus qualify` remains available.

Implementation:
- remove `qualify_episode` import/call from `generate` command only.

Gate:
- CLI unit/integration tests green.

## Validation batch

Avoid running an expensive Actions job after every commit. After focused tests are green in the implementation runner, run one consolidated validation:

1. exact solver proof tests;
2. all unit/integration tests excluding stress;
3. slow/extended suite;
4. `NEXUS_STRESS_SEED_COUNT=1` across all 24 D/P profiles;
5. cold `generate_episode(17, D5, P3, R1)` under `/usr/bin/time -v`.

Compare the cold case with the first-pass baseline on the same hosted environment when possible:
- prior wall: ~4:03;
- prior peak RSS: ~4.60 GB (4,601,152 KiB);
- prior seed-17 costs: physical 14, guaranteed 17.

The exact costs must remain 14/17 for that seed/profile. Any deterministic generation metadata changes require investigation before merge.

## Merge criterion

Merge/fast-forward into `feat/epistemic-calibration` only if:
- all robustness proof tests pass;
- all supported D/P stress profiles qualify;
- no semantic changes are observed for fixed seeds;
- no private/public contract changes occur;
- runtime and/or peak RSS improve measurably or the code removes clearly redundant work without regression.

After merge, delete the temporary optimization branch and any validation-only branches/workflows while retaining `poc/theory-prior-axis`.
