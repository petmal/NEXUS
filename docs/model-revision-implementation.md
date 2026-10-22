# Model revision: implementation and resume checkpoint

Base branch/head: `feat/theory-prior-axis` / `bf86ce8c`.
See [system design](model-revision-design.md) for invariants and admission limits.

## Phases

1. **Proof before integration.** Independent packet-network prototype in
   `../revision-poc`; enumerate grammar, behavioral classes and archive groups.
   Compare exact shortcuts and public policy costs before selecting a family.
   Record rejected assumptions and update the design before implementation.
2. **Diagnostics.** Bounded terminal summary, non-informative action semantics,
   compatibility/privacy regressions. Verify the actual 8192-byte capture case.
3. **Author API.** Consolidate catalog/schema registration, document contracts,
   retain explicit trusted catalog loading; defer automatic installed-package discovery until provenance is supported.
   Test conflicts, validation, lazy loading and old-family compatibility.
4. **New adapter.** Primitive network laws, schemas, evidence, inference, runtime
   integration and all-history acceptance. Reuse existing discovery mechanics
   while keeping per-family policy bounds and configuration explicit.
5. **Qualification and matrix.** Independent oracle, complete public-prior
   consistency, shortcut report, matched controls, source-bound preflight,
   MindTrial YAML, plain-language example and operator guide.
6. **Review and delivery.** Independent read-only review as recommended by the
   Short Circuit skill; triage findings, run targeted and existing full gates,
   refresh source-bound legacy proofs as required, package/build/preflight.
   Commit focused stages on the existing feature branch and update PR6; no merge.

## Validation

Use the repository's Python 3.14 / frozen uv environment and existing CI commands.
Start with focused semantic tests, then the fast and extended legacy suites,
property stress and affected independent preflights. No dependency/toolchain
migration: existing Ruff checks are used; adding repository-wide new type-checker
or coverage gates is deferred because it would be a separate migration.

New mechanics require deterministic oracle conformance, equivalent-build
acceptance, invalid-action rollback, privacy, repeatability, exact replay,
save/load, HTTP persistence and positive/negative qualification checks. A source
digest change requires checking existing immutable proof binding workflows.

## Current checkpoint

- Plan commit `54876aab`; implementation based on `bf86ce8c`.
- Implemented the new family, compact diagnostics, lazy schema catalog, validated
  options, author documentation, live example, paired matrix and MindTrial YAML.
- Independent review completed with three findings fixed; see
  [review](model-revision-review.md). The four-reading figure is explicitly a
  reading-only certificate; live mixed-feedback shortcuts remain documented.
- The selected-seed preflight now independently enumerates every 0/1/2/3-reading
  intersection in addition to the production certificate search. Selected cases
  check 608,685 / 608,685 / 585,276 / 7,393,585 triples independently.
- 879 fast tests, nine solver tests, two cross-seed stress tests passed. The final
  source adds one registry regression and independent lower-bound enforcement;
  35 focused final-source tests pass. All 51 extended tests passed, including
  every new behavioral class and exhaustive older-family live/replay checks. No paid executions or public MindTrial changes.
- All 16 legacy/new preflight/reference gates passed. Final ten-cell admission is
  retained in `model-revision-preflight.json` and was repeated from an installed
  wheel, including the exact release binding. CLI generate/qualify/solve/replay,
  author example, YAML parsing/bindings and changed-module Ruff checks pass.
- All 32 generated prior-family episodes match `bf86ce8c` exactly after excluding
  random episode IDs and the expected repair release identity. Prior physics,
  controls, evidence and seeds are unchanged in these comparisons.
- Dynamics reference regenerated through its independent checker; unchanged repair
  proof and witness identities plus 15 construction/conformance/qualification
  gates were verified before refreshing the full-source release binding.
- Publication/CI pending. No local Docker/Podman binary is available; actual-image
  execution is delegated to the existing CI container job. Resume by checking
  the PR6 feature head, publishing the verified tree with an expected-head
  lease, then watching both CI jobs. Do not repeat finished proofs
  unless source changes invalidate them.

## Performance and scope

The prior compiles 20,736 constructions into 748 exact behaviors, with immutable
transition/observation tables and bitset posteriors reused per process. Cold compile
was about 0.63–1.01 seconds locally (the latter during concurrent tests); a warm
lookup was about one microsecond. These are observations, not a cross-machine SLA.
Generation does not execute the exhaustive proof or certificate search. Operator
checkpoints copy only the newly committed trace suffix, and the compact terminal
summary projects the existing snapshot without another inference replay.

Automatic installed-package plugin discovery remains deferred until package code
can be bound into qualification provenance. The supported human extension path is
one explicit catalog registration, with family-owned schemas/options and optional
shared discovery mechanics. No generic simulator or dependency migration was added.

## Decisions

- Keep unknown representation bounded and public at the primitive level. Exact
  finite-data inference needs this restriction; do not claim unrestricted science.
- Accept common or equivalent winning models. Difficulty is goal-relevant
  ambiguity, not mandatory identification of irrelevant internal details.
- A provisional explanation is optional assistance and an experimental factor.
  It cannot prove that the player personally underwent belief revision.
- Report qualification limits honestly if one/two-reading or synchronization
  shortcuts survive; preserve shallow controls rather than outlawing good play.
