# Stateful discovery pilot

## What changed

`stateful-discovery-v1` is an opt-in ontology on `feat/theory-prior-axis`.
The player must align the original seal component. It is also the only experimental
subject: an intervention can reveal information, move the seal away from its
goal, and change which experiment is useful next. Previous families and defaults
remain available.

The seal has four registers in 0–4. Only the first is displayed. Four apparatus
modes each update one register using its neighbour's current value and an unknown
gain and exponent. The dependencies form a cycle. The full 256-law grammar and
the joint target are public; the selected law is hidden at T3. Display equality
alone is insufficient to escape. For example, changing the third register may
leave the display unchanged, yet change what the second apparatus does next,
which changes a later first-apparatus reading. The player must interpret that
reading against the actual intervention history and plan from the resulting state.

Ordinary probes remain legal, nonmutating, one-step previews. There is no duplicate
seal or reset. Reaching `(4,4,4,4)` causes disclosed, absorbing collapse. A rejected
finish leaves the specimen unchanged and gives only the failed joint-goal result.
Successful finish checks the exact physical state and produces the usual receipt.
No particular experiment order or theory report is mandatory.

## What qualification establishes

The source-bound result is [stateful-preflight.json](stateful-preflight.json).
The checked admission contract is in [the plan](stateful-discovery-plan.md).

- An independent scalar interpreter agrees on **641,024** law/state/mode cases.
- The constructive public policy succeeds with supported finishes for every one
  of the 256 laws at each of three supported goals: **768 complete scalar replays**.
  The main goal's uniform policy upper bound is 39 science actions, or 41 with
  taking and P1 movement. These are achievable bounds, not optimal minima.
- Each selected hard truth needs **12–13 science actions** for an evidence-supported
  finish, even permitting unsafe alternative branches in that optimistic search.
  At least **10–11 committed transformations** remain necessary when all probes
  and rejected finishes are free. This separates physical investigation progress
  from repeated information requests.
- A free complete initial probe panel does not enable observation-blind completion
  within 22 subsequent actions. All **21** committed prefixes of length zero, one
  or two also fail the handoff test: free full probe panels at every visited state,
  then blind completion, within 20 total committed/suffix actions. The search
  includes repeated finish attempts, synchronization and blind reset-like words.
- Each hard truth nevertheless has a **13-science-action adaptive branch** with
  independently replayed safe continuations for every other possible observation.
  Their all-outcome upper bounds are 33–41 science actions. This demonstrates a
  useful adaptive alternative to the excluded short handoff strategies.
- The physical dependency cycle has no proper autonomous coordinate partition.
  The shallow negative control is explicitly rejected by the hard gate. All ten
  live reference missions win with evidence support and exact canonical replay.
- Search caps return **unknown and block admission**. Atomic reports preserve
  completed cells and identify any unfinished cell; interrupted search cells are
  recomputed. No capped result is treated as an impossibility proof.

These are bounded, mechanically checkable statements. They do **not** prove an
unbounded absence of shortcuts, forbid every possible mental decomposition,
establish a full-game minimax optimum, or predict a model failure rate. A model
may still reason efficiently or win by a compatible guess; telemetry distinguishes
the latter from a supported finish. The selected seeds are a challenge set, not
a random-population estimate. Arbitrary generated episodes are reference-qualified
but are not automatically admitted to this trajectory tier.

The four hard worlds deliberately share the initial state, goal and topology.
They have four distinct gain patterns and three power patterns, but share some
local parameters. This pilot varies mechanism structure under a controlled goal;
it is not broad goal/topology coverage. Do not expose the seeds, selection filter,
source code or proof reports to players. Their disclosed prior is all 256 laws.
If those selection facts are exposed, requalify against the conditional prior.

## Pre-qualified ten-execution matrix

Every R1 row has **64 environment actions**. R0 removes that cap, while retaining
physical irreversibility and the same harness limits. Each execution needs a fresh
context. No external Python or source access is provided.

Action counts below include taking, movement and successful finish. The supported
minimum is an optimistic actual-outcome certificate, not a guaranteed worst-case
policy cost. The reference column is the measured action count of the supplied
public policy on that seed, not a required route for the player.

| Run | Seed | T/D/P/R | Purpose and expected relative challenge | Supported minimum | Public reference |
|---|---:|---|---|---:|---:|
| 01 | 371 | 3/5/1/1 | Shallow-handoff control; expected easier than selected hard worlds | Not computed | 16 |
| 02 | 229 | 0/0/1/1 | Laws and procedure supplied; easiest execution control | 10 | 10 |
| 03 | 229 | 0/5/1/1 | Laws supplied, route unsupplied; isolates state tracking and planning | 10 | 10 |
| 04 | 229 | 3/5/1/1 | Main coupled discovery/control case | 15 | 25 |
| 05 | 229 | 3/5/1/0 | Same reasoning as 04, unlimited environment actions | 15 | 25 |
| 06 | 737 | 3/5/1/1 | Qualified gain/power contrast; high expected challenge | 14 | 29 |
| 07 | 605 | 3/5/1/1 | Qualified contrast with 11-transform free-evidence minimum | 14 | 27 |
| 08 | 468 | 3/5/1/1 | Qualified contrast with 11-transform free-evidence minimum | 15 | 24 |
| 09 | 229 | 3/5/0/1 | Same reasoning as 04, movement removed | 14 | 24 |
| 10 | 95 | 3/4/0/1 | Previous `coupled-memory-v1` baseline; expected easier from prior runs | Not recomputed here | 16 |

All rows except 10 use `stateful-discovery-v1`. Relative difficulty predictions
are hypotheses; the pilot must establish whether the new reasoning burden is
material. Do not infer a ranking of runs 04/06/07/08 from reference lengths alone.

The machine-readable matrix is [stateful-matrix.json](stateful-matrix.json).
The ready-to-use files are
[nexus-stateful-config.yaml](../examples/mindtrial/nexus-stateful-config.yaml) and
[nexus-stateful-tasks.yaml](../examples/mindtrial/nexus-stateful-tasks.yaml).
Place them together. The config points to `./nexus-stateful-tasks.yaml` and image
`nexus:stateful-discovery-v1`. Provider IDs, reasoning settings and price fields
were retained from the previous operator config; they were not refreshed in this
implementation. API keys are blank. Astra medium is enabled; other runs remain
disabled for the operator to select.

The harness allows 120 tool calls and 160 turns, with a 60-second tool timeout and
120-second service startup timeout. Free manifest/evidence/observe requests still
consume harness calls. Extended diagnostics and generation timing are enabled.
Player prompts are manifest-led and disclose no seed, private parameter, reference
route or qualification hint. The adapter continues to use one persistent session.

## Build and validate the actual image

From the feature-branch repository root, with a clean checkout:

```sh
docker build --build-arg VCS_REF="$(git rev-parse HEAD)" -t nexus:stateful-discovery-v1 .
docker image inspect nexus:stateful-discovery-v1 --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}'
docker run --rm --entrypoint python nexus:stateful-discovery-v1 scripts/preflight_stateful.py --output /tmp/stateful-preflight.json
```

Replace `docker` with `podman` for Podman. PowerShell also accepts the quoted
`"$(git rev-parse HEAD)"` substitution. The OCI revision must match the checkout.
The preflight must exit zero and print `stateful preflight passed: 10 rows` before
spending model credits. It re-runs the qualification inside the installed image;
the checked-in report alone does not validate a locally built image. Source files
must retain LF endings as required by the repository attributes.

To retain the image's fresh report on the host, create `stateful-results` and mount
it at `/results`, then change the output to `/results/preflight.json`. Keep operator
reports out of the model's mounted files. Rerun preflight after source or matrix
changes. CI runs the same source and actual-image gates.

## Interpreting the pilot

Compare 02 against 03 for planning, 03 against 04 for discovery, 04 against 05 for
budget effects, 04 against 09 for movement, and the four hard seeds for mechanism
sensitivity. Row 01 tests whether a player finds a legitimate simpler route.
Row 10 anchors comparison to the previous resettable experimental setting.

Record success, first-finish support, actions, committed transformations, probes,
rejected finishes, physical collapse, final surviving laws/states, tool calls and
wall time. Active play receives only ordinary world feedback; private inference
and qualification diagnostics remain terminal/operator output. A correct route
that was never executed, a lucky compatible finish, irreversible collapse, an
action-budget loss and a harness/parser failure are different outcomes.

For action overhead, report both `actions − supported minimum` (where certified)
and `actions − realized public reference`. Do not subtract the uniform reference
upper bound and label the result excess over an optimum. The local inference
tracker's common-decision count concerns **finish now**, not the number of all
possible future plans.

## Implementation and validation record

The new schema, mechanics, generation, public evidence, inference, finite planner
and qualification live under `ontology/stateful`; matrix admission lives under
`evaluation/stateful`. The existing trusted registry is the integration seam.
The generic transition engine, protocol actions and receipt/replay rules are
unchanged. There is no new runtime dependency. Immutable transition tables,
interned law/state IDs, exact physical-distance pruning and bounded caches keep
the expensive offline audits out of routine per-task generation.

Two early candidate designs were rejected because the qualifier found short
investigate-once/blind-install shortcuts. A fresh implementation review found a
known-law policy bug for routes longer than eight transformations; exact singleton
distance descent fixed it. Regression tests cover the nine-step initial route,
repeated finish in blind search, nonmutating probes, irreversible collapse,
privacy, exact replay, HTTP persistence and misleading display matches.

See [initial design review](stateful-initial-design-review.md),
[follow-up design review](stateful-followup-design-review.md), and
[implementation review](stateful-implementation-review.md). The final source-bound
report supersedes intermediate review hashes. The legacy repair source manifest
was refreshed only after its unchanged proof, witness and 15-test conformance gates.

Final regression and CI results are recorded at completion below. No paid model
calls are part of implementation validation; empirical calibration remains open.

## Completion checkpoint

Implementation and selected matrix are complete. Final regression, source identity
and publication checks are in progress; do not treat this paragraph as CI approval.
Resume commands are in [stateful-discovery-plan.md](stateful-discovery-plan.md).
