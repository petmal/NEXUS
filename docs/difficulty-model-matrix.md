# Retained ten-run control and efficiency matrix

This is an **operator-only diagnostic matrix**, not player evidence or a uniformly
sampled benchmark. Use the environment blocks in
[difficulty-model-matrix.json](difficulty-model-matrix.json). The corresponding
[preflight report](difficulty-matrix-preflight.json) binds qualification to the
installed package and matrix content. All ten cells must pass before a model run.

As of the 2026-10-16 follow-up, all 70 tested missions in this matrix were won.
Retain it for controls and efficiency comparisons; the new experimental challenge
is the [compositional pilot](structural-model-matrix.md). The table below uses the
improved reference's actual action counts; game budgets and old guaranteed upper
bounds are unchanged. This historical matrix is not a newly difficult model test.

## Original design rationale

The previous repair pilot achieved 42/42 first-attempt victories, but all three
seeds used the cubic law. Its reference strategy cancels nuisance terms in three
compact steps. That family remains a useful compact-reasoning control.

Seed selection alone did not produce the stronger tier in the existing causal
family: all its mission-order-sensitive worlds admit two-reading certificates.
The new opt-in `coupled-dynamics-v1` ontology adds two interacting hidden state
components, simultaneous transitions, unknown routing and response forms, and
prediction of eight transfer protocols. Existing families and defaults remain
available. The scientific prior is completely disclosed; no external interpreter
is needed to interact with the world, and enumeration remains a valid strategy.

## Matrix

All cells use axis version 2, **P1/R1**, generation timing, no external Python,
and a recommended **120 tool calls**. Start every cell in a fresh model context
and fresh single-session NEXUS instance. Randomize execution order. Numeric
axis labels are family-local settings, not calibrated difficulty equivalence
between ontologies.

| ID | Family | Seed | T/D | Purpose | Expected relative difficulty | Reference actions / budget |
|---|---|---:|---|---|---|---:|
| nexus-01 | coupled-repair-v1 | 1198 | T3/D5 | Linear law; compact cancellation | Low | 15 / 18 |
| nexus-02 | coupled-repair-v1 | 1205 | T3/D5 | Quadratic law; same nuisance parameters | Low; more arithmetic | 15 / 18 |
| nexus-03 | coupled-repair-v1 | 1212 | T3/D5 | Cubic law; same nuisance parameters | Low; comparison with previous pilot | 15 / 18 |
| nexus-04 | coupled-dynamics-v1 | 128 | T0/D0 | Exact treatment supplied; physical execution control | Lowest | 5 / 13 |
| nexus-05 | coupled-dynamics-v1 | 128 | T3/D5 | Matched to execution control; transition 0, response 2, wiring 0 | Higher candidate | 37 / 73 |
| nexus-06 | coupled-dynamics-v1 | 839 | T3/D5 | Transition 0, response 2, wiring 1; different hidden preparation | Higher candidate | 40 / 73 |
| nexus-07 | coupled-dynamics-v1 | 1013 | T3/D5 | Transition 1, response 2, wiring 0 | Higher candidate | 45 / 73 |
| nexus-08 | coupled-dynamics-v1 | 649 | T3/D5 | Transition 0, response 1, wiring 0 | Higher candidate | 43 / 73 |
| nexus-09 | coupled-dynamics-v1 | 1509 | T3/D5 | Transition 2, response 0, wiring 1 | Higher candidate | 46 / 73 |
| nexus-10 | coupled-dynamics-v1 | 219 | T3/D5 | Longer-history discriminator | Strongest structural requirement; empirical rank unknown | 40 / 73 |

The five broad dynamics cases span structural strata selected before model
outcomes. The sixth adds a deliberate longer-history diagnostic; it is not a
representative frequency estimate. Do not infer a statistically representative
overall success rate from this stratified ten-cell set.

## What qualification proves

- All ten generated cells pass compiled validation, serialization, a public-
  information reference policy, real `finish` victory, and exact replay.
- Repair covers all three law degrees with nonzero coupling. It is explicitly
  labeled compact adaptive, never accepted as a deep candidate.
- Each of the six dynamics challenges has a distinct world and mission target.
  Together they cover all transition/response forms, both wirings, and both
  order-sensitive and order-insensitive mission outcomes.
- Across **all 4,674 normalized legal scientific experiments**, no collection
  of at most three actual readings identifies the required target for any of
  these six truths under the full 1,944-world prior. This holds even if an oracle
  chooses the experiments knowing the truth. The lower bound is four, not a
  proof that four readings suffice. The reference uses seven; the full-prior
  reference bound is eight readings and 65 actions at P1.
- Complete untreated measurements remain target-ambiguous in every challenge.
  Five broad cases can be resolved from sufficiently many one-pulse experiments.
  For seed 219, **even every untreated and one-pulse measurement leaves two
  target classes**, so positive-measurement identification needs a longer history.

These are information requirements, **not a guarantee of deep cognition or a
particular LLM failure rate**. A lucky treatment can win without a reading.
Failed finishes remain legal. Separately, a checked relaxed bound includes those
guesses: at budget 73, a policy using at most two ternary scientific readings has
uniform full-prior success at most **5/12**. The three-reading version of that
bound is vacuous; do not extend the claim to it or to this selected matrix.

## Mandatory preflight

From the final checkout:

```bash
uv sync --frozen --all-extras
uv run python scripts/preflight_matrix.py \
  --matrix docs/difficulty-model-matrix.json \
  --output /tmp/nexus-matrix-preflight.json
```

Expected final output: `pilot-ready; empirical calibration pending; full rollout
not yet recommended`. Every row must say won and replayed. Exit must be zero.
An invalid matrix, audit timeout, missing coverage, stale repair package, or live
failure writes `blocked` and returns nonzero. Interrupted runs retain a `running`
checkpoint; that is never an admission certificate. Rerun the command after
interruption or any package/matrix edit; it starts a fresh deterministic audit.

Build with the standard revision label and run the same check **inside the image
you will evaluate**, especially when building on Windows:

```bash
docker build --build-arg VCS_REF="$(git rev-parse HEAD)" -t nexus:qualified .
docker run --rm --entrypoint python nexus:qualified \
  scripts/preflight_matrix.py --output /tmp/matrix-preflight.json
```

Use the equivalent shell syntax for obtaining the revision on Windows. Preserve
the full preflight output. The committed report validates the tested source;
it cannot substitute for checking the actual image. Container CI runs this same
command. Packaging normalizes LF line endings without relaxing source identity.

To check a saved report against a checkout without rerunning the proof:

```python
import json
from pathlib import Path
from nexus.evaluation.matrix import Matrix, verify_preflight_binding

matrix = Matrix.model_validate_json(Path("docs/difficulty-model-matrix.json").read_text())
report = json.loads(Path("/tmp/nexus-matrix-preflight.json").read_text())
verify_preflight_binding(matrix, report)
```

Identity verification is not report authentication. Trust operator-produced
reports and rerun the proof when in doubt.

## MindTrial setup and pilot decision

Use the existing persistent single-session adapter and manifest-driven action
contract. Remove wrapper assumptions about a `controller`, five/nine settings,
or a fixed numeric field: dynamics uses `stage` with three bits and `doser` with
eight ternary values. Keep `operate` and `probe` available; configure alone does
not commit a treatment. No MindTrial code or error-status behavior changes are
required by this implementation.

A suitable common task instruction is:

> Read the manifest and every listed evidence file. Investigate the artificial
> world using its public action contract, produce the exact required physical
> state, and finish successfully. Use NEXUS for all in-world actions and
> observations. Finite hypothesis enumeration is allowed. Return only the actual
> victory receipt from this live session.

Do not include the matrix, seeds, hidden structural labels, prior run solutions,
qualification reports, reference traces, or source code in player context. Give
each task only a neutral ID. In particular, the paired T0 control reveals a T3
target if context is shared. The audit demonstrates that revealing a narrow seed
pool can collapse the purported difficulty; secrecy of the hidden selection is
part of the evaluation boundary, not a replacement for a fully disclosed law prior.

Start with cells **01, 04, 05, and 10** on one or two representative models, with
the same reasoning/token allowance intended for the full run. Inspect actual
traces before expanding to all ten cells and all models. This is an empirical
calibration decision, not an extra implementation permission gate.

Record actual victory, scientific measurements, first-finish target classes,
failed finishes, actions after target resolution, active/terminal status,
reasoning-token usage, and stage timings. Separate scientific inference and
experiment selection from treatment execution, budget exhaustion, and receipt
formatting. If all challenge cases still solve compactly, classify the observed
shortcut before increasing scale. If failures only reflect tool/token limits,
adjust the harness allowance before attributing them to science difficulty.

Full rollout remains uncalibrated until the pilot supports a meaningful control/
challenge distinction. No model failure rate has been measured for this family.

