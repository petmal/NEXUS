# Resonant-network pilot: ten runs per model

Build `feat/theory-prior-axis` and record its OCI revision. Use axes2,
`NEXUS_SCIENCE_FAMILY=resonant-network-v1`, T3/P1/R1. Keep the no-external-Python
condition, model reasoning/output settings, and tool contract consistent with
the preceding coupled-network run. This is a proposed real-model matrix;
only deterministic reference policies have been run in this implementation.

| Runs | Seed | D4 expected challenge | D5 expected challenge |
|---|---:|---|---|
| 01–02 | 7 | Select calibration/response experiments; combine laws | Same laws plus mixed preparation and instrument state |
| 03–04 | 17 | Same scientific demands, different hidden parameters | Same scientific demands plus construction |
| 05–06 | 23 | Same scientific demands, different hidden parameters | Same scientific demands plus construction |
| 07–08 | 41 | Same demands; shorter reference path on this seed | Additional construction; shorter reference path |
| 09–10 | 73 | Same demands; shorter response witness | Additional construction and state tracking |

Expect more work than the prior coupled family and potentially more mistakes in
measurement selection, instrument configuration, or combining the laws. D5 adds
construction difficulty; it does not increase the hidden theory prior. No numeric
failure forecast or monotonic per-seed model ranking is established. Calibration
itself has a two-reading solution, and legal fitting shortcuts remain; top models
may still solve every task. Reuse the previous coupled results as a separately
labelled baseline; downstream G is paired by seed, but the new H and H+G mission
mean this is a feature comparison, not a single-variable causal ablation.

Common environment:

```yaml
NEXUS_AXIS_VERSION: "2"
NEXUS_SCIENCE_FAMILY: resonant-network-v1
NEXUS_THEORY_LEVEL: "3"
NEXUS_PLANNING_LEVEL: "1"
NEXUS_RESOURCE_PRESSURE: "1"
NEXUS_GENERATION_TIMING: "true"
# Set NEXUS_DISCOVERY_LEVEL to4 or5 and NEXUS_SEED to the table value.
```

The [JSON matrix](resonant-network-model-matrix.json) contains all ten explicit
environment blocks. D4's certified policy bound is34 actions with budget42;
D5's is51 with budget59. Set a harness tool-call limit that does not bind before
the game budget plus manifest/evidence/status overhead; at least96 calls is a
reasonable pilot setting. Keep it consistent across compared models, and record
it. Do not silently increase only a struggling model's output allowance.

Use a neutral task prompt:

> Read the manifest and every evidence file. Investigate the artificial world
> using the NEXUS interface, follow its current apparatus and action contracts,
> configure the controller to satisfy the exact goal, and finish successfully.
> Track specimen state, instrument settings, and the remaining budget. Finite
> hypothesis enumeration is allowed. Return only the actual victory receipt.

The tool description must allow `configure` on the instrument named by the
manifest; do not retain wording that says configure is only for the controller.
In this family `configure meter settings:[z]` is legal, consumes an action, and
provides no correctness feedback. Let the public evidence explain the science;
do not give models this operator matrix, proof witnesses, or reference sequences.

Record Pass/Failed/Error separately. Inspect first-submission correctness and
evidence sufficiency, calibration and meter calls, no-signal outcomes, meter
settings, preparation mistakes, measurements after target identification, output
limits, and parser errors. The new operator log `resonance_terminal` reports
calibration/no-signal counts and post-identification measurements only at terminal
summary time. Generation logs separate base witness, factor prior, composed
witness and evidence construction. R0/P0 remain diagnostics, not the primary eval.
