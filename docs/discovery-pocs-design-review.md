# Fresh-context design judgement

Scope: read-only review of AGENTS.md, both discovery PoC plans, the existing scalar script/report, and the design-check fixtures. No repository files changed. Recommendations below are for an honest bounded pilot; neither family should receive a deep-tier claim. Exact small enumerations described here were executed independently in JavaScript, not through the NEXUS runtime.

## Decision

The existing 972-program candidate is a useful system-identification control but does not yet establish the approved representation contrast. Its public transition skeleton already fixes the three delayed coordinates and the feature basis; varying its seven coefficients mainly tests parameter fitting. Its ten-query panel is an achieved shortcut, and its 972 distinct initial behaviors are not yet 972 mission-acceptance classes: no build language or mission acceptance relation exists in that script.

A meaningful pilot is possible with the small structural change below. It will test the value of supplying a sufficient memory-composition skeleton, not prove that a model invents a uniquely correct internal ontology or needs an intrinsically deep reasoning process. Fixed panels, enumeration, alternative sufficient representations, and successful shortcuts remain legal.

## Representation: concrete bounded replacement

Use three trit memory cells, initially zero, updated synchronously from old cell values. Each cell chooses an input source, update kind, and nonzero gain:

- Cell 0 source is the public input x.
- Cell 1 source is x or old cell 0.
- Cell 2 source is x, old cell 0, or old cell 1.
- Update kind is overwrite or accumulation: r_i' = g_i*source_i or r_i + g_i*source_i, modulo 3.
- Each g_i is 1 or 2.
- Readout is r_2 or r_0 + r_1*r_2, modulo 3.

This gives 6 source graphs × 8 update-kind assignments × 8 gains × 2 readouts = 768 syntactic worlds, at most 27 states. Nine integer construction settings suffice: source1, source2, kind0, kind1, kind2, gain0, gain1, gain2, readout.

Independent exact refinement found 138 initial behavior classes after six rounds. Reachable-state counts across the 768 programs are 3 (32 programs), 9 (448), and 27 (288). Minimal reachable predictive partitions have sizes 2, 3, 5, 6, 7, 9, 14, 17, 18, 21, and 27; 80 syntactic worlds require 27 classes. This is actual variation in operational memory structure. Preserve prior weights when quotienting duplicates.

T2 supplies the source graph, overwrite/accumulate choices, and readout expression, leaving gains unknown. T3 supplies only the complete bounded primitive grammar. The same physical world, observations, controls, mission, and allowance must be used. Select T2 seeds for which unknown gains still leave mission-incompatible builds; otherwise T2 accidentally becomes another execution control.

The concrete build is a predictor with the public input stream as input and an emitted response as output. At finish, compare its response with the specimen for every reachable input history. Product-automaton equivalence has at most 27×27 states per pair; equivalently use exact initial-behavior classes when both programs belong to the enumerated grammar. A live raw-response feedthrough must not be a predictor input, since that trivializes the public behavior contract. Accept any expressible behaviorally equivalent build, including a different wiring, rather than requiring latent settings to match.

The claim remains narrow: structural state-system identification with a supplied-skeleton control. Much of this family may admit impulse-response or short universal-panel shortcuts. The parent independently reports length-six reset words distinguish all 138 classes. That result should be recorded, priced using actual actions, and used to calibrate the pilot rather than suppressed. A/B seed selection must use canonical behavior and memory structure, not syntactic graph differences alone.

## Uncertainty: mechanism and initial scheduling variant

Use all rank-two dual subspaces of GF(2)^5 for which every nonzero dual vector has Hamming weight at least three. There are 15 such subspaces. Each of their four affine cosets is a disturbance support of eight five-bit vectors, giving 60 physical supports. Every support has identical one-channel and two-channel marginals. Distinct supports intersect in zero, two, or four vectors.

Let physical signs be s_j = (-1)^z_j. The lab displays y_j = s_j + lambda_j, with loading pattern either all +1 or alternating +1,-1,+1,-1,+1. The fixture keeps its reading on repeat. A known zero-signal reference exposes the loading vector. Operationally, enumerate both shared nuisance values delta=-1,+1, expose a reference r=delta, and let sensor readings be y_i=s_i+lambda_i*delta for i<4. This is finite persistent measurement nuisance, not a statistical-noise or confidence-calibration claim.

The first scheduling proposal used a hidden cyclic phase 0..7 over the sorted support, yielding 60 supports × 8 phases × 2 loadings = 960 worlds. This was subsequently superseded: the parent's exact Python audit found a universal THREE-consecutive-fixture shortcut. Although cyclic phase removes one-query leakage, it insufficiently hides sorted order. Public evidence must retain fixture identity; marginal views must not accidentally retain cross-channel row alignment.

A build uses [mask, offset, loading_pattern], with mask 0..15 over the first four channels and offset 0/1. It corrects selected sensors by y_i - chosen_lambda_i*r, requires their corrected values to be valid signs, and emits their signed product multiplied by (-1)^offset. The target is s_4. Enumerate every support point and both operational nuisance values at finish. Wrong loadings on unused channels may be irrelevant and must be accepted.

Independent enumeration of this exact final variant found:

- 64 legal builds; 120 operational worlds, or 960 including panel phase.
- 96 operational worlds have two accepted builds and 24 have three, counting equivalent loading choices.
- No universal accepted build.
- Any single physical vector leaves 15 of the 60 supports and no common predictor.
- The 56 possible raw joint-reading outcomes, with unknown loading and phase, all leave no common accepted build. Thus one joint fixture reading cannot support a construction.
- Twenty-four operational worlds admit a predictor using only even-index sensor channels, making the loading-pattern distinction mission-irrelevant. Retain these worlds in the full prior but avoid them as the main measurement-relevant seed, or label them easier controls. Equivalently, the relevant dual rowspace contains mask 21 (bits 0,2,4).

T2 supplies the dual rowspace and loading pattern, leaving the affine coset bits and fixture assignment unknown. T3 supplies the bounded rowspace/minimum-weight grammar, affine offsets, loading grammar, and fixture-index contract. Universal panels remain an explicit pilot limitation.

### Scheduling correction: exact factored permutation model

The parent's replacement uses all 8! bijections from fixture IDs to support points. There are 120 support/loading mechanism models and 4,838,400 compiled model/schedule combinations. These counts must be reported separately; do not keep calling the revised prior 960 worlds. The program cap can still cover 120 mechanism models, with schedule nuisance factored explicitly.

This factorization is sound with a uniform schedule prior: after k distinct fully observed fixtures, each compatible support/loading model admits exactly (8-k)! schedules. The matching is unique because each support/loading observation map is injective. Thus the mission posterior can retain the 120 models and shared multiplicity. For an unused fixture, possible observations are exactly the model's remaining rows; all unused IDs are exchangeable.

Enumerating all 256 observed-row subsets per operational model gives an exact audit for full joint fixture exposures. Track calibration knowledge separately. Arbitrary partial or channelwise reads of indexed fixtures require a richer matching-state calculation; the subset audit alone cannot claim to cover those channels. Unknown permutation removes sorted-order leakage but does not create valuable adaptive choice among unobserved fixture IDs.

An analytic universal upper bound remains five raw joint exposures, even without explicit calibration. Five distinct points of an affine three-flat span that flat: every proper affine subflat has at most four points. Loading is also resolved by five rows, because every odd physical channel is balanced, so at most four of the eight rows produce the ambiguous zero reading. One nonzero odd-channel reading identifies all-positive versus alternating loading. Therefore five raw rows recover loading and physical support, allowing a robust predictor. The parent should confirm this with the exact subset audit and report any shorter mission-support policy. This calibration-bypass shortcut is compatible with an honest dependence/robustness pilot and incompatible with a claim that explicit reference calibration is mandatory.

## Gates before registration

1. Build acceptance masks first. Compute supported construction by intersecting accepted-build sets across surviving worlds; unique parameter identification is unnecessary. Inference must retain phase/loading worlds until evidence excludes them.
2. Test raw readings, reference readings, fixture identity, repeats, unsynchronized marginals, synchronized pairs, complete joint panels, direct build trials, and recoverable finish outcomes as explicit legal information channels. Price queries and physical actions separately.
3. Validate no-sample and one-sample mission ambiguity exactly; search fixed panels, standard calibration prefixes, individual higher-order moments, and conservative builds. Report achieved upper bounds and bounded-search limits without calling them optimal costs.
4. For uncertainty, show complete local/pairwise closures leave incompatible builds even with nuisance calibrated; show the complete joint/reference policy is evidence-supported. Evaluate averaging, independence, and mean-only policies as actual constructions. Seed selection should retain cases where loading matters to every valid predictor.
5. For representation, retain same-current-reading/different-future witnesses, shortest distinguishing suffixes, actual mission equivalence, and residual mission ambiguity after fixed prefixes. Test T2 still leaves bounded parameter work and T3 never leaks its selected skeleton.
6. Check controls and error/finish projections, failed-finish recovery, deterministic replay, public/private separation, exact T0/T2/T3 matching, and R0 matching in the runtime. These scalar enumerations do not replace those gates.

No remaining conceptual blocker prevents scalar proofs and thin runtime implementation of these pilot mechanisms. Admission should explicitly record their shortcuts and leave hard/deep tier false. If the project requires resistance to every short universal panel as a prerequisite for any pilot, neither mechanism is yet established to meet that stronger gate.
