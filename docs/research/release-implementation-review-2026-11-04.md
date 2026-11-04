# Release implementation review — 2026-11-04

Read-only review of the current uncommitted release-hardening implementation in the repository, against `AGENTS.md`, the release preparation plan. No tracked files were edited. Qualification/source bindings and the new current report files were intentionally pending and were not treated as defects.

The later [release validation](release-validation-2026-11-04.md) records final gates.

## Judgement

No remaining blocking defect was confirmed in the reviewed audit export, player projection, continuation-cost hooks, provider-stop integration, or distribution/CI changes. Two concrete readout defects were found during review, communicated to the parent, fixed in the working tree, and verified below. This is a bounded implementation review, not an independent hosting-security or full-release attestation.

## Findings resolved during review

| Finding | Reproduction and impact | Inspected resolution |
|---|---|---|
| Raw model errors mislabeled as provider errors | In `examples/mindtrial/summarize-pilot-results.py`, the new aggregate fields counted every `Kind="Error"`. A fixture with `model returned no actionable content (stop reason: length)` yielded `provider_error_attempts=1` and `completed_without_provider_errors=false`, while its own row correctly had `provider_error=null` and `outcome=response_length_without_text`. This conflated completion/model behavior with provider availability. | The current code retains all raw errors in `error_attempts` and computes provider aggregates from recognized row `diagnostics.provider_error`. The length-error regression passes. |
| A null compact-summary field erased known legacy goal satisfaction | `attempt_diagnostics` selected the compact summary when there was no `decision_diagnostics`. `compact_summary` supplied `physical_goal_satisfied:null` for legacy episodes, so `dict.get(key, performance.goal_satisfied)` returned null even when the full legacy performance contained `goal_satisfied:true`. The same complete block reported true without a summary and null with one. | The readout now falls back when the summary value is null, preserving historical summaries; the compact summary also projects legacy `goal_satisfied`. The added old-summary regression passes. |

Both were medium-priority research-readout correctness defects. Neither changed game state or the raw harness result.

## Review evidence

- Ran the existing Python **3.14.7** interpreter directly from `.venv`, without uv sync or environment rebuild.
- `python -m pytest -q tests/unit/test_research_audit.py --maxfail=1`: **9 passed in 3.70s**.
- `python -m pytest -q tests/unit/test_pilot_readout.py tests/unit/test_operator_summary.py --maxfail=1`: **67 passed in 2.17s**, after the above fixes.
- Independently reproduced both original readout defects with small local fixture calls before their fixes. No paid/model calls were made.
- Parent-reported additional evidence, not rerun by this reviewer: continuation results matched an earlier scalar/BFS audit over **64 historical P/R trajectories and all 1,321 accepted-action prefixes**.

## Boundary and exactness assessment

**Audit lifecycle.** `AuditRecorder` creates a new owner-only destination, writes the private compiled world separately from captured public exchanges, and leaves an open manifest until normal close. HTTP records transport responses through the existing outer ASGI boundary; JSONL records parser failures and output delivery failures. Recorded trace write errors do not replace a committed action's player response, and capture overflow/write errors fail coverage closed. Early evaluator finalization is separately recorded and reconstructed during verification; normal shutdown/EOF retains an active attempt as active. No audit endpoint or active-player physical-cost projection was found.

The verifier's stated limit is appropriate: it verifies byte inventory, source/episode bindings, exact accepted-action replay and original receipts, lifecycle state hashes, and exchange coverage/order. It explicitly does not claim independent semantic replay of every public response or provider authentication. I did not report those deliberate exclusions as defects.

**Continuation costs.** The planning hook searches vectors plus disclosed locations, includes retrieval of a dropped seal, and treats collapsed states as unreachable. The interference hook searches reverse transitions from the actual target rather than incorrectly using distances from the initial vector. Both include take/finish costs. The reporting layer retains the first infeasible/unreachable prefix, reports unknown for unsupported or hidden-law families, and does not expose diagnostics to an active player. I found no mismatch in these inspected semantics. Current tests and the parent's historical cross-check support the claim, subject to the supported-family boundary.

**Human player.** Normal play now calls `render_player(Session.observe())`; the renderer enumerates only observation-provided entities. Full observer/private data require the explicit unscored operator option. Public strings in the new player view use literal text rather than Rich markup interpretation. Quit, EOF and keyboard interruption do not manufacture a failed game. Guided demo is clearly labeled an unscored reference solution.

**Provider/readout.** Recognized HTTP billing, rate, authentication, permission, request-rejection and server errors stop later launcher groups while retaining raw records. Diagnostics keep previously proven budget infeasibility separate from provider interruption. The classifier intentionally does not infer provider outages from bare numeric text, a length stop, or no-actionable-content. Unclassified failures remain unclassified; this is not proof every possible provider error wording is recognized.

**Distribution/CI.** Inspected license/metadata inclusion, isolated wheel/sdist installation workflow, frozen runtime dependency export, source-binding admission, fresh-world CI trigger/build/preflight/service additions, and the shared packaged readout dependency. No concrete new packaging defect was confirmed. A Docker build, clean distribution installation, full qualification refresh and remote CI were not run in this review; the parent still owns those release gates. Stale source-bound failures or not-yet-created current reports are expected until that work completes.

## Limits and follow-up

- Audit writer attachment/closure is assumed to occur at a quiescent lifecycle boundary, as the HTTP lifespan and serial CLI paths do. Concurrent direct API mutation while attaching or closing a recorder was not established as a supported contract.
- Filesystem permissions and safe output paths do not provide protection against an operator actively racing filesystem replacements. The docs correctly keep this as a trusted local research service, not a hostile multi-tenant host.
- The source tree was being amended by the parent during review. Re-run final gates against the frozen final tree, regenerate current source/proof bindings, and retain this report as advisory evidence rather than proof of the eventual commit's complete release status.
