# Scientific investigation architecture (axes v2)

Status: approved semantic direction, 2026-10-09. Concrete families must pass the
proof gates below before runtime integration. Zero levels are diagnostic controls;
the primary model evaluation uses nonzero levels at moderate P/R.

## Evidence and intent

NEXUS remains an artificial, deterministic world with generated integer laws and
exact verification. The agent applies science to accomplish an operational mission;
this is not a separate questionnaire/escape game, a real-physics simulator, or an
LLM-graded explanation task. Useful scientific reasoning should improve transfer
and experiment efficiency, without requiring a prescribed verbal workflow.

The audited 17-09-01 run had 70 live wins (68 official passes, two post-win harness
errors). Of 84 operations, 79 had an exact-context preview. Current T3 could be
resolved by a direct measurement or measurement plus solvability promise. Earlier
D4 runs used mission specimens directly rather than the intended auxiliary
investigation. These are legitimate strategies: qualification failed to establish
the intended reasoning requirement. R2 losses in 13-26-53 were largely physical
budget failures and cannot establish theory difficulty.

### Research informing the changes

| Primary source | Relevant finding/design | NEXUS consequence |
| --- | --- | --- |
| [DiscoveryWorld](https://arxiv.org/abs/2406.06769) | Evaluates iterative discovery with completion, process, and explanatory knowledge measures. Includes basic interaction controls. | Separate mission success, experiment efficiency, and transfer. Use deterministic traces rather than an explanation judge. |
| [NewtonBench](https://arxiv.org/abs/2510.07172) | Embeds a hidden equation inside supplied systems of equations; counterfactual law variations and system complexity test generalization. | Compose artificial laws and require inference through intermediate quantities. Keep exact bounded arithmetic and disclose the hypothesis grammar. |
| [DiscoverPhysics](https://arxiv.org/abs/2605.26087) | Active experiments and held-out trajectory prediction probe inference of latent structure. | Require operational predictions outside directly measurable contexts. Do not import numerical integration noise or Python submission execution. |
| [Alchemy](https://arxiv.org/abs/2102.02926) | Procedural latent causal structure supports online experimentation and ideal-observer analysis. | Pair generated worlds with exact observers and shortcut baselines; report behaviorally relevant uncertainty. |
| [ScienceWorld](https://aclanthology.org/2022.emnlp-main.775/) | Interactive scientific tasks ground concepts in actions and observations. | Preserve physical interaction while separating logistical burden from scientific inference. |

Historical benchmark scores are not predictions about the current models. NEXUS
must demonstrate its own difficulty empirically. A finite public grammar permits
enumeration; success via sound programmatic inference is valid scientific reasoning.

## Approved semantic contract

### Theory T: what is missing from the account of the world

- T0: resolved operational model; task-relevant properties/predictions supplied.
- T1: complete exact laws; unknown specimen properties or apparatus state may
  require measurements. This is state estimation and composition, not law discovery.
- T2: a supplied effective theory has a correction of specified shape with unknown
  parameters. Infer that correction and combine it with other laws.
- T3: a relationship is missing within disclosed dependencies and a bounded grammar.
  It may depend on an upstream T2 correction. Infer structure as well as parameters.

T3 may contain T2 reasoning; no forced chronological sequence prevents valid joint
inference. Do not relabel the same unknown coefficient as a state property merely
to populate a matrix. Track state and theory uncertainties separately.

### Discovery D: the investigation structure

| D | Required structure |
| --- | --- |
| 0 | Supplied observations suffice; no new measurement required. |
| 1 | A direct informative measurement suffices. |
| 2 | Combine measurements to separate effects or infer an indirect quantity. |
| 3 | An upstream inference is needed to configure/interpret downstream evidence. |
| 4 | Adaptive discrimination: an exact policy is strictly better than any fixed experiment batch. |
| 5 | Construct a diagnostic specimen/context using earlier discoveries; raw direct measurements cannot guarantee the mission. |

These are structural categories, not a universal scalar ordering. Every supported
cell needs explicit certificates; an unsupported cell must fail clearly. T0 only
pairs with D0. D0/T3 can infer structure from supplied data. Changing T disclosure
can change required measurements; do not claim exact factorial equivalence when it
does not hold.

### Planning P and resource pressure R

P0 places stocks, instruments and destination together and removes incidental
logistics. Higher P separates physical work while leaving the scientific response
function and legal experimental contexts unchanged. Scientific preparation remains
D even at P0. Publish a map to avoid mixing hidden navigation with budget pressure.

R0 has no in-game action limit. Accepted actions still increment turns, are hashed,
and count toward telemetry. Machine uses and initial-specimen stocks are unlimited.
Taking a designated stock creates an identical fresh specimen; taking a dropped
specimen does not clone it. Transformations can remain irreversible. No reset,
reroll, special replenish action, or general artifact cloning exists. Failed goal
checks remain recoverable and return no per-component hint. Harness limits remain
external and must not be reported as an in-world exhausted budget.

Higher R uses the same operations with disclosed finite budgets/stocks/uses.
Moderate R includes room for learning and recovery, based on a realizable policy,
not only a perfect-knowledge shortest route. R must not change scientific laws.

## Architecture and integration boundaries

1. Explicit `axes-v2` selection; keep legacy generation, seed meanings, action
   semantics, public payloads and hashes stable by default.
2. Declarative finite law expressions and experiment dependencies, separate from
   hidden specimen state and player-visible control definitions.
3. Existing room/inventory/machine/stock interactions. A mission apparatus accepts
   operational settings for disclosed future conditions. The measurement range
   and operational range are explicit. Probes retain their documented semantics;
   no secret restriction is introduced just to defeat a model strategy.
4. One exact deterministic evaluator feeds both runtime and qualification; an
   independently implemented tiny oracle checks the qualifier before adoption.
5. Public theory/evidence/controls are distinct from private truth, posterior,
   policy, certificates and terminal diagnostics. No progress hint during play.
6. Mission correctness evaluates a vector of predictions/settings jointly. A
   failed attempt provides only failure, not a component score. Enumeration is
   legal and measured; never claim guessing impossible in a finite R0 world.

## Proof gates

- Enumerate the complete public prior and all legal measurement contexts.
- Every admitted truth is solvable under the same public goal and interface.
- Public metadata and solvability do not select the truth; D0/T0 disclosures are
  intentional exceptions. Qualify whole public families, not lucky hidden truths.
- Sufficient evidence identifies mission behavior; removing claimed dependencies
  leaves relevant ambiguity. Count equivalence classes, not syntactic formulas.
- D4: prove adaptive worst-case cost and best fixed-set cost separately.
- D5: include construction and all alternate legal contexts in the proof.
- Target contexts are not directly measurable through probe, operate, errors,
  resource quantities, object IDs or replay hashes.
- Replay a realizable policy for every candidate truth; check invalid-action
  atomicity, recoverability at R0, exact receipts and terminal-only telemetry.
- Compare random/exhaustive experiments, direct preview and repeated goal guesses.
  A 3-vs-4 measurement gap proves efficiency only, not hard model reasoning.

## Performance choices

Precompute integer outcome partitions and prediction equivalence masks once per
immutable problem. Memoize belief costs across queries for that problem. Avoid
repeated Pydantic/AST evaluation inside minimax. Bound hypotheses/experiments and
reject problems that exceed qualification limits. Benchmark against the existing
tuple oracle with identical answers before accepting speed claims. No CPU/GPU
parallelization until profiling demonstrates enough independent work to amortize
startup, serialization and duplicated caches. Existing catalogue caching is retained.

## Acceptance and limitations

Primary evaluation: nonzero D/T with P1 or P2 and R1. Diagnostic controls use
P0/R0, supplied evidence, known corrections and direct previews. Report mission
success, held-out transfer, informative/redundant measurements, failed settings,
actions, generation time and harness errors separately. Real-model difficulty is
unproven until the user executes the paired pilot. Do not add noise as a shortcut
to difficulty. Do not run paid model evaluations in this implementation task.
