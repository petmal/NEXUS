# GLM and MiniMax challenge-screen results

Runs dated 31 October 2026, America/Toronto. Source: `results-v1.zip`.
This report covers 28 new attempts. The four controls in the archive are
byte-for-byte copies of the previously analysed text-output controls; they are
comparison evidence, not four new repetitions.

## Result and interpretation

**Both models passed 9 of 14 challenge rows, but they failed in different ways.**
GLM has three world-action-budget failures and two response-length errors.
MiniMax has five response-length errors. All nine MiniMax wins are supported by
the evidence it collected; two GLM wins are compatible with its evidence but
not guaranteed by it. This is useful discrimination between configurations,
without establishing a stable ranking or a pure single-axis failure boundary.

| Configuration | Attempts | Accepted wins | Evidence-supported wins | World failures | Response-length errors |
|---|---:|---:|---:|---:|---:|
| GLM 5.2, xhigh | 14 | 9 | 7 | 3 | 2 |
| MiniMax M3, provider default | 14 | 9 | 9 | 0 | 5 |
| Total, new screen only | 28 | 18 | 16 | 3 | 7 |

A **supported win** succeeds in every world still consistent with the public
evidence available before the successful submission. A **compatible win** works
in the actual world but fails in at least one remaining alternative. Both are
valid wins with accepted receipts. Support measures what the observations
justify; it does not reveal the model's private reasoning or prove that it
explicitly considered every alternative.

The screen shows three different limits: spending physical actions efficiently,
using observations to select a correct solution, and producing an actionable
response within the configured generation budget. NEXUS should preserve all
three measurements rather than collapsing them into one explanation of failure.

## Results by condition

Numbers in parentheses are accepted actions / world action budget. Every win
below also passed MindTrial's exact final-receipt validation. `Length` means the
provider stopped a response with `length` and MindTrial received no actionable
content; the world was still active.

| Row | Condition | GLM 5.2 | MiniMax M3 |
|---|---|---|---|
| interference 09 | Short independent plan, tight | Failed (17/17) | Supported win (17/17) |
| interference 11 | Long coupled plan, tight | Length (0/35) | Length (0/35) |
| interference 25 | Same world as 09, slack | Supported win (17/26) | Length (0/26) |
| interference 27 | Same world as 11, slack | Length (15/53) | Length (0/53) |
| S01 | Stateful world, disclosed solution | Supported win (10/64) | Supported win (11/64) |
| S02 | Same world, laws disclosed | Supported win (10/64) | Supported win (15/64) |
| S03 | Same world, laws hidden | Supported win (37/64) | Supported win (26/64) |
| S08 | Hidden revision; disclosed control S05 | Failed (64/64) | Length (31/64) |
| S22 | Hidden repair, standard allowance | Failed (30/30) | Supported win (29/30) |
| S23 | Same repair as S22, six extra actions | Compatible win (31/36) | Length (14/36) |
| S24 | Second hidden repair world | Compatible win (25/36) | Supported win (32/36) |
| S13 | Disclosed spatial P0, tight | Supported win (11/11) | Supported win (11/11) |
| S16 | Disclosed spatial P3, tight | Supported win (22/22) | Supported win (22/22) |
| S17 | Same world as S16, slack | Supported win (25/33) | Supported win (24/33) |

The earlier same-configuration S05 controls passed in four actions for both
models. S21 passed in six actions for GLM and eight for MiniMax. These remain
the appropriate disclosed controls. The older structured-output failures belong
to a different integration cohort.

## What materially changes the interpretation

### 1. The seven errors are generation-budget outcomes

Every error says `model response contained no actionable content`, with stop
reason `length`. This is different from the earlier missing-argument and
structured-output problems. Both models retain `disable-structured-output: true`;
all 707 new tool calls completed successfully, with no malformed protocol calls.
There is no recorded billing or HTTP failure explaining these seven stops.

The configured completion ceiling is **65,536 tokens per response**, including
reasoning under the recorded accounting convention. Task usage aggregates many
responses, so a task reporting more than 65,536 output tokens does not imply
that the cap was violated. The artifacts do not give a precise final-response
token breakdown or establish why that response failed to become actionable.

Four errors occurred after reading the public material but before taking any
world action: GLM 11 and MiniMax 11/25/27. GLM 27 stopped after 15 actions with
38 available; an independent shortest-path calculation still finds a 28-action
physical continuation. MiniMax S08 stopped with 33 actions available, and S23
with 22. None had exhausted the world's allowance or the 600-call/650-turn
harness ceilings.

Count these as unsuccessful attempts under the fixed evaluation configuration.
Keep their cause separate from world-action failure. Dropping errors would make
MiniMax look perfect on its nine remaining rows and obscure a substantial
reliability limitation. Conversely, treating them as proof of inadequate
physical planning or discovery would overstate what the traces establish.

### 2. GLM 09 exposes a precise action-management failure

The exact physical minimum is 17 actions, including taking the seal and the
mandatory final `finish`. GLM takes the seal, then spends turn 2 on an unnecessary
probe despite having disclosed laws. At that point 16 actions are still needed
but only 15 remain. Every subsequent physical operation follows a shortest
continuation. It reaches the target on action 17, after which `finish` is rejected
because the episode has already ended.

The relaxed counterpart, 25, wins in the optimal 17 actions. That is a clean
candidate resource effect, but it is only one attempt per condition and the
trajectories differ. Slack did not merely extend the failed trajectory; the
model also chose a better trajectory. MiniMax wins tight 09 optimally but hits
the response ceiling before acting on relaxed 25. That reversal requires a
repeat, not a claim that extra world resources make the problem harder.

Rows 11/27 require 35 physical actions, but their response stops prevent a
clean comparison of action allowances. The 09↔11 contrast changes both horizon
and coupling. It does not isolate either feature or establish a 17-to-35-action
planning threshold.

### 3. GLM S08 collected sufficient evidence, then failed to use it

GLM makes 25 measurements, 17 of which do not reduce the remaining uncertainty.
By turn 44 its accumulated evidence identifies a guaranteed repair, leaving
20 actions. It still makes five further measurements. Its finish attempts on
turns 53, 60, 63 and 64 submit builds contradicted by the evidence already
available. An earlier attempt on turn 30 was compatible with incomplete evidence
but wrong in the actual world.

Thus insufficient observations are not a sufficient explanation of this failure.
The trace supports a problem with interpreting evidence, translating it into a
build, or retaining and applying the resulting decision. It cannot distinguish
those internal causes. MiniMax stops earlier, with three alternative worlds and
no common repair, so its S08 trace supports a different diagnosis.

Both passed disclosed S05. The S05↔S08 contrast is therefore promising across
these configurations, consistent with the earlier Luna/Flash repetitions.
However, it changes theory/discovery demands together; this is not an isolated
T or D effect. The new models each have only one hidden-world attempt.

### 4. GLM repair wins do not yet demonstrate reliable discovery

On S22, GLM submits two wrong repairs, then applies the correct one on its last
available action. The physical target is satisfied, but no action remains to
finish. Three worlds with different winning repairs are still consistent with
its evidence. Its final-answer claim to have identified the mechanism is
therefore stronger than the mechanical audit supports.

On S23 and S24, GLM wins while retaining two alternatives with different winning
repairs; its chosen repair works in one of them. These are legitimate compatible
wins. S22 loss versus S23 win is a receipt-level resource contrast, not evidence
that extra actions reliably produced justified discovery.

MiniMax's S22 and S24 wins are supported. S24 retains two possible worlds, but
both accept the same repair. Unique law identification is unnecessary when the
remaining uncertainty cannot change the correct decision. MiniMax's S23 length
stop leaves its tight/slack comparison unresolved.

### 5. Some retained controls remain comfortably solvable

Both models pass S01/S02/S03. Hiding laws increases accepted work, but this
screen has no stateful-discovery failure boundary. The 41-action S03 reference
is an upper bound supplied by a qualified policy, not a proven minimum. Winning
in 37 or 26 actions does not violate qualification. The repair reference of
27 actions is also an upper bound.

In contrast, independent physical search verifies the spatial minima: 11 actions
for S13 and 22 for S16/S17. Both models solve the tight spatial rows optimally.
Their relaxed S17 wins use three and two extra actions respectively. Existing
spatial P3 is useful as a working control, but repeating it is a lower priority
than the informative failures and ambiguous wins.

## Recommended next sequence

1. **Repeat six screen rows once for each model: interference 09, 11, 25, 27;
   S22 and S23.** This is 12 new attempts. Keep the v3 text-output settings,
   effort, token ceiling, seed, world definitions and exact validator unchanged.
   Include the paired successes, not just failures. If splitting the work, run
   09/25/S22/S23 for both models first (eight attempts), then 11/27 (four).
   Retain the originals and append repetitions; do not replace errors with wins.
2. **Make S08 a separate, secondary two-attempt repeat**, one per model. GLM's
   original S08 used approximately 340,000 output tokens and 33 minutes of
   aggregate provider-request time. It is informative but expensive. Repeating
   the easy spatial rows or disclosed controls has less immediate value.
3. **If length stops recur, test inference allocation separately.** Use a small
   affected pair such as 11/27 and change only one verified provider-supported
   generation setting. First check which ceiling/effort controls the endpoint
   actually supports. A larger completion cap, if supported, tests truncation;
   a lower supported GLM effort tests whether its current setting over-invests
   before acting. Do not change both, invent a MiniMax effort option, or mix
   altered settings into the original cohort. Recheck controls for that new
   configuration. More world actions do not directly fix a per-response limit.
4. **Then broaden worlds, not merely repetitions of a favorable seed.** Qualify
   rival repair worlds for the GLM S23/S24 compatible wins, extending the earlier
   S10 recommendation. The alternatives should remain indistinguishable under
   the ambiguous observation sequence, require different repairs, and expose a
   legal discriminating experiment. Prove solvability and information separation
   before evaluation. Add a small fresh-seed sample to any contrast that survives
   repetition; two or three attempts on one seed are still not a population
   success estimate.
5. **Continue P/R development selectively.** Retain interference as the main
   base for exact planning costs and dependencies, repair/revision for discovery
   plus action allocation, and spatial planning as a disclosed execution control.
   For harder planning, increase mechanically required work or goal reopening
   while matching disclosure and allowance. Avoid increasing everything at once
   or cutting budgets below the proved minimum. Do not add broad new complexity
   before distinguishing repeated response limits from world-action limits.

The v3 package remains valid for these repeats. Choose the six named rows from
its `screen` suite using interactive selection. Its existing non-interactive
screen command runs all fourteen rows; a restricted unattended batch needs a
separately prepared task selection. No new test package or live evaluations are
part of this analysis.

Grok's screen, Muse's S21 answer-delivery repeat, and Mistral's response-format
diagnostic are not present in this archive. They remain separate outstanding
items. Do not count them as completed or infer their outcomes from GLM/MiniMax.

## Compute and audit record

| New screen only | Input tokens | Output tokens, including reasoning | Reported reasoning tokens | Aggregate request time |
|---|---:|---:|---:|---:|
| GLM | 20,284,699 | 1,167,855 | 1,160,551 | 109.3 min |
| MiniMax | 9,194,289 | 978,324 | 954,544 | 68.0 min |

Input totals include cache reads; output totals include reasoning. Do not add
those subcounts again. Request time is neither total wall time nor measured
compute. The proposed 12-row core consumed about 84 minutes of requests in the
original attempts; this is historical context, not a cost or duration forecast.
Provider routing, caching, effort semantics and stochastic generations prevent
a fair general efficiency ranking from these totals.

The audit verifies config/task hashes, source/image bindings, actual MindTrial
binary identity, complete launcher coverage, and stored qualification against
the committed reference. It joins trace and call identities, regenerates the
worlds, and replays every public response and accepted action. Including the
copied controls, this covers 749 responses, 568 actions and all 121 captured
action-hash records. New screens contribute 707 responses, 546 actions and
102 hash records. Every attempt read all listed evidence. The only rejected
world actions were GLM's two post-terminal finish calls on 09 and S22.

Fresh replay secrets verify deterministic world behavior. Original emitted
receipts are compared with submitted receipts and recorded validator acceptance;
the unavailable original private HMAC is not reconstructed. For interrupted
response errors, an active-state diagnostic is recomputed from the captured
trace; it is not presented as an original terminal report. Independent scalar
transitions and reverse search verify physical continuation costs for disclosed
interference and spatial rows. They do not certify cognitive difficulty.

- Archive SHA-256: `5f3718fc2d8570f71787884f9f6ae451e86085b973a0d4f0ece767a4852945ff`.
- Evaluated source: `92fa0888546498373f4c011a79778b7caf614f12`.
- Runtime SHA-256: `ba22502788acf7ce1684e1e527e5aa332cd1746b37423fececabc90d71b8ee83`.
- MindTrial binary SHA-256: `95c57d56e3d8739c19c4be1d33ec8de876c6522a003704c4f2d277978baf8660`.
- Seed: `nexus-cross-axis-pilot-v1`.

The [machine-readable results](capability-screen-results-2026-10-31.json) retain
per-row outcomes, evidence diagnostics, token usage and control-copy hashes.
These results support NEXUS's value as a repeatable and auditable evaluation
framework. Its strongest current contribution is showing *how* a configuration
fails under specified constraints, rather than declaring one universal difficulty
number or trying only to defeat the strongest model.
