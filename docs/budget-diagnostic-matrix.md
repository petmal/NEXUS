# Eight-execution action-budget diagnostic

Machine-readable configuration: [budget-diagnostic-matrix.json](budget-diagnostic-matrix.json).
These are **eight executions total**, not eight tasks for every model. Each row
starts a new world and a fresh model context. Do not give players the table, seeds,
previous transcripts, operator diagnostics, or [episode guide](compositional-pilot-guide.md).

## Runs

| Order | Model and reasoning | Original cell | Seed | Profile | Actions | Question |
|---|---|---|---:|---|---:|---|
| 01 | Gemini 3.8 Flash, high | 05 | 438 | `standard` | 30 | Fresh baseline for the passive-only failed investigation. |
| 02 | Gemini 3.8 Flash, high | 05 | 438 | `diagnostic-plus6` | 36 | Does extra room lead to a useful intervention and a justified repair? |
| 03 | Gemini 3.8 Flash, high | 07 | 493 | `diagnostic-plus6` | 36 | Does it avoid the previously evidence-contradicted retry? |
| 04 | Gemini 3.8 Flash, high | 07 | 493 | `standard` | 30 | Paired baseline; earlier replay proved an informed 30-action win was possible. |
| 05 | Gemini 3.8 Flash, high | 08 | 542 | `standard` | 30 | Fresh baseline for the correct seal reached without a successful finish. |
| 06 | Gemini 3.8 Flash, high | 08 | 542 | `diagnostic-plus6` | 36 | Does slack restore both completion and evidence sufficiency? |
| 07 | Grok 4.7, xhigh | 05 | 438 | `diagnostic-plus6` | 36 | Can more investigation resolve uncertainty despite using interventions already? |
| 08 | Grok 4.7, xhigh | 05 | 438 | `standard` | 30 | Paired baseline for its compatible-but-wrong final repair. |

Pairs run in alternating condition order to reduce a simple order effect. Run
only the specified model on each row. Rows 01–02, 03–04, 05–06 and 07–08 are pairs.
Keep the same image, prompt, tool schema, provider settings and stopping limits
within every pair. Use provider model IDs `gemini-3.8-flash` and `grok-4.7`; record
the resolved revision if the provider exposes it. These IDs/settings come from
the pilot artifacts, not a claim that a mutable provider alias is pinned forever.

## Setup

All rows use axes-v2, `compositional-repair-v1`, T3/D5/P1/R1. The extra profile
adds six actions above the ordinary 30, leaving the science unchanged. It is a
**diagnostic condition**, not an ordinary R1 score or a new R level.

Common service environment:

```yaml
NEXUS_AXIS_VERSION: "2"
NEXUS_SCIENCE_FAMILY: compositional-repair-v1
NEXUS_THEORY_LEVEL: "3"
NEXUS_DISCOVERY_LEVEL: "5"
NEXUS_PLANNING_LEVEL: "1"
NEXUS_RESOURCE_PRESSURE: "1"
NEXUS_GENERATION_TIMING: "true"
NEXUS_EXTENDED_DIAGNOSTICS: "true"
```

Set `NEXUS_SEED` and `NEXUS_BUDGET_PROFILE` from each row. Keep these operator
environment variables off the player prompt. The player sees its actual budget
through the ordinary observation. No special refill or extra action is added.

- No external Python or source access; ordinary NEXUS interface only.
- Tool-call ceiling: 120 per execution, including non-consuming calls. This is
  deliberately above the environment's action allowance.
- Gemini: `thinking-level: high`; preserve the pilot's unset output cap and other
  provider defaults, including `media-resolution: high`, 3 requests/minute.
- Grok: `reasoning-effort: xhigh`, `max-completion-tokens: 65536`, 30 requests/minute;
  retain the existing retry policy (3 attempts, initial delay 30 seconds).
- Preserve remaining sampling, provider and harness limits from the pilot. Do not
  raise both action and token budgets in this experiment. Keep validation-on-error
  behavior unchanged. A provider retry must not silently create a new NEXUS world.
- Preserve complete service stderr, player tool inputs/outputs, final answers,
  provider finish reasons, usage accounting and image OCI revision. Service stderr
  is private operator material and must never be returned as player tool output.

## Preflight the actual image

Build the latest feature head with its OCI revision, then run:

```bash
docker run --rm --entrypoint python YOUR_NEXUS_IMAGE scripts/preflight_budget.py --output /tmp/budget-preflight.json
```

The command must exit zero and print `diagnostic-ready`. To retain the full report,
mount an operator output directory and use that path for `--output`, for example:

```bash
docker run --rm --mount type=bind,source=/absolute/operator-output,target=/out --entrypoint python YOUR_NEXUS_IMAGE scripts/preflight_budget.py --output /out/budget-preflight.json
```

Preflight generates all eight cells, checks their compiled qualification, runs a
public-evidence reference policy, verifies live victory and exact replay, and
compares each pair's entire scientific world, reference actions and event payloads.
Every selected witness uses 24 actions in both conditions. Reports bind to the
installed Python source and exact matrix; regenerate after any source/image change.
This does not execute a model or guarantee that a model will pass.

## Reading the results

Report three outcomes separately: **live escape**, **evidence-supported escape**,
and **accepted final receipt**. The new `mission-performance-v3` data adds:

- Per-submission evidence: `guaranteed` (every remaining world accepts it),
  `compatible` (only some do), `contradicted` (none do), or `ineligible` (the
  physical prerequisites are missing). These are support counts, not probabilities
  or a judge of the model's private reasoning.
- `correct_state_without_successful_finish`: the final physical goal holds but no
  successful finish occurred. This still counts as a failed game.
- Remaining worlds/common repairs, measured contexts, passive/intervention reading
  counts, first intervention and first evidence-supported repair opportunity.
- Extended operator reports include a reading-by-reading timeline. The private
  journal emits a binding and one entry per committed action. Graceful shutdown
  reports unfinished sessions without changing their state. Hard kills may omit
  that final report; reconstruct from the journal and harness trace instead.
- The validator separately logs `accepted_receipt`, `won_receipt_mismatch` or
  `mission_not_won`, without changing its result. NEXUS cannot infer provider length
  stops, refusals, quota errors, or whether malformed final text came from a model
  or an integration layer; join the external harness evidence explicitly.

If 36 actions produces more **supported** escapes, budget pressure is a plausible
contributor. If it produces only more compatible guesses, completion improved
without demonstrating stronger investigation. Repeated passive readings or a
contradicted submission despite extra actions point toward experiment selection
or evidence application. A fixed provider length stop is a different limit.

Expected relative difficulty: the 36-action condition is mechanically no harder
and permits up to two additional ordinary experiments, but each seed has exactly
the same information problem as its 30-action counterpart. Do not claim a strict
difficulty ordering between the three seeds from one pilot. In particular, seed
438 cannot be resolved by collecting more passive observations alone.

One execution per condition is a screening diagnostic. Improvements may reflect
sampling variation; use matched repeats before making causal or population claims.
Do not run a broad model sweep until these eight results have been reviewed.
