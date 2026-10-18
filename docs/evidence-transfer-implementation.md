# Evidence/transfer implementation ledger

This is the durable resume point for the approved feature work.

## Phase 0: baseline and plans

- [x] Read AGENTS.md, architecture, current families and skill guidance.
- [x] Confirm local clean `b36703d` equals PR 6 head.
- [x] Write system design and this execution plan before source changes.
- [x] Baseline fast regression: 633 passed, 46 deselected, three existing warnings.

## Phase 1: independent finite proof

Implement a bounded standard-library PoC independent of NEXUS runtime. Enumerate
the full grammar and behavior classes, reader observations, restricted closures,
mission ablations, public reference policy, and shortcut bounds. Record runtime
and memory. Obtain fresh-context design judgement per Short Circuit skill.
Resolve findings before runtime implementation. Perform selective-revision PoC
and explicitly state which claims pass, fail or remain unknown.

Expected files: `scripts/poc_evidence_transfer.py`, proof JSON and explanatory
`docs/evidence-transfer-proof.md`, independent review, unit oracle tests.

## Phase 2: runtime and public inference

Implement a cohesive `ontology/transfer` adapter with typed schema, laws, evidence,
runtime, inference, generation, public policy and qualification. Register the
two versioned calibrated/combined families. Preserve existing defaults and
serialization. Add necessary CLI/service family selection without changing
existing profiles. Validate complete round trips, transaction rollback,
immutable probes, raw versus physical semantics, acceptance and live receipts.

Reuse equivalence-class masks and compiled outcomes; benchmark cold/warm paths.
Do not put proof search in per-task generation. Add terminal-only diagnostic
information for reference use, measurement scope and unresolved mission groups
where exact public-evidence inference supports it.

## Phase 3: coverage, docs and pilot

Create a small diversified paired matrix with an execution control, calibrated
transfer, combined evidence and generous-budget diagnostics. Preflight every
row by generated identity, claimed obstruction, reference win and exact replay.
Include both sides of appropriate indistinguishability pairs. Public instructions
must be self-contained; a player-only walkthrough begins with actual public
files and introduces observations in chronological order.

## Phase 4: integration validation and delivery

Run targeted tests, then existing fast/slow/stress gates in bounded partitions.
Refresh release/source-bound proof assets using existing scripts; never weaken
old certificates. Run installed-wheel and CLI/preflight smoke, applicable static
checks and independent implementation judgement. Commit by phase, update this
ledger, sync the approved feature branch and verify remote tree/CI as available.
No main merge or paid model testing.

## Current checkpoint

18 October 2026: independent oracle and fresh design review exposed the original
reader shortcut. Refined n2-companion design adopted and plans updated. Full
physical prior has 5,184 programs/5,016 behaviors; combined prior 15,552 worlds.
Public offline witnesses compiled: 9/10 readings, 310,700-byte policy asset.
Revision is withheld: this stationary two-context construction permits early
transition/joint inference, so required revision is not established.

The runtime adapters, registry/schema admission, public contracts, exact
posterior, terminal logs, immutable policy cache, CLI and image preflight are
implemented. Fresh implementation review found no remaining correctness blocker.
It found that combined passive observations resolve the whole prior; that
negative ablation is now explicit in the oracle, matrix, tests and operator guide.
Three delta-reader alternatives lost structural survey ambiguity and were rejected.

Completed gates:
- Every independent policy branch; exhaustive independent arithmetic.
- All 20,736 worlds win through live Session, within 33/37 P1 actions, with
  evidence-supported receipts and exact replay. Source-bound checkpoints saved.
- 652 fast tests plus the subsequent assertion-disabled-proof regression pass
  (653 unique fast tests); 20 final targeted tests pass.
- Two three-seed property/stress tests pass.
- Installed isolated wheel: release identity, generate, public qualify,
  omniscient solve/replay, and all 13 matrix rows pass.
- New-module Ruff/Pyright, whitespace, immutable policy recompilation pass.
- Public-only walkthrough and measured cold/warm performance are saved.

Remaining at this checkpoint: finish the 45-test extended gate, synchronize the
feature branch, verify actual-image CI, and record the final tested commit.
No paid model calls, main merge, or MindTrial changes. Resume commands and proof
limits are in `transfer-pilot.md`; full live verification uses
`scripts/verify_transfer_live.py` with explicit seed ranges and checkpoints.
