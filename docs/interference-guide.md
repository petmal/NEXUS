# Disclosed interference: longer plans and coordinate subgoals

`stateful-interference-v1` is a bounded planning experiment with complete public laws
and state. It extends the ideas tested by `stateful-coordination-v1` with prerequisites
and simultaneous effects on two registers. The original family and its historical
exports remain available. This new family has not yet been evaluated on models.

The goal is to measure planning under interacting subgoals, while retaining exact
costs, reproducibility and inspectable traces. A longer reference word alone is not
enough: qualification proves the shortest possible plan, verifies matched controls,
and establishes which kinds of simplification cannot solve each admitted problem.

## Motivation from the pilot and rerun

The coordination pilot produced 39/40 new-family wins. The only failure chose a
one-operation-longer route under an exact budget. The supplied selected rerun has
one further attempt on each of core09/core10/slack33/slack34, not four each. All four
win: core10 now achieves its 10-action optimum, whereas slack34 spends 13 actions
against an optimum of 10. This supports strategy variability on the existing
fixtures, not a reliable failure threshold. See the
[rerun audit](research/coordination-rerun-results-2026-10-26.md).

The next pilot therefore changes the planning structure, rather than inferring a
capability boundary from the single failure. The user authorized proceeding with
this extension; completing the remaining previously suggested repeats is not a
prerequisite for this exploratory pilot.

## World and operations

There are two banks, each with three registers taking values 0–4. The vector starts
at zero. One original seal carries this vector; all six machines are in `array`.
The complete physical state space contains at most 15,625 vectors. All laws,
prerequisites, current values, target values and machine locations are disclosed.

For mode `bankB_rJ`, with flat coordinate index `i = 3*B + J`:

1. Read the next register in the same bank, `3*B + (J+1)%3`.
2. If it does not equal the public `guards[i]`, leave the vector unchanged.
3. Otherwise simultaneously add `gains[i]` to register `i` and `spill_gains[i]`
   to the public spill register, both modulo five. All other values stay fixed.

Both increments are nonzero. The guard, operated register and spill register are
distinct. An enabled operation changes exactly two registers. A disabled operation
is accepted, leaves the vector unchanged and still costs one action.

| Condition | Spill destination |
|---|---|
| Independent | `3*B + (J+2)%3`, in the same bank |
| Coupled | Same except when `J=2`: first register of the other bank |

The intervention redirects two write edges. It preserves the number of reads and
writes, coefficients, prerequisites, initial state and target. Both conditions have
local interference; “independent” means independent **banks**, not independent
registers or absence of subgoal interactions. No operation is hidden or chosen by
an LLM, and no private source code executes inside a law.

`operate` commits the update. `probe` previews the same full resulting vector at
the same action cost, without committing it. Taking, dropping, waiting and finishing
retain their ordinary meanings. Invalid controls are atomic and uncharged. Public
reads are free. Success requires carrying the original seal with every target met
simultaneously and explicitly calling `finish`. Take and finish are included in
the exact action minimum. No reset, duplicate seal, stock, travel, checkpoint or
external compute tool is provided.

## Admission and matched target strata

A seed deterministically defines a stream of at most 32 candidate kernels. Each
kernel has at least one initially enabled mode per bank. No substitute seed is
used after failure. Generation records the accepted attempt and fails closed if
no kernel has an admissible short/long target pair. Selection depends only on
mechanical criteria, never model outcomes.

Each accepted kernel supplies two different targets. Both coupling conditions and
both budgets use the same target within a stratum. The law stays fixed across the
short/long targets. Every target coordinate is nonzero, and both targets must be
reachable in both conditions.

- The coupled short target requires 12–20 operations.
- The coupled long target requires 30–48 operations.
- The independent long target requires at least 14 operations and at least four
  more operations than its short target.
- Every coupled optimum beats all bank-contiguous plans.
- Every coupled solution must unset a coordinate that was already at its target.

Short and long are construction strata, not calibrated reasoning-difficulty levels.
Horizon changes also change the target, so the experiment does not isolate plan
length from every other property of the selected goal.

The planned seeds, chosen before model evaluation, are 67, 79, 101 and 103. Their
accepted kernel attempts are 7, 3, 5 and 25. The fixed matrix is:

| Seed | Target | Independent operations | Coupled operations | Coupled bank-contiguous operations | Minimum coordinate-breaking operations, independent / coupled |
|---|---|---:|---:|---:|---:|
| 67 | short | 6 | 19 | 24 | 1 / 3 |
| 67 | long | 34 | 30 | 35 | 9 / 4 |
| 79 | short | 17 | 16 | 21 | 3 / 1 |
| 79 | long | 33 | 33 | 38 | 8 / 5 |
| 101 | short | 15 | 17 | 22 | 3 / 2 |
| 101 | long | 23 | 33 | Unreachable | 3 / 7 |
| 103 | short | 13 | 18 | 23 | 3 / 2 |
| 103 | long | 20 | 31 | 36 | 4 / 4 |

These counts exclude take and finish. The independent reachable components contain
2,304 states for the first three kernels and 624 for seed103; the coupled components
contain 11,529 states. Coupling does not uniformly increase optimal length or minimum
regression count. For example, seed67 long needs 34 independent versus 30 coupled
operations. Those differences are part of the measured intervention, not anomalies
to hide by selecting different targets for the control.

## What qualification proves

The exact planner uses breadth-first search over the compiled finite state graph.
An independent tuple-state interpreter derives index relationships directly and
checks all 93,750 transitions per admitted kernel/condition against both the runtime
and compiled tables. Independent searches establish minimum cost and restricted
strategy costs. The independent-bank optimum must factor into the sum of two
125-state bank problems.

The bank-contiguous baseline permits every operation sequence using each bank in
at most one block, in either order. It retains the full vector and allows a later
bank's cross-write to complete an earlier bank. Requiring the first bank to be
finished when leaving it would be an invalid shortcut for this family. `null`
means no restricted solution exists, not a missing proof.

The coordinate-regression check forbids every edge that changes any coordinate
from equal-to-target to unequal-to-target. If the target is unreachable under this
restriction, every unrestricted successful plan must contain a regression. A
separate weighted search computes the minimum number of such operations across
**all successful plans**, regardless of length. One operation unsetting two target
coordinates counts once. This minimum need not equal the count in a shortest-action
reference. The proof concerns individual coordinates, not necessarily reopening
an entirely completed bank.

An exact public reference is derived only from evidence, executed through a real
Session, checked for supported success and replayed by canonical hashes. Matrix
export rechecks the numerical and live qualification records and rejects stale
source identities, missing checks, altered costs or modified pairings. The standalone
launcher repeats qualification inside the installed image and compares exported
tasks with the shipped files before any model call.

Selection labels, kernel attempts, proof results and reference words are absent
from active player inputs and evidence. The existing protocol includes the operator
certificate in terminal performance after the attempt has ended. This post-terminal
reporting contract is preserved. Generator seed, solution word and verifier secret
are never supplied as player evidence. A public exact budget necessarily reveals
the optimal total action count; that is the intended R2 condition.

## Budgets and live matrix

Only T0/D0/P0 are supported. `ontology-options` accepts `coupling` (independent or
coupled) and `horizon` (short or long); unknown fields and unsupported axes are
rejected. The horizon option is an operator generation input.

- R2: exact minimum number of total actions.
- R1: that minimum plus `max(6, ceil(minimum/2))`.
- R0: uncapped diagnostic mode, outside the live matrix.

The [matrix](interference-matrix.json) contains 32 attempts: four kernels × two
targets × two coupling conditions × two budgets. Core rows01–16 use R2; slack
rows17–32 repeat the same physical problems at R1. These are four kernels and
paired variants, not 32 independent sampled worlds. Default MindTrial settings are
Astra medium, no automatic retries, 600 tool calls and 650 harness turns.

The [launcher instructions](../examples/mindtrial/interference-run.md) explain the
local build/run flow. Generation and qualification can also be run directly:

```bash
uv run --frozen --all-extras python scripts/preflight_interference.py \
  --output /tmp/interference-preflight.json --tasks-output /tmp/interference-tasks
uv run --frozen --all-extras nexus generate /tmp/interference-example \
  --axis-version 2 --science-family stateful-interference-v1 --seed 67 \
  --theory-level 0 --discovery-level 0 --planning-level 0 --resource-pressure 2 \
  --ontology-options '{"coupling":"coupled","horizon":"long"}'
```

## Reading the results

Record mission completion separately from action optimality, reported reasoning
tokens and time. From the public trajectory, count blocked/unchanged operations,
coordinate-breaking operations, bank blocks and budget loss relative to a shortest
continuation. Terminal diagnostics additionally log the first three counts. Keep
source/config/image identities and all failed/interrupted attempts.

Bank revisits are necessary for optimal/R2 coupled solutions; seven of the eight
coupled targets also have a longer bank-contiguous solution that fits R1. Only
seed101 long rules out that strategy at every budget. Coordinate regression is
unavoidable for every coupled target at both budgets. All enabled operators are
reversible: four more repetitions undo one modulo-five update. Recovery can fail
because of the remaining allowance, not because the world has permanent physical
dead ends.

This experiment changes modulus and operation semantics relative to old coordination.
Cross-family comparisons are descriptive. The matched within-family comparisons
are the primary evidence. High success rates would still leave meaningful signals
in optimality and effort, and would motivate a measured next extension rather than
discarding NEXUS's auditable framework.
