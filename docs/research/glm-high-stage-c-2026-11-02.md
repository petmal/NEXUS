# GLM high: Stage C planning addition

2 November 2026, Toronto. This supplements the
[evening diagnostic report](inference-diagnostic-results-2026-11-02.md).

**GLM high can solve the short planning world optimally, but the relaxed attempt
fails after making a provably fatal planning detour.** Its eventual stop is a
response-length limit. This is additional evidence of a planning error; it is
not evidence that relaxed resources inherently make the world harder.

## Supplied results and verification

`glm-addition-v1.zip` contains one screen folder with **two attempts**, interference
09 and 25. The S05 and S21 high-setting controls are not included. The manifest
correctly reports complete coverage of its selected two-row screen; it does not
establish completion of the original four-row Stage C.

The archive SHA-256 is
`1cede979e8202de87eb02e9f7439249c0ecbe17567440041d27940b0b23928a7`.
Both attempts retain NEXUS source commit
`2b843649c6f61272edff05d437689ac9f619038d`, runtime digest
`ba22502788acf7ce1684e1e527e5aa332cd1746b37423fececabc90d71b8ee83`, and MindTrial
binary digest `95c57d56e3d8739c19c4be1d33ec8de876c6522a003704c4f2d277978baf8660`.
The input config is byte-identical to the earlier high-setting D run; the complete
recorded RunConfig also matches. Settings are GLM 5.2 high, text output, 10 RPM,
65,536 maximum completion tokens per response, and the existing retry/tool/turn
limits. World inputs match the earlier trials. Neither trace duplicates an earlier
attempt.

The audit checks the selected tasks against the full qualified parent matrix,
input/effective configuration hashes, preflight/source bindings and image identity.
Canonical replay reproduces all **34 public responses, 22 accepted actions and
five captured action-hash records**. Both trajectories also pass independent
scalar-transition and reverse-search checks. There are no malformed calls or
rejected actions. The winning receipt matches the submitted answer and recorded
validator acceptance. Replay uses a fresh secret, not the original HMAC secret.
No paid evaluation calls were made for this audit.

## Outcomes

Both rows disclose the same laws, initial state and target. Their exact minimum
is 17 actions: take, 15 operations and finish. Only the world action allowance
differs.

| Row | Budget | Result | Accepted actions | Actions available at stop | Minimum still needed |
|---|---:|---|---:|---:|---:|
| 09, tight | 17 | Supported world win; accepted receipt | 17 | 0 | 0 |
| 25, relaxed | 26 | `length`, no actionable content | 5 | 21 | 22 |

**Row 09 is an optimal execution.** It reaches the goal and submits successfully
using exactly the certified minimum, with no wasted actions. This demonstrates
working tool use, execution and receipt delivery at high effort on this world.

**Row 25 is already budget-infeasible before its response stops.** The exact
remaining cost exposes where it goes wrong:

| Turn | Action | Minimum remaining | Budget remaining | Interpretation |
|---|---|---:|---:|---|
| 1 | Take artifact | 16 | 25 | Nine spare actions |
| 2 | Operate bank0_r1 | 20 | 24 | First detour spends five actions of slack |
| 3 | Operate bank0_r1 | 19 | 23 | Still feasible |
| 4 | Operate bank0_r1 | 18 | 22 | Still feasible |
| 5 | Operate bank0_r2 | 22 | 21 | Second detour makes success impossible within budget |

All four operations change state; these are not rejected calls or no-ops. The
trajectory has introduced ten avoidable actions against a nine-action allowance.
The world is still marked active at turn 5 because its budget is not yet exhausted.
Nevertheless, every legal successful continuation requires more actions than
remain. The remaining-cost calculation includes the final finish action.

Keep the two findings separate: **the observed terminal cause is length**, while
**the earlier action sequence already prevents a win under R1**. More output
tokens after turn 5 cannot repair this trajectory within its unchanged action
budget. Starting a new run with a larger inference allowance could change earlier
choices; these data do not determine that counterfactual.

Row 09 reports 20,013 output tokens, including 19,601 reasoning tokens, over
186.4 seconds of recorded request time. Row 25 reports 81,405 output tokens,
including 81,249 reasoning tokens, over 485.0 seconds. These are whole-attempt
totals over multiple responses, so output above 65,536 is not itself a cap
violation. Usage reports do not establish the upstream route or effective
reasoning allocation.

## What this changes

Combined with D, high effort now has **one supported win and three length stops
across four planning rows**, one attempt per row. One of those length stops follows
the newly proved fatal detour. The earlier xhigh long row 11 had a similar
combination of an early fatal detour and a later length stop.

The high-setting failures are therefore **not confined to long, coupled worlds**.
Nor can the high setting be dismissed as unable to use the integration: the
optimal 09 win exercises the full execution and receipt path. Lowering effort
has not produced a dependable workaround for the response limits.

The earlier xhigh 25 attempts both won optimally, whereas this high attempt did
not. Conversely, high 09 wins and xhigh 09 previously produced one win and one
budget loss. These small, unbalanced samples do not establish which effort is
better. OpenRouter documents both settings as supported, with xhigh mapping to
max ([model documentation](https://openrouter.ai/z-ai/glm-5.2), checked 2 November
2026 Toronto); configuration support does not prove identical upstream handling
on every request.

The tight-pass/relaxed-loss pattern also does not prove that adding resources
harms reasoning. The allowed successful plans remain available with the larger
budget; separate model samples chose different trajectories. A budget-dependent
strategy change is a possible hypothesis, alongside ordinary run variability and
unobserved provider differences. More controlled evidence would be needed to
distinguish them.

**T/D conclusions do not change:** both new rows have fully disclosed laws.
**P/R interpretation improves:** the extra allowance was sufficient for one
detour, but not both. We can identify a concrete planning failure even though the
run ends before exhausting the physical budget. This is a useful capability of
the framework, not a new calibrated or isolated axis threshold.

## Next steps

1. **Do not rerun 09/25 to complete Stage C.** These two rows are supplied and
   audited. Only S05/S21 high controls remain absent. If completing the admission
   record is useful, recover them or run those two once; the optimal 09 already
   demonstrates that the basic planning tool/receipt path works. Do not block
   the wider research track on another round of GLM diagnostics.
2. **Keep further unchanged C/D challenge repetitions paused.** Retain GLM as a
   comparator under the stated inference budget, with stopping causes and
   pre-stop planning errors reported separately. Neither another broad screen
   nor a blanket completion-limit increase is justified as an automatic fix.
3. **Proceed with the established science sequence:** the contemporary Astra
   revision/repair anchor on S05/S08/S21/S22/S23/S24, then fresh matched worlds for
   the strongest Luna/Flash contrasts. Continue breadth/dependency preparation
   with disclosed controls and exact costs; isolate horizon, coupling, component
   count and resource pressure where possible.

Optional command for the two outstanding controls, using the existing package
with its GLM config still set to high and its verified image retained:

```bash
cd ~/Downloads/NEXUS-capability-diagnostics-2026-11-02
bash run.sh --model glm --suite controls --task-id S05 --task-id S21 \
  --non-interactive --skip-build
```

No world/runtime or validator defect was found. This update adds the
[attempt and cost ledger](glm-high-stage-c-2026-11-02.json) and revises the operator
plan; it does not change engine behavior, scoring or the historical results.
