# Resume record

Status: solver and T1 PoCs implemented; final solver measurements running.

Read AGENTS.md and docs/performance-poc-plan.md. Base is diagnostic PR #2 at 75d5bda.
Use poc/solver-theory-performance, never main. No changes to public MindTrial.

Completed: remote base verified byte-for-byte; Python 3.14.7 frozen dependencies installed.
Solver modes baseline/intern/bounds/combined implemented; 10 differential/cache tests pass.
T1 compact grammar has 41,472 syntax forms / 27,120 behaviors. Four proof tests pass,
including all T0 membership, full-domain branch/condition equivalence, and a tiny independent
ordinary-action minimax comparison. First 20-seed exact T1/P2 sweep: D0 20/20 accepted,
D1 18/20, D2 11/20. All accepted policies replayed over every viable hypothesis at their
proved action budget. Rejections retained; this is conditional on current T0-selected families.

Seed-17 corrected solver ablation completed: P3 baseline 157.04 s / 4056 MiB;
combined 99.12 s / 544 MiB. P2 baseline 17.60 s / 528 MiB; combined 9.88 s / 115 MiB.
All four modes have identical episode and policy hashes per profile.
Next: extend baseline/intern/combined to seeds 18/19, compare
one/two process workers, rerun T1 reports on the final code fingerprint, run fast regression.

Important: docs/profiling/poc-solver-pilot is a superseded timing pilot. Experimental modes
initially missed richer cached proof reuse during qualification; corrected by separating cache
semantic keys per mode and retaining normal richer-proof lookup. Do not report pilot speedups.
Pinned pydantic_core fails loading in Python 3.14 subinterpreters; use process workers.

Setup: `uv sync --frozen --all-extras`.
Existing proof gate: `uv run pytest -q tests/unit/test_belief_policy.py tests/unit/test_solver_performance_invariants.py`.

Results and commands will be appended at each phase boundary. Do not infer that a launched
benchmark completed; inspect its atomic JSON result and code fingerprint.

Resume commands (fresh processes and atomic files; matching completed cases are skipped):

```bash
uv run python scripts/benchmark_solver_poc.py --seeds 17 --planning 2 3 --out docs/profiling/poc-solver
uv run python scripts/benchmark_solver_poc.py --seeds 18 19 --planning 2 3 --modes baseline intern combined --out docs/profiling/poc-solver
uv run python scripts/benchmark_solver_poc.py --seeds 17 18 --planning 3 --modes combined --workers 1 --timeout 300 --out docs/profiling/poc-cpu-serial
uv run python scripts/benchmark_solver_poc.py --seeds 17 18 --planning 3 --modes combined --workers 2 --timeout 300 --out docs/profiling/poc-cpu-parallel
uv run python scripts/benchmark_theory_poc.py --seeds 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 --exact
uv run pytest -q -m 'not slow and not stress' tests/unit tests/integration --maxfail=1
```

Seed 18 solver comparisons have also completed; seed 19 and the CPU throughput comparison
are in progress. No source edits during final measurements. Extra certificate regression cases
were added to the test suite (tests are outside the measured runtime fingerprint).
