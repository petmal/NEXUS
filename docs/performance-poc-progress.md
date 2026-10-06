# Resume record

Status: plan committed; implementation next.

Read AGENTS.md and docs/performance-poc-plan.md. Base is diagnostic PR #2 at 75d5bda.
Use poc/solver-theory-performance, never main. No changes to public MindTrial.

Completed: remote base verified byte-for-byte; Python 3.14.7 frozen dependencies installed.
Next: implement opt-in state interning and budget bounds, fresh-process differential benchmark.

Setup: `uv sync --frozen --all-extras`.
Existing proof gate: `uv run pytest -q tests/unit/test_belief_policy.py tests/unit/test_solver_performance_invariants.py`.

Results and commands will be appended at each phase boundary. Do not infer that a launched
benchmark completed; inspect its atomic JSON result and code fingerprint.
