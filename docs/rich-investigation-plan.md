# Rich scientific investigation: design and execution checkpoint

## Objective and authority

User approved work on 9 October 2026 to increase T/D difficulty through richer
worlds and relationships, holding P/R moderate. Latest run: 103 legitimate
first-submission wins, one provider Error, no replay discrepancies. The v2
shared-response family remains a reproducible baseline. No paid model calls,
no public MindTrial changes, no main-branch changes.

## System design

The next family must make causal relationships interact rather than merely expand
coefficient ranges. T1 provides exact mechanisms while specimen/apparatus state
may require measurement. T2 specifies correction forms with unknown parameters.
T3 withholds bounded relationship structure, including where interactions occur.
D describes evidence/experiment dependencies and construction, not a generic
scalar increase of prior cardinality. Public controls and complete bounded priors
remain explicit. Exact prediction equivalence, not a preferred symbolic spelling,
defines scientific success.

Candidate: a two-input coupled finite-field response network with composed
relationship nodes and noncommuting specimen-preparation operations. Bench
observations and field targets must differ. More than one observable relationship
must participate in the target; no reference specimen may universally isolate
all unknowns through the old zero/one/two recipe.

### Acceptance and falsification gates

- Every admitted world has a valid exact public-information solution; no hidden
  truth selection by solvability or unannounced prior truncation.
- Independently evaluated expression truth tables agree with the runtime semantics.
- Exhibit easy-experiment-equivalent worlds with different held-out predictions.
- Measure a fixed-reference recipe, low-degree interpolation/union-basis fitting,
  fixed exhaustive experiments, random experiments and an exact adaptive policy.
- Prove a meaningful adaptive advantage before labeling a profile D4. A large
  hypothesis count alone is insufficient.
- D5 must require a mixed preparation route, not merely additional applications
  of one preparation operator. Prove a target ambiguity if mixed routes are removed.
- Disclose prediction-equivalent alternatives honestly. Do not require identifying
  unidentifiable causal structure or claim a model difficulty improvement before
  real-model testing.
- Bound generation work and record prior construction, exact policy, physical
  witnesses, and qualification timings separately.

### Compatibility

Preserve axis-version 1 and the existing axis-version 2 shared-response family.
Add an explicit opt-in family only after the proof gates pass. Preserve ordinary
actions, terminal receipts, unlimited R0 source stocks, and terminal-only private
telemetry. No automatic change to validation on Error, rate limits, or Python tools.
Zero levels remain diagnostic controls; the primary pilot will use nonzero axes.

## Implementation phases

1. **Complete:** construct a runnable mathematical PoC; counterexample/shortcut
   checks; fresh independent design review. Scripts and machine-readable proof
   results become durable review artifacts.
2. **Complete:** the family passed; extract only exercised declarative expression/preparation
   primitives and integrate generation, runtime, evidence, qualification and
   diagnostics behind explicit family selection. If it fails, record the reason
   and revise the mathematical family before touching production behavior.
3. **Complete:** targeted semantic tests, old-family baseline compatibility, bounded seed sweep,
   independent integrated review and final regression. Publish focused commits to
   the existing private feature branch with the expected-head lease.
4. **Complete:** produce a ten-cell structural-seed pilot and revised prompt removing the stale
   claim that direct mission previews are legal. No paid evaluations in this task.

## Resume state

Baseline local commit: `51bf3e57510f86ea148ef7868941059f09449a89`.
Baseline published commit: `f1de5d663f6d72331b42627f3611334a0162d62e`.
Matching tree: `3bd27ac4ceb807b347152225b4b13823909be9b7`.
Branch: `feat/theory-prior-axis`, PR #6, base `feat/epistemic-calibration`.
Local/imported and remote ancestry differ: publish verified trees through Git data
with an expected-head lease; never force-push the imported local history.

Decision: retain simple-family successes as a baseline rather than tightening R.
Reason: latest models recover the small separable family reliably; changing R
would predominantly measure extra work. Invalidate only if future task goals
explicitly prioritize resource efficiency over scientific reasoning.

## Frozen PoC decision

Use GF(7), stable specimen properties a,b and correction coefficients c,d in1..3.
Independent gates produce u from {x+a, ax, x²+a}, v from {y+b, by, y²+b}, and
Y from {uv+cu²+dv², (u+c)v²+du, (u²+c)v+duv}. This is composition of three
independent mechanism choices, not selection of a single prewritten full law.
T1 supplies gates and c=d=1; T2 supplies gates with unknown c,d; T3 leaves all
three gates unknown. T1/T2 are PoC ablation controls in this first release.

Exact controls: T1 9 worlds, adaptive2/fixed2; T2 81 worlds, adaptive3/fixed4;
T3 2,187 worlds, 1,175 prediction classes, adaptive5/fixed8. All12bench measurements
identify the four field predictions. Axes+diagonal leave54 ambiguous transcripts.
A union-polynomial null witness proves unconstrained basis fitting insufficient.
Independent reviewer confirmed matrix counts and exact optimized costs against
small arbitrary exhaustive oracles.

Live opt-in scope: T3/D4 and T3/D5, with D0/T0 and D0/T3 diagnostics. Do not
relabel an identical T3 experiment problem as D3 simply to fill the grid. More
T/D cells require their own semantic proof. The former shared-response family
and its supported grid remain unchanged.

D4 supplies all calibrated preparations; D5 supplies only (0,0), with public
noncommuting A:(x,y)->(x+1,y), B:(x,y)->(x,y+x+1), modulo7. Both branches alone
only yield axes; jointly they reach all49contexts. The two levels share truth and
bench/field laws. Only12bench coordinates are calibrated; other points are legal
preparation states, not legal meter contexts. Field coordinates are not measurable.

Proof-directed optimization: target-mask lookup, fanout lower bounds, duplicate
partitions and incumbent pruning for adaptive minimax; counterexample-derived
pair-separator constraints for minimum fixed sets. Preserve100,000belief guard.
Both algorithms require independent arbitrary-problem oracle tests.

## Validation checkpoint

- Full regression: 372 passed, three warnings, 283.14 seconds, three stress seeds.
- All 2,187 prior worlds physically replayed for both D4/P1/R1 and D5/P2/R2.
- 24 D/P/R reference profiles pass, as do D0/T0,T3 controls.
- Independent review findings fixed: initial stock/sample family consistency,
  symmetric runtime guard, schema/prior validation before truth evaluation.
- Previous real-model artifact replay: 104 sessions, zero mismatches.
- CLI D5/T3/P1/R1 seed17 generate/qualify/solve/replay passed.
- Final focused gate: 45 passed, two slow cases deselected; final observer/family
  boundary check: two passed. Ten fresh-process pilot cases won with reference
  policies; cold generation 0.791–0.985 seconds, warm 0.272–0.341 seconds. Recorded
  results and the paired pilot are in `rich-investigation-results.md` and
  `rich-investigation-model-matrix.{md,json}`.

Reproduction commands (from repository root):

```bash
uv sync --frozen --all-extras
uv run python scripts/coupled_network_poc.py --out /tmp/coupled-proof.json
NEXUS_STRESS_SEED_COUNT=3 uv run pytest -q --durations=12
uv run python scripts/scientific_investigation_benchmark.py \
  --family coupled-network-v1 --out /tmp/coupled-benchmark.json
uv run nexus generate /tmp/coupled --axis-version 2 \
  --science-family coupled-network-v1 --seed 17 --discovery-level 5 \
  --theory-level 3 --planning-level 1 --resource-pressure 1
uv run nexus qualify /tmp/coupled/private.json
uv run nexus solve /tmp/coupled/private.json --trace-out /tmp/coupled/trace.jsonl
uv run nexus replay /tmp/coupled/private.json /tmp/coupled/trace.jsonl
```

No model/API calls are needed to resume these checks. Do not rerun completed
expensive checks unless code changes affect their scope. Do not infer quota-reset
timing; the task uses deterministic local checks and no paid model evaluation.

## Commit mapping and next action

Implementation local commit: `9adcadb9325eb96b53f32823cb054154427dbd00`.
Implementation remote commit: `3322db18c8b8cad185c448592c991c3773e431ba`.
Verified implementation tree: `58a54e3eebe092472d2c65273319397952d8bb4f`.
The documentation/benchmark follow-up is published after that implementation
commit; PR #6 records the final remote head and matching final tree.

All local gates are complete. Remaining empirical action: build the published
feature head and run the paired ten-cell matrix on real models, then audit
inference versus preparation errors. T1/T2 live integration and larger grammars
remain follow-up decisions, not silently supported profiles. CI status belongs
to the exact remote head; do not claim final-head CI from an earlier commit.
