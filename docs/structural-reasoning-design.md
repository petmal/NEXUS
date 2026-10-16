# Structural reasoning and reusable qualification: design

Status: implementation in progress, 2026-10-16. Baseline: feature branch
`feat/theory-prior-axis`, commit `09fe7bb`. The user approved the recommendations
from the complete 13-22-12 real-model run. This document and its implementation
ledger are durable checkpoints, not claims of completed validation.

## Product purpose and evidence

NEXUS should measure investigation, revision of explanations, and the ability to
use those explanations to produce a concrete successful state. The latest run
won all 70 completed missions: all 42 dynamics investigations identified their
entire hidden world before submission. More readings separated efficiency but
not eventual success. Existing families remain valuable controls.

The north star is a useful, falsifiable increase in structural reasoning burden
at moderate planning/resource settings. Neither an observation lower bound nor
a longer trace establishes cognitive depth or an LLM failure rate.

## Approved work and boundaries

1. Preserve and document the current matrix as a control/efficiency benchmark.
2. Cache seed-independent dynamics qualification work and add scoped operator
   timings. Preserve laws, public evidence, seeds, budgets and certificate meaning.
3. Improve the public-information reference policy to account for specimen reuse,
   existing histories, apparatus settings and actual action costs. Keep the old
   complete witness as a fallback and distinct upper-bound reference.
4. Prove a stronger structural reasoning PoC, then integrate it as an explicitly
   experimental, separately versioned ontology through existing interfaces.
5. Audit plausible shortcuts and produce a small, mechanically preflighted pilot
   matrix. Empirical model calibration remains a subsequent operator task.

No main merge, paid model evaluation, public MindTrial changes, provider settings
changes, new mandatory experiment order, external Python access, or change to
victory-receipt validation is included. No claim that half of models will fail.

## Fixed invariants

- Canonical deterministic state, exact goal checking, live receipts and replay.
- Explicit stable action syntax and complete bounded public law prior.
- Private seed, selected truth, solutions and inference telemetry remain private.
- Invalid actions are atomic; physical preparation requires ordinary operations.
- Experiments and guesses remain legal in arbitrary order. Qualification includes
  informative errors/failed finishes where a claim depends on them.
- New graphs use data and trusted primitives, never executable source/eval.
- Existing ontologies, serialized episodes, action costs and defaults remain
  supported. A new family does not retroactively reinterpret earlier T/D levels.

## Phase A: reusable dynamics proof work

A checked artifact may hold immutable observation partitions and full-prior
policy-bound data. It must be bound to the complete semantic inputs of its
computation, have a bounded schema, and be exhaustively regenerated/compared in
CI. Missing or stale artifacts must not silently weaken a certificate. Runtime
fallback may recompute the same proof; corrupted data must never be trusted.

Cold worker processes must benefit without sharing session state. Public episode
serialization and current fixed budgets must remain identical except random
nonce/secret fields. The artifact is operator/package data, not public evidence.

Timings distinguish artifact validation/load, partition compilation, policy-bound
construction and episode construction. Existing terminal-only metrics stay out
of live play.

## Phase B: cost-aware reference policies

The current query-minimizing witness is a valid upper bound, not an optimal plan.
A second strategy accounts for extending a prepared history, changing a readout,
reusing current apparatus settings, fresh specimen acquisition and movement.
It receives only player operations and public evidence. It must win/replay all
1,944 worlds within the existing budget; it may use a proved-safe continuation
or select the legacy policy before play when its bound is better. Do not start
an unbounded greedy strategy and claim the legacy guarantee still applies.

The policy and metrics must distinguish full-world information gain, target
information gain, cost, and discretionary confirmation after identification.
Lower-bound qualification continues to cover the entire legal observation space,
not merely the policy's chosen subset.

## Phase C: structural reasoning PoC and admission gate

Candidate construction: shared compositional mechanisms across experimental
contexts, with a locally adequate model that fails under a discriminating
intervention and whose selective correction changes joint mission predictions.
The prior must expose primitive operations/composition bounds rather than only a
short menu of complete equations. Goal success remains a concrete physical state.

Before implementation, a bounded executable PoC and independent review must
resolve the exact grammar, full prior, control levels, query space, mission and
public witness. Required evidence:

- deterministic arithmetic independently crosschecked;
- complete admitted prior and seed sampling, with no hidden seed filtering;
- target-relevant ambiguity under declared restricted experiment classes;
- counterexamples to untreated tomography, local-only fitting, cancellation,
  independent-output fitting and other proposed shortcuts where applicable;
- sound quantitative identification/guess bounds with explicit scope;
- a feasible public-information strategy through ordinary actions;
- sensitivity of joint repair to shared mechanisms, not merely extra independent
  slots or gratuitous arithmetic;
- all controls available immediately; no scripted revision or stage unlock.

A sequential mental process cannot be enforced. An agent may infer the final
model immediately. A revision claim must concern observable predictive
constraints or submitted operational behavior, not undocumented mental states.
If a proposed construction fails its gate, record the negative finding and
revise the candidate before integration; do not relabel it deep.

The concrete construction and measured gates will be appended here after the
PoC. Its release is experimental pending independent real-model calibration.

## Decision ledger

- Preserve existing behavior. Reason: compatibility is a repeated user constraint;
  evidence: old episodes and latest controls are useful baselines. Invalidated
  only by an explicitly approved behavior change, not by faster reference plans.
- Optimize shared mathematics before parallelization. Reason: cold generation is
  dominated by repeated qualification independent of seed. Reassess if profiling
  after caching leaves a meaningful parallel workload.
- Separate formal and empirical claims. Reason: all qualified dynamics worlds in
  the latest matrix were solved. A proved certificate does not predict failures.
- Keep the strongest PoC opt-in. Reason: uncalibrated structural difficulty must
  not replace stable worlds or silently redefine existing numeric axes.
- No paid model calls. Evidence: approved workflow reserves real-model evaluation
  for the user. Offline proof/public-policy tests precede the pilot matrix.

## Admitted concrete PoC

Implemented `compositional-repair-v1` per the independent finite design report
`structural-reasoning-proof.md`. Three independently selected primitive gates
compose over one of three shared graphs. One gate changes in context 1; a single
four-trit applied treatment must null two inputs in each context. All 615 solvable
grammar worlds are admitted; 81 repair vectors may have overlapping winning sets.
There are 486 normalized queries. Every query/trim/context is available immediately.

The exact two-query one-repair success maximum is 202/615 under a uniform admitted
world prior. A public-information witness wins in at most seven readings. Twelve
worlds have a passive-observation obstruction; this is a targeted-fixture claim,
not universal intervention necessity. Live acceptance/observation assumptions and
costs are documented in `compositional-live-conformance.md`. The new eight-cell
pilot is separate from the retained ten-cell control matrix.
