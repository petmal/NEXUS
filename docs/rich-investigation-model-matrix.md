# Coupled-network model pilot

Use the new image from `feat/theory-prior-axis`, with OCI revision recorded.
The [machine-readable matrix](rich-investigation-model-matrix.json) contains exact
environment settings for ten runs per model. All use axis version 2,
`NEXUS_SCIENCE_FAMILY=coupled-network-v1`, T3/P1/R1 and generation timing.
These are expected relative difficulties, not calibrated model scores.

| Runs | Seed | D4 expectation | D5 expectation |
|---|---:|---|---|
| 01–02 | 7 | Coupled relationship inference | Same truth, constructed experiments |
| 03–04 | 17 | Coupled relationship inference | Same truth, constructed experiments |
| 05–06 | 23 | Coupled relationship inference | Same truth, constructed experiments |
| 07–08 | 41 | Coupled relationship inference | Same truth, constructed experiments |
| 09–10 | 73 | Coupled relationship inference | Same truth, constructed experiments |

D4 is expected to exceed the old shared-response T3 task in inference difficulty;
D5 adds preparation planning and state tracking. D5 need not be harder on every
individual seed, and different seeds need not have the same realized measurement
count. The pairs preserve all hidden parameters and relationship choices. The
seeds span at least four distinct composed programs; no world is rejected during
generation based on whether it is convenient for the solver.

## Model instructions

Use the existing standalone integration/tool instructions, replacing the stale
sentence that direct mission probes remain legal with this task text:

> You are in a NEXUS laboratory. Read the manifest and all supplied evidence files
> to learn the controls, scientific prior, apparatus limits, and objective. Use
> observations and experiments to infer the field response, configure the
> controller, and finish successfully. The meter only measures its explicitly
> listed calibrated contexts; the controller has no preview channel. Track
> specimen state and remaining resources. Computation and finite hypothesis
> enumeration are allowed. Return the victory receipt only after NEXUS reports
> success.

If the harness executes each Python call in a fresh process, say so explicitly in
its tool description. Do not change stable error-status validation behavior. Do
not supply this operator matrix, hidden truth, private episodes, proof results,
reference plan, or terminal certificates to the model during play.

## Readout

Collect first-submission correctness, terminal target ambiguity, useful/redundant
measurements, invalid actions, preparation actions, total actions, tokens, model
latency, NEXUS generation stage timings, service readiness, and provider errors.
Keep Error separate from a played failure. Audit the action trace before attributing
a failure to scientific reasoning. Compare D4/D5 within model and seed; do not
infer a general success rate from only five worlds.

The certificate's five measurements are a *worst-case adaptive guarantee*, not a
requirement for each truth. Its physical action bound is a realizable reference
policy bound, not the optimum over every physical strategy. R1 adds eight actions
to that bound. A failed D5 case with exhausted resources may combine inefficient
preparation and inference; inspect the trace rather than assigning it solely to T.

If both levels remain at ceiling but models enumerate the grammar correctly, count
that as valid science. Use measurement efficiency and transfer to additional
structural seeds as evidence before enlarging the grammar again. If D4 succeeds
but D5 fails, focus next on construction/state tracking. If D4 fails with an
incorrect response despite ample actions, inspect hypothesis elimination and
generalization to field coordinates.

Optional controls outside the ten runs: D0/T0/P1/R1 for integration; D0/T3/P0/R0
for supplied-data inference; D5/T3/P0/R0 to separate preparation reasoning from
navigation and action pressure. Reuse a failed seed for the latter diagnostic.
T1/T2 are not live profiles in this family yet; use the PoC for their matched
mathematical comparisons. Existing shared-response profiles remain available.
