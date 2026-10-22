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

## Follow-up: derive the admissible model, then identify it

The user proposed withholding the list of complete interaction functions while
retaining exact, noise-free measurements. The preferred challenge would require
deriving possible response forms from underlying laws, then fitting parameters
and checking the model, rather than guessing curves from their appearance. A
bounded polynomial with unnecessary coefficients equal to zero is one possible
restricted family. The user agreed to retain this proposal for post-pilot triage.

**Exact data does not imply a unique unrestricted law.** For observations at
`x = 0, 1, 2`, both `f(x) = 2*x` and
`g(x) = 2*x + k*x*(x-1)*(x-2)` agree for every k. A finite sample needs a justified
model class and sufficiently informative experiments. Within polynomials of
degree at most d over the rationals/reals, d+1 distinct samples determine a unique
polynomial. Excess coefficients become exactly zero if the true law has lower
degree and the measurements identify the fit; this does not follow from noise
removal alone. Multivariable designs require the corresponding full-rank condition.
The toy argument must not be transplanted blindly into modular worlds: check
field size, aliasing and identifiability in the actual arithmetic domain.

For deterministic exact measurements, use exact consistency, not a statistical
chi-squared threshold without a noise model. Several zero-residual candidates
require discriminating evidence or theoretical constraints. A simplicity
preference alone is not proof of the true mechanism. Identify laws only up to
behavioral equivalence where appropriate; a common supported winning strategy
can be sufficient even when the full law remains ambiguous.

### Illustrative derivation, not a proposed hard matrix row

Public principles for transfer J between chambers with imprints u and v:

1. Shifting both imprints by the same amount leaves J unchanged.
2. Exchanging chambers reverses J.
3. J is a polynomial of total degree at most three.
4. The amount leaving one chamber enters the other.

These principles imply dependence on `d = u-v`, odd symmetry, and consequently
`J(d) = a*d + b*d^3`. Measurements `J(1)=3`, `J(2)=12` imply `a=2`, `b=1`.
An independent check at d=3 predicts 33. Conservation gives
`qA_next=qA-J`, `qB_next=qB+J`; any physical implementation must also constrain
available inventories and legal settings. The extra check validates the
assumptions against another case; it is not mathematically necessary to identify
the coefficients within the supplied class. Do not force redundant experiments.

This illustrates theory-guided derivation and fitting, not a difficulty guarantee.
A large polynomial can reduce the challenge to linear algebra and bookkeeping.
Withholding a function menu may even simplify inference when principles collapse
the possibilities. Symmetries and conservation can make discovery easier.

The proposed semantic distinction, without changing existing profiles, is:

| Axis role | Intended reasoning |
|---|---|
| T1 | Derive the apparatus response from complete known laws and constants. |
| T2 | Derive a constrained response family; identify its unknown parameters. |
| T3 | Discover missing dependencies, hidden state or mechanism composition within a complete bounded construction language. Merely fitting a larger polynomial is not sufficient evidence of this capability. |
| D | Compose and reuse discoveries across causally dependent preparations, apparatuses and histories. Shared constraints must affect the actual goal; extra procedural stages alone are insufficient. |

The stronger candidate publishes primitive laws, invariants and construction
limits, but withholds derived apparatus equations and selected structural facts.
One model with shared parameters must explain several contexts and enable escape.
Permitted controls remain explicit; the truth remains within the public prior.

Primary references checked for this follow-up:
- [NIST interpolation theorem](https://dlmf.nist.gov/3.3): uniqueness requires a
  degree bound and distinct nodes in the stated setting.
- [Model structures and structural identifiability](https://arxiv.org/abs/2101.06382):
  distinguish parameter ambiguity from reliable prediction.
- [AI Feynman](https://arxiv.org/abs/1905.11481): exploit symmetry, separability and
  composition to simplify equation discovery.
- [SINDy](https://arxiv.org/abs/1509.03580): sparse term and coefficient selection;
  representation assumptions remain necessary.
- [NIST weighted least squares](https://www.itl.nist.gov/div898/handbook/pmd/section1/pmd143.htm):
  statistical weighting depends on assumptions about measurement variances.

## Tentative next-step triage (awaiting the current pilot)

These priorities are design judgements, not measured difficulty rankings. The
user explicitly requested waiting for the pilot before moving on. No new PoC,
mechanic, test matrix or tool access is authorized by this context-saving step.

| Priority | Candidate | Expected information value and overlap | Main risk / prerequisite |
|---|---|---|---|
| Gate | Analyze the existing stateful pilot and its matched controls | Establish whether failures concern inference, experiment choice, tracking, planning or execution; measure supported success and scoped action overhead. | Confirm image identity and separate infrastructure failures. Do not assume a bound is a full-game optimum. |
| 1 | Controlled model revision with preservation of old predictions and global constraints | Tests detection of an inadequate explanation, discriminating experiments, selective repair and operational use. Combines the earlier representation-expansion, falsification and invariant-constrained repair suggestions into one candidate. | Must genuinely require a goal-relevant model change; reject a disguised repeat of known-template fitting. Laws stay fixed. |
| 2 | Derive response families from primitive laws; share the resulting model across apparatuses | Adds theoretical deduction and cross-context consistency. Can supply the foundation and T1/T2 controls for candidate 1, or be a separate matched contrast. | Authenticity is more certain than increased difficulty. Derivation may collapse to a tiny fit. Qualify actual shortcuts and shared dependencies. |
| Supporting requirement | Exact identifiability, behavioral-equivalence handling and shortcut qualification | Makes candidates 1 and 2 interpretable. Global validity must constrain the player's solution, not just be automatic in the engine. | Cheap interpolation, fixed panels, blind construction, synchronization and independent subproblem solutions must be assessed. Keep valid shortcuts legal and label shallow episodes honestly. |
| Later diagnostic | Isolated in-NEXUS calculation/simulation access | Separates a wrong representation from difficulty executing the right one; useful if no-Python traces show arithmetic or bookkeeping bottlenecks. | Keep tool access a separate controlled factor; no private source/truth exposure. Benefits are not assumed uniform. |
| Defer | Noise, continuous calculus, unrestricted symbolic regression and larger polynomial families as difficulty drivers | Could eventually probe uncertainty or different mathematical skills. | Noise changes the qualification problem; unrestricted functions destroy finite-data uniqueness; larger fits may add computation instead of scientific reasoning. |

Use the pilot to revise this order:

- Supported success near ceiling with modest overhead strengthens the case for
  a representation/model-revision PoC rather than another size increase.
- Failures that persist with the true laws supplied point first to state tracking,
  control/planning or execution; do not label them discovery failures.
- A clear discovery-versus-known-law gap motivates diagnosing the current
  mechanism before adding another one.
- A shortcut, support-classification defect or insufficient control calls for
  qualification/diagnostic repair before collecting a more complex matrix.

If a new PoC is selected after review, begin with independent mathematical
conformance and exact qualification before production integration. Compare the
same worlds with a supplied response model, a principles-only model, and where
appropriate a provisional model needing revision. Hold resource and logistics
settings fixed, account for mechanical action overhead, and retain shallow
negative controls. Combine new mechanisms only after contrasts establish what
each contributes. Do not force an investigation order merely to manufacture depth.
