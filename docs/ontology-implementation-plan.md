# Replaceable scientific ontologies: implementation and resume plan

## Phase 1 — prove the proposed boundary

- Read AGENTS.md, current generation/runtime/projection/inference code and exact
  GitHub head. Capture compatibility fixtures already established by maintenance.
- Run a pure finite permutation PoC before changing runtime. Exhaust every world
  at depths 2/3; check sequential prediction, missing-factor ambiguity, calibration
  dependency, no-signal evidence and predictive equivalence.
- Review architecture independently. Keep report in scratch; record accepted
  findings and proof results here. Gate: no critical unaddressed design issue.

## Phase 2 — existing scientific adapters

- Add ontology contracts/catalog and family adapters with stock creation,
  transformation, configuration and mission behavior. Keep axis-v1 branch stable.
- Route engine, manifest and scientific solver through adapters. Core retains
  consumption/turn/receipt ownership. Preserve exact old error/event behavior.
- Normalize scientific measurements at adapter boundary. Implement flat and
  resonant belief adapters; move generic trace accounting away from instrument
  names. Keep historical performance JSON unchanged.
- Route generator and qualifier selection through catalog factories with lazy
  inference imports. Gate: 21 golden cases, 197-case comparison, action atomicity,
  replay and terminal privacy tests before adding a new family.

## Phase 3 — typed domains and composed investigations

- Add validated domain entity/stock/public/private envelopes once to core schemas;
  obtain concrete payload schemas through a versioned built-in definition.
- Add validated relationship DAG and reusable evaluation over typed primitives;
  describe existing resonant dependency and the categorical chain through it.
- Integrate the categorical PoC through the same runtime, protocol, save/load,
  receipt and diagnostic contracts. Expose it explicitly as experimental.
- Ensure adding its adapter/definition does not require a new branch in session,
  replay, receipt or generic diagnostic accounting. Update renderers to project
  domain properties without assuming legacy fields.
- Gate: exhaustive 36/216-world public-policy wins, oracle posterior agreement,
  failed submissions/no-signal, HTTP privacy/finalization and strict schema tests.

## Phase 4 — quality and performance

- Keep immutable catalog/graph data and cached seed-independent compile products.
  Remove redundant artifact copies if ownership proof establishes safety. Preserve
  cold/warm generation improvements; benchmark same seeds and profiles.
- Run focused tests first, then full `NEXUS_STRESS_SEED_COUNT=3 uv run pytest -q`.
- Run focused Ruff/Pyright, frozen lock and whitespace checks. Independently review
  actual diff for private/public mistakes, shared-state leaks and missing seams.
- Fix valid findings and rerun relevant gates. No paid model evaluations.

## Phase 5 — delivery

- Write an ontology author guide with concrete extension example, supported
  guarantees, performance data and limitations. Keep checkpoint resumable.
- Publish focused commits through expected-head GitHub lease, preserving the
  private feature branch and verifying every uploaded tree. Update PR #6 and
  inspect exact-head CI. No main merge or public MindTrial changes.

## Checkpoint

Phase 1 passed: exhaustive proof covers all 36/216 worlds; baseline compatibility
suite passes (24 tests). Independent design review accepted with explicit public
projection/mutation boundaries, versioned payload validation, and separate generic
mission diagnostics. Integer selectors preserve the current action schema; arbitrary
noninteger controls remain outside this PoC. Reading bounds are not action optima.

Phase 2 underway: runtime ownership extraction, catalog routing and compatibility
adapters. No legacy wire/schema changes intended. Development dependencies restored
with `uv sync --frozen --all-extras` before testing.

## Implementation checkpoint

- Runtime/catalog/manifest/qualification/physical-plan routing extracted; legacy
  scientific encodings preserved. Public-only belief construction, normalized
  measurements and common terminal accounting implemented.
- Typed domain envelopes, registered payload schemas, mission state/projection,
  immutable dependency graphs and categorical depth-2/3 PoC integrated.
- Independent proof: 36/216 worlds. Live exhaustive policy/replay and posterior
  oracle checks pass. Focused regression: 78 passed. 197-case comparison: zero
  episode/manifest/trace/performance differences.
- Review fixes: keyed episode identity; loaded apparatus arity/range and topology
  validation; initialize submission telemetry from canonical initial state.
- Shared control scalar normalization intentionally retained. PoC is explicitly
  uncalibrated, one-room, unlimited-resource and separately generated; no new
  production D/T claims. Target class count stays six as chain depth increases.
- New-module Pyright passes. Full regression on stable source and isolated
  before/after timing remain final gates, followed by commits/expected-head publish.

## Final validation and publication checkpoint

All implementation gates passed: full suite 451 tests with three existing warnings;
36 post-format checks; 197 compatibility cases unchanged; new-module Pyright,
focused Ruff, frozen lock and whitespace checks. Sixteen fresh-process benchmark
references won with no material generation regression in this sample. See
`ontology-refactor-results.md` and raw benchmark JSON for details.

Local commits: `368d0dd` (plan/proof), `576a79f` (implementation/tests).
Equivalent remote Git Data commits prepared with exact tree matches:
`d9224c76d50f58a54c81b30db68e4f72044cb5d0`,
`cd37c751078f6224bc9afccedcf7bae235fa80ca`.
Final documentation commit follows; publish using expected head
`eaeb8f5cbecd08109569c14228334cf7b2bfd8f6`, then inspect exact-head CI.
Do not force-push, merge main, or publish private code to MindTrial.
