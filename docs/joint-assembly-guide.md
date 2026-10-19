# Joint inference and assembly pilot

`joint-assembly-v1` is an opt-in ontology. Older NEXUS families remain available.
The pilot asks the model to discover a facility response, prepare two compatible
components, and assemble an exit compensator. Everything is in one workshop.
There is no external Python tool, imposed experiment order, or required theory report.

## What is new

Two locally valid components can fail together. Reader bias is entangled with
component phases: it adds to B readings, subtracts from C readings, and adds to
joint readings. There is no independent reference that supplies this bias in one
calibration step. The same unknown law must reconcile all relevant observations.

Each component must preserve its own gain contract, while the assembled device must
match the facility at **all nine operating inputs**. These are separate, public goal
conditions. The component contracts matter: a device can reproduce the joint output
using a wrong local gain. Such a device does not meet the complete mission. Several
phase assignments can nevertheless be equivalent and are accepted.

Preparation also has a persistent mounting effect: replacing either component
rotates the other mounted component's phase. This effect is public and deterministic.
It tests planning and state tracking; it is not an additional hidden scientific law.
Repair is possible. A wrong finish gives only binary rejection, and another build can
be attempted while actions remain. Fatal activation and scarce material consumption
are deliberately deferred to separate matched experiments.

## A concrete example

The player is given the complete formula menu, arithmetic, reader signs, preparation
rules and exact goal. They are **not** given the selected gains, phases, kernel or bias
in T3. For seed 136 the private operator truth is U(x)=x+1, V(y)=2y+2,
H(u,v)=u-v, r=1, all modulo three. This paragraph is operator-only explanation.

The reference investigator starts from the public prior, selects readings that split
its remaining hypotheses, and stops when some complete build works in every remaining
world. This seed takes seven readings under that policy. It then prepares components
and installs a kernel. To construct B=(1,1), C=(2,2), kernel 1, one correct sequence is:

1. Forge B with gain 1 and phase 2 (=1-2 modulo 3).
2. Forge C with gain 2 and phase 2; mounting C rotates B from phase 2 to phase 1.
3. Install kernel 1 and finish.

Simply preparing B at phase 1 and then C at phase 2 leaves B at phase 0. Both gains
still pass their local contracts, but the assembled response is wrong. Preparing a
component again can also rotate its partner, so correction requires tracking both.

## Validated ten-execution matrix

All rows use P0/R1: one workshop, unlimited stock/apparatus use, 40 environment
actions (46 for row 10). The harness allows 120 calls. Every execution needs a fresh
session and model context. Run order may be randomized; row identifiers retain pairing.

| Run | Seed | T/D | What it tests | Exact supporting readings | Reference readings / actions | Expected relative challenge |
|---|---:|---|---|---:|---:|---|
| 01 | 349 | 0/0 | Supplied-law construction control | 0 | 0 / 8 | Lowest; execution only |
| 02 | 349 | 3/3 | Calibrated version of 03 | 4 | 4 / 16 | Moderate |
| 03 | 349 | 3/4 | Sum law hidden among the menu; all three channels necessary | 5 | 7 / 22 | Highest information requirement |
| 04 | 136 | 3/4 | Difference law; different gains/phases; all three channels necessary | 5 | 7 / 22 | Highest information requirement |
| 05 | 127 | 3/4 | Product law; either local channel plus joint can suffice | 4 | 6 / 20 | Moderate–high; shortcut available |
| 06 | 178 | 3/4 | Squared-left law; B+joint can suffice, C+joint cannot | 4 | 7 / 22 | High; asymmetric evidence choice |
| 07 | 178 | 3/3 | Calibrated version of 06 | 4 | 5 / 18 | Moderate; same certificate, shorter reference |
| 08 | 349 | 2/4 | Known sum: opposite biases cancel in the local data | 4 | 4 / 16 | Shortcut/control |
| 09 | 136 | 2/4 | Known difference: joint calibration remains necessary | 4 | 4 / 16 | Intermediate |
| 10 | 136 | 3/4 | Exact 04 with six additional actions | 5 | 7 / 22 | Same science; more recovery room |

Expected challenge is a hypothesis, not a measured failure rate. The new grammar
has 432 worlds, 144 complete build settings and 96 distinct mission signatures.
Differences in reader offset alone are not counted as different physical coverage.
The four main science seeds cover all four kernel shapes and different gain/phase
settings. T3 sum/difference are harder by the certificate than the nonlinear worlds.

## What qualification proves—and does not prove

An independent literal-table oracle checks arithmetic and complete build acceptance.
An independent exhaustive subset search agrees with the optimized certificate search.
Every T3/D4 world needs at least four supporting readings; sum/difference need five.
For the latter, even a complete sweep through any two reader channels leaves
incompatible complete builds. Nonlinear channel omissions remain legal and labelled.

These are **actual-outcome information certificates**: even a chooser who knows which
world is real cannot select a smaller set of truthful measurements that supports a
complete build. They do not include rejected finishes or prove a minimum total action
count, multi-round cognitive depth, or an LLM failure probability. The public greedy
policy supplies a constructive upper bound, not an optimality claim.

The finish audit separately allows free preparation, free configuration and arbitrary
complete guesses. Exact successful world masses out of the uniform 432-world prior:
0 readings + 1 guess: 9; 1+1: 9; 2+1: 27; 0+2: 18; 1+2: 18.
These are short-horizon exact results. The broader feedback upper bound saturates at
five feedback actions; no exact search of all 40-action strategies is claimed. A model
can still guess a correct build. Terminal classification distinguishes supported wins
from compatible wins and never treats success itself as evidence that the preceding
inference was justified. `deep_tier_admitted` therefore remains false.

## Live interface coverage argument

The canonical public state consists of location, apparatus settings, prepared
component fields, installed kernel, cached readings, resources and turn. All hidden
laws are fixed. Starting from identical public state, the following partition covers
every legal action and response:

| Surface | Hidden information and state effect |
|---|---|
| Reader probe/operate, any artifact | One ternary reading in 15 classes: 3 B, 3 C, 9 joint. The unused coordinate is normalized. Preparation and old cache do not affect the reference fixture. Operate stores the same reading; probe leaves the artifact unchanged. |
| Forge/assembler operate | Known deterministic component/assembly update only. No hidden residual, gain validity, phase validity or goal preview is returned. |
| Forge/assembler probe | The same public update on a copy; no physical commitment and no new hidden information. |
| Configure | Public settings only. Arity/range and room errors depend only on public data. |
| Take/drop/move/wait | Public logistics/resources only. Copies use the same response law; only the actual carrier is mission eligible. |
| Observe/status/manifest/evidence | Public state or the fixed disclosed prior, including any previously observed cache. No fresh hidden values or active posterior diagnostics. |
| Invalid actions | Rollback without resource cost; errors depend on public syntax/state, never hidden truth. |
| Eligible finish | Membership in one of the 144 complete-build acceptance masks. All failed acceptance worlds are excluded; equivalent accepted phase settings count. |
| Ineligible finish | Constant rejection from visible missing components/carrier/location; no law elimination. |
| Terminal state | Receipts only after real success. No reset/new-session surface; operator diagnostics do not feed back into active play. |

Induction over this partition gives the reduction from arbitrary preparation and
experiment histories to public state plus a law posterior. Granting free access to
every query and build strengthens the player, so the relaxed guess bounds remain
valid even when the real player alternates experiments, repairs, previews and finishes.
The runtime checks actual physics directly; changing inference caches cannot change
the winning predicate. Tests check the complete returned reader payload and exact replay.

The private CLI solver's construction count is also checked against an independent
BFS of the entire public preparation/control graph, including repeated operations.
It skips unchanged settings and accepts equivalent phase assignments. Its physical
optimum is separate from the public investigator's evidence-gathering cost.

## Running and building

From the latest `feat/theory-prior-axis` checkout:

```bash
uv sync --frozen --all-extras
uv run python scripts/joint_assembly_oracle.py --output /tmp/assembly-proof.json
uv run python scripts/preflight_joint_assembly.py --output /tmp/assembly-preflight.json
docker build --build-arg VCS_REF="$(git rev-parse HEAD)" -t nexus:joint-assembly-v1 .
docker run --rm --entrypoint python nexus:joint-assembly-v1 scripts/preflight_joint_assembly.py
```

Use `podman` in both commands instead of `docker` if preferred. In PowerShell:

```powershell
$revision = git rev-parse HEAD
podman build --build-arg "VCS_REF=$revision" -t nexus:joint-assembly-v1 .
podman run --rm --entrypoint python nexus:joint-assembly-v1 scripts/preflight_joint_assembly.py
```

Use `examples/mindtrial/nexus-assembly-config.yaml` and `nexus-assembly-tasks.yaml`
together. Tool, service and validator all use the same image. Existing provider
settings are retained with blank API keys; Astra medium is enabled by default.
Inspect provider settings and enable the desired comparisons. Preflight failure blocks
the recommended pilot; do not disregard it. The image includes its operator matrix.

## Extending this ontology

Schema and bounded primitive semantics are separate from observation channels,
acceptance, state updates, posterior and runtime. The existing trusted plugin catalog
is sufficient; engine/session/replay contain no assembly-specific branches. To add a
kernel, channel or hidden state, update the complete public prior, independent oracle,
all legal observation classes and accepted-build audit before claiming difficulty.
Do not silently expand the response payload without expanding the proof alphabet.

Finite tables are immutable and shared; each belief has its own mask. Generation
selects a world directly, with no online search. Offline proof and preflight are bounded,
atomic and source-bound; running/blocked outputs replace stale successes. New secret
state transitions would require a belief over laws **and reachable physical states**;
the current public mounting transition does not pretend to supply that future proof.
