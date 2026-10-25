# What NEXUS learned about T/D difficulty

Evidence through the 40-execution screen assessed on 24 October 2026. This is an
operator research summary, not material to give to a model playing an episode.

## Main conclusion

NEXUS has not yet demonstrated a reliable way to make the strongest tested model
fail through theory and discovery difficulty alone. It has demonstrated something
useful: a range of artificial worlds in which we can check exactly what a model
did, whether it won, what its observations justified, and where a failure occurred.

The progression matters. Early failures often mixed inference with navigation and
tight budgets. Later worlds removed those confounds, but models usually solved
them. More complicated mechanisms often increased work without reducing success.
Some proposed deeper tasks also had legal shallow solutions. Model revision
produced particularly useful evidence-use failures, but the latest controlled
screen ended with **40 genuine, receipt-accepted wins in 40 executions**. Only
**28 first submissions** and **34 final submissions** were justified by all the
evidence available before submission.

The recommended next step is to shift the main effort toward **depth, breadth and
coordination of meaningful tasks**, using model revision, compositional repair
and stateful discovery as complementary bases. Keep a small, hypothesis-driven
T/D track. Do not spend another broad sweep on a larger version of the same finite
grammar without a new reason to expect a useful contrast.

This is a conclusion about the tested designs and model settings. It is neither
a proof that intrinsic T/D difficulty is impossible nor a general ranking of models.

## What the axes and measurements mean

NEXUS generates small, deterministic worlds with unfamiliar rules. The player
receives public instructions and evidence, performs experiments, and takes actions
to satisfy an exact goal. The engine, rather than another language model, decides
success. A successful finish produces a verifiable receipt. The world can be
replayed from its action trace.

In the current axes-v2 design:

| Control | Intended meaning | Important limit |
|---|---|---|
| **T: theory sufficiency** | How much of the rule is supplied: a resolved model, known laws, unknown correction parameters, or unknown structure within a bounded grammar. | T labels are not a universal scale of cognitive difficulty. |
| **D: investigation structure** | How the missing information must be obtained: supplied evidence, direct measurement, separating effects, dependent experiments, or constructing informative contexts. | A deep-looking mission may still have a shallow identification strategy. |
| **P: planning/logistics** | Movement, preparation, delivery and coordination. | P0 removes travel, not necessarily scientific preparation. |
| **R: resources** | Limits on actions, stock and equipment use. | R0 still has external tool, output and time limits. |

Legacy axes used different meanings, including for T0. Always record the family,
axis version and actual settings. A seed identifies a world only together with
those settings and source version; revision seed 438 and repair seed 438 are not
the same world.

Three distinctions are essential to interpreting the experiments:

1. **A win is not the same as a supported decision.** A supported build works in
   every world still consistent with the public evidence. A compatible build works
   in some of them. A contradicted build works in none. A compatible build can win
   legitimately. The diagnostic says the evidence did not guarantee it, not that
   the player cheated or necessarily guessed randomly.
2. **More hypotheses do not necessarily mean more relevant uncertainty.** Different
   programs can behave identically. Different mechanisms can also allow the same
   repair. Count distinguishable behavior and valid decisions, not just program text.
3. **A feasible solution is not a difficulty lower bound.** A public-information
   reference policy proves that a task can be solved. Its cost is an upper bound
   unless optimality is proved separately. An omniscient shortest plan, an
   evidence certificate chosen with hindsight, and an adaptive public policy are
   different objects. Models can legitimately beat a reference trajectory.

An evidence certificate is a set of observations sufficient to justify a decision
for a particular world. Finding that set with knowledge of the answer can be much
easier than deciding which experiment to run next. Likewise, a lower bound of four
readings says nothing by itself about how hard their interpretation is for an LLM.

## Experimental progression

The studies below are ordered by the design question they addressed. Counts come
from the recorded audits listed in [Sources and scope](#sources-and-scope). They
must not be added into one pass rate: cohorts overlap, some rows are selected
successful subsets, and tools, budgets, prompts and model settings changed.

### 1. Transformation facilities: inference mixed with execution

The original facility asked players to transform artifacts with unfamiliar
machines and deliver them through a map. The initial 80-task audit found 72 live
wins, five real losses and three provider-aborted tasks. Eight live wins were
reported as parser errors. All five real losses occurred at D5/P3/R2; four had
completed the causal transformation but failed the remaining logistics. [H1]

The T-axis implementations then tested three kinds of missing theory:

- **T1:** a structural law grammar with 41,472 syntactic candidates and 27,120
  behavior classes in the full prior.
- **T2:** a supplied correction form with nine possible laws, five viable under
  the public solvability promise. One relevant probe could settle the decision.
- **T3:** six independent rule cells, giving 729 nominal laws. For the reachable
  mission, these reduced to nine behaviors, five physically viable. Again, the
  apparently large prior overstated mission uncertainty.

Local qualification exercised 116 T1 generation cases, accepted 113, and replayed
865 policy paths. A further D4 pass accepted 22 of 24 cases and replayed 83 paths;
T1/D5 remained outside the supported grammar. T2 qualification covered 21
generation cases and 105 paths. The T3 check used 675 full-law replays. These were
engineering and solvability checks, not LLM trials. A bounded-search rejection
also did not necessarily prove mathematical impossibility. [Q1]

The live T2 matrix won 43/70 games, with 42 official passes. All 14 T2/R2 attempts
became physically unwinnable during exploration before the first experiment.
The qualifier knew the map; the player did not. Of 25 T2 losses, 15 ended with
the correct transformed value but incomplete delivery. There were genuine
evidence-use mistakes too, including committing a transformation after its probe
had already shown the wrong output. The aggregate loss rate did not isolate T. [H2]

A later, more forgiving T1/T2/T3 matrix produced 70/70 live wins and 68 official
passes. Of 84 machine operations, 79 had an exact-context preview. Probing the
very transformation needed for the mission was legal and often removed the need
to infer a transferable law. This was successful use of the interface, not an
exploit. It weakened the intended interpretation of success as theory discovery.
The changed matrices prevent treating 43→70 wins as a controlled resource effect. [H3]

A separate cumulative-progression proof of concept made two observations jointly
necessary for a held-out prediction, across 20 truths and five fixtures; an
independent review checked 1,000 seeds. Either observation alone was ambiguous.
However, directly probing the target was a one-observation bypass if allowed.
The PoC established an information dependency under its restricted interface,
not a production challenge or measured model failure. [Q2]

### 2. Response laws, networks and treatment history

**Shared response** replaced direct mission previews with calibration and
prediction from a common response law. Across 103 completed games, every first
submission won. External Python was available in this cohort, so it is not
directly comparable with later no-Python studies. **Coupled-network** and
**resonant-network** variants added upstream preparation and downstream tuning.
They established useful compositional mechanics, but the available reports do
not establish a separate failure-inducing gradient for either family. The causal
pilot below included 12 successful resonant tasks and two errors. [H4,H5,H7]

**Causal mechanisms** added hidden state, routing and treatment order. The initial
77-task study had 67 passes, one failure and nine errors; all 20 playable hard
causal cases won. Unfortunately, all three selected hard truths reduced to
additive updates: they did not actually require reasoning about treatment order.
One Sonnet win still had two possible mission answers. A DeepSeek run had enough
evidence at action 42, but spent another 49 actions without completing the mission
and hit the external 96-call limit. That was a stopping/completion failure, not
failure to identify the required answer. [H5]

The follow-up deliberately selected order-sensitive worlds. It produced 69 wins
and one output-limit error, including **35/35 hard wins without external Python**.
All wins were evidence-supported. In 29 of those 35 hard runs, the answer was
settled without measuring a two-pulse experiment. Exhaustive analysis over all
648 worlds found that the complete set of untreated and single-pulse observations
always determined the mission answer. This proves shallow observational
sufficiency; it does not prove that collecting the whole set is cheap. [H6]

The lesson was precise: asking for predictions after several steps does not
force several levels of experimental discovery. Once the simple update rule is
known, a long history may be easy to calculate.

### 3. Repair: from prediction to an actual intervention

**Coupled repair** required a physical repair, with potentially several acceptable
repairs per mechanism. Its tightly specified T3/D5/P0-or-P1/R1 profiles have a
checked bound: any policy using at most two feedback rounds succeeds on at most
3/7 of the declared conditional uniform prior. A three-round public policy wins.
One extra action removes that two-round ceiling. This is a real structural result,
but it depends on the exact budget and prior. It is not a prediction that an LLM
will fail at the full allowed task. [Q3]

**Coupled dynamics** added history-sensitive transitions and responses. Its
70-session mixed repair/control/dynamics matrix produced 70 live wins and 69
receipt passes. All 42 dynamics investigations won; 40 won on the first submission,
and all had identified the world before their first finish. Median actions ranged
from Astra's 29 to DeepSeek's 67.5 under a 73-action allowance. Effort separated
models more than eventual success did. [H8]

**Compositional repair** was a stronger intervention test. Some mechanisms agree
under every passive observation but require different interventions to distinguish
them. A joint repair must work across two contexts. Complete mechanism identification
is still unnecessary when several surviving mechanisms accept the same repair.

The eight-cell, seven-model pilot had 56 tasks: 45 live wins, with official results
44 Passed / 5 Failed / 7 Error. In the four hard cells, 19/28 games won and 18
passed receipt validation. Four games exhausted their action budget; five ended
in incomplete model stops, including four length stops and one refusal. Astra and
Qwen won all eight cells. This was meaningful separation, but not pure T/D
failure: hard winners had median slack of only two actions and five of 19 used
their last action to win. [H9]

A Gemini budget diagnostic confirmed the resource interaction. On repair seed
438, wins changed from 0/3 at 30 actions to 3/3 at 36. On seed 493, the two played
30-action attempts and all three 36-action attempts won; a third 30-action task
ended in a provider error before play. This small diagnostic does not estimate a
general six-action treatment effect. It does show why these losses must not all
be attributed to intrinsic theory difficulty. [H10]

### 4. Richer readers, histories, assemblies and memory

Several subsequent families tested whether coupling more unknowns would remove
the remaining easy strategies. Their value was often in new controllable mechanics
rather than lower success rates.

| Family | What changed | Observed result and interpretation |
|---|---|---|
| **Coupled transfer / coupled evidence** | Build a program matching complete behavior; in the combined version, also infer an upstream reader. | Astra's 13 initial cells all produced supported wins. A fixed 15/16-reading panel solved the calibrated/combined prior, and a passive-only combined policy existed. An extra unknown reader could also expose useful information. More unknowns were not uniformly harder. [H11] |
| **History-coupled** | Make outcomes depend on prior preparation and actions. | 20/20 live wins, 19 supported; all 18 history-family wins were supported. Later qualification found finish/omission shortcuts that undermined the claimed deeper tier. [H12,H13] |
| **Staged repair** | Diagnose and repair three seals, with independent or dependent experiment contexts. | A selected diagnostic subset of eight rows × two models contained 16 successes, median 19 actions versus reference 19–20. This is not a complete-matrix pass rate. [H13] |
| **Joint assembly** | Infer a confounded reader/law and assemble components whose local validity does not guarantee joint compatibility. | The selected unknown-reader T3 cells contained 22 completed successes across six models, median 21 actions versus reference 20–22. Useful physical compatibility constraints; no demonstrated deep failure boundary. [H13] |
| **Representation discovery** | Infer predictive memory within a finite supplied representation family. | The ordinary T3/R1 subset contained 14 wins across seven models, median 24.5 actions versus reference 14. Astra used 16 and 20. Extra work did not establish new representation learning outside the supplied family. [H13] |
| **Uncertainty construction** | Build under hidden higher-order dependence and nuisance channels. | The selected T3/R1 subset had 13 wins and one mission failure. The failed Grok run had a correct candidate but did not install and finish it. [H13] |
| **Coupled memory** | Infer interacting transfer, hidden memory and encoding; match every future history. | Of 30 tasks, 26 completed and all won on supported first submissions. Official accounting was 23 passes, three post-win receipt failures and four provider errors. The latent structure still consisted of eight choices in a known binary feature family. [H14] |
| **Stateful discovery** | Experiment on the actual goal object and bring four coupled hidden registers to one joint target. | Of 40 tasks, 38 completed and all won on supported first finishes. Official accounting was 35 passes, three post-win answer failures and two provider errors. Normal R1 challenge completions used 21–40 of 64 actions. [H15] |

Stateful discovery deserves a careful interpretation. Investigations really do
change the object that must later satisfy the goal. That makes it useful for
planning and preserving earlier work. But the representation and update equation
are supplied, with eight binary unknown choices. Repeating a mode five times
provides a modular reset shortcut. The results therefore do not establish that
players faced a difficult general problem of learning while controlling an
irreversible system.

The action-overhead audit also examined 51 successful transfer-family traces.
That is a success-selected sample, not 51 wins out of all scheduled tasks. The
same restriction applies to the staged and assembly subsets above. They support
claims about costs and strategies among completions, not a complete reliability
estimate. [H13]

A categorical permutation-chain PoC checked 36- and 216-world families, with
four/six-reading policies and ten/fourteen-action completions. Only six target
classes remained relevant. It demonstrated an extension path, not a calibrated
new source of model difficulty. [Q4]

### 5. Model revision: reconstructing a mechanism from primitives

This family supplies exact elementary transfer rules rather than a menu of
complete mechanism formulas. Four reservoirs hold five packets. A directed link
transfers `min(source, 1 + destination % 2)` packets. Each of two modes executes
two hidden links in order. The display reveals only the first reservoir modulo
three. The player gets two trusted one-mode observations and can query sequences
of one to eight modes on a freshly initialized reference device.

The mission is to install a program whose displayed behavior matches the reference
for **every finite history**, not just the observations already made. Equivalent
wirings are accepted. There are 20,736 programs but only 748 distinct behaviors.
Some conditions supply a provisional program consistent with the initial archive;
the player may revise or ignore it. Conservation is built into the primitives,
so the task does not test discovery of conservation itself. [Q5]

The first 30-task pilot produced 28 wins, one genuine reconstruction failure and
one output-limit interruption. Of the wins, 25 were supported and three remained
compatible with unresolved alternatives. Astra won all ten cells. Seven challenge
cells represented four distinct worlds, not seven independent mechanisms. [H16]

The important failure was Gemini on revision seed 1101: sufficient evidence was
available by action 34, yet it continued reading and submitted several programs
contradicted by that evidence until the 64-action budget expired. A seven-task
rerun produced six wins, four supported and two compatible. Gemini again failed
1101 after enough evidence was available by action 32. The prior Sonnet shortcut
interruption did not recur. These are repeatable examples in a small cohort of
failure to turn evidence into a consistent construction; they are not yet a
stable population failure rate. [H17]

### 6. The bounded T/D screen and latest live evaluation

The next screen separated two structural quantities:

- **C:** the smallest number of additional observations that can justify the
  correct behavior for a particular world, given the archive. This is an
  optimistic certificate size, not an adaptive-policy bound.
- **L\*:** the smallest maximum query length for which the complete set of
  observations identifies the actual behavior among all archive survivors.
  A rival pair that agrees on every shorter word can witness a lower bound on
  L\*. This is distinct from the shortest query separating an arbitrary pair,
  and a large L\* does not imply that many experiments are needed.

The panel included archive-matched triples agreeing on all words of length at
most three, pairs agreeing through length five, and shallow/known-construction
controls. Two C=4/L*=5 worlds had only three or four reachable states and were
explicitly outside the earlier hard-tier state threshold. In the tested grammar,
no C≥4/L*=6 world was found. All behavior pairs separate by length six, and a greedy
public policy requires at most nine readings from the full prior, or seven after
the archive. These are bounded results for this grammar. [Q6]

Restricting query length can change the certificate itself: one world has C=4
but needs five observations when queries are limited to length three. Thus C,
query depth, reachable-state count and action cost must remain separate measures.
A C4 lower bound yielded a minimum of 12 supported actions in the relevant
protocol, versus reference trajectories of 14–18; it was not a cognitive bound.

The resulting live screen had the following outcomes. Each row counts executions,
not independent sampled worlds. “Supported” is assessed immediately before the
submission and includes public failed-finish feedback where available. [H18]

| Condition | Executions | Correct first submission | Supported first submission | Supported final submission | Live wins and accepted receipts |
|---|---:|---:|---:|---:|---:|
| Astra, recoverable baseline | 24 | 16 | 13 | 18 | 24 |
| Astra, single-shot finish | 10 | 10 | 10 | 10 | 10 |
| Gemini, fresh baseline | 2 | 2 | 2 | 2 | 2 |
| Gemini, consistency prompt | 2 | 2 | 2 | 2 | 2 |
| Gemini, reading-consistency checker | 2 | 1 | 1 | 2 | 2 |
| **Total** | **40** | **31** | **28** | **34** | **40** |

The audit checked 367 readings, 49 checker calls and 54 submissions. A separate
implementation reproduced all 20,736 programs and 748 behavior classes and agreed
with every checked reading, submission and witness. All runs recorded the same
source hash. There were no logged retries, invalid actions or provider warnings;
unobserved SDK retries and immutable model versions remain unknown. [H18]

The matched five-world Astra subset is especially informative. Recoverable play
had 4/10 correct first submissions and 3/10 supported first submissions; single-shot
play had 10/10 for both, with all 20 eventual wins. Mean readings rose from 7.7 to
9.3, while mean actions were almost unchanged, 22.4 to 22.6. Single-shot play
appears to have encouraged more careful commitment. It did not make the mechanism
intrinsically harder. Runs were blocked at different times and used different
evaluation seeds, so this is suggestive policy adaptation, not a clean population
causal estimate.

Four contradicted Astra submissions repeated an already rejected **behavior**
under different literal wiring. The literal-repeat counter correctly reported
zero; it could not express this distinction. Six final wins still left two to
four possible behaviors. Rejected finishes supplied the first sufficient evidence
in four runs. Success alone conceals both of these evidence-use patterns.

The new Gemini baseline won both 1101 trials. The earlier two failures remain real,
but they did not reproduce here. The prompt and checker arms each have only two
runs and cannot establish a reliable intervention effect. In particular, the
checker tests consistency with readings, not full correctness or previous rejected
finishes; it allowed one consistent but wrong construction, exactly as specified.

### 7. Bounded local prototypes: useful negative results

Two additional designs were tested locally before committing to another live
integration. Neither result is a model evaluation. [Q6]

**Selective control after a law change (W4).** Starting from the revision mechanism,
the prototype considered 45 possible unchanged/one-link-changed laws and all ten
old reachable physical states. No different exact target state was reachable
under every allowed changed law, even for a controller that knew the law. A
focused display-goal redesign also failed. This candidate is physically
unsolvable under its stated requirements; it cannot provide a fair reasoning test.
The result does not rule out other change sets, initial states or goal definitions.

**Two-module cascade (NW2).** The prototype connected upstream and downstream
revision mechanisms, with at most one faulty module and 89 possible joint worlds.
With only downstream observations, an all-history indistinguishable class of 35
worlds contained incompatible repairs. Therefore no amount of observation before
repair could guarantee the right repair in that protocol.

Adding diagnostic taps or clamps made the bounded specification identifiable.
The tested greedy policies needed at most six readings when modules were isolated
and four with combined assistance; these are upper bounds. Although 87 worlds
had a one-reading certificate and two had a two-reading certificate, that does
not establish a two-reading adaptive strategy. The largest reachable joint machine
had 59 states. Exact joint correlations mattered: one observation left 74 actual
joint worlds, whereas multiplying separate module possibilities would invent
1,394 combinations.

The assisted cascade is a promising composition specification and positive
control, **not a playable production family or an empirically harder task**.
Tentative repair followed by observation and rollback could change the
downstream-only result, but that would be a new protocol needing qualification.

## What follows from the combined evidence

**The T/D effort found useful dimensions, but no dependable strongest-model failure
boundary.** It raised experimental work, exposed unsupported commitments and
stopping failures, and clarified the difference between a long mission and a
deep identification problem. It did not justify claiming that every more elaborate
ontology is harder than its predecessor.

**Finite, exact worlds are a strength, not a defect to hide.** Exact inference lets
us distinguish inadequate evidence, misused evidence, a valid alternative repair,
an execution failure and a harness problem. Finite enumeration is a legitimate
player strategy if the interface permits it. The goal is a meaningful challenge,
not to disqualify a correct strategy because it differs from the designer's intent.

**Budget pressure can be useful when named honestly.** The repair and early
navigation results show real planning and efficiency differences. They support
resource experiments, but cannot establish pure theory difficulty. Larger budgets
can also trigger over-investigation, so “more budget” is not automatically easier
behaviorally even when it expands the set of feasible policies.

**Avoid claiming an internal reasoning mechanism from a trace.** A contradicted
submission establishes inconsistency with available evidence. It does not reveal
whether the cause was arithmetic, memory, representation, anchoring or strategic
risk-taking. Small paired ablations can test those explanations more usefully than
another broad architecture expansion.

**The remaining uncertainty is empirical as well as architectural.** Selected
seeds, repeated worlds, small arms, unequal model settings and changing harnesses
limit generalization. New dimensions should first produce a measurable within-world
gradient, then be confirmed on held-out mechanisms and repeated runs. Do not
erase prior failures when a rerun wins, or call provider errors scientific failures.

## Bases for the next phase

Use three primary bases, each for a distinct reason. This is a development
priority, not removal of older families or a claim of empirically proven superiority
on axes that have not yet been tested.

| Base | Best next uses | Why this one | Why not use another family instead? |
|---|---|---|---|
| **`model-revision-v1`** | Multiple interacting investigations, transferring findings between modules, revising constructions, commitment and consistency. | Exact primitives, all-history acceptance, accepted equivalent programs, certificate/query-depth controls, public-evidence witnesses and observed evidence-use mistakes. It is compact enough to audit exhaustively. | Earlier prediction families often reduce to fitting a small formula or directly previewing the mission. Coupled memory supplies more of the representation. Revision offers a cleaner construction unit, though its current single-module success is near ceiling. |
| **`compositional-repair-v1`** | Coordinating interventions across contexts, competing repair choices, breadth of joint constraints, resource allocation. | Passive-equivalent alternatives make intervention genuinely relevant; overlapping valid repairs test decision-making rather than unnecessary full identification. It has real pilot separation and a budget diagnostic. | Coupled repair's strongest bound depends on a narrow budget. Coupled dynamics and staged repair increased work but did not provide equally clear intervention separation in the available evidence. Use generous budgets initially to avoid importing the old 30-action confound. |
| **`stateful-discovery-v1`** | Longer plans, preserving earlier achievements, shared consumables/state, ordering and recovery. | Investigation changes the actual goal object, with exact replayable joint-state goals. This gives a concrete base for depth and coordination. | Most transfer/memory families permit fresh or reset experiments followed by a final installation. They are useful inference controls but less direct bases for persistent-state planning. Audit the five-step reset before attributing future difficulty to irreversibility. |

Retain **coupled memory** as an all-history, known-representation comparison and
**coupled dynamics/shared response** as simpler calibration and execution controls.
Retain **joint assembly** for experiments specifically about component compatibility;
it need not become a fourth general research track yet. Staged repair and history
families remain regression fixtures and sources of mechanics, with their shortcut
limits recorded. Preserve legacy families for reproducibility, not as the main
route to isolated T/D difficulty.

Use the **assisted cascade specification** as the first bounded composition
candidate if a new multi-module experiment is needed. It already has a solvability
argument and a useful joint-correlation test. Do not promote W4 or downstream-only
NW2 as currently defined: their failures concern task validity. Do not select a
family merely because it has more latent states, a larger nominal prior or a lower
unadjusted pass rate.

## Recommended experiment sequence

1. **Freeze this T/D checkpoint.** Preserve the old matrices, source/image identity,
   raw outcomes and interpretation. Treat current screen exports as tied to their
   original source. A refactor changes the source hash and requires a fresh preflight
   before another live run; it does not invalidate the historical result.
2. **Establish small controls on the chosen bases.** Use a known-law execution
   control and a generously budgeted unknown-law condition on the same physical
   task. Keep public information, reset rules and tool availability explicit.
3. **Vary breadth and depth separately.** Breadth can mean more modules or joint
   constraints; depth can mean more dependent stages whose outputs affect later
   choices. Include an independent-task version at the same module count. This
   distinguishes added volume from interactions. Do not equate a longer text or
   more repeated arithmetic with a deeper challenge.
4. **Qualify the joint task before a model pilot.** Check reachable goals, all legal
   observations and recoveries, valid alternative solutions, public-information
   solvability and action costs. Keep correlations between modules. Isolated
   solvability does not imply that their combination is solvable or identifiable.
5. **Run a small matched pilot and then a holdout.** Record first and final actual
   success, support, contradicted decisions, first sufficient-evidence point,
   post-support actions, behavioral repeats, receipt reliability and provider stops.
   Record actions, readings, calls, tokens and time separately. Randomize/interleave
   conditions where practical and reserve new mechanisms for confirmation.
6. **Expand only after a useful contrast.** A useful contrast may be a repeatable
   accuracy difference, supportedness difference or resource-efficiency gradient;
   it need not be universal failure. Retain only a bounded T/D follow-up that tests
   a specific explanation, such as consistency assistance on held-out failing
   constructions. The two-run Gemini arms do not justify a broad assistance claim.

The [future-experiment guide](future-experiments.md) translates these choices into
repository boundaries and qualification steps. NEXUS's repeatability, auditability
and customization should remain acceptance criteria throughout this next phase.

## Sources and scope

Historical counts above are transcribed from the supplied audits, not newly
replayed against today's code. The latest 40-run audit includes independent
arithmetic and behavior checks. Some earlier full raw matrices are not present
in this checkout; selected-subset results are labelled accordingly. No missing
cohort has been assigned a guessed pass rate. References to other research in
historical reports are not used as evidence for the NEXUS conclusions here.

The machine-readable [source manifest](research/td-source-manifest.json) records
report filenames, retrieval identifiers and checksums of the available snapshots.
The latest [evaluation assessment](research/td-evaluation-assessment-2026-10-24.md)
and [40-run ledger](research/td-latest-run-ledger.json) are committed alongside this
summary. The ledger is an audit derivative, not a replacement for raw transcripts.

| ID | Source report or repository record |
|---|---|
| H1 | `NEXUS-test-matrix-audit-2026-10-07.md`, run `09-55-47` |
| H2 | `nexus-13-26-53-review.md` |
| H3 | `nexus-17-09-01-review.md` |
| H4 | `NEXUS-12-05-35-analysis.md` |
| H5 | `nexus-11-50-21-analysis.md` |
| H6 | `nexus-21-29-08-analysis.md` |
| H7 | `nexus-architecture-and-findings-2026-10-13.md` |
| H8 | `NEXUS-run-13-22-12-analysis.md` |
| H9 | `NEXUS-23-00-26-pilot-analysis.md` |
| H10 | `NEXUS-30-action-budget-analysis-2026-10-17.md` |
| H11 | `nexus-astra-investigation.md`, version 2, initial run `22-11-11` |
| H12 | `nexus-history-run-17-50-17-analysis.ipynb` |
| H13 | `NEXUS-action-overhead-and-state-changing-experiments.md` |
| H14 | `nexus-coupled-memory-results-2026-10-21.md`, run `12-21-57` |
| H15 | `NEXUS-stateful-pilot-2026-10-22.md`, run `11-33-16` |
| H16 | `NEXUS-model-revision-pilot-analysis.md`, run `18-38-10` |
| H17 | `NEXUS-rerun-analysis-2026-10-23.md` |
| H18 | [Latest evaluation assessment](research/td-evaluation-assessment-2026-10-24.md), runs `22-49-40`, `10-44-05`, `11-51-35`, `12-24-44`, `12-54-08` |
| Q1 | [T1 implementation](theory-implementation-results.md), [next pass](theory-next-pass-results.md); T2/T3 implementation records in this repository |
| Q2 | Cumulative theory-progression PoC and its independent review, summarized in H7 |
| Q3 | [Repair results](repair-results.md), [live conformance](repair-live-conformance.md) |
| Q4 | Categorical permutation-chain PoC, summarized in the 22 October self-contained briefing; source manifest includes the briefing |
| Q5 | [Model revision guide](model-revision-guide.md) and family inference/qualification code |
| Q6 | [Bounded cycle results](td-cycle-results.md), [implementation and commands](td-cycle-implementation.md) |

Design-review synthesis and the 23 October roadmap inform the investment choices;
they are interpretations, not additional model trials. The source manifest records
those documents too. Plans discussed in reviews but never implemented or evaluated
are not counted as experiments.
