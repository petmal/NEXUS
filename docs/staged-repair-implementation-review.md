# Fresh staged-repair implementation review

Reviewed the working implementation on `feat/theory-prior-axis` against base `ca471a6702a4da8be9023b4846acef7cc24b2ae6`. Read-only review: no production changes, paid evaluations, network requests, or further agents. Read AGENTS.md, approved design/implementation ledger, the Short Circuit review guidance, all staged ontology modules, both new evaluation modules, registration changes, matrix/YAML, focused tests, and the relevant shared engine/session/diagnostic boundaries. The guide appeared during the review and was also inspected.

## Finding status

**Resolved. No open findings from this review.**

### Resolved P2 — Matrix input errors preserved a stale successful preflight report

**Original location:** `scripts/preflight_staged_repair.py:14` (the matrix-loading call preceding `nexus.evaluation.staged.preflight`). The following records the original finding, before the verified fix.

`Pilot.model_validate_json(args.matrix.read_text())` runs before `preflight()` resets the output to `status: running`. If a matrix is missing, malformed, or fails schema validation, the command exits nonzero while an older report at the requested output path still says `status: passed`. This breaks the advertised fail-closed persisted artifact contract precisely when an operator is checking a changed matrix. The existing source-failure regression exercises only failures after `preflight()` starts, so it does not cover this path.

**Executed reproduction:** created a temporary output containing `{"status":"passed","old":true}`, supplied a matrix containing only `{"version":"staged-repair-pilot-v1"}`, and invoked the real CLI with both paths. It exited 1, and the output still contained the original passed document. A missing path takes the same pre-initialization path.

**Suggested repair:** initialize/invalidate the output before matrix I/O and validation, and wrap those stages so input errors persist `status: blocked` with an error. Add subprocess regressions for invalid JSON/schema and a missing input path, starting from an existing successful report. Keep a nonzero exit code.

**Resolution verified:** the CLI now writes a running report before reading the matrix, catches matrix I/O/JSON/schema failures, writes a blocked report with the error, and re-raises for a nonzero exit. The new real-subprocess regressions cover missing input, malformed JSON, and an invalid schema, each beginning with a stale passed report. Ran `uv run pytest -q tests/unit/test_staged_matrix.py -k cli_invalid_matrix_replaces_stale_pass`: **3 passed, 3 deselected in 1.40s**. This follow-up was limited to the single finding.

## Positive findings and limits

- The physical repair uses actual seal identity, immutable tags, carried location, current room, and all nine residual loads. Survey copies cannot substitute for actual seals.
- Every public reader result contains only the disclosed stage/carrier/tag trit plus already-public fields. Reader results are baseline copies regardless of cumulative treatment; trimmer and anneal previews reveal only public transformations. No new active-play truth or qualification leak was found.
- Configure, probe, operate, take/drop, and finish preserve canonical-engine charging and transactionality. The mission tracker follows committed doses rather than previewed doses or trimmer settings. An ineligible failed finish does not exclude a possible world; an eligible rejected full repair does.
- The finite-law implementation and independent scalar checker agree over the complete supported query/treatment domain exercised by the tests. Fixed-panel minima, adaptive upper bounds, actual-world certificates, and finish-inclusive feedback ceilings have appropriately separate meanings. I found no mathematical overclaim in the current implementation or guide.
- The new family is additive through the registry and payload map. Legacy action contracts and transition code are unchanged. The known temporarily stale legacy release manifest was deliberately not treated as a newly discovered bug.
- The Python source bindings and their end-of-preflight recheck are present. Failures inside preflight rewrite the report as blocked; the verified CLI fix now covers input failures before that function runs as well.
- No P0/P1 finding. This review does not establish live-model difficulty, exact action minimax, or production deployment readiness.

## Verification

Executed:

```sh
uv run pytest -q -m 'not slow and not stress' tests/unit/test_staged_repair.py tests/unit/test_goal_information.py tests/unit/test_staged_matrix.py tests/integration/test_staged_service.py
```

Result: **33 passed, 1 deselected in 20.08s**. The selection includes all 20 proof profiles through matrix preflight, runtime/oracle payload checks for all 216 worlds, public HTTP play, receipts, deterministic replay, private terminal diagnostics, and cold-process timing. The deselected test is the separate all-world/all-profile live-policy stress case. Full legacy/CI gates and final regenerated-source checks remain the implementation owner's release verification.

The repository currently exposes Ruff configuration but does not supply the Short Circuit skill's complete lint/type/coverage toolchain or Makefile gates. This is pre-existing tooling debt, not a blocker introduced by this feature; this read-only review did not migrate the toolchain.

Follow-up owner evidence: the legacy proof/source manifest was refreshed after 15 construction/conformance/qualification tests passed and proof/witness identities were rechecked. That broader release verification was reported by the implementation owner and was not rerun during this narrowly scoped follow-up.

## Packaging follow-up review

A separate narrow read-only review of `e25887e8aa9836d7880ccd42cecfd4a53e10fba4`
found no issues. All seven Docker-copied matrix files have build-context exceptions,
and the regression detects the original omission. Container job eligibility
matches the former step condition exactly; its complete smoke command block is
unchanged. Independent checkout, inherited read-only permissions and a 60-minute
timeout are configured. Runtime source files are unchanged. The container and
follow-up fast gates subsequently passed in CI run 39300712416.
