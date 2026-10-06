# Solver and terminal diagnostics integration

## Goal and boundary

Promote the measured high-value single-episode optimizations into `feat/epistemic-calibration`,
with terminal-only evaluation diagnostics and operator generation profiling. Keep `main` unchanged.
Fresh random seeds must benefit without precompilation. Public mechanics, difficulty guarantees,
episode identities, exact action costs, deterministic witnesses and receipts must be preserved.

Production uses state interning, monotone exact-budget memoization, route/choice/per-hypothesis
transition reuse, and direct expected-cost certification for P3 (with ordinary optimization as
fallback). Remove research switches and subprocess search variants from the runtime. Retain their
full source/results through integration ancestry and immutable commit links. T1 remains research.

## Diagnostics decisions

PR #2 provides the canonical performance-v2 fields, irreversible evaluator finalization, strict
player protocol, validator stderr diagnostics, and operator-only stage timing/profiler. Keep these.
PR #3 contributes the physical-action delta and correct Boolean goal-deficit handling; retain its
useful tests while avoiding conflicting field aliases and a duplicate profiling script.

Atomic leaf truth counts are descriptive only. For OR/NOT, do not report every false child as a
required missing condition; preserve the Boolean expression in the terminal diagnostic. Do not
emit solver baselines or deficits while play is active. Finalization cannot resume play.

A new immutable schema revision must match the integrated payload. Keep the published historical
v1/v2 schemas available and publish the integrated contract as v3 to avoid silently redefining v2.

## Validation and calibration

Run unit/integration tests including slow tests, 3-seed x 24-profile generation stress, dedicated
D5/P3/R1 and R2 checks, and differential episode/policy comparisons with the prior validated
combined solver. Exercise live service/client/validator and replay flows. Use frozen dependencies.
Create 10 real-model cells, label difficulty as ordinal estimates, use matched seeds for P/R
comparisons, and separate tool-call limits from in-world action pressure. No model calls here.

## Preservation and cleanup

Canonical base: ad7d73499ae55dcaa212a675ac0b73fde218ffa2.
Diagnostics #2: 75d5bdacdd66aadb48609696592e0e37c5f3b390.
Alternative diagnostics #3: 2095a947b5eac34fef69418cf771006475e4b300.
Completed PoCs #4: 49965c2128e187bae5be87224c7d02a5fed16b97 (descends from #2).

The integration merge preserves #3 and #4 as ancestors. The current tree contains production
code and useful profiling tools; archived experiments remain recoverable from those commits.
Retain `poc/theory-prior-axis`: it contains separate, intentionally retained theory design work.
After tested integration, retire PRs #2/#3/#4 and their heads plus the integration head.

The connector lacks branch deletion and local git has no authenticated remote. Use a narrowly
scoped, temporary merged-PR cleanup workflow with contents-write permission, exact expected
heads, ancestry checks and git force-with-lease deletions. Remove that workflow after it finishes.
Never change repository settings or delete `main`, the canonical feature branch, or the theory branch.
