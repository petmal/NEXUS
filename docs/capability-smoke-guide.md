# Five-model capability smoke panel

Updated 2 November 2026. Controls, initial GLM/MiniMax screens and the requested
selected repetitions have been analysed. Other model followups remain unreported.
Read [the latest synthesis](research/smaller-model-synthesis-2026-11-01.md) and
[the consolidated findings](research/smoke-findings-2026-10-31.md) first.
The [2 November evening diagnostics](research/inference-diagnostic-results-2026-11-02.md)
add four supported MiniMax control wins (three accepted receipts), two MiniMax
world-budget losses and four GLM high/xhigh length stops. No 429 occurs at the
unchanged rate; the earlier [interruption](research/minimax-control-interruption-2026-11-02.md)
remains separate. The [later Stage C pair](research/glm-high-stage-c-2026-11-02.md)
adds a GLM high optimal 09 win and a 25 length stop after a fatal detour. Only
high S05/S21 controls remain absent; do not repeat the supplied planning rows.
Keep unchanged challenge repetitions paused. The launcher still stops subsequent groups on a
recorded 429; no lower-rate recovery claim follows from this batch.
The frozen specification is [capability-smoke-matrix.json](capability-smoke-matrix.json).

Do not repeat the entire unchanged GLM/MiniMax screen. The completed repetitions
recommend a MiniMax response/provenance diagnostic and a bounded GLM generation-
setting comparison before fresh qualified seeds and broader world changes.
The [follow-up matrix](inference-diagnostic-matrix.md) retains the original
18-attempt specification and records which stages are now supplied or paused. The revised launcher supports exact `--task-id`
selection and `--repeat` without interactive confirmations or task-file edits.
The [initial screen](research/capability-screen-results-2026-10-31.md) and
[text-output controls](research/capability-text-output-controls-2026-10-31.md)
remain historical comparison records. See [the initial control audit](research/capability-controls-results-2026-10-31.md)
for pending Grok, Muse and Mistral followups.
The revised launcher supports `--non-interactive` for configured unattended
runs and `--interactive` (the default) for manual rerun selection. Unattended
runs stop on incomplete result coverage even when MindTrial exits zero.
The v3 package changes only GLM/MiniMax output mode and run labels. Tasks,
scientific budgets, model effort and the receipt validator remain unchanged.

## Models and purpose

| Selector | MindTrial provider / exact model | Reasoning | RPM | Purpose |
|---|---|---|---:|---|
| `glm` | `openrouter` / `z-ai/glm-5.2` | xhigh (max) | 10 | Newer GLM requested; 30/39 text passes in supplied leaderboard |
| `muse` | `openrouter` / `meta/muse-spark-1.2-contributor` | xhigh | 10 | Requested inexpensive cross-family probe; 36/39 text passes |
| `minimax` | `openrouter` / `minimax/minimax-m3` | provider default | 10 | Additional 30/39 text candidate; reliability requires control checks |
| `mistral` | `mistralai` / `mistral-large-4` | high | 5 | Native-provider cost/diversity probe; 35/39 text passes |
| `grok` | `xai` / `grok-4.7` | **medium** | 20 | Moderate-effort probe; leaderboard xhigh passed 39/39 |

These are five model configurations, not a verified parameter-size ranking. GLM
and MiniMax are the clearest candidates with text-task headroom. Muse, Mistral and
Grok need not be weaker than Flash. Grok medium is deliberately different from
its leaderboard setting; do not label its results a replication of xhigh.
Effort labels cannot equalize compute across vendors. MiniMax has no invented
reasoning knob; its service default is a reproducibility limitation.

GLM and MiniMax now have **`disable-structured-output: true` at run level**,
alongside `model` and `model-parameters`. This restores the compatibility setting
the user reports needing in prior MindTrial evaluation. It removes MindTrial's
structured final-answer wrapper; the NEXUS tool JSON schema and exact receipt
validation remain in force. The original control archive used the structured
default, so keep the corrected “text output” attempts separate. Output mode is
pinned by the package contract; use the revised release rather than editing an
older package. Other models retain their original output settings. All four
corrected controls passed; keep their results separate from the initial
structured-output attempts when estimating axis effects.

Each completion is capped at 65,536 output tokens (Mistral `max-tokens`; others
`max-completion-tokens`). This is a ceiling per request, **not a total token or
spending cap**. The inherited 600-tool-call and 650-turn limits also remain.
RPM limits pace calls and do not cap spend. No price is hard-coded: routing,
caching and changed pricing make static cost estimates unreliable.

All providers have zero MindTrial retries. OpenRouter requests require support
for all supplied parameters and disable fallback routing. That does not pin one
upstream provider for the whole experiment; record returned provider/model
metadata when available. A no-eligible-endpoint error is an integration outcome,
not a NEXUS loss. Do not silently remove parameter requirements or change models
mid-cohort. Model or effort edits must be treated as separately labeled settings.
There are no provider-managed search, code execution or other server tools.

The Muse **Contributor** tier may use prompts and outputs to improve Meta's
products. This is the exact user-requested endpoint. Only the public NEXUS player
interface is exposed; operator reports and private qualification material are
not tools available to the evaluated model.

## Conditions and contrasts

The panel is a deterministic subset of the qualified cross-axis release. Task
objects, public prompts, world seeds, tool contract and harness ceilings are
unchanged. Evaluation seed remains `nexus-cross-axis-pilot-v1`. Source binding
changes at the release commit while installed world source remains the same.

| Stage | Existing rows | Count per model | Interpretation |
|---|---|---:|---|
| `controls` | S05, S21 | 2 | Disclosed revision and repair; check multi-turn integration and finish receipts |
| `screen` | interference 09, 11, 25, 27 | 4 | Tight/slack pairs 09↔25 and 11↔27; disclosed planning/dependency contrast |
| `screen` | S01, S02, S03 | 3 | Procedure removal then law hiding on one stateful world, same 64-action budget |
| `screen` | S08 | 1 | Hidden counterpart to control S05; joint T/D contrast |
| `screen` | S22, S23, S24 | 3 | Hidden repair; 30↔36-action pair and second world; S21 control |
| `screen` | S13, S16, S17 | 3 | Spatial P0↔P3 structural contrast and P3 tight/slack pair |

There are **16 unique conditions per model**, split 2+14. Five complete model
panels give **80 attempts**, with ten controls and seventy followups. Controls
are not duplicated in `screen`. `all` combines both stages exactly once and is
for deliberately running a complete panel, not for following completed controls.

09↔11 and 25↔27 change short independent work to long coupled work at the
same kernel seed. They are compound horizon/dependency screens, not isolated
coupling or length effects. Tight/slack comparisons preserve physical worlds.
Structural contrasts can change minimum work and derived budgets; these are
not single-factor cognitive interventions.
S01↔S02 and S02↔S03 are the cleaner disclosure comparisons; S05↔S08 changes T
and D together. Spatial P0↔P3 changes layout and required work. Seeds and row
numbers identify fixed cases, not independent samples from a difficulty level.

The screen intentionally omits redundant stateful uncapped S04, intermediate
spatial layouts and extra revision variants. S10's repeated compatible wins are
retained in the findings, but repeating its favorable world again is lower value
than the future qualified rival-world test. Astra anchors on revision/repair are
still outstanding; they are not silently added as a sixth model here.

## Admission, reruns and analysis

Run controls first. Inspect access to manifest and every listed evidence file,
valid calls over multiple turns, state persistence, stop reasons and any returned
receipt. A real world loss with a functioning interface does **not** disqualify
a model. Repeated provider/schema failures can block interpretation, so resolve
them before spending on the fourteen followups. The launcher does not infer this
scientific judgement from process exit status.

For a billing/transport rerun, retain original files and specify the affected
model and exact row selection in MindTrial. Never select a successful retry as
if it were the only observation. If interface settings change, label a new cohort
and rerun controls. Do not repeat successful rows accidentally by running `all`
after `controls` or `screen`.

Report attempted, completed, provider Error and world Failed separately. Report
mechanical and evidence-supported wins separately after replay. In failed worlds,
track unnecessary actions, earliest budget infeasibility, evidence sufficient for
a decision, inconsistent submissions and stopping with useful actions remaining.
Compare each model's matched pairs before comparing overall scores. Preserve raw
token usage and accounting conventions; missing usage is not zero cost.

One attempt per row is a screen, not a calibrated model ranking. Repeat selected
contrasts before drawing a boundary, then test new mechanically qualified seeds.
Keep all results, including empty launcher folders and partial attempts. The
convenience readout reports raw outcomes and conservative log access evidence;
it is not a canonical replay or a supported-win certificate. Concurrent task
logs can remain unknown in that summary even when a fuller audit resolves them.
The v3 readout preserves raw labels and separately reports response-length stops,
no-candidate errors, last observed world state and finalized performance. Detailed
invalid-argument calls remain accounted for even when aggregate ToolUsage omits
them. Configuration checks include output mode, extra parameters and retry policy;
reported token totals retain their accounting labels and partial-telemetry flag.

## API/source checks and limits

IDs and capabilities were checked 31 October 2026 against:

- [GLM 5.2](https://openrouter.ai/z-ai/glm-5.2), including high/xhigh support.
- [Muse Spark 1.2 Contributor](https://openrouter.ai/meta/muse-spark-1.2-contributor), including tools and Contributor terms.
- [MiniMax M3](https://openrouter.ai/minimax/minimax-m3), including tools.
- [Mistral Large 4](https://docs.mistral.ai/models/mistral-large-4-0), native ID and tools.
- [Grok 4.7](https://docs.x.ai/developers/models/grok-4.7), including medium effort and tools.
- [OpenRouter routing](https://openrouter.ai/docs/guides/routing/provider-selection), parameter support and fallback controls.

Read-only inspection of MindTrial `f8a723665fff16d395e581f63d806bebf61938f5`
confirmed config API-key fallbacks in `config/utils.go`, inline OpenRouter request
parameters in `config/config.go`, forwarding and reasoning continuity in
`providers/openrouter.go`, and native Mistral effort forwarding in
`providers/mistralai.go`. The supplied leaderboard records Muse's exact
Contributor model and xhigh setting, Mistral's ID/high setting, and Grok's
ID/xhigh setting. Older GLM/MiniMax entries lack full RunConfig snapshots.

This is source/config verification, not capture of transmitted provider requests
or proof that the locally built binary has those exact bytes. The launcher hashes
the user's actual binary on every run; live controls resolve remaining service
compatibility uncertainty. No MindTrial repository modification is required.
