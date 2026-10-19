# Goal-sensitive qualification and staged repair

Status: implemented; independent proofs and review passed. Base: `ca471a6702a4da8be9023b4846acef7cc24b2ae6`,
branch `feat/theory-prior-axis`. Keep this document and implementation ledger
current so another session can resume without repeating discovery.

## Purpose and approved scope

Implement the recommendations following the history pilot: qualify the information
needed for an actual winning decision; broaden the physical goal so unresolved
law differences matter; and make earlier findings useful for later experiment
selection. Preserve all existing ontologies and legal shortcuts. No paid model
calls, changes to MindTrial, merge to main, or forced branch update.

Success means a usable opt-in family, complete public contract, independent proof,
exact post-run evidence classification, a preflighted diverse matrix, and unchanged
legacy behavior. A reference policy is an upper bound, never a depth proof. A
mathematical information bound is not a prediction of model failure.

## New opt-in family: staged-repair-v1

Three physical exit seals have public tags u=0,1,2. Each has three hidden loads.
Arithmetic is modulo three. Offline proofs also examine one/two-mechanism controls.
Mechanism i is constructed from shift k_i in {0,1,2} and exponent e_i in {1,2}:
F_i(u)=(u+k_i)^e_i mod 3. Its route r_i=(k_i+e_i-1) mod 3.
Every combination is possible; no truth-dependent solvability or hardness filter.

A reader configured with [stage,carrier] returns F_stage(u) iff carrier is zero
at stage zero (and throughout the independent D3 profile), or equals the previous
mechanism's route at later stages in D4. Otherwise
it returns zero. Zero does not disclose whether the reader was on the active route.
All legal stages/carriers/tags remain available at all times. Reading reconstructs
a fresh baseline COPY for the specimen's public tag; it does not measure remaining
load and never mutates a mission seal. Thus a result can guide the next setting,
but the interface does not mechanically enforce an investigation order.

A trimmer configured with three doses, then operated on a seal, adds those doses to
its public cumulative treatment vector d. The actual remaining loads are
F_0(u)-d_0 and F_i(u)-d_i-r_(i-1)*d_(i-1) for i>0. Earlier corrections disturb
later loads. Repeated doses add modulo three; anneal restores the baseline by
clearing doses. Probe previews only public changes, never a hidden residual or
accept/reject result. The same ordinary actions work on survey stocks. Finish
requires all three actual seals carried in array and every hidden load zero.
Finish gives binary feedback and may be retried; no forced unique-theory report.

This changes the mission type deliberately; the existing history family remains
available. This family measures dependency-aware experiment selection and coupled
repair, not noncommuting pulse-history tracking.

T0/D0 supplies exact laws and the complete repair table; T2 supplies exponents
but hides shifts; T3 hides both. T1 remains unsupported pending a separate
state-estimation design. D3 has independently accessible reader contexts; D4 has
dependent reader contexts. Both retain the same coupled physical repair and truth
for a matched seed. D0 is the linked-world execution control. Other D values fail
clearly. These are explicit axes-v2 family profiles, not v1's exact probe-count
guarantees. Numeric labels are not comparable across ontologies without certificates.
P0/P1 and R0/R1 retain one/two-room and unbounded/moderate-budget meanings. Budget
is based on the full T3 reference upper bound plus twenty recovery actions, including
for controls. A diagnostic +6 profile is supported through the registry capability.

## Critical proof obligations (before runtime integration)

1. Exhaustively check all 6^n worlds for n<=3. Full three-seal repair signatures
   must be injective: a shared successful repair cannot hide unresolved mechanism
   differences. Prove constructively by induction over the triangular coupling.
2. Exhibit lower-coverage missions where distinct laws share a repair. Include
   the six-world teaching example and seed 239's 32-world common procedure as
   regression counterexamples to parameter-count-based qualification.
3. Build a public-only adaptive policy (at most two readings per stage). Verify
   every branch, and compare with a globally fixed panel using exact pair-separation
   constraints. Publish a checkable lower-bound witness and sufficient panel.
   Initial independent scalar proof: linked fixed-panel minima 3,10,15 versus
   adaptive upper bounds 2,4,6 for one, two, three mechanisms. The three-mechanism
   independent profile has fixed minimum 9. Hidden-route zeros prevent a naive
   13-query panel from resolving all worlds; the exact checker rejects it.
4. Cover all feedback channels, including legal failed finishes. A relaxed
   information game allows free setup and arbitrary repairs, bounds each reader
   to three outcomes and each successful finish to one mission signature. With k
   feedback actions it can cover at most 3^(k-1) signatures. Derive conservative
   success ceilings under the explicit uniform conditional prior. This includes
   guessing/repeated finishes and is not an exact total-action minimax result.
5. Separate worst-case prior guarantees, per-world achieved policy length, fixed
   panel cost, and human/model reasoning difficulty. Do not call any profile an
   unavoidable-deep tier without a separately satisfied admission gate.

## Architecture and performance

Use the existing ontology registry and payload schemas. New modules own schema,
laws, inference, evidence, policy, generation, runtime and qualification. Engine
transactions, charging, replay and receipts remain authoritative. A public-only
mission tracker follows all three seals' accumulated doses and eligibility.

Use immutable compiled response/decision tables and integer posterior bitsets;
cache by public profile, never by selected truth. Generation must not run minimax,
search for hard seeds, import optional frameworks, or materialize large transcript
products. Offline proof checks use an independent scalar implementation.

Qualification reports are source-bound, fail closed, and private. Terminal logs
separate mission resolution, law resolution, reader calls, construction, failed
finishes and actual adaptive path length. Active player responses contain none
of these diagnostic hints. Full public schema and walkthroughs distinguish baseline
copy readings, cumulative doses and unobserved current loads.

## Risks and limits

The proposed laws are small and the public prior is enumerable. Models may solve
them readily. A fixed panel remains legal and may fit the moderate action budget.
The proofs must report that, not increase R pressure to manufacture a T/D result.
T2 disclosures alter the conditional prior and must be qualified separately.
Seed mappings and matrix selection are operator information, not player evidence;
claimed uniform success bounds do not automatically apply to a hand-picked matrix.

Decision: implement an additive versioned family rather than mutate history-v1.
Reason: histories, goals and receipts from existing runs must remain reproducible.
Invalidates if: proof finds mission aliases or runtime observations violate the
claimed finite information interface; stop admission and repair the design first.
