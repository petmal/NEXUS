# Deep investigation model pilot

Ten runs per model; exact environment blocks are in [repair-model-matrix.json](repair-model-matrix.json).
Use the final feature image and record its OCI revision. The default scientific
family remains unchanged; repair is opt-in. No real-model results are claimed.

| Run | Family | T | D | P | Seed | Purpose / expected relative challenge |
|---|---|---:|---:|---:|---:|---|
| 1 | Causal | 0 | 0 | 1 | 7 | Control: direct supplied knowledge and correct execution |
| 2 | Causal | 1 | 1 | 1 | 7 | Low: exact-law inference |
| 3 | Causal | 2 | 2 | 1 | 7 | Medium: known-form correction |
| 4 | Causal | 3 | 5 | 1 | 7 | Previous-family reasoning anchor |
| 5 | Repair | 3 | 5 | 0 | 3943 | Higher intended dependence: three feedback rounds; P0/P1 pair isolates transport |
| 6 | Repair | 3 | 5 | 1 | 3943 | Higher intended dependence: three feedback rounds; P0/P1 pair isolates transport |
| 7 | Repair | 3 | 5 | 0 | 3479 | Higher intended dependence: three feedback rounds; P0/P1 pair isolates transport |
| 8 | Repair | 3 | 5 | 1 | 3479 | Higher intended dependence: three feedback rounds; P0/P1 pair isolates transport |
| 9 | Repair | 3 | 5 | 0 | 5835 | Higher intended dependence: three feedback rounds; P0/P1 pair isolates transport |
| 10 | Repair | 3 | 5 | 1 | 5835 | Higher intended dependence: three feedback rounds; P0/P1 pair isolates transport |

All rows use axes-v2/R1. Causal is `causal-mechanisms-v1`; repair is
`coupled-repair-v1`. Expected rankings are hypotheses. Cross-family comparisons
change ontology and prior, not only difficulty. The repair P0/P1 pairs have the
same hidden law and same scientific depth; P1 adds one required move and one
action to the budget. The three repair seeds were uniformly drawn before examining
their truths. Three paired worlds are a pilot, not a precise failure-rate estimate.
For a population study, sample fresh indices uniformly from 0..7202, independently
within each fixed public configuration; record them privately and pair across models.

## MindTrial configuration

Use `serve-session` with the existing NEXUS transport and the environment block.
One persistent, non-resettable session per attempt. The multi-session server rejects
this family because another attempt on the same hidden world invalidates its bound.
Keep external Python, filesystem/source access, and other computation tools disabled
for this pilot. Give at least 80 harness tool calls; ordinary reads are free in-world.
Do not put the private seed, certificate, laws or policy implementation in the prompt.
Provider/harness failures should be reported separately; a retry must be a separately
labelled attempt and is excluded from the strict one-attempt claim.

Suggested family-neutral task text:

> Investigate the current artificial world. Begin with manifest and observe, then
> read every listed evidence file. Use the public laws and action contract to plan
> experiments and satisfy the exact mission. Use returned specimen IDs. Apparatus
> configuration and specimen operation may have different effects; follow the
> disclosed semantics. Finite hypothesis enumeration is valid. Use NEXUS for every
> in-world action. Finish successfully and return exactly the actual victory receipt.

Remove assumptions about a `controller`, port-first ordering, five/nine values,
previews that are always illegal, or prediction-only goals. Repair uses a unique
physical seal specimen. Configuring its doser alone does not apply the treatment.
This is documented in its manifest/evidence, not a hidden tool-syntax trap.

## What to score

Report victory, first-finish correctness, target classes before first finish,
informative/redundant measurements, wrong preparation/operation, invalid requests,
failed finishes, remaining budget, and actual receipt extraction. Keep science,
logistics, action semantics, provider errors and parser errors distinct. Terminal
mission telemetry and operator diagnostics contain these signals; do not expose
them during active play. Preserve the public transcript and accepted replay trace.

Strict profile: T3/D5/P0-or-P1/R1, budgets 17/18, public witness costs 14/15. One
complete wrong repair after acquisition/transport can be recovered. Any extra
budget, prepared initial sample, hint or same-world reset requires a new claim.
At one extra action a shallow policy becomes perfect. The proven <=3/7 success
bound concerns policies with at most two feedback rounds over the stated prior;
it is **not** a predicted LLM failure rate. Models using three or more rounds may
all succeed. Do not classify a lucky shallow win as improper play.

The local-regime variant is intentionally excluded: its early-trigger shortcut
removed the intended revision requirement. See [repair-local-regime-poc.json](repair-local-regime-poc.json).
