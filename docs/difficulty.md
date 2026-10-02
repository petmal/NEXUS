# Difficulty profiles

NEXUS intentionally exposes only two public generation knobs. Low-level topology, evidence,
resource, and qualification settings remain internal so callers do not need to reason about
incompatible parameter combinations. Discovery guarantees are evaluated after conditioning on
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

## Planning level

`--planning-level` controls topology/planning scale while leaving exact solution length as a
measured property:

| Level | Internal room range |
| --- | ---: |
| 0 | 4–5 rooms |
| 1 | 5–7 rooms |
| 2 | 7–9 rooms |

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
- Changing P0/P1/P2 does not reroll mechanics or evidence. Topology has an independent named RNG
  stream, so planning variants share the causal problem while changing the room graph and role
  placement.

The generator first finds a causal family that satisfies every discovery profile in that family.
Once selected, topology rejection may retry only the topology stream; it is never allowed to
silently reroll the hidden law. Stable SHA-256-derived seeds are used for named streams rather than
Python's process-dependent `hash()`.

Private generation metadata records a `scenario_family_id`, `scenario_family_attempt`, and
`topology_attempt` so benchmark analysis can verify that compared episodes were genuinely
paired.

## Resource budget

Resource pressure is currently derived rather than publicly configurable. For D0-D3 the action budget is:

```text
physical optimal actions
+ qualified probe allowance
+ conservative local-exploration allowance
+ execution slack
```

For D4 the qualifier has an exact minimum worst-case **total action** policy, so the budget uses:

```text
minimum guaranteed policy actions
+ conservative local-exploration allowance
+ execution slack
```

This avoids penalizing an agent merely because the private reference solver already knows hidden
entity locations. Resource pressure can become a public axis later after calibration data exists.

The qualified probe allowance is a guarantee-level quantity. A model may guess the true hidden
world and win with fewer probes than the minimum needed by a policy that succeeds across all
evidence-consistent worlds.

## Operator metadata

`private.json` contains typed `generation_metadata`, including:

- selected discovery/planning levels and scenario-family identity;
- physical optimal action count;
- required informed-probe count;
- exact guaranteed-policy action count where available;
- selective-experiment proof metadata for D4;
- action budget;
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
