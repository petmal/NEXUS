# Fresh-world results and project assessment — 4 November 2026

## Assessment

NEXUS now demonstrates useful differences between model configurations on fresh,
mechanically qualified worlds. Astra medium has the strongest overall evidence
in this panel; Luna medium is substantially less reliable; Grok medium is strong
at disclosed planning but has a specific repair weakness; Flash high wins all
six completed T/D challenges, but three wins do not establish that its evidence
justified the solution. Flash's incomplete planning panel prevents a full ordering.

The most important new result is a **real Astra planning failure**. It changes
the previous observation that Astra solved every tested interference condition.
It does not establish a repeatable failure threshold, a pure T/D failure, or a
limitation of Astra at its highest inference setting.

My recommendation is to prepare an **experimental public research release**, with
a short reliability and reporting pass before publication. Do not wait until one
axis consistently defeats the strongest model. Do not present the current panel
as a calibrated general leaderboard. NEXUS's demonstrated value is the ability
to generate controlled challenges, verify their solvability, and explain exactly
where an attempt went wrong.

## 1. What was evaluated and verified

The supplied `results-fresh-complete.zip` contains 110 records in 17 folders:
six historical Astra anchors and 26 fresh conditions for each of four models.
The ten initial Astra records are byte-identical to those already reviewed in
the [initial report](fresh-world-initial-results-2026-11-03.md); they are included
once here, not counted as ten additional repetitions. There are 100 new records.

| Configuration | Reasoning setting | Requests/minute |
|---|---|---:|
| OpenAI gpt-6-astra | medium | 20 |
| OpenAI gpt-6-luna | medium | 20 |
| Google gemini-3.8-flash | high thinking | 3 |
| xAI grok-4.7 | medium; 65,536 completion-token cap | 20 |

The presets retain their structured-output defaults, 600 tool calls, 650 turns,
and zero configured provider retries. Astra/Luna/Flash have no explicit completion
cap in these configs. These settings do not allocate equal compute across models.
Model names identify configured endpoints, not independently verified immutable
weight versions.

T/D means constructing or inferring a causal model from evidence and experiments.
P/R means planning and managing limited world actions. The
[frozen guide](../fresh-world-guide.md) defines the exact interventions:

- Revision: two seeds, each with a supplied-law control and a hidden-law challenge.
- Repair: two seeds, each with a supplied-solution control and hidden challenges
  at 30 and 36 actions.
- Interference planning: two seeds, each crossing short/long goals,
  independent/coupled laws, and tight/relaxed budgets. Laws, state and map are
  disclosed. Tight budgets equal the exact minimum, including take and finish.

These are purpose-selected fixtures, one attempt per cell. Several cells share
one mechanism. They are not 26 independent random samples from a population of
worlds, and their percentages are not precise estimates of general ability.

The offline audit checked task/configuration hashes, source/image bindings,
recorded settings, control-admission references, evidence and investigation hashes,
and the committed mechanical preflight. It regenerated every world, replayed
**2,342 accepted actions and all 2,920 public responses**, and matched all **200
captured action-hash records**. The 2,935 tool calls include 15 malformed calls,
all from Luna; they were not treated as successful world actions.

An independent scalar transition implementation and reverse breadth-first search
checked all 64 P/R trajectories, including nine empty trajectories, and their
1,321 accepted actions. This establishes the minimum remaining physical cost
after each accepted action. It does not measure internal reasoning complexity.

Replay used a fresh verifier secret. Original receipt strings were matched from
the emitted response through the submitted answer and recorded validator result;
the original HMACs could not be recomputed without the original secrets. No paid
model calls or new container tests were performed for this analysis.

## 2. Results and relative performance

The raw harness totals are **84 Passed, 15 Failed and 11 Error**. Six of the passes
are historical anchors. For the 104 fresh records, there are **78 wins, 17 known
losses and nine unassessed outcomes** when already irreversible planning failures
are recognized separately from their later provider errors.

| Configuration | Supplied controls | T/D world wins | T/D supported wins | P/R verified outcomes |
|---|---:|---:|---:|---|
| Astra medium | 4/4 | 6/6 | 6/6 | 15 wins, 1 loss |
| Luna medium | 4/4 | 2/6 | 2/6 | 8 wins, 8 losses |
| Flash high | 4/4 | 6/6 | 3/6 | 6 wins, 1 proven loss before error, 9 unassessed |
| Grok medium | 4/4 | 4/6 | 4/6 | 15 wins, 1 proven loss before error |

A **supported win** is a valid victory whose chosen solution works in every world
still consistent with the available evidence. A **compatible win** succeeds in
the actual world, but an evidence-consistent alternative would reject it. It is
still a legitimate victory under the current rules. Compatibility alone does not
prove random guessing, and support does not require identifying a unique world
when several remaining worlds admit the same solution.

On the common 16 conditions F01–F16, all four models completed normally:

| Configuration | World wins | Supported wins |
|---|---:|---:|
| Astra | 16/16 | 16/16 |
| Luna | 9/16 | 9/16 |
| Flash | 16/16 | 13/16 |
| Grok | 14/16 | 14/16 |

This is the cleanest common comparison, although it omits the long coupled
planning pair and the entire second planning seed. It supports a broad separation
between Luna and the other configurations, and a more consistent evidence-use
record for Astra. It does not establish a stable total ordering among Astra,
Flash and Grok. Flash's missing rows are concentrated in challenging planning
conditions, so its completed-only success percentage is especially misleading.

Across those common 16 conditions, recorded output plus reasoning tokens total
40,859 for Astra, 183,521 for Luna, 473,979 for Flash and 351,654 for Grok.
Reasoning is already included in OpenAI's output count and was added only where
the provider records it separately. This is useful operational context, not an
equal-compute or monetary comparison: tokenizers, inference settings, cache
accounting and provider behavior differ. More reported reasoning tokens did not
ensure stronger performance in this panel.

### The errors conceal two already decisive planning mistakes

All manifests say completed and all expected result records exist. That means
the batch produced records, not that every scientific condition was evaluated.

| Attempt | Recorded stop | What the trace establishes before that stop |
|---|---|---|
| Flash F17, budget 36 | HTTP 402, depleted credits | Action 2 is a probe. After two actions, 35 more are required: minimum total 37. At interruption, 24 actions are spent and 38 more are needed. |
| Flash F18–F26 | HTTP 402, depleted credits | No model tool calls. These nine conditions remain unassessed. Service setup alone is not model interaction. |
| Grok F26, budget 37 | HTTP 503 | Action 2 is a probe. After two actions, 36 more are required: minimum total 38. Three probes leave the state unchanged and the world irrecoverable under its budget. |

Keep both facts in the ledger: provider error **and** a proven earlier budget
failure. Do not turn every error into a loss, and do not discard an already
conclusive failure because a later request failed. Repeating F17/F26 is valuable
for stability and clean completion, but cannot retroactively erase these attempts.

## 3. What the traces say about T/D

| Fresh challenge | Astra | Luna | Flash | Grok |
|---|---|---|---|---|
| F02 revision 2073 | supported, 22 actions | loss, 63 | compatible, 42 | supported, 51 |
| F04 revision 2178 | supported, 14 | supported, 59 | compatible, 43 | supported, 30 |
| F06 repair 541, 30 actions | supported, 30 | supported, 30 | supported, 29 | loss, 30 |
| F07 same repair, 36 actions | supported, 24 | loss, 36 | supported, 33 | loss, 36 |
| F09 repair 586, 30 actions | supported, 27 | loss, 30 | compatible, 27 | supported, 28 |
| F10 same repair, 36 actions | supported, 27 | loss, 36 | supported, 33 | supported, 36 |

Several distinctions materially change interpretation:

1. **Astra clears the fresh hidden-law panel with supported solutions.** Its six
   first submissions are all guaranteed by the evidence. The historical S08
   anchor is different: its victory leaves three competing mechanisms with no
   shared solution. The anchor is a physical win, not proof of full identification.
2. **Flash's apparent T/D ceiling hides evidence gaps.** Both revision wins leave
   two incompatible possibilities. Repair F09 leaves four worlds and no common
   repair; F10 reaches a supported win. Thus all six victories do not establish
   six successful evidence-based identifications. Earlier compatible Flash wins
   make this a recurring concern, rather than an isolated scoring curiosity.
3. **Luna has both investigation and execution failures.** F07 and F10 reach a
   uniquely identified mechanism, then submit contradicted repairs. F02 also
   repeats contradicted constructions. Adding more ambiguity alone would not
   address all observed failure mechanisms. F04 eventually recovers after a
   contradicted first submission.
4. **Grok has a seed-specific repair weakness.** Both F06/F07 fail despite the
   supplied control passing, while F09/F10 succeed. Its measurements in F06/F07
   cover only context 0; a guaranteed repair is never established. F06 has no
   intervention measurement. In revision F02, Grok uses rejection feedback to
   recover from an unsupported first choice to a supported final solution.

The original strongest-model T/D conclusion remains: **the tested families have
not established a reliable pure T/D failure boundary for Astra.** The fresh data
strengthen that statement for the tested medium configuration, while reinforcing
that these families discriminate among other configurations and expose different
evidence-use strategies.

The experiment does not isolate T from D: revision changes both. The repair
execution control changes disclosure and budget together. Its hidden 30/36 pair
isolates budget, but Luna reverses from pass to fail on seed 541; Astra and Grok
do not change outcome; Flash's seed 586 change is from compatible to supported
success. There is no universal repair-budget rescue in this fresh panel.

## 4. What changes for P/R

**Astra F22 is a substantive counterexample to saturation.** Its first operation,
`bank1_r0`, occurs at action 2 and raises the minimum total completion cost from
22 to 27. Its later failed finish and final answer happen while the engine still
says active, but recovery within the allowance is already impossible. This is
not merely forgetting to return a receipt or encountering a provider limit.
On matched relaxed F21 it wins in 27 actions with a budget of 33.

Across the fresh panel, Astra wins 15/16 P/R conditions, with 13 optimal wins.
The earlier 32/32 optimal record remains true of that earlier panel, but is no
longer a description of all evaluated interference worlds. F22 is the short
coupled case, while Astra solves longer coupled cases. Therefore these results
argue against using plan length alone as a reliable difficulty scale.

| Configuration | Tight-budget outcomes | Relaxed-budget outcomes | Matched pairs |
|---|---|---|---|
| Astra | 7/8 wins | 8/8 wins | 1 loss-to-win, 7 both win |
| Luna | 2/8 wins | 6/8 wins | 5 loss-to-win, 1 reverse, 1 both win, 1 both lose |
| Grok | 7/8 wins, including proven F26 loss | 8/8 wins | 1 loss-to-win, 7 both win |
| Flash | 3 wins, 1 proven loss, 4 unassessed | 3 wins, 5 unassessed | 3 completed pairs both win; others incomplete |

Luna's earlier 1/16 tight versus 13/16 relaxed result, with 12 rescues and no
reverse pairs, now has a qualitative replication on fresh seeds. The new reverse
pair, F20/F19, means extra actions are an opportunity rather than a guarantee of
better behavior. Resource pressure remains the best demonstrated adjustment.
Do not pool the two panels into an independent-trials significance calculation.

All eight fresh Luna P/R losses become physically infeasible before the attempt
ends. In F11/F13/F15/F21 the final physical target is reached with no action left
for finish. The wasted allowance comes from a no-op, an unnecessary probe, or
longer detours; the task explicitly charges for finish. Keep these as losses,
but separately report physical-goal attainment. Other losses stop at a wrong
state after an already fatal decision. None of the 15 normal Failed records in
the archive ends with a recorded response-length stop.

Grok wins its 15 normally completed planning attempts, ten optimally. F26 shows
that it is not immune to tight-budget failure: probing known laws can be a poor
allocation of world actions. Flash makes the same kind of mistake in F17. This
supports studying redundant experimentation and commitment discipline alongside
search complexity.

There is still no isolated general effect estimate for horizon or coupling.
Longer goals change the target; coupling changes the laws; budget amounts follow
the resulting optimal costs. The factorial panel is informative, but two seeds
and single attempts cannot establish a monotone difficulty law. Only the same
world's tight/relaxed pair changes budget alone.

## 5. Highest-value work before public release

These are recommendations, not runtime changes made by this report.

| Priority | Improvement | Reason and completion criterion |
|---|---|---|
| 1 | Make outcome reporting multi-dimensional | Preserve raw harness result, world victory, evidence support, physical-goal attainment, response stop and provider error. Add first proven budget-infeasible action where exact continuation costs exist. The current 110 records should reproduce the distinctions above automatically. |
| 1 | Stop unusable provider batches | The runner currently stops later groups on HTTP 429, but continued after depleted-credit HTTP 402. Add typed billing/quota failures and explicit partial status. Stop later groups; stopping remaining tasks inside a running group requires harness support or smaller groups. Preserve zero-retry scientific configs and append-only attempt history. |
| 1 | Cover the fresh release in CI | `ci.yml` excludes `docs/**` then lists selected matrices, but omits `fresh-world-matrix.json`. The dedicated container workflow also lacks the fresh-world export/package paths and integration stage. Add those triggers and exercise the exact packaged fresh launcher plus control admission. A docs-only matrix change must not bypass validation. |
| 1 | Produce a small stable public release | Tag source, build an identifiable image, document one neutral CLI/HTTP example and one adapter path, and provide a no-provider reference replay. Test install, package, reset, malformed action and receipt handling in a clean environment. Clearly label experimental families and historical matrices. |
| 2 | Export structured audit events | Much of this audit still joins debug logs and parses Go map text. Provide versioned JSONL for requests, responses, episode binding, accepted actions, terminal state and provider stop. Keep private solver diagnostics on the operator side. Require explicit missing-data states. |
| 2 | Declare the evaluation protocol | Freeze presets, repetition rules, budget accounting, primary metrics and seed selection before runs. Separate public development seeds from held-out evaluation seeds. Record structural novelty rather than assuming a new seed is a new challenge. Keep model-size and general-intelligence claims out of the initial release. |

The current core already has deterministic execution, exact goals and receipts,
replay, source-bound qualification, known-law controls and an ontology extension
boundary. Preserve those assets. This audit found no public-response divergence
from the pinned engine, and does not justify rewriting the architecture.

Do not silently make finish free or ban redundant probes to improve scores.
Either would change the measurement. A separate, labeled budget reminder or
assisted-execution control could reveal how much loss comes from bookkeeping;
the original condition must remain available for comparison.

## 6. Next evaluation and difficulty research

First close the current evidence gaps, then expand one structural knob at a time.

| Stage | Models and rows | Purpose |
|---|---|---|
| A: completion | Flash: pr-a F17/F18 and pr-b F19–F26; Grok: pr-b F25/F26 | Ten Flash attempts plus one Grok pair. Fill nine unassessed conditions and obtain completed paired observations for interrupted losses. Keep the original F17/F26 records. Existing matching controls remain valid if release, binary and settings are unchanged. |
| B: strongest-model confirmation | Astra F21/F22, two additional attempts per row | Test whether the fresh tight-budget failure repeats, interleaving the pair. If it repeats, compare a higher effort preset with its own admission controls; report it as a separate configuration. |
| B: selected diagnostics, after budget review | Luna F19/F20 and F06/F07; Grok F06/F07; two additional attempts per selected row | Test the reverse budget effects and Grok's repair weakness without rerunning the entire panel. These repetitions are exploratory, not a definitive failure-rate estimate. |
| C: evidence support | Flash F02/F04 and F09/F10, with qualified alternative truths | Test whether compatible victories survive worlds that distinguish the remaining hypotheses. Predeclare and qualify alternative truths; do not choose only adversarial outcomes after seeing guesses. Preserve supplied-law controls and compute-aware stopping rules. |

Stage A plus the Astra confirmation is a bounded **16-attempt** first follow-up.
The optional diagnostics need not run in the same batch. Flash F17 alone consumed
209,093 recorded reasoning tokens before the billing stop, so broader sweeps
should have explicit operational budgets and a stop-on-error policy. No current
model-price assumptions are needed to see that this was an expensive attempt.

For the next architecture increment, prioritize these adjustments:

1. **Breadth and dependency structure.** Vary the number of subgoals, prerequisite
   chain depth, fan-in and shared state separately. Compare equal-size independent
   and interacting tasks. Require plans that revisit or temporarily undo earlier
   goals. Match plan lengths where possible; otherwise publish their differences.
2. **A resource curve rather than only two endpoints.** For the same compiled
   world, compare exact minimum, small absolute slack such as +1/+2, and moderate
   relative slack. Include a generous baseline. This distinguishes one redundant
   probe or missing finish allowance from a substantial planning failure.
3. **Information use with consequences.** On revision/repair, control experiment
   cost, the availability of informative contexts, and the need to choose a
   solution valid across remaining hypotheses. Measure support at first commitment
   and final victory. Avoid making unique identification mandatory when a shared
   valid repair is enough.
4. **Observation and memory burden, later.** Compare explicit public state/history
   with partial observation or a permitted notebook while holding laws and goals
   fixed. Make observability changes explicit; hidden interfaces and undocumented
   controls should never become accidental difficulty knobs.

The best immediate P/R base is **stateful interference**, because exact physical
costs and dependency diagnostics make failures explainable. Keep **model revision**
for evidence accumulation and commitment, and **compositional repair** for joint
constraints and experiment selection. **Stateful discovery** is the bridge for
combining investigation with state-changing execution after the separate effects
are understood. Keep spatial planning and older families as controls and regression
fixtures; do not launch another broad sweep of every architecture.

Start new composition with disclosed laws and generous resources, then qualify
each added dependency independently. Only after that baseline works should hidden
laws and tight resources be combined. Increase breadth and depth separately,
publish solver limits, and retain independent small-world checks. Simply adding
more steps risks measuring accumulated execution errors without learning which
structural feature matters.

## 7. Overall state

| Area | Assessment |
|---|---|
| Deterministic environment and auditability | Demonstrated in the evaluated configurations; the complete response replay passed. |
| Useful model discrimination | Demonstrated on selected fresh fixtures, especially Luna's resource sensitivity and differing evidence-use strategies. |
| Strongest-model saturation | Broken for Astra medium on one fresh P/R condition; repeatability and higher-effort behavior remain open. |
| Pure strongest-model T/D boundary | Not established. Fresh Astra T/D performance is fully supported. |
| Difficulty calibration | Incomplete. Two seeds per family and one attempt per condition cannot define general difficulty levels. |
| Operational reliability | Improved by the control-admission fix, but billing interruption handling and structured result export need work. |
| Public release | Suitable direction: an experimental research framework after a bounded hardening pass. A broad model leaderboard needs more coverage and replication. |

I agree with the goal of meaningful challenges across several axes. I would change
the immediate emphasis from “keep increasing difficulty until Astra fails” to
“make the observed differences reproducible and interpretable, then broaden the
challenge.” The first fresh Astra failure is useful precisely because NEXUS can
identify its cause. That explanatory capability should remain a release criterion.

## Reproducibility and evidence

- Input ZIP SHA-256: `aec4cdaff3352118be04ec1e59c489130709ea854304ce193949a776d303f757`.
- World/image source: `3ded3ba1a83815ed12950529619b344b23186e68`.
- Runtime source SHA-256: `ba22502788acf7ce1684e1e527e5aa332cd1746b37423fececabc90d71b8ee83`.
- Host readout fix: `7e2b74e5c16a8afd4687bfaf4538bbba72592ed6`.
- MindTrial binary SHA-256: `95c57d56e3d8739c19c4be1d33ec8de876c6522a003704c4f2d277978baf8660`.
- Evaluation seed: `nexus-cross-axis-pilot-v1`; offline Python: 3.14.7.
- [Compact per-attempt ledger](fresh-world-results-2026-11-04.json): all 110 records,
  raw outcomes, support, provider status and independent continuation results.
- Mechanical evidence: [fresh preflight](fresh-world-preflight-2026-11-03.json),
  [matrix](../fresh-world-matrix.json), and [pilot guide](../fresh-world-guide.md).
- Historical comparisons: [smaller-model synthesis](smaller-model-synthesis-2026-11-01.md),
  [consolidated smoke findings](smoke-findings-2026-10-31.md),
  [GLM Stage C](glm-high-stage-c-2026-11-02.md), and
  [original T/D synthesis](../td-experiments-and-next-directions.md).

The companion audit package contains the input archive, safe extraction script,
parser, replay checks, independent cost audit and generated audit files. It needs
a NEXUS checkout with the recorded runtime and host readout fix. Historical
comparisons above retain their original cohorts; no GLM/MiniMax/Muse/Mistral
scores are merged into this four-model fresh panel.
