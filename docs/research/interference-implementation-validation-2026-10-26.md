# Disclosed interference implementation validation

The new `stateful-interference-v1` family is mechanically qualified for a first
model pilot. No model has been evaluated on this family. The source-bound
[32-cell preflight](interference-preflight-2026-10-26.json) records every cost,
restricted-strategy result, transition check and replay check. The
[guide](../interference-guide.md) defines their scope and interpretation.

## Checks completed before release

- Broad unit/integration regression: **1,183 passed**, 51 slow/stress tests
  deselected, in 280.91 seconds. Three existing Pydantic warnings occurred in
  negative/schema-normalization tests; warning filters were not changed.
- Focused independent review run: **108 passed**, covering the new mechanic,
  paired matrix/export checks, shared launcher and container build context.
- Final interference preflight: **32/32 passed**. Its exported tasks are byte-for-byte
  identical to the shipped core/slack task files. The exhaustive proof checks
  93,750 transitions for each of eight kernel/condition combinations.
- Historical coordination preflight: **40/40 passed** against the extended runtime.
  Legacy repair construction, conformance and qualification: **15 passed**.
  The unchanged repair proof and witnesses were validated before refreshing only
  its source map; no old acceptance criterion or witness was weakened.
- Real subprocess HTTP service, CLI tool and receipt validator smoke: core rows
  **02, 04, 11** and slack rows **19, 28** all achieved supported wins at exact
  costs of **21, 36, 35, 32, 25 actions**, respectively. Forged receipts before a
  win and wrong receipts after a win were rejected. Active player responses did
  not expose generation seeds, selection metadata, solution words or secrets.
- The documented CLI generation example (seed67, coupled long, R2) qualified,
  solved in **32 actions** and replayed successfully by canonical hashes.
- Changed Python files passed Ruff checking and formatting; shell syntax and
  Git whitespace checks passed. Source distribution and wheel builds succeeded.

Fresh design and implementation review found no remaining core correctness issue.
Review caught a missing Docker build-context exception; it was corrected and the
context regression test passed. Privacy wording was corrected to distinguish active
player evidence from the inherited terminal performance certificate, which may
include proof metadata after the attempt ends. The generator seed, solution word
and verifier secret remain excluded from player-facing evidence.

## Container and live-evaluation boundary

The local development host has no Docker daemon. The feature's container-smoke
workflow builds the exact PR head, runs all three preflights, checks both packaged
launchers against the actual image and exercises all new core/slack rows through
the service and validator without model calls. Its result is recorded in PR checks.
The downloadable launcher repeats the image revision/digest, source, configuration,
fresh qualification and task-export checks locally before starting MindTrial.

Run the 16 core rows and 16 slack rows once for initial coverage, retaining every
attempt. Assess completion, action efficiency, coordinate-goal breaks and reported
effort separately. Replicate selected informative matched pairs afterward; do not
interpret 32 paired variants of four kernels as 32 independent sampled worlds.
