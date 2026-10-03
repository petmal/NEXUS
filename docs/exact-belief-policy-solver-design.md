# Exact compressed belief-policy solver design

## Problem

The current exact belief-policy solver is correct in principle but expands ordinary `move` actions
inside every belief branch. That couples a small causal decision problem to a much larger navigation
state graph and made D2/D3/D5 qualification impractically expensive.

A later optimization attempted to certify D0-D3 with:

```text
selected-world physical optimum + minimum guaranteed probes
```

as the exact total guaranteed cost. Validation disproved that equality. It is only a lower bound:
an informative probe can require travel, phase adjustment, or a continuation different from the
selected hidden world's omniscient shortest path.

The replacement must therefore preserve the full minimax policy problem while compressing only
behavior that is provably irrelevant to causal branching.

## Engine facts used by the proof

Under the current stable NEXUS mechanics:

1. `move` consumes one environment action.
2. `move` changes only `agent_room`.
3. `move` does not advance phase.
4. `move` does not transform artifacts or consume machine uses.
5. `move` emits no hidden-law-dependent observation.
6. The room graph is static for the complete episode.
7. Carried artifacts move with the agent at no additional cost.
8. All non-movement state changes occur through `take`, `drop`, `wait`, `probe`,
   `operate`, or `finish`.

These facts are engine invariants, not assumptions about generated examples.

## Movement quotient

Define an **interaction state** as the complete observable WorldState immediately after a
non-`move` action (or the initial state). For any interaction state S and any legal
non-movement interaction A that must occur in room R, define a macro edge:

```text
S -- shortest_path(S.agent_room, R) ; A --> S'
```

with cost:

```text
distance(S.agent_room, R) + 1
```

The macro stores the actual shortest sequence of ordinary `MoveAction` objects followed by A.

Interactions:

- `take artifact`: target room = the artifact's current room;
- `drop artifact`: target room = a goal-referenced drop room;
- `probe machine/artifact`: target room = machine room, artifact must be carried;
- `operate machine/artifact`: target room = machine room, artifact must be carried;
- `wait`: current room, cost 1;
- `finish`: current room, cost 1 and generated only when the goal is currently satisfied.

There is no standalone movement macro.

### Lemma 1 — shortest-path replacement

Consider any valid ordinary action sequence between two consecutive non-movement interactions.
Its intervening actions are only moves. Replacing that move subsequence with a shortest path
between the same endpoint rooms:

- reaches the same room;
- leaves phase unchanged;
- leaves all artifact state unchanged;
- leaves all machine-use counts unchanged;
- produces no different hidden-law observation; and
- costs no more actions.

Therefore every policy has an equal-or-cheaper policy whose movement between interactions is a
shortest path.

### Lemma 2 — no useful movement-only stopping state

Suppose a policy moves to room X and then makes no state-changing interaction there before later
moving to an interaction in room Y. The combined movement cost is at least the shortest distance
from the original room directly to Y. Because movement has no side effects, stopping at X changes
nothing relevant to the later interaction. The stop is dominated.

Waiting does not invalidate this lemma: `move; wait` and `wait; move` produce the same phase,
inventory, machine state, and final room at the same cost, so waits can be canonicalized as
interactions at the pre-movement room.

### Theorem 1 — movement quotient preserves optimal minimax cost

By repeatedly applying Lemmas 1 and 2 to every branch of an ordinary contingent policy, obtain a
macro policy with no greater cost and identical observation partitions. Conversely, every macro
edge expands to legal ordinary moves plus its interaction with exactly the declared cost.
Therefore the ordinary policy graph and macro graph have the same minimum worst-case total action
cost.

This is the central correctness proof for compression.

## Belief semantics

A search node remains:

```text
(observable physical state, viable hypothesis set)
```

The hypothesis set contains complete correlated machine-rule tuples; correlations are never
factorized.

For each macro interaction:

1. execute the route once on the representative observable state;
2. execute the final interaction under every surviving hypothesis using the real engine;
3. group hypotheses by the observation available to the player:
   - probe: exact reported hypothetical transformed artifact;
   - operate: resulting observable canonical state;
   - deterministic actions: resulting observable canonical state;
4. recurse on every outcome branch.

The route can be executed once because movement is hypothesis-independent and all hypotheses in a
belief node share the same observable state.

A policy is guaranteed only if **all** outcome branches can win within the remaining budget.

## Exact optimization

All macro costs are positive integers. The existing bounded decision predicate remains useful:

```text
can_win(state, belief, remaining_cost)
```

but it now recurses once per meaningful interaction rather than once per room edge.

For exact optimization:

1. compute exact single-world macro shortest costs for every evidence-consistent hypothesis;
2. discard physically impossible hypotheses, preserving the existing viable-world semantics;
3. use the maximum single-world optimum as a sound minimax lower bound;
4. test budgets from that lower bound upward to the configured proof bound;
5. the first feasible budget is the exact guaranteed cost.

The invalid D0-D3 `physical + probes` equality is removed. Minimum guaranteed probes remains a
separate causal statistic, not a total-cost certificate.

### Lemma 3 — lower bound

A guaranteed policy must win in every viable hidden world. Its worst-case cost therefore cannot be
less than the optimal cost for any individual viable world. Hence:

```text
guaranteed_cost >= max(single_world_optimum[h] for h in viable_hypotheses)
```

Starting iterative minimax search at this value skips impossible budgets without changing the
answer.

## Exact single-world macro solver

Hypothesis viability and the lower bound use Dijkstra over the same macro graph with one concrete
hidden rule tuple.

This is exact by Theorem 1. The existing ordinary-action BFS remains independent:

- generation/qualification still uses concrete BFS for the selected hidden world;
- targeted proof tests compare macro Dijkstra and BFS costs/plans;
- replay of expanded macro witnesses goes through the unchanged engine.

Thus the optimized solver does not become its own only oracle.

## Dominance rules retained

Only previously proved mechanics-level pruning remains:

- drop only at rooms referenced by location goals;
- do not operate artifacts referenced only by location goals;
- a final-machine-use operation on a non-goal artifact is dominated by a non-destructive probe;
- zero-information probes that leave state and belief unchanged are dominated.

No pruning depends on the selected hidden rule.

## Witness construction

The solver keeps a macro choice internally but emits the existing ordinary-action policy witness.

A macro:

```text
move R1 -> move R2 -> probe M1/A1
```

is expanded into deterministic unary witness nodes for the moves followed by the branching probe
node. Remaining-budget fields decrease by one for each ordinary action.

Consequences:

- witness depth equals exact total environment-action cost;
- the private witness remains inspectable at ordinary protocol granularity;
- witness replay needs no special macro action in the engine or public protocol.

## Caching

Use immutable per-call caches for:

- all-pairs shortest room paths;
- legal macro choices by semantic observable state;
- macro transition outcomes by (state, belief, macro);
- single-world macro shortest costs;
- `can_win(state, belief, remaining_cost)`.

The existing bounded cross-call result cache remains keyed by a SHA-256 semantic digest. No cache
entry may depend on action budget fields that are normalized away.

## Failure/limit behavior

The exact solver retains explicit limits:

- maximum causal hypotheses;
- maximum physical/macro states per concrete hypothesis;
- maximum guaranteed-policy action bound.

Exceeding a limit returns an explicit unsolved/exhausted result; generation rejects the candidate.
No fallback approximation is permitted for metadata labeled exact.

## Critical proof tests before broad generation

1. Macro single-world Dijkstra cost equals ordinary BFS on hand-built and generated D0-D5 worlds.
2. Expanded macro plans replay to the same terminal state.
3. Macro minimax cost equals the old ordinary-step minimax solver on tiny hand-checkable fixtures.
4. Probe outcome partitions and operate outcome partitions are identical.
5. Waiting before/after movement equivalence is tested under nontrivial phase rules.
6. Correlated multi-machine hypotheses remain correlated after observations.
7. D2 fixture demonstrates why `physical optimum + one probe` may be a strict lower bound.
8. Policy witness depth equals the reported exact guaranteed cost.

## Execution plan

### Stage A — solver core

1. Add a shortest-path movement oracle with deterministic lexicographic shortest paths.
2. Add private macro-choice generation and macro execution.
3. Add exact concrete macro Dijkstra for hypothesis viability/lower bounds.
4. Replace ordinary-step recursion inside the belief solver with macro transitions.
5. Expand macros back into the existing ordinary-action witness.
6. Remove the invalid structural D0-D3 total-cost certificate; use the generic exact macro solver
   for D0-D5.

### Stage B — correctness gates

1. Add movement-quotient unit proofs.
2. Compare macro concrete solver against BFS.
3. Compare macro belief solver against tiny legacy ordinary-step fixtures.
4. Retain physical BFS and replay qualification as independent checks.

### Stage C — M7 integration

1. Generate exact guaranteed cost/witness for every discovery profile with the compressed solver.
2. Qualification independently recomputes exact cost/witness.
3. Keep minimum guaranteed probes as a separate statistic.
4. Preserve signed terminal action/probe deltas and the published telemetry semantics.

### Stage D — M8 repair

1. Re-run P3 exact counterfactual qualification through the compressed solver.
2. Fix R0/R1/R2 metadata consistency without changing world semantics.
3. Validate P3 adds exactly its recorded physical and guaranteed-policy overhead.
4. Validate resource pressure changes only allowance/budget.

### Stage E — runtime/test pipeline

1. Keep fast/slow/stress pytest tiers.
2. Move all generated D4/D5/P3 integration-heavy checks out of the automatic paid fast gate unless
   they are the sole focused proof for a mechanic.
3. Reuse generated episodes within a test module where semantics permit rather than regenerate the
   same seed/profile.
4. Retain configurable stress seed count; use 3 seeds for development validation, 5 for final
   paid branch validation, and 10 for an explicit release-grade run.
5. Keep uv download caching and single-job ordered gating.

### Stage F — final validation

Use Actions conservatively:

1. no CI runs during implementation;
2. one temporary validation-branch run with fast + extended + 3-seed stress;
3. repair locally/by static review if needed;
4. one final 5-seed full run only after the first run is green;
5. reserve the 10-seed/240-world matrix for explicit release validation if the 5-seed sample is
   clean and runtime is acceptable.

The feature branch is considered complete only after fast, extended, stress, CLI, container, replay,
and schema-contract checks pass.
