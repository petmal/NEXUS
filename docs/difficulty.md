# Difficulty profiles

This page describes the default **axis version 1** profiles. Version 2 is selected
explicitly with `NEXUS_AXIS_VERSION=2` or `--axis-version 2` and has revised T/D
semantics, a true one-room P0 and unlimited/recoverable R0. See the
[scientific investigation design](scientific-investigation-design.md) and
[model pilot matrix](scientific-investigation-model-matrix.md). Do not mix scores
or numeric difficulty labels across versions.

Axes v2 also has an explicit experimental `coupled-network-v1` family. Its live
support is T3/D4-D5 and D0/T0,T3 controls; T1/T2 remain mathematical PoC comparisons.
See [rich investigation results](rich-investigation-results.md). Always record the
family as well as axis version when comparing runs.

The original three controls vary discovery, planning and resource pressure. The theory
setting selects what account of a mechanism is supplied; only supported combinations
are valid. See the [T/D synthesis](td-experiments-and-next-directions.md) for the differences between axis versions. Low-level topology, evidence construction, and qualification settings remain internal so
callers do not need to reason about incompatible parameter combinations. Discovery guarantees are evaluated after conditioning on
both the public evidence and the public goal.

## Discovery level

`--discovery-level` controls mission-relevant causal uncertainty, not simply the number of
evidence rows.

| Level | Guarantee |
| --- | --- |
| 0 | Relevant transformation context is directly demonstrated; the evidence identifies the selected rule. |
| 1 | No direct-context example is supplied, but evidence plus the public goal admit a guaranteed winning causal policy with zero probes. |
| 2 | Evidence plus the public goal require exactly one probe in the minimum guaranteed causal policy. |
| 3 | The world contains two required transformation stages and the minimum guaranteed causal policy requires exactly two probes. The second stage operates on the artifact produced by the first. |
| 4 | Probe mechanics are unchanged, but the world exposes multiple legal experimental contexts. At least one auxiliary context is discriminative and lies on a minimum-cost guaranteed policy, while a distractor context is predictably non-discriminative and costs an extra action. |
| 5 | The agent must construct a lower-cost diagnostic context by operating an auxiliary machine on an auxiliary artifact, then probe the mission machine. Direct mission-artifact probing and a functional distractor-machine path remain legal but are mechanically proved to have higher worst-case total action cost. |

A probe is an information action, not a gate. NEXUS never refuses an `operate` merely because the
agent has not probed. An agent can therefore guess and get lucky. The qualifier instead enumerates
all causal worlds consistent with the evidence, removes worlds that contradict NEXUS's public
winnability guarantee, and computes the minimum worst-case number of probes needed by a policy
that guarantees the target. Observable results from irreversible `operate` actions also narrow the
belief state, so they are not incorrectly treated as hidden information.

For level 3, generation additionally proves that the target artifact projection cannot be obtained
by using only one machine or by applying the two generated machine laws in reverse order.

Level 4 does **not** introduce a special probe or protected mission artifact. The ordinary
non-destructive `probe` action remains available on every carried artifact. The generated world
adds auxiliary and distractor samples and the qualifier compares them with an exact
belief-state policy solver over all evidence-consistent causal worlds. Brute-force probing remains
legal; the guarantee is about total action cost:

- the auxiliary sample is discriminative and can be used by an optimal guaranteed policy;
- the mission artifact can still be probed directly;
- the distractor sample is predictably non-discriminative from the public evidence and adds one
  action without improving the guaranteed policy.

This lets NEXUS measure experiment-selection efficiency without changing the player mechanics.

Level 5 extends the same idea to **experiment construction** without adding any new action
semantics. The generated public grammar discloses two calibration-machine laws and a four-member
mission-machine hypothesis family. The hidden parameter is the mission machine's winning phase.
One calibration machine transforms an auxiliary sample into a diagnostic input that makes a
single subsequent M1 probe distinguish all four hypotheses. A second calibration machine is fully
functional but produces a non-diagnostic state. Qualification proves with the exact belief-policy
solver that:

- `operate M2(A2)` can start a minimum-cost guaranteed policy;
- directly probing the mission artifact has strictly greater worst-case total action cost;
- the `M3/A3` distractor path is also strictly more expensive;
- the constructed M1 probe has four distinct outcomes, one for every viable hidden phase; and
- the selected hidden world remains independently winnable by the ordinary physical solver.

Brute-force probing remains legal. D5 therefore tests whether the agent can spend actions to
*create* a useful experiment rather than merely choose among already informative probes.

## Planning level

`--planning-level` controls topology/planning scale while leaving exact solution length as a
measured property:

| Level | Internal room range |
| --- | ---: |
| 0 | 4–5 rooms |
| 1 | 5–7 rooms |
| 2 | 7–9 rooms |
| 3 | 7–9 rooms + delivery dependency |

P3 deliberately does **not** increase the P2 room-count range. It is compiled from the paired P2
world with identical rooms, edges, hidden laws, evidence, and core entities. NEXUS adds one cargo
artifact whose intrinsic state duplicates an already available experimental context, places it in
the existing topology, and adds a delivery-location goal for that cargo. Qualification then removes
only that cargo/goal to reconstruct the P2 counterfactual and proves that both the physical optimal
action count and exact guaranteed-policy action count decrease by exactly the recorded
`planning_dependency_action_cost` (at least two actions).

When a discovery profile requires more distinct roles, NEXUS automatically raises the minimum
room count needed to keep start, artifact, machines, and destination distinct.

The generator does not ask the user to choose an optimal-action range. It generates the requested
semantic world, solves it exactly, rejects pathological horizons, and records the resulting
physical optimum.

## Paired scenario families

Difficulty comparisons are deliberately paired rather than relying on one shared sequential RNG.

For a fixed seed:

- D0, D1, and D2 use the same qualified one-machine causal family. At a fixed planning level they
  share the hidden law, intrinsic artifact state, target transformation, phase, topology, and role
  locations; only the evidence/discovery profile changes.
- D3 uses its own qualified two-machine causal family.
- D4 uses a separate selective-experiment family with one mission artifact plus qualified auxiliary and distractor samples.
- D5 uses a separate constructed-experiment family. For a fixed seed, all planning variants share the same hidden winning phase, artifact roles, and three machine laws; only the delivery topology changes.
- Changing P0/P1/P2 does not reroll mechanics or evidence. Topology has an independent named RNG
  stream, so those planning variants share the causal problem while changing the room graph and
  role placement.
- P3 reuses the exact paired P2 topology and causal world, then adds only the mechanically isolated
  delivery dependency described above.

The generator first finds a causal family that satisfies every discovery profile in that family.
Once selected, topology rejection may retry only the topology stream; it is never allowed to
silently reroll the hidden law. Stable SHA-256-derived seeds are used for named streams rather than
Python's process-dependent `hash()`.

Private generation metadata records a `scenario_family_id`, `scenario_family_attempt`, and
`topology_attempt` so benchmark analysis can verify that compared episodes were genuinely
paired.

## Resource pressure

`--resource-pressure` is an independent action-budget axis. Every profile first computes the exact
minimum worst-case **total environment-action** cost of a guaranteed winning policy. Resource
pressure changes only the explicit allowance above that baseline:

| Level | Meaning | Action allowance above exact guaranteed policy |
| --- | --- | ---: |
| 0 | forgiving | `2 * (room_count - 1) + 2` |
| 1 | constrained | `room_count - 1` |
| 2 | tight | `0` |

R2 gives exactly `guaranteed_policy_actions`. This is a guarantee over causal hypotheses
**with the topology and role locations known to the solver**; it is not a guaranteed budget
for discovering the initially hidden map. Even an early legal exploratory move can consume
all available slack. R0 preserves the exploration + execution cushion and is preferred when
isolating theory reasoning. This clarification does not change existing resource semantics.

Resource pressure never rerolls topology, mechanics, evidence, goals, physical optimum, or the
exact guaranteed-policy optimum. The qualifier recomputes the selected allowance and rejects an
episode whose budget does not equal:

```text
exact guaranteed-policy actions + resource allowance
```

The minimum guaranteed probe count remains a separate causal statistic. An agent can guess the
selected hidden world and win with fewer probes than the minimum required by a policy that succeeds
across all evidence-consistent worlds; terminal telemetry therefore reports signed action and probe
deltas rather than labeling every negative delta as better reasoning.

## Operator metadata

`private.json` contains typed `generation_metadata`, including:

- selected discovery/planning/resource-pressure levels and scenario-family identity;
- physical optimal action count;
- required informed-probe count;
- exact guaranteed-policy action count and a private branching witness for every profile;
- selective-experiment proof metadata for D4 and constructed-experiment proof metadata for D5;
- P3 dependency cost where applicable, resource allowance, and action budget;
- recommended tool-call ceiling;
- room count and graph diameter;
- evidence candidate/prediction counts and goal-compatible causal-hypothesis count;
- rule AST complexity;
- solver search metrics.

This metadata is deliberately absent from the player manifest. Inspect it with:

```bash
nexus inspect ./episode/private.json
```

The command does not print latent rule ASTs, verifier secrets, or the reference plan.


## Theory profiles and cumulative research

| T | Information supplied | Supported D | Interpretation |
|---|---|---|---|
| 0 | Explicit candidate catalogue | 0–5 | Catalogue-based discovery |
| 1 | Complete primitive and conditional grammar | 0–4 | Compose/select exact laws in a broad structural prior |
| 2 | Effective model, exact region, known correction form | 2 | Infer a bounded additive correction |
| 3 | Dependencies, invariants, complete independent operator-cell prior | 2 | Infer a missing bounded relationship without an effective baseline |

T2/T3 support P0–P3 and R0–R2. Unsupported combinations reject explicitly.
T3 is `t3-independent-operator-cells-v1`: 729 complete laws, 243 after calibration,
nine reachable equivalence classes with multiplicity 27, five viable classes (135 full laws).
For this profile metadata `candidate_rules_before_evidence` counts 729 full laws;
`candidate_rules_after_evidence` and `evidence_candidate_counts` count the nine solver classes.
Qualification metrics also report full surviving cardinality and multiplicity explicitly.
The quotient is sound only for one machine and shape-invariant artifacts of the same shape;
P3's duplicate cargo preserves that condition. New reachable shapes require a new proof.

T is a theory-information axis, not an ordinal score. Current T3 is deliberately bounded and
can be easier than T1. Existing levels remain independent families. Cumulative theory
progression is described and proved separately in the [progression results](theory-t3-progression-results.md).
