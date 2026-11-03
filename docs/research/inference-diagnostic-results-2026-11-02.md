# MiniMax and GLM inference diagnostics: 2 November results

**Later addition:** [GLM high Stage C planning results](glm-high-stage-c-2026-11-02.md)
supply rows 09/25 after this ten-attempt archive. Only S05/S21 controls remain
unreported. The later report supersedes the missing-four-row recommendation
below; the original results and archive scope are retained.

The evening run removes the immediate HTTP 429 interruption, but it does not
establish a stable MiniMax evaluation path or rescue GLM's long-plan trials.
MiniMax solves all four disclosed controls in the world; one final answer fails
the exact receipt check. It then exhausts the world budget on both short planning
rows. GLM reaches a response-length limit on all four long-plan attempts, at both
`high` and `xhigh`. In one of those attempts, exact replay also proves that its
earlier actions had already made victory impossible within the remaining budget.

This is useful additional P/R evidence. It does not change the original T/D
conclusion, and it does not justify another unchanged broad screen.

## Scope and verification

The input is `results-v1(1).zip`, SHA-256
`bc95ec52c037e29bb1c213098db95112c8733ee9d31a0dd702da52fca14b2cdd`.
Its five folders contain **10 new, unique attempts**, recorded on 3 November UTC
(the evening of 2 November in Toronto). None duplicates a trace in the earlier
46-attempt compiled archive. The earlier four interrupted MiniMax controls remain
separate observations; these successful connections do not erase them.

All folders identify NEXUS commit
`2b843649c6f61272edff05d437689ac9f619038d`, runtime digest
`ba22502788acf7ce1684e1e527e5aa332cd1746b37423fececabc90d71b8ee83`, and MindTrial
binary digest `95c57d56e3d8739c19c4be1d33ec8de876c6522a003704c4f2d277978baf8660`.
The recorded evaluation seed is `nexus-cross-axis-pilot-v1`.

The audit verifies file hashes, selected task objects against the full qualified
parent matrix, source-bound preflight reports, image identity, effective
configuration, and task inputs. Full recorded RunConfig objects match the prior
cohort after accounting for the declared GLM effort change. Both models retain
text output (`disable-structured-output: true`), 10 RPM, a 65,536-token completion
ceiling, zero retries and the existing tool/turn limits. MiniMax did **not** use
the proposed 2-RPM probe in these folders. GLM high changes only the run label
and reasoning-effort field from its shipped preset.

Canonical offline replay matches **131 public responses, 73 accepted world
actions and all 28 captured action-hash records**, across 132 completed tool
calls. One malformed call has no public response. Independent scalar transitions
and reverse breadth-first search check all six planning trajectories, including
the three with no actions. Original emitted receipts are compared with submitted
answers and recorded validator decisions. Replay uses a fresh verifier secret;
it does not recompute the original HMACs. No paid calls or Docker runs were made
for this analysis.

## What ran

| Planned stage | Supplied execution | Status |
|---|---|---|
| A: MiniMax controls, two repetitions | S05 and S21, twice each | All four world wins; three accepted final answers |
| B: MiniMax short tight/slack pair | 09 and 25, once each | Both world-action-budget losses |
| C: GLM high controls and short pair | S05, S21, 09, 25 | **Not present in this archive** |
| D: GLM long tight/slack pair | 11 and 27, once at high and once at xhigh | Four length stops; one of two planned repetition blocks supplied |

Stage A's receipt-delivery gate was therefore not completely clean. The B traces
are still valid and informative; they should not be discarded. Likewise, the
absence of C does not invalidate D's recorded stops, but leaves the simpler
admission check for the high setting unreported. Missing here does not mean the
user never ran those rows elsewhere.

## MiniMax: working controls, a receipt failure, and real planning losses

| Row | Attempt | Raw result | Audited result | Actions / initial budget |
|---|---|---|---|---:|
| S05 | 1 | Passed | Evidence-supported world win; accepted receipt | 4 / 64 |
| S21 | 1 | Passed | Evidence-supported world win; accepted receipt | 6 / 8 |
| S05 | 2 | Passed | Evidence-supported world win; accepted receipt | 4 / 64 |
| S21 | 2 | Failed | Evidence-supported world win; extra prose around correct receipt | 5 / 8 |
| interference 09 | 1 | Failed | World action budget exhausted | 17 / 17 |
| interference 25 | 1 | Failed | World action budget exhausted | 26 / 26 |

For the failed S21 submission, the final text begins “Mission complete. Victory
code received.” and then includes the exact emitted code. The validator correctly
reports a won session with a nonmatching submitted string. This is an output
contract failure, not a failed repair. Preserve both scores: **4/4 supported
world wins and 3/4 accepted answers**. Do not silently turn the raw Failed record
into a pass or relax the historical validator. The second S05 also recovers from
one call missing `operation`; the second S21 recovers from a configuration action
issued in the wrong room. Neither prevents the later world win.

Rows 09 and 25 have the same fully disclosed short, independent-bank world and
the same exact minimum: **17 actions**, including take and finish. Row 09 allows
17 actions; row 25 allows 26. They differ in resource pressure, not in the laws.

* **09 becomes impossible at turn 7.** A wrong operation increases the shortest
  remaining route by enough to require 22 total actions, exceeding its budget of
  17. Later detours and two unsuccessful finish actions exhaust the budget. This
  is a mechanically demonstrated planning loss, not a response-length stop.
* **25 becomes impossible at turn 14.** Six probes consume actions without
  changing the physical state, despite the laws already being disclosed. Seven
  later operations leave the registers unchanged. The trace spends more than
  its nine-action allowance on probes, ineffective operations and a detour. At
  the final state, reaching and submitting the goal still requires 10 actions.
  The final `VICTORY_CODE_PLACEHOLDER` is not hiding a world win: no victory was
  reached or receipt emitted.

The histories matter. In the earlier text-output panel, MiniMax won 09 optimally;
its next 09 attempt ended with no response candidates. Its earlier 25 attempts
ended at length and with no response candidates. Including the current run,
09 is **one world win in three attempts** and 25 is **zero in three**, with
different stopping causes. This does not establish that relaxation hurts the
model, or that a reproducible R threshold has been located. The current pair
shows planning failure in both budgets, not a tight-loss/slack-rescue contrast.

No new 429 or empty-content errors occur in these six MiniMax attempts. Recovery
at the unchanged 10 RPM means the results cannot demonstrate that lowering RPM
fixed the previous outage. Nor do they establish permanent provider stability.

Usage reporting remains variable. For example, 09 reports 74,074 output tokens,
including 71,909 reasoning tokens; 25 reports 2,099 output tokens and 26 reasoning
tokens. These are whole-attempt totals, not per-response limits. This variability
alone does not prove a routing change or disabled reasoning. It also does not
explain away the observable wrong actions. Upstream identity and per-response
metadata are still needed to resolve the earlier accounting anomaly.

## GLM: lowering effort did not rescue the supplied long cases

Rows 11 and 27 share a fully disclosed long, coupled world with an exact minimum
of **35 actions**. The budgets are 35 and 53. Successful plans require interaction
between the banks; no plan that completes one bank and then the other is possible.

| Effort | Row | Accepted actions | Actions still available at stop | Exact minimum still needed | Terminal response |
|---|---|---:|---:|---:|---|
| high | 11 | 0 | 35 | 35 | `length`, no actionable content |
| high | 27 | 0 | 53 | 35 | `length`, no actionable content |
| xhigh | 11 | 11 | 24 | 39 | `length`, no actionable content |
| xhigh | 27 | 0 | 53 | 35 | `length`, no actionable content |

The high attempts read the public materials but make no world actions before
stopping. Thus **high did not rescue either tested case**. One attempt per cell,
without the missing simple high controls, cannot establish equivalent performance
or prove that effort has no effect. Across the previous and current archives,
all six xhigh 11/27 attempts stop at length; both new high attempts do too.

The xhigh 11 attempt has two distinct findings. Its observed terminal cause is
a response-length limit. But its first operation, at turn 2 after taking the
artifact, already leaves 38 actions of work with only 33 available. At turn 11,
the gap is 39 needed versus 24 available. Extending the response ceiling at that
point would not rescue that trajectory under its existing world budget. A new
run with more inference allowance could choose a different plan; this audit
does not predict that counterfactual.

The other three attempts remain physically feasible when they stop. Therefore,
it would be misleading either to label all four as ordinary world-budget losses
or to treat all four as uninformative infrastructure errors. Length termination
is part of practical model performance under the chosen inference budget; it
does not reveal how the model would behave without that limit.

OpenRouter's [GLM model page](https://openrouter.ai/z-ai/glm-5.2) documents high
and xhigh support. Its [reasoning documentation](https://github.com/OpenRouterTeam/docs/blob/main/guides/best-practices/reasoning-tokens.mdx)
explains that reasoning can consume the completion allowance and leave an empty
content response at `length`. That supports the classification, but does not
prove how a particular upstream honored effort or accounted for every token.
Aggregate output above 65,536 is not itself evidence of a ceiling violation,
because an attempt includes multiple responses. Sources checked 2 November 2026 (Toronto).

## Effect on the scientific conclusions

**T/D:** unchanged. These new worlds disclose their relevant laws; there is no
new hidden-law challenge result here. The broader smaller-model evidence still
supports useful practical discrimination, but not a reliable strongest-model
failure boundary caused solely by T/D. Keep model revision and compositional
repair as foundations for further evidence-use and multi-subgoal work.

**P/R:** the evidence becomes more specific. We now have two clean MiniMax world
budget losses and an early, provably fatal GLM planning detour. This strengthens
the case that the planning worlds can expose observable errors. It does not
establish a new isolated axis effect: the new MiniMax pair has no slack rescue;
the long GLM cases are mostly limited before execution; and comparing short
independent worlds with long coupled worlds changes horizon and coupling
together. Luna's earlier 1/16 tight versus 13/16 relaxed result remains the
stronger matched evidence for resource pressure.

**Framework value:** reinforced. The same raw Failed label covers an actual
budget loss and a supported world win with bad receipt formatting. Exact replay
and shortest-path analysis distinguish them, and can identify a doomed plan even
when the eventual stop is a response limit. Preserve these separate measures
as NEXUS grows.

## Recommended next sequence

1. **Recover or run the missing GLM high Stage C:** S05, S21, 09 and 25, once
   each, with the same 65,536 ceiling and all other settings fixed. If those
   artifacts already exist, analyze them rather than spending on duplicates.
   This is the most useful remaining piece of the original matrix.
2. **Do not automatically finish the second unchanged D block.** Four earlier
   xhigh stops plus the four new high/xhigh stops are enough to pause this route
   as a smoke discriminator. The present evidence supplies no successful setting
   worth expanding. A larger, verified completion ceiling would be a separately
   labelled inference-budget experiment, conditional on C and better response
   metadata; it is not the next default rerun.
3. **Limit MiniMax follow-up to the unresolved integration question.** If exact
   receipt delivery must be admitted before further use, run S21 once at the
   unchanged preset and retain the outcome. Otherwise proceed with the existing
   dual world/receipt scores. Do not run another broad MiniMax challenge panel
   before obtaining better upstream/per-response provenance. Do not run the
   2-RPM probe merely because it was the earlier recommendation: the supplied
   batch has already demonstrated renewed connectivity at 10 RPM.
4. **Move the main science track forward independently of these diagnostics.**
   Use the previously proposed contemporary Astra revision/repair anchor on
   S05, S08, S21, S22, S23 and S24 at its established preset. Then qualify fresh
   matched worlds for the strongest existing Luna/Flash contrasts. Repeats of
   one seed measure run variability, not generalization across generated worlds.
5. **Continue preparation for breadth and dependency experiments.** Use revision,
   compositional repair and stateful interference for complementary questions.
   Vary component count, dependency depth, horizon and coupling separately where
   possible. Keep disclosed controls, evidence-support checks and exact physical
   costs. This batch supplies no reason to make the current long worlds still
   harder before resolving what their present stops measure.

For Stage C, use the existing 2 November package; no image/runtime update is
needed for this report. Set only the GLM run name and
`model-parameters.reasoning-effort` to `high`, preserving the shipped xhigh file
for restoration as described in the [operator matrix](../inference-diagnostic-matrix.md).

```bash
cd ~/Downloads/NEXUS-capability-diagnostics-2026-11-02
bash run.sh --model glm --suite all --task-id S05 --task-id S21 \
  --task-id 09 --task-id 25 --non-interactive --skip-build
```

Use `--skip-build` only while retaining that package's verified image. The
optional single MiniMax receipt check is:

```bash
bash run.sh --model minimax --suite controls --task-id S21 \
  --non-interactive --skip-build
```

The [compact audit ledger](inference-diagnostic-results-2026-11-02.json) retains
attempt identities, raw and audited outcomes, provenance and exact-cost results.
The prior [46-attempt synthesis](smaller-model-synthesis-2026-11-01.md) and
[four interrupted controls](minimax-control-interruption-2026-11-02.md) remain
historical records. No engine, task, scoring or validator change is warranted by
an identified defect in this batch; this update records findings and revises the
immediate operator plan.
