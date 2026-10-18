# Terminal diagnostic latency fix — 18 October 2026

The 22-11-11 pilot exposed four internal HTTP timeouts. In three cases the mission
had already won; in the fourth, an action exhausted the budget. State committed
before synchronous terminal diagnostics returned. Cold combined inference-table
construction took up to 13.36 seconds against a 10-second client deadline. Episode
generation was not the bottleneck (116 attempts: median 0.094 s, max 0.479 s).

## Change and invariant

The complete three-channel observation partitions are now compiled offline from
scalar laws into `ontology/transfer/observations.json` (747,408 bytes). The loader
checks content identity, semantic source identity, dimensions, bounded decompression,
complete/disjoint partitions, and returns immutable tuples. Missing, changed or
stale assets fail closed. CI reconstructs every mask and compares the artifact.
Runtime behavior labels come from the existing verified reference asset.

The tables cover the whole prior, not selected seeds; random seeds still work.
No session state, readings or receipts are shared. There is no background worker,
new runtime dependency or private solution endpoint. Scalar full-domain victory
acceptance, evidence, actions, budgets, schemas and terminal-only disclosure stay
unchanged. Terminal compile logs now identify `source=verified_asset`.

Action requests allow 45 seconds, inside the existing 60-second MindTrial tool
limit. Health retains 1 second; status/evidence/finalization retain 10 seconds.
The latency removal is the primary fix; extra action headroom is secondary.

## Proof and release gates

- `scripts/compile_transfer_observations.py`: recreate every base channel/program/query
  mask from scalar laws. `--write` is only for deliberate artifact regeneration.
- `scripts/compile_transfer_reference.py`: unchanged policy bytes and 9/10-reading
  bounds. It uses independently computed labels; it does not load the artifact it
  is rebuilding. When laws change, rebuild observations first, then reference.
- Independent full-domain oracle and all policy branches retain their tests.
- Fresh-process HTTP tests cover both families, wins, budget exhaustion and
  explicit finalization. No scalar signatures or target compilation may occur.
- Corrupt/stale/truncated/oversized/invalid-partition assets are rejected.
- Existing privacy, exact receipt, replay and source-bound release tests remain.
- Installed wheel tested outside source checkout; artifact loaded and public
  policy won with evidence-supported receipt.
- Fresh review found and resolved the offline reference regeneration dependency
  cycle and strengthened its missing-asset regression.

Controlled same-host, three-process medians for complete public reference play,
including cold terminal diagnostics (imports excluded):

| Family | Before | After | Speedup |
|---|---:|---:|---:|
| Calibrated transfer | 1.479 s | 0.035 s | 42.2x |
| Coupled evidence | 2.696 s | 0.052 s | 52.2x |

Raw samples are in `terminal-diagnostics-performance.json`. This is not a target
container latency SLA. Rerun telemetry should verify the improvement on the user's
host. No paid model requests were used.

## Resumption / validation ledger

Implementation lives on `feat/theory-prior-axis`; no main merge. Existing repair
proof and serialized witnesses are unchanged; their source binding is refreshed
only with regression/conformance gates. Existing repository-wide type/coverage
migration remains outside this repair; touched-module static checks are separate.
Final gate outcomes and image CI are recorded in `terminal-diagnostics-validation.json`.
The ten-row follow-up is `astra-diagnostic-matrix.json`; its preflight has exact
source binding, public-policy wins, replay, and restricted-observation closures.

Release commit `680e4f5034ff25e32339ecbd04a38eea6513eec1` passed the complete
[CI run](https://github.com/petmal/NEXUS/actions/runs/39148658419), including Docker
build, OCI revision validation, legacy image preflights and all ten new matrix
rows inside the image. The first image attempt caught an omitted Docker-context
allowlist entry for the new matrix; that packaging omission is corrected.
