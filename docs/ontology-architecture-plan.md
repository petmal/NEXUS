# Replaceable scientific ontologies: system design

## Approved goal

Keep NEXUS's scientific-process evaluation, deterministic runtime, public controls,
privacy, difficulty semantics and exact receipts stable while making entities,
laws, instruments and investigation structures replaceable. Preserve all current
families and their serialized behavior. Prove critical assumptions before runtime
migration. Work stays on `feat/theory-prior-axis`, private petmal/NEXUS, PR #6.

Baseline: published `eaeb8f5`, local `39d051b`, identical tree
`3357aac8fa34552d48774551d4dbb54f0b1ee780`; CI passed; 440 tests passed previously.

## Boundaries

1. Runtime owns action atomicity, location/access, resource consumption, turn
   accounting, replay, terminal gating and receipt issuance. Existing axis-v1
   mechanics remain an isolated compatibility path.
2. Scientific ontology adapters own typed specimen creation, transformations,
   configuration validation, public controls and mission assessment. They do not
   issue receipts, expose terminal diagnostics during play or consume resources.
3. Scientific inference owns a normalized measurement representation and a small
   belief interface (counts, observation update, complete-submission exclusion).
   Historical event wire formats are interpreted, not rewritten. Generic terminal
   accounting uses this interface; legacy performance projections remain unchanged.
4. Investigation graphs describe relationship dependencies and disclosure roles.
   They are validated DAGs with explicit external inputs and target nodes; hidden
   expressions remain private. A graph is not a stage-unlock mechanism or proof
   that a particular experiment order is mandatory.
5. Qualification belongs to each scientific family behind a common dispatch.
   Generic conformance checks do not substitute for scientific-identifiability
   proofs. Exact finite minimax remains an optional small-problem backend; larger
   families may supply factor or compositional witnesses with honest bound labels.

## Serialization and extension contract

Keep old Artifact, sample, stock, investigation and truth encodings intact. Add a
single versioned domain envelope for new ontologies, with identity/location and
ontology-owned payloads validated against registered Pydantic schemas. Unknown
ontology/version and mismatched payloads fail closed. No unconstrained properties
bag, arbitrary import path from episode data, eval/exec, or player-loaded code.

Use an explicit built-in catalog initially. Third-party package installation and
discovery are deferred; the same contracts are the future trusted-code extension
boundary. Declarative law building blocks remain typed data, interpreted by the
ontology. Numeric/categorical domains and operator vocabularies need not be shared.

Runtime/mission and inference services are separate: playing an episode must not
compile its complete hypothesis prior. Public projections must not inspect truth.
Registry objects contain stateless adapters; do not cache mutable episodes or
session state. Preserve named RNG streams, identity encoding and old cache keys.

## Concrete extension proof

Add an opt-in categorical permutation investigation with three symbols and two or
three relation stages. Each relation is one of all six permutations. The first
instrument reads its relation directly; later instruments return a reading only
when configured with the preceding composed response, otherwise public no-signal.
The mission predicts the composed relation, using a prediction board rather than
the historical port/controller convention. Specimens have a categorical symbol,
not shape/pattern/polarity filler fields.

All combinations are admitted (36 or 216 worlds). Two readings determine each
permutation; a composed public-information policy uses at most 2*depth readings.
Every relation affects mission predictions; later instrument tuning depends on
upstream relationships. Direct guessing and interleaved inference remain legal.
Exhaustive oracle checks establish these claims before live integration. This is
an extension/conformance PoC, not a claim of increased empirical model difficulty
or a new cross-ontology calibrated axis profile.

Extract the existing resonance H -> response G -> field composition into the same
graph representation as an operator-side specification; do not add hidden graph
metadata to old manifests or alter old evidence.

## Invariants and risks

- Accepted observations must correspond to actual world execution. Off-signal is
  evidence, distinct from invalid action and zero reading.
- Invalid actions preserve the entire state. Probe preserves specimens and uses.
- Mission configure has no correctness feedback. Only finish can issue victory.
- Complete-vector rejection updates scientific belief, including correlations.
- Public controls are complete; private truth/prior diagnostics remain private.
- Axis values retain their meanings, with family-specific qualification and an
  explicit experimental flag for the new uncalibrated PoC.
- Compatibility guards compare episode, manifest, trace, receipt and terminal
  performance. Old schemas and transport unions are sensitive migration seams.
- Graph syntax validation is not semantic proof of irreducible reasoning depth.
- Arbitrary physical topology remains outside the network witness compiler; do
  not claim that ontology modularity alone solves graph planning.

## Decision ledger

Decision: adapt old wire formats; use typed envelopes only for new ontologies.
Reason: preserve benchmark comparability and saved artifacts.
Invalidates if: a separately approved versioned wire-format migration is needed.

Decision: common inference accounting with legacy output projection.
Reason: instrument names should not be embedded in generic diagnostics.
Invalidates if: a family cannot report exact target counts; then mark unsupported
or bounded diagnostics explicitly rather than inventing exactness.

Decision: no dependency/toolchain migration or dynamic package loader in this pass.
Reason: core extension contracts must first be proven by distinct built-ins.
Existing pytest/Ruff/Pyright gates are retained; broad ty/basedpyright/coverage
toolchain adoption is a separate repository-wide change.
