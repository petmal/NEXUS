# Solver and theory PoCs: design and execution

Base: `75d5bdacdd66aadb48609696592e0e37c5f3b390` (diagnostics PR #2).
Working branch: `poc/solver-theory-performance`. No main or production rollout.

## Goal and boundaries

Measure whether exact solver optimizations make fresh-seed D5/P3 practical, and whether a
bounded T1 prior can support lower-D/P2 scientific reasoning tasks economically. Preserve engine,
public controls, hidden-state separation, and exact qualification. T1 is a research harness,
not a newly supported CLI/service axis. T2+, D4/D5 under T1, map-uncertainty budgeting, and
model evaluations are outside this PoC. Do not claim model discrimination from generator tests.

## Design

1. Opt-in solver experiments: intern semantic states and replace repeated budget facts with
   monotone bounds. A state proven losing through b loses at all smaller budgets; a state
   proven winning at b wins at all larger budgets. Budget means at-most actions. Keep the
   baseline selectable and compare witness, action values and exact optima, excluding counters.
2. T1: formal independent branch primitives, compact finite signatures, behavior deduplication,
   evidence conditioned against the full public prior, materialize only surviving ASTs. Preserve
   the paired world's laws/topology/goals; reject unsupported evidence rather than weakening D.
   Measure D0/D1/D2 at P2/R0 first. Public theory and enumeration use the same specification.
3. Parallelism: benchmark independent cold episodes with Python's ProcessPoolExecutor (spawn),
   bounded explicit workers, deterministic result IDs and parent-only checkpoint writes. Assess
   within-search dependencies and GPU array suitability before adding any framework dependency.

## Execution and gates

1. Commit this plan and resumable progress record before experiments.
2. Implement baseline/intern/bounds/combined modes and a fresh-process comparison harness.
   Run existing solver proofs plus differential fixtures, then sequential D5/P2 and P3 seeds
   17, 18, 19. Start with 17; expand only if correctness and resource gates pass. Record wall
   time, peak RSS, exact outputs, work counters, runtime and code fingerprint. Never compare
   profiled and unprofiled wall times or simultaneous and sequential cases as a speedup.
3. Build T1 signatures and prove count, T0 inclusion, evaluator equivalence and evidence
   membership. Sample evidence acceptance and run bounded exact P2 policy cases. Record
   rejected cases and distinguish surviving from physically viable hypotheses.
4. Compare sequential and two-worker episode batches, conditional on available CPU/memory.
   Document GPU feasibility using primary documentation; no unsupported GPU speed claim.
5. Commit raw results, conclusions, limitations and exact resume commands. One final review
   and targeted verification; create a draft PR only after commits are ready to avoid CI churn.

## Interruption and cost policy

Every completed case writes an atomic JSON checkpoint. Resume skips only matching input/code
fingerprints; incomplete output is rerun. Use subprocess timeouts and conservative workers.
Commit each completed phase to private GitHub. Long deterministic experiments run without LLM
calls per case. No model API calls, paid CI stress runs, or speculative agent fan-out.
The assistant cannot inspect credits or the five-hour allowance timer and cannot automatically
pause/resume its own billing. Resume from the progress file after an interruption/reset; no
requirement to restart completed measurements.

## Decisions

- Baseline is PR #2, not the alternative PR #3 telemetry schema (verified remote head).
- Use standard-library process workers first: maintained, no new dependency, isolated caches.
- Keep production behavior unchanged by default until multi-seed exactness/performance evidence.
- Broader T1 theory does not establish fair exploration budgets: current solver knows the map.
