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

- Base `bf86ce8c`; no old family removed or default changed.
- Candidate proof complete: 20,736 wirings, 748 exact behaviors, independent
  all-history equivalence/conservation and complete legal-query coverage.
- Compact summary, lazy collision-checked registry, schema-owned options and
  `model-revision-v1` implemented. Targeted semantic tests pass.
- Ten-cell paired matrix preflight passed; YAML and image/CI wiring added.
- Author guide and executable example added. Independent implementation review
  and full regression/release gates in progress; no remote publication yet.
- No paid model executions or public MindTrial changes.
- Resume: run focused revision tests, inspect independent review in
  `../revision-poc/implementation-review.md`, complete legacy gates and source
  binding refresh, then commit/publish feature branch and verify CI.

## Decisions

- Keep unknown representation bounded and public at the primitive level. Exact
  finite-data inference needs this restriction; do not claim unrestricted science.
- Accept common or equivalent winning models. Difficulty is goal-relevant
  ambiguity, not mandatory identification of irrelevant internal details.
- A provisional explanation is optional assistance and an experimental factor.
  It cannot prove that the player personally underwent belief revision.
- Report qualification limits honestly if one/two-reading or synchronization
  shortcuts survive; preserve shallow controls rather than outlawing good play.
