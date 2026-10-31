# Five-model control results

31 October 2026. Source: `multi-model-smoke-control.zip`, SHA-256
`ea72e5a6e1273aa3384e744a2663927d09f78a4acdf22ce848c3fc550e4e71bc`.
These are integration controls, not measurements of T/D or P/R difficulty.

## Main finding

**Followup:** the [text-output control rerun](capability-text-output-controls-2026-10-31.md)
now passes all four GLM/MiniMax attempts. Both advance to their screens. The
original archive and interpretation below remain as a historical record.

**Configuration correction, 31 October:** The user reports that GLM and MiniMax
required `disable-structured-output: true` in their prior MindTrial evaluations.
The presets used in this archive omitted that run-level flag, leaving structured
final output enabled. This makes output-mode compatibility the first hypothesis
to test before broader interface debugging. The v3 run package sets the flag for
these two models and labels their runs “text output.” Repeat **S05 and S21 for
both models** with all other experimental settings unchanged. These four attempts
supersede the generic interface-diagnostic recommendation below as the immediate
next step. The original results and provenance remain unchanged; a causal effect
of output mode is not established until the reruns are observed. Changing the
mode also changes MindTrial's final-answer instructions/parsing, so it tests that
integration configuration as a whole, not an isolated decoding mechanism.

Grok is ready for the fourteen-row challenge screen. Muse also demonstrated
working world interaction, but needs a repeat of S21 to check final-answer
reliability. Hold GLM, MiniMax and Mistral challenge runs while diagnosing their
interface or response failures. Making the worlds harder would currently mix
those failures with the reasoning effects we want to measure.

Ten attempts were planned; nine started and eight produced complete result
records. Those records contain three Passed, three Failed and two Error results.
MiniMax's interrupted S05 has no result record; its S21 never started. Independent
replay establishes **five supported world victories**, of which **three produced
accepted final answers**. Neither 3/10 nor 5/9 is a useful reasoning-accuracy
estimate: the conditions are easy controls and the missing/error outcomes have
different causes.

S05 discloses the revision law and solution procedure, with a 64-action budget
and a four-action reference solution. S21 discloses repair laws, with eight
actions available and a five-action reference solution. The same two tasks,
world inputs, prompts and evaluation seed were used for all five configurations.

| Model setting | S05: reported result / world | S21: reported result / world | Next action |
|---|---|---|---|
| GLM 5.2, xhigh | Failed / no interaction | Failed / no interaction | Diagnose missing tool use |
| Muse Spark 1.2 Contributor, xhigh | Passed / won in 4 actions | Failed / won in 6 actions | Repeat S21 once, then screen if answer delivery works |
| MiniMax M3, default | Interrupted / 0 actions | Not started | Diagnose missing tool arguments with a bounded interface test |
| Mistral Large 4, high | Error / active after 5 actions | Error / won in 6 actions | Diagnose final-response format and termination |
| Grok 4.7, medium | Passed / won in 4 actions | Passed / won in 5 actions | Run fourteen screen rows unchanged |

## What happened

**GLM:** Both attempts ended after the first model response, with zero tool calls.
One response announced an intention to call the tool; the other returned
`NEED_TO_INTERACT`. Neither accessed the world or its evidence. The terminal
failure recorded after harness finalization therefore does not establish an
inability to infer laws or plan. Logs are insufficient to assign responsibility
between the model, provider route, tool schema handling and harness integration.

**Muse:** S05 was optimal and produced a valid receipt. S21 had one rejected
attempt to configure apparatus from the wrong room, then completed the world
with six accepted actions. It read all three evidence files in each control.
Its final S21 answer appended explanatory prose to the actual victory receipt.
The exact-answer validator correctly rejected that answer. Keep this as a
reported failure and a supported world win; do not trim the answer and change
the official result. This is a delivery-reliability issue, not a failed repair
plan. One unchanged S21 repetition can check whether it recurs, but cannot
estimate a reliable failure rate.

**MiniMax:** Cancelling was reasonable. The log records 194 conversation turns
and 194 tool-call starts, of which 193 completed. There was one valid manifest
request and 82 valid observations. Another 65 completed evidence requests omitted
the filename, and 45 completed action requests omitted the action object. The
last evidence request was also missing its filename, but has no captured result
and must not be counted as another completed error. In total, 110 completed calls
were malformed. No evidence file was read and **no world action was accepted**;
all 64 world actions remained available.

Reads and malformed requests do not consume the world's action budget. The
separate 600-call/650-turn harness limits allowed this loop to continue. Extra
world budget would not help. The trace demonstrates repeated missing arguments;
it does not show whether the model omitted them in the upstream request or an
adapter lost them. There is no completed usage record, so its token use and cost
are unknown, not zero. Its empty JSON/HTML files and exit code zero are an
incomplete run, not a successful or complete evaluation.

**Mistral:** S05 performed five actions, including unnecessary reader operations,
then returned `[1]`. MindTrial expected its structured result object and could
not parse this array. The world was still active with 59 actions left. This
early stop is not evidence of action-budget exhaustion.

S21 reached a supported world victory with two actions left. It then spent about
another four minutes and 25 seconds producing a final response: a bare receipt
followed by hundreds of repeated JSON explanations. The receipt appears 410
times in the captured raw response. The final stop reason was `length`; parsing
failed because the output was not the expected JSON object. Thus a short world
solution still led to a large, unsuccessful response. The two attempts used
13,596 and 75,910 recorded output tokens respectively, including reasoning as
reported by that provider. These are totals across requests, so the latter does
not contradict the 65,536 per-request completion limit.

The [exact MindTrial adapter source](https://github.com/petmal/MindTrial/blob/f8a723665fff16d395e581f63d806bebf61938f5/providers/mistralai.go)
requests a result JSON schema by default and parses the final response into
`providers.Result`. It also supports an unstructured-output path. A controlled
comparison of those paths is a reasonable diagnostic, not a proven fix for
repetition or early termination. Do not silently extract a receipt from the
failed response or change the validator to count this run as Passed.

**Grok:** Both worlds were completed in the reference number of actions, all
evidence files were read, and both exact receipts were accepted. There were no
invalid calls or actions. This establishes working integration on the controls;
it does not establish resistance to the challenge rows or rank Grok above the
other models in reasoning ability.

## Audit and limits

All five folders bind to NEXUS commit
`ad5b9d2f4fec2fb4626672a9d01cad97d540b3d4`, runtime source digest
`ba22502788acf7ce1684e1e527e5aa332cd1746b37423fececabc90d71b8ee83`, the same
immutable image and evaluation seed `nexus-cross-axis-pilot-v1`. Their configs,
task exports, contracts and recorded file hashes match the release. The
MindTrial binary hash is
`95c57d56e3d8739c19c4be1d33ec8de876c6522a003704c4f2d277978baf8660`.

The audit joins log entries by explicit trace and call identities, regenerates
each world, and replays all **146 valid public responses and 30 accepted actions**.
All **28 captured action hash records** match. Captured operator snapshots and
terminal performance records match replay points. Fresh replay secrets were
used; the original private HMAC secret was not available. Original receipt
acceptance is asserted only where the recorded validator actually accepted it.
Mistral's world win is established by replay, not an invented validation result.

The [compact audit data](capability-controls-results-2026-10-31.json) preserves
row outcomes and provenance. A separate reproducible audit bundle retains the
parser, replay script and detailed audit, without putting raw user logs in Git.
No paid model evaluation was performed during this analysis.

The archive does not capture full provider wire requests/responses. It cannot
fully localize missing tool calls or arguments. Provider token conventions also
differ: Grok's output count excludes separately reported reasoning, whereas the
other completed records include it. Avoid naive token comparisons, guessed
MiniMax cost or a pooled model ranking from these controls.

## Next sequence

1. Run **Grok `screen` only**, all fourteen rows, with the existing settings and
   matched controls retained from this archive. There is no reason to repeat its
   controls. Keep the same tasks, world seed and evaluation seed.
2. Repeat **Muse S21 only**, unchanged, using interactive selection. If it delivers
   the exact receipt successfully, run its fourteen-row screen. Retain both S21
   attempts and report world success separately from final-answer acceptance.
3. For GLM and MiniMax, use a separately labeled, short interface diagnostic:
   manifest, named evidence read, then one correctly nested action. Inspect the
   provider wire/schema boundary. A proposed 20-call/30-turn limit would bound
   that diagnostic; it must not silently replace the scientific panel's limits.
   For Mistral, compare structured and unstructured final-response handling on
   the controls, with a bounded response budget. Any changed setting is a new
   integration cohort and needs its own controls before challenge comparisons.
4. Do not launch the three held challenge panels until their failures are
   understood. The existing T/D and P/R conclusions remain unchanged. Once
   integration works, use paired challenge results to locate useful difficulty
   boundaries, then repeat the informative pairs rather than the whole matrix.

## Launcher revision

The revised package adds mutually exclusive `--non-interactive` and
`--interactive` options. Interactive remains the default and preserves manual
model/task selection. Non-interactive passes `--interactive=false` to MindTrial,
closes terminal input and keeps progress output visible.

After a zero process exit, unattended mode checks for exactly one completed
result record per enabled provider/run/task, with unique trace IDs. Missing,
empty, malformed, duplicated or unexpected results stop the batch with launcher
exit code 2; the original process exit and artifacts are preserved. Failed,
Error and Skipped records are recorded outcomes, not successes, and do not by
themselves stop the batch. Completeness is not a scientific admission decision.
Do not use `--suite all` expecting an automatic control-quality gate.

Interactive subsets are intentionally exempt from full-matrix coverage checking.
The summary helper now preserves missing/empty result files as zero completed
records with missing expected slots instead of crashing. It does not reconstruct
interrupted MiniMax progress; that comes from the detailed log audit above.
