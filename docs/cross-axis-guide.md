# Cross-axis smaller-model pilot

29 October 2026. This is a screening experiment, not a model ranking or a claim that one numerical axis has a universal difficulty scale. It reuses qualified worlds and separates world reasoning from interface access. No new world mechanics are introduced.

## What to run

The package defaults to `--suite canary`: eight existing interference conditions for Astra, Luna and Gemini Flash, 24 attempts. Inspect those results before running `--suite followup` (96 more attempts). `--suite all` explicitly requests all 120 attempts; canary conditions occur only once. Every attempt starts a fresh world. Automatic provider retries are zero.

| Suite | Conditions | Models | Attempts |
|---|---|---|---:|
| canary-core | Interference 09–12 | Astra, Luna, Flash | 12 |
| canary-slack | Interference 25–28 | Astra, Luna, Flash | 12 |
| rerun-core | Interference 01–08, 13–16 | Astra, Luna | 24 |
| rerun-slack | Interference 17–24, 29–32 | Astra, Luna | 24 |
| smoke-td | S01–12, S21–24 | Luna, Flash | 32 |
| smoke-pr | S13–20 | Luna, Flash | 16 |

Aliases: `canary` runs the first two suites, `rerun` the next two, `smoke` the last two, and `followup` combines rerun and smoke. Individual suite names also work. The complete allocation is Astra 32, Luna 56 and Flash 32 attempts across 56 distinct task conditions. The 32 interference task dictionaries, prompts, worlds and budgets are retained from the earlier comparison. The family-neutral tool description and adapter diagnostics are new, so these are a new interface cohort, not additional samples under an unchanged harness.

The canary includes both horizon and coupling levels for seed 101, exact and slack budgets, including the long coupled condition that requires a whole-bank reopening. Its purpose is to expose interface problems early while exercising meaningful planning. A legitimate mission failure is useful evidence and is not a reason to discard or silently rerun a task. Check successful manifest/evidence access, exact outer tool arguments, stop reasons, receipts and provider interruptions. Preserve every attempt. If the contract changes after the canary, version the change and rerun affected controls; do not combine incompatible cohorts.

## Model choice

| Role | Native provider/model | Reasoning setting | Requests/minute |
|---|---|---|---:|
| Established control | openai / gpt-6-astra | medium | 20 |
| Efficient-tier continuity | openai / gpt-6-luna | medium | 20 |
| Efficient-tier second provider | google / gemini-3.8-flash | high thinking | 3 |

“Smaller” means efficient product tier here; parameter counts have not been established. Luna keeps continuity with the prior NEXUS trial. Among the 39 common text tasks in the supplied leaderboard, Astra and Flash each passed 39, while native DeepSeek Flash passed 38 and had one final-format error. Luna was absent. Flash made 184 detailed Python calls versus Astra's 18; 50 Flash call statuses were unsuccessful but all its text tasks recovered. NEXUS offers no external Python tool. These observations motivate a transfer test; they do not establish a NEXUS ranking or predict which model will fail.

Native DeepSeek Flash (`deepseek`, `deepseek-flash`, max reasoning) is the next candidate if a third efficient model is useful. It is deliberately absent from these configs to bound cost and avoid an unused credential requirement. A later separately named cohort should preserve its native route, `max-tokens: 65536`, `disable-structured-output: true`, 15 requests/minute and 15-minute request timeout from the supplied settings. Do not substitute the OpenRouter route. GPT-6.1 Sol is a possible same-provider bridge later; another near-ceiling model adds less value to this first screen.

Reasoning labels are not equal compute across providers. Keep settings fixed across paired rows. Google 3 RPM preserves the user's setting and may dominate wall time; it is not a claimed quota limit. The runner permits an intentional, recorded RPM change. Unsnapshotted model aliases do not pin immutable weights.

Leaderboard source: `mindtrial-eval-all-models-03-2026_42.json`, SHA-256 `e482c97b7ca390663f6f3fe621275380e395d061e98244de668ddbe8120779b7`. The comparison uses the same 39 exact text task names, not mixed multimodal denominators. Official API references checked 29 October: [Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [Gemini Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash), [DeepSeek updates](https://api-docs.deepseek.com/updates/).

## Smoke conditions and interpretation

T controls disclosure of the selected law. D in these retained families controls procedure/evidence conditions; it is not a common, graded measure of experimental depth. P changes the planning layout or structure. R changes the resource budget. Interpret only comparisons supported by the qualification, not the ordering of labels.

| IDs | Family and seed | Conditions | Purpose |
|---|---|---|---|
| S01–04 | Stateful discovery, 229 | T0 D0 P1 R1; T0 D5 P1 R1; T3 D5 P1 R1; T3 D5 P1 R0 | Procedure disclosure, selected-law disclosure, then action cap |
| S05 | Model revision, 5866 | T0 D0, principles guidance, C0/L0 | Disclosed execution control |
| S06 | Model revision, 468 | T3 D5, provisional guidance, C1/L2 | Short diagnostic structure |
| S07 | Model revision, 6467 | T3 D5, principles, C2/L4 | Moderate diagnostic structure |
| S08 | Model revision, 5866 | T3 D5, principles, C4/L4 | Same-seed compound T/D contrast to S05 |
| S09 | Model revision, 1101 | T3 D5, provisional, C4/L4 | Alternative guidance/world screen |
| S10 | Model revision, 438 | T3 D5, principles, C4/L5 | Longer identifying panel words |
| S11–12 | Model revision, 3 and 1185 | T3 D5, principles, C3/L6 and C2/L6 | Same-evidence rival pair agreeing through length 5 |
| S13–16 | Spatial planning, 21 | T0 D5, P0/P1/P2/P3, R2 | Minimum actions 11/16/20/22, budgets equal minima |
| S17 | Spatial planning, 21 | T0 D5 P3 R1 | Same minimum 22, budget 33 |
| S18–19 | Spatial planning, 31 | T0 D5, P0/P3, R2 | Minimum actions 10/19, budgets equal minima |
| S20 | Spatial planning, 31 | T0 D5 P3 R1 | Same minimum 19, budget 29 |
| S21 | Compositional repair, 438 | T0 D0 P1 R1, standard | Execution control, budget 8 |
| S22–23 | Compositional repair, 438 | T3 D5 P1 R1, standard / diagnostic-plus6 | Matched science, budgets 30/36 |
| S24 | Compositional repair, 493 | T3 D5 P1 R1, diagnostic-plus6 | Additional intervention-obstruction world, budget 36 |

Stateful S01/S02 isolates procedure disclosure, S02/S03 selected-law disclosure, and S03/S04 the world action cap (64 versus unlimited, with the same finite harness cap). S03 retains the full 256-world prior. These worlds keep state across actions; immediate probe previews do not advance the specimen history.

All revision rows use P0 R1, a 64-action budget, recoverable finish, and no consistency checker. C is an optimistic certificate length for the actual world; L is the maximum query-word length needed by the complete identifying query panel. Neither is a cognitive-depth measure or a minimax adaptive policy bound. Cross-seed C/L comparisons are structural screens, not isolated D interventions. S05/S08 changes both T and D. S11/S12 retain the full pair with identical public evidence and identical responses to every query word of length at most five. Seed 438 has fewer observable states than the older hard-tier threshold; L5 must not be called uniformly harder than every L4 world.

Spatial P3 requires joint route/operation planning: for seeds 21 and 31, the best total-action plans cost 22 and 19, whereas every operation-shortest route needs at least 25 and 24 total actions. Across P, R2 fixes the *budget rule* (exact optimum), not the absolute action count. P labels describe layouts, not a proven cognitive ranking. S16/S17 and S19/S20 isolate the budget change on identical worlds.

Repair S22/S23 isolates the named budget profile, although both retain numeric R1. S21/S22 changes T/D and budget together; it is an execution baseline, not an isolated T effect. Qualification retains the intervention-obstruction proofs: passive information alone cannot certify the repair for the relevant rivals. The extra six actions are diagnostic headroom, not new physics.

All new smoke tasks have a common ceiling of 600 tool calls and 650 conversation turns. This is larger than the historical T/D export's 120/160 limits and is explicitly a new harness condition. World budgets remain as listed. The interference exports keep their original harness limits. Evaluate per-attempt usage and truncation; a finite ceiling is still a possible source of failure.

## Interface and audit guarantees

The tool contract is `cross-axis-tools-v1`. Complete examples show the required outer `request` argument, including manifest, evidence, take, operate and configure. The actual parameter file contains only its inner object. The new `--tool-argument request` CLI option adds conditional mapping guidance when the file is missing; it does not silently wrap or repair arguments. Historical configs are unchanged. Controls are family-neutral, while each world's manifest remains authoritative for available actions and settings.

At MindTrial source commit `f8a723665fff16d395e581f63d806bebf61938f5`, OpenAI Responses forwards `toolCfg.Parameters` unchanged with `Strict: false`; Google forwards `ParametersJsonSchema: toolCfg.Parameters`. This is source-adapter evidence, not captured provider-wire evidence or a live compatibility test. Config-level schema/description/command hashes are recorded by the runner and must not be described as wire capture. Credentials resolve from `OPENAI_API_KEY` and `GOOGLE_API_KEY`; `GEMINI_API_KEY` is not an automatic fallback in that source version.

The runner builds the pinned commit, verifies image revision and runtime source identity, reruns qualification inside that image, compares exported tasks, and records image ID, executable hash, actual configurations, tasks, release and qualification reports. Both Docker `sha256:` IDs and Podman's bare 64-hex IDs are accepted. No model calls are made in `--preflight-only` mode. Source qualification covers current-source independent proofs, public-policy wins, deterministic replay, exact receipts, support diagnostics and matched controls. Passing qualification establishes the stated finite mechanics and controls; it does not establish psychological difficulty.

The result readout now preserves partial usage from `Details.Error` and joins logs by TraceID. It distinguishes confirmed access, confirmed no successful access, and unknown access. Missing/interleaved logs cannot establish a no-access failure. Reported wins are not relabeled as independently audited supported wins. Full receipt/replay auditing remains separate.

## Decision rules after live evaluation

1. Resolve interface/provider failures first. Report them separately from world-reasoning failures; retain them in the unconditional attempt denominator. Do not silently discard errors or compare success-conditioned subsets as causal effects.
2. Examine matched contrasts within each model: S01/S02, S02/S03, S03/S04, S16/S17, S19/S20, S22/S23, and the unchanged interference horizon/coupling/budget pairs. Use traces to separate excess probes, reversible detours, no-ops, early stopping and unsupported finishes.
3. Treat the revision C/L cohort and cross-family results as screens. One attempt per condition can locate a candidate boundary, not estimate a stable failure probability or prove monotonic difficulty. Repeat the most informative success/failure boundary with at least three independent attempts and matched fresh seeds before claiming an axis effect. Retain both the fixed-seed reproducibility panel and a separate fresh-seed generalization panel.
4. If Luna or Flash fails qualified worlds while Astra remains successful under the same contract, that is useful discrimination. The 24 new smoke conditions do not include a contemporary Astra run; repeat informative failures with Astra under this exact contract before attributing a gap to model choice. Historical Astra results used different harness conditions. NEXUS need not defeat Astra to be valuable. Expand the informative family/axis locally rather than increasing every dimension at once.
5. If both efficient models saturate, first confirm that the harness left useful headroom; then extend the qualified planning/dependency frontier or add the native DeepSeek cohort. Do not reopen a large T/D grammar search solely to force a failure. Preserve disclosed controls, matched interventions, exact verification and replay throughout.
