# First planning/resource pilot

`stateful-planning-v1` begins the next stage after the
[T/D synthesis](td-experiments-and-next-directions.md). It asks whether a model can
coordinate transformation order and travel, and whether a smaller action allowance
changes its success. The first implementation is mechanically qualified. **No live
model evaluations have been run for this family.**

## What changes, and why

The base is the stateful architecture: one original seal, four coupled registers,
four operations, a partial readout and an exact joint goal. The same seed selects
the same law and target as `stateful-discovery-v1`. There are still 256 possible
laws; operations and ordinary hypothetical probes retain their meanings. No
additional hidden-law complexity is claimed.

The new family places the operations in different rooms. A player must carry the
seal to a machine, use it, and eventually return to the exit. Transformation order
can therefore change both the number of operations and the travel cost. This is
a useful first planning experiment because the complete physical state space is
small enough to solve exactly. It also preserves exact receipts, deterministic
replay, public evidence and private operator diagnostics.

The **entire map and all machine locations are disclosed** in `layout.json`.
Map discovery is not part of this pilot. That choice avoids repeating the earlier
confound where a private solver knew routes that the evaluated player had to find.

The revision architecture remains the preferred later base for several evidence
and construction tasks, and compositional repair for contextual interventions.
Neither needs to be modified to test this first spatial hypothesis. The old
stateful family and its historical matrices remain unchanged.

## Axis definitions

All cells use D5. T0 supplies the complete selected law but no solution procedure.
T3 supplies the full 256-law prior without the selected gains and powers.

| P setting | Layout | Purpose |
|---|---|---|
| P0 | One room; all operations at the exit | Transformation-order control without travel |
| P1 | Two rooms; alternating modes share locations | Small grouping/travel tradeoff |
| P2 | Exit hub and four separate operation rooms | Repeated travel through a common hub |
| P3 | Six-room circuit with one cross-link | Several routes and nonuniform pairwise travel costs |

These names describe layouts, **not a proved ranking of cognitive difficulty**.
P2 and P3 can have equal optimal costs. A higher action count alone is not evidence
of deeper reasoning.

Every accepted action costs one unit, including take, move, operate, probe and
finish. Free manifest/evidence/observe/status requests do not use the world action
allowance. Invalid actions are rejected atomically. The shared engine retains its
existing exhaustion and terminal rules.

| R setting | Environment action allowance |
|---|---|
| R0 | Uncapped; available as a diagnostic, outside the initial 16-cell matrix |
| R1 | Reference cost plus `max(6, ceil(reference / 2))` |
| R2 | Exactly the reference cost |

The meaning of “reference” depends on T:

- **T0:** the exact minimum total cost, including taking the seal, all movement,
  transformations, return travel and successful finish. R2 permits no wasted action.
- **T3:** the worst-case cost of one fully public contingent investigation policy,
  over every possible law. It includes every probe and every movement. This is an
  upper bound on achievable guaranteed cost. It is **not** the optimal policy cost.
  R2 therefore does not mean optimal or necessarily severe resource pressure at T3.

T3 budgets are computed solely from the public target, prior and layout. The
selected hidden law and its private shortest plan cannot influence them. Two T3
episodes with the same target/layout but different selected laws have identical
public contracts, budgets and evidence, apart from random episode identifiers.

## Verified planning tradeoffs

The two fixtures were selected from a local seed0..39 scan because joint planning
beats every shortest-operation solution. They form a challenge set, not a random
sample of generated-world difficulty. All numbers below include take and finish.

| Fixture | Fewest operations at P0 | P3 cost of the cheapest route among **all** shortest-operation solutions | P3 exact joint cost | Operations in the joint solution |
|---|---:|---:|---:|---:|
| Seed21 | 9 | 25 | 22 | 10 |
| Seed31 | 8 | 24 | 19 | 9 |

In each case one extra transformation reduces the total cost. The comparison does
not route just one arbitrarily chosen shortest word: it minimizes travel over
**all** minimum-operation words. This matters because a poor tie-breaking choice
could otherwise create a false planning advantage.

The production planner uses Dijkstra search over `(physical state, room)`, with
travel compressed to known shortest routes. A separate checker uses scalar tuple
physics and one-edge-at-a-time breadth-first search. They agree on the pilot's
physical minima. Taking the only seal initially loses no optimal solutions;
dropping it, waiting, probing a known law, or unsuccessfully finishing cannot
improve a known-law physical shortest plan in this static world.

The unknown-law reference routes the existing stateful investigator. Its certified
P3 upper bounds are 105 actions for seed21's target and 98 for seed31's target.
The realized public-policy traces use 77 and 87 actions respectively. These gaps
illustrate why a worst-case policy allowance is not a per-instance optimum.
The offline checker executes all 256 laws with independent scalar physics and
travel counting. The maximum realized cost equals the recursive bound for that
policy. This does not exclude a more efficient investigator or successful guessing.

## Matched pilot

The [matrix](planning-resource-matrix.json) has two blocks of eight cells, one for
each fixture. Within a block:

1. T0/P0, P1, P2 and P3 at R2 compare layouts at equal zero slack above their
   respective exact physical minima.
2. T0/P3/R1 versus T0/P3/R2 measures the effect of extra action allowance.
3. T3/P0/R2 versus T3/P3/R2 compares routed investigation under their respective
   public-policy allowances.
4. T3/P3/R1 versus T3/P3/R2 measures extra allowance with uncertainty held fixed.

The T0/P3 and T3/P3 cells also provide a disclosure comparison, but their budgets
are different by design. Do not treat their win-rate difference as a pure T effect.
Likewise P comparisons hold the **budget rule**, not the absolute action count,
fixed. A later fixed-absolute-budget experiment should be separately labelled.

The primary first read is the slack T0/P3 cells (rows05 and13): can the model
coordinate the known mechanism and travel at all? Next compare their exact-budget
partners, then interpret the T3 interaction. Use fresh contexts, retain row IDs,
and interleave paired conditions when executing the full pilot. Do not enlarge
the sweep until those controls have been reviewed.

## Run and reproduce

From the repository root:

```bash
uv sync --frozen --all-extras --python 3.14.7
uv run --frozen --all-extras --python 3.14.7 python scripts/preflight_planning.py \
  --output /tmp/planning-resource-preflight.json \
  --tasks-output /tmp/nexus-planning-resource-tasks.yaml
```

The preflight checks the physics kernel, independent spatial minima, strict
planning tradeoffs, all-prior public policies, live supported wins and exact
replay. Its source and matrix hashes bind the result to the implementation.
Task export rejects stale, failed or mismatched preflight results. The
[committed task file](../examples/mindtrial/nexus-planning-resource-tasks.yaml)
uses JSON syntax, which is valid YAML. It contains operator-only seeds and must
not be mounted into a player's accessible files.

Use this task source with the existing MindTrial NEXUS service and an explicitly
chosen provider configuration. The task file does not choose a model or launch
calls. It sets a common 600-tool-call and 650-turn harness ceiling, above the
largest reference-derived recommendation in the matrix (494 tool calls). These
are harness ceilings, distinct from the much smaller world action budgets.
Rebuild the service image from this branch, run the preflight in that image, and
record its digest before paid evaluation. This workspace did not execute the
new pilot through a MindTrial container.

For one standalone episode:

```bash
uv run --frozen --python 3.14.7 nexus generate /tmp/nexus-pr \
  --axis-version 2 --science-family stateful-planning-v1 --seed 21 \
  --theory-level 0 --discovery-level 5 --planning-level 3 --resource-pressure 1
uv run --frozen --python 3.14.7 nexus qualify /tmp/nexus-pr/private.json
uv run --frozen --python 3.14.7 nexus solve /tmp/nexus-pr/private.json \
  --trace-out /tmp/nexus-pr/reference.jsonl
uv run --frozen --python 3.14.7 nexus replay /tmp/nexus-pr/private.json \
  /tmp/nexus-pr/reference.jsonl
```

`solve` is an operator tool with access to hidden truth. Its optimum is not an
available T3 player policy. Do not expose private episodes, repository source,
proof reports or reference traces to evaluated models.

## What to measure and decide next

Record receipt success, first/final evidence support, moves, operations, probes,
failed finishes, invalid actions, environment exhaustion and provider/harness
stops separately. At T0, report excess total actions over the exact optimum.
At T3, report the private physical minimum and public policy upper bound as
different quantities; neither alone measures the player's investigation quality.
Preserve the existing source/image, model/effort, evidence, transcript and receipt
ledger. Provider failures are not reasoning failures.

If T0/P3 fails even with slack, inspect state tracking and route/transformation
coordination before adding more uncertainty. If only T0/R2 fails, report a
resource-efficiency limitation. If T0 succeeds and T3 fails, inspect experiment
routing and belief/state tracking; do not relabel the result pure T/D difficulty.
If all cells remain easy, the next additions should vary dependency length or
the number of interacting objectives, with equal-size independent controls.

Open questions include unknown-law policy optimality, whether models exploit
the demonstrated tradeoffs, generalization to held-out laws/layouts, and whether
longer plans expose reasoning limits or mainly accumulate execution errors.
Unknown maps, multiple seals, consumable instruments, shared stock and a general
composition framework are intentionally outside this first experiment.

The [dated preflight](research/planning-resource-preflight-2026-10-25.json) and
[validation record](research/planning-resource-validation-2026-10-25.json) document
mechanical evidence. Live model results remain the next decision point.
