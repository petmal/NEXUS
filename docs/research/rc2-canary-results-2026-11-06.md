# RC2 live canary — 6 November 2026

**Result: the planned six-attempt canary passed.** Astra at medium reasoning won
all four controls and both selected P/R rows on the audited runtime. Reconstructing
the recorded interactions found no discrepancy in game transitions, win decisions,
terminal metrics or retained state hashes. This closes the small live integration
check for this model/settings combination; no additional canary rerun is needed
unless the runtime or integration changes.

Together with the completed core review, full local test collection, stress
sample and container checks, this supports proceeding with the experimental
research release. It does not establish a calibrated benchmark or certify every
provider. Merge, release/tag selection and public visibility remain owner decisions.

## Results

The archive contains one preflight folder and two completed, non-interactive
MindTrial groups. All six expected records are present once. There are no reported
provider errors, unsuccessful tool calls, invalid world actions or failed finishes.
Every first submission succeeds and is supported by the disclosed information.

| Row | Condition | Actions / budget | Tool calls | Reconstructed outcome |
|---|---|---:|---:|---|
| F01 | Disclosed model-revision control, seed 2073 | 4 / 64 | 9 | Supported win |
| F03 | Disclosed model-revision control, seed 2178 | 4 / 64 | 9 | Supported win |
| F05 | Disclosed repair control, seed 541 | 5 / 8 | 10 | Supported win |
| F08 | Disclosed repair control, seed 586 | 5 / 8 | 10 | Supported win |
| F11 | Short independent P/R world, seed 107, tight budget | 12 / 12 | 18 | Supported win; exact physical optimum |
| F12 | Same P/R world, relaxed budget | 12 / 18 | 18 | Supported win; exact physical optimum |

F11 and F12 use the same sequence: take the seal, perform ten machine operations,
then finish. The tight row succeeds on its final permitted action. The relaxed
row leaves six actions unused. Neither trajectory becomes budget-infeasible or
unreachable; both have zero excess actions. The four controls use their qualified
reference action counts. Tool calls also include free information requests and
must not be substituted for world-action counts.

One metric needs care: the P/R records each contain ten `redundant_measurements`.
These are operations whose observations do not reduce uncertainty about already
disclosed laws. They are **not ten wasted actions**: all ten operations are needed
by an optimal plan. Use the family certificate and exact physical-cost diagnostics
for planning efficiency. Likewise, the shared legacy `optimal_action_count=0`
field in these plugin worlds is not a zero-action optimum. The family certificate
explicitly identifies the P/R bound as `exact-known-law-optimum`, with 12 actions.

## Verification and its limits

The offline review checked:

- Source commit, runtime digest and recorded image identity against RC2; input,
  effective-config and task-file hashes; configured and recorded inference settings.
- All four challenge-admission references against the actual control manifests
  and result-file hashes. The challenge group used these fresh matching controls.
- Fresh-world qualification by recomputing all 32 fresh/anchor rows. All three
  captured preflight reports agree after excluding elapsed time, and their exported
  task objects match the frozen matrix.
- All **74 public request/response pairs**, associating TraceIDs and call IDs
  with MindTrial's tool telemetry; all **42 accepted actions**; successful final
  states; six terminal performance reports and operator snapshots.
- All **14 retained original before/after state-hash records**: 2 each for F01/F03,
  5 each for F05/F08, and none for F11/F12. The reconstructed traces also replay
  consistently against their regenerated worlds.

The original emitted receipt strings match the submitted answers and recorded
live validator successes. Offline regeneration uses a different verifier secret,
so receipt strings are excluded from public-response equality. The archive does
not contain the original private worlds or complete audit bundles; therefore
**original-secret HMAC verification was not possible**. Bounded service-log
collection explains the incomplete original action-hash journal. Full public
debug responses happened to survive for these six short attempts.

This is the documented harness-retention limitation, not a new NEXUS defect or a
reason to couple NEXUS to MindTrial. Researchers requiring complete private replay
should use the [framework-neutral audit storage contract](../research-guide.md#reproducibility-record).
This archive does not exercise `verify-audit` on original live bundles; the core
test suite covers that verifier separately. No new paid model calls were made
during this analysis.

Both [main CI](https://github.com/petmal/NEXUS/actions/runs/42195245242) and
[runner/container smoke](https://github.com/petmal/NEXUS/actions/runs/42195245268)
passed on `78cfdc8`, whose runtime is identical to the canary's `164cb12`.
The [core review](core-robustness-review-2026-11-06.md) records the 1,719-case local
collection, 72-world stress sample, population proofs and clean-package checks.

## Interpretation and next steps

This is an integration confirmation, not a new difficulty experiment. It tests
supplied-law controls and one short, independent planning world at two budgets.
It does not retest hidden-law T/D challenges, long coupled plans, or other providers.
The result therefore changes neither the earlier T/D/P/R conclusions nor the
research roadmap. In particular, it does not resolve the earlier Astra F21 failure.

There is no newly identified runtime fix or additional paid release check to
require from this result. Complete the final PR/publication review, retaining the
experimental scope and known audit-storage requirements. Keep the outstanding
16-challenge confirmation/completion panel as follow-up research, separate from
release admission. It should retain earlier outcomes and obtain matching controls
for each model/settings pair on the current runtime.

## Evidence identity

- Input: `rc2-results-v1.zip`, SHA-256
  `f1007173812098bf48d6bd289a6eeef60174fcbd8e312720048dfbe8dc758168`.
- Live source: `164cb123b092bb0104f6a4de950a105bf28107fe`.
- Runtime SHA-256:
  `630d5838e4c7e5964ce7585c655ebde691ed93bf85f2a9f0cd91f975d9e324ac`.
- Image ID: `5199e04e70042efbe8b51b6ca20c8bf09de84a9429d0ee109127a7536c5496e4`.
- MindTrial: `v0.25.3-0.20261026041336-f8a723665fff`; binary SHA-256
  `95c57d56e3d8739c19c4be1d33ec8de876c6522a003704c4f2d277978baf8660`.
- Provider/model: OpenAI `gpt-6-astra`, medium reasoning, structured-output default;
  evaluation seed `nexus-cross-axis-pilot-v1`.
- Machine-readable reconstruction: [RC2 audit record](rc2-canary-results-2026-11-06.json).

These identifiers bind the recorded configuration and source; they do not
independently authenticate the provider's immutable model weights.
