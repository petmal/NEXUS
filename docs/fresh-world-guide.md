# Fresh-world pilot — 3 November 2026

Current-source packages use `fresh-world-preflight-current.json`. The dated
3 November report and original results remain historical evidence. New runtime
source requires newly matched control admission; do not reuse the old package's
control results. Run `make qualify-release` and `make preflight` after source
changes, then package from a clean committed checkout. See
[the evaluation guide](evaluation-guide.md) for the current operator workflow.
The design below records the original 110-attempt screen. For release checking,
start with the six-attempt canary in the
[run guide](../examples/mindtrial/fresh-world-run.md#small-release-canary);
that guide also gives the bounded completion/confirmation panel.

This pilot checks whether the most useful earlier distinctions survive a change
of world. It adds **two fresh fixtures in each of three established families**,
26 conditions per model, and a contemporary six-task Astra anchor against the
historical worlds. It does not introduce a fourth architecture or new axis levels.
Mechanical qualification has passed. The [complete result analysis](https://github.com/petmal/NEXUS/blob/8b0a8b80425221ec4f71cc96a8ac152d5082841c/docs/research/fresh-world-results-2026-11-04.md)
now covers all 110 records, including the initial Astra runs counted once. It
separates provider interruptions, physical success and evidence-supported success.
The [initial Astra report](research/fresh-world-initial-results-2026-11-03.md) and
[host-only recovery](fresh-world-readout-fix.md) remain historical records.

The original evaluation used Astra medium, Luna medium, Flash high and Grok medium.
Each model was assigned the same 26 fresh conditions, subject to an integration-control
gate. One unchanged Astra anchor adds six attempts: **110 attempts maximum before
optional reruns**. There is one attempt per condition, no automatic retry and no
default repetition. These are a screening matrix, not stable failure-rate estimates.

## Why these fixtures were selected

The latest GLM/MiniMax diagnostics showed mixed response-limit, planning and
receipt-submission behavior. GLM high solved short row 09 optimally, while row 25
reached a length stop after an already fatal detour. Repeating unchanged challenges
would not isolate resource sensitivity. GLM and MiniMax are therefore absent from
the default panel; their historical records remain intact.

Luna has the clearest earlier planning-budget signal: 1/16 wins at the exact
minimum versus 13/16 with slack, with 12 rescues and no reverse pair. Flash is a
strong comparison model, not evidence about a uniformly weak-model tier. Grok
medium passed the earlier S05/S21 integration controls optimally and supplies a
fourth tested interface. Astra provides a contemporary strong-model reference:
the earlier interference results were 32/32 optimal, but its selected revision
and repair anchor had not yet been collected.

These observations motivate fresh fixtures before broader composition. They do
not establish a pure strongest-model T/D boundary, a model-size ordering, or
equivalent inference effort across vendors. The prior result reports remain the
source for those earlier outcomes, including
[GLM Stage C](https://github.com/petmal/NEXUS/blob/02fd61d257a4f88c2d238c0dcc2a46df93acea26/docs/research/glm-high-stage-c-2026-11-02.md)
and the
[smaller-model synthesis](https://github.com/petmal/NEXUS/blob/02fd61d257a4f88c2d238c0dcc2a46df93acea26/docs/research/smaller-model-synthesis-2026-11-01.md).

## Models and execution settings

| Selector | Provider/model | Inference setting | Requests/minute |
|---|---|---|---:|
| astra | OpenAI / gpt-6-astra | medium | 20 |
| luna | OpenAI / gpt-6-luna | medium | 20 |
| flash | Google / gemini-3.8-flash | high thinking | 3 |
| grok | xAI / grok-4.7 | medium; 65,536 completion-token cap | 20 |

The configs copy the already evaluated per-model presets. Astra/Luna/Flash retain
their prior implicit response caps. Structured-output settings, provider retry
policies and tool contracts are unchanged. Each config contains just one model
and requires only its provider key. The complete batch needs OPENAI_API_KEY,
GOOGLE_API_KEY and XAI_API_KEY.

All task groups use the historical evaluation seed nexus-cross-axis-pilot-v1,
600 tool calls and 650 turns. The evaluation seed is harness provenance; the
matrix's generator seeds select the new worlds. Neither a common effort label nor
a common turn limit makes inference compute equal across providers.

## Fresh T/D fixtures

T denotes theory/model construction and D denotes discovery through experiments.
The fresh revision fixtures require interpreting behavior and constructing an
evidence-supported mechanism. Repair fixtures require selecting interventions
and finding a repair valid in both contexts.

| Rows | Generator seed | Condition | Action allowance | Public reference actions |
|---|---:|---|---:|---:|
| F01 / F02 | 2073 | Revision supplied law / hidden law | 64 / 64 | 4 / 18 |
| F03 / F04 | 2178 | Revision supplied law / hidden law | 64 / 64 | 4 / 18 |
| F05 / F06 / F07 | 541 | Repair supplied solution / hidden standard / hidden plus six | 8 / 30 / 36 | 5 / 27 / 27 |
| F08 / F09 / F10 | 586 | Repair supplied solution / hidden standard / hidden plus six | 8 / 30 / 36 | 5 / 27 / 27 |

Controls are F01, F03, F05 and F08. The td suite contains the other six rows.

Revision hidden fixtures use T3/D5, principles guidance, recoverable finish and
consistency checking off. The supplied-law counterparts use T0/D0. Both retain
P0/R1. Their reading-only certificate sizes are respectively 5 and 4, and both
need query length 5 before the closure of all queries through that length
identifies the behavior. The qualifier computes the certificate, checks its live
witness, and independently rules out every certificate of at most three readings.
It does not independently prove the absence of four-reading certificates for the
size-five fixture. These are information properties of the actual outcomes,
not a lower bound on a model's internal reasoning depth or a guarantee that
guessing cannot succeed.

Repair uses P1/R1 and retains its intervention/context obstructions. Qualification
checks the three-reading lower bound, that passive closure does not supply a
common repair, that both contexts are needed, and that all 81 live repair choices
agree with the independent acceptance evaluator. The public evidence policy
achieves supported success within both hidden allowances.

Interpret these contrasts carefully. Revision changes T and D together, not one
axis at a time. The repair supplied-solution control also changes its allowance
from 8 to 30 actions; it is an execution control, not a pure difficulty effect.
F06/F07 and F09/F10 isolate allowance: identical science, reference actions and
reference events, with 30 versus 36 actions. Public reference lengths are feasible
policy lengths, not general optimal cognitive or experimental costs.

## Fresh P/R fixtures

P concerns planning and dependent subgoals; R concerns the available world actions.
The stateful-interference family exposes its complete laws, state and map. An
operation can disturb a coordinate that already meets its goal. Its independent
counterpart removes the cross-bank dependency while preserving the selected
kernel and target. Each fresh seed crosses two horizons, two coupling settings
and two resource levels, giving eight rows per seed.

The exact minimum below includes take and finish. Tight R2 equals that minimum.
Relaxed R1 adds max(6, ceil(minimum/2)) actions.

| Suite | Seed | Horizon | Coupling | Tight row / allowance | Relaxed row / allowance |
|---|---:|---|---|---|---|
| pr-a | 107 | short | independent | F11 / 12 | F12 / 18 |
| pr-a | 107 | short | coupled | F13 / 22 | F14 / 33 |
| pr-a | 107 | long | independent | F15 / 22 | F16 / 33 |
| pr-a | 107 | long | coupled | F17 / 36 | F18 / 54 |
| pr-b | 109 | short | independent | F20 / 17 | F19 / 26 |
| pr-b | 109 | short | coupled | F22 / 22 | F21 / 33 |
| pr-b | 109 | long | independent | F24 / 35 | F23 / 53 |
| pr-b | 109 | long | coupled | F26 / 37 | F25 / 56 |

Resource order is reversed in the second block to reduce a fixed tight-first
ordering effect. The two blocks remain purpose-selected worlds, not randomized
replicates. Horizon changes the target on one kernel; coupling changes dependency
laws at one target. For those comparisons the resource *rule* is fixed but the
absolute action allowances can differ. Attribute a pure allowance effect only to
the same-world tight/relaxed pair.

Qualification independently checks the complete transition tables, exact physical
costs, live reference execution and replay, optimal interleaving versus restricted
bank-by-bank plans, and unavoidable coordinate-goal regression in coupled worlds.
The fresh long coupled minima are 36 and 37 actions. These are longer than the
short counterparts, not a claim that a new empirical failure boundary exists.

## Selection and novelty

Selection was completed before any live outcomes for these fixtures. It was
purposeful, using existing mechanical admission criteria:

- Revision scan 2001–2256 sought certificate size at least four and identifying
  query horizon at least four. 2073 and 2178 meet these rules. 2128 was excluded
  because it has the same behavior class as 2073.
- Repair scanning first tried 701–800, whose modulo-population mapping was
  unsuitable, then 501–614. Admitted candidates included 541, 542, 586 and 607.
  542 is historical; 541 and 586 were selected as distinct admitted missions.
- Interference seeds 107 and 109 produced admitted kernels at generator attempts
  seven and two respectively. Their complete eight-condition blocks qualify.

The report compares revision behavior classes, repair measurement-and-acceptance
signatures and resolved interference kernels against the committed historical
matrices and cross-axis fixtures. Both new identities in each family differ from
each other and from those recorded fixtures. A new numeric seed alone would not
have established that. This check is scoped to recorded history and these
identities; it does not prove nonisomorphism or a representative population sample.

## Anchor, admission and stopping rules

The anchor suite contains exactly the historical S05, S08, S21, S22, S23 and S24
task objects, prompts, world seeds and task limits. The all-in-one batch runs it
once for Astra, then runs each model's controls, td, pr-a and pr-b in that order.
The anchor is a comparison, not a pass gate: ordinary recorded task failures do
not prevent fresh evaluation.

Fresh challenges require all four fresh controls to have accepted victory
receipts under the matching release, runtime, binary, evaluation seed and exact
input config. The runner also compares recorded inference settings and qualified
task objects. Partial control reruns may fill the record; the newest matching
attempt for a control overrides an older pass. Changed settings or a changed
MindTrial binary require new controls. A newer corrupt or incomplete selected
result cannot silently fall back to an older success.

This gate checks receipt acceptance and recorded configuration; it is **not** an
offline canonical-replay audit. A control failure can itself be scientific
evidence. Retain it and diagnose whether it concerns execution, interface,
response limits or receipt formatting before resuming challenges.

The unattended launcher stops the batch on a rejected control gate, incomplete
results, interruption, launcher failure or recognized provider HTTP errors
(including billing/quota, rate limits, authentication and server failures). There is no automatic
retry. An ordinary completed challenge failure remains a result and does not halt
later challenges. Selected interactive reruns remain available.

## Readout and decisions after the run

Keep every attempt, including abandoned and failed controls. Summarize world
success, submitted-receipt acceptance and supported evidence use separately.
For every failure record actual world status, provider/harness stop, usable tool
access, accepted world actions, and the first point of physical infeasibility
where an exact solver supports that conclusion. A response-length stop after a
fatal detour has both observations; it is not solely an inference-cap failure.

For P/R compare the eight matched allowance pairs per model, then horizon and
coupling within each seed. Report individual pair outcomes rather than a pooled
success rate that hides seed or factor differences. For repair compare the two
30/36 pairs; for revision compare the two supplied/hidden pairs. Two worlds and
one attempt per cell can identify promising contrasts, not estimate stable
thresholds or establish a model ranking.

If the Luna budget effect repeats, use it to calibrate a subsequent seed bank.
If Grok completes controls but exposes meaningful challenge failures, prioritize
bounded repetitions of the discriminating pairs. If all four models solve these
worlds, move to broader composition or stronger subgoal dependence rather than
inflating certificate size alone. If Astra fails hidden T/D, audit and repeat that
specific contrast with supported-evidence and response-stop analysis before
claiming a pure T/D boundary. The six historical anchors help distinguish a fresh
fixture effect from a contemporary model/configuration change.

Preserve deterministic replay, disclosed controls and independent qualification
when adding breadth. A repeatable framework with useful cross-model distinctions
remains valuable even without strongest-model failures from one axis alone.

## Implementation and reproduction

The frozen [matrix](fresh-world-matrix.json) is validated against the complete
inventory. Operator qualification lives in scripts/fresh_worlds.py, outside the
runtime package. The original 3 November run used runtime digest
`ba22502788acf7ce1684e1e527e5aa332cd1746b37423fececabc90d71b8ee83`.
Current packages bind the exact new source digest in their release manifest.
The original task laws and contrasts remain fixed; source identity must still
match the current qualification report.
The report separately binds the qualifier itself and the historical matrices.
Package creation recomputes the proof and exact task exports; container preflight
does so again before a paid run. Private witnesses remain in operator reports,
outside model-visible prompts and observations.

See the [current-source proof](research/fresh-world-preflight-current.json) and
[original validation record](research/fresh-world-validation-2026-11-03.md).
