# Structural P/R qualification and a two-model comparison

This release adds exact structural measurements and a reproducible three-bank
feasibility probe. **It does not introduce an admitted harder runtime family.**
The live experiment compares GPT-6 Astra and GPT-6 Luna, both at medium reasoning,
on the same 32 qualified `stateful-interference-v1` tasks. Selecting both models
and all rows produces 64 attempts.

## Why the three-bank proposal was not admitted

The initial proposal used three banks of three ternary registers: 19,683 physical
states. Each operation reads a public equality guard and simultaneously updates
its own register and one spill register. The independent arm keeps writes local;
the coupled arm redirects boundary writes around a ring. Unlike v1, this
rewiring preserves each register's number of incoming writes. Gains, guard
values, initial state and targets are paired. Equality of degrees does not
control algebraic invariants, reachable-state counts or shortest path length.

The prespecified cohort is seeds67/79/101/103, 32 kernels per seed. All nine target
coordinates must be nonzero and reachable in both arms. The first proposed
strong-target gate is at least16 machine blocks; the next is at least two
operations reopening an already completed whole bank, minimized over **all**
solutions. Later requirements concern a paired short/long gap, required
dependency operations and bank-contiguous paths. No model outcomes select laws
or targets, and no substitute seeds are used.

Four operator-only variants were examined on those same128 kernels:

| Variant | Intervention | Maximum paired minimum blocks | Targets passing16 blocks | Targets also requiring two whole-bank reopenings |
|---|---|---:|---:|---:|
| Spill ring | Cross-bank writes, local unchanged guards | 13 | 0 | 0 |
| Boundary crossguard | Also moves boundary reads across banks | 11 | 0 | 0 |
| All crossguards | Also moves all reads across banks | 12 | 0 | 0 |
| Self guard | Both arms read each operation's own written register | 20 | 5 | 0 |

Crossguard variants change read placement as well as write placement; they are
not matched-guard controls. The self-guard variant keeps the guard indices
matched between arms but changes the grammar. Each operation disables its own
guard: useful repeated-machine runs disappear, while irreversible dead ends
become possible. The five block-qualified targets require17–20 operations, yet
all have a zero-whole-bank-reopening solution. The rejected proposal is therefore
not a stronger whole-bank challenge under the stated criteria. These are bounded
search results, **not an impossibility proof for every law in these grammars**.

Reproduce the full probe with:

```bash
uv run python scripts/probe_ternary_interference.py \
  --output /tmp/ternary-feasibility.json
```

It records every kernel, paired reachability, exact costs, first/second gate
results, absorbing dead ends and exhaustive scalar-versus-compiled transition
checks. An independent full same-machine-orbit BFS checks block costs, including
irreversible operators. It never registers a playable family or exports tasks.
A search bound error is a blocked probe, not an unreachable-goal proof. Physical
state bounds and the generic augmented-search bound of1,000,000 are separate.
The optional `--variant` restricts a diagnostic run; the release report uses all
four variants. Later gates are not waived when an earlier one fails.

## What the new metrics mean

- **Minimum actions:** exact operation minimum plus take and successful finish.
- **Minimum machine blocks:** fewest maximal runs of one machine in any
  successful operation word. Repeated uses within one run count as one block.
- **Minimum blocks on action-optimal paths:** the same count restricted to words
  attaining the operation minimum. It can exceed the unrestricted block minimum.
- **Minimum whole-bank reopening operations:** fewest operations unsetting at
  least one fully matched bank across all successful words. One operation
  reopening two banks still counts once. This differs from returning to a bank
  or disturbing one matched coordinate.
- **Avoidable actions so far:** accepted actions already used plus the physical
  minimum still needed, minus the original minimum. It can describe an unfinished
  or budget-exhausted attempt. The first increase marks first loss of optimality.
- **Success excess actions:** actual actions minus minimum, defined only on a
  successful finish.

Blocks are a structural property, not a count of mental decisions. Minima are
not inferred from one reference word. Production table searches are checked
against separate scalar-state searches with different algorithms. For example,
seed67 short coupled needs19 operations, at least7 blocks overall, but at least8
on an action-optimal path. Seed101 long coupled requires at least one whole-bank
reopening; no other v1 physical row requires one. The new fields remain
operator-side. Active player evidence, action semantics, target, budgets and
post-terminal certificates remain unchanged.

The runtime logs `interference_structure` on terminal diagnostic output. It
counts coordinate and whole-bank breaks, operation blocks, unchanged operations,
remaining physical cost, avoidable actions, first loss of optimality and success
excess. Public reads cost no actions; accepted waits, probes, drops and failed
finishes are included in efficiency costs. Rejected requests remain uncharged.
Canonical replay and supported-win verification remain the validity checks.

## Live matrix

The 32 task files are byte-for-byte the original v1 exports. The four selected
rerun anchors are already in the matrix, so they are not duplicated.

| Core row / slack row | Seed | Target | Coupling | Minimum total actions |
|---|---:|---|---|---:|
| 01 / 17 | 67 | short | independent | 8 |
| 02 / 18 | 67 | short | coupled | 21 |
| 03 / 19 | 67 | long | coupled | 32 |
| 04 / 20 | 67 | long | independent | 36 |
| 05 / 21 | 79 | short | coupled | 18 |
| 06 / 22 | 79 | short | independent | 19 |
| 07 / 23 | 79 | long | independent | 35 |
| 08 / 24 | 79 | long | coupled | 35 |
| 09 / 25 | 101 | short | independent | 17 |
| 10 / 26 | 101 | short | coupled | 19 |
| 11 / 27 | 101 | long | coupled | 35 |
| 12 / 28 | 101 | long | independent | 25 |
| 13 / 29 | 103 | short | coupled | 20 |
| 14 / 30 | 103 | short | independent | 15 |
| 15 / 31 | 103 | long | independent | 22 |
| 16 / 32 | 103 | long | coupled | 33 |

Each row is crossed with both configured models:

| Model | Reasoning | Requests/minute | Automatic retries |
|---|---|---:|---:|
| `gpt-6-astra` | medium | 20 | 0 |
| `gpt-6-luna` | medium | 20 | 0 |

Both models get exactly the same prompts, public laws, limits, tools and world
budgets. Core uses R2 (the exact minimum); slack uses R1 (minimum plus
max(6,ceil(minimum/2))). T0/D0/P0 generation labels remain unchanged: short/long
and coupling are experimental structural planning manipulations, not new
empirically calibrated P levels. Tool limit600 and max turns650 remain fixed.

Luna is a preselected efficient-tier contrast, not an established weaker model
on NEXUS. Equal reasoning-effort labels do not imply equal compute. API model
aliases are recorded; their behavior can change. Model support was checked on
2026-10-27 against the [official Luna model page](https://developers.openai.com/api/docs/models/gpt-6-luna)
and [MindTrial's OpenAI routing at the supplied binary's source revision](https://github.com/petmal/MindTrial/blob/f8a723665fff16d395e581f63d806bebf61938f5/providers/openai.go).
The user runs their existing locally built MindTrial binary; this release does
not change MindTrial or make paid calls during qualification.

## Run and collect

Unpack `NEXUS-interference-comparison-test-run-2026-10-27.zip` under `~/Downloads`.
Use the supplied `run.sh --suite all`, selecting both model runs and all16 rows
in each suite. The launcher builds an isolated archive of the pinned feature
commit using `~/Go-Projects/NEXUS`, qualifies the actual image and runs
`~/MindTrial/mindtrial` interactively. It accepts both Docker's `sha256:` and
Podman's bare immutable image IDs. Paths remain overridable with `NEXUS_REPO`
and `MINDTRIAL_DIR`. The package README contains the complete shell command.

Collect the whole package `results/` directory, including configuration, task,
source/image/binary manifests, JSON results and debug logs. Do not provide only
a screenshot or headline success rate. A selected rerun is a partial matrix;
keep every original attempt and distinguish new attempts from new worlds.
The evaluation seed is recorded as `nexus-interference-comparison-pilot-v1`.

The optional `summarize_results.py` produces a compact readout from collected
folders. It reports missing/repeated conditions, per-model reported outcomes,
request/tool durations and time before the first logged task separately. It
checks manifest hashes but **does not replace replay or verify original HMACs**.
The `DurationNS` meaning is grounded in [MindTrial's result schema source](https://github.com/petmal/MindTrial/blob/f8a723665fff16d395e581f63d806bebf61938f5/formatters/json_view.go):
network plus inference time, excluding local tools and validation. Log timestamps
are second-resolution and use the result's UTC offset; inspect offset changes
separately. Pre-task time can include interactive selection and startup. Do not
add reasoning tokens to output tokens when output accounting already includes
them. Failed or absent telemetry is not zero effort.

## Interpret the next results

First establish source/image/configuration identity, full public replay,
physical terminal state, supported-win classification and recorded receipt
agreement. Separate provider, tool, protocol and budget failures. For each
model, compare short/long, coupled/independent and exact/slack paired cells;
report success and efficiency alongside operation and block minima. Repeat
matched failures before describing a stable boundary. Effort and latency are
secondary observations and require their own accounting.

The sample has four kernels and16 physical tasks, not64 independent worlds.
The v1 write-degree mismatch and varying optimal length remain known coupling
confounds. A lower Luna success rate alone does not identify a specific P or R
effect; the within-model matched contrasts are necessary. A coupling effect can
still reflect multiple consequences of rewiring. No numerical success threshold
is being selected after seeing new model outcomes.

If the comparison separates behavior, retain v1 as a useful qualified evaluation
basis and confirm the effect with prespecified unseen seeds in a later release.
If both models remain near-perfect, revise the law grammar or dependency
structure before increasing primitive repetition. Mixed guard placements,
nonconstant disclosed effects and explicit bounded scheduling/logistics worlds
remain candidates. More blocks, more mandatory reopening, larger action minima
and lower model success are distinct goals.
