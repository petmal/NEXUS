# Public-release preparation: changes and validation

NEXUS is ready for review as an experimental research framework, subject to the
container/CI and live harness gates below. The work strengthens measurement and
reproducibility; it does not add new empirical model results or claim a calibrated
leaderboard. No paid model call, repository visibility change, release tag or
package publication was made.

The source preceding this work was `8b0a8b80425221ec4f71cc96a8ac152d5082841c`.
The resulting runtime digest is
`bb2dc0dbee12a9cf01633818638fc7b1bac4f4224fd146c441cd1af68912ccf4`.
The environment used Python 3.14.7 with the frozen dependency lock. The lock and
clean-distribution flow were also checked using CI's uv 0.12.21.

## Defects and interpretation

| Issue | Correction and practical effect |
|---|---|
| Legacy episode IDs exposed a searchable seed hash | New IDs use the verifier secret in an HMAC. Saved historical IDs still load unchanged. |
| JSONL truncated fractional turn values | HTTP, JSONL and Python now reject invalid turn types consistently before state changes. |
| Missing legacy qualification metadata could fail after committing an action | Session creation rejects the malformed compiled world before play. |
| Attachment filenames could escape the output directory | Basename validation and symlink checks reject unsafe output paths. Private world files are written atomically with owner-only permissions. |
| Modular effects could exceed the artifact value domain | Modulus validation enforces the bounded 0–10 representation. |
| Human play exposed objects and apparatus in other rooms | The player renderer consumes only the public observation. The whole-world observer is explicitly an operator view. |
| Batch stopping recognized only rate limits | Billing, authentication, permission, request and server errors are classified separately and stop later groups. Raw results and earlier planning errors remain intact. |
| Long text logs obscured research outcomes | Compact summaries and private structured exports retain separate physical, evidence, resource and provider outcomes. |

Independent review found two additional readout errors during implementation:
raw model errors were counted as provider errors, and a null compact-summary field
could hide a known legacy physical goal. Both were corrected and given regression
tests. The [review](release-implementation-review-2026-11-04.md) found no remaining
blocking defect within its stated scope; this is not a security certification.

## Research records

The new audit bundle records runtime binding, private compiled world, public
exchanges, accepted-action trace and final diagnostics. Its verifier checks
integrity, exact replay and original receipts, while distinguishing evaluator
closure from ordinary shutdown. It explicitly does not authenticate a provider
or independently reconstruct every public response. Capture limits and partial
exports are visible; no audit endpoint or active-player planning hint was added.
See the [research guide](../research-guide.md).

Exact continuation costs are available for disclosed planning and interference
worlds. They include retrieval, movement and finish, and identify the first action
that leaves no solution within the remaining budget. All 64 historical P/R
trajectories and 1,321 action prefixes matched the earlier independent scalar/BFS
calculation. The [compact result](release-cost-validation-2026-11-04.json) records
that comparison. Re-execution used a new secret; it is not original historical
HMAC verification or a new model evaluation.

## Validation record

| Check | Result |
|---|---|
| Targeted release input, audit, readout and summary tests | 94 passed before the final broad run |
| Independent review | 9 audit and 67 readout/summary tests passed after review fixes |
| Repair proof/conformance/runtime gates | 30 tests passed, including all 7,203 live policy/receipt/replay worlds |
| Rebound repair profiles | P0 won in 14 actions; P1 in 15; both replayed exactly |
| Dynamics/transfer reference compilers | Independently checked and current; repair binding refreshed only after gates |
| Cross-axis qualification | All 56 conditions passed on current source |
| Fresh-world qualification | All 32 fresh/anchor rows and 30 scientific contrasts passed |
| Historical continuation cross-check | All 64 trajectories / 1,321 action prefixes matched |
| Property/stress tests | 3 tests passed; 3 seeds × 24 legacy profiles plus deterministic transitions and matched resource variants |
| Wheel and source distribution | Each installed in isolation; help/demo/generate/qualify/solve/replay and repair binding passed, including CI's uv version |
| Actual HTTP and JSONL audit flows | Both won, validated, closed exports and verified original receipts |
| Actual fresh-world service/client/validator flow | All 26 cases won with public support; 4 additional forged-receipt controls rejected |
| Lint, current documentation links, diff whitespace | Passed |
| Broad fast suite | **1,506 passed**, 52 slow/stress cases deselected, 3 expected malformed-fixture warnings; 315.60 seconds |

The first broad pass found the expected old-ID/observer assumptions and package
guide links. Tests now normalize only the intentionally changed ID before checking
all historical golden bytes, and require entering the apparatus room before
expecting its display. Package links distinguish current proof from historical
validation. All nine affected cases passed targeted rechecks. The final clean
rerun then passed all 1,506 fast cases. The later documentation-only package
link/command refinements also passed the packaged-guide test.

Three Pydantic warnings in the broad suite arise from tests that deliberately
construct malformed tuples or non-normalized enum fields. They are not observed
failures in valid compiled worlds. The separate slow suite beyond the exhaustive
repair gate was not rerun locally; ordinary fast CI and explicit full CI retain
those broader checks.

## Release boundary and next step

Current-source proof files are separate from dated historical reports. The
compiled game laws, targets, budgets, required finish semantics and versioned
model presentation were preserved. New source identity still requires matched
control admission before live challenge runs; old control receipts do not admit
a changed runtime.

Docker is unavailable in this environment. CI now covers fresh-world trigger
paths, image qualification, actual service checks, and the packaged launcher.
Require its green result before release. Then run a small live harness canary on
the candidate to check provider/tool behavior, followed by the bounded missing/
confirmation panel if desired. No local reference policy can replace that check.

The public service still has no authentication or tenant isolation. Keep the
operator/private-data boundary in the harness; do not deploy it as an open web
service. Broad static typing and exhaustive response-semantic audit remain future
maintenance work, not claims of this release. See [release readiness](../release-readiness.md)
for the owner publication decision and the next research priorities.
