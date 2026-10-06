# Terminal diagnostics and D5/P3 generation investigation

Historical investigation from PR #2, based on `124be3d`. The integrated production
contract is now v3; see [integration evidence](solver-optimization-evidence.md).
The paragraph below describes the branch state at the time of that investigation.
The parallel PR #3 has a different v2 schema; do not combine those schemas or cherry-pick its
schema URL into this branch. This continuation uses PR #2's published v2 contract and evaluator
finalization. It fixes two integration gaps: the fast `nexus validate` entrypoint now prints the
terminal report to stderr, and nested action responses serialize `$schema` correctly.

## Additional MindTrial runs

Sources: `14-06-57.{log,html}`, `19-10-51.{log,html}`, and `19-35-51.{log,html}`, October 5, 2026.
These runs used the user's existing NEXUS build, not the changes in this branch. Seed: 17.
Reported MindTrial outcomes from the HTML summaries:

| Configuration | Pass | Fail | Error | Coverage |
| --- | ---: | ---: | ---: | --- |
| Gemini 3.8 Flash, high | 8 | 2 | 0 | 10 tasks |
| Grok 4.7, xhigh | 8 | 2 | 0 | 10 tasks |
| Kimi K3, max | 6 | 1 | 3 | 10 tasks |
| Meta Muse Spark 1.3, xhigh | 0 | 5 | 5 | 10 tasks |
| Qwen3.8 Max 0902, xhigh | 8 | 2 | 0 | 10 tasks |
| DeepSeek V4 Pro 0813, max | 8 | 2 | 0 | 10 tasks |
| Claude Sonnet 5.5, xhigh | 2 | 1 | 0 | D0/P1/R0, D5/P1/R0, D5/P3/R1 only |

The four clean 8/10 runs fail D5/P3/R1 and R2. Kimi's D1/P1/R0 and D5/P3/R0
traces reach `won` with a receipt, but its final text fails MindTrial's structured-result parsing;
its third error is a parsing failure after losing R1. Thus Kimi has eight observed game wins,
while its harness score remains six passes. Muse's five API errors and five early answers while
active should not be interpreted as ten demonstrated game losses.

R1 illustrates why the new report needs both goal state and terminal status:

| Model | Final observed state at R1 budget exhaustion |
| --- | --- |
| DeepSeek, Grok, Kimi | A1 transformed correctly; A1 and A4 dropped in R8; no action left for `finish` |
| Qwen | Correctly transformed A1 and recovered A4, but both still carried; rejected `finish` |
| Gemini, Sonnet | A1 correctly transformed and dropped; A4 still carried; rejected `finish` |

All six reached R8 at phase 2, but carrying an artifact in R8 does not satisfy its location
predicate. No post-mortem prose is used to override the observed state or victory rule.

The terminal schema makes these outcomes inspectable with `goal_satisfied`,
`unsatisfied_goal_leaves`, action counts, `failed_finishes`, and remaining budget. The new tests
cover active-route non-disclosure, idempotent finalization, missed explicit finish, receipt
preservation, fast-validator stderr, and the actual nested response schema alias.

## Startup observations

Measured interval: service `starting execution` to `is ready`, not pure Python generation time.
It includes container startup and health-check polling; hardware and concurrent workload were
not controlled.

| Log | D5/P3 sessions | Startup range | Median |
| --- | ---: | ---: | ---: |
| 14-06-57, four model configurations | 12 | 591–1372 s | 1223.5 s |
| 19-10-51, Sonnet subset | 1 | 590 s | 590 s |
| 19-35-51, two model configurations | 6 | 529–653 s | 607 s |

The longer overlapping run is consistent with CPU/memory contention, but the logs alone do not
identify the host bottleneck. Peak RSS from an isolated generation below makes concurrent memory
pressure a concrete concern to measure, not proof that swapping occurred.

## Reproduced generation bottleneck

Existing GitHub profiling job: run `37360309713`, job `111932966271`, Python 3.14.7,
commit `124be3d`. Separate cold processes, seed 17:

| Profile | Generation | Policy solver in P3 compilation | Final qualification | Peak RSS |
| --- | ---: | ---: | ---: | ---: |
| D5/P2/R0 | 16.09 s | — | 0.13 s | 532 MiB |
| D5/P3/R0 | 173.80 s | 156.81 s | 0.57 s | 4057 MiB |

P3 accepts its first tested cargo candidate and topology attempt 0. The cold P3 solver reports
180,409 memo entries, versus 20,306 in the core P2 solve. Final qualification already reuses
exact cached policy results. Removing qualification cannot materially address this bottleneck
and would weaken the benchmark's guarantee.

A fresh local baseline with the same frozen dependencies completed D5/P3/R0 in 152.58 s:
137.56 s in the P3 policy solver, 0.47 s in final qualification, and 4060 MiB peak RSS.
Physical optimum remains 14 actions, guaranteed policy 17, P3 dependency cost 6, R0 budget 35.
Only one seed is measured here; these numbers are not a cross-seed performance claim.

The added internal timings separate hypothesis physical solves, minimax search, witness
construction, and requested action values. They preserve solver decisions, search ordering,
qualification, and R0/R1/R2 budgets. This change instruments performance; it does not claim a
solver speedup. See the companion JSON reports for the complete timing events.

Internal timing from the instrumented cold D5/P3/R0 run (150.24 s total, 4055 MiB peak RSS):

| Phase inside P3's policy solver | Time | Cache entries after the phase |
| --- | ---: | --- |
| Physical feasibility of four hypotheses | 0.94 s | — |
| Exact minimax search | 119.98 s | 158,952 memo; 389,266 branch |
| Witness construction | 0.007 s | — |
| Three requested initial action values | 15.04 s | 180,409 memo; 417,472 branch |

The core P2 solve separately spent 12.48 s in minimax and 0.94 s in action values.
The comparison with the baseline preserved every non-timing wrapper event metric, including
visited counts, exact costs, candidate call counts, and qualification success. The roughly 2 s
wall-time difference is ordinary single-run variation, not evidence of a speedup; short test
processes also ran concurrently with part of the instrumented measurement.

Companion reports: `profiling/d5-p3-seed17-baseline.json` and
`profiling/d5-p3-seed17-instrumented.json`. The latter records a full compiled-episode hash for
future comparisons; the baseline profiler did not yet record that hash, so this run does not
claim full D5 byte-for-byte differential verification. A cold D2 fixture verifies complete
compiled-model equality with timing disabled/enabled after clearing the policy-result cache.

## Next optimization target

Focus on exact minimax state/transition storage and repeated branch expansion. The 417,472
branch-cache entries retain full successor `WorldState` objects, including copies of artifact
and machine models. Interning immutable normalized states within a solve and/or representing
cached transitions more compactly are concrete next candidates. Measure allocation/copy costs
with `--cprofile` before adopting either. They need differential solver tests covering witnesses,
action values, invalid actions, aliasing, and fixed-cost certificates, followed by cold cross-seed
D5/P3 validation. This instrumentation change does not introduce either optimization.

Do not raise budgets, weaken D5 proof obligations, remove P3 cargo, skip qualification, or
suppress the three requested action values to obtain an apparent speedup. Qualification and
witness construction are negligible here; the measurements argue against optimizing those first.

Validation: frozen dependencies on CPython 3.14.7; 84 fast unit/integration tests passed (32
slow/stress tests deselected). Two existing Pydantic serialization warnings arise in a generic
rule-normalization fixture. Full cross-seed stress was not run for this instrumentation-only
change. The cold D5/P3 generated episode passed the generator's complete final qualification.
