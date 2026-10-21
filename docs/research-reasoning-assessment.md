# Scientific-reasoning challenges: assessment and NEXUS coverage

Reviewed 2026-10-21. This assesses the supplied ten-part essay against primary
research and the completed discovery pilot. It is not evidence that a particular
current model must fail a new family.

## Assessment

The failure categories are useful. The repeated explanation “trained to predict
text, therefore unable to reason/check probabilities/discover laws” is too strong.
A training objective is not a capability measurement. Separate a standalone model
from an agent with search, numerical tools and formal verification; separate lack
of a correctness guarantee from demonstrated inability. A model may express exact
mathematics or a probability distribution, even if its unverified answers are
unreliable. Multimodal models also cannot be dismissed as primarily text models.

Recent primary evidence supports a more specific conclusion: success on familiar
science or bounded hypothesis selection need not transfer to finding an adequate
representation, falsifying a plausible explanation, or closing the loop from
inference to a correct operational result.

- **DiscoverPhysics**, v2, August 2026: agents investigate 22 deliberately unusual
  simulated worlds using trajectories and submit executable laws. The authors
  report that their strongest agents pass about half and struggle with latent
  structure. This is a promising comparison for NEXUS, but different models,
  tools, budgets, curated worlds and partially judged explanation scores prevent
  direct score comparisons. [Paper](https://arxiv.org/html/2605.26087v2)
  Its appendix separates inadequate hypothesis classes from numerical-integration
  and implementation errors. The failure attribution is LLM-mediated, not a
  causal intervention proving why a model failed. More experimental rounds also
  helped different models differently; extra budget did not uniformly repair
  conceptual errors. These distinctions reinforce our separation of inference,
  execution and resource failures.
- **REFUTE**, February 2025: finding counterexamples to incorrect competitive
  programming solutions was substantially harder for the tested agents than
  solving the associated problems. Its o3-mini-era numbers are not forecasts for
  Astra. It motivates explicit falsification tests rather than relying on a
  correct final answer as proof that alternatives were properly rejected.
  [Paper](https://arxiv.org/abs/2502.19414)
- **Scientific Discovery Evaluation**, v2, May 2026: scenario-level hypothesis,
  experiment and result reasoning exposes gaps not captured by ordinary science
  question answering. Its variation across scenarios cautions against treating
  “scientific reasoning” as one skill. [Paper](https://arxiv.org/abs/2512.15567)
- **Mathematical exploration and discovery at scale**, v3, December 2025:
  LLM-guided evolutionary search improved constructions for several problems
  among 67 studied, with additional proof systems in some cases. This refutes
  blanket claims that LLM-based systems cannot produce novel correct mathematics;
  it does not establish autonomous general physical theory discovery.
  [Paper](https://arxiv.org/abs/2511.02864)
- **DiscoveryWorld**, 2024: a useful predecessor for evaluating the full
  experimental cycle and intermediate scientific behavior. Its older baseline
  results cannot establish the weakness of current models.
  [Paper](https://arxiv.org/abs/2406.06769)

## Which claims have we actually tested?

| Essay category | NEXUS coverage so far | Assessment / remaining gap |
|---|---|---|
| 1. Long mechanistic chains | Multi-stage repair, assembly, history, finite-memory prediction | Substantial bounded coverage; symbolic depth and state count did not reliably create cognitive difficulty. Cross-scale representation changes remain largely untested. |
| 2. Exact symbolic mathematics | Small modular/integer equations and finite constructions | We test exact execution, not long integrals or proof derivations. Larger arithmetic risks testing bookkeeping rather than science. |
| 3. Experimental design and instrumentation | Calibration offsets, loading, informative vs uninformative probes, joint observations | Directly tested. Many disclosed priors permit compact census or elimination strategies; realistic engineering feasibility and noisy systematic estimation are not covered. |
| 4. Abduction and counterfactual tests | Bounded alternatives, interventions, provisional notes and repair | Partly tested. Finding a counterexample when its location/representation is unknown is a stronger target than choosing among listed formulas. |
| 5. Multimodal integration | Structured tool outputs and numeric tables | Raw plots, images, waveform interpretation and metadata reconciliation are largely untested. These would introduce a separate perception factor. |
| 6. Probabilistic inference and uncertainty | Exact compatible-world sets and robust constructions | Robustness over a finite support is not calibrated Bayesian inference or uncertainty propagation. Current wins do not establish either. |
| 7. Novel mathematics or physics | New episode-specific rules within disclosed grammar | Not open-ended law discovery. Selecting a generated program cannot demonstrate discovery of a new representation or truly novel mathematics. |
| 8. Global constraints | Exact whole-program validation and dependency constraints; conservation now added | The checker already rejects locally plausible but globally wrong constructions. New conservation is a disclosed invariant, not something the player has discovered. |
| 9. Long research programs | Logistics, preparations, dependent construction and recovery | Bounded coverage. Correct inference can still fail operationally; longer plans alone often add action pressure. No evidence about multi-year research management. |
| 10. Conflicting literature | Provisional/artificial evidence and revision | Only a narrow analogue. No realistic source reliability, incompatible measurement conventions or cross-paper methodological reconciliation. |

## What our latest data establish

After replacing the three provider-failed Gemini attempts, 69 of 70 executions
won. Every winning construction was supported by the available evidence under the
complete prior; this was not a collection of lucky guesses. The sole remaining
failure described a valid compensator but did not install or submit it. Another
model temporarily installed stale settings, failed finish, then recovered.
These are operational failures, not evidence that the physical law was too hard
for the model to infer. All 496 recorded readings agreed with the world laws.

The strongest model used 16–20 actions on the memory discovery cells. All R0 runs
also finished within 64 actions. Thus these data do not support either “more
resources are necessary to solve these worlds” or “hidden patterns generally
trip frontier models.” They support a narrower finding: the tested models can
solve these bounded, fully specified hypothesis-selection tasks quite reliably.

## Conservation without calculus

Use exact discrete transport. For material amounts q and transfers f:

`q_next = q + B*f`, with every column of B summing to zero.

Then `sum(q_next) = sum(q)` exactly. Example: transfer two packets from reservoir
0 to reservoir1: `(3,1,0) -> (1,3,0)`. Total remains four. A hidden third reservoir
could make a visible subsystem seem to lose material while the entire system
conserves it. A sensor's displayed value need not equal material or flow.

A rate can be `delta_q / delta_phase`; with a unit phase step it is simply the
integer change. Continuous derivatives are unnecessary. If future mechanics need
continuous-time laws, represent rational rates or exact event updates first;
floating-point integrators and tolerances would complicate exact qualification.
Conservation is only one invariant; it does not uniquely identify dynamics.
Every legal construction in this pilot conserves packets by construction, so
it cannot directly measure whether a player independently enforces conservation.
That capability needs alternatives or repairs that fit local data but violate a
global constraint; it should be scored separately from conservation of the engine.

The implemented coupled-memory prototype preserves four packets in three
reservoirs. Two memory cells alter later transfers and are altered by past
transfers; the sensor mixes material and memory. The player must construct a
predictor correct for every future input history. Neither the memory cells nor
the displayed signal are conserved quantities. This is an artificial transport
law, not a physically faithful energy model or a claim about Noether's theorem.

Conservation can make inference **easier** by eliminating inconsistent candidates.
Its evaluation value comes from forcing a proposed local explanation to remain
consistent across other contexts, not from adding a formula to the manual.

## Highest-value follow-ups

1. **Invariant-constrained model revision.** Supply a model correct in one regime,
   then an anomaly with several explanations: sensor drift, transfer to a hidden
   reservoir, or changed interaction. A repair must explain the anomaly while
   preserving old predictions and the global ledger. Qualify against one-probe
   shortcuts and repairs that fit the new observations while breaking old cases.
2. **Representation expansion with operational consequences.** Let evidence force
   a change in model structure (for example, an extra state variable), followed
   by a device that must work in a new regime. Public syntax must remain complete;
   conceal the correct representation, not the permitted controls. This needs a
   new qualifier, not merely a bigger list of coefficients.
3. **Falsification and selective repair.** Give several plausible near-correct
   mechanisms and require an operational repair supported by a discriminating
   experiment. Score preservation of unaffected behavior separately. Existing
   repair families cover part of this; the extension must avoid repeated formula
   selection under a different story.
4. **Later: experiments that change the state being controlled.** Measurement
   would also alter the goal-relevant hidden state, making information gathering
   affect later options. This requires belief-state planning, synchronizing/reset
   audits and explicit resource/logistics controls. Appending a steering stage
   after independent reset experiments would not establish that coupling.

The current coupled-memory implementation is deliberately the bounded first step,
with bandwidth/oracle controls and no deep-tier claim. New live results are needed
before asserting an improvement in model failure rate.

## Verification advice from the essay

Independent verification is sound advice; “always rederive with a CAS” is not a
universal solution. A CAS can verify algebra under supplied assumptions while the
model, boundary conditions, branch choices or physical interpretation are wrong.
Use algebraic checks for identities, simulation for specified dynamics, statistical
methods for uncertainty, and domain review for model adequacy. Verification must
match the claim being made.
