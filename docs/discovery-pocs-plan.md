# Representation discovery and uncertainty-aware construction: implementation plan

Status: approved scope; design/proof checkpoint only. Runtime integration and seed qualification are pending.
Baseline: petmal/NEXUS, feat/theory-prior-axis, 9c7939c6531e4a0d6d1e275fafa7420fd3798651.
Date: 2026-10-20. Preserve all existing families, defaults, axes, protocols, receipts, and behavior.

## Objective and evidence

Implement two independently selectable experimental ontologies and one shared MindTrial matrix:
- representation-discovery-v1: learn an operationally sufficient state representation from observations and interventions.
- uncertainty-construction-v1: infer the dependence/measurement structure needed to construct a device robust to a finite, disclosed class of operating disturbances.

The latest joint-assembly audit found a universal eight-reading fixed schedule, a 24-action supported win in every one of 432 worlds, and an allowance of 40. Its four ordinary local readings reduce the prior to twelve worlds. All 58 completed real-model games won on their first finish; 56 wins were supported by evidence. New machinery must address these shortcuts explicitly.

These are PoCs, not a promise of model failure or an admitted cognitive-depth tier. Qualify observable behavioral claims, then measure model difficulty. Never require a particular explanation, private parameter spelling, or designer-preferred representation.

Research basis:
- Schölkopf et al., Towards Causal Representation Learning: https://arxiv.org/abs/2102.11107
- DiscoverPhysics: https://arxiv.org/abs/2605.26087
- CausalDS, revision 2: https://arxiv.org/html/2607.08093v2
- Klenske and Hennig, Dual Control for Approximate Bayesian Reinforcement Learning: https://jmlr.csail.mit.edu/papers/v17/15-162.html

These sources motivate the hypotheses; they do not certify NEXUS-specific difficulty. CausalDS's uncertainty findings concern statistical estimation. The first exact NEXUS PoC below tests dependence-aware robust construction, not confidence-interval calibration or an equivalent reproduction of that benchmark.

## Design decisions

1. Use separate versioned plugins. Do not combine the PoCs before measuring their individual effects.
2. Preserve the Sealed Facility setting, artificial names, exact public controls, persistent specimens, explicit finish, and live receipt.
3. No external Python for evaluated players. The operator/reference investigator may use Python. Expose raw observations with sufficient indexing and small exact arithmetic; a declared aggregate-statistics view must not reveal the hidden dependence or an optimal experiment.
4. Deterministic bounded integers, finite disturbances, and data-only programs. No floating-point physics, LLM judge, generated Python, eval, or exec.
5. Unlimited reusable apparatus and replenishable ordinary stocks; moderate action allowance for science rows. No fatal commitment, consumable trap, forced investigation order, or extra replenish action.
6. T0/D0 supplies a correct law and construction for the identical physical episode. T2 supplies the relevant representation or measurement/dependence shape while leaving bounded parameters unknown. T3 supplies the complete bounded construction grammar, not an enumerated short menu of final theories.
7. Initially hold D at one explicitly experimental family-specific profile, D4. Do not manufacture a D ladder from unproved claims. P0 removes travel as a confound. T1 and other unsupported profiles fail clearly.
8. Keep all ordinary alternative strategies legal, including finite enumeration, skipping irrelevant mechanisms, direct mission-compatible inference, and recoverable failed finishes.
9. Classify epistemic support before revealing the finish outcome. A lucky robust build is still an unsupported win if incompatible worlds remain.

## Critical design checks already executed

See discovery-pocs-design-checks.json and discovery-pocs-implementation.md for scope and reproduction.

A small eight-state hidden-register system genuinely requires eight predictive state classes: twelve pairs have identical current readings but distinct future responses. Nevertheless a fixed three-observation schedule reveals the whole state. This is a rejected hard-case candidate and a regression fixture for the qualifier.

Two disturbance supports with opposite triple parity have identical one-coordinate and two-coordinate marginals, yet require opposite robust settings. Thus independent means/variances or covariance can be insufficient. Nevertheless one synchronized triple reading identifies the support. This is another rejected hard-case candidate, not a prequalified pilot seed.

Neither hidden variables nor higher-order dependence alone is enough. The next construction search must produce stronger candidates and report the shortcuts it actually finds.

## PoC A: representation discovery

### Scientific task

The player sees a compact raw instrument view and can prepare specimens through public apparatus operations. Different preparation histories can produce the same current view while having different responses to future interventions. The required representation must retain the distinctions that matter to the mission.

Generate causal programs compositionally from a bounded primitive grammar. Do not disclose the final hidden coordinates, factorization, or a list of four complete explanations. The grammar and admissible bounds remain complete and public. Controls, action effects that are administrative, measurement timing, and specimen identity are fully documented.

The player builds an exit device using public primitive modules and wiring. Test its behavior over the complete finite set of relevant legal preparation/operating conditions. A lookup-based or alternative representation is accepted when it meets the same public behavior contract. Do not grade an essay or require recovery of the private latent AST.

### Candidate search

Begin with a small bounded subset and expand only after profiling:
- up to 1,024 possible world programs per disclosed profile;
- up to 64 reachable states per world;
- up to 4,096 canonical build candidates;
- bounded normalized experiment histories with explicit coverage limits.

These are engineering caps, not desired difficulty metrics. Exact search must terminate with a scoped result or report incomplete. Do not claim exhaustive coverage of all player policies from an exhaustive search over a shorter experiment grammar.

Vary structural composition, observation maps, and intervention effects. Exclude duplicate worlds modulo observable behavior, preserving prior probability mass when grouping. Keep a deliberately simple control family to ensure the qualifier accepts legitimate easy strategies.

### Required qualification

- All admitted worlds have reachable successful concrete builds.
- At least one same-observation/different-future witness, with a legal experiment that distinguishes it.
- Exact behavioral partition: sufficient memory/state classes, distinguishing suffixes, and goal-relevant equivalence.
- Reject a hard-case claim if a current-reading-only policy or a common build succeeds throughout the public prior.
- Audit universal fixed panels, standard short preparation/calibration prefixes, direct terminal probes, reset-like synchronizing sequences, and legal preview/error/finish channels.
- Compute mission-acceptance intersections, not merely unique hidden-law identification.
- State the residual mission ambiguity after each tested prefix.
- Check whether all scientific uncertainty can be resolved before construction. Report this honestly; construction-dependent discovery is a future integration gate, not an implicit claim of this first PoC.
- Verify physical costs separately from query counts and information bounds.

The intended contrast is supplied representation versus representation discovery under the same raw data and physical mission. It is not renamed-coordinate arithmetic, obligatory prose explanation, or more hidden-state bits.

## PoC B: uncertainty-aware construction

### Scientific task

Reader values combine specimen response with persistent shared nuisance effects and bounded operating variation. Repeated observations of one channel cannot automatically be treated as independent evidence about the physical response. Available cross-channel/condition experiments make the mission resolvable.

The player constructs a compensator that succeeds across every admissible operating disturbance for the actual world. The engine enumerates this finite support exactly at finish. This preserves deterministic exact victory and avoids failure because of an unlucky random test.

Keep three concepts explicit in player evidence:
- physical response;
- displayed measurement and its measurement conditions;
- variation allowed during final device operation.

Do not conflate uncertainty in the player's knowledge with actual physical variability. A common build across all surviving worlds is evidence-supported. A build that handles every disturbance only in the true world may still be an unsupported commitment.

### Candidate search

Use compositional, bounded measurement and disturbance programs. Include shared drift, different channel loadings, and dependence that changes operational worst cases. Keep relevant arithmetic small. Sample generation may be seeded, but a compiled episode and action trace must replay identically.

Do not make correctness depend on estimating an unbounded distribution from a few noisy samples. Every admitted profile must have a finite evidence-supported public policy. A finite balanced experimental panel or exact bounded observation contract may be used, but its revealing power belongs in the shortcut audit.

The first version tests robust dependence reasoning. Frequency-based confidence intervals, probability reports, and proper-scoring-rule missions are separate future extensions.

### Required qualification

- Matched marginal or local-observation closures leave operationally incompatible possibilities.
- A well-defined legal joint/contrast experiment can resolve them.
- Mean-only, independent-channel, diagonal-covariance, and inappropriate averaging baselines are evaluated as explicit policies with exact acceptance results.
- Audit whether one full joint panel, one higher-order moment, a standard calibration prefix, or a universal conservative build solves the whole family.
- Prove every selected mission has a robust build under the actual disturbance support.
- Accept every equivalent robust build; do not reward identification of irrelevant nuisance constants.
- Count same-fixture repeats and information-equivalent observations privately; do not label repetition universally irrational.
- Compare supplied measurement/dependence shape with hidden shape at the same budget and physical target.
- Preserve exact recovery after a rejected build.

Simple two-support parity is a negative qualification fixture because a single paired sample resolves it. The hard-case search must address that shortcut rather than enlarging the sample list.

## Architecture and performance

Add two small packages under src/nexus/ontology/:
- representation/: schema, laws, evidence, generation, inference, runtime, policy, qualification, proof.
- uncertainty/: the same roles, only where actually needed.

Register schema mappings in ontology/payloads.py and definitions in ontology/catalog.py. Use the current trusted adapters; no dynamic external plugin loading is needed.

Keep all game transitions in the canonical runtime. Player evidence describes but does not implement laws. Private latent state must not leak through DomainArtifact payloads. Where possible, store public preparation history and recompute private state using the immutable world law, with bounded memoization. Any private mutable-state extension requires an explicit projection and replay audit.

Construction should use public primitive selection/wiring through existing configure/operate surfaces if feasible. If that becomes opaque or unreasonably verbose, introduce one narrowly typed declarative program capability with strict schema validation; do not make undocumented opcode syntax a challenge. This choice is settled after the proof model determines the required build language.

Reuse existing inference and mission-tracking contracts. Extract a shared finite-decision utility only if the two concrete PoCs demonstrate the same semantics. No speculative universal science engine.

Performance priorities:
- compile normalized observation signatures once per profile;
- cache immutable primitive/transition tables and integer-bitset acceptance masks;
- preserve original prior weights in quotient classes;
- short-circuit mission support when a common accepted build exists;
- reuse prefix-state calculations for experiment histories;
- keep expensive qualification offline, not per generated episode;
- report cold/warm compile, generation, filtering, qualification, replay time, and memory;
- prefer sparse/factored storage when full world-by-query tables exceed measured bounds;
- do not introduce multiprocessing or GPU dependencies without a measured bottleneck.

## Private telemetry

Add terminal/shutdown-only summaries compatible with existing diagnostics:
- remaining worlds, behavior classes, and mission acceptance classes;
- first evidence-supported build, action, and observation ordinal;
- pre-finish supported/compatible/contradicted/ineligible classification;
- representation ambiguity and omitted distinguishing contrasts;
- local-only versus joint evidence coverage;
- repeated and information-equivalent measurements;
- robustness violations categorized by physical variability versus unsupported inference;
- committed construction, corrective operations, and recovery;
- qualification version, source/matrix identity, exact bounds and incomplete searches;
- cold/warm performance timings.

No private truth, optimal next query, posterior hint, counterexample, or qualification label reaches active player output. Do not infer hidden chain-of-thought from the trace.

## Shared ten-row matrix

The draft inventory is discovery-pocs-matrix.draft.json. It is intentionally not runnable and contains no invented or unqualified seeds.

All main science cells use P0/R1 and a common action allowance B across both PoCs. Choose B only after public-policy validation: initially require at least twice the larger achieved reference cost plus a checked recovery allowance. This is reference-policy slack, not an optimality claim. Keep B identical for T0, T2, and T3 comparisons.

Rows 01-05: representation discovery.
1. T0/D0 execution control, mechanism A.
2. T2/D4 supplied representation, mechanism A.
3. T3/D4 hidden representation, mechanism A.
4. T3/D4 structurally different held-out mechanism B.
5. Exact row-03 scientific world at R0, with the same external harness ceiling.

Rows 06-10: uncertainty-aware construction.
6. T0/D0 execution control, mechanism C.
7. T2/D4 supplied measurement/dependence shape, mechanism C.
8. T3/D4 hidden measurement/dependence shape, mechanism C.
9. T3/D4 structurally different held-out mechanism D.
10. Exact row-08 scientific world at R0, with the same external harness ceiling.

R0 removes the world action limit; it does not reset the world, bypass finish, grant extra observations, or mean unlimited model computation. Record the actual harness/time/reasoning limits. No replenish action.

A/B and C/D must differ in canonical mechanism structure rather than constants or labels alone. Stronger claims require more seeds and replications. This ten-row pilot diagnoses mechanisms; it does not estimate a population failure rate.

Expected relative challenge is a hypothesis: T0 low, T2 intermediate, T3 experimental/high relative to its matched control; R0 has identical science. Do not forecast a percentage of models failing.

Preflight must:
- scan and select qualified seeds mechanically;
- record exact shortcut/baseline results, goal equivalence, policy costs, recovery and replay;
- reject stale or partial reports;
- bind source, grammar, prior, matrix, and relevant assets;
- verify T0/T2/T3 matched worlds and R0 pairs;
- retain the complete public prior rather than exposing selected seed pools;
- export matching config and tasks YAML only after admission;
- validate prompt/tool semantics from each manifest;
- keep seeds, private mechanism labels, difficulty proofs and solutions out of player prompts.

## Implementation phases and completion gates

1. Read latest branch and instructions; commit this resumable design checkpoint.
2. Implement independent standard-library scalar proof models and candidate searches. Reject both naive shortcut witnesses from hard-case admission. Do not register new families yet.
3. Produce the first bounded accepted candidate set for each PoC; document every proof's exact scope and remaining counterexamples. If a candidate fails, revise the mechanism before runtime integration.
4. Implement schemas/laws/inference/runtime/evidence and public reference investigators through the trusted registry.
5. Add meaningful tests: independent scalar conformance, acceptance equivalence, source/privacy, invalid-action atomicity, supported versus lucky success, recovery, deterministic save/load/replay, and all admitted profile worlds.
6. Add source-bound preflight, selected seeds, operator guide, player-faithful walkthroughs, and MindTrial YAML for the joint matrix.
7. Refresh legacy source-bound manifests only after their unchanged proof/witness/conformance gates pass. Never weaken admission or regenerate a release hash as a substitute for proof.
8. Run fast, extended, cross-seed, HTTP/CLI, installed-wheel, and actual-image tests; verify OCI revision. Record exact commands, counts, timings, and CI links.
9. Commit focused stages to feat/theory-prior-axis. Preserve main and previous versions. Deliver qualified matrix, build command, downloadable YAML, proof limits and test results.

No paid real-model calls, public MindTrial repository edits, main merge, or branch cleanup is authorized by this scoped implementation.

## Resumption

Read discovery-pocs-implementation.md first. Recheck branch head and preserve any concurrent changes. Do not mistake the executed finite design checks for runtime qualification or a completed feature.
