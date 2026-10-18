# Complete-behavior transfer and coupled evidence pilot

Two opt-in families extend the existing feature branch. Existing families,
defaults, receipts, action semantics and saved episode formats remain supported.

- `coupled-transfer-v1`: infer a shared mechanism and program a seal that cancels
  its physical behavior in **all 486 public conditions**, rather than finding an
  additive treatment that happens to satisfy four excitations.
- `coupled-evidence-v1`: the same physical problem, with a reader contribution
  coupled to an upstream mechanism in the other context. Survey and reference
  measurements must be interpreted together. A reference carries useful physical
  information as well as information about the reader.

The player still takes specimens, configures and operates apparatuses, carries
the treated seal to the array, and finishes. The controller now accepts seven
selectors `[topology,f,g,h,changed,replacement,q]`. Any behaviorally equivalent
program wins; identifying the generator's preferred spelling is unnecessary.

## What qualification does and does not establish

The complete prior contains 5,184 physical programs, 5,016 physical behaviors,
and 15,552 combined program/reader worlds. No difficulty or solvability filter
silently narrows the public prior. All 20,736 calibrated/combined worlds were
solved through the live Session interface, with evidence-supported receipts,
advertised action bounds and exact replay. Independent scalar arithmetic and
every compiled policy branch were checked separately.

Every combined world retains incompatible mission targets under survey-only
or reference-only evidence. This is more than an offset ambiguity in selected
fixtures: 524/1,728 base worlds have different physical mechanisms with exactly
the same complete raw survey field, even with both offsets known. The selected
pilot fixtures rule out evidence-supported solutions from any two scalar
readings, including oracle-chosen readings. That per-fixture statement excludes
failed-finish feedback. Separate population bounds include binary rejection:
at most 234/5,184 uniform-prior physical worlds can be solved with three scalar
readings and three guesses under a generous information-capacity relaxation.

**The combined family is not uniformly harder along D.** Its reference exposes
upstream information: complete passive paired readings identify every joint
world. A single context also suffices for some worlds. Calibrated physical-only
passive obstruction therefore does not transfer to the combined family. The
preflight reports the actual observation closures for every row, alongside the
explicitly named physical-only rival check. This is a useful capability contrast,
not a monotone difficulty guarantee. A complete-prior passive-only public greedy
policy also has a ten-reading/37-action P1 upper bound, within the standard budget.
Consequently, skipping interventions in this family can be a sound strategy.

Neither family proves required adaptive rounds, cognitive depth, or an LLM
failure rate. Constructive fixed panels of 15 calibrated or 16 combined scalar
readings exist. The adaptive public witnesses use at most 9/10 readings. A
matched-pair strategy can instead recover each physical reading by subtraction;
its nine-query P1 upper is 52 actions, versus 37 for the combined joint policy.
These are algorithmic witnesses, not instructions requiring models to follow a
particular order or use enumeration. A clever shorter solution deserves credit.

The selective-revision PoC did **not** establish a required revision capability:
both contexts are available immediately, so early transition and stationary
joint inference defeat that interpretation. Revision was not integrated as a
claimed new difficulty feature. The negative result is preserved in the proof
and independent reviews. A concrete inherited-program candidate was checked for
all 576 possible truthful notebooks: each leaves only nine change hypotheses,
and triggering the change immediately permits a stationary policy with at most
three new-context readings and no old-context measurements.

## Recommended runs

Use `docs/transfer-model-matrix.json`, fresh model context per execution, no
external Python, and a harness allowance of at least 120 tool calls. All rows
use axes v2, P1/R1; rows 02–13 use experimental T3/D5. Row 01 is T0/D0.
Run 01–10 for an initial ten-execution screen; 11–13 complete the paired rivals
and are recommended for an interpretable full pilot. These are targeted cases,
not a representative population sample. Repeat failures before interpreting a
model difference. Do not put operator seeds, rivals or proof files in player
evidence.

| Run | Family | Seed | Budget | Public witness actions | Purpose / expected relative challenge |
| --- | --- | ---: | ---: | ---: | --- |
| 01 | evidence | 3550 | 11 | 5 | Execution control: valid program supplied; low |
| 02 | transfer | 3550 | 39 | 30 | Full transfer with genuine physical passive ambiguity; higher |
| 03 | evidence | 3550 | 43 | 34 | Same physical world, coupled raw evidence; different reasoning burden |
| 04 | evidence | 3550 | 49 | 34 | Exact science match to 03, six more actions; budget diagnostic |
| 05 | evidence | 3688 | 43 | 37 | Different physical target, identical full survey field to 03; higher |
| 06 | transfer | 3 | 39 | 30 | Serial topology, upstream replacement; calibrated comparison |
| 07 | evidence | 3 | 43 | 34 | Same physical world as 06; a single-context shortcut exists |
| 08 | evidence | 6943 | 43 | 34 | Parallel topology, upstream replacement; both contexts needed |
| 09 | evidence | 13847 | 43 | 34 | Coupled topology, downstream replacement; both contexts needed |
| 10 | evidence | 14255 | 43 | 34 | Survey-indistinguishable rival of 09; different required program |
| 11 | evidence | 3562 | 43 | 34 | Physical-passive rival of 03; raw references distinguish them |
| 12 | evidence | 7051 | 43 | 34 | Survey-indistinguishable rival of 08 |
| 13 | evidence | 864 | 43 | 34 | Survey-indistinguishable rival of 07 |

“Both contexts needed” here means even complete raw observations from either
context alone retain incompatible mission targets, as checked by preflight.
Relative difficulty is a hypothesis for real-model testing, not an empirical
ranking. In particular, 03 may outperform 02 if a model exploits the additional
upstream information efficiently. Report that as a finding, not an anomaly.

```bash
python scripts/preflight_transfer.py --output /tmp/transfer-preflight.json
nexus generate /tmp/transfer-03 --axis-version 2 \
  --science-family coupled-evidence-v1 --seed 3550 \
  --theory-level 3 --discovery-level 5 --planning-level 1 --resource-pressure 1
```

Use `--budget-profile diagnostic-plus6` for row 04. The corresponding environment
selectors are `NEXUS_SCIENCE_FAMILY`, `NEXUS_AXIS_VERSION`, and
`NEXUS_BUDGET_PROFILE`, with ordinary axis settings. The Docker build includes
the new preflight and matrix. Re-run preflight in the actual image before paid
model runs; source/package identities remain fail-closed.

## Player contract and post-run interpretation

The manifest and evidence are authoritative for machine names, selector ranges
and arity. Remove external prompt assumptions about a five/nine-field controller
or D-specific arity. Keep the generic instruction to read all evidence and use
the current manifest. This implementation does not change MindTrial.

The public files now explicitly separate physical response F, reader contribution
E, and raw display M. The complete primitive/graph prior appears before it is
needed. They explain the reference's zero physical response, matched preparation,
fixed reader strength, unknown offset, calibration scope, and the difference
between configure, preview and committed application. No provisional note is
presented as an authoritative law. See `transfer-player-walkthrough.md` for an
actual public-response example.

Post-run diagnostics retain supported/compatible/contradicted/ineligible
submissions, actual application versus physical eligibility, context/intervention
coverage, and measurements after a guaranteed program is known. Added private
logs report reference readings, remaining joint worlds, physical behavior
classes and compatible reader offsets. A reference can reduce physical
uncertainty; do not classify all reference readings as calibration overhead.
There are no live posterior, solver or mission-residual hints.

## Performance and resume points

Policy search is offline. The immutable policy is about 311 KB; generation
loads it instead of rebuilding a decision tree. Physical acceptance evaluates
only the submitted program against the actual program. Posterior tables reuse
upstream responses across physical and reader offsets; caches contain immutable
prior data or public masks, never session state.

Fresh-process medians on this shared host were about 29 ms calibrated / 43 ms
combined generation, and below 1 ms warm generation. First live solution plus
terminal diagnostics took about 1.6/3.2 seconds; peak RSS was about 61/76 MiB.
These are measurements of this host, not container guarantees. Detailed data:
`transfer-performance.json`. No GPU or multiprocessing dependency was added.

Durable checkpoints: `evidence-transfer-implementation.md`, the two independent
review reports, `evidence-transfer-proof.json`, `transfer-live-conformance.json`,
and `transfer-preflight.json`. `verify_transfer_live.py` supports bounded seed
ranges and source-bound restart checkpoints. No paid model runs were executed.
