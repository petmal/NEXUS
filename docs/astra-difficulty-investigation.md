# NEXUS: Astra-targeted difficulty investigation

Research cutoff: 18 October 2026. This is an operator document, never player evidence.

**Recommendation:** first prototype history-dependent mechanisms with delayed
consequences, then combine them with experiments that must separate complete,
mutually incompatible models. Selective revision is a useful third dimension,
but only after a stronger proof than our previous unsuccessful revision PoC.
Do not treat extra gates, arithmetic, noise or shorter budgets as a demonstrated
Astra weakness. No defensible numerical Astra failure-rate forecast is available.

## What our own run establishes

Astra at medium reasoning passed all 13 cells; all wins were supported by the
observations under the exact public prior. Its 12 non-control runs used 9–12
readings and 28–37 actions, with one successful submission each. There were no
invalid actions, duplicate measurements, or measurements after the evidence first
established a guaranteed solution. This does not establish a general failure rate:
seeds were targeted, several cells share mechanisms, and there was one execution
per cell.

The two longest trajectories were seed 6943 (37 actions, 12 readings) and its
survey-indistinguishable rival 7051 (36 actions, 12 readings). These are useful
stress sentinels, not failures. Seed 3550 used only two survey readings plus seven
reference readings. Its combined-reader episode finished in 29 actions versus 31
for the calibrated version. Reference complexity can supply useful upstream
information rather than make inference harder.

The current family still has three small gates, exact scalar outputs, freely
settable contexts and trims, and a stationary mechanism. A complete program can
be inferred and then applied once to the seal. A fixed 15/16-reading panel solves
the calibrated/combined prior; a passive-only combined policy also exists. Thus
our present D5 label does not prove obligatory adaptive research or operational
repair. The data show Astra handling the current task well, not merely lucky
winning guesses. Terminal timeout fixes do not change this scientific conclusion.

Local evidence: `22-11-11.json` and `.log`; independent audit/oracle under
`analysis/transfer-2026-10-18` in the working workspace; committed qualification
and shortcut findings in `evidence-transfer-proof.json` and `transfer-performance.json`.

## Public evidence, with the relevant limits

| Source | What it actually supports | Consequence for NEXUS |
|---|---|---|
| OpenAI, [Astra launch/evaluation table](https://openai.com/index/gpt-6-astra/) | Reports ARC-AGI-3 99.9%, FrontierMath Tier 4 97.6%, but AutomationBench 41.4% and Terminal-Bench Science 64.6%. Scores are maximum over tested effort and depend on harness. | Abstract pattern discovery and more mathematics alone are weak bets. Operational work retains headroom, but aggregate scores do not identify a particular causal defect. |
| Chandra et al., [Hierarchical Experimentalist Agents v2](https://arxiv.org/abs/2606.29315v2), Fig. 5 / App. G.1 | On 50 held-out seeds, Astra ReAct achieves 92% on catapult and 56% on pass-the-parcel; learned skills raise these to 100% and 76%, using fewer turns. The often-quoted 0%/6% baseline has only one inspection and one committed action. | Strongest directly relevant evidence: reusable experimental strategies and coordinated multi-stage actions matter. Do not compare NEXUS's interactive Astra to the one-shot baseline or promise 44% failure in an alien symbolic world. |
| Zhang et al., [RoboDojo evaluation](https://arxiv.org/html/2609.24170v1), Tables 1–2, §4.4 | Astra-medium has 22.48% average success; precision and long-horizon axes are weaker than its semantic strengths. Authors explicitly cannot isolate perception, physical knowledge and action-interface effects. | Supports a bounded hypothesis about delayed consequences and preserving earlier work. It does not justify adding pixel alignment or tiny numeric tolerances to NEXUS. |
| MBaert, [randomized Boolean experiments](https://www.lesswrong.com/posts/PAHqDoFrp9fybcSn2/astra-appears-to-perform-belief-propagation-like-inference), 15 September | Author-run exploratory tests report more invalid assignments when competing joint solutions have similar probability. No-CoT/filler-token protocol; not peer reviewed. Internal belief-propagation claims remain speculative. | Test preservation of joint constraints, with ordinary reasoning enabled. Do not claim to know Astra's internal algorithm or transfer a no-CoT result directly to MindTrial. |
| [CausaLab](https://arxiv.org/abs/2605.26029) | GPT-5.2-high can predict accurately while recovering an incomplete mechanism; interventions and verification alter results. | Measure counterfactual/operational validity, not just one matching output. This is older-model evidence, not an Astra result. |
| [CausalGame](https://arxiv.org/abs/2607.04293) and [ACED-Bench](https://arxiv.org/html/2610.14381v1) | Interactive causal evaluation separates experiment selection, evidence use and commitment. ACED's four-turn budget is a major constraint; its listed models do not include Astra. | Use causal contrasts and exact trajectory diagnostics, but do not import their tight-budget difficulty as T/D difficulty. |
| [DeReLab](https://arxiv.org/html/2608.30413v1) | Older models often retain defeated beliefs; extended thinking greatly reduces one model's bias. Astra is not evaluated. | Revision is a hypothesis requiring testing under our normal reasoning setting; misleading prose alone is unlikely to be enough. |

These are primary evaluation reports or author-run experiments. Several are recent
preprints. None proves a NEXUS-specific Astra weakness. Robotics evidence has the
largest transfer uncertainty; the Boolean result has the weakest experimental
maturity. Unrelated projects named ASTRA/ASTRA-bench were excluded.

## High-value candidates

### 1. History-dependent mechanisms and delayed operational consequences — first PoC

**Plain example:** a specimen passes through the vek, nol and tor apparatuses.
Vek sets a hidden persistent latch. Nol changes the displayed property correctly
under either latch, so the intermediate result looks successful. Tor later uses
the latch and either preserves the earlier property or breaks it. The player must
identify the upstream cause, reproduce it on a fresh specimen, and repair the
whole chain while preserving already-correct properties.

**Why it may work:** Astra currently learns a stationary mapping and submits one
counterprogram. This adds causal credit assignment across time and composition
of experimental procedures, where HExA provides relevant model-specific evidence.
It also restores a meaningful distinction between identifying laws and producing
a valid terminal state. A large amount of static algebra need not be involved.

**Critical design:** persistent state must obey disclosed bounded transition
forms. Give reusable specimens, exact readings, a readable action history and
moderate budgets. Start with 2–3 state variables and 3–4 interacting stages.
Do not make hidden state arbitrary or repair impossible. D controls the number
of scientifically necessary dependencies (not merely the number of apparatuses);
T controls which transition laws are supplied,
parameterized or structurally unknown. P controls room logistics separately.

**Qualification:** exhibit histories with identical current readings but different
future responses; prove the history resolves that ambiguity. Show noncommuting
orders and a reachable exact goal. Compare against single-step fitting, latest-
observation-only policies, greedy local repair, all legal probes and failed-finish
feedback. Report a constructive policy and check whether fewer feedback rounds
still solve the prior. A long witness alone is not evidence of necessary depth. Include a known-law
control with the same physical execution: failure there is operational planning,
not evidence that unknown-theory inference became harder. Repeat qualification
with a generous allowance to expose depth produced only by a tight budget.

**Limits:** state tracking can become a small finite automaton Astra solves easily;
robotic failures may not transfer to exact symbolic observations. Expected added
challenge: high relative to current stationary transfer, confidence moderate.

### 2. Joint consistency across competing explanations — second PoC

**Plain example:** three apparatus calibrations remain plausible. Each dial's
most common value is zero, but the only jointly consistent assignments are
`(1,0,0)`, `(0,1,0)` and `(0,0,1)`. Combining the individually attractive values
produces `(0,0,0)`, which fits no possible world. A well-chosen cross-apparatus
experiment separates the alternatives before the model manufactures the seal.

**Why it may work:** this specifically probes whether the player keeps correlated
hypotheses intact instead of solving each component independently. It has a
small, exact failure signature and exploratory Astra-specific support. The current
posterior already represents joint worlds, but our pilot does not establish that
Astra faced a sustained, deceptive local-versus-global conflict.

**Critical design:** use 4–8 linked unknown relationships with looped constraints
and several locally consistent models. Keep arithmetic small. End in one concrete
joint artifact state, not a verbal explanation. Deterministic observations should
allow eventual evidence-supported success; do not require guessing between truly
indistinguishable worlds. The toy above proves only that marginal decisions can
be invalid; it is not itself a hard benchmark.

**Qualification:** measure surviving behavioral classes, near-rival separation,
and exact joint validity. Test independent-component solvers, greedy information
selection and available fixed panels. Accept equivalent complete solutions.
If an experiment or controller preview supplies the whole assignment at once,
reject the instance from the intended hard tier. Compare looped versus acyclic
mechanisms at matched variables, reading alphabets and resource allowance.

**Limits:** explicit hypothesis enumeration may solve it; some looped systems
remain algebraically trivial. Do not rely on denying reasoning or increasing
numbers. Expected added challenge: medium-to-high; confidence low-to-moderate.

### 3. Operationally consequential selective revision — gated follow-up

**Plain example:** a truthful archive describes the facility before a declared
phase shift. One apparatus now follows a different member of the disclosed law
family; two others remain unchanged. A specimen made earlier contains a persistent
state that depends on the old law. The player must determine what changed,
retain valid relationships, and repair that actual specimen using the new law.
Relearning only the new static input/output map is insufficient.

**Why it may work:** it combines belief revision with its operational consequences.
This is closer to maintaining a scientific model than saying that an old note is
wrong. It addresses the exact bypass in our earlier revision PoC, where immediate
transition and at most three new-context readings solved the task.

**Qualification:** prove both retained and revised knowledge are needed for the
mission; explicitly try immediate transition, discarding the archive, relearning
only the final regime, fresh-specimen replacement, and brute-force repair.
A public change schedule must not leak the changed gate. Preserve finite prior,
reproducible transitions and fair recovery. Pair stable/changed worlds and test
both directions of change. Keep the existing family unchanged.

**Limits:** making history indispensable by confiscating all samples is R pressure,
not a good revision guarantee. A complete new-regime readout again creates the
old shortcut. Evidence for Astra-specific revision weakness is presently weak.
Expected challenge: medium alone, potentially high with candidate 1.

### 4. Interventions that expose otherwise indistinguishable mechanisms — enabling constraint

Construct two models with identical passive observations but different effects
under a legal internal clamp. The player must decide what to intervene on, and
use that distinction in the final transformation. Calibrate the reader through
an independent channel that does not reveal the hidden internal node as a side
effect. Explain every legal clamp and bounded prior in the actual player files.

This closes a demonstrated NEXUS design gap: combined reference observations can
make passive experiments sufficient. It overlaps earlier causal families, so it
is an ingredient in candidates 1–2 rather than a claim of wholly new coverage.
Ablate clamps and calibration separately, quantify behavioral ambiguity, and
require that the correct operational result differs between rival models.
Expected gain alone is uncertain: Astra may immediately choose the right clamp.

## What to build, and what to avoid

Prefer one versioned plugin prototype combining **1 + 2**, with **4** as an
admission criterion. Add **3** only after the history/shortcut proof succeeds.
Keep existing versions and moderate P/R. First implement a small independent
finite oracle and adversarial shortcut baselines, then the canonical runtime.
Reuse bitset posteriors and verified offline tables where bounded; factor the
state transition model instead of precomputing every possible transcript. Admit
only configurations within explicit world/state/memory limits.

Do not prioritize extra nomenclature, huge hypothesis lists, tiny tolerances,
random unbounded noise, hidden rules, repeated room travel, misleading instructions,
or arbitrary budget cuts. More noise can make the mission unknowable; more
turns can test context retention rather than the intended scientific dependency.
Longer histories alone are also a weak Astra target given its strong public
long-context results.

A fair PoC keeps ordinary reasoning enabled and allows existing NEXUS tools.
Use exact oracle outcomes, not a judge's impression of a convincing narrative.
Log decision support, joint contradiction, necessary contrast acquisition,
history-state mistakes, revision scope and actual repair success separately.
No chain-of-thought disclosure is required. Test generous-budget controls and
fresh held-out mechanisms before claiming the candidate topples Astra.

## Compatibility with the current plugin architecture

The versioned ontology registry and `ScientificRuntime` adapter can host these
families while keeping previous episodes unchanged. Typed specimen schemas,
`transform`, `assess_mission`, public evidence, posterior inference and public
policy witnesses belong in the new plugin. The core continues to own action
charging, transactions, receipts and replay.

There is one important boundary: current observations serialize domain artifact
payloads. **Do not put a hidden latch directly into that payload.** For the first
PoC, store a bounded, publicly determined preparation/action history plus cached
readings; recompute the latent state from that history and the immutable private
law inside `transform`. This keeps hidden truth out of observations and canonical
public-state hashes. It is cheap at the proposed depth. Private mutable latent
state would instead need an explicit, audited projection/replay extension.

Likewise, the current transform hook receives one artifact rather than arbitrary
world state. Start with interactions between stages of the same specimen.
Cross-specimen operations would need a deliberate adapter capability, not hidden
side effects. A simultaneous multi-property goal fits `assess_mission`; its
terminal inference tracker must follow the new operational semantics. New
hypothesis/state caps must be proved, not inherited from transfer's 15,552-world
cap. No new runtime mechanics are included in this timeout-fix patch.

## Ten-execution diagnostic available now

`astra-diagnostic-matrix.json` uses existing families only. It does not pretend the
proposed mechanics are already implemented. Every row is preflighted; player
prompts contain no seeds, rivals, proofs or solution hints.

| Row | Private seed | Condition | Actions | Main comparison |
|---|---:|---|---:|---|
| 01 | 3550 | T0/D0 combined execution control | 11 | Receipt/transport sanity |
| 02 | 6943 | T3/D5 calibrated | 39 | Physical inference without mixed reader |
| 03 | 6943 | T3/D5 combined | 43 | Repeat pilot's longest Astra trajectory |
| 04 | 6943 | Combined, +6 diagnostic allowance | 49 | Resource sensitivity |
| 05 | 6943 | Independent repeat of 03 | 43 | Within-seed variation |
| 06 | 7051 | T3/D5 calibrated | 39 | Paired physical rival |
| 07 | 7051 | T3/D5 combined | 43 | Repeat second-longest trajectory |
| 08 | 7051 | Combined, +6 diagnostic allowance | 49 | Resource sensitivity |
| 09 | 7051 | Independent repeat of 07 | 43 | Within-seed variation |
| 10 | 9631 | New T3/D5 combined mechanism | 43 | Held-out mechanism, both contexts needed |

All P1/R1; +6 rows retain the same laws/evidence. The calibrated/combined pair
uses each family's normal R1 budget (39 versus 43), so it is not a pure
fixed-action-count ablation. Compare reading counts, information gained and
supportedness alongside wins. Existing evidence suggests most or all Astra runs
may still pass. A failure on one repeat is a reason to gather more repeats, not
proof of a stable weakness. Ten executions are diagnostic, not a leaderboard.

Use Astra-medium by default, no Python, fresh model context and fresh service for
each task. An optional disabled Astra-high run is provided for follow-up; enabling
it doubles the matrix. Other providers are retained but disabled in this separate
configuration. Preserve attempts separately when infrastructure causes retries.

Collect actual finish outcome/receipt, first guaranteed-solution turn, last
submitted program support, remaining behavior classes, survey/reference use,
contexts/interventions, repeated readings, actions after sufficient evidence,
output-limit/refusal status, and terminal compile/response latency. If the paired
combined version is easier, improve information-channel design before adding
more nominal D. If extra budget rescues failures, classify that component as
resource pressure. If all repeats pass, stop farming the same family and move to
the proved history-dependent PoC.
