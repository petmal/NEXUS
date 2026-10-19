# Staged repair verification

Base: `ca471a6702a4da8be9023b4846acef7cc24b2ae6`, feature branch
`feat/theory-prior-axis`. Python 3.14.8, dependencies installed from the frozen lock.
No paid model calls. Independent design and implementation reviews are retained
alongside this report. The one implementation finding is fixed: matrix loading
errors now overwrite a stale successful preflight report with `blocked`.

## Completed local checks

| Gate | Result |
|---|---|
| Independent scalar proof | All 20 conditional profiles passed; every full repair unique; exact fixed panels checked independently |
| New live policy coverage | All 216 worlds × 5 supported T/D profiles: 1,080 wins with supported evidence; replay checked separately in representative profiles and every matrix row |
| Solver proof tests | 9 passed |
| Fast unit/integration suite | 713 passed, 46 deselected; 3 pre-existing malformed-fixture serializer warnings |
| Extended unit/integration suite | 46 passed in 531.40 seconds; exhaustive legacy domains and all 1,080 new policy runs |
| Cross-seed property stress | 2 passed; 72 generated worlds across 24 legacy profiles |
| CLI invalid/missing matrix regressions | 3 passed |
| New matrix preflight | All 10 rows passed with exact actual-world certificates, live adaptive and fixed-panel policies, receipts and replay |
| Legacy dynamics/transfer immutable references | Recompiled and independently checked; no reference changes |
| Transfer and Astra preflights | 13 and 10 cells passed |
| History proof and preflight | 1,024-world proof and 10 cells passed; seed 239 common-procedure shortcut preserved |
| Repair source refresh prerequisites | 15 construction/conformance/qualification tests passed; original proof and witness identities unchanged |
| Actual TCP/CLI service | `serve-session`, `request`, and `validate`: 20-action public win, correct receipt accepted, incorrect receipt rejected |
| MindTrial YAML | Both parsed; all 10 cells match matrix, only NEXUS exposed, 120 calls, operator seeds absent from player prompts, credentials blank |
| Ruff and whitespace | All new Python files pass; `git diff --check` clean |

Repair, the original ten-cell matrix, structural, and eight-cell budget preflights
also passed. Repair, the original ten-cell matrix, structural, and eight-cell budget preflights
also passed. The four local test gates total **770 passed**.

Full CI for implementation commit `33c9181e5ef6256eace257f319c50e0f8bb7eb7c`
passed proof/preflight, solver, fast, extended, stress, and CLI gates. Its image
build caught an omitted `.dockerignore` exception for the new matrix:
https://github.com/petmal/NEXUS/actions/runs/39297192096.

The packaging follow-up adds that exception and a regression checking every copied
document against the build-context allowlist. Container verification is now an
independent CI job with the same full-run conditions, so packaging failures appear
promptly. Runtime source files and proof bindings are unchanged. The local workspace
disconnected after the completed tests; the follow-up is verified through GitHub CI.
The new CI result is pending and will be recorded here before release completion.

## Performance and meaning

Within the final matrix preflight, warmed staged generation took 0.56–2.32 ms per
cell and public-policy execution with terminal diagnostics took 6.28–10.24 ms.
These are local measurements under concurrent test load, not a cross-machine
performance guarantee. A separate cold-process test passed a generous three-second
bound for generation and play/terminal work. The generation path performs direct
selection and validation, with no minimax or hardness search. Posterior updates
use immutable response tables and bitsets cached by public profile.

The pilot establishes mission-relevant information requirements, not guaranteed
model failures. In particular, D4's dependent reader can convey useful upstream
information; selected D4 certificates require four readings while the matched
D3 case requires six. Fixed panels remain legal and fit R1. Exact model difficulty
and the value of adaptive experiment selection require the proposed real-model run.
