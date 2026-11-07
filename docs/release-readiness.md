# Release readiness — 6 November 2026

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

The evaluated game laws, targets and action costs remain unchanged. Saved
`sealed-facility-v1` episodes retain their original wording; the subsequent story
review introduces `sealed-facility-v2` for newly generated episodes. Wording is
part of the evaluated input: record its version, use new source bindings and
matched controls, and do not treat old live runs as validation of the new text.
Historical empirical reports are preserved. Current preflight artifacts
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

The release-handoff follow-up adds a packaged six-attempt canary, corrects the
fresh-world regeneration command to preserve dated reports, extends current-doc
link checks and adds software citation metadata. Its **193 fresh-world and shared
runner tests passed**, including preflight-only execution, control-failure stops,
bounded model selection and packaged links. Lint and all 14 current-doc link checks
passed. It changes no runtime source or world mechanics; the qualified runtime
digest remains `bb2dc0dbee12a9cf01633818638fc7b1bac4f4224fd146c441cd1af68912ccf4`.

The RC1 live canary at `db6d043fd5dbb4a719f96858ef4d052cb5b93271` passed all
six attempts. Independent reconstruction matched 42 accepted actions and 74
public responses, excluding regenerated receipt codes. Only 14 action-hash
journal records survived bounded service-log collection; the original private
bundles were not retained, so original-secret receipt verification was unavailable.
The follow-up fixes control admission when a newer manifest is damaged or missing
and orders timestamps by their actual instants. The runtime digest is unchanged.
All 212 fresh-world/shared-runner tests passed, including 17 new regression cases;
lint and the 14 current-document link checks also passed.

Audit retention is an integration responsibility: NEXUS provides a portable
export and verifier; the calling framework supplies persistent operator storage
and collects it. MindTrial is one example adapter, not a NEXUS dependency.
Its current examples retain bounded logs rather than complete private bundles.
See the [framework-neutral storage contract](research-guide.md#reproducibility-record).

The [core robustness review](research/core-robustness-review-2026-11-06.md)
fixes stored-reference certification, negated-goal solver pruning, malformed phase
and goal values, unlimited legacy resources, and missing semantic checks of audit
metrics. It adds 135 regression cases, including independent finite-state oracles.
Audit verification now reconstructs game-derived metrics and explicitly names
the request/provider fields it does not certify. Whole-world qualification remains
a separate command. Valid generated laws and historical empirical reports are
unchanged; runtime source identity changes and current bindings must be refreshed.
The completed refresh passed all 7,203 live repair worlds, both repair profiles,
56 cross-axis conditions and 32 fresh/anchor rows. Both current reports retain
the same substantive results after removing source identity and timing fields.
The new runtime digest is
`630d5838e4c7e5964ce7585c655ebde691ed93bf85f2a9f0cd91f975d9e324ac`.
The 72-world stress sample, clean wheel/source installs, lint and current-doc links
also passed. All 1,719 unit/integration cases are now complete: 1,661 passed before
an environment interruption, then the remaining 58 passed after recovery in
50.99 seconds. The ordered test collection and runtime digest were identical.
This is complete coverage across two processes, not one uninterrupted run.

The [RC2 live canary](research/rc2-canary-results-2026-11-06.md) passed all six
Astra-medium attempts on `164cb12`. Reconstruction matched all 42 accepted actions,
74 public responses apart from regenerated receipt codes, six terminal metric
reports and all 14 retained original action-hash records. F11/F12 both used the
exact 12-action optimum. Source/configuration/control-admission bindings matched;
there were no provider errors or unsuccessful tool calls. Original private bundles
remain unavailable, as documented above. This completes the planned small live
check for this model/settings combination on presentation v1; no new runtime fix
was identified from those runs.

The subsequent [story review](research/story-review-2026-11-06.md) clarifies the
setting, terminology, action allowance and ending in presentation v2. It fixes a
routing briefing that contradicted disclosed-law controls and preserves existing
public room functions in nested maps. All changes stay in public presentation;
canonical laws and technical evidence are unchanged. Historical v1 text is covered
by golden snapshots. This review changes the runtime and public-input identity;
the RC2 model runs above do not test v2. The final repair gate, 56 cross-axis
conditions, 32 fresh/anchor rows and clean package installs passed. The current
runtime digest is
`1e064b6fd5d3a7e330e61fa04da529c2e084f05258002f668694157b4c06bb99`.
All 1,698 fast unit/integration cases passed, with 52 slow cases excluded; 31 new
regressions cover presentation and player output. Lint and current-document links
passed. See the review for the complete scope and local validation.

## Documentation review

The [documentation index](README.md) now separates first use, benchmark design
and research. The [first-model tutorial](first-model.md) uses one disclosed repair
control and an operator-selected provider/model. The [worked comparison](benchmark-guide.md)
and [metric dictionary](reference/metrics.md) distinguish physical cost, evidence
support and harness outcomes. A clean play-only install ran the demo; its nine
documented commands won. A local service using the tutorial inputs accepted the
real request client and validator, won F05 in 5/8 actions and passed private audit
verification. This was an offline control execution, not a run through a paid
provider or MindTrial. The two documented planning worlds qualified at 12 and 18
available actions, with identical goals, rooms, law specification and evidence;
the operator extension example won and replayed in 16 actions. All 111 focused
fast CLI, presentation, starter and fresh-world tests passed (three slow cases
excluded). Local file links passed in 175 Markdown documents, with heading
links checked from 17 maintained entry documents.

The previous story commit passed [CI](https://github.com/petmal/NEXUS/actions/runs/42312181012)
and [container smoke](https://github.com/petmal/NEXUS/actions/runs/42312181063).
This documentation pass changes no NEXUS runtime or historical result. At public
handoff, point the README clone command at the released default branch or tag.

## Before publishing

1. Review the candidate and require green CI on the final head before merge.
   Both [CI](https://github.com/petmal/NEXUS/actions/runs/42195245242) and
   [runner/container smoke](https://github.com/petmal/NEXUS/actions/runs/42195245268)
   passed for `78cfdc8f975123c3a9e533d6c5baba81583a4dc7`, including the actual Docker
   image, source-bound preflights, packaged launchers and service/client/validator
   checks. These are completed checks for that commit, not a promise about later
   revisions. Require new relevant checks after further changes. Extended and
   cross-seed jobs were skipped in CI; the completed local full collection and
   property run above supply those results. `make test-full` and `make stress`,
   or the CI workflow's `full=true` option, reproduce the broader gate.
2. Retain the completed RC1 and RC2 live canaries. Repeat the small check after
   changes to the game runtime or provider/tool integration. The successful
   `NEXUS-RC2-core-canary-2026-11-06.zip` run pins `164cb12` and the runtime digest
   recorded in its report, which is unchanged at `78cfdc8`. The later story review
   changes that runtime and the default presentation. Complete the remaining
   requested reviews, rebuild the canary from the final candidate, then run the
   small live check once. Documentation-only changes do not require new paid attempts.
   Launcher-only admission safeguards are
   covered by regression tests. The package's `bash run-canary.sh astra` runs four
   matching controls
   and F11/F12 (six paid attempts). See [commands and acceptance checks](../examples/mindtrial/fresh-world-run.md#small-release-canary).
   Local reference policies cannot validate a provider's current tool or
   structured-output behavior. No paid calls are part of these code checks.
3. Confirm the repository's intended public contents and visibility, select the
   release/tag, and publish only after owner approval. No repository visibility,
   package publication, or release tag is changed by this preparation.

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
