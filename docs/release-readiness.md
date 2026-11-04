# Release readiness — 4 November 2026

NEXUS is being prepared as an **experimental research framework**, with human
play and mechanically scored model interaction. The intended release does not
claim a calibrated leaderboard, a universal model ranking, or a reliable
strongest-model failure boundary on the T/D axis.

## What this preparation changes

- Shared strict turn validation across HTTP, JSONL and Python prevents accidental
  fractional/boolean turn coercion. Unqualified legacy metadata fails before play.
- Attachment filenames and symlink targets are checked before export; private
  world files and audit bundles use owner-only POSIX permissions. Modular rules
  cannot produce values outside the artifact domain.
- Newly generated legacy worlds use secret-backed opaque IDs, closing a seed
  dictionary-recovery channel. Historical saved worlds retain their IDs.
- Human play uses the player observation boundary. The guided local demo needs
  no model account. The explicit operator observer remains available separately.
- Private audit exports preserve source binding, public exchanges, accepted trace
  and outcomes; a verifier checks file integrity and exact replay.
- Exact physical continuation diagnostics support disclosed planning and
  interference worlds, including the first action that makes a budget infeasible.
- Result summaries distinguish world/evidence outcomes and provider errors. The
  launcher stops subsequent groups after recognized provider failures. Incomplete
  or missing results remain visible.
- Current entry docs are organized by reader. License/metadata, frozen lint,
  clean-distribution checks and fresh-world CI coverage are included.

The evaluated game laws, targets, action costs, and `sealed-facility-v1` model
presentation remain unchanged. Diagnostic/schema additions and opaque IDs still
change runtime identity: use new source bindings and matched controls for new
runs. Historical empirical reports are preserved. Current preflight artifacts
have `-current.json` filenames and are not historical result sets.

## Validation

Validation is recorded in the [release validation report](research/release-validation-2026-11-04.md)
and CI. The final fast suite passed **1,506 tests**. The local checks cover
input/privacy regressions, replay and lifecycle export, provider-stop behavior,
player rendering, frozen dependencies, package installation, and source-bound
proofs. The new continuation implementation was cross-checked against an earlier
independent scalar/BFS audit: all **64 trajectories and 1,321 accepted-action
prefixes** matched exactly. This re-executes recorded actions; it is not a new
model trial or verification of historical receipts with their original secrets.

Current repair qualification must pass the independent stored-proof check,
finite conformance tests and all 7,203 live policy/receipt/replay cases before
its source binding is refreshed. Current cross-axis and fresh-world reports must
recompute from that final source. A fresh implementation review checks the
research export and transport boundaries separately from their author's tests.

## Before publishing

1. Merge the reviewed candidate and require green CI, including the Docker
   build, source-bound preflights, packaged launcher and actual service/client/
   validator smoke checks. Docker is unavailable in this local editing environment;
   remote container checks remain a separate gate.
2. Confirm the repository's intended public contents and visibility, select the
   release/tag, and publish only after owner approval. No repository visibility,
   package publication, or release tag is changed by this preparation.
3. Run a small live harness canary on the exact candidate before new empirical
   claims. Local reference policies cannot validate a provider's current tool or
   structured-output behavior. No paid calls are part of these code checks.

The outstanding empirical panel remains Flash F17–F26 once, Grok F25/F26 once,
and Astra F21/F22 twice (16 challenge attempts). On this new runtime, first run
matching controls for each selected model/settings pair. This panel clarifies
availability gaps and the observed failure; it does not establish a leaderboard.
See [the latest assessment](research/fresh-world-results-2026-11-04.md).

## Deliberate limits and next research

The HTTP service has no authentication or tenant isolation. Audit checksums are
not signatures, capture is bounded, and semantic reconstruction of every public
response remains an independent analysis task. See the
[research guide](research-guide.md) and [security scope](../SECURITY.md).
A broad static type-checking migration is still future maintenance work.

Prioritize new breadth/dependency contrasts with disclosed laws and sufficient
resources, then measure resource curves. Keep T/D controls and evidence-support
analysis. More fresh seeds, repetitions and predeclared sampling are needed for
stronger comparative claims. The goal is a repeatable, auditable challenge across
several dimensions; no single axis needs to explain every failure.
