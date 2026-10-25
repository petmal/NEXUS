**NEXUS: assessment of the completed T/D evaluation cycle**

24 October 2026 — America/Toronto. Analysis of the five supplied JSON/log pairs, covering all 40 planned executions on 23–24 October. No new model evaluations were launched.

**The bounded screen is complete, and its main investment decision is now clear.** All 40 executions won the live mission and returned accepted receipts. The screen did not establish a terminal-failure tier from the tested T/D contrasts. It did establish a useful distinction between operational success and evidence-supported commitment, with a strong descriptive change under single-shot rules. I recommend closing this round of intrinsic T/D expansion, retaining model revision as a diagnostic component, and directing the main development effort toward a qualified two-module challenge. Keep the 20-run reserve conditional; there is no reason to spend it simply because it remains available.

This conclusion is narrower than “T/D cannot be hard.” These are selected worlds in a bounded grammar, evaluated with particular model aliases, effort settings, tools and budgets. Successful final behavior also does not establish a model's private reasoning method.

**What was tested.** Model revision asks the player to reconstruct a four-link routing cartridge from exact primitive laws and observations. There are 20,736 permitted ordered constructions and 748 distinct all-history behaviors. Reader queries are binary words of length 1–8, each starting from a fixed inventory and returning one final display. A successful build must match the reference for every finite history, including longer histories. Equivalent constructions are accepted. Failed eligible finishes normally supply binary feedback and allow recovery. The explicit single-shot condition ends the episode at the first eligible wrong finish. The optional checker tests only consistency with the archive and observed reader outputs; it does not establish full correctness or incorporate rejected-finish feedback.

The screen used a 64-action budget, with planned caps of 120 tool calls and 160 conversation turns. All scientific rows were T3/D5/P0/R1; the supplied-construction control was T0/D0. Main investigative rows used principles guidance; seeds 1101 and 468 retained provisional guidance. Astra used medium reasoning; Gemini 3.8 Flash used high thinking. Neither model had an external programming tool in the supplied execution traces.

A **supported** submission succeeds under every behavior still consistent with the public history before that finish. A **compatible** submission fits some remaining possibilities but leaves a conflicting alternative. A **contradicted** submission is already excluded. These are evidence classifications, not probabilities. Rejected finishes can legitimately supply additional evidence; winning feedback is not used retrospectively to promote an unsupported submission.

| Condition | Runs | First submission correct | First submission supported | Final win supported | Accepted receipt |
|---|---:|---:|---:|---:|---:|
| Astra baseline | 24 | 16/24 | 13/24 | 18/24 | 24/24 |
| Astra single-shot | 10 | 10/10 | 10/10 | 10/10 | 10/10 |
| Gemini baseline | 2 | 2/2 | 2/2 | 2/2 | 2/2 |
| Gemini verification prompt | 2 | 2/2 | 2/2 | 2/2 | 2/2 |
| Gemini checker | 2 | 1/2 | 1/2 | 2/2 | 2/2 |

Across the complete screen, 31/40 first submissions were actually correct, 28/40 were supported, and 34/40 final wins were supported. These pooled counts describe coverage, not a common population success rate. The baseline includes two shortcut and two known-construction executions. Removing those controls leaves Astra with 9/20 supported first submissions and 14/20 supported final wins on the investigative rows.

**The single-shot comparison is the strongest new signal.** The correct comparison uses only the five worlds present in both conditions: seeds 5866, 6464, 6467, 678 and 1293, each repeated twice. Comparing all 24 baseline runs against the ten single-shot runs would mix different case distributions.

| Matched Astra contrast | Recoverable finish | Single-shot finish |
|---|---:|---:|
| Executions | 10 | 10 |
| Correct first submission | 4/10 | 10/10 |
| Supported first submission | 3/10 | 10/10 |
| Supported final win | 6/10 | 10/10 |
| Accepted receipt | 10/10 | 10/10 |
| Contradicted submissions | 4 | 0 |
| Median reader measurements | 8 | 8.5 |
| Mean reader measurements | 7.7 | 9.3 |
| Median world actions | 22.5 | 21 |
| Mean world actions | 22.4 | 22.6 |
| Median tool calls | 27.5 | 26 |
| Median generated tokens, including reasoning | 5,467 | 6,414.5 |
| Median reported duration | 129.5 s | 148.5 s |

Single-shot runs gathered more measurements on average and avoided failed-build recovery, leaving mean world-action expenditure nearly unchanged. Generated-token and duration medians increased. This is a change in the observed balance between investigation and commitment, rather than evidence that the hidden mechanism became intrinsically harder. It also shows that recoverable failures were not necessary for success on these selected worlds.

The sample supports a practical working hypothesis: the consequences of an incorrect commitment influence the evidence standard used before acting. It does not identify the model's intentions or establish a population causal effect. The arms ran in separate time blocks, used different harness evaluation seeds, and supplied different policy disclosures. The five worlds belong to one balanced rival triple and one rival pair, rather than five independent structural groups. Fresh, interleaved confirmation is warranted only if this policy distinction will affect benchmark design.

**Four baseline submissions repeated a rejected behavior under different wiring.** All four contradicted submissions were refuted by an earlier failed finish, not by an earlier reader measurement. In baseline-02-r1 and baseline-03-r1, Astra submitted `[3,4,11,7]` after `[3,4,8,10]` had failed. Those programs are behaviorally equivalent. In both baseline-08 repeats, `[0,2,4,3]` repeated the rejected behavior of `[0,1,4,3]`. Independent all-history checks confirm both equivalences.

This is a narrower issue than inability to infer the primitive laws: feedback was not carried through behavioral equivalence when selecting the next build. The current literal repeated-build counter correctly reports zero, but that alone hides all four events. Add a separate private count for resubmitting an already rejected **behavioral class**, while preserving the existing literal counter. Do not automatically give this equivalence oracle to the player.

Astra's six compatible final wins retained two to four behavior classes. They are legitimate mission successes, but do not establish sufficient evidence before commitment. Three Astra supported final wins first acquired support through rejected-finish feedback. Across both providers, four runs first acquired support this way; two known-construction controls had support initially, 28 acquired it through a reading, and six never acquired it before winning.

**Gemini's earlier seed-1101 failure did not recur in the fresh baseline.** Both baseline runs now made one supported, correct submission, using 39 and 51 actions. The earlier two failed attempts remain valid historical observations, but this screen does not support treating that cell as a stable failure case. Changed source/instrumentation and possible prompt or provider differences, together with small samples, prevent attributing the change to a particular cause. Record the old and new cohorts separately.

The verification prompt also produced two supported first-submission wins, so there is no success-rate improvement to attribute to it. Both checker runs eventually won with support; one first submitted a compatible but wrong build. The checker correctly accepted that build as consistent with the readings then available. This is expected behavior under its disclosed scope, not a checker defect.

| Gemini seed-1101 condition | Baseline | Verification prompt | Checker |
|---|---:|---:|---:|
| World actions, runs 1 / 2 | 39 / 51 | 49 / 51 | 36 / 33 |
| Reader measurements, runs 1 / 2 | 18 / 24 | 23 / 24 | 15 / 15 |
| Tool calls, runs 1 / 2 | 44 / 56 | 54 / 56 | 79 / 49 |
| Checker calls, runs 1 / 2 | 0 / 0 | 0 / 0 | 38 / 11 |
| Supported first submissions | 2/2 | 2/2 | 1/2 |
| Median generated tokens, including reasoning | 81,672.5 | 70,460 | 56,735 |
| Median reported duration | 678.5 s | 621.3 s | 566.2 s |

The checker condition used fewer physical measurements and world actions, but more tool calls. Across its two runs, it answered 49 checks: 28 false and 21 true. It therefore supplied substantial explicit computation over existing evidence, even though it disclosed no new physical observation. This may be useful assistance, but it measures a different exposure condition and should remain separately labeled. Two repeats do not establish a reliable cost advantage, and the results do not demonstrate a construction-consistency repair effect because the fresh baseline already submitted consistent constructions.

Gemini still often continued measuring after a supported decision became available: two and seven further readings in baseline, seven and nine with the verification prompt, and two and zero with the checker. This is an efficiency signal, not evidence that the model consciously recognized sufficiency and ignored it.

Token accounting matters here: Astra's reported output count already includes reasoning; Gemini's output and reasoning counts are separate and must be added for the comparable generated-token measure above. Input-token totals accumulate repeated conversation context and include cache reads; they are neither unique context length nor evidence of a particular search algorithm. Durations are the JSON-reported measure. Different provider rate limits and batched execution preclude interpreting cross-provider duration ratios as pure reasoning speed. No monetary cost estimate is asserted.

**The horizon contrasts did not establish an intrinsic difficulty gradient.** The C=4/L*=5 cases produced four correct first submissions, three supported, with a median 17 actions. The L*=6 rival-pair rows produced eight eventual wins, but only three supported first submissions and four supported final wins, with a median 20 actions. These distinctions are useful diagnostics; they do not isolate L* causally. The panel is not a crossed C-by-L* design, and its state sizes and other structure differ.

C is an optimistic minimum reading certificate for the actual behavior. L* is the smallest maximum query length whose complete query set identifies it. Neither is cognitive depth, a guaranteed adaptive measurement count, or operational workflow depth. Seed 6467 retains the corrected C=2; the balanced triple is not balanced on unrestricted C. Seeds 438/516 remain outside the original hard tier because their observable machines have fewer than six states. The controls behaved as intended: the shortcut used eight actions in both repeats; the known-construction task used four in both.

**Qualification failures remain design findings.** The earlier bounded W4 selective-revision/control prototype had allowed worlds with no common nontrivial reachable target, even with the law and state supplied. Its focused display-goal redesign also failed. The downstream-only two-module cascade had an all-history indistinguishability class with incompatible required repairs. These cannot become meaningful model challenges merely by increasing the run budget. They were not live-evaluated in this screen and must not be counted as model failures.

The cascade with explicit taps and clamps has a constructive winning policy and remains the most concrete next composition candidate. Its combined observation condition has a four-reading greedy worst-case bound; the isolated tap/clamp policy has six. These are bounds for the qualified specification, not optimality or cognitive-difficulty results. Local access may make the task separable. A playable implementation and matched controls must establish what the composition actually adds.

**Recommended next work, in order.**

1. **Close and retain this T/D cycle.** Preserve the 40-run cohort, historical failures, exact structural qualifications, and this assessment. Stop adding current-grammar variants merely to seek a terminal failure. Retain model revision as an investigative component, an evidence-to-action diagnostic, and an efficiency/reliability regression suite. Keep both operational success and supported commitment in the benchmark profile.
2. **Make one focused audit improvement.** Count rejected behavioral-class resubmissions separately from literal repeats. Automate the joins among execution ID, trace, episode, source identity, receipt, support witnesses and provider termination. The accompanying completed ledger and independent audit provide concrete examples. Preserve nulls for immutable model versions and hidden SDK retry counts that were not observed.
3. **Develop one two-module composition with generous resources.** Begin from the qualified assisted cascade and bounded one-fault repair vocabulary. Implement explicit interface/update/reset semantics, action costs, exact acceptance and replay. First compare the two components individually, an uncoupled combined mission, and the coupled mission with the same local observation access. Add a supplied-upstream-result control when the downstream task actually depends on upstream inference. Establish solvability and audit cost before any model pilot; do not promote the downstream-only obstruction into a challenge.
4. **Use component-level outcomes to interpret any difficulty.** Record local identification, evidence-supported repair choice, final component state, error propagation and joint mission success. A lower all-components pass rate may simply accumulate ordinary component errors. Compare against the independent-component prediction only as an explicitly tested model; do not assume independence. Add resource pressure and logistics after the generous-budget depth/breadth comparison is informative.
5. **Keep the remaining 20 executions conditional.** If commitment policy will be a published suite dimension, the best immediate confirmation would be five fresh structural groups × two finish policies × two repeats, with fixed model/effort, predetermined interleaving and first-submission support as the primary endpoint. Qualify and freeze those groups before evaluation; renamed wirings do not create holdouts. If that policy distinction is already sufficient for an engineering decision, retain the reserve and prioritize composition qualification. Any later use for a composition pilot needs a new explicit allocation; these are alternative uses of the same reserve.

A suggested practical gate for the optional policy confirmation is at least a 30-percentage-point supported-first-submission improvement, positive case-level direction in at least four of five fresh groups, and no new operational failures. This is a proposed engineering threshold, not a significance test, and should be fixed before the follow-up. If distinct qualified groups are unavailable, document the limitation rather than filling the panel with symmetry variants. The present matched comparison gives a 70-point descriptive increase, but is a screening result on the original selection.

I agree with making auditability, repeatability and customization central to NEXUS. This screen gives a concrete reason: an undifferentiated score says “40/40,” while the audit separates supported discovery, successful unresolved choices, useful finish feedback, and repeated rejected behaviors. The qualification process also prevents impossible designs from being misreported as reasoning failures. Those are useful framework capabilities even when a particular family reaches a terminal-success ceiling.

**What was independently verified.** Every planned execution ID occurs once, with 40 distinct traces and service episodes. All rows match the intended seed, axes, guidance/intervention options and recorded model/effort. The public evidence retrieved by each run hashes to its runtime binding; unmodified baseline/prompt bindings match the qualified baseline. The expected task prompt appears in every corresponding log section. All 40 models requested the manifest and all three evidence files.

The runtime source digest equals the qualified export digest in every run:
`a51c008b96a660f8b322f6e4a7528c9d726b7757084fab791773df5a47ec36ee`.

All use image ID `sha256:49e255626f3bbeb65693c797db5f2ecf2edceede5577f733b98daa3cb47ac378`, repository digest `localhost/nexus@sha256:5b544cbf7140c943859b8ecd6d7a98ab9085611022d323ae51bfebac211bd6ab`, and OCI revision `8f5fc0e77262d0772f5193d3f61995dc567885a3`. The local implementation's commit ID differs; applying patches can change commit identity. The observed source digest establishes agreement of the source content covered by that binding, not identity of the entire build environment. A separately archived image-preflight report and effective runtime config are not among these ten attachments.

MindTrial reports version `v0.25.3-0.20261017164258-00dada61a962`. Its final raw stop labels are `completed` for all 34 Astra runs and `STOP` for all six Gemini runs, explicitly marked terminal in the logs. All 1,178 recorded tool calls succeeded; there are no logged retries, warning/error entries, invalid world actions, duplicate requests or protocol conflicts. The largest observed tool-call and conversation-turn counts are 79. Every run has at least 13 world actions left. This is observed execution coverage, not a test that the configured external caps would be enforced at their boundaries.

An implementation independent of NEXUS recomputed primitive transitions for all 20,736 constructions, grouped the 748 behaviors using legal observations, and proved every grouping by full reachable-product equivalence. It then reconstructed the transcripts and checked all 367 reader measurements, all 49 checker responses, all 54 submission classifications and actual outcomes, and all 20 contradiction/alternative witnesses. It also checked action-turn/budget accounting for 929 actions and the support-set sizes before/after every reading. Each final JSON answer exactly matches the live victory code and the validator's accepted-receipt result. This is a semantic/transcript audit; it does not claim a rebuild of the operator's container or a reproduction of provider behavior.

The JSON `Stdout.Truncated` flags concern a size-limited diagnostic preview, not a truncated tool response delivered to the model. This was checked against the recorded MindTrial revision: its executor retains the full output for the returned tool result while limiting the summary preview. See [the pinned executor](https://github.com/petmal/MindTrial/blob/00dada61a962/providers/tools/docker_executor.go) and [result view](https://github.com/petmal/MindTrial/blob/00dada61a962/formatters/json_view.go).

**Source map.** Each stem names both the supplied `.json` and `.log`. Full input SHA-256 hashes and trace-level references are in the accompanying audit package.

| File stem | Condition | Executions |
|---|---|---:|
| `22-49-40` | Astra baseline | 24 |
| `10-44-05` | Astra single-shot | 10 |
| `11-51-35` | Gemini baseline | 2 |
| `12-24-44` | Gemini verification prompt | 2 |
| `12-54-08` | Gemini checker | 2 |

Concrete rejection examples occur in `22-49-40.log` at submission lines 1275/1332, 2090/2147, 5360/5417 and 12953/13010. The checker's compatible wrong submission and supported recovery appear in `12-54-08.log` at lines 1106 and 1524. The completed ledger records each run's binding, full report and receipt line. Earlier qualification findings come from the delivered T/D implementation's `docs/td-cycle-results.md` and exact preflight; the historical Gemini comparison comes from `NEXUS-rerun-analysis-2026-10-23.md`. Historical attempts and prototype proofs are not included in the 40-run denominator.

**Per-execution record.** S = supported/guaranteed; C = compatible; X = contradicted. The sequence records every eligible finish in order; the last finish always won and its receipt was accepted. A C earlier in the sequence was wrong; a final C was an actual success without full evidence support. Check calls are separate from reader measurements and consume no world action.

| Execution | Seed | Submission sequence | Actions | Readings | Tool calls | Checks |
|---|---:|---|---:|---:|---:|---:|
| `baseline-01-r1` | 5866 | S | 24 | 10 | 29 | 0 |
| `baseline-02-r1` | 6464 | C → X → S | 26 | 8 | 31 | 0 |
| `baseline-03-r1` | 6467 | C → X → S | 26 | 8 | 31 | 0 |
| `baseline-04-r1` | 438 | S | 16 | 6 | 21 | 0 |
| `baseline-05-r1` | 516 | S | 18 | 7 | 23 | 0 |
| `baseline-06-r1` | 3 | C | 16 | 6 | 21 | 0 |
| `baseline-07-r1` | 1185 | S | 22 | 9 | 27 | 0 |
| `baseline-08-r1` | 678 | C → X → C | 22 | 6 | 27 | 0 |
| `baseline-09-r1` | 1293 | C → S | 23 | 8 | 28 | 0 |
| `baseline-10-r1` | 1101 | C → S | 27 | 10 | 32 | 0 |
| `baseline-11-r1` | 468 | S | 8 | 2 | 13 | 0 |
| `baseline-12-r1` | 5866 | S | 4 | 0 | 9 | 0 |
| `baseline-01-r2` | 5866 | C | 18 | 7 | 23 | 0 |
| `baseline-02-r2` | 6464 | S | 24 | 10 | 29 | 0 |
| `baseline-03-r2` | 6467 | S | 22 | 9 | 27 | 0 |
| `baseline-04-r2` | 438 | S | 18 | 7 | 23 | 0 |
| `baseline-05-r2` | 516 | C | 14 | 5 | 19 | 0 |
| `baseline-06-r2` | 3 | S | 18 | 7 | 23 | 0 |
| `baseline-07-r2` | 1185 | S | 18 | 7 | 23 | 0 |
| `baseline-08-r2` | 678 | C → X → C | 22 | 6 | 27 | 0 |
| `baseline-09-r2` | 1293 | C → C | 17 | 5 | 22 | 0 |
| `baseline-10-r2` | 1101 | C → C → S | 29 | 10 | 34 | 0 |
| `baseline-11-r2` | 468 | S | 8 | 2 | 13 | 0 |
| `baseline-12-r2` | 5866 | S | 4 | 0 | 9 | 0 |
| `single-shot-01-r1` | 5866 | S | 26 | 11 | 31 | 0 |
| `single-shot-02-r1` | 6464 | S | 20 | 8 | 25 | 0 |
| `single-shot-03-r1` | 6467 | S | 24 | 10 | 29 | 0 |
| `single-shot-08-r1` | 678 | S | 20 | 8 | 25 | 0 |
| `single-shot-09-r1` | 1293 | S | 20 | 8 | 25 | 0 |
| `single-shot-01-r2` | 5866 | S | 30 | 13 | 35 | 0 |
| `single-shot-02-r2` | 6464 | S | 26 | 11 | 31 | 0 |
| `single-shot-03-r2` | 6467 | S | 22 | 9 | 27 | 0 |
| `single-shot-08-r2` | 678 | S | 18 | 7 | 23 | 0 |
| `single-shot-09-r2` | 1293 | S | 20 | 8 | 25 | 0 |
| `consistency-baseline-10-r1` | 1101 | S | 39 | 18 | 44 | 0 |
| `consistency-baseline-10-r2` | 1101 | S | 51 | 24 | 56 | 0 |
| `consistency-prompt-10-r1` | 1101 | S | 49 | 23 | 54 | 0 |
| `consistency-prompt-10-r2` | 1101 | S | 51 | 24 | 56 | 0 |
| `consistency-checker-10-r1` | 1101 | C → S | 36 | 15 | 79 | 38 |
| `consistency-checker-10-r2` | 1101 | S | 33 | 15 | 49 | 11 |
