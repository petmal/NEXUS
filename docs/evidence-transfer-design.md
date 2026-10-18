# Coupled transfer and evidence validity: system design

Status: implemented and release-validated; empirical difficulty uncalibrated, 18 October 2026. Approved baseline is feature branch
`feat/theory-prior-axis` at `b36703d868f83882543f6a77a6b5ce4b9f7e3f38`,
confirmed against GitHub PR 6. Existing families and defaults remain supported.

## Purpose and authority

The user approved implementing the recommended T/D extensions: consequential
coupled transfer, uncertainty about how evidence is produced, improved coverage
and qualification, and a selective-revision PoC with integration conditional on
its gate. The walkthrough feedback requires self-contained public contracts:
explicit exhaustive priors, raw versus physical response, reference guarantees,
calibration scope, and provisional versus authoritative statements.

Latest evidence: Gemini seed 438 failed all three new 30-action repetitions and
won all three 36-action repetitions. Seed 493 can have a common accepted repair
before all laws are identified. These motivate consequential goals and new
uncertainty, not tighter budgets or forced scientific rituals. No model failure
rate or cognitive-depth theorem is promised.

## Qualified construction

Reuse the trusted three-gate compositional grammar as a scientific building
block, but create separate versioned families. Keep every one-module replacement
world (1,728 candidates), with no solvability filtering, and an independent
physical output offset q (three values, hence 5,184 programs). A seal is programmed
with a bounded seven-selector countermechanism. The goal is zero physical residual
over both contexts, all ternary inputs and both internal trim selectors. Thus
different world programs that have the same complete behavior are accepted as
equivalent. The old four-point scalar-repair family is unchanged.

The calibrated `coupled-transfer-v1` control reads physical response directly.
The combined `coupled-evidence-v1` adds a raw reader:

```
physical current-context response = n3 + q
survey display = physical current-context response + reader contribution
reader contribution = reader_offset + companion-context upstream n2
reference display = reader contribution
```

All arithmetic is modulo 3; reader strength is the public constant 1, and
reader_offset is 0, 1 or 2. A reference cancels its current physical output
while preserving the companion upstream path.
Shared preparation, context and trim settings are essential to transferring the
reference. The public contract states these semantics and parameter stability;
it does not disclose the selected offsets or mechanisms. Matched readings
subtract exactly, but cheaper reference-only, survey-only and passive policies
are audited. Full survey-only and reference-only closures retain incompatible
physical targets in every joint world. Beyond scalar offset ambiguity, 524 of
1,728 base worlds retain structural survey ambiguity, including 480 nonlinear
worlds. Independent reviewer and standalone PoC reproduce these counts.

Implementation review exposed a separate limitation: complete paired passive
raw observations identify every combined world, and one context suffices in
some worlds. These upstream observations are richer than physical-only data.
Therefore calibrated physical-only intervention/context obstructions must not
be transferred to the combined variant. The final matrix reports both scopes;
combined evidence is an orthogonal capability contrast, not universally stronger
D. A passive-only greedy witness also uses at most ten readings. Three tested
delta-reader refinements restore passive obstruction but lose all structural
survey ambiguity, so they were rejected. No stronger depth claim is attached.

The rejected original gain/final-response reader is preserved as a negative
result in the independent review. An independent known-feature calibration
variant was also rejected as merely a short separable calibration prefix.

All experiments, including mission conditions, remain legal from the start.
There are no stage locks. Physical preparation is ordinary configure/operate;
probe is immutable. Only applying a program to the carried seal and finishing in
the exit room can win. Wrong eligible finishes provide binary evidence. Public
errors and preview results must not reveal unmodeled truth.

## Acceptance gates

1. Independent scalar oracle and production semantics agree over the complete
   finite grammar, legal queries, and mission acceptance.
2. Every admitted world has a public-information winning policy, replayable in
   the live engine. Equivalent counterprograms count as valid.
3. Quantify complete passive, single-context, survey-only and reference-only
   closures; selected strong fixtures must retain incompatible required repairs
   under the claimed restrictions. Report scope and actual sampler explicitly.
4. Mission ablations demonstrate that mixed inputs/contexts/interventions are
   consequential; no universal program or low-cost guessed submission sequence
   silently defeats the advertised bounds.
5. Compare policy cost with a fixed-panel/pairing baseline. No adaptive-round or
   cognitive-depth claim follows from a greedy witness or longer preparation.
6. Standard and generous resource controls have explicit executable bounds and
   slack; all scientific fields stay paired. P0/P1 only initially.
7. Public evidence states complete grammar, types, controls, reference scope,
   raw-readout semantics, and exact mission. Terminal diagnostics remain private.
8. Selected fixture matrix varies graph, primitive, replacement location and
   instrument nuisance. Include equivalent rivals and control ablations.

## Revision PoC

Evaluate a provisional inherited program/notebook and localized model change
against fresh-start, final-context-only and anticipatory policies. Preserve
unaffected mission capabilities. Do not force a wrong belief or fixed order.
If the construction is equivalent to stationary joint inference, or adds only
relearning costs, record that result and withhold a required-revision claim.
Public provisional evidence must condition the inference prior if it carries
truthful additional information; arbitrary narrative cannot be treated as data.

## Architecture, performance and boundaries

Use existing ontology/catalog, payload schemas, runtime, public belief,
AppliedTreatmentTracker, qualification and Session seams. Keep family logic out
of the canonical engine. Prefer immutable public preparation history plus
immutable private laws. Maintain raw/physical projections and data-only code.

Compile seed-independent primitive/response tables and observation partitions
once. Store an immutable, integrity-checked offline public policy (about 311 KB);
generation loads it without policy search. Preserve joint posterior correlations and equivalence-class probability
mass. Bound caches and offline searches; timeouts mean unknown. Measure cold
generation and peak memory before adopting large artifacts or parallelization.
Do not blindly raise generic minimax limits; complete-behavior targets can use
the existing target-equivalence backend or a narrow factored representation.

No MindTrial change, paid model call, main merge, external player Python,
stochastic noise, broad toolchain migration or third-party plugin loader.
The walkthrough is documentation inspiration, not the complete hard family.

## Decision ledger

- Preserve old behavior and version new families: compatibility and matched
  controls are user requirements. Revisit only for a demonstrated shared bug.
- Full behavioral goal rather than a canonical hidden program: unresolved
  mechanisms must matter, but equivalent theories must remain valid.
- Use companion upstream cross-talk, not the rejected companion final response.
  The reference leaves 24–288 physical targets; survey structural ambiguity is
  present across all topologies and replacement positions. Do not claim every
  fixture needs intervention or that calibration must occur first.
- Offline greedy witnesses take at most 9 calibrated or 10 combined readings.
  These are upper bounds, not optimality or difficulty claims. R1 has six spare
  actions; diagnostic-plus6 adds six more without changing scientific fields.
- Keep revision gated: earlier early-transition shortcut is a known negative
  result. A revised story is not evidence of a new capability requirement.
- Follow existing pytest/Ruff/Pyright and source-binding conventions. This task
  does not migrate the mature project to a different checker/coverage framework.
