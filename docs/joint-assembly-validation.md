# Joint assembly validation

Implementation baseline: `139f3bedefa6c5f6af54e101eab0bf68411d6cee` on
`feat/theory-prior-axis`. No older ontology was replaced. This record distinguishes
mechanical qualification, live conformance, regression tests and unmeasured model
difficulty. The implementation ledger and guide contain reproduction commands.

## Completed checks

| Check | Result |
|---|---|
| Final fast unit/integration suite | 757 passed, 47 deselected; 180.53 s |
| Extended unit/integration suite | 47 passed; 521.55 s |
| Cross-seed property stress | 2 passed, 1 deselected; three seeds per sampled profile; 135.27 s |
| Legacy repair construction/conformance/qualification gates | 15 passed; 9.13 s |
| Legacy qualified P0/P1 public witnesses | Won in 14/15 actions; exact replay verified |
| All-world public investigation profiles | 1,728 live supported wins: 432 worlds × T2/T3 × D3/D4 |
| Independent runtime acceptance review | 62,208 engine finish cases (432 worlds × 144 builds) |
| Independent reader conformance review | 46,656 cases across profiles, carrier states and all legal settings |
| Construction/recovery proof | 7,056 cases, covering all 49 component states and 144 builds |
| Independent private physical optimum | 864 live solver replays, all 432 worlds at P0/P1, matching exhaustive BFS |
| Ten-row matrix preflight | All exact claims, supported wins, budget bounds and replays pass; science recovery checks pass |
| Packaging contract tests | 11 passed; Docker context includes the new preflight and matrix |
| Final CLI help cleanup | 13 CLI tests passed; family names come from the static catalog |
| Changed-scope Ruff and ty | Passed; no dependency or project gate migration |
| MindTrial YAML | Parsed on export; ten service-input blocks match the matrix; all three image roles match |

Local runtime is Python 3.14.8 with frozen project dependencies. CI/container remain
on the existing Python 3.14.7 pin. The fast suite reports three existing Pydantic
serializer warnings from a test that deliberately inserts raw strings into enum
fields. No new warnings or observed legacy seeded-behavior changes were introduced.

The only subsequent source edit after the fast suite replaced two CLI help strings
with family-neutral budget wording. The 13 CLI tests and final source-bound matrix
preflight cover that edit; it changes no transition, inference or solver behavior.

## Qualification and limits

The full prior contains 432 worlds, 144 complete builds and 96 mission acceptance
signatures. The independent literal-table oracle and exhaustive query-subset search
agree with production arithmetic, accepted builds and optimized certificate search.

T3/D4 sum and difference worlds require five actual supporting readings and all
three reader channels. Even every reading from any two channels is insufficient.
Product and squared-left worlds require four readings and retain documented channel
omissions. The T2 known-sum case admits local bias cancellation. The selected matrix
covers all four physical kernels and includes matched controls instead of counting
offset-only changes as new scientific mechanisms.

These are exact evidence certificates with oracle query selection. They exclude
finish feedback and setup, and do not prove that an LLM must reason in a particular
sequence. A separate query/finish audit includes equivalent builds, failed attempts
and free physical setup, but its exact search covers only the small horizons listed
in the guide. The broader feedback upper bound becomes uninformative at five actions.
No full 40-action information optimum or empirical failure rate is claimed.

Private physical construction optimum is proved separately. Across P0 worlds,
54 need six actions, 108 need seven, and 270 need eight. P1 adds one unavoidable
move. The public investigator uses a constructive, non-optimal information policy;
its selected science rows take 16–22 total actions within budgets of 40/46.

## Performance

Three isolated-process measurements for a hard row gave generation times of
34–43 ms and public investigation/construction/terminal diagnostics of 14–24 ms.
Each played 22 actions and won. These are local observations, not service/network
latency or cross-machine guarantees. Exact offline proof plus the ten-row preflight
took about 10–12 seconds. Finite tables are immutable/shared, posterior updates use
bitsets, and ordinary generation selects directly without a search/rejection loop.

## Review disposition

The independent design and implementation reports are preserved alongside this file.
Review found and corrected mixed tool/service/validator image tags, a malformed
test fixture, the explicit live-to-finite argument gap and the older repair family's
stale source binding. The proof and serialized legacy witnesses remain byte-identical;
the binding was renewed after their gates and never bypassed or weakened.

## Delivery status

All local regression gates passed. Remote CI/container checks are pending
publication; no local Docker/Podman is
available, so a local image build is not claimed. This section will be updated with
the final result/run identifier. No paid model calls have been made. Model difficulty
is still uncalibrated and `deep_tier_admitted` remains false.
