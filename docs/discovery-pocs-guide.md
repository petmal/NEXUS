# Discovery PoCs: operator guide

Both families are opt-in plugins. Existing families/defaults are preserved. They test
different reasoning mechanisms with ample actions; neither is a proven deep tier or
a prediction that models will fail. Do not include this guide, source, proof reports,
seeds, or preflight output in the player's context.

## Ten-execution matrix

All rows use P0, NEXUS-only tools, fresh model context, 120 tool calls and 160 harness
turns. R1 has 64 environment actions; R0 removes that limit but keeps the same harness
caps. No external Python. These are ten executions **per enabled model**.

| Run | Family | Seed | T/D/R | What changes | Expected relative difficulty | Reference actions | Minimum supporting readings |
|---|---|---:|---|---|---|---:|---:|
| 01 | Memory | 305 | 0/0/1 | Complete program supplied | Low; execution control | 4 | 0 |
| 02 | Memory | 305 | 2/4/1 | Wiring, update kinds and readout supplied; gains unknown | Lower than 03, hypothesis | 8 | 1 |
| 03 | Memory | 305 | 3/4/1 | Discover wiring, updates, gains and readout | Main experimental case | 14 | 3 |
| 04 | Memory | 753 | 3/4/1 | Different wiring/update composition | Structural contrast; shorter certificate than 03 | 14 | 2 |
| 05 | Memory | 305 | 3/4/0 | Same world as 03; unlimited environment actions | Same inference as 03 | 14 | 3 |
| 06 | Dependence | 123841 | 0/0/1 | Complete physical laws supplied | Low; execution control | 4 | 0 |
| 07 | Dependence | 123841 | 2/4/1 | Dependence masks/loading supplied; parity constants unknown | Lower than 08, hypothesis | 6 | 1 |
| 08 | Dependence | 123841 | 3/4/1 | Infer dependence and persistent nuisance | Main experimental case | 14 | 2 |
| 09 | Dependence | 123849 | 3/4/1 | Different dependence masks | Structural contrast | 14 | 2 |
| 10 | Dependence | 123841 | 3/4/0 | Same world as 08; unlimited environment actions | Same inference as 08 | 14 | 2 |

“Minimum supporting readings” means the fewest actual-outcome measurements that make
at least one complete build valid in every remaining world, with hindsight selection
of experiments. It excludes setup and finish feedback. It is **not** a strategy the
player knows in advance, a model-failure probability, or cognitive reasoning depth.
For the selected rows these minima are exact. Reference policies are achieved upper
bounds, not optimal policies.

Both memory cases need 27 distinguishable predictive states, yet different numbers of
readings. This deliberately exposes the difference between mechanism complexity and
information difficulty. The uncertainty cases have ambiguous first four sequential
fixtures, but another pair can suffice. No claim of five necessary adaptive stages is made.

## What the player does

The player is confined to a sealed workshop. It reads `manifest`, `observe`, and every
evidence file, takes the actual `carrier`, investigates the facility with `reader`,
configures `assembler`, operates it on the carrier, and finishes successfully. Blank
stock makes optional survey copies, which cannot substitute for the actual carrier.
Configure stores settings; operate commits; probe previews without committing. A reader
always measures the facility reference, never whether the candidate build is correct.
Eligible failed finishes provide one binary rejection and allow repair while actions remain.

The full primitive grammar is public. Private parameters and fixture ordering are hidden.
Equivalent solutions are accepted; there is no mandatory theory report or experiment order.

### Memory example: run 03

**Operator-only explanation:** three cells update simultaneously modulo 3. In this seed,
`r0'=x`, `r1'=r1+x`, `r2'=r2+old_r1`; the displayed value is `r0+r1*r2`. The cartridge
must match the facility for every finite input history from zero. It receives input
pulses, never a feed of the facility's answer. Other programs with identical behavior pass.

**Player-faithful walkthrough:** the initial evidence supplies only the complete choices
for wiring, overwrite/accumulate updates, gains and readout. It does not supply the formula
above. Configure the reader with a word of 1–6 trits, then probe the carried carrier.
Each probe starts an isolated reference fixture at zero and returns only its final trit.
One valid investigation observes:

| Word | Returned final trit |
|---|---:|
| `[1,1,0,1]` | 1 |
| `[1,0,0,0,2,1]` | 2 |
| `[1,0,0]` | 2 |
| `[1]` | 1 |
| `[1,0]` | 1 |

Compare the disclosed candidate programs with these observations. Two syntactic programs
remain, but they agree on every future input history, so identifying their spelling is
unnecessary. One supported construction is `[0,2,0,1,1,1,1,1,1]` in the public settings
order. Configure assembler, operate it on carrier, then finish. The checker uses complete
finite-automaton equivalence, including histories longer than the six-pulse reader limit.
The five measurements above are one strategy; the private certificate records a favorable
three-reading solution and proves no one/two-reading solution for this seed.

### Dependence example: run 08

**Operator-only explanation:** five bits obey `z0 XOR z1 XOR z2=0` and
`z0 XOR z3 XOR z4=0`. Each of the eight allowed vectors appears once on the fixture panel,
in a hidden arbitrary order. True physical signs are `s_j=(-1)^z_j`; lab displays add
`lambda=(1,-1,1,-1,1)`. Means and all pairwise covariances do not reveal the parity laws.
At operation, the disturbance changes to either sign, with a live reference `r=delta`.
A robust solution is `s4=s0*s3`, after correcting selected displayed sensors with `r`.

**Player-faithful walkthrough:** evidence discloses the parity-mask grammar, both loading
patterns, all reader modes and the robust acceptance rule, but not the selected laws.
Probe joint fixtures 0 through 4 using reader settings `[0,fixture]`:

| Fixture | Displayed joint vector |
|---|---|
| 0 | `[2,0,2,0,2]` |
| 1 | `[0,-2,2,-2,2]` |
| 2 | `[0,-2,2,0,0]` |
| 3 | `[2,0,2,-2,0]` |
| 4 | `[2,-2,0,0,2]` |

Negative values in odd channels establish the alternating loading pattern. Subtract its
lab loading to recover physical signs, convert signs to bits, and test the disclosed
two-parity grammar against all observed vectors. The fifth row resolves the remaining
ambiguity in this sequence. Derive `s4=s0*s3`. Configure assembler with `[9,0,1]`: mask 9
selects channels 0 and 3, offset 0 leaves the product's sign unchanged, pattern 1 supplies
the alternating loading. Operate on carrier and finish. Both operational disturbance
signs and all eight physical states are checked, not just the measured fixtures.

A blank reference is also legal; repeating a fixture does not produce independent noise
samples. Fixtures 0 and 4 happen to provide a two-reading certificate in this world;
the player cannot infer that choice from the hidden ordering. Another robust build can
also be accepted. No uniqueness of hidden parameters is required.

## Qualification and known shortcuts

- Memory: 768 equally weighted syntactic programs, 138 complete behavioral classes.
  Independent partition refinement proves the cached observations characterize complete
  behavior. A fixed six-reading panel solves the whole prior. Minimal predictive state
  count and experiment count are reported separately.
- Dependence: 120 physical mechanisms and 8! assignments each, or 4,838,400 complete
  worlds. The solver retains 120 mechanisms plus exact schedule multiplicity, instead of
  materializing millions of schedules. This is sound for full joint fixture observations;
  partial-channel queries would require a different posterior.
- Every single joint reading leaves incompatible builds. Five distinct joint readings
  always support a build, including recovery of loading without an explicit reference.
  All means, variances and pairwise covariances together are insufficient at T3.
- Pure build trials remain legal. Achieved blind schedules need 138 memory builds and
  26 dependence builds (415/79 actions); the latter is not proved minimal. These are
  upper bounds, not reasons to claim guessing is impossible within 64 actions.
- All scientific inference can precede construction. These PoCs do not yet implement
  construction-dependent discovery, irreversible preparation, or unbounded theory invention.
- All selected worlds recover from an injected rejected build within 17 actions. T0
  wins require four actions. The shared 64-action allowance is intentionally generous.

## Build, preflight and run

Build from the committed feature branch with a clean checkout. Use the same tag for the
tool, service and validator; the supplied config already does. Bash example:

```sh
podman build --build-arg VCS_REF="$(git rev-parse HEAD)" -t nexus:discovery-pocs-v1 .
podman image inspect nexus:discovery-pocs-v1 --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}'
podman run --rm --entrypoint python nexus:discovery-pocs-v1 scripts/preflight_discovery.py --output /tmp/discovery-preflight.json
```

For PowerShell, set `$nexusRevision = git rev-parse HEAD`, then pass
`--build-arg "VCS_REF=$nexusRevision"`. Replace `podman` with `docker` if preferred.
The image normalizes canonical source line endings before checking its release binding.
Do not disregard a failing preflight. The report is private operator material.

Use `examples/mindtrial/nexus-discovery-config.yaml` and `nexus-discovery-tasks.yaml` in
the same directory. Provider settings, prices and enablement are inherited unchanged
from the previous assembly configuration, not newly verified recommendations. Only the
existing Astra medium run is enabled by default. Restore keys locally and enable the
desired models. Preserve fresh sessions/context for every row; do not share control-run
solutions with later rows. No external interpreter is exposed.

Preflight binds the full installed Python source map, validated matrix digest and freshly
executed independent proof. It checks paired physical worlds, both distinct structures,
exact selected certificate claims, live supported receipts, replay and recovery.
Incomplete or failed execution overwrites a stale success with `running`/`blocked`.
Run it in the **actual built image** before paid evaluations.

## Read the results

Report wins separately as evidence-supported or compatible guesses. Keep inference,
measurement choice, construction, resource exhaustion and receipt/parser mistakes apart.
The terminal diagnostics include repeated readings, first supported-build turn, committed
builds/replacements and remaining mission classes. Dependence also reports the exact
remaining schedule count; the generic world counter counts mechanisms, not permutations.
No posterior count, optimal experiment or qualification hint is exposed during active play.

Compare 02→03 and 07→08 for the missing-structure effect; 03↔04 and 08↔09 for structural
variation; 03↔05 and 08↔10 for environment-budget sensitivity. One seed per contrast
cannot establish a general capability ranking. Retain reasoning traces and exact receipts;
passing both families would be evidence to revise the mechanisms, not to silently lower R.
