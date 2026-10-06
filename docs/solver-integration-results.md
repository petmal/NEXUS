# Solver and terminal-diagnostics integration results

The validated high-value optimizations are now the default solver path on the integration PR
into `feat/epistemic-calibration`. Fresh random seeds benefit from within-solve reuse. Exact world
acceptance, optimum costs, policy witnesses, action values, and player-visible mechanics remain
unchanged in the differential sample. Terminal diagnostics use immutable performance-v3.

## Integrated changes

- Canonical state interning and compact monotone budget intervals reduce search storage and
  repeated work. Cached choices, routes and per-hypothesis transitions avoid repeated engine
  calls and copying across belief sets.
- P3 directly proves the required cost K and disproves K−1, sharing memoized facts. A rejected
  certificate falls back to ordinary exact optimization. Failed claims cannot poison later
  searches; warm and cold certificate status agree. Physical state-limit exhaustion fails closed.
- PR #2's irreversible evaluator finalization, strict player protocol, validator stderr report,
  stage timing, and generation profiler are retained. PR #3's physical-action delta and proper
  Boolean goal deficits are included in v3, without conflicting field aliases or duplicate tools.
- CPU process splitting is not enabled. The previous PoC found overlapping proof work and loss
  of memo reuse made the tested splits slower. No GPU dependency or production T-axis is added.

## Validation

| Gate | Result |
| --- | --- |
| Final unit/integration suite, including slow tests | 127 passed; 98.30 s |
| Property suite | 3 passed; 152.10 s |
| Generated profile stress | 72 worlds: 6 D × 4 P × seeds 1, 17, 73 |
| Paired resource-pressure property check | R0/R1/R2, seeds 1, 17, 211 |
| Cold differential cases | 30/30 complete episode and successful exact policy hashes match |
| Differential coverage | All 24 D/P cells, seed 17; D5/P3/R1 and R2, seeds 17, 73, 211 |
| Live HTTP + actual request/validate CLI | Won and abandoned attempts passed; no active telemetry; terminal v3; no resume after finalization |
| CLI generate → qualify → solve → replay | D2/P3/R2 seed 17; won at turn 19; replay verified |
| Packaging | Frozen lock install, wheel and source distribution built |
| GitHub CI, including Docker build/smoke | [Passed full gate](https://github.com/petmal/NEXUS/actions/runs/37538266610) |
| Static checks | Changed solver/session/runner/tests pass Ruff; diff whitespace clean |
| Independent review | One cache-status inconsistency found, fixed, regression-tested |

Raw evidence: [validation summary](profiling/integration-validation.json),
[test output](profiling/integration-tests.txt), [30 differential records](profiling/integration-final).
Each differential record contains exact source fingerprints. The final run completed without source
drift. Policy comparison excludes only the diagnostic `visited_belief_nodes` count, which now
counts state/belief intervals. Complete episode hashes include all compiled episode data.

For the seed-17 D5/P3 anchor, physical optimum remains 14 and guaranteed policy cost 17; budgets
are 35, 25 and 17 for R0, R1 and R2. The v3 schema was separately published at
`15a252279da3da870fab354d92cb3e92726445d2`, and its remote bytes were verified against the local
schema. The published integration source tree was also compared byte for byte with the checkpoint.

## Limits and next use

Two pre-existing Pydantic fixture serializer warnings remain; they did not fail tests. There is no
configured repository-wide type-check gate. Differential runs used two independent case workers
for correctness throughput, so their times are not isolated latency measurements. The earlier
PoC's 3.66–3.87× improvement was relative to the already optimized combined control, not to the
original model-run service startup. Do not interpret it as a deployment SLA or multiply speedups
from separate experiments. See [archived performance evidence](solver-optimization-evidence.md).

Run the [ten-task model matrix](model-testing-matrix.md), or consume its
[JSON manifest](model-testing-matrix.json), with fresh paired private seeds and generous common
harness ceilings. Expected difficulty is ordinal and uncalibrated. Record startup separately from
play, and distinguish model/harness errors from mechanically failed episodes. No paid real-model
runs were performed in this integration.

The superseded diagnostics and PoC commits remain ancestors and have immutable archive links.
The separate `poc/theory-prior-axis` branch is intentionally retained for the next research phase.

CI tested code commit `46fd17091a411998758de54ff4f08bed515ca3f7`. Subsequent pre-merge
changes publish documentation and evidence only; production source remains byte-identical.
