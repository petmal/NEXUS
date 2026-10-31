# GLM and MiniMax controls with structured output disabled

31 October 2026, America/Toronto. Source: `smoke-test-v1.zip`.

## Result and decision

**Both models passed both controls.** Independent replay confirms four
evidence-supported world victories and four accepted final receipts. All 42
tool calls completed successfully, with no malformed requests or rejected world
actions. The corrected integrations are ready for the existing fourteen-row
challenge screen: **28 new attempts in total**. No additional control rerun or
new package is needed before that screen.

This strongly supports the user's diagnosis that structured final output was
interfering with the earlier GLM/MiniMax runs. The original GLM attempts made no
tool calls; the original MiniMax attempt repeatedly omitted required arguments.
Those are configuration-sensitive integration outcomes, not evidence that these
models cannot solve the disclosed NEXUS controls.

## Verified results

S05 is the disclosed revision control, with a four-action reference solution and
64 actions available. S21 is the disclosed repair control, with a five-action
reference solution and eight actions available. Each attempt read all three
public evidence files and succeeded on its first finish submission.

| Model | Row | Accepted actions / reference | Actions left | Tool calls | Request time | Output tokens, including reasoning |
|---|---|---:|---:|---:|---:|---:|
| GLM 5.2, xhigh | S05 | 4 / 4 | 60 | 9 | 22.56 s | 2,501 |
| GLM 5.2, xhigh | S21 | 6 / 5 | 2 | 11 | 30.65 s | 4,343 |
| MiniMax M3, default | S05 | 4 / 4 | 60 | 9 | 11.82 s | 1,534 |
| MiniMax M3, default | S21 | 8 / 5 | 0 | 13 | 24.46 s | 4,949 |

Request time is MindTrial's aggregate provider-request duration, not end-to-end
task wall time. Across the two controls GLM records 53.21 seconds of requests,
13.24 seconds of tool runtime and approximately 86 seconds of logged task wall
time. MiniMax records 36.28, 14.71 and 73 seconds respectively. Wall times have
one-second log precision and include service/validation/rate-limit overhead;
these components should not be assumed to add exactly.

Before MindTrial started, the GLM launcher spent 313 seconds in setup, including
280 seconds of recorded mechanical qualification. MiniMax setup took 277 seconds,
including 272 seconds of qualification. Thus most elapsed setup time came from
preflight rather than model reasoning. `--skip-build` still qualifies the image;
it does not skip that work. The timings are useful framework overhead data,
not evidence that either model was looping during these successful runs.

GLM records 79,807 input tokens and 6,844 output tokens, including 6,562 reasoning
tokens. MiniMax records 98,813 input tokens and 6,483 output tokens, including
5,275 reasoning tokens. Both report cache reads within input totals and reasoning
within output totals: do not add those subcounts again. These four attempts are
too few for a general efficiency ranking. The prior incomplete MiniMax run has
no usage total, so no before/after token-cost reduction can be calculated.

## What the action traces reveal

Both S05 traces follow the four-action reference sequence: take the carrier,
configure the assembler, operate it and finish. Neither spends actions on
measurements after receiving the disclosed solution information.

On S21, GLM takes the seal and also takes stock, moves to the array, configures
the doser, operates it on the seal and finishes. The extra stock acquisition is
unused. That one unnecessary action explains six actions against the reference
five; there is no tool failure or wrong repair.

MiniMax first moves from stores to the array without the seal, returns to stores,
takes the seal and unused stock, then moves to the array again and completes the
same repair. The unnecessary round trip costs two actions and the unused stock
costs one. It wins on action eight, leaving **no spare action**.

This is a useful early planning observation. The same pass count hides different
amounts of wasted work, and MiniMax's successful attempt uses all available
slack. It motivates the existing matched budget comparisons. It does not yet
establish a P/R failure boundary: we have one attempt per control, and the model
could choose a different plan under a different allowance. Do not invent a new
tighter control or alter prompts before running the prepared screen.

## Interpreting the output-mode change

The two new configs set `disable-structured-output: true` at provider-run level.
Both the input/effective configs and the recorded `RunConfig` confirm the flag.
Compared with the original structured-output presets, the only config changes
are this flag and the display name identifying “text output.” Model identifiers,
effort settings, RPM, token ceilings, task objects, world inputs, evaluation seed,
tool schema and receipt validator are unchanged. The actual MindTrial binary
hash is also identical between the original and corrected attempts.

The new source commit and image differ because this was a newly pinned package;
the installed NEXUS runtime digest is identical. The launcher is now explicitly
non-interactive, with complete 2/2 saved coverage in both groups and zero process
and launcher exit codes. It executed the requested rows without the selection
ambiguity or empty output seen in the earlier cancelled run.

The comparison gives strong practical evidence for keeping text output enabled
for these models in NEXUS. It is not a randomized causal estimate of one decoder
feature: output mode also changes MindTrial's final-answer instructions and
parsing, the calls occurred at different times, OpenRouter's upstream route is
not pinned, and generations remain stochastic. It does not prove a universal
GLM/MiniMax limitation across providers or all structured-output schemas.
Further structured-mode reruns are unnecessary for moving this NEXUS experiment
forward; they would serve a separate integration investigation.

Preserve the original attempts as a separate configuration cohort. For subsequent
T/D contrasts, pair the text-output screen with **these text-output controls**,
not the earlier structured-output failures. Do not count the recovery itself as
a T/D or P/R effect. Successful disclosed controls also do not establish ability
to discover hidden laws.

## Next run

Use the existing **v3 package** and its already built image:

```bash
cd ~/Downloads/NEXUS-capability-smoke-test-run-2026-10-31-v3
bash run.sh --model glm --suite screen --non-interactive --skip-build &&
bash run.sh --model minimax --suite screen --non-interactive --skip-build
```

Keep `OPENROUTER_API_KEY` available. This runs fourteen rows for each model,
without repeating S05 or S21. The current v3 source/image pin remains valid even
though this analysis is committed later. Retain every result folder, including
any interruption or provider error.

The screen covers interference 09/11/25/27; stateful S01/S02/S03; hidden revision
S08; hidden repair S22/S23/S24; and spatial S13/S16/S17. Its primary resource
contrasts are 09↔25, 11↔27, S22↔S23 and S16↔S17. S05↔S08 is a joint T/D
contrast, and 09↔11 combines horizon and dependencies. Interpret those compound
contrasts accordingly. Preserve action inefficiency alongside win/receipt and
evidence-support outcomes, especially for MiniMax.

Grok's screen can also proceed if still pending. Muse's S21 receipt-delivery
repeat and Mistral's response-format diagnostic remain separate; this ZIP
contains neither and provides no new evidence about them. Avoid `--suite all`,
which would repeat completed controls.

## Audit trail

- Archive SHA-256: `a9d07d654dba161af15fed702f39ca2f0c5b5ff28d2d22b4a06580ad07b5a07e`.
- Evaluated NEXUS commit: `92fa0888546498373f4c011a79778b7caf614f12`.
- Runtime source SHA-256: `ba22502788acf7ce1684e1e527e5aa332cd1746b37423fececabc90d71b8ee83`.
- MindTrial binary SHA-256: `95c57d56e3d8739c19c4be1d33ec8de876c6522a003704c4f2d277978baf8660`.
- Evaluation seed: `nexus-cross-axis-pilot-v1`.

The audit verifies config/task hashes, source/image bindings, stored qualification
against the committed report, per-result model settings and launcher coverage.
It joins trace/call identities, regenerates each world and exactly replays all
42 public responses and 22 accepted actions. All 19 captured action-hash records
match, as do captured operator snapshots and terminal performance. Four final
answers match their emitted receipts and their recorded accepting validators.
The original private HMAC secret is not available; replay uses a fresh secret
and does not claim to recompute original HMACs.

[Compact results and provenance](capability-text-output-controls-2026-10-31.json)
accompany this report. The downloadable audit bundle contains the parser,
replay program, detailed derived output and reproduction instructions. Raw user
logs are kept out of Git. No live model calls, engine changes or new scientific
qualification are part of this analysis; it checks the qualification already
recorded for the evaluated worlds.
