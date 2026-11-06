# Core robustness review — 6 November 2026

This pass examined the mechanics and certificates used to interpret NEXUS runs:
goal evaluation, victory receipts, stored witnesses, exact action costs, finite
world proofs, terminal metrics and private audit exports. The starting revision
was `25f52bbfc4d2eb3295c2ce79deb675be4d54fbc2`.

Five defects or verification gaps were fixed. No defect was found in the selected
shipped scientific worlds' transition laws or their independently checked cost
and winnability claims. This is bounded software verification, not a proof that
every possible generated instance or implementation path is correct.

## Findings and fixes

| Finding | Why it matters | Change |
|---|---|---|
| Legacy qualification checked a fresh solver plan instead of the stored reference plan. A same-length list of waits or an illegal first action could pass. | Physical winnability was still checked, but the shipped witness and `reference_plan_wins` result were not trustworthy. | Qualification now executes and replays the stored plan and requires its terminal receipt. Empty, malformed, illegal, nonwinning and post-victory continuations are tested. |
| Physical and belief search pruned necessary drops under negated location goals. | A legal two-action drop/finish solution to “artifact is not in inventory” could be reported as impossible. | Drop pruning tracks logical polarity. Odd negation retains every physical room; positive and double-negated goals retain the usual optimization. |
| Goal values were insufficiently validated. Fractional phases were truncated, booleans compared equal to integers, and unknown fields could crash victory evaluation. Rule phase conditions had the same truncation problem. | A malformed compiled goal or phase condition could silently mean something different from its JSON, or fail during play. | Phase predicates and numeric artifact goals require integers; artifact fields and enum values are checked; location goals require strings. Unsupported field aliases must use the proper location predicate. |
| Schema-valid unlimited resources crashed legacy execution or search. | `null` budgets or machine-use limits could trigger integer comparison/addition errors despite being represented as unlimited resources. | Engine and both physical searches handle unlimited resources consistently. Exact belief costs also preserve unlimited machine uses. |
| Audit verification replayed the trace but did not recompute stored outcome metrics. | A self-consistent set of file checksums could accompany an incorrect reported status, action count, evidence classification or continuation cost. | Verification reconstructs the session and compares game-derived performance, status, evidence witnesses and continuation diagnostics. It compares canonical JSON, including numeric types. |

The audit verifier reports `game_metrics_verified` separately from public-response
verification. Invalid-action, duplicate-request and protocol-conflict counters
are not recoverable from accepted actions alone. The result explicitly lists them,
assistance, provider metadata and external receipt-validation metadata as unverified.
Complete semantic reconstruction of public responses remains a separate check.
Checksums and recomputation establish internal consistency; they do not authenticate
an editable bundle or its external provider.
Metric reconstruction uses the compiled world's declared baselines; it does not
repeat world qualification (`world_qualification_rechecked: false`). The separate
`nexus qualify DIR/private.json` command rechecks admission. Family-specific
preflights retain responsibility for their stronger finite-population proofs.

## New independent checks

The new tests use small complete state spaces or independently expressed mechanics
where possible:

- **84 Boolean-goal/start-state combinations:** an unpruned unit-action search
  checks solvability and minimum cost against ordinary BFS, movement-compressed
  search and the guaranteed-policy solver. Cases include AND, OR, NOT, double
  negation, impossible goals and goals already satisfied at the start.
- **Receipt and finish boundaries:** independent standard-library HMAC calculation,
  Unicode canonicalization, binding to secret/episode/protocol/goal, rejection of
  foreign receipts, tampered replay receipts, last-budget-action wins, and failure
  one action short. Terminal actions cannot emit a new receipt or change the state.
- **4,096 finite-machine pairs:** all two-state, two-symbol binary-output machines
  are compared by explicit input-word enumeration. Four product states make words
  through length three sufficient to check all-history equivalence. Canonical
  signatures and shortest counterexamples agree with that oracle.
- **1,024 supporting-certificate cases:** exhaustive query subsets check the
  minimum observation count for overlapping winning sets, including impossible
  and already-supported cases. This guards against confusing truth identification
  with the weaker requirement of a common valid solution.
- **Continuation costs:** for a selected law, all 15,625 interference vectors in
  each coupling condition and every vector/room combination in all four planning
  layouts satisfy the shortest-path recurrence using independent scalar physics.
  Unreachable states are included. These checks distinguish distance *to* the
  target from distance *from* the initial state.
- **Cross-family metrics:** planning, interference, coordination, compositional
  repair and model revision runs check committed-action counts, budgets, free
  observations, invalid calls, retries, conflicts, submissions and exact replay.
  Reading metrics is checked not to mutate the game state.
- **Audit corruption cases:** changing reported status, action count/type,
  evidence classification, witnesses or continuation costs is rejected even after
  recomputing file checksums. The verifier does not claim to certify request
  counters from the action trace.

The focused additions comprise 135 regression cases. Existing tests also cover
failed-finish feedback, unsupported versus supported wins, probe immutability,
atomic invalid actions, exhausted budgets, destructive operations, all-history
machine acceptance and tampered proof payloads.

## World and guarantee review

| Area | Checked interpretation and invariants |
|---|---|
| Legacy T/D worlds | Legal execution and stored witness agree; physical optimum and guaranteed total-action cost are distinct. A search limit is not an impossibility proof. Location pruning must preserve arbitrary Boolean goal semantics. |
| Stateful/planning worlds | Modular updates, absorbing collapse, public probe semantics, travel costs and explicit finish agree with scalar/unit-action proofs. Hidden-law reference bounds are checked across the finite prior. |
| Coordination | One operation writes one coordinate; disclosed cross-bank dependencies do not imply a universal reasoning-depth lower bound. Known-law joint costs and bank-contiguous comparison costs use independent searches. Largest admitted kernels have exhaustive scalar checks. |
| Interference | Guards read the old vector; successful updates write their declared coordinates simultaneously. Independent and coupled controls share matched targets/laws. Restricted-plan costs and required disruption of completed coordinates are separately proved. |
| Repair and compositional repair | Acceptance uses applied treatment, carried specimens and the correct location. Configuration or preview alone cannot win. Common winning decisions can exist before the hidden truth is unique. Repair qualification includes all 7,203 live public-policy cases. |
| Revision and related finite-machine worlds | Acceptance means complete behavior equivalence, including histories beyond the reader's finite query window. Provisional models do not remove the true world from the prior. Actual-outcome certificate minima are distinguished from adaptive worst-case policy costs. |
| Earlier scientific families | Existing conformance, independent proof and matrix tests retain coverage of response, network, dynamics, transfer, history, staged, assembly, representation and memory mechanics. These families are not interchangeable difficulty scales. |

A **physical optimum** assumes the law is known. A **guaranteed policy cost**
requires a single observation-dependent strategy that succeeds throughout the
stated prior. A **reference-policy upper bound** proves that one particular policy
works within its bound; it does not prove that policy is optimal. An
**actual-outcome certificate** allows the favorable experiment choices for a
particular hidden world and is not a worst-case strategy. The code and reports
must retain these distinctions.

## Validation record

| Check | Result |
|---|---|
| Focused core and audit tests | 144 passed, including all 135 added cases |
| Exact belief-policy proof tests | 9 passed |
| Repair release qualification | 30 passed, including all 7,203 live policy/receipt/replay cases; P0 and P1 then qualified and won in 14 and 15 actions |
| Property/stress sample | 3 passed; 72 generated worlds across 24 legacy D/P profiles, plus determinism and matched resource variants |
| Current-source preflights | All 56 cross-axis conditions and all 32 fresh/anchor rows passed |
| Clean distributions | Wheel and source archive installed in isolation and passed CLI, qualification and replay checks |
| Lint and current-document links | Passed |

The runtime digest after qualification is
`630d5838e4c7e5964ce7585c655ebde691ed93bf85f2a9f0cd91f975d9e324ac`.
Refreshing the dynamics artifact preserved all 3,043 reference-policy nodes;
only its binding changed. No paid model calls are part of this review.
Both current preflight reports have identical substantive content to their prior
versions after removing source identities and timing fields. This includes their
world metrics, qualification results and selected contrasts.

The full unit/integration run was interrupted by loss of the execution environment.
The last confirmed state was **1,661 of 1,719 tests completed without failure**,
with the exhaustive transfer-physics test running. The completed portion included
the 1,944-world comparison of old and optimized dynamics policies and the full
repair population. The final result and remaining tests could not be recovered,
so this is **not a complete suite pass**. Run `make test-full` or the CI workflow
with `full=true` on this candidate before release. The dedicated qualification,
preflight, focused, property and packaging results above had completed successfully.

The main new checks are in
[core certification tests](../../tests/unit/test_core_certification.py),
[mathematical checks](../../tests/unit/test_core_math_audit.py) and
[research audit tests](../../tests/unit/test_research_audit.py).
To reproduce the full local gate from the repository root:

```bash
make qualify-release
make preflight
make check
make test-full
NEXUS_STRESS_SEED_COUNT=3 NEXUS_STRESS_FAIL_FAST=1 make stress
make package
```

Run qualification and preflight on stable source before the test suites: they
deliberately reject artifacts produced for different implementation bytes.

## Effect on previous conclusions

The findings do not establish a different ranking of models, a new T/D failure
boundary, or a reason to abandon P/R research. The generated legacy goals use
the positive, correctly typed predicates unaffected by the custom-goal defects;
their historical resource budgets and machine limits are finite. The stored-plan
bug weakened admission of corrupted witnesses, not the independently solved
physical goal. No reviewed generated plan was found to be invalid.

The audit gap limits what the old verification result established. It verified
trace replay and receipts, not the semantic correctness of every stored outcome
metric. Recompute such metrics before treating them as verified research inputs.
This finding alone does not show that any historical metric was wrong.

Historical reports and model runs are retained. Current proof bindings and
preflight artifacts must be regenerated for the changed implementation. Original
audit bundles require their recorded runtime; do not overwrite their source
identity to make them pass a newer verifier. New runs should record the new
revision and use matching controls. The planned public release still needs green
checks on the final head and the documented live-provider canary after runtime
changes. Repository publication remains a separate owner action.
