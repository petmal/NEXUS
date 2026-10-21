# Coupled-memory design judgement

Reviewed 2026-10-21. Read-only review of `NEXUS/AGENTS.md`, `NEXUS/docs/coupled-memory-plan.md`, the scratch `poc_coupled_memory.py`, and the existing discovery runtime, generation, policy, qualification, audit, and engine action semantics. No repository files were modified. The calculations below used the supplied scratch model; they are design evidence, not a review of a completed implementation.

## Decision

The ternary candidate is a defensible **experimental coupled-memory family**, provided its qualification reports the limitations below and it receives no stronger difficulty or deep-tier admission. It has real material-memory feedback and a mixed observation function. It does not yet establish a substantial increase in reasoning difficulty over the previous family. In particular, the six-reading worst case is information-bound tight, the oracle-disclosure costs are additive, and every actual truth has a three-reading certificate.

Proceed with the parent's stated narrowed decision: opt-in ternary `coupled-memory-v1`, preserve the two old families and their defaults, keep R1 at 64 actions, retain `deep_tier_admitted=false` and `empirical_difficulty_calibrated=false`, and do not add a persistent operational stage in this phase. Update the plan's earlier wording about rejecting short-panel candidates: this is provisional experimental admission, not fulfillment of a claim that all short-panel strategies have been eliminated.

## Independently checked facts

| Quantity | Result | What this establishes |
|---|---:|---|
| Programs | 384 = 48 dynamics × 8 encoders | Finite grammar size only |
| Ternary all-future behavior classes | 336 | Acceptance must quotient equivalent programs |
| Reachable states per program | 40, 43, 45, 126, 129, 132, or 135 | Bounded deterministic transition systems |
| Ternary legal-query signatures | 336 | Length 1–4 queries distinguish the all-future classes in this model |
| Ternary greedy adaptive worst case | 6 | Exact probe-only minimax depth: 3^5 < 336 ≤ 3^6 |
| Actual-outcome minimum certificate | Exactly 3 for every one of 336 classes | No one- or two-query certificate exists; a three-query certificate does exist for each class |
| Dynamics disclosed | Greedy worst case 2 for all 48 dynamics | Exact depth, since each known-dynamics prior has 8 distinct behaviors and 3 < 8 ≤ 9 |
| Encoder disclosed | Greedy worst case 4 for all 8 encoders | Exact depth: each prior has 48 distinct behaviors and 3^3 < 48 ≤ 3^4 |
| Simple fixed panel | 9 queries suffice | Upper bound only; no fixed-panel optimality or adaptivity advantage is proved |
| Behavioral equivalence sizes | 288 singleton classes, 48 two-program classes | Uniform-program and uniform-class priors differ |
| Classes spanning encoder spellings | 48 | Unique calibration recovery is not always identifiable, even with unlimited queries |
| Single-query output supports by encoder | All 120 queries permit every ternary output under every encoder | No one query can logically eliminate an encoder under the full dynamics prior |
| Single-query output frequencies by encoder | All 120 queries have encoder-dependent frequencies under uniform dynamics | Statistical calibration information remains; the support result is not probabilistic independence |

The greedy fixed panel found by an independent pair-separation calculation is:

`(0,0,2,1), (0,1,1,0), (2,1,0,0), (2,2,0), (1,0,2,2), (2,0,2,2), (1,0,0,2), (1,2,0,1), (2)`.

Certificate calculation: for each behavioral representative and each legal query, form a bitset of incorrect behavioral representatives eliminated by the actual answer. Exhaustively reject all singleton and pair covers, then find a triple covering every incorrect representative. All 336 representatives passed with exact optimum three. This uses the truth to select the questions and therefore is not an executable three-reading policy for an uninformed player.

The binary and five-symbol results supplied by the parent are also information-bound tight: `ceil(log2(384)) = 9` and `ceil(log5(384)) = 4`. Choosing binary would increase measurement count through bandwidth restriction, not demonstrate stronger reasoning. Six ternary readings translate to a simple 16-action public-policy upper bound under the existing take/configure/probe/build/finish pattern, comparable with the previously observed strong-solver effort. Initial apparatus settings may allow cheaper policies; 16 is not established as an optimal total-action cost.

A bounded 35-second MILP attempt to optimize the fixed panel timed out without improving the elementary lower bound six or the independently verified greedy upper bound nine; **the fixed-panel claim remains only the interval [6,9]**. A six-query fixed panel has not been ruled out. There is no justification yet for claiming that adaptivity is necessary.

## What is genuinely coupled, and what is not established

Material availability clips the flow. Memory affects later flow. Flow and prior destination occupancy update memory. Observation mixes material and memory, including a material-memory product when that encoder bit is enabled. These are actual causal feedback paths, not merely concatenated output fields.

However, this remains a known finite grammar with independent reset-style history queries and a final equivalence-class selection. Matching a small transcript against that grammar can solve it without discovering a reusable physical theory. Joint inference here does not create a demonstrated cost premium: the exact oracle costs 2 and 4 sum to the joint cost 6. This neither disproves coupling nor supports a claim that coupling makes the task substantially harder.

The existing `calibration_only_queries` test is insufficient as a general shortcut qualification. It only detects a query whose answer is constant across dynamics for each encoder. It misses multi-query calibration panels, adaptive preliminary calibration, set-valued distinctions, and probabilistic information. More fundamentally, encoder spellings differ within 48 mission-equivalent classes; a gate that demands exact encoder recovery would falsely report difficulty due to an irrelevant nonidentifiability.

Conservation is sound and useful as a check: there are 15 nonnegative allocations of four packets among three reservoirs and nine memory configurations, hence at most 135 states. Each transition subtracts and adds the same bounded flow. But when every public candidate is conservative, the player is using a disclosed invariant, not empirically discovering conservation. A hidden reservoir could explain apparent local loss; it would not by itself establish a more difficult inference problem.

## Required admission gates for experimental integration

1. **Independent mechanics and complete acceptance.** Implement a plainly written scalar reference transition/observation calculation independently of the optimized evaluator. Exhaustively compare every valid program, reachable state, and input, including the exact order of old/new memory updates. Verify integer types, q_i ≥ 0, sum(q)=4, and h,k ∈ {0,1,2}. Compute full reachable-machine equivalence independently of the bounded query signatures; export distinguishing suffix witnesses for inequivalent pairs. Explicitly define whether the empty history belongs to the acceptance contract. Compare the actual partitions, not only their class counts. Never accept merely because the 120 reader values match unless the independent all-future theorem has been checked for this grammar version.

2. **Public prior and legal-evidence closure.** Derive each T0/T2/T3 posterior from exactly the public disclosure. Audit every valid reader setting and both `probe` and `operate`, plus assembler previews, default apparatus settings, carrier copies, observations, validation failures, and eligible/ineligible finishes. If an action is omitted from the information analysis, prove that its public output is deterministic from already public information. A failed eligible finish must remove the entire accepting class of the attempted build; invalid physical attempts must not exclude a hidden rule. Do not permit live correctness hints through validation or setup.

3. **Separate four costs.** Report actual-outcome certificate bounds, guaranteed adaptive reading bounds, nonadaptive fixed-panel bounds, and total environment-action bounds independently. Label optimized policies as optimal only with a completed lower-bound proof. For probe-only ternary minimax, the class-count lower bound plus the exported six-reading decision tree is sufficient. For fixed panels, use exact pair-separation/set-cover certificates or report an honest interval `[6,9]`. Use a public policy replay as an upper bound, not a lower bound on total actions.

4. **Finish and blind-build accounting.** Include valid build attempts and failed finishes in shortcut reporting. With eight encoders and known dynamics, T2 can guarantee success with at most eight blind build attempts: at most `1 + 3×8 = 25` actions under the simple existing pattern, potentially less with initial assembler settings. Thus T2 does not force measurement within the 64-action allowance. Under T3, 21 attempts fit the same simple 64-action pattern; under a uniform program prior, choosing 21 two-program classes succeeds on `42/384 = 10.9375%`, while a uniform-class prior gives `21/336 = 6.25%`. These are specified-prior baselines, not selected-seed or model failure probabilities. A mixed query/build/finish strategy may do better and must be included before any all-action lower bound is claimed.

5. **Meaningful calibration shortcut audit.** Compare oracle-known dynamics, oracle-known encoder, joint inference, and explicitly defined bounded calibration-first policies. Record whether a short calibration transcript still leaves multiple mission predictions, rather than asking for a unique encoder spelling. Audit fixed panels and adaptive preliminary panels using entire answer tuples. Where parameter labels vary inside an accepted equivalence class, retain sets or quotient labels rather than treating label ambiguity as a required challenge. The single-query support and frequency checks should remain separate named metrics.

6. **Coupling witnesses with mission relevance.** For every admitted structural stratum, exhibit reachable histories with the same current observation but different future predictions, and show a history-dependent distinction relevant to accepted behavior. Verify feedback and observation interactions by ablation against concrete predictions, rather than counting fields or states. Report oracle reductions without claiming superadditivity. If a stronger future tier claims experiment selection matters, require a proved fixed-panel lower bound greater than the adaptive upper bound, or another precise branch-dependent query-value theorem. Current evidence does not meet that stronger gate.

7. **Source-bound, fail-closed proof artifacts.** Bind the proof to the grammar, prior/disclosure functions, legal queries, independent reference, acceptance relation, initial apparatus configurations, action semantics, and the concrete matrix/decision tree. A missing or stale proof cannot inherit stronger qualification from a matching family name. Keep experimental admission separate from any stronger tier. Diversify mechanism structures and observable behaviors; do not count duplicate seeds or equivalent programs as independent diversity.

8. **Preservation and integration.** Retain old family schemas, seeded truths, default CLI behavior, query semantics, proof reports, and R1=64. Replay the shared public policy through the real protocol for all paired T0/T2/T3 and R0/R1 settings. Compare old-family golden behavior, serialization, installed-image execution, and privacy projections. Measure inference failure separately from correctly inferred but uninstalled construction failure; the prior Grok case does not establish scientific reasoning failure.

## Required negative controls

| Deliberate defect/control | Expected check |
|---|---|
| Drop one packet or overdraw an empty reservoir | Independent conservation/nonnegative check fails |
| Use new h where the formula requires old h | Scalar/optimized equivalence comparison fails |
| Hide a transition difference beyond length four | Full-machine acceptance rejects it or query-completeness gate fails |
| Submit an alternate program in one of the 48 paired classes | Accepted despite different encoder spelling |
| Submit an inequivalent program sharing a partial transcript | Finish rejects; posterior removes only its accepting class |
| Make a constant/blank calibration fixture available | Calibration-shortcut metric changes; stronger coupling admission fails |
| Make two or more fixtures jointly reveal calibration, with neither alone revealing it | Multi-query shortcut check catches it |
| Remove memory feedback or replace memory with the current observation | Predictive/history witness or ablation gate fails when behavior collapses |
| Reuse one nine-query fixed panel for all truths | Every behavior resolves; report this baseline rather than calling it an adaptive strategy |
| Enumerate T2 builds without any readings | Wins within the reported ≤25-action baseline |
| Wrong eligible finish, followed by repair | Binary feedback, correct class exclusion, recoverable state, exact replay |
| Finish with no installed carrier or wrong physical eligibility | No hidden class is incorrectly excluded |
| Probe assembler or use a stock copy | No new facility-truth signal beyond the documented reader/finish channels |
| Change grammar, query list, defaults, or acceptance after producing proof | Source/proof mismatch blocks qualification |
| Expose private seed/program/proof in public JSON, evidence, logs, or errors | Privacy test fails |

## Bounded improvement recommendation

The immediate useful improvement is **qualification**, not another parameter or smaller sensor alphabet: export the complete ternary decision tree, exact three-reading certificate witnesses, explicit oracle ablations, fixed-panel baseline, and finish-aware action accounting. This makes the new family materially more trustworthy and reusable without pretending it is an empirically harder benchmark.

Do not add a persistent steering stage now. Identifying a model from reset queries and then steering a known initial state mostly appends ordinary planning. A substantive experimental/operational coupling would require the measurements to act on the same hidden goal-relevant state, making information gathering change later options. That changes P0 and requires belief-state planning, synchronization/reset-word audits, open-loop success baselines, and new goal semantics. It is a reasonable separately tagged follow-up family if requested, not a small fix for this family.

Keep shared machinery narrowly reusable: finite hypotheses, measurement partitions, acceptance masks, posterior updates, and proof/search utilities belong in shared discovery code once exercised by multiple families. Reservoir transitions, encoder syntax, all-future equivalence construction, conservation witnesses, and domain evidence belong in the coupled-memory adapter. Avoid encoding reservoir or memory semantics into the generic engine.

## Remaining uncertainty

No fresh live model evaluation was run or authorized. This review does not establish cognitive hardness, a model failure rate, fixed-panel optimality, or an optimal total-action bound. Those limitations are compatible with experimental integration and incompatible with stronger claims. The parent remains responsible for reviewing the implementation and checking the negative controls after integration.
