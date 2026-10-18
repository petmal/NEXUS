# Evidence/transfer implementation ledger

This is the durable resume point for the approved feature work.

## Phase 0: baseline and plans

- [x] Read AGENTS.md, architecture, current families and skill guidance.
- [x] Confirm local clean `b36703d` equals PR 6 head.
- [x] Write system design and this execution plan before source changes.
- [ ] Baseline fast regression result (running; `/tmp/nexus-baseline-fast.log`).

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

17 October 2026: plans written; candidate construction is not yet qualified.
Python 3.14.8 runtime restored. Baseline fast tests started. Next: independent
finite prototype and design review. No production code changed yet.
