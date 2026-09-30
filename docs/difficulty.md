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

A probe is an information action, not a gate. NEXUS never refuses an `operate` merely because the
agent has not probed. An agent can therefore guess and get lucky. The qualifier instead enumerates
all causal worlds consistent with the evidence, removes worlds that contradict NEXUS's public
winnability guarantee, and computes the minimum worst-case number of probes needed by a policy
that guarantees the target. Observable results from irreversible `operate` actions also narrow the
belief state, so they are not incorrectly treated as hidden information.

For level 3, generation additionally proves that the target artifact projection cannot be obtained
by using only one machine or by applying the two generated machine laws in reverse order.

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

## Resource budget

Resource pressure is currently derived rather than publicly configurable. The action budget is:

```text
physical optimal actions
+ qualified probe allowance
+ conservative local-exploration allowance
+ execution slack
```

This avoids penalizing an agent merely because the private reference solver already knows hidden
entity locations. Resource pressure can become a public axis later after calibration data exists.

## Operator metadata

`private.json` contains typed `generation_metadata`, including:

- selected discovery/planning levels;
- physical optimal action count;
- required informed-probe count;
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