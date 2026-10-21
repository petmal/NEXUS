# Coupled memory discovery: design and implementation plan

Status: implemented; final validation/publication phase. Updated 2026-10-21 UTC.
Branch: feat/theory-prior-axis. Baseline: b61c6f2.

## Purpose and evidence

The discovery pilot produced 69/70 live wins. All winning decisions were supported;
the remaining model described a valid compensator but never installed or submitted
it. Memory discovery increased effort but Astra used only 16–20 actions. Independent
calibration followed by an eight-fixture census made the uncertainty family easy.

Build an opt-in coupled-memory family that makes latent dynamics and observation
encoding interact, retains exact all-history acceptance, and measures shortcut
policies honestly. Preserve previous families, seeds, defaults, and the 64-action
R1 allowance. No paid model calls, external player Python, main merge, or new
dependencies are authorized or required. Do not claim cognitive hardness from
state counts, grammar size, or proof depth alone.

The supplied scientific-reasoning essay is inspiration and a set of hypotheses,
not empirical authority. Critique it against primary sources and our own results.

## Proposed system, subject to proof

- A small conservative artificial transport system: three reservoirs exchange
  integer packets; their sum is exactly fixed. Two latent memory cells affect
  subsequent transfers and are updated by those transfers. Observation encoding
  depends on both material state and memory, with unknown parameters.
- A complete finite public grammar; T0 supplies the construction, T2 supplies
  dynamics but leaves observation parameters unknown, T3 hides both. P0 and R0/R1.
- The laboratory returns a bounded final observation for an input history, not
  the hidden trajectory. No blank fixture directly discloses calibration.
- The actual carrier must contain a model equivalent to the facility over every
  future input history. Equivalent constructions are accepted; no exact private
  parameter spelling is required. Finish feedback remains binary and recoverable.
- Discrete conservation uses q_next=q+B*f with column sums of B equal to zero.
  No derivatives, floats, numerical integration, or tolerance-based victory.
- Candidate grammar, word length, observation alphabet and memory rules are not
  final until exhaustive checks demonstrate identifiability, coupling and useful
  information bounds. Reject a candidate that is still solved by a simple
  isolated calibration or short-panel shortcut rather than relabeling it deep.

## Qualification requirements

1. Independent scalar dynamics and global behavioral equivalence proof, including
   all reachable states and future histories beyond the reader horizon.
2. Exact conservation/nonnegative/bounded-state invariants and deterministic replay.
3. Full legal query set audit: identifiability modulo full mission equivalence;
   minimum actual-outcome certificates with explicit proven lower/upper bounds.
4. Guaranteed adaptive-policy bounds and fixed-panel baselines; preserve the
   distinction between measurement counts, action costs and cognitive difficulty.
5. Coupling witnesses: same measurement compatible with distinct physical/calibration
   explanations; history-dependent discrimination; quantify oracle-disclosure
   ablations rather than claiming joint inference from concatenated parameters.
6. Blind-build and failed-finish strategies included in reporting. Strong claims
   must account for all legal evidence-bearing actions or explicitly narrow scope.
7. Admission is fail-closed, source/proof/matrix bound, diversified by mechanism
   structure and observable behavior, and excludes shallow seeds from stronger tiers.
8. T0/T2/T3/R0 paired truths, clear public controls and no live private hints.

## Phases and completion gates

1. Research assessment + bounded mathematical PoC. Write executable proof and
   negative controls; fresh independent design judgement before integration.
2. Domain plugin and shared finite-discovery adapter cleanup after concrete reuse.
   Keep ontology-specific mechanics outside the core engine. Cached transitions,
   bitset posteriors and behavioral classes should eliminate repeated simulation.
3. Qualification/preflight, terminal classification, and qualified pilot matrix.
   Fix the stale prior preflight snapshot as a separate documentation correction.
4. Unit/integration/conservation/negative/serialization/privacy/replay tests and
   installed-image packaging. Fresh implementation judgement and fixes.
5. Full regression gates, branch publication, CI, downloadable MindTrial YAML and
   operator guide. Record exact tested commit and any remaining experimental limits.

## Resume

Read AGENTS.md and this plan; inspect status before edits. Record candidate results
and design changes here before integration. Do not overwrite old experiments or
silently change their qualification semantics. The first prototype is provisional.

## Design decision, 2026-10-21 UTC

Integrate the ternary conservative-feedback candidate as `coupled-memory-v1`.
The exhaustive prototype has 384 programs, 336 complete behavioral classes,
40–135 reachable states, and a public minimax policy of 5–6 readings. The
six-reading worst case meets the information lower bound, not a cognitive-depth
lower bound. Every world has a three-reading actual-outcome certificate. The
binary alternative needs nine readings entirely because of output bandwidth;
reject it as a claimed reasoning improvement. Keep ternary output comparable to
representation-discovery-v1. The five-valued counterfactual solves in four reads.

T2 discloses physical dynamics; the observation encoder remains unknown. Its
policy takes two readings. The private known-encoder ablation takes four. Their
sum equals the joint worst case; do not claim superadditive inference difficulty.
No single query identifies encoder parameters independently of dynamics, but
query frequencies can provide partial information, and 48 equivalent-program
pairs span encoder choices. Qualification must reason about mission equivalence,
not insist on recovering non-identifiable private parameter spelling.

A persistent manipulation/escape stage is deferred: reset-based identification
followed by steering mostly appends planning. Genuine dual-control would require
a separate belief-state qualifier including synchronizing/reset words and unsafe
actions. It must not silently change P0 in this comparison.

Implementation scope: explicit shared adapter metadata/read hooks; new versioned
schema/laws/evidence/runtime; cached finite transitions and posterior partitions;
independent all-state scalar conformance and all-history partition proof; exact
single/pair/triple certificates, adaptive and fixed-panel bounds, oracle and
sensor-bandwidth controls; source-bound paired pilot; terminal-only telemetry;
regression/privacy/replay/HTTP/package gates. Deep-tier admission remains false.

Qualification also reports eligible finish feedback: each such action asks
membership in one behavioral class. Any evidence-bearing event has at most three
outcomes, so the six-event minimax lower bound survives mixed probe/finish
strategies. This is not a six-reader lower bound or exact total-action optimum.
A correct blind guess still wins; unsupported success is classified separately.

Checkpoint: mathematical prototype and fresh design judgement completed; runtime
integration begins after this decision. No changes to old truth selection or public
contracts intended. Review report will be summarized in the final operator guide.

## Integration checkpoint

New plugin and explicit shared adapters implemented. Independent proof checks all
51,840 legal program/states; three-reading certificates and six-reading policy
confirmed. Full feedback ablations are observable for all selected pilot truths;
12/384 unselected programs lack a legal-horizon memory-to-transfer witness and
are not silently counted as passing that matrix gate. Runtime accepts all finite
histories by product-machine traversal, independently of bounded reader tables.

Ten new pilot cells and old ten pilot cells passed preflight. Legacy proof and
serialized witnesses unchanged; 15 legacy conformance/qualification tests passed.
Thirty old-family episode snapshots match baseline b61c6f2 exactly excluding random
IDs. Focused shared tests58 passed; new proof tests7 passed before adding feedback
witness assertion (covered in pending full gate). Full fast, slow and property gates
are running. First fast run caught a missing Docker build-context allowlist entry;
fixed before restart. No production state/mechanics change was needed for that fix.

The earlier plan's rejection of short-panel candidates applies to stronger admission.
The chosen bounded candidate is integrated experimentally with its three-reading
shortcut disclosed; it does not meet a claim of unavoidable deep investigation.

Resume: inspect current processes/results at ../coupled-{fast,slow,property}-tests.txt,
finish independent implementation review, regenerate any source-bound artifacts if
code changes, validate isolated wheel, publish feature branch and check CI. Docker
is unavailable in this host; actual-image testing must be via CI. Do not mark those
gates passed based on the older image.

Independent implementation judgement found no blocker. Its suggested fifth-pulse and complete reader-surface regressions were added; final new-family focused suite11 passed. Isolated frozen-dependency wheel passed all ten cells with identical source/proof/matrix identity and results, plus CLI generate/qualify/solve/replay. Three property tests passed (three-seed sampling,426s). No source edits after the bound reports. Fast and extended suites still running at this checkpoint.
