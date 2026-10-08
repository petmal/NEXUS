# Theory-prior axis (T) — design and proof plan

Status: T0/T1 implemented on `feat/theory-prior-axis`, based on integration
commit `cd69107f02af30c10464b85b47fa343a3f96aaef`. This document retains the broader
research ladder; current runtime scope and measured gates are recorded in
`theory-implementation-progress.md` and `theory-next-pass-results.md`. D4/T1 is
now qualified experimentally; T2 has a bounded-correction PoC but T2+ runtime
profiles are not enabled.

## 1. Motivation

NEXUS currently tests causal discovery while giving the player a strong scientific prior:
`facility_manual.txt` discloses the complete finite grammar from which each hidden machine law is
drawn. The player must identify mission-relevant behavior within a known theory class.

The proposed T axis varies the amount and quality of *prior theory* available to the player while
keeping controls, observations, goals, and hidden execution deterministic.

The intended scientific progression is:

- apply/select within an explicit theory;
- derive a law from more primitive theory;
- work with an effective/approximate theory and discover its correction;
- reason from incomplete structural knowledge;
- eventually perform black-box empirical discovery with minimal assumptions.

This axis is orthogonal in intent to:

- D: how hard it is to acquire mission-relevant information *given the public theory prior*;
- P: how hard it is to plan physical/dependency execution;
- R: how much action slack is provided above the exact guaranteed policy.

T must not be implemented as prose-only concealment while the private solver continues assuming
knowledge the player was not given.

## 2. Central formal requirement

Every theory level T defines a public prior `P_T` and an evaluator hypothesis class `H_T`.

The same structured source must generate both:

1. player-facing theory material; and
2. the admissible hidden-law class used by evidence planning, discovery analysis, and exact
   belief-policy qualification.

The selected true machine law must satisfy:

```text
true_law ∈ H_T
```

After public evidence E and observations O, the evaluator's belief is:

```text
B_T(E,O) = { h ∈ H_T : h is consistent with E and O }
```

No private DSL restriction may be used by the policy solver unless that restriction is represented
in the public theory prior.

### Why this is mandatory

If T merely deletes parts of the manual but the solver keeps the current 288-rule catalogue, the
reported "guaranteed" policy can exploit knowledge unavailable to the evaluated model. In
particular, an R2 budget could then be exactly sufficient only for an oracle that knows the secret
benchmark DSL. That would violate the semantics of both T and R.

## 3. Mission equivalence, not exact theory recovery

NEXUS should not require the player to identify the exact private AST when several theories are
behaviorally equivalent for the mission.

For a belief B and reachable context set C, define mission equivalence relative to the exact
policy problem: two hypotheses need not be separated if every relevant interaction produces the
same observable branches and admits the same mission-winning continuations.

The existing belief solver already implements the useful operational version of this principle:
hypotheses are partitioned by observable outcomes, and a policy only needs to narrow belief enough
to guarantee success.

Therefore T difficulty is not "name the hidden equation." It is "acquire/derive enough predictive
structure to control the world successfully."

## 4. Proposed levels

### T0 — explicit finite grammar (backward-compatible)

Public prior:
- current complete facility-law grammar;
- exact condition forms;
- exact true/false branch transformation templates;
- explicit invariances (no dependence on pattern, room, turn, history).

Hypothesis class:
- current 288-rule catalogue for the generic D0-D4 family;
- the current explicit four-member D5 mission family plus disclosed calibration-machine laws.

Expected implementation impact:
- none beyond recording `theory_level=0`;
- all existing episodes remain semantically identical.

Purpose:
- compatibility/control condition.

### T1 — derivational structural theory

Scientific analogue:
- known primitive laws/allowed mechanisms, but the mission-specific composite law must be derived.

Public prior:
- deterministic, stationary, memoryless machines;
- branch selection may use one shape predicate and phase parity through a bounded Boolean
  composition;
- branch effects are composed independently from primitive value, polarity, and orientation
  operations;
- shape and pattern are preserved;
- no enumeration of the current four true-branch and four false-branch macro templates.

Initial bounded candidate class for PoC:
- current 18 condition predicates;
- each branch independently chooses:
  - value operation: identity, +1, +2, +3, ×2, or ×3 modulo 11;
  - polarity: unchanged or toggled;
  - orientation: rotate 0, 1, 2, or 3 quarter turns.

Raw syntactic count:

```text
18 × 48 × 48 = 41,472
```

Behavioral deduplication over the current finite experimental domain gives 27,120 distinct
input/output laws in the initial PoC analysis.

The true T0 law family is a subset of this T1 class.

Purpose:
- test derivation/model construction from primitives rather than selection among enumerated macro
  laws.

### T2 — effective theory with bounded corrections

Scientific analogue:
- an effective theory known to work in a calibrated regime, analogous to using a lower-order or
  limited-domain model before encountering a correction.

Public prior contains:
- an explicit effective model E;
- a mechanically defined validity/calibration region V where E is guaranteed correct;
- an explicit statement that behavior outside V may contain one bounded correction drawn from a
  disclosed correction primitive class;
- invariants that remain exact (determinism, stationarity, memorylessness, preserved fields).

Private true law:

```text
F = E + C
```

where C is generated from a finite correction DSL and is inactive on V.

Generation must prove:
1. all supplied "established" measurements in V agree with E;
2. the mission reaches at least one context outside V where at least two admissible corrections
   make different mission-relevant predictions;
3. an affordable experiment can distinguish enough correction hypotheses to guarantee success;
4. the selected true law is in the disclosed correction class.

The public theory must never falsely state that E is universally exact. It should say, in effect,
"this model is established in regime V; extrapolation outside V is unverified."

Purpose:
- test recognition of model limits, anomaly-driven experimentation, and theory refinement.

### T3 — incomplete structural theory

Scientific analogue:
- known invariances/dependencies, but no useful closed-form law.

Public prior initially gives only:
- deterministic, stationary, memoryless dynamics;
- exact observable variables that the law is allowed to depend on;
- exact fields guaranteed invariant;
- a bounded output/effect family, but no condition/formula structure.

The hypothesis space should be represented behaviorally rather than by enumerating every AST.

A first T3 scope should use a small context partition, for example shape × phase parity. Each cell
maps to one bounded branch effect. The solver can maintain uncertainty per context cell and merge
cells only when public structure requires correlation.

Purpose:
- test empirical model construction with weak theory while keeping exact public-prior semantics.

### T4 — black-box empirical law (future gate)

Scientific analogue:
- very little prior theory beyond reproducibility and observable state.

Public prior:
- deterministic;
- stationary;
- memoryless;
- explicit observable state/action semantics;
- minimal invariant information only if required for tractability.

No cross-context formula/DSL is disclosed.

A formal T4 hypothesis class is the set of all deterministic maps over the declared finite context
and output domains. This set is astronomically large and must **not** be enumerated. A future
solver would represent it symbolically: unobserved contexts have unconstrained output sets;
observing/probing a context fixes its output.

Important consequence:
- without structural generalization, some existing D meanings collapse. For example D1
  "infer mission outcome without a direct-context example" is generally impossible under a fully
  unconstrained function prior.
- D4/D5 experiment-value structure also changes because an observation from one context need not
  constrain another.
- therefore T4 is not part of the first implementation unless a new symbolic solver and a
  supported D×T profile matrix are proved.

T4 must not use the private generated DSL as a hidden solver prior.

### T5 — hidden ontology (out of initial scope)

Variables themselves, dependency structure, or latent state may be unknown. This requires a new
representation-learning/latent-state layer and is explicitly deferred until T0-T4 calibration.

## 5. Structured theory contract

Do not make T semantics exist only in prose.

Introduce a typed theory-prior specification that can generate the public theory attachment and
the evaluator hypothesis class. Conceptually:

```text
TheoryPriorSpec
  level
  deterministic
  stationary
  memoryless
  input_dependencies / unknown
  invariant_fields
  condition_primitives / unknown
  effect_primitives / unknown
  structural_bounds / unknown
  effective_model / optional
  validity_region / optional
  correction_primitives / optional
```

The exact schema should remain small and reflect only implemented levels.

Player-facing outputs:
- `theory.json`: canonical machine-readable public contract;
- `theory.md` or `facility_manual.txt`: natural-language rendering generated from the same
  object.

Qualification must reconstruct the expected public rendering from the structured contract so prose
cannot drift from solver semantics.

Private metadata may store richer compilation data, but no undisclosed prior restriction may enter
belief-policy qualification.

## 6. T-aware evidence planning

Evidence is conditional on the public theory class.

For each machine, evidence planning must start from `H_T`, not from the T0 catalogue.

Given candidate class H, selected law h*, mission context m, and desired D profile, choose evidence
E such that the existing D semantics hold under H conditioned on E.

Examples:

D0:
- direct mission context is demonstrated;
- evidence leaves one mission-relevant behavior (and, where required, one behavioral hypothesis).

D1:
- no direct mission-context row;
- all evidence-consistent public-prior hypotheses predict the same required mission outcome;
- exact minimum guaranteed probes = 0.

D2:
- no direct mission-context row;
- at least two mission-relevant predictions remain;
- exact minimum guaranteed probes = 1.

D3:
- both stages meet the required ambiguity under the *joint correlated* T-aware hypothesis set;
- exact minimum guaranteed probes = 2.

D4/D5:
- experiment-value proofs must use the T-aware hypothesis set.

Do not preserve evidence row count as an invariant. Broader theory priors may legitimately require
more historical evidence to hold D fixed.

## 7. Pairing semantics

For a fixed seed and D/P/R, changing T should preserve whenever possible:

- selected hidden laws;
- initial intrinsic artifacts;
- target/goal;
- topology and role placement;
- resource profile mechanics.

Evidence may differ because D is defined relative to the public prior.

This gives a useful interpretation:

```text
D = residual active-discovery burden after conditioning on theory + supplied evidence
T = strength/form of prior theory needed to reach that residual state
```

Record a stable theory/scenario family ID so analysis can verify pairing.

A secondary research mode may intentionally hold evidence fixed across T to measure raw prior-value
degradation, but that should not be the default D-normalized generator because D would cease to
have stable semantics.

## 8. Exactness proofs

### Lemma A — belief soundness

If H_T is exactly the class admitted by the public theory contract and evidence filtering removes
exactly hypotheses inconsistent with public observations, then every hidden world compatible with
the public information remains in B_T.

Proof: construction of H_T covers every law permitted by the contract; filtering is equality of
deterministic observable outcomes only. Therefore no compatible law is removed.

Required tests:
- selected hidden law always remains;
- randomized public-prior laws are never incorrectly filtered;
- laws violating one disclosed invariant never enter H_T.

### Lemma B — theory monotonicity where priors are nested

For T levels with H_a ⊆ H_b under identical public evidence, the minimum worst-case guaranteed
policy cost satisfies:

```text
C(H_a) <= C(H_b)
```

Proof: every policy guaranteed over H_b is also guaranteed over its subset H_a. Therefore the
optimum over H_a cannot be more expensive.

This should be mechanically checked for paired T0/T1 worlds when evidence is intentionally held
fixed in proof fixtures.

Note: D-normalized production evidence can differ, so monotonicity is not required across generated
episodes with different evidence.

### Lemma C — D semantics are theory-relative

The current DiscoveryBelief/policy solver remains valid if its initial hypothesis set is replaced
with B_T(E), because probe/operate partitioning depends only on deterministic hypothesis-specific
outcomes. The solver does not require hypotheses to originate from today's 288-rule catalogue.

Proof obligation:
- refactor no transition semantics;
- only candidate construction changes;
- tiny exhaustive fixtures compare the generalized solver with explicit enumeration.

### Lemma D — T2 effective-theory honesty

For every generated T2 episode:
- E(x) = F(x) for every x in declared validity region V;
- at least one mission-reachable x outside V has multiple admissible correction predictions before
  the required experiment;
- selected F belongs to the disclosed correction family.

Thus no observation inside V contradicts the public effective theory, and the benchmark tests
extrapolation/theory refinement rather than deception.

### Lemma E — R2 fairness

R2 is valid only when its exact guaranteed-policy baseline is computed over the same H_T disclosed
to the player.

If a T level lacks an exact public-prior solver, R2 must be rejected for that T level rather than
silently using a stronger private prior.

## 9. Efficiency design

### Behavioral canonicalization

T1 contains many syntactically distinct laws with identical behavior over the finite NEXUS domain.
Candidate generation should canonicalize by deterministic behavior signature and retain one
representative AST per equivalence class.

Initial PoC result:
- 41,472 raw T1 syntax combinations;
- 27,120 distinct behaviors over the existing experiment domain.

The player need not know this count; it is evaluator implementation detail implied by the public
finite primitive contract.

### Precomputed signatures

For finite T0/T1 classes, precompute/cache an experiment-major behavior matrix:

```text
signature[experiment_id][hypothesis_id] -> observable output
```

Evidence filtering becomes integer/bitset intersection instead of repeatedly interpreting every
AST.

### Bound solver hypotheses after evidence

The exact belief solver should continue operating on a deliberately small evidence-conditioned set.

Generation requirements should include a per-machine candidate ceiling before invoking the
full contingent policy solver.

For multi-machine families, enforce the product bound explicitly, e.g. if the existing solver
limit is 256:
- two independent stages may target <= 8 or <= 12 candidates each depending on correlation;
- never rely on accidental product size.

If sufficient D ambiguity cannot coexist with the candidate ceiling, reject/reroll the causal
family rather than increasing the exact solver limit blindly.

### PoC observations

A local behavioral enumeration using the current experiment pool found:

- T0 has 288 rules.
- T1 PoC has 41,472 syntactic / 27,120 behaviorally distinct rules.
- Existing T0 D0 evidence, when interpreted under T1, often leaves multiple hypotheses
  (sample median 4, observed maximum 18), proving evidence must be T-aware.
- Existing T0 D1/D2 evidence can leave far more T1 predictions, again proving manual concealment
  alone is semantically invalid.
- Replanning evidence against the T1 class can still identify a T1 behavior in roughly four rows
  for sampled D0 contexts.
- Sampled T1 D2 constructions can preserve mission ambiguity while reducing the candidate set to
  tens rather than thousands.
- T1 D1 is not possible for every selected law/context without direct evidence, so generation must
  reject unsuitable causal families rather than weaken the D1 guarantee.

These are feasibility observations, not benchmark calibration results.

## 10. Interaction with D4/D5

Do not hard-code T only into legacy D0-D3.

D4 and D5 currently construct specialized experiment-value scenarios and sometimes custom
candidate families.

The generalized interface should let each discovery family provide:

```text
selected true law(s)
public TheoryPriorSpec
candidate hypotheses under that prior
evidence
experiment domain
```

Then the same exact policy solver can qualify experiment value.

However implementation should first prove T0/T1 on D0-D3. D4/D5 integration is a separate gate
because their carefully constructed experiment-cost inequalities must remain true under the
broader T1 prior.

## 11. Supported-profile policy

Never pretend the four axes are a full Cartesian product.

Each implemented T level declares supported D levels. Generation rejects unsupported combinations
with a clear error.

Initial target:

```text
T0: D0-D5  (current)
T1: D0-D3 first; D4-D5 after dedicated proof
T2: start with D1-D3 or a dedicated anomaly profile after PoC
T3: start with D2 single-machine only, then expand
T4: unsupported until symbolic solver proof
```

P0-P3 and R0-R2 may be enabled only after the T/D combination has an exact public-prior policy
solver. In particular R2 is blocked whenever exact theory-relative minimax cost is unavailable.

## 12. Public/private leakage tests

For every T:

- public files must not contain the selected private AST;
- public text/JSON must not contain restrictions omitted by the selected theory level;
- candidate counts, exact hypothesis IDs, reference policies, and generation metadata remain
  private;
- lower-T manuals may contain information intentionally absent from higher T;
- higher-T variants must not leak lower-T content through description strings, evidence filenames,
  error messages, schema descriptions, or CLI summaries.

Add golden/structural tests that compare public artifacts across paired T levels and assert the
allowed information delta.

## 13. Research grounding

Relevant external benchmark lessons:

- NewtonBench (ICLR 2026) evaluates interactive recovery of altered physical laws and reports steep
  degradation with system complexity and very small observational noise. Its design supports
  separating law complexity from environment/system complexity.
  https://arxiv.org/abs/2510.07172

- SCILAWS-BENCH separates real-record discovery from active recovery of synthesized hidden laws
  and reports that predictive fit can diverge from scientific validity.
  https://arxiv.org/abs/2609.01552

- ARC-AGI-3 removes explicit rules/instructions and measures exploration plus construction of an
  internal world model in novel interactive environments.
  https://arxiv.org/abs/2603.24621

NEXUS should borrow the *capability target*—interactive model discovery—without abandoning its
distinctive strengths: procedural laws, exact symbolic execution, exact success, explicit
public/private separation, and mechanically qualified policies.

## 14. Proof/PoC gates before implementation

Do not begin production implementation until all of these are satisfied.

### Gate 1 — T1 finite-class feasibility
- formal T1 grammar written down;
- exhaustive generator enumerates/canonicalizes it deterministically;
- selected T0 laws are proven members;
- behavior-class count is bounded and reproducible;
- signature precomputation is acceptably fast/memory-bounded.

### Gate 2 — T-aware evidence feasibility
Across a broad seed/mission-context sample:
- D0 can be produced with unique mission behavior;
- D1 can be produced without direct-context evidence and with zero guaranteed probes;
- D2 can preserve >=2 mission predictions while bounding candidates;
- D3 can bound the joint hypothesis product under the exact solver ceiling.

Record rejection rates. Reject the design if family acceptance is too low or biased toward a tiny
subset of laws.

### Gate 3 — exact-policy equivalence
On tiny T1 fixtures:
- generalized candidate construction + current compressed belief solver equals exhaustive
  enumeration;
- witness replay remains ordinary-action exact;
- R2 budget equals exact T-aware minimax cost.

### Gate 4 — pairing
For fixed seed across T0/T1:
- true laws/topology/goals remain paired;
- only theory/evidence differences permitted by the profile change;
- scenario IDs prove pairing.

### Gate 5 — T2 correction-family feasibility
Before implementing T2 production:
- define one small correction DSL and validity-region grammar;
- prove effective law and true law agree throughout V;
- prove mission-relevant disagreement outside V;
- measure evidence-conditioned hypothesis sizes and solver runtime.

### Gate 6 — T3/T4 symbolic feasibility
Do not implement T3/T4 on the enumerative solver merely by raising limits.
Prototype symbolic context uncertainty first and demonstrate exact agreement with explicit
enumeration on tiny domains.

## 15. Decision after current design study

The architecture is considered robust enough to proceed with an execution plan for T0/T1 and the
shared theory-prior infrastructure.

T2 is sufficiently specified conceptually to include as a gated second implementation milestone,
but should not be coded until its correction-family PoC passes Gate 5.

T3/T4 are deliberately not approved for production implementation yet. Their public priors are
scientifically coherent, but efficient exact policy qualification needs a symbolic belief backend
that has not yet been proved.

T5 hidden ontology remains future work.

