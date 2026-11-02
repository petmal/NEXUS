# NEXUS: smaller-model trials and the next research phase

Evidence through 1 November 2026, America/Toronto. Latest source:
`smoke-test-v3.zip`. This is an operator report, not a player prompt.

## What changes

**The new runs refine the roadmap rather than overturn it.** NEXUS already
produces useful differences between tested configurations. Further broad
increases in world complexity are not the immediate priority: response limits,
provider behavior, evidence use and physical-action efficiency must first be
distinguished. The latest repetitions make that distinction more important.

| Question | Assessment |
|---|---|
| Do the original T/D conclusions change? | The narrow conclusion remains: no reliable strongest-model failure boundary from T/D alone was demonstrated. The smaller-model evidence strengthens the practical value of revision and repair as challenges. It does not establish a pure T or D effect or invalidate the earlier qualification results. |
| Does the P/R work remain useful? | Yes. The earlier Luna action-budget effect remains the clearest result. The new GLM repeat shows that its tight interference failure was not stable. Repair still distinguishes configurations, but response-length stops prevent treating every failure as a physical-resource effect. |
| Does the roadmap change? | Its architecture choices remain sound. Its order should change: improve outcome classification and inference reproducibility, run bounded diagnostics, then test fresh qualified worlds and add controlled breadth/dependencies. Another unchanged broad rerun is now low priority. |

Here **T** controls how much theory is disclosed, **D** describes how information
must be obtained, **P** concerns planning and coordination, and **R** limits world
actions or resources. A model's response-token allowance is an additional
evaluation constraint; it is not the same resource as the world's action budget.

## 1. What is new in the compiled archive

The archive contains 46 unique attempts: four disclosed controls, 28 initial
challenge attempts, and **14 new repetitions**. The first four folders, containing
32 attempts, are byte-identical to the previous archive. They must not be counted
again as new observations. The repetitions cover interference 09/11/25/27 and
repair S22/S23 for each model, followed by a separate S08 repeat for each.

Source commit, installed runtime, model presets, actual MindTrial binary, seed,
world inputs and token ceilings match the earlier GLM/MiniMax runs. Both models
retain `disable-structured-output: true`. The new runs use interactive selection;
the unused rows in the fourteen-task files are intentionally unselected, not
missing executions. All requested repetitions have saved records and traces.

MindTrial records **3 Passed, 3 Failed and 8 Error** for the 14 new attempts.
Replay gives a more useful explanation:

| New outcomes | Count | Meaning |
|---|---:|---|
| Accepted, evidence-supported wins | 3 | All are GLM: 09, 25 and S23 |
| World action budget exhausted | 1 | MiniMax S22 |
| Response stopped at `length` | 7 | Five are raw `Error`; two are raw `Failed` because text was returned |
| No response candidates | 3 | MiniMax 09, 11 and 25; distinct from length stops |

All original labels are preserved. The audited cause is an additional field,
not a replacement score. In particular, **two of the three new raw `Failed`
results are not world-action failures**.

### New repetitions, row by row

Counts show accepted actions / world allowance. `Length + text` means the
provider returned ordinary answer text at a length stop; validation then ended
an incomplete mission. `Empty` means no response candidates, without a recorded
terminal length reason.

| Row | GLM 5.2 xhigh | MiniMax M3 default |
|---|---|---|
| interference 09 | Supported win, 17/17 | Empty, 0/17 |
| interference 11 | Length, 0/35 | Empty, 0/35 |
| interference 25 | Supported win, 17/26 | Empty, 12/26 |
| interference 27 | Length, 0/53 | Length + text, 7/53 |
| S22 | Length, 19/30 | World budget exhausted, 30/30 |
| S23 | Supported win, 34/36 | Length + text, 15/36 |
| S08 | Length, 41/64 | Length, 35/64 |

The full compiled GLM/MiniMax challenge record, excluding controls, is 42
attempts with 21 accepted wins, including 19 supported wins. The unsuccessful
attempts comprise four world-action failures, fourteen length stops and three
no-candidate errors. The selected repeats concentrate on problematic rows, so
their 3/14 pass count must not be compared with the initial 18/28 as a general
performance trend.

## 2. Findings that materially affect interpretation

### GLM's short tight planning failure does not reproduce

Previously, GLM spent an unnecessary probe on interference 09. With a budget
equal to the exact 17-action minimum, that extra action made completion
impossible. It reached the target but could not afford the required finish.
The repeat wins in the optimal 17 actions. Both relaxed 25 attempts also win
optimally.

The combined result is **1/2 wins tight versus 2/2 with slack**. The original
failure remains a valid example of resource-management error. It is not a
stable inability to perform the short plan, and two attempts do not estimate
the size of a resource effect accurately.

GLM's long coupled rows 11 and 27, however, stop at the response limit in both
attempts: four stops across tight and relaxed conditions. Three occur before
any physical action; the original relaxed attempt stops after 15. This is a
repeatable limitation of the tested configuration on these cases, but it does
not identify a physical-action threshold. The short-to-long comparison changes
both required work and coupling, so neither cause is isolated.

### GLM can reach an evidence-supported repair

GLM's first S23 win used 31 actions and left a plausible alternative in which
its repair failed. The new attempt uses 34 actions, obtains sufficient evidence
by turn 31, and wins with a repair supported by every remaining possibility.
Both S23 attempts win, but only one is supported. Its single S24 win remains
compatible rather than supported.

This updates the earlier concern: GLM is capable of justified discovery on this
repair world, although it does not achieve it consistently. S22 remains 0/2:
the first attempt exhausted its world budget after applying the correct repair;
the second hits the response limit with 11 world actions left and unresolved
uncertainty. A 30-to-36-action benefit is suggested by the outcomes, but it is
not a clean estimate of resource rescue when the stopping causes differ.

### MiniMax's six-row repeat has a conspicuous response/accounting change

The six-row MiniMax repetition reports **172,636 output tokens but only eight
reasoning tokens**. The earlier full screen reported 954,544 reasoning tokens
within 978,324 output tokens. Its later, separate S08 repeat reports 91,491
reasoning tokens within 94,620 output tokens. Long analysis-like prose also
appears as ordinary answer content in the six-row batch.

Recorded settings and the MindTrial binary are unchanged. These observations
do not prove that reasoning was disabled or that the underlying model changed.
Routing, provider behavior, response-channel handling and usage accounting are
possible explanations; the artifacts do not identify the cause. Keep this batch
in the end-to-end results, while flagging it before making a capability comparison.

Three attempts end with no response candidates. Two others stop at `length`
after returning text: interference 27 still has **46 world actions available**,
and S23 has **21**. The independent physical audit finds a 34-action continuation
for interference 27 at its stopping state. The world was recoverable; validation
finalized it after the truncated answer. Neither failure demonstrates that the
world allowance was insufficient.

MiniMax S22 is a genuine world-budget loss: all 30 actions are spent, eight
measurements leave 17 possible worlds with no common repair, and no finish is
submitted. Its earlier attempt won with support in 29 actions. Thus this row
shows variability, with the additional response/accounting caveat above.

There are five malformed calls across the new MiniMax attempts: two incomplete
JSON arguments on 25, two missing operation fields on S23, and one on the later
S08 run. They recover sufficiently to continue. S23 also has two validly formed
world actions rejected for missing configuration. This is weaker interface
reliability than the first screen, despite keeping structured output disabled.
It does not negate the earlier compatibility improvement.

### S08 remains hard, but the failure mechanism varies

Both new S08 attempts hit the response limit. GLM stops after 41 actions with
four possible behaviors remaining; MiniMax stops after 35 with two. Neither has
gathered enough evidence for a guaranteed solution, and neither has submitted a
finish.

This differs from GLM's first S08 attempt: that run had sufficient evidence by
turn 44, then submitted builds contradicted by it and exhausted the world budget.
Earlier Flash failures similarly included enough evidence followed by inconsistent
submissions. The same unsuccessful row can reflect experiment selection, use of
evidence, execution or inference limits. A single explanation for all S08 losses
would discard useful information.

## 3. Combining the smaller-model evidence

These are model configurations, not a parameter-size ranking. Flash is a strong
baseline; GLM and MiniMax were chosen partly because the supplied MindTrial text
leaderboard showed more headroom. Effort labels and provider implementations do
not allocate equal compute. There is no new Grok, Muse or Mistral evidence in
this archive.

### A common first-panel comparison

The following uses the first comparable attempt on the **same sixteen task/world
conditions** for each model: two controls plus fourteen challenges. It excludes
later repetitions, the earlier structured-output GLM/MiniMax attempts, and the
superseded Google credit-error panel. World inputs match exactly; model settings
and external inference behavior differ.

| Configuration | Accepted wins / 16 | Supported wins | Raw Failed | Raw Error |
|---|---:|---:|---:|---:|
| Luna, medium | 6/16 | 6 | 10 | 0 |
| Flash 3.8, high | 13/16 | 13 | 3 | 0 |
| GLM 5.2, xhigh | 11/16 | 9 | 3 | 2 |
| MiniMax M3, default | 11/16 | 11 | 0 | 5 |

This describes this panel, not a general model ranking. In particular, MiniMax's
errors remain in the denominator, while GLM's compatible wins remain valid wins.

### Repeated revision and repair conditions

Each cell is **wins / attempts [supported wins]**. Counts include the first
attempt and all relevant repetitions once. Denominators differ because the
controls and S24 were not repeated for GLM/MiniMax.

| Condition | Luna | Flash | GLM | MiniMax |
|---|---:|---:|---:|---:|
| S05: disclosed revision | 3/3 [3] | 3/3 [3] | 1/1 [1] | 1/1 [1] |
| S08: hidden counterpart | 1/3 [0] | 1/3 [1] | 0/2 [0] | 0/2 [0] |
| S21: disclosed repair | 3/3 [3] | 3/3 [3] | 1/1 [1] | 1/1 [1] |
| S22: hidden repair, 30 actions | 1/3 [1] | 1/3 [1] | 0/2 [0] | 1/2 [1] |
| S23: same repair, 36 actions | 1/3 [1] | 3/3 [3] | 2/2 [1] | 0/2 [0] |
| S24: second repair, 36 actions | 0/3 [0] | 2/3 [2] | 1/1 [0] | 1/1 [1] |

A supported solution works in all worlds still consistent with the observations
available before submission. It need not identify one unique law: multiple
worlds may accept the same repair. A compatible win works in the actual world
but not in every remaining alternative. This distinction measures evidential
justification, not the model's private reasoning process.

Across these configurations, S05 is consistently solved while S08 is difficult.
The contrast is useful, but joint T/D changes and external response limits prevent
calling it a pure intrinsic-discovery effect. Flash's repair contrast remains the
cleanest repeated repair resource result: 1/3 supported wins at 30 actions and
3/3 at 36. Luna does not show that rescue. GLM's repeat adds a supported S23 win;
MiniMax's outcomes are too affected by response behavior to resolve its R effect.

Other earlier findings remain important:

- **Stateful discovery S01/S02/S03:** all four configurations pass all three
  first-panel rows. Actions are 10/17/26 for Luna, 10/11/38 for Flash, 10/10/37
  for GLM and 11/15/26 for MiniMax. Removing information increases work more
  clearly than it changes success in this small family.
- **Disclosed interference:** across the earlier full sixteen pairs, Luna wins
  1/16 tight and 13/16 relaxed. Twelve pairs change from loss to win with slack,
  with no reverse pair. Astra wins all 32 optimally. Flash wins 3/4 tight canaries
  and all four relaxed counterparts. Those data remain stronger evidence of an
  R effect than the latest small GLM/MiniMax repetitions.
- **Spatial planning:** Flash solved all eight earlier layouts optimally. GLM
  and MiniMax solve selected tight S13/S16 optimally; Luna's wider results were
  non-monotonic in P labels. Spatial P3 is not a universal difficulty threshold.
- **Unsupported successes persist:** earlier repeated S10 wins, particularly
  Flash's three compatible wins, and GLM's compatible repairs make qualified
  alternative-world tests more informative than more repetitions of one favorable
  truth.

The initial and repeated tables overlap. Their counts must not be added into
one score. Repetition on a fixed seed measures variability on that case; it
does not replace sampling new mechanisms.

## 4. Implications for the original T/D conclusion

The original synthesis concluded that the tested designs had not reliably
defeated the strongest model through T/D alone. Its final controlled screen
produced 40/40 accepted wins, of which 34 final submissions were supported.
The new runs contain no contemporary Astra revision/repair comparison, so they
cannot reverse that specific conclusion.

They strengthen a different conclusion: **the retained T/D architectures can
produce meaningful discrimination among practical model configurations**. S08
separates disclosed execution from hidden reconstruction across four families.
Repair separates actual success from justified decisions and interacts with
action allocation. Those are useful evaluation properties even without a
strongest-model failure threshold.

The qualifications also remain unchanged. Large hypothesis counts are not
automatically large decision uncertainty; a deep-looking task may admit a shallow
legal policy; a reference policy is an upper bound unless optimality is proved.
No new run removes those shortcuts or strengthens the old mathematical bounds.
The S03 reference of 41 actions and repair reference of 27 are still upper bounds,
so models may legitimately win faster.

Keep a bounded T/D research track focused on specific questions: distinguishing
alternative repairs, selecting useful experiments, and testing whether consistency
assistance changes evidence-use failures. Give it fresh qualified worlds and
matched controls. A broad expansion of the same finite grammar is not justified
by response-length errors alone.

## 5. Implications for P/R and the roadmap

P/R remains a productive direction. Exact physical costs let us explain losses
that a pass count hides: a wasted probe, failure to reserve a finish action, or
unnecessary travel. The strongest existing resource evidence survives these runs.
What changes is confidence in a few proposed boundaries and the order of work.

| Priority | Next work | Evidence needed before advancing |
|---|---|---|
| 1 | Preserve raw scores and add an explicit stopping-cause view: world budget, length with/without text, empty candidates, malformed calls and receipt delivery. Retain both pre-validation world state and finalized state. | The known MiniMax 27/S23 cases classify as length stops with unused world actions, without rewriting their raw Failed labels. |
| 2 | Investigate MiniMax response/accounting variation; record request/generation identifiers, upstream provider, returned model, native stop reason and per-response usage where available. Pin a supported route for a new diagnostic configuration if possible. | Short disclosed controls work consistently and response/usage semantics are interpretable. Preserve the anomalous batch as observed evidence. |
| 3 | Run a small GLM inference-allocation diagnostic on 11/27. Compare the current setting with one verified supported alternative, changing only a completion ceiling or an effort setting. Recheck controls for a changed configuration. | Determine whether the repeated stops mainly reflect the chosen generation allowance. More world actions alone do not test that explanation. |
| 4 | Confirm useful scientific contrasts on a small set of fresh qualified seeds and rival worlds. Include a contemporary Astra anchor on the same revision/repair tasks before updating claims about the strongest model. | Disclosed controls succeed; effects survive beyond one truth; failed solutions can be attributed to evidence, decisions or execution. |
| 5 | Extend breadth and dependency depth separately, with independent and interacting tasks at the same component count. Add resource pressure after generous-budget feasibility and baseline execution are established. | Joint solvability, legal information access, valid alternative solutions and mandatory physical work are mechanically qualified and independently checked. |

Do not launch another full unchanged GLM/MiniMax screen now. The last recommended
repetitions have been completed. MiniMax needs a focused integration/inference
diagnostic; GLM's repeated long-plan length stops now justify the separate
generation-setting experiment previously deferred until repetition. Complete
Grok's screen and the Muse/Mistral followups if still pending, without expanding
the number of models simply to obtain more failures.

The architecture priorities remain:

- **Model revision:** bounded reconstruction, evidence consistency and eventual
  interacting constructions. Current evidence supports targeted diagnosis rather
  than indiscriminate growth in the program grammar.
- **Compositional repair:** decisions under uncertainty, intervention choice and
  shared constraints. Preserve overlapping valid repairs; do not force needless
  unique-law identification just to make a benchmark harder.
- **Stateful interference:** disclosed planning, dependencies and reopening of
  completed goals with exact continuation costs. It is the strongest basis for
  isolating physical P/R effects.
- **Stateful discovery and spatial layouts:** retain as calibration and execution
  controls, and as regression coverage when introducing larger compositions.

NEXUS should report a profile of performance under specified constraints:
accepted success, evidence support, action efficiency, response reliability,
tokens and time. It should not optimize solely for making every model fail.
Repeatability, auditability and customization are already useful outcomes and
remain acceptance criteria for each extension.

## 6. Audit, compute and sources

The latest 14 attempts used 839,507 reported output tokens, including 660,699
reasoning tokens, and 76.5 minutes of aggregate provider-request time. That is
not end-to-end wall time or a measured compute allocation. Input totals include
cache reads; output totals include reasoning. The MiniMax reporting anomaly
prevents treating reasoning-token deltas as an efficiency improvement.

Official OpenRouter documentation explains that reasoning and visible output
usually share the completion allowance, and that consuming it can produce an
empty-content `length` response. This supports the stopping-cause interpretation,
but aggregate task usage does not recover exact final-request usage. Its generation
metadata API exposes provider and native finish-reason fields that can improve
future diagnostics. These documentation facts do not identify which upstream
behavior caused the MiniMax batch. [W1, W2]

Replay verified all 46 compiled attempts: **1,056 successful public responses,
795 accepted actions and all 210 captured action-hash records**. The 14 new
attempts contribute 307 responses, 227 actions and 89 hash records. All 1,061
tool attempts are accounted for; five malformed calls have no public response.
Two invalid-JSON calls are present in detailed calls/logs but excluded from
MindTrial's aggregate ToolUsage count, so the audit uses explicit call identities.
Independent scalar transitions and reverse search check 22 disclosed trajectories.

Original receipts are checked against emitted codes and recorded validators.
Replay uses a fresh secret; it does not claim to reconstruct the unavailable
original HMAC. The compiled archive's old folders are verified byte-for-byte.
Historical Luna/Flash/Astra comparisons use their previously replayed audits,
with trace identities and source hashes retained; this report does not claim
to repeat those entire older replays. Provider routing and immutable upstream
model versions remain unresolved provenance limits.

- Latest archive SHA-256: `00c861c0247c487c3905d0a1083ed7e05fbd77b00534080d4e1cba464e7cd25c`.
- Evaluated NEXUS source: `92fa0888546498373f4c011a79778b7caf614f12`.
- Runtime SHA-256: `ba22502788acf7ce1684e1e527e5aa332cd1746b37423fececabc90d71b8ee83`.
- Actual MindTrial binary SHA-256: `95c57d56e3d8739c19c4be1d33ec8de876c6522a003704c4f2d277978baf8660`.
- Evaluation seed: `nexus-cross-axis-pilot-v1`.

Project evidence:

- [Original T/D synthesis](https://github.com/petmal/NEXUS/blob/5b21d99a551b44f79750892fbde772b8696f55f0/docs/td-experiments-and-next-directions.md).
- [Consolidated earlier smoke findings](https://github.com/petmal/NEXUS/blob/5b21d99a551b44f79750892fbde772b8696f55f0/docs/research/smoke-findings-2026-10-31.md), including
  source hashes and Luna/Flash repeat counts in its JSON companion.
- [Initial GLM/MiniMax screen audit](capability-screen-results-2026-10-31.md).
- [Text-output controls](capability-text-output-controls-2026-10-31.md).
- [Current machine-readable synthesis](capability-repeat-synthesis-2026-11-01.json).

External documentation, checked 1 November 2026:

- W1: [OpenRouter reasoning-token budgets](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens#reasoning-tokens-and-max_output_tokens).
- W2: [OpenRouter generation metadata](https://openrouter.ai/docs/api/api-reference/generations/get-generation).
