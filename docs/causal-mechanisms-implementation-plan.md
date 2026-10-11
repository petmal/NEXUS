# Causal mechanism laboratory: implementation and resume plan

Baseline: local b460a0f on feat/theory-prior-axis, clean worktree. Existing remote
feature head from preceding work: 5f2a0c7590f7b35b40c483770ede3e2e46b3891f.
Verify remote head before publishing; local and remote ancestry differ. No force
push or main merge. Existing ontologies are compatibility fixtures, not migration
targets.

1. Prove a finite family independently; document public grammar, target
   equivalence, history ambiguity and a realizable public policy. Read-only design
   review of serialization/replay boundary. COMPLETE: scratch arithmetic proof and
   review accept full public history with privately derived mode.
2. Add data-only schemas, compositional exact laws, cached public inference and
   policy qualification under ontology/causal. Test independent oracle agreement
   before runtime integration.
3. Implement runtime adapter, generator, evidence, normal CLI/service family
   selection and terminal diagnostics. Generalize code-owned registry entries so
   family addition does not require branches in engine/session/replay. Keep
   unsupported D/T/P/R combinations explicit.
4. Test all admitted truths against policy, live reference play, off-policy
   posterior updates, failed submissions, privacy, malformed payloads, save/load,
   replay, CLI/HTTP and stock/probe semantics. Compare existing fixtures unchanged.
5. Fresh independent implementation review; full regression and fixed-host
   cold/warm profiling. Fix concrete findings; do not broaden tests after gates pass.
6. Document supported profiles, exact proof scope, player-safe tool/task examples,
   model pilot matrix, remaining empirical calibration and final resume checkpoint.
   Commit focused phases and publish on the existing private feature branch.

Implementation checkpoint: steps 1–4 complete. Independent implementation review
accepted corrected code; all 648 truths passed live public-policy play and JSON replay.
All 197 previous compatibility snapshots are unchanged. Full regression is running;
final focused tests cover late CLI/type/telemetry refinements. No paid APIs used.

Resume from this branch and inspect git status before editing. Local plan commit
7832e7a has equivalent prepared remote commit 974c91b51c692640c29438b46669ed9bdb550785,
with exact tree 66103aa6694602540232344177049fd1c358a485. The remote branch is still at
5f2a0c7590f7b35b40c483770ede3e2e46b3891f until all implementation gates pass.
Publish the final descendant using an expected-head lease; never force-push.

Reproducible validation commands:

```sh
uv sync --frozen --all-extras
NEXUS_STRESS_SEED_COUNT=3 uv run pytest -q --maxfail=1 --durations=12
uv run pytest -q tests/unit/test_causal_mechanisms.py tests/unit/test_cli.py
uv run python scripts/profile_causal.py --out /tmp/causal-benchmark.json
uv run nexus generate /tmp/causal --axis-version 2 --science-family causal-mechanisms-v1 --seed 17 --discovery-level 5 --theory-level 3 --planning-level 1 --resource-pressure 1
uv run nexus qualify /tmp/causal/private.json
```

Use the new model-matrix JSON for harness settings and its Markdown companion for
the manifest-led task prompt. Never reuse hardcoded controller/port/five-setting
instructions for this family. Full plans, proof scope and results are committed
project documentation; no scratch artifact is required to resume implementation.


## Completed local gates and publication

Implementation is complete. Full regression: **504 passed**, three existing
malformed-model warnings, including three-seed stress. Final focused CLI/new-family
check: **61 passed**, four slow cases deselected; the complete 648-world live/replay
case also passed after the final mechanics refinements. New-module Pyright, focused
Ruff, frozen lock and whitespace gates pass. All 197 compatibility cases are unchanged.

Local implementation commit: `4d6f3c3d212176af953c6ad111118161124b2ced`.
Equivalent prepared remote commit: `b3cdd1e9d2f7543d4ce08f8eb1ea7b43c69cc137`.
Exact tested implementation tree: `8bbdadce13701cc38f51d42a688cc319774315f4`.
Final documentation follows as a separate commit. Publish the documentation head
as a descendant of the prepared remote implementation commit; verify its tree and
inspect exact-head CI. No main merge, force-push, public MindTrial changes or paid
model runs. The PR records final publication/CI state without creating another
self-referential documentation commit.

The next user step is the real-model pilot in `causal-mechanisms-model-matrix.md`.
Future work should follow empirical failures: adaptive construction qualification,
richer ontology blocks or additional supported D/T cells require new proofs.
Do not infer a >=50% model-failure rate from reference solver success.
