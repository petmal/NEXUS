# Research reasoning: conclusions retained for the next iteration

Recorded 2026-10-22 after reviewing the user's two follow-up essays. This extends
[the earlier ten-category assessment](research-reasoning-assessment.md).

## Decision and resume gate

**Review the current `stateful-discovery-v1` real-model pilot before choosing or
implementing another iteration.** The user requested that this analysis be kept
for that review. These are research hypotheses and design candidates, not a new
implementation authorization or a prediction that particular models will fail.

The pilot implementation is `4db25dd05496b88db7caff9e5e93e87025853e09` on
`feat/theory-prior-axis`. Its [guide](stateful-guide.md),
[matrix](stateful-matrix.json) and [plan](stateful-discovery-plan.md) describe the
current experiment. No new real-model results are asserted here. Keep the pilot's
mechanics, settings and no-external-Python condition fixed while gathering results.

## What we agree and disagree with

The first essay identifies useful research challenges, but its ordering from
easiest to hardest is a hypothesis, not an established capability ranking. The
second essay's categorical claim of a “hard wall” at genuine discovery is too
strong. Evidence supports uneven, fragile and scaffold-dependent performance;
it does not establish a universal inability to discover anything novel.

The important distinction for NEXUS is **finding a model within a supplied
representation versus recognizing that a provisional representation is inadequate
and revising it**. A precise task objective is compatible with discovery: the
unknown can be the explanatory model or route to the goal. Vague instructions
are not needed to make the task scientifically difficult.

Success with a calculator or verifier is a property of the complete system.
Conversely, a correct final answer does not prove that the player checked its own
reasoning. Verification must match the claim: valid algebra does not establish
that the assumed physical model is adequate.

## What the cited research actually supports

| Source | Finding and qualification retained from the review |
|---|---|
| [NewtonBench](https://arxiv.org/html/2510.07172v2) | 324 tasks across 12 physics domains, with interactive experiment selection and modified laws. Surrounding equations and the discovery objective are supplied. This is stronger than passive curve fitting, but not unrestricted conceptual invention. “Memorization-resistant” is safer than a guarantee of no memorization. Code assistance has mixed effects across models. Detailed review used v2; the [version record](https://arxiv.org/abs/2510.07172) now lists v3, which should be rechecked before making version-specific comparisons. |
| [PRL-Bench](https://arxiv.org/html/2604.15411v1) | The reported best score is 44.27/100, a rubric score rather than the percentage of complete research projects solved. Code execution is enabled and search disabled. Tasks deliberately include relatively independent subtasks to reduce error propagation, so their aggregate score alone does not prove failure from long dependency chains. Attributions to sparse domain knowledge are interpretations, not causal isolation. |
| [TPBench](https://arxiv.org/abs/2502.15815) and its [weak-verifier study](https://arxiv.org/html/2506.20729v1) | Research-level physics was difficult for the tested, older model cohort. Symbolic assistance improves answer selection over the compared scaling methods. The weak verifier is fallible and is not a formal proof system or a check of all physical assumptions. |
| [MadEvolve](https://arxiv.org/html/2602.15951v1) | LLM-guided evolutionary search can produce useful scientific algorithm improvements when humans provide the problem, baseline and evaluator. This challenges blanket no-discovery claims without demonstrating autonomous general physics. An inadequate BAO objective also permitted reward hacking: external evaluators can have different blind spots rather than no blind spots. |
| [Scientific Discovery Evaluation](https://arxiv.org/abs/2512.15567) | Performance varies across research scenarios. Scientific research should be measured as several capabilities; aggregate rankings are not universal. |

These publications span 2025 and 2026. Their model cohorts, tools, objectives and
scoring differ from NEXUS. Their scores are not forecasts for Astra or a new pilot.

## What NEXUS has and has not tested

| Essay claim | Our evidence and remaining gap |
|---|---|
| Model-class discovery is harder than parameter fitting | T3 already includes structural alternatives and hidden interactions within complete bounded grammars. Strong results show competence there. Inventing or expanding an adequate representation remains less tested. |
| Long workflows accumulate reasoning errors | Repair, assembly and history families exercise dependencies. Extra stages did not reliably cause inference failure; some added procedural work after one decisive insight. Separate scientific inference from execution and state-tracking errors. |
| Models struggle to recognize their own mistakes | Evidence-support diagnostics distinguish a supported construction from a compatible guess. Whole-program acceptance tests the result, not deliberate falsification. Do not demand redundant experiments when the evidence already establishes a winning strategy. |
| Experiment design and anomaly diagnosis are weak | Calibration, confounding, reader/law inference and informative experiment selection have been tested. Disclosed bounded nuisances were often tractable. “Models do fine once given data” is also too broad. |
| Underdetermination and regimes of validity are hard | We test finite ambiguity and predictions outside measured cases. Noisy model adequacy and calibrated statistical uncertainty remain largely untested. Accept multiple explanations when they imply the same valid goal strategy. |
| Conceptual leaps and question selection are hardest | Mostly outside current coverage: missions, primitives and broad hypothesis spaces are given. New episode coefficients are not evidence of a new scientific framework. |
| Sparse frontier knowledge causes failures | NEXUS deliberately supplies the necessary artificial-world knowledge. It cannot verify this claim about specialized real physics; those benchmarks may mix knowledge, retrieval and reasoning failures. |

The completed discovery pilot recorded in the earlier assessment had **69/70
successful executions after replacing three provider-failed Gemini attempts**.
All 69 wins were evidence-supported under the complete prior. The remaining
failure described a valid compensator but never installed/submitted it. Another
model recovered after installing stale settings. All 496 recorded readings
matched the world. These are historical results, not results of the current
state-changing pilot.

That evidence challenges universal claims that models cannot perform bounded
interactive discovery. It neither verifies nor falsifies broad claims about
open-ended research, advanced mathematical derivation or noisy science. Increasing
hidden structure or procedural length alone has not reliably reduced success at
generous fixed resources.

The current stateful family couples experiments to the original goal object's
future state and options. Its exact qualification establishes specified action
lower bounds and excludes specified shortcut classes; it does not prove universal
cognitive depth or model failure. Its register structure and operator grammar are
still supplied, so it is not a representation-invention experiment.

## Preferred follow-up hypothesis: controlled model revision

Give a provisional model that correctly predicts one regime. Two controlled
preparation histories then reach the same visible reading, but the same next
operation produces different outcomes. The player must distinguish specimen
memory, apparatus memory or an observation-rule issue, revise the model, preserve
earlier valid predictions, and use the revised model to escape.

The world laws remain fixed; the provisional model is incomplete. Public controls
and the permitted construction language remain complete. If the manual already
provides the exact memory layout or correction form, this risks repeating earlier
bounded hypothesis selection under a different story. Conceal the correct
representation, not legal action syntax. Accept equivalent explanations and
common winning strategies; avoid compulsory theory essays or ceremonial stages.

Before implementation, qualification must establish:

- The disputed distinction matters to the goal, with no cheap blind strategy
  bypassing it at the intended difficulty.
- One-query diagnosis, fixed panels, reset/synchronization shortcuts and early
  commitment are audited against the full public prior.
- A repair passes both old and new regimes and relevant global constraints.
- Public grammar, simulator and independent verifier agree; capped or incomplete
  searches do not silently qualify episodes.
- Matched controls disclose the correct model structure at the same budget, so
  additional difficulty can be attributed more clearly to discovering it.

## Other retained design decisions

**Global constraints:** exact discrete conservation can bind local explanations
without calculus. A hidden reservoir can explain apparent loss in a visible
subsystem. A grammar that automatically conserves everything does not by itself
test whether the player discovers or enforces conservation. The useful challenge
is repairing an anomaly without breaking old predictions or the global ledger.
Conservation can also simplify inference, so added difficulty must be measured.

**Noise:** defer as a separate factor. It requires statistical identifiability,
uncertainty-aware grading and qualification. Exact finite elimination guarantees
do not transfer automatically; adding noise merely to lower scores is uninformative.

**Tools:** retain the no-Python primary condition. A later isolated in-NEXUS
calculator/simulator ablation could separate choosing the wrong model from
manually executing the right one. Do not expose private source, truth or reference
solutions, and do not assume tools help every model equally.

## Questions to answer after the pilot

Review supported first submissions, recovery, action overhead relative to the
appropriately scoped certified minima, control contrasts, and failure traces.
Distinguish law inference, experiment selection, state execution, logistics,
final-answer handling and infrastructure failures. Do not equate a reference
policy's cost with a proved optimum or a scientific-action bound with a complete
game-action minimum.

Then decide whether model revision plus preservation of global validity merits a
new PoC, or whether the current family first needs better diagnostics, controls or
qualification. No failure percentage or next architecture is committed in advance.
