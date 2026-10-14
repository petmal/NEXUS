# NEXUS: qualified deep investigation and operational repair

Implementation plan • revised 14 October 2026 • Status: reviewed design and small counterexample proofs; live deep-family feasibility unproved; production implementation not started.

Scope clarification: the setting, storyline, nomenclature and plot apply across the entire current NEXUS version, including every supported ontology. Only the new coupled-repair mechanics are opt-in.

Sanity-check revision: qualification is strengthened below with explicit feedback-round and bounded-success gates, higher-order repair obstructions, complete protocol observations and weighted public priors. The earlier three-reading/preparation targets alone were insufficient. No production ontology has yet passed the strengthened deep-profile gate.

Robustness revision: require a winning policy within the advertised round count; define an executable batch language; qualify each exposed configuration under its actual conditional sampler; make recovery a public-information policy; and require checkable proof payloads rather than trusting digests or search-completion flags. These are soundness fixes, not new difficulty thresholds. Prior/resource sensitivity is reported separately and never assumed.

## Decision

Establish a **shared alien-facility setting and presentation layer across current NEXUS**, then add a new, opt-in ontology around **coupled diagnosis and repair**, supported by a stronger qualification system. Add a bounded, specimen-local regime-change variant after the stationary family passes qualification. Preserve existing ontology mechanics, axis meanings, machine-readable action contracts and historical replay behavior. New presentation text is a deliberate, versioned change across supported families.

The central change is to make difficulty an **auditable property of the complete interaction problem**, rather than an assumption inferred from a complicated formula or dependency graph. Generation must establish both that a public-information policy can win and that cheaper/shallow alternatives fail the particular guarantee being claimed. A successful shortcut remains a valid win; it either belongs in a lower profile or invalidates an overstated certificate.

This plan does not promise that half the models will fail. It makes that hypothesis testable while addressing the shortcut problem before spending on model evaluations.

## 1. Integration baseline and scope

| Item | Verified baseline |
|---|---|
| Repository | `petmal/NEXUS` |
| Feature branch | `feat/theory-prior-axis` |
| Open integration PR | [#6](https://github.com/petmal/NEXUS/pull/6) |
| Remote feature head | `4f394126ee6d5943b62f09ab0b1d7ec8f48ec0dc` |
| Matching source tree | `e4c610f8718ed1c62fbe0792dc7eccf7d9a5d945` |
| Local inspection checkout | `nexus-theory`, local commit `3bbe3dba7fee163cd076c429852f986eacd95189` |
| Relationship | Different commit histories, matching source tree; local checkout clean |

Implementation must start from the actual remote feature head, recheck it before modifying the branch, and preserve its history. Do not force-push the inspection checkout. No main-branch merge, branch deletion, public MindTrial change or paid model run is part of this planning task.

The previous branch report records 504 passing tests, coverage of all 648 causal truths by public policies/replay, and 197 unchanged legacy snapshots. Those are historical results, **not tests rerun in this planning task**. The new standard-library proof below was run successfully; the routing results also received an independent review and reproduction.

## 2. What must be proved—and what cannot be proved

We can prove requirements on observations, actions and successful policies within a specified finite world family. We cannot prove that an LLM used a particular mental process, prevent a lucky first guess, or infer model failure rates from a mathematical lower bound.

There are three different questions:

1. **Evidence:** What must be observed to justify a decision that succeeds in every world still consistent with the transcript?
2. **Operation:** What is the cheapest policy that actually wins, including experiments, repair attempts, failed submissions, travel and resources?
3. **Model behavior:** Does an evaluated model select informative experiments, revise its account appropriately, and execute a successful repair within the disclosed limits?

Report these separately. In particular, recoverable submissions and unlimited R0 play can make eventual success possible through enumeration with no dedicated measurements. A measurement lower bound is therefore not automatically a lower bound on winning the live game.

### 2.1 Define success by valid decisions, not complete identification

Let `B` be the possible hidden worlds and their current physical states after the complete public transcript. For an executable repair decision `a`, let `W(a)` be the possibilities in which that decision succeeds. The current evidence supports `a` when:

```text
B ⊆ W(a)
```

Different repairs can have overlapping winning sets. Two theories need not be distinguished if the same repair works under both. Conversely, a single public goal such as “all passage channels balanced” does not imply that all worlds have the same solution.

Use **acceptance obstructions**, not only pairs of differently labelled targets: a subset of possible worlds whose intersection of feasible winning decisions is empty. Three worlds admitting repairs `{A,B}`, `{B,C}` and `{A,C}` respectively have a common repair for every pair, but none for the full set. A disjoint pair is a sufficient obstruction, not a complete test. The existing static solver's target-partition/pair-separator logic stays valid for prediction boards; overlapping repair regions require the generalized predicate or higher-order cuts. Do not merge overlapping regions transitively.

For a stateful sequence, evaluate a continuation policy, its observations and its resource feasibility. Do not pretend every task reduces to a unique answer vector. Existing prediction-vector classes remain a useful special case when the decision regions form a partition.

### 2.2 The certificate contract

Every certificate must name the family and version, complete public disclosure, admitted prior, action domain, observation projection, goal semantics, cost objective, resource scope, solver version and any abstraction used. Bind cached certificates to a semantic digest of these inputs. Distinguish:

| Claim | Required evidence |
|---|---|
| Solvable | A policy using only public information wins through the real interface in every admitted world. |
| Exact optimum | Complete search or a matching sound lower bound and executable upper bound. |
| Lower bound | Exhaustive analysis or a proved relaxation giving the player at least as much information/ability at no greater cost. |
| Upper bound | A successful concrete policy; searching a restricted experiment pool only establishes this direction. |
| Unknown | A search limit, unsupported abstraction or incomplete action coverage. Never silently treat this as impossible or qualified. |

Include separate fields for adaptive experiment cost, best fixed-batch cost, feedback-round bounds, preparation depth, success probability under a stated prior/horizon, physical action cost, and coverage across worlds. Do not collapse these into a single invented “reasoning depth” score. Carry the actual prior probability mass when merging equivalent worlds; never assume the resulting classes are uniformly distributed. Use exact rational/integer weights or conservative numerical bounds for threshold checks.

Reconstruct the admitted law/state family from the public contract and disclosed generation constraints. The public witness cannot assume a private generator restriction that the player was never told. Let `m` denote all initially exposed information, including template/claim identifiers, wording, resources and disclosed seed information. A strict per-configuration claim must hold for **every advertised `m`**, using `H_m` and the actual conditional sampling distribution `μ_m = Law(H | m, generation acceptance)`. Account for filtering, rejection sampling and seed selection. A pooled bound over distinguishable configurations is a different, explicitly labelled claim. Do not require the same success ceiling after informative observations: investigation is supposed to resolve uncertainty.

State the sampling assumption. A probability bound over fresh hidden draws is not a prediction about a fixed seed or an adversarially selected instance. New priors require rechecking an all-policy bound, not replaying the formerly best shallow policy. A public seed that makes the hidden truth computable destroys the corresponding uncertainty and must be included in conditioning.

### 2.3 Reject all relevant shortcuts

The proof model must include every player-visible channel: public evidence and metadata, observations, measurements, probe previews, ordinary operations, controller settings, specimen identities/history, inventory, errors, resource counters, finish feedback and terminal transitions. Movement and stock acquisition also belong in the physical model.

Explicitly test:

- A direct mission reading; a preview of a prepared or mission specimen; an operation response that reveals the answer.
- A universal repair, replacement, bypass or common repair that avoids distinguishing the proposed theories.
- Arbitrary experiment order, compound settings, repeated actions, intermediate measurements and legal actions outside the reference policy.
- Reusing or prebuilding specimens, retaining partially prepared specimens, and experimenting on several stock copies.
- Failed submissions as information, including how many candidate decisions a rejection eliminates.
- Public profile selection, identifiers, budgets or certificate availability narrowing the supposed prior.

Qualify a complete publicly described family **before sampling its hidden truth**. If generation conditions on a subset, that selection rule must be part of the admitted prior and requalified. A claim about one difficult world cannot be presented as a guarantee about every generated episode.

No arbitrary stage locks or required explanatory prose will force the intended solution. An early guessed diagnostic context is legal. Its reliability and cost are accounted for by the certificate.

### 2.4 Strengthen high-profile acceptance without changing old scores

For the new family, target all-world shallow ambiguity, multiple task-relevant experimental decisions, and a certified advantage for adaptation. Require a real constructed context for D5. Use stage-removal counterexamples: remove a proposed dependency, give the player all remaining permitted shallow evidence, and demonstrate an acceptance obstruction. It may require more than two worlds when repairs overlap.

These checks must be operational: if a common repair still wins, ambiguity about the laws is irrelevant. If one rich measurement reveals everything, the episode does not meet a multistage claim merely because several internal mechanisms contributed to that reading.

For a profile advertised as requiring three feedback rounds, comparison against all policies with at most two rounds is a release gate, not optional analysis. A fixed batch may remain possible at greater cost; “three adaptive measurements” does not mean “three adaptive rounds are logically unavoidable with unlimited experiments.” Publish the actual bound and scope.

Keep existing certificates and their historical meanings intact. Add stronger claims under a versioned certificate for the new family; do not retroactively reinterpret older D5 results as having passed these gates.

Retain at least three necessary task-relevant observations, two useful physical transformations and a meaningful adaptive/fixed cost gap as construction targets. They are **insufficient acceptance criteria**: several independent readings can be gathered in one batch, and fixed transformations can add mechanical work without adding investigation. The strict deep profile must also pass Sections 2.5–2.7. These stronger requirements apply to the proposed deep template, not to every historical D4/D5 episode.

Separately compute the best live-game policy including speculative commitments. A template whose full-game optimum is a cheap universal repair or short guess sequence fails the intended deep operational profile even if its measurement-only certificate looks impressive. At R0, report the cost of such alternatives instead of claiming they are impossible.

### 2.5 Operational feedback-round gate

Initial manifest/evidence and all other initially available public information are round zero. Define `Π≤r` with a small serialized policy language and interpreter, not an informal count of measurements:

- `Batch`: at entry, public history chooses a finite ordered request list, its length and its end boundary. No response-dependent branching, skipped commands, substantive argument changes or early exit is permitted inside it. One completed batch can supply the next feedback-dependent decision.
- `Branch`: selects the next batch or final continuation from the accumulated public responses. At most `r` batches may supply such feedback.
- `Commit`: selects a final fixed request list whose responses cannot change later choices. It adds physical cost but **no experimental round**. It may use any request, including acquisition, movement, operations and repeated candidate repairs/finishes. Automatic halt at an absorbing terminal state is allowed; a nonterminal response-dependent stop or skip is feedback.

The request domain includes syntactically valid requests that fail only in some hidden states and modeled malformed-input classes. Do not use a private legality oracle to filter choices. Failures and their observations are part of execution. An open-loop physical computation or enumeration that succeeds remains a legitimate shortcut, even when it does not resemble the intended science.

Allow a declared, total administrative adapter for fresh opaque handles and transport envelopes such as `expected_turn`. Prove that it preserves scientific command choices, observations, effects, costs and continuation options under handle renaming. It cannot use an ID's content, a turn change or a failed command to choose a scientific setting or silently skip work. Any automatic status requests remain modeled public interactions. Without this adapter, incidental bookkeeping can create fake rounds; without its restrictions, bookkeeping can hide real adaptation. The current client's turn filling and rejection-without-turn-advance behavior must be covered explicitly.

For each exposed configuration `m` and its actual resource contract define:

```text
C≤r(m) = min over π in Π≤r of max over h in H_m of cost_to_live_victory(π,h)
S≤r(B | m) = max over π in Π≤r of Pr[h ~ μ_m](live victory within B)
```

A failing or nonterminating branch has infinite cost for the guarantee calculation. Cost includes preparation, transport, configuration, experiments, attempts and successful finish. A policy may adapt to public observations only; do not optimize separately with access to the selected hidden truth. Preserve the same hidden world along a trajectory.

Allow arbitrary local computation over the public grammar in the proof model. These are information/interaction bounds, not bounds that assume weak arithmetic or absence of Python. For the finite prior and finite-horizon expected-success objective, randomized mixtures cannot beat the best deterministic policy; document this reduction if the checker enumerates only deterministic policies. Worst-case guaranteed cost must include every allowed policy branch, not expected cost.

For the **new strict three-round profile**, require all of:

| Gate | Required result |
|---|---|
| Public solvability within advertised rounds | An exported executable public policy `π* ∈ Π≤3` with worst-case live-victory cost `U3 ≤ B_cert`, within every stock/use limit. |
| Necessary rounds at release budget | A sound lower bound proving `C≤2(m) > B_cert(m)` for every advertised configuration. |
| Shallow success ceiling | A sound upper bound proving `S≤2(B_cert(m) \| m) ≤ α` for every advertised configuration; provisional design target `α = 0.5`. |
| Genuine dependency | The stateful construction and ablations in Section 2.7 pass. |
| Full protocol equivalence | The exported proof model matches the real interface, including zero-cost responses. |

An unrestricted winning witness plus a two-round exclusion establishes only **at least three rounds**, not that three suffice. A four-round family must not receive an exact three-round profile. Generalized `k`-round claims need a witness in `Π≤k` as well as the exclusions for `Π≤(k−1)`.

`B_cert` is the actual released finite-R1 action budget, not a smaller convenient proof budget. Include the stated recovery allowance before testing these inequalities. Name the finite deviation class, its timing and what the player observes. For every permitted deviation history, group successor worlds by their complete public transcript and exhibit **one public continuation over each resulting belief**, with actual remaining resources. Separate omniscient repairs for indistinguishable successors do not prove recovery. State whether recovery retains the nominal round limit or only budgeted eventual solvability. Spare actions cannot guarantee recovery from a destroyed irreplaceable object; unpromised destructive mistakes can lose legitimately.

`α = 0.5` is a proposed product threshold, not a theorem about LLMs or a claim that the first construction can attain it. It means the best policy in this shallow class succeeds on at most half the admitted probability mass; models using more rounds may still all win. If feasibility fails, keep the template experimental or label it lower. Do not relax the threshold silently, hide legal actions, or remove a promised recovery margin.

Worst-case optimality alone does not provide the success ceiling. A rare difficult world or skewed goal distribution can coexist with a 93% successful uninformed guess. Retain actual sampling weights after public conditioning and after all quotient operations. If only a restricted policy pool was searched, its best success is a **lower** bound on achievable success; it cannot establish `S≤2 ≤ α`. An upper bound needs exhaustive coverage or a justified player-favoring relaxation preserving the policy/round interpretation. Timeouts remain unknown.

At P0, qualify the scientific structure without travel padding. At the intended P/R settings, qualify full cost again. At R0, report cost/round curves and an explicitly stated finite evaluation horizon if used; do not claim that unlimited enumeration has been excluded. Specify any tool-request bound independently from the action budget. Prefer closing free, informative observations without an artificial request cap; a bounded-harness result must name its horizon.

#### Robustness scope

Bind the certificate to exact supported resource cells or a proved envelope: actions, stocks, apparatus uses, prebuilt objects, harness limits and restart access. Reuse requires a checked instantiation of that contract. For an envelope, solvability at the least permissive boundary and hardness at the most permissive boundary suffice **only after proving resource dominance** while preserving laws, goals and public conditioning. Otherwise certify each cell. R0 is outside a finite-budget envelope by default. All success probabilities are per episode; multiple attempts need a separate combined-success statement.

Measure budget sensitivity at the release budget and at least one extra action, plus any supported override. Report the first observed loss of the shallow ceiling, or `unknown` beyond the proved range. A one-action cliff is allowed but must be visible. Infinite cost in a game that already terminates at its deadline is not an infinite safety margin: recompute under each changed deadline or prove equivalence to a deadline-relaxed model. No arbitrary percentage margin is an additional release gate.

Optional prior robustness has a simple bound: with identical support/transition/policy semantics and `TV(μ_m, ν_m) ≤ ε`, a nominal success upper bound `s` implies `Sν≤r(B | m) ≤ min(1, s + ε)`, even if the best policy changes. This follows from the event-probability definition of total variation. It needs headroom: `s = 0.5` certifies no positive prior shift at the same ceiling; `s ≤ 0.45` permits `ε ≤ 0.05`. Global prior closeness does not imply closeness inside every public stratum. Exact-prior invalidation is the simpler valid default; no robust-POMDP framework is required.

### 2.6 Complete public transcript and semantic conformance

The current code has a concrete integration gap: `protocol/session.py` records `TraceRecord` only when a turn advances. Invalid-action responses and non-consuming observations remain visible to the player but do not enter that trace. Investigation `operate`/`probe` responses in `engine/engine.py` also include the complete transformed artifact, not merely a scalar reading. A qualifier or posterior built only from named measurements and accepted-action traces would be incomplete.

Add a normalized **public-interaction transcript** alongside the existing replay trace. Capture request operation, public request, exact public response projection and resource/terminal effects, including manifest/evidence/status/observe, validation errors, protocol conflicts, retries, operations and failed finish. It must be operator-side, preserve current action/replay semantics, and never contain extra private truth as supposed player evidence. Instrument the common public service boundary so HTTP, stdio and direct reference-policy execution use equivalent projections.

Analyze zero-action responses explicitly. Either prove they add no information beyond already available public state or include their information closure in policy search. Check zero-cost cycles and arbitrary malformed input classes; collapsing them requires matching observations and continuations. A valid-action-only search is insufficient.

The witness must reach actual `won` state through `finish` and produce the live receipt. Match deadline ordering and remaining resources exactly, including success on the last allowed action, failed finish at exhaustion, terminal failure, destructive changes, stock depletion and cached/retried requests. A resolved model or a repaired artifact before finish is not a winning terminal state.

Build an independently implemented small oracle and a separate certificate checker. A digest establishes input identity, not a difficulty theorem. The private proof payload must supply:

1. Canonical admitted worlds and exact weights; public-state projection; resource scope; finite request classes with coverage justification; transition and goal versions.
2. The serialized public winning policy, its round/cost bounds and complete tiny-world replay through live finish/receipt; a public recovery policy when promised.
3. A complete finite search representation or independently recomputable bounded model. A success upper bound must satisfy checked Bellman upper-bound inequalities for **every** admitted choice and response branch, with correct terminal values and round/resource counters. A cost lower bound needs a checkable bounded no-win/obstruction proof. The checker derives coverage from the model, not the searcher's reported counts or `complete` flag. Check pruning reasons and zero-cost closure/termination explicitly.
4. For an abstraction, a causal mapping from every concrete public policy to an abstract public policy with no more rounds, no greater cost/resource use and no lower success under the preserved prior. The mapping must be uniform on indistinguishable public histories; a hidden-truth-dependent mapping is invalid. Exact quotients require correspondence in both directions.

Record the trusted boundary: parser/runtime/exporter semantics covered by exhaustive finite conformance, proved quotient/composition rules, and remaining assumptions. Include player-visible structured timing/performance fields and cache indicators in the observation inventory. If uncontrolled transport timing is outside the model, say so; do not claim a wall-clock side-channel theorem. Sampled agreement is not proof of untested quotient behavior. Before interface equivalence is established, label the result as conditional on the exported model.

Mutation tests must reject an omitted action/response branch even with internally consistent digests, hidden-state-dependent policy mappings, response-dependent stopping inside a batch, and falsely normalized informative IDs. Also test new previews, universal repairs, ignored failures, changed budgets/priors and changed disclosure. Larger templates require a proved abstraction/composition argument or remain uncertified.

### 2.7 Scientific dependencies, not preparation padding

For each advertised stage, identify the uncertain state/theory component, the intervention it changes, the evidence it predicts and its effect on the final winning decisions. Show that plausible alternatives agree on available shallow evidence yet form an acceptance obstruction for the mission. A stage relevant only to a nuisance parameter does not qualify.

Use controlled ablations: supply an upstream relation/calibration, remove a proposed coupling, or provide a matched prepared context, and recompute the relevant round/cost/success bounds. Keep observation bandwidth, action costs, material availability and goal conditions controlled where possible; document unavoidable changes. A reduced cost caused solely by deleting two preparation actions does not demonstrate an inferential dependency.

For a coupled-family claim, verify a concrete shared mechanism or interaction in the transition/acceptance model and show that the proposed independent-component explanation or repair strategy is insufficient. Compare with a matched independent-lookup control. Do not equate algebraic nonlinearity, noncommuting known operations, graph depth or a long deterministic script with scientific reasoning difficulty.

Track uncertainty by role: specimen state, correction parameter, relationship structure and regime. A T3 claim needs semantically distinct candidate relationships with a mission-relevant distinguishing witness; different spellings of one function or a hidden specimen selector do not establish missing-law discovery. Requalify after T1/T2 disclosures remove alternatives. This prevents deeper state lookup from being relabelled as higher theory difficulty.

Even a sound three-round lower bound can describe simple pointer-following. Scientific richness also needs empirical checks: reuse inferred relationships across distinct contexts, demonstrate operational transfer beyond copying a single reading, vary structural motifs, and evaluate held-out structures and simple greedy/lookup baselines. These are calibration requirements, not proofs of an LLM's internal reasoning. Finite hypothesis enumeration remains valid.

Each generation template must carry an explicit status: `experimental`, `qualified` for named claims, or `calibrated` after model evaluation. Export a per-template qualification report with thresholds, exact/upper/lower/unknown results, prior mass and structural coverage. Add the complete action grammar, goal, resource budget, public disclosure/presentation and abstraction version to certificate validity. At instantiation, verify the rendered public signature, selected truth's membership in the certified support, resource scope and sampler/version identity. A new seed reuses a certificate only if it instantiates that proved family; a new structure must be separately certified or covered by a verified composition theorem. Never silently fall back from a requested high profile to an easier world.

Publish the exact family/D/T/P/R-to-certificate mapping in the manifest metadata and operator configuration documentation, exposing only safe claim/version identifiers during play. Recommended MindTrial configurations must select the intended qualified family explicitly. Historical families retain their existing qualification scope; the new strict claim must never be inferred from a legacy D5 label alone. Generalize the certificate to requested round depth `k` using `C≤(k−1)` and `S≤(k−1)` for future scaling, without redefining the existing difficulty axes.

## 3. Proof work completed for this plan

A small, independent finite fixture separates adaptive investigation from a fixed panel of experiments. A hidden binary value occupies every internal node of a small tree. Reading a node reveals its value; the mission answer is the sequence of values along the selected route. All nodes can be read immediately and in any order.

| Route length | Possible worlds | Mission answers | Optimal adaptive readings | Smallest fixed panel | Worlds still ambiguous after all shallower-node readings |
|---|---:|---:|---:|---:|---:|
| 1 | 2 | 2 | 1 | 1 | 2/2 |
| 2 | 8 | 4 | 2 | 3 | 8/8 |
| 3 | 128 | 8 | 3 | 7 | 128/128 |

For the three-position route, the best success probability after zero, one, two and three readings is respectively **12.5%, 25%, 50% and 100%**, assuming uniformly sampled worlds and one final answer. Every world needs three measured cells for a sufficient evidence certificate, even if an omniscient selector chooses the cells.

Why the result holds: eight equally likely route answers require three binary outcomes for guaranteed identification; following the observed route attains three. Every one of the seven cells can lie on the route, so omitting any cell from a fixed panel leaves two worlds with the same panel observations but different mission answers. Exhaustive search confirms the bounds.

Negative controls also pass:

- Add a direct answer-reading experiment: adaptive and fixed costs both become **one**.
- Permit overlapping repairs on three worlds: one reading guarantees a valid repair without requiring a unique theory; the best unmeasured repair succeeds in two of three worlds.
- Permit a universal repair: the necessary reading count becomes **zero**.

**Limit:** this is a static query fixture, not a playable scientific ontology. Address length is not a physical preparation transition. It does not yet establish successive stateful experiments, scientific richness, full-game cost, or LLM difficulty. Failed submissions and physical actions are absent. Its role is to test the qualifier and falsify inflated claims. The runnable source is included at the end of this document.

The independent review agreed with these numerical results and required the full-game and overlapping-repair corrections above. Those corrections are incorporated into the implementation gates.

### 3.1 Additional sanity-check counterexamples

The following exact fixtures were executed during the additional audit. A separate reviewer independently verified the selector construction and overlap obstruction. The original proof source remains below; a second runnable audit script follows it.

| Check | Verified result | Consequence |
|---|---|---|
| Selector plus two selected independent bits, 32 worlds | Three readings needed in every world; fixed/adaptive costs 5/3; two rounds suffice. | The previous numerical targets do not prove three rounds. |
| Selector plus three selected bits, 128 worlds | Fixed/adaptive readings 7/4. In a cost-model control with two action units per reading, two common preparation units and two finalization units, totals are 18/12; still two rounds. | A 1.5× cost gap including preparation/finalization does not establish three rounds. This remains a cost-model counterexample, not a live-world construction. |
| Original three-position routing fixture | Optimal reading costs with at most 1/2/3 rounds are 7/4/3. | Three-versus-seven hides how cheap a two-round alternative is. |
| Same routing fixture, two-round policy | 75% success within three readings; 100% within four. | One extra action of slack removes the three-round guarantee; it fails the proposed 50% shallow-success ceiling even at three readings. |
| Three overlapping repair regions | Every pair has a common repair; the full set does not. | Pair-only cuts cannot certify general repair resolution. |
| Skewed eight-world prior | Three readings needed for guaranteed identification, but an uninformed answer succeeds 93% of the time. | Worst-case depth cannot substitute for a probabilistic shortcut bound. |
| Nine equivalent variants versus one alternative | Correct best guess is 90%; a uniform two-class quotient incorrectly reports 50%. | Probability mass must survive equivalence compression. |

These are falsification tests, not new production worlds. Neither the original routing fixture nor the selector fixture qualifies for the new strict deep release claim. Stateful feasibility and model difficulty remain unproved until the implementation gates pass.

### 3.2 Robustness-pass counterexamples

The second audit script also checks these small examples with exact rational arithmetic. They expose specification errors; they do not allege that the current runtime has these leaks or certify a live ontology.

| Check | Verified result | Required protection |
|---|---|---|
| Publicly labelled easy type occurs 10%; other types have shallow success 40% | Pooled success is 46%, although the easy type succeeds 100%. | Qualify each advertised public configuration, or explicitly make only a mixture claim. |
| Two repairs with winning regions `{h0}` and `{h1,h2}`; weights change from `(0.6,0.2,0.2)` to `(0.4,0.3,0.3)` | Formerly best repair falls to 40%; the new best still succeeds 60%. | Replaying the old policy does not revalidate an upper bound. |
| A public type occurs 1%; its hidden split changes from 50/50 to 99.5/0.5 | Global total variation is only 0.495%; within that type it is 49.5%. | Prior robustness must respect public conditioning. The event-probability TV inequality was also checked over all subsets of this four-world support. |
| Two indistinguishable post-deviation worlds require opposite repairs with one action left | Each hidden state has a repair; no public policy guarantees recovery. | Check recovery over beliefs, not separate hidden states. |
| Constant reading but hidden-bit-dependent returned ID | Raw responses permit 100% identification; stripping the ID gives a false 50% estimate. | Prove information-preserving normalization; synthetic IDs in this fixture are deliberately leaky. |

The three-round-witness requirement is an additional logical correction: excluding two rounds while showing unrestricted solvability cannot establish that three rounds suffice. No new positive stateful construction was produced in this review.

## 4. Shared NEXUS world: The Sealed Facility

The player is trapped in an alien facility whose passage system releases them only when a concrete, publicly specified physical or operational condition is satisfied. Available chambers, objects, stocks, apparatuses and records depend on the episode. The player investigates the facility's artificial laws and uses that knowledge to meet the release condition. This premise, narrative voice and terminology cover every ontology supported by the current version, including controls and simpler missions.

Different ontologies supply different mission mechanics within that same world:

| Mission mechanics | Shared-world interpretation |
|---|---|
| Artifact transformation and delivery | Prepare a passage object in the specified state and place it at the designated dock. |
| Scientific prediction/controller tasks | Infer the required responses and configure the passage controller for its declared operating conditions. |
| Network/causal investigation | Investigate interacting facility elements and satisfy that family's exact operational goal. |
| Coupled diagnosis and repair | Restore the passage assembly's joint response while preserving specified working channels. |

These descriptions must follow each family's actual goal; story text cannot invent extra actions, observations, hidden objectives or mandatory stages. The plot is expressed through actual state and progress already exposed by the contract. It does not imply an omniscient narrator announcing that a theory is correct.

Maintain one short terminology/style specification and a shared public-data-only renderer, with ontology-specific role descriptions where needed. Apply them consistently to manifests, evidence introductions, room/object/apparatus descriptions, observations, human-readable action/error/terminal text, help/examples and MindTrial-facing recommended instructions. Keep text concise for model runs and coherent for human play. Use stable common terms for common roles; reserve invented terms for alien substances, properties and mechanisms. Names must not encode the selected hidden law or distinguish otherwise ambiguous hypotheses.

Keep action verbs, JSON keys, IDs, exact values and success predicates explicit. For example, “passage controller” can describe the existing controller while its API identifier remains `controller`. “Facility phase-shifts” can describe elapsed actions, but the contract must state exactly which actions advance them and whether any deadline exists. R0 must not narrate a fictitious in-world deadline. Obfuscate real-world scientific analogies, not the instructions needed to operate the interface.

Version the presentation separately from ontology mechanics. Preserve stored episodes and replay them with their recorded text/contract version. Newly generated episodes across current families use the shared setting; their public-text snapshots or hashes may legitimately change and must receive reviewed versioned fixtures. Scientific seeds, laws, resources and action semantics remain stable. Record presentation version in evaluation metadata so wording changes are not mistaken for increased reasoning difficulty.

This presentation work is a product-wide deliverable and can ship independently if the new repair family fails its proof gate. The Sealed Array below is one mission within this shared facility.

### 4.1 Coupled-repair mission: The Sealed Array

The player is confined in an alien return chamber. A passage assembly in the exit dock must attain a precise joint response under several declared conditions. The player has stocks of fresh specimens, a configurable manipulator, a reader and access to the assembly. The assembly's internal relationships are initially uncertain; experiments can reveal how to alter it without breaking responses that already work.

The manifest states the exact success predicate, apparatus controls, observable fields, supported experiments and resource limits. It does not reveal the selected laws. Invented channel names such as `vek`, `sai` and `nul` avoid physical analogies; ordinary words such as “reader,” “stock” and “dock” keep the action contract understandable. Avoid making vocabulary itself a puzzle.

The intended—but never mandatory—progression is:

1. Observe an anomaly compatible with several explanations.
2. Separate a property of the specimen from a property of the instrument or interaction.
3. Use that result to choose or construct a discriminating context.
4. Infer the coupled behavior relevant to the passage assembly.
5. Apply a repair that satisfies the whole mission while preserving specified control responses.

For example, two candidate mechanisms could agree on every raw-stock reading. A prepared context can distinguish them, but the useful preparation depends on an earlier calibration. The final repair affects several channels jointly, so correcting the visible anomaly alone is insufficient. This is a **candidate construction to prove**, not a claim that the structure alone ensures difficulty.

### 4.2 Scientific content of the repair family

Use small, exact integer or categorical state spaces and a bounded, disclosed operator grammar. Candidate building blocks include conditional routing, modular transformations, permutations, shared latent causes, coupled terms and order-dependent transformations. Express dependencies declaratively where the existing trusted graph/evaluator supports them.

Generate meaningful structural alternatives—different dependencies, locations of corrections, and interaction order—not just new constants in one repeated procedure. Reserve structural motifs for later evaluation. A shuffled vocabulary or longer formula is not sufficient novelty.

Require joint mission acceptance across all publicly specified conditions. Prefer observable control channels that must remain correct, rather than a hidden secondary objective. If more than one repair is acceptable, accept all of them. “Minimal repair” is an efficiency metric unless an explicit material constraint makes it part of the public goal.

Keep lower profiles with direct readings, supplied calibration or a universal safe repair. They provide both controls and legitimate opportunities to notice that an elaborate investigation is unnecessary.

### 4.3 Regime change as a second, bounded variant

First implement a specimen-local conditional regime: an accepted intervention changes a specimen's operating mode according to a stable, disclosed family of possible rules. The occurrence/condition is observable as specified by the contract; its scientific consequences may require inference. Earlier measurements remain valid for their earlier conditions.

This tests selective revision: identify which part of the model ceased to apply, retain unaffected relationships, and repair the resulting operational failure. A paired stationary version is essential to distinguish revision cost from ordinary extra work.

The current runtime transform hook receives the specimen, apparatus, episode and settings, but not the current world turn. Bounded specimen history can support local mode changes without changing engine accounting. Facility-wide timed changes or mutable room topology require a deliberate core extension and are deferred until the local variant demonstrates value.

If a global context is later needed, the engine must own a versioned immutable transition context. Advance it exactly once for an accepted action; observation, invalid actions and retries must retain existing semantics. Do not invent private mutable state inside an adapter.

“Facility phase-shifts” can describe elapsed actions in narrative text. Keep the exact clock semantics public and do not repurpose an existing protocol `phase` field silently.

## 5. Keep T, D, P and R distinct

| Axis | Preserved meaning | Application to the new family |
|---|---|---|
| T0 | Operational model already resolved | Supply task-relevant predictions/decisions; pair with D0. |
| T1 | Exact complete laws | Discover hidden specimen/apparatus state and compose the supplied laws. |
| T2 | Correction of known shape | Estimate the correction parameters and apply the corrected model to repair. |
| T3 | Missing relationship within a bounded prior | Distinguish structural alternatives and any associated parameters. |
| D0–D2 | Supplied, direct, then combined evidence | Controls and smaller investigations, qualified for the actual disclosure. |
| D3 | Upstream inference supports downstream evidence | Calibration or inferred context changes how later evidence is obtained/interpreted. |
| D4 | Adaptive policy beats every fixed batch | Prove the comparison under the same defined experiment/cost contract. |
| D5 | Constructed diagnostic context | Prove raw contexts insufficient and account for all alternative constructions. |
| P | Logistics | Room placement and transport; keep scientific laws and contexts unchanged. |
| R | Resource pressure | Disclosed actions, stocks and uses; keep laws unchanged. |

D is a set of structural categories, not a universal scalar ranking. Add certificate measurements for depth and coupling instead of inventing D6 or T4. Regime change is a family variant, not a new meaning for T, P or R.

Start science qualification with incidental logistics removed. Analyze evidence sufficiency separately from unlimited R0 eventual play. Then certify physical policies and finite R overlays. Moderate R must fund an actual public-information investigation and recovery margin, rather than only a perfect-knowledge shortest path.

Changing T disclosure changes the admissible hypotheses and may remove an adaptive dependency. Requalify each supported cell; reject unsupported combinations clearly. Do not populate a rectangular matrix by relabeling theory uncertainty as specimen uncertainty.

## 6. Architecture and compatibility

Use the existing trusted ontology registration mechanism. Working family identifier: `coupled-repair-v1`. It remains opt-in through the existing family selector. This is not arbitrary third-party code loading.

The shared setting is independent of this selector. Put common presentation definitions and rendering outside `ontology/repair`, for example in a small `presentation/` module. Existing and new adapters provide public role/mission descriptions; the common layer must not inspect private truth or implement scientific behavior. Do not duplicate the narrative separately inside each ontology.

| Boundary | Planned responsibility |
|---|---|
| Shared `presentation/` module and terminology document (new) | Facility premise, consistent public role names, mission framing and presentation versions for all current families. |
| `ontology/repair/schema.py` and `laws.py` (new) | Versioned public controls, specimen state/history, private truth, exact transformations and acceptance. |
| `ontology/repair/runtime.py` (new) | Ordinary take/configure/operate/measure/probe behavior and concrete mission assessment. |
| `ontology/repair/inference.py` (new) | Public-transcript belief updates, including repair and rejected-goal evidence. |
| `ontology/repair/generation.py`, `qualification.py`, `evidence.py` (new) | Certified family templates, private sampling, witnesses and clear public instructions. |
| `ontology/catalog.py`, `payloads.py` | Explicit registration and role-specific validation. |
| `solver/finite_experiments.py` | Preserve existing static solver; reuse immutable partitions and bitsets where appropriate. |
| New bounded policy-analysis module | Full stateful search and independently checked certificate logic, initially for tiny instances. |
| New round-limited policy/certificate checker | Serialized batch semantics, weighted bounds, public recovery, checkable proof payloads, resource/prior scope and mutation tests. |
| `ontology/contracts.py`, `ontology/inference.py` | Add the smallest capability for state-dependent winning decisions without breaking prediction-board adapters. |
| `protocol/public_transcript.py` (new), shared service/session boundary | Complete normalized player-visible requests/responses, including free observations and errors, alongside the unchanged historical action-replay contract. |
| `protocol/investigation_metrics.py` | Common terminal metrics driven by the mission capability, without one branch per family. |

The current interfaces include `expected`, `submitted` and target exclusion, which suit prediction boards. Before integrating repair, introduce a backward-compatible mission-decision capability: legal decision representation, acceptance/feedback semantics and evidence-supported success. Existing adapters retain their exact-vector behavior through a compatibility implementation. Do not manufacture a unique hidden repair vector for a mission that has several valid solutions.

Keep runtime execution, private qualification and public inference separate. The public inference path must never receive the selected truth. A truth-aware shortest plan is useful for debugging but cannot justify a player's budget; the winning witness must choose its actions from the public transcript.

The engine continues to own transactional copying, locality, action/resource accounting, terminal state, replay and receipts. Preserve probe immutability, invalid-action rollback, fresh-stock semantics, explicit `finish`, and the actual live victory receipt. New family behavior should not require family-name conditionals in the engine, service or receipt code.

### Full-state qualification

Represent a belief node as possible `(hidden world, current hidden state)` pairs, plus common observed state, inventories, remaining resources and the transcript information relevant to future behavior. Preserve correlations with the fixed initial world across action branches.

Use bounded AND/OR policy search: the player selects an action, then every compatible observation branch must admit a winning continuation for a guarantee. A known finite action budget supplies a horizon. R0 requires a separate terminating-policy/reachability treatment or a proved finite abstraction; an arbitrary stock/horizon cap is not an unlimited-play theorem.

Macro-experiments may accelerate analysis only after proving that their expansions match live actions and that no relevant off-macro sequence is omitted. An exact state quotient must preserve legal continuations, observations, acceptance, prior mass, feedback-round accounting and costs—not merely the current measurement partition. Drop no-op observation loops only after establishing that they cannot alter future behavior or information. Zero-cost informative responses require closure or an explicit bounded-request scope.

## 7. Performance and cleanup

The existing static minimax solver is bounded to small hypothesis/experiment sets; the causal greedy policy is a witness, not a global minimax result. Do not simply raise those limits and put full policy search on every MindTrial task's startup path.

Prioritize these optimizations:

1. **Qualify reusable families offline.** Cache immutable compiled transitions, partitions and checked proof payloads by semantic version, disclosure, sampler/prior, resource cell and structural template. Use a cheap instantiation-membership check rather than rerunning search per episode. Instantiate independent hidden truths from fresh seeds. Distinguish structural seeds from parameter seeds: a genuinely new structure may need fresh qualification.
2. **Use compact exact representations.** Integer bitsets, immutable transition tables and bounded memoization avoid repeated Python object construction. Track peak memory and explored states as well as time.
3. **Search with sound bounds.** A cheap executable policy supplies a cost upper bound and a success-probability lower bound. Generalized acceptance obstructions or proved player-favoring relaxations can supply cost lower bounds and success upper bounds. Pair-separator shortcuts apply only where their assumptions hold. Preserve these directions in results and use incremental obstruction discovery before constructing an expensive full hypergraph.
4. **Reduce only proved equivalences.** State symmetry and dominated-test elimination must preserve future options, resources and acceptance. Equal current outcomes alone do not justify merging destructive experiments.
5. **Keep expensive generation diagnostics private.** Record compile, qualification, cache, instantiation and replay timings; expose no posterior or experiment recommendation to the player.

Parallelize independent offline template qualification only if profiling shows a useful batch workload. A standard-library process pool is a reasonable first comparison. Avoid nested pools and per-action IPC. CPU/GPU execution, a new symbolic engine or an external model-checker library requires a measured bottleneck and a small equivalence/performance PoC first; none is a prerequisite for this bounded integration.

Use explicit wall-time, state-count and memory limits. On exhaustion, return `unknown` with a resumable checkpoint; never promote an uncertified template. Cold/warm timings and repeated-generation memory must be measured on the same machine against the current branch. Keep existing families off new analysis paths.

Cleanup should be limited to seams exercised here: common mission acceptance, reusable bounded search data and repeated pure compilation. Extract abstractions when both a current family and repair use them. Avoid a general simulation framework or broad renaming during compatibility-sensitive work.

## 8. Implementation sequence and proof gates

Each phase ends with a focused commit, a checkpoint and an explicit gate result. Later production registration depends on earlier proof gates. A failed gate returns the family to a PoC; it does not justify hiding an action or tightening the budget to disguise a shortcut.

### Phase 0 — Anchor the branch and record the baseline

Fetch the actual feature head; inspect `AGENTS.md`; create a branch-local work log with the base SHA/tree, supported family versions, commands, fixtures and unresolved risks. Run the existing suite once and record generation/runtime profiles. Preserve historical snapshot hashes and representative live transcripts. Inventory player-facing text across every supported ontology and protocol surface before introducing the shared presentation version.

**Gate:** clean baseline or an explicitly isolated pre-existing failure; no accidental replacement of remote history.

### Phase 1 — Implement the proof contract and falsification fixtures

Add versioned certificate schemas with proof direction and scope. Add support for overlapping winning decisions in the analysis layer. Port the routing, direct-read, shared-repair and universal-repair fixtures from this plan. Add negative fixtures where a misleading dependency graph, a failed submission or a preview removes the claimed difficulty.

Include both audit scripts' fixtures: selector/padding false positives, exact one/two/three-round costs, the three-world overlap obstruction, skewed prior and mass-preserving quotient. Implement the finite round-limited cost/success analysis and certificate checker on these small cases first. Define the complete public-transcript schema and inventory its emitters; include a deliberately informative zero-cost error as a negative qualification fixture. Do not rely on the current accepted-action trace as the full observation model.

Freeze the serialized batch language and minimal proof payload on one tiny finite request quotient. Add the robustness fixtures in Section 3.2, a winning witness that exceeds its advertised round count, response-dependent batch stopping, valid opaque-handle renaming/turn filling, and an omitted proof branch with matching digests. Ensure finite request classes cover hidden-state-dependent rejection as well as accepted commands. Test public recovery and per-configuration sampling explicitly. Do not build a generic verification framework before this small checker works.

Specify the mission-decision capability and check its compatibility mapping on an existing prediction ontology before changing runtime consumers. Existing causal certificates retain their scope; a 568-row greedy witness must not become an exact optimum by renaming it.

**Gate:** independent enumeration agrees with the solver on tiny cases; each injected shortcut lowers/rejects the relevant certificate; the two-round counterexamples cannot pass a three-round claim; overlapping repairs and prior masses are handled correctly. Existing prediction semantics unchanged. A certificate checker rejects intentionally incomplete action/observation coverage and incorrect bound direction.

**Companion presentation commit:** define the facility premise and terminology, implement the small shared renderer and adapt all currently supported ontologies. Add versioned public-text fixtures and update human-facing documentation/examples. Verify that the same legal action trace produces the same scientific state, acceptance and resource usage under each presentation; historical replay fixtures remain intact. Review wording for clues, unsupported capabilities and contradictions with R0/P0 controls. This commit has its own gate and does not wait for repair integration.

### Phase 2 — Prove a real coupled-repair construction

Build a tiny pure-state PoC using the intended specimen transformations, legal action grammar and repair goal. Enumerate all admitted truths and reachable states under the declared bounded profiles. Search actual policies, including speculative repairs and failed submissions. Compare against a separately implemented small oracle.

Start with two or three response channels and at most 128 admitted truths; expand only after measuring state growth and proving the smaller case. Enumerate actual bounded resources for finite-R certificates. Any restriction used solely to make the solver tractable must be identified as an analysis restriction, not silently imposed on R0 or treated as the full game. Collapse invalid control values only after showing identical responses and continuations.

Produce acceptance obstructions for every claimed dependency, all-world evidence-certificate coverage, a public winning policy within three rounds and round-limited cost/success bounds. Establish the relationship between macro-experiments and arbitrary public request sequences, including final open-loop continuations. Measure state growth before increasing size. Validate controlled dependency/coupling ablations and public recovery over actual successor beliefs.

**Gate:** before claiming the strict deep profile, at least one stationary family must provide `π* ∈ Π≤3`, `U3 ≤ B_cert`, `C≤2 > B_cert` and `S≤2(B_cert | m) ≤ 0.5` for every configuration it advertises under its actual released moderate-resource contract, plus the scientific-dependency and complete-interface gates. Preparation cannot exist only as a label or known mechanical padding. The original routing toy does not satisfy this gate. Lower qualified profiles may be retained, but they do not complete this phase's deep-mission objective. If the strict family is infeasible within the declared search scope, record the counterexample/unknown result and redesign before production registration of that claim.

Keep the first positive target to one exact T/D/P/R configuration; extend resource/prior envelopes only after it passes. Freeze the provisional three-round/50% targets while checking this feasibility. Record state count, time, memory, uncovered input classes and assumptions. Interface-equivalence obligations that require the final adapter are provisional until Phase 3; a pure-state PoC alone does not authorize a live-game certificate. Optional robustness margins must not displace this central positive construction.

### Phase 3 — Integrate the stationary family through ontology contracts

Add the repair modules and trusted registration. Implement public evidence and the Sealed Array mission using existing action verbs and bounded controls. Extend mission diagnostics through the accepted capability, retaining the compatibility adapter. Bind generation to approved family templates and sample the hidden truth only after the public family is fixed.

Implement the public-interaction transcript at the shared boundary without changing turn accounting or historical replay. Execute each reference policy through the real interface in every tiny-world truth. Compare complete responses, posterior updates, acceptance and costs with the PoC. Include off-policy traces, invalid/free requests, protocol retries, failed attempts, reused specimens and probes. Verify the same public transcript produces the same policy action, regardless of private truth. Qualification runs on the final rendered public contract, not an earlier simplified PoC interface.

**Gate:** real runtime and proof model conform over every reachable state/action class in the smallest released template; receipts, replay, privacy and rollback pass; only certified D/T combinations are advertised. Larger released templates require a verified coverage/composition argument, not only sampled trajectories. Recompute the strict gates after final budget, presentation and action-contract changes. Older ontology mechanics and scientific seed behavior remain unchanged; their approved shared-presentation changes use the new presentation version.

### Phase 4 — Add local regime change and selective repair

Add one bounded local regime variant plus a paired stationary control. Use public treatment history and immutable law data where possible. Verify that old evidence retains its contextual meaning, unaffected mechanisms remain valid, and a successful repair after the change is possible under the public contract.

Check policies that anticipate the regime, make a universally robust repair, or avoid the trigger. Such policies are valid; account for them before claiming revision is required. Re-run qualification with the entire conditional law in the prior.

**Gate:** the variant adds a demonstrated operational revision problem rather than unexplained drift or merely extra actions. Defer global clock/context extensions unless this phase establishes a concrete need. If this variant fails, ship only the qualified stationary family.

### Phase 5 — Optimize, harden and prepare evaluation

Move reusable qualification out of per-task generation; add bounded caches, profiling and terminal telemetry. Run compatibility and conformance gates, cold/warm performance comparisons, documentation review and end-to-end live-session tests. Publish the supported profile table, exact certificate scopes and the model matrix below.

**Gate:** no mechanical regressions in old families; shared setting consistent across all current families; no active-play diagnostic hints; reproducible reference wins; acceptable measured startup/resource cost; unsupported profiles fail clearly. Only then invite real-model runs.

## 9. Validation and telemetry

Proposed new test files are `test_repair_qualification.py`, `test_repair_runtime.py`, `test_repair_regimes.py`, `test_round_limited_policies.py` and `test_public_observation_coverage.py`; names can be consolidated if that improves readability. Prioritize semantic tests over tests that mirror implementation:

| Area | Essential checks |
|---|---|
| Qualification | Exact tiny-world oracle agreement, round-limited witness and cost/success bounds, repair obstructions, conditional-prior weights, independently checked proof coverage, timeout reported as unknown. |
| Runtime conformance | All finite actions/states in the smallest family; targeted off-policy traces for larger certified templates. |
| Public information | Inference consumes only public transcript; no truth selection through public metadata; no active certificate/posterior leakage. |
| Protocol coverage | Invalid/free responses, complete artifact projections, retries and protocol conflicts; informative zero-cost mutation rejected; no hidden outcome omitted from the solver. |
| State ownership | Invalid actions roll back; probes preserve specimens; sessions and cached data are independent. |
| Goal | Common valid repairs accepted; insufficient repairs rejected with documented feedback; no invented unique solution requirement. |
| Budget/rounds | Fixed batch length/stopping; administrative ID/turn adapters; final commitment and terminal halt; finish/deadline ordering; one public recovery policy per transcript; checked resource envelope and extra-action sensitivity. |
| Scientific dependency | Fixed preparation padding and independent-lookup controls rejected for stronger claims; controlled coupling/context ablations alter the claimed inferential requirement. |
| Compatibility | Existing ontology mechanics, historical snapshots/hashes, CLI/service action contracts and scientific seeds preserved; new presentation fixtures explicitly reviewed and versioned. |
| Shared presentation | Coverage of every supported family and player-facing surface; consistent terms; no private-truth-dependent hints; exact goal/action/resource semantics preserved. |
| Replay/receipt | Exact replay of successful and failed missions; actual finish required; live receipt validation preserved. |
| Regimes | Context-correct evidence, unchanged unaffected mechanisms, trigger/avoidance/robust-repair cases. |
| Performance | Cold/warm generation, qualification states and peak memory, repeated-session cache bounds, action latency. |

Baseline/final commands use the repository's declared Python environment:

```bash
uv sync --frozen --all-extras
NEXUS_STRESS_SEED_COUNT=3 uv run pytest -q --maxfail=1 --durations=12
uv run pytest -q tests/unit/test_causal_mechanisms.py tests/unit/test_cli.py
```

Add targeted new tests and the existing profiling scripts as each phase lands; no `make` target is assumed. Run the full suite at baseline and final integration, with targeted checks between phases. Expand testing when a specific unresolved risk or changed shared contract requires it.

Private terminal telemetry should distinguish: certificate status/scope; remaining valid decisions; first evidence-supported successful decision; unsupported versus supported attempts; redundant measurements; regime-specific belief updates; preservation of control responses; execution failure after sufficient evidence; actions/resources; and final receipt submission. A guessed win remains a win. Evidence-supported performance is an additional diagnostic, not a retroactive change to scoring.

Do not label an individual trace as proof of the model's internal adaptive reasoning: the observed sequence does not expose its unchosen branches. Round bounds describe the task's policy class. For a run, report actual interactions and objective evidence/decision sufficiency, using the complete public transcript and its declared initial-information convention. Suppress any stronger diagnostic that is unknown.

“Already resolved” must refer to the current regime and executable decision. It can cease to hold after a state change. Do not reuse a permanently monotone target-resolved flag for these missions.

## 10. Initial real-model matrix

Use this as a **ten-cell pilot**, not ten runs sufficient for a reliability claim. Hold model settings, presentation version and tool availability fixed; use fresh paired seeds where the same latent structure is meaningful. All profile labels below are conditional on qualification. Cells with altered disclosure must be independently certified. Comparisons against earlier NEXUS runs must identify the presentation change; use a small matched old/new wording control if attributing a performance shift to mechanics.

| Cell | Family/control | T / D intent | P / R | Expected relative challenge and purpose |
|---|---|---|---|---|
| 1 | Stationary, operational solution supplied | T0/D0 | P1/R1 | Very low scientific demand; checks execution. |
| 2 | Stationary, sufficient observations supplied | T3/D0 | P1/R1 | Structural inference without experiment selection. |
| 3 | Stationary, direct informative shortcut | Qualified lower D, supported T | P1/R1 | Low; tests whether the model takes a legitimate shortcut. |
| 4 | Stationary, combined evidence | T2/D2 where supported | P1/R1 | Moderate control for composition/correction. |
| 5 | Deep stationary, correction shape supplied | T2/high qualified D | P0/R1 | Stronger investigation, minimal logistics. |
| 6 | Matched deep stationary, structure hidden | T3/same D only if requalified | P0/R1 | Isolates added theory uncertainty. |
| 7 | Deep stationary | T3/high qualified D + strict certificate | P1/R1 | Main test; must pass the round/success gates at this exact budget before evaluation. |
| 8 | Same family with unlimited in-world resources | T3/high qualified D | P1/R0 | Separates resource failure and excessive investigation; track bounded-harness completion. |
| 9 | Paired local regime change | T3/high qualified D | P1/R1 | Revision and preservation of unaffected mechanisms. |
| 10 | Unseen qualified structural motif | T3/high qualified D | P1/R1 | Checks transfer beyond memorizing one experimental procedure. |

D4 should identify an adaptive advantage; D5 must additionally demonstrate constructed-context necessity within its stated evidence contract. They are not automatic synonyms for “hard.” Expect cells 6–10 to be more challenging, but treat that as an empirical hypothesis.

Keep external Python/source access disabled for this comparison, matching current evaluation practice. Developer proof code is not a player tool. Give the harness enough calls for required manifest/evidence reading and the certified policy, separately from the in-world action budget. Report harness truncation and infrastructure failures separately from mission failure.

After the pilot, freeze the architecture and evaluate multiple fresh seeds per cell/model, with paired comparisons and uncertainty intervals. Do not select seeds solely because a target model failed them. A win-rate target such as “at least half fail” is an evaluation outcome, not a generation certificate.

Compare the main deep condition with a matched independent-lookup or supplied-upstream-relation control to separate serial data collection from coupled inference. Use an existing pilot control where it can be matched validly; add a diagnostic ablation run if it cannot, rather than claiming an unmatched comparison isolates T/D. Keep calibration/model results distinct from formal qualification in reports.

## 11. Resume and cost discipline

At every phase boundary, commit a small work-log entry with: base/current SHA, changed modules, completed proof obligations, counterexamples, exact commands/results, certificate/cache versions, profile artifacts and the next executable task. Store expensive qualification checkpoints with their semantic digest; invalidate them when the public contract, transitions, acceptance or prior changes.

Keep phases independently resumable and the last passing implementation usable. Do not start a long search without a bounded budget and checkpoint path. Actual account credit/reset availability is external; do not assume the process can observe it or automatically wait for it. Prefer resumable local proof work and defer paid model runs to the agreed matrix.

**Next executable task:** anchor the real remote feature head, record baseline tests, then implement Phase 1's certificate/acceptance fixtures. Production family generation must wait for Phase 2's stateful proof.

Sanity-check decision: the architecture is viable as a plan, but point 1 is not fulfilled by the existing toy proof. The strict qualification gates are now mandatory for claiming the new deep profile. Unresolved feasibility is an explicit implementation risk; a failed proof gate must remain visible in the handoff.

Robustness-pass decision: the claim is now specified tightly enough to implement and falsify, but the joint positive result remains open. The next proof must simultaneously establish public solvability within three rounds, shallow success at most 50% at the recovery-inclusive budget, scientific coupling, live-interface equivalence and tractable qualification. A guarantee about this policy class does not guarantee sophisticated reasoning or failure by unrestricted LLMs. Do not add further generic metrics before attempting that smallest positive case.

## 12. Research grounding and limits

- [Agarwal et al., Learning with Limited Rounds of Adaptivity (2017)](https://proceedings.mlr.press/v65/agarwal17c.html): treats query count and number of feedback rounds separately. The round-limited NEXUS gate uses this distinction; the paper's learning bounds do not transfer automatically to this game.
- [Javdani et al., Near Optimal Bayesian Active Learning for Decision Making (2014)](https://proceedings.mlr.press/v33/javdani14.html): explicitly treats overlapping decision regions and higher-order structure. This supports the generalized repair acceptance model; its static-test guarantees do not certify destructive stateful actions.
- [PRISM, Partially Observable Models](https://www.prismmodelchecker.org/manual/ThePRISMLanguage/PartiallyObservableModels): specifies policies through observations rather than hidden states. This is a useful independent modeling reference, not a decision to introduce a model-checker dependency or assume it proves NEXUS properties automatically.
- [Norman, Parker and Zou, Verification and Control of Partially Observable Probabilistic Systems (2017)](https://www.prismmodelchecker.org/bibitem.php?key=NPZ17): distinguishes partial-observation models, strategies and numerical bounds. Supports the explicit proof-model/strategy contract; it does not discharge NEXUS's exporter or abstraction obligations.
- [Levin, Peres and Wilmer, Markov Chains and Mixing Times, Chapter 4](https://www.stat.berkeley.edu/~aldous/260-FMIE/Levin-Peres-Wilmer.pdf): defines total variation as the largest difference in event probabilities. The optional optimized-success bound in Section 2.5 is derived from that definition for a fixed NEXUS policy class, not a claim about changing transitions or public conditioning.
- [Nielsen Norman Group, Consistency and Standards](https://www.nngroup.com/articles/consistency-and-standards/): supports consistent terminology across a product. Applied here to interface roles and action clarity, while intentionally keeping the world's scientific laws artificial and unfamiliar; it is not evidence of increased model difficulty.
- [Golovin, Krause and Ray, Near-Optimal Bayesian Active Learning with Noisy Observations (2010)](https://proceedings.neurips.cc/paper/2010/hash/1e6e0a04d20f50967c64dac2d639a577-Abstract.html): supports reasoning about adaptive test selection under explicit priors and costs. Its guarantees apply to its assumptions, not automatically to state-changing NEXUS actions.
- [Golovin and Krause, Adaptive Submodularity](https://www.cs.cmu.edu/~dgolovin/papers/colt10.pdf): a warning against assuming greedy experimental design is inherently weak. Use greedy policies as serious baselines; establish where a proposed family differs from the theorem's setting.
- [Soucha and Bogdanov, Observation Tree Approach: Active Learning Relying on Testing](https://academic.oup.com/comjnl/article/63/9/1298/5525443): supports treating action sequences and their responses as finite-state behavior, with explicit testing/conformance assumptions. NEXUS does not inherit the paper's teacher, reset or equivalence-query facilities.

The concrete design, certificate contract and fixture in this document are engineering proposals/proofs for NEXUS. These papers do not establish that this proposed ontology is difficult for current LLMs. The repository's `docs/scientific-investigation-design.md` and `docs/ontology-author-guide.md` remain the compatibility and axis references.


