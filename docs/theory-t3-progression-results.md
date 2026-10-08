# T3 runtime, evidence optimization, and cumulative discovery

## Delivered behavior

T3 is integrated into `generate_episode`, qualification, CLI and `NEXUS_THEORY_LEVEL`.
Supported profiles: **D2/P0–P3/R0–R2**. Other D/T3 combinations reject explicitly.
T0/T1/T2 causal worlds and ordinary actions are preserved. Terminal performance now uses
v6 with T=0–3; historical schema files are unchanged. The immutable schema commit is
`50ea40636bf46313fe5eef46973527dec097d17a`.

The T3 family independently selects add-one, add-two or multiply-two modulo 11 for
each of six shape/parity cells. It supplies no effective baseline; the player infers
the missing operator relationship within that complete bounded structural prior.
It does not claim open-ended scientific theory synthesis or greater difficulty than T1.

A truthful calibration on another shape leaves 243 of 729 full laws. All available
artifacts retain the same shape, so nine representatives cover reachable behavior,
with multiplicity 27. Five classes / 135 full laws are physically viable. One probe
is sufficient for a guaranteed causal policy. Qualification reconstructs this argument
from the public files, checks the actual full law, and validates ordinary-engine
policy cost and metadata. P3's identical-context cargo preserves the reduction.
The generator rejects unsupported projection conditions instead of silently pruning.

Counts have explicit units: before-evidence metadata counts 729 full laws;
after-evidence and per-machine metadata count nine reachable classes. Qualification
metrics retain the 243 full survivors and multiplicity 27. The calibration alone does
not reduce the prior to nine laws.

## High-value optimization

Evidence search previously interpreted identical rule/context combinations for every
trial subset. It now computes mission signatures once per search and reuses them,
plus a cached index of the fixed catalogue. Tie-breaking and selected evidence remain
unchanged. There is no growing cache of random episode seeds.

Cold local D3/P2/R0/T1 generation: Seed1 **4.711→4.020 s (14.7%)**; Seed17
**4.152→2.773 s (33.2%)**. Physical-world hashes match and both policy sets replayed.
See [optimization evidence](theory-t3-optimization-results.md). These two samples are
not a universal speedup estimate. Production remains sequential: T2/T3 are already
cheap, and prior parallel-worker experiments regressed under concurrent episodes.
MindTrial's readiness delay is outside this NEXUS change.

New operator-only timing stages cover mission signatures and T3 family, topology,
projection, physical solve and policy solve. Existing final generation summaries
retain their wall/process-CPU stage accounting. No diagnostic payload enters active play.

## Cumulative progression PoC

Run `uv run python scripts/theory_progression_poc.py`. It writes fingerprinted,
atomic, resumable reports separating `public_problem` from `judge_only` truth and proofs.
Never give the latter block to an evaluated model. The script refuses Python `-O` so
proof checks cannot silently disappear.

A concrete Seed17 fixture, all arithmetic modulo 11:

1. T1 supplies `a=x+2`, `b=3a`, `q=b−6`; composing them gives `q=3x`.
2. T2 supplies `u=q+c`, with unknown `c∈{2,3}`. Calibration measures `u` at `x=0`.
3. T3 leaves the relationship `y=u+5` versus `y=−u` unknown. A second experiment
   measures `y` at `x=2`; the task predicts `y` at the unmeasured `x=6`.

| Correction / relationship | Calibration | Relationship observation | Held-out prediction |
|---|---:|---:|---:|
| c=2, y=u+5 | 2 | 2 | 3 |
| c=2, y=−u | 2 | 3 | 2 |
| c=3, y=u+5 | 3 | 3 | 4 |
| c=3, y=−u | 3 | 2 | 1 |

The relationship observation has different interpretations depending on the correction.
For every truth, both observations identify the answer; either alone leaves two possible
predictions. A wrong correction selects the wrong relationship and wrong prediction.
Thus the dependency is proved by information, not merely declared in a graph.

Controls:

- Independent: the relationship experiment uses a disclosed input u, so its interpretation
  does not depend on the unknown correction. Both controls still require two measurements
  overall, controlling for simple sequence length / information volume.
- Known correction: supply the correct intermediate result; one measurement remains.
- Direct target: allowing a measurement at the prediction context reduces the task to one
  measurement, exposing a bypass. The PoC's public experiment list excludes that context.

Five checked-in fixtures cover 20 truths. Independent review also executed 1,000 seeds
successfully. This is an information-only experiment: no model performance claim, forced
chronological discovery order, or production progression mode. A model may reason jointly
or collect observations in either order. T1 is an algebraic composition prerequisite here,
not an independently uncertain stage or a proof that a model performed that derivation.

## Groundwork and future integration

Two small, exercised components are included:

- `models/theory.py`: serializable immutable theory-stage/dependency records, rejecting
  duplicate IDs, missing prerequisites and cycles.
- `solver/finite_experiments.py`: exact finite belief filtering, held-out predictive
  ambiguity and minimum worst-case measurement counts. Inputs are complete aligned
  hypothesis/experiment tables with explicit size limits. It does not model navigation.

The current PoC consumes both. No unused runtime setting or new D semantic is introduced.
Future physical integration must bind measurements to ordinary actions and reachable
contexts, ensure the target cannot be directly probed to bypass the chain, preserve a
complete public prior, and verify every viable law through the real engine. Only then
assign a D level based on proven experiment requirements. Keep dependent/independent and
known-intermediate controls; add navigation only after the theory distinction is measured.

## Model matrix and validation

The [ten-run matrix](theory-reasoning-model-matrix.md) uses fresh fixed Seeds7/23,
R0 and mostly P0: six D2/T1–T3 cells, two P2 sensitivity controls, and two D3/T1 controls.
All ten prequalified with **60 viable policy replays**. T2/T3 are separate world families;
cross-T equal seeds are not a physically paired causal estimate. The matrix does not
pretend the progression PoC is already a playable runtime mode.

Focused gates: 44 optimization/theory tests; 28 structural tests; 21 progression/schema/
protocol tests; final ten-test progression gate after review hardening. The structural
oracle compares 21,384 complete value/phase evaluations and replays all 270 viable full
laws across Seeds1/17. Every P/R combination is tested. A further 16 T3 generation cases
(all accepted) replayed 80 viable paths; median local generation 0.087 s, range and full
records in `docs/profiling/t3-runtime-sweep`. Concurrent test activity means these are
feasibility timings, not isolated speed benchmarks.

All 70 sessions from the preceding real-model run replayed again against the updated
source with zero discrepancies: 1,690 action responses, 81 manifests, 82 standalone
observations and 229 evidence responses. CLI T3/D2/P3/R2 generate→qualify→solve→replay
passed. Lockfile, compile and diff checks passed. Independent review found no blocker;
its `-O` proof-report safeguard was applied and regression tested.

Full suite: **255 passed in 230.39 s**, with two existing Pydantic enum warnings.
The later-added optimized-Python test passed in the final ten-test progression run;
all **256 current tests** are covered. Validation and commit mapping are recorded in
`theory-t3-progression-validation.json` and the execution checkpoint. No paid model calls
were made. Docker/Podman are unavailable locally; CI includes T3 CLI/container smoke.
Existing missing Ruff/ty/basedpyright/coverage gates remain a separate repository tooling
gap; this feature did not migrate the project's toolchain.
