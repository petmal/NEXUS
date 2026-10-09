# Scientific investigation v2: implementation and validation

The approved architecture is integrated into the existing NEXUS engine, HTTP
session, receipt validator and human CLI on `feat/theory-prior-axis` (PR #6).
Select it with `NEXUS_AXIS_VERSION=2`, or `nexus generate --axis-version 2`.
The legacy version remains the default. Zero levels are diagnostic controls;
every primary cell in the [ten-run pilot](scientific-investigation-model-matrix.md)
uses nonzero D, T, P and R.

## What changed

- T1 supplies exact laws; T2 requires estimating a correction of known shape;
  T3 requires identifying a missing relationship within a disclosed finite grammar.
- D changes the investigation: independent measurements, dependent calibration,
  adaptive experiment choice, and construction of a diagnostic specimen.
- Bench experiments support prediction at inaccessible field settings. The
  controller checks the full submitted result jointly, without partial hints.
- P controls movement. R controls action/resource pressure. R0 uses ordinary
  `take` from unlimited stocks, repeatable machines and unlimited game actions.
  Transformations can remain irreversible because another source specimen is
  always obtainable. No special replenishment action is introduced.
- Terminal-only telemetry distinguishes first-attempt correctness, evidence
  sufficiency, redundant measurements, transfer errors and eventual victory.
  During play, players receive normal observations and public laws only.
- Exact finite-family qualification verifies the scientific certificate and
  physically replays a reference policy for every possible hidden world.

The [design](scientific-investigation-design.md) records the research, axis
definitions, supported combinations, proofs, and limits. T0 is supported at D0;
D1 currently supports T1. D0 and D2-D5 support T1-T3. These are explicit supported
families rather than a promise that every numerical combination exists.

## Validation evidence

| Gate | Observed result |
| --- | --- |
| Full regression, including legacy seed checks | 323 passed, 2 warnings, 243.37 seconds |
| Final CLI/display gate after the full run | 10 passed, 67 deselected, 4.53 seconds |
| Ten-cell pilot preflight | All qualified; 2,928 complete-world physical policy replays |
| Independent finite-family proof | 18 cases; tuple and bitmask solvers agree, plus 15 small arbitrary problems |
| Integrated review | Goal/stock/resource/certificate tampering and null serialization findings fixed; no remaining blocker in reviewed scope |
| CLI generate/qualify/solve/replay | D5/T3/P2/R1, seed 17 passed |
| Live HTTP service plus command-line receipt validation | D5/T3/P0/R0, seed 7 won in 16 actions; first submission correct; validator exit 0 |
| Lockfile, changed Python syntax, focused Ruff, whitespace | Passed |

Full test command:

```sh
NEXUS_STRESS_SEED_COUNT=3 uv run --frozen pytest -q --durations=12
```

Final CLI gate:

```sh
uv run --frozen pytest -q tests/unit/test_cli.py tests/unit/test_scientific_investigation.py -k 'cli or human_play or action_help'
```

The two new display/help tests were added after the full suite. The final help-text
wording also received a direct CLI smoke check. The full suite's two warnings were
Pydantic enum serialization warnings, not test failures. No paid model calls were
made. Docker/Podman were unavailable locally; local container validation is not
claimed. The CI workflow includes the scientific CLI and container smoke paths.
GitHub [CI run 37886563711](https://github.com/petmal/NEXUS/actions/runs/37886563711)
passed for integrated runtime commit `5c7f056b`, including extended tests,
cross-seed stress, CLI smoke and container smoke. This predates the final
documentation/display commit. No separate type-check or coverage result is claimed.

## Generation performance

The largest current family has 576 possible worlds but only 132 distinct terminal
policy transcripts. Generation constructs one physical witness per transcript;
qualification still replays every world. Precomputed outcome bitmasks, target
equivalence masks and per-instance dynamic-programming caches avoid repeated work.

Fresh-process measurements on Python 3.14.8, P1/R1, seeds 7 and 23:

| D/T | Cold generation, seconds | Warm generation, seconds |
| --- | ---: | ---: |
| 3/1 | 0.0042-0.0047 | 0.0012-0.0013 |
| 3/2 | 0.0126-0.0129 | 0.0035-0.0037 |
| 3/3 | 0.0366-0.0378 | 0.0092-0.0114 |
| 4/3 | 0.1218-0.1243 | 0.0221-0.0244 |
| 5/3 | 0.1126-0.1143 | 0.0202-0.0220 |

These are local generation timings, excluding interpreter/import startup and
standalone exhaustive qualification. They are not container readiness or harness
latency measurements. See the [raw benchmark](profiling/scientific-investigation-benchmark.json)
and `scripts/scientific_investigation_benchmark.py`. CPU/GPU parallelization is
not justified for this measured subsecond workload; retain it as a question if
future relationship families substantially expand the state space.

## What remains empirical

The new families remove the observed exact-context preview shortcut and introduce
provable information dependencies. This supports testing a stronger scientific
reasoning demand; it does not prove that current models will fail. The grammar is
small and disclosed, and systematic enumeration remains legitimate.

R0 permits eventual controller enumeration. D3/T1 has only four distinct targets,
so even finite-budget blind guessing can be competitive there. First-submission
correctness and target ambiguity before submission must accompany eventual wins.
The certified adaptive measurement minimum is not a physical-action minimax
optimum; the physical reference bound is a realizable worst-case policy.

Next empirical step: run the [matrix](scientific-investigation-model-matrix.md)
using its [exact environments](scientific-investigation-model-matrix.json), retain
the OCI revision, and audit live play separately from harness Pass/Fail/Error.
Treat the suggested difficulty scores as hypotheses. If models solve these
efficiently, expand compositional relationships or linked investigations with
proved dependencies before increasing resource pressure.
