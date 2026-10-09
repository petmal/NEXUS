# Scientific investigation pilot: ten runs per model

Use the feature-branch image with its OCI revision label and set
`NEXUS_AXIS_VERSION=2`. Other environment keys retain their names, but v2 changes
their documented meaning. See the adjacent JSON for exact environments. Keep the
same seeds across models. These are new experimental profiles, not calibrated
claims about frontier-model difficulty.

| Run | D/T/P/R | Seed | Expected relative difficulty /10 | Main question |
| --- | --- | ---: | ---: | --- |
| 01 | 2/1/1/1 | 7 | 2 | Combine independently measured properties under exact laws |
| 02 | 2/2/1/1 | 7 | 3 | Estimate a global correction and transfer across specimens |
| 03 | 2/3/1/1 | 7 | 4 | Identify structure while controlling material differences |
| 04 | 3/1/1/1 | 7 | 3 | Separate instrument offset from material state |
| 05 | 3/2/1/1 | 7 | 4 | Calibrate instrument and correction before interpretation |
| 06 | 3/3/1/1 | 7 | 5 | Infer missing structure through dependent measurements |
| 07 | 4/3/1/1 | 7 | 6 | Allocate experiments adaptively to the selected stock |
| 08 | 5/3/1/1 | 7 | 7 | Construct a decisive diagnostic specimen |
| 09 | 5/3/2/1 | 7 | 7 | Preserve scientific reasoning with modest added logistics |
| 10 | 5/3/1/1 | 23 | 7 | Check another latent world before drawing conclusions |

P/R are nonzero in every primary cell. Numeric D is structural, not an assured
ordinal rank: D2 targets both stocks while D3 targets one after instrument
calibration. Cross-T seeds do not isolate a pure theory effect because disclosed
law families differ. Runs08/09 hold the scientific truth fixed and change only P.
Runs07/08 hold the scientific truth fixed and change stock preparation availability.
Random per-task seeds are supported, but repeat fixed seeds for this initial paired
analysis. Two seeds do not estimate a population failure rate.

## Player setup

Give every model the same instruction: read the manifest and all listed evidence,
investigate the artificial world, configure its controller, finish, and return
the actual victory receipt. Do not include private files, seed values, reference
plans, certificate/proof reports or operator logs in the model's context. Normal
local Python computation is allowed; finite hypothesis enumeration is a valid method.

Use at least60 tool calls when actions are not batched, with a generous response
token/time allowance. Keep provider formatting and structured-output settings
fixed across cells. A text response format that is still passed to a structured
result parser can turn a live win into a harness Error; preserve both records.

The stable extra control is `configure`: for example
`{"type":"configure","machine":"controller","settings":[0,1,2,3,4]}`.
This illustrates syntax only, not a solution. The first value is the port, followed
by field responses in the public order. D2 requires nine values rather than five.
Stocks create specimens through ordinary `take`; use the returned specimen ID.

## Analysis priorities

1. Report official Pass/Fail/Error and audited live victory separately.
2. Compare first-submission correctness with eventual mission success. A recovered
   guess is a valid win, but weaker evidence of scientific inference.
3. Use terminal `target_classes_before_first_submission`, measurement counts,
   redundant measurements, port correctness and correct field values to distinguish
   inference, experiment choice, transfer, and controller mistakes.
4. Compare scientific measurements with the certified pre-submission information
   minimum; do not compare total actions to that measurement count. The physical
   policy bound is realizable, not an exact full-game minimax optimum.
5. Investigate movement/budget failures separately from theory errors. R1 adds8
   actions to a realizable worst-case policy. Do not start difficulty calibration at R2.
6. Inspect generation time and service readiness separately. Fast generation does
   not remove an external orchestrator's health-poll scheduling delay.

## Diagnostic controls, outside the ten primary runs

| Profile | Use when |
| --- | --- |
| D0/T0/P1/R1, seed7 | A model cannot use the controller or return its receipt |
| D0/T3/P0/R0, seed7 | Distinguish inference from experiment-selection difficulties |
| D5/T3/P0/R0, seed7 | Remove logistics and exhaustion after a primary failure |

Zero levels are controls, not the normal evaluation setting. R0 is truly unlimited
inside the game, with replenishable source stocks and repeatable machines. The
harness still limits execution. Eventual enumeration is possible in a finite family;
first-attempt correctness and evidence sufficiency must remain visible.

If all models solve the primary cells efficiently, retain that result. The next
scientific change should expand compositional relationship structure or add a
second linked investigation with a proven dependency—not simply tighten R.
