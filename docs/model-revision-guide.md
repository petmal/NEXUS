# Model-revision pilot: operator guide

This opt-in family asks the player to reconstruct a device from exact primitive
laws, rather than fit coefficients to supplied apparatus equations. A provisional
explanation is an experimental factor: it fits the archive but can need revision.
Earlier NEXUS families and the default selection remain available unchanged.

## What the player faces

The facility needs a replacement routing cartridge. Four reservoirs contain five
packets in total, initially `(2,1,1,1)`. A directed link moves
`min(source, 1 + destination % 2)` packets. Each of two modes applies two hidden
links in sequence. The second link uses the updated inventory. The display is
only `q0 % 3`, not the full state or a transfer amount.

The player knows these primitives, all 12 permitted directed links, the exact
four-link construction bounds, and two trusted measurements of isolated modes.
The reader runs any chosen word of 1–8 modes from the initial inventory and returns
one final display. It interrogates the reference device, never the player's build.
Some runs also provide a clearly provisional four-link explanation. The player
can test, revise or ignore it. There is no required experiment order.

For example, a player can predict the provisional model's response to `[0,1,0]`,
measure that word, and reject the explanation if the exact display disagrees.
They then seek a construction that preserves the trusted archive and explains the
new observation. Studying each mode in isolation does not suffice in the hard
selected worlds: their interaction changes the internal inventories. The player
must choose further discriminating words, install a compatible cartridge on the
actual carrier and finish. Acceptance requires the same displayed behavior for
**every finite mode history**, including histories longer than eight. Equivalent
hidden wirings win; matching only the two archived values is insufficient.

The primitive language is still bounded. It enforces conservation automatically;
this does not test discovery of conservation itself or unrestricted new science.
A competent enumeration or deduction strategy is legal. No Python or source is
provided to evaluated players.

## Qualified matrix

All rows use P0, R1, 64 NEXUS actions, 120 tool calls and 160 harness turns, with a
fresh context for each execution. Rows 02–09 are experimental T3/D5; row 01 is T0/D0.
Row 10 retains the prior stateful family at T3/D5 and the same P/R budget.

| Run | Seed | Condition | Minimum supported actions | Public reference actions | Expected relative challenge |
|---|---:|---|---:|---:|---|
| 01 | 5866 | Exact construction supplied | 4 | 4 | Execution control; easiest |
| 02 | 5866 | Primitives only | 12 | 16 | Hard mechanism reconstruction |
| 03 | 5866 | Same world + provisional model | 12 | 16 | Tests whether an inherited explanation helps or misleads |
| 04 | 6464 | Primitives only | 12 | 16 | Distinct hard mechanism |
| 05 | 6464 | Same world + provisional model | 12 | 16 | Matched revision condition |
| 06 | 5431 | Primitives only | 12 | 14 | Distinct hard mechanism |
| 07 | 5431 | Same world + provisional model | 12 | 14 | Matched revision condition |
| 08 | 1101 | Fourth mechanism + provisional model | 12 | 18 | Largest archive ambiguity; expected hardest structurally |
| 09 | 468 | One-reading shortcut available | 6 | 12 | Tests finding an easy solution; reference is not optimal |
| 10 | 229 | Prior stateful-discovery baseline | Not established here | 24 | Previously solved architecture; matched resource allowance |

These are structural expectations, not measured LLM rankings. A provisional model
could help, hinder or have no effect. More reference actions do not imply harder
reasoning. The new family's **universal constructive bound is 18 actions**, not its
minimum; T0's bound is four. The optimistic supported-action minimum is separately
proved for each selected new-family world. Do not divide by 12 and call it overhead
above a guaranteed worst-case optimum. Report both denominators with their scope.

The hard cases have no certificate from three legal readings, even if experiments
are chosen with knowledge of the eventual outcomes. All single-mode histories
still leave 39/39/42/77 behaviors respectively; finding the provisional model's
shortest counterexample still leaves a reading-only certificate of at least three
further observations. Failed submissions are also evidence: three readings plus
one or two rejected builds can suffice. Those mixed routes do not undercut the
12-action supported minimum. Four readings are not a mandatory live action ritual.
These checks rule out specific shallow shortcuts. They do not prove that a model's
internal reasoning cannot decompose the task in some clever way. No new calibrated
D tier or predicted failure percentage is claimed.

## Build and preflight

From the feature branch root, in a POSIX shell (replace `podman` with `docker` if
preferred):

```sh
podman build --build-arg VCS_REF="$(git rev-parse HEAD)" -t nexus:model-revision-v1 .
podman run --rm --entrypoint python nexus:model-revision-v1 scripts/preflight_revision.py
```

PowerShell accepts the same build command and substitution. Require a successful
preflight before spending model budget. The image normalizes Windows source line
endings without bypassing qualification. Inspect the OCI revision label if an
unexpected image appears. Use the same tag in tool, service and validator entries.

Use `examples/mindtrial/nexus-revision-config.yaml` together with
`examples/mindtrial/nexus-revision-tasks.yaml`. Provider/model settings are retained
from the earlier supplied operator config; insert your credentials locally and
choose which models to enable. There are no embedded credentials. The service maps
`ontology-options` to `NEXUS_ONTOLOGY_OPTIONS`, so matched guidance is generated in
the image, not injected as a task prompt hint. Do not supply private preflight
reports, seeds, source or this operator guide to evaluated agents.

Locally, the reproducible proof and matrix command is:

```sh
uv run --frozen python scripts/preflight_revision.py --output /tmp/revision-preflight.json
```

The report checkpoints every cell and binds source and matrix identity. A proof
limit, mismatched pair, shallow hard cell, equivalent mechanism contrast or failed
live replay blocks the run. Generic `nexus qualify` checks family conformance and
solvability; it does **not** replace this stronger selected-matrix admission.

## Read the results correctly

Collect the JSON result, full tool history, service diagnostic output, model
reasoning/token totals where available, exact model settings, image revision and
preflight report. Keep successful live escape, evidence support, final receipt
formatting and provider interruption separate.

Extended diagnostics now end with a separate `NEXUS operator summary:` JSON line
bounded to 4096 bytes, after the detailed history. It survives the tested 8192-byte
stderr-tail capture. Existing detailed events remain available. Nothing is added
to active player responses. `noninformative_*` means no candidate elimination;
a committed reading can still perform necessary control or preparation. It is
not a wasted-action count. Legacy action counts are taken from the canonical trace.

NEXUS cannot see the provider's raw final response or MindTrial's parser outcome.
Those fields say `not_observed_by_service`. For another receipt failure, preserve
raw provider completion, normalized final text and validator input in MindTrial;
do not loosen the exact receipt requirement. Provider failures are not game failures.

Primary comparisons: paired 02/03, 04/05 and 06/07; shortcut detection in 09; execution
control in 01; then new-family behavior against 10. Report success and evidence
support before action/token overhead. Repeat matched pairs before interpreting one
lucky or unlucky run. Keep the resource allowance fixed while judging this change.
