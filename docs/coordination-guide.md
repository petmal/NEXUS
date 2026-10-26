# Known-law coordination pilot

`stateful-coordination-v1` tests efficient action ordering across several groups
of goals. It follows the [P/R pilot and rerun](research/planning-resource-pilot-results-2026-10-25.md):
21 physical wins in 21 supplied attempts, but only 19 evidence-supported wins.
The known-law P/R controls were almost always optimal. The selected rerun did not
establish a stable resource-pressure effect, so the old unknown-law budgets remain
unchanged.

## What changes

One original carried seal contains two or three **banks**, each with two or three
registers. A bank is a group of goal coordinates, not a separate copy of the old
episode. Every register must equal its public target simultaneously at finish.
The current vector, all laws and the entire room map are public. There is no
hidden-law discovery in this family. `T0/D0` means full disclosure here; it does
not supply a solution procedure.

Each register has its own machine. Operating it updates only that register:

```
new x_i = (old x_i + gain_i * (1 + local_next^power_i + cross)) mod 3
```

The gains and powers are public integers in `{1,2}`. `local_next` is the next
register in the same bank's cycle. In the **independent** condition, `cross=0`.
In the **coupled** condition, the last register's machine in each bank additionally
reads the first register of the next bank. Other machines still use `cross=0`.
An operation in another bank does not directly undo a completed coordinate; it
can change the cost of future operations through these known inputs.

Each matched pair shares gains, powers, target, register/machine count, map and
machine locations. The only physics intervention is adding the cross-bank input.
This changes active input count as well as dependency placement; it is not a
comparison at equal graph degree. The complete-vector display and modulus three
are deliberate new-family controls. The old four-register, modulus-five worlds
retain their original behavior.

There is **no collapse condition** in this family. A global absorbing condition
would couple the supposedly independent banks. Ordinary `take`, `move`, `operate`,
`probe`, `drop`, `wait` and `finish` retain their engine meanings. A probe previews
one operation without changing the seal. Public reads are free; actions consume
budget. There are no resets, stocks, configuration settings or external compute.

## What qualification proves

The generator selects paired, reachable targets using mechanical checks before
model testing. Targets have no zero coordinates, so every coordinate machine is
needed. Selection is deterministic from the seed and shape. It considers all
nonzero target vectors in descending coupled P0 distance, with seeded tie order,
and admits the first reachable pair with a strict coordination gap. These are
selected challenges, not a random population sample; seed substitution is not
silently allowed when no target qualifies.

The primary P0 proof compares the exact joint minimum with the best plan that
completes each bank in one uninterrupted block and never returns to it. This
restricted baseline optimizes **all bank orders and all legal within-bank words**.
For independent banks the costs must be equal, and the optimum must equal the
sum of the separately solved bank costs. For coupled banks the unrestricted
optimum must be strictly smaller. At R2, a winning coupled P0 plan therefore
needs to revisit at least one bank. Merely printing a reference plan that switches
banks would not establish this guarantee.

Both solvers include take, travel, operations and finish. A separate tuple-based
interpreter and unit-edge BFS check the optimized solver. Preflight compares every
physical-vector/mode transition for every admitted law/condition, runs a public-only
reference through the live session, validates supported success and replays the
canonical trace. Exact budgets are derived from these costs. No reference plan or
seed is sent to the evaluated player.

At P3 the existing disclosed six-room circuit places coordinate machines in a
round-robin assignment to the four machine sites. The mechanical independence
control still shares travel, so P3 is a secondary logistics experiment. A strict
interleaving gap is required for the underlying P0 fixture, not automatically
claimed for its P3 variant.

`R2` is the exact minimum total action count. `R1` adds `max(6, ceil(minimum/2))`
actions. `R0` is an uncapped diagnostic. R comparisons fix the problem; coupling
comparisons fix the budget rule, not necessarily the absolute number of actions.
A larger connected problem is not automatically harder than its independent control.

## Pilot and controls

The [matrix](coordination-matrix.json) uses seeds 41 and 53, without model-based
selection. The option names describe structure rather than calibrated axes:
`banks` counts groups and `registers_per_bank` counts coordinates per local cycle.
Do not equate this automatically with required reasoning depth or assume a
monotonic ordering. Two banks of three registers and three banks of two registers
provide different topologies at the same six-register volume.

| Suite | Cells | Purpose |
|---|---:|---|
| core | 16 | Four shapes (2×2, 2×3, 3×2, 3×3), two seeds, independent/coupled; P0/R2 |
| slack | 16 | The same P0 problems with R1 allowance; follow up exact-budget failures |
| spatial | 8 | Largest shape, both seeds and conditions, P3 at R1/R2 |
| repeat | 10 | Two further attempts each on old P/R rows 06, 07, 08, 15, 16 |

Conditions are interleaved/counterbalanced in the exported task order. Each task
gets a fresh session and model context. Automatic task retries remain disabled.
The old repeats carry explicit attempt labels 03 and 04, following the original
pilot and supplied single rerun. Their source qualification is refreshed for the
new image without rewriting the historical model source checkpoint.

Run `core` first. Compare coupled and independent outcomes within shape/seed,
record excess actions over the exact optimum, and inspect failed or premature
finishes. If exact-budget failures appear, use the `slack` suite before interpreting
them as an inability to coordinate at all. `spatial` asks whether travel and slack
change that behavior. `repeat` remains a separate investigation of old T3 strategy
variability and unsupported success. There are no new T3 coordination cells.

Physical success, evidence support, invalid actions, exhaustion, provider errors
and harness stops remain separate outcomes. Full known state makes supportedness
an audit consistency check here, rather than a substantive hidden-law challenge.
Do not count uninformative committed readings as wasted actions.

## Run locally

The downloadable package's launcher implements the user's local workflow; see
[the launcher instructions](../examples/mindtrial/coordination-run.md). It uses the
existing `~/Go-Projects/NEXUS` clone to build the exact package revision, launches
the existing `~/MindTrial/mindtrial` binary interactively, and writes into a unique
directory below the unpacked package's `results/` folder.

For operator qualification from a checkout:

```bash
uv run --frozen --all-extras --python 3.14.7 python scripts/preflight_coordination.py \
  --output /tmp/coordination-preflight.json --tasks-output /tmp/coordination-tasks
```

For a standalone generated world:

```bash
uv run --frozen --python 3.14.7 nexus generate /tmp/nexus-coordination \
  --axis-version 2 --science-family stateful-coordination-v1 --seed 41 \
  --theory-level 0 --discovery-level 0 --planning-level 0 --resource-pressure 2 \
  --ontology-options '{"banks":3,"registers_per_bank":3,"coupling":"coupled"}'
```

The bounded nine-trit cap keeps exact checking feasible. Broader sizes, partial
state, destructive cross-effects and unknown laws require new qualification and
separately labelled experiments. Live model results for this new family are still
pending; its proof certificates establish the stated mechanics, not empirical
difficulty.
