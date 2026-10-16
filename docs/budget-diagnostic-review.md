# Independent budget diagnostic implementation review

Reviewed the working diff on `feat/theory-prior-axis`, including the design and implementation plan, without modifying implementation. The main agent was concurrently finishing documentation and regression tests; their temporary absence was not treated as a defect.

## Findings

### P2 — Preflight verification does not bind the four pair results to the matrix inventory

Location: `src/nexus/evaluation/budget_diagnostic.py:99–108` (`verify_binding`).

The validator checks that the report has four pair objects and that three fields in each are truthy. It never checks their `pair` identities against the four expected matrix pairs. Starting from a real successful preflight, replacing `report["pairs"]` with four copies of its first `gemini-05` entry still passes verification. This accepts an incomplete report with no pair-level evidence for Gemini 493, Gemini 542, or Grok 438 despite the explicit requirement to reject incomplete preflights. In the same report, changing a row's `model` to `wrong-model` and `pair` to `unrelated-pair` also passes because the row identity comparison covers only `id` and `environment`.

Fix: require the exact unique pair-name inventory and compare every row's model/pair assignment to its matrix cell. Require proof flags to be literal `True`, rather than accepting arbitrary truthy values. Add negative tests for a duplicated pair result, wrong pair identity, wrong row model/pair, and nonboolean proof flags.

### P2 — The fixed diagnostic admits arbitrary pilot model IDs and reasoning configurations

Location: `src/nexus/evaluation/budget_diagnostic.py:18–23,59–78` (`ModelCondition`, `BudgetDiagnostic.inventory`).

The design fixes exact prior model IDs and reasoning settings, but model and reasoning are unconstrained strings. Inventory validation checks providers and seeds only. Changing the checked-in Gemini condition to `model="different-model"` and `reasoning="low"` still constructs a valid `BudgetDiagnostic`; a fresh structural preflight can therefore label a different experiment diagnostic-ready. The digest proves consistency with the modified matrix, not compliance with the fixed diagnostic's configuration.

Fix: validate the exact provider/model/reasoning/token-limit configurations for this version, or use an explicit versioned experiment definition that validates against those pinned values. Test model ID, reasoning, and token-limit drift. The currently checked-in matrix has the expected values; this finding concerns the advertised admission guarantee.

## Verified behavior

- `PYTHONPATH=src .venv/bin/python -m pytest -q tests/unit/test_decision_diagnostics.py tests/unit/test_budget_diagnostic.py tests/integration/test_operator_diagnostics.py` — **22 passed**.
- A separate live edge trace applied a correct treatment only after first previewing it, submitted in the wrong room, submitted after dropping the seal, and obtained a no-signal seal sensor result. All three ineligible finishes retained the full prior; the no-signal result did not count as passive evidence; an active operator snapshot left state hash and committed trace length unchanged; the later successful finish remained a compatible, unsupported win.
- Submission classification occurs before eligible rejection filtering. Successful finish is not fed back into the public posterior.
- The tracker follows committed `operate` results, not `configure` or previewed `probe` results.
- Active action responses do not carry terminal performance, extended readings are private operator output, and shutdown reporting does not finalize the attempt.
- Default metadata serialization omits the new standard profile field; named diagnostic budget/profile/certificate/allowance checks reject arbitrary budget edits.
- The actual eight-run preflight completed with all required qualification/live-win/replay checks. Pair science/action/event comparisons passed for the supplied matrix.

No P0/P1 finding was identified. The two P2 cases above were reproduced against the actual code. These findings were sent to the main agent during the review so repair can proceed before release.

## Owner disposition

Both P2 findings were valid and are fixed. The preflight now checks exact pair
identities, row model/pair assignments, literal boolean proof flags, and bounded
reference actions. This diagnostic version rejects model, reasoning, token-cap
and request-rate drift from the recorded pilot conditions. Negative tests cover
duplicated pair summaries, row identity changes, truthy nonboolean flags, and
model/reasoning/token drift. All 58 focused tests pass after these fixes.

The v2 response parser and optional adapter capabilities are retained; v3 is an
additive audited subclass. A recorded v2-shaped response still parses, and the v3
JSON schema matches its runtime model. No additional blocker remains from this
review. Full release gate results are recorded in budget-diagnostic-validation.json.
