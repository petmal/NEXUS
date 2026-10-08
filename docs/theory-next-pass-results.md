# Physical-search optimization, D4/T1 and T2 correction PoC

This is the continuation of the T-axis calibration work, following the seven-model
`20-19-27` run. Engineering measurements are distinct from model ability scores.
Production generation remains sequential; process workers are profiling-only.

## Implemented behavior

The physical solver now omits plan construction when screening hypotheses, shares
immutable shortest-path tables and
applies movement macros without deep-copying every intermediate move. Ordinary
engine transitions still perform interactions, and the generated policy witness
still consists entirely of ordinary actions. The shortcut relies on the current
contract that movement does not change phase, artifacts or machine state; changes
to that contract require revisiting the quotient and its tests.

An exact 512-entry cost-result cache was also tested, keyed by all physical inputs
and search bounds. It produced zero hits in the measured fresh D3/T1 and D5/P3
workflows, so it was removed from production. This does not prove all possible
caching approaches ineffective: semantic rule normalization could expose reuse
that exact AST identity misses, but that requires another measured PoC. The
previous exact policy-result cache remains. State-limit exhaustion still raises
during qualification and never eliminates a potentially viable hypothesis.

D4/T1 is enabled with the existing `--theory-level 1` switch. It uses the complete
27,120-behavior public T1 prior. A truthful row establishes the distractor context;
bounded evidence search retains mission uncertainty and proves the informative
auxiliary probe resolves it. Exact total-action qualification separately checks
that the mission and auxiliary probes are optimal and the distractor costs one
extra action. No private catalogue restriction enters the solver. Physical worlds
remain paired with T0, including P3 delivery selection before theory compilation.

## D4 evidence and qualification

Initial P2/R2 sample: seeds 0–9, 17 and 2525 at T0/T1, 24 cases. All 12 T0 cases
and 10 T1 cases passed, with 83 viable-hypothesis policy replays. T1 seeds 0 and 2
explicitly rejected: the bounded evidence search could not prove the requested
profile. No reroll or weakened guarantee was substituted. All ten accepted pairs
have identical physical-world hashes. Accepted T1 median generation was 2.20 s;
this sweep is an acceptance test, not an isolated performance comparison.

Increasing the D4 beam/options to 96 did not rescue seeds 0 and 2. A maximal
truthful-evidence check retaining all original T0 alternatives still left 283 T1
behaviors for seed 0, exceeding the 32-candidate ceiling. The production search
therefore permits further evidence narrowing while preserving the exact D4
proof; it does not promise to preserve the T0 posterior. Rejections are bounded
search outcomes, not proofs that a valid T1 episode is mathematically impossible.

## T2 proof of concept

`scripts/theory_correction_poc.py` creates a distinct nine-room, single-machine
research family. It is not paired with T0/T1 and does not enable production T2.
One immutable structured specification renders the public manual/JSON and
enumerates the complete nine-member correction class:

- effective model: add a disclosed amount modulo 11;
- exact validity region: phases 0 and 2;
- phases 1 and 3 independently add an unknown correction from {0, 1, 2};
- all other intrinsic artifact fields remain invariant;
- the public physical-solvability promise removes only exactly impossible worlds.

All nine candidates agree with established calibration evidence. Five are
physically viable for each mission. The exact discovery analysis requires one
probe; all five branches replay to victory at the exact action budget. Using only
the effective model cannot reach the goal. Across seeds 0, 1, 2, 17 and 2525, all
25 viable policy paths passed. Exhaustive finite-domain validation performed
85,536 law/input checks across the three effective-model choices. Median fixture
construction plus policy/replay validation was about 0.095 s.

This proves feasibility and honest theory limits, not that T2 is harder than T1.
The current correction class is intentionally small and may be easy for capable
models. The next production-design gate should choose whether to use two stages,
more coupled corrections, or selective experiments, then qualify D semantics and
R budgets over that exact disclosed class. Calibration-only evidence must not
secretly restrict the unknown corrections.

## D5/T1 gate

The current D5 mission rule is not representable in T1: it uses a conjunction
with an exact input-value test, nested conditionals, exact phase equality and
constant value assignment. The two calibration machines also assign constants.
T1 permits one shape/parity conditional and independently composed bounded
arithmetic/toggle/rotation branches. Widening it silently would change the public
theory contract and invalidate comparisons.

Keep D5/T1 rejected. A future PoC must construct a family entirely within T1 and
prove that constructing an experimental artifact is strictly better than the
direct mission probe and a functional distractor, using the full evidence-filtered
T1 prior. Merely proving hidden-rule membership is insufficient. This is a gate
for a new family, not a claim that all possible D5/T1 families are impossible.

## Reproduction and checkpoints

Use Python 3.14.7 and `uv sync --frozen --all-extras`.

```bash
uv run python scripts/profile_physical.py
uv run python scripts/profile_physical.py --workers 2
uv run python scripts/profile_physical.py --workers 4
uv run python scripts/profile_theory.py --seeds 0 1 2 3 4 5 6 7 8 9 17 2525 \
  --levels 4 --resource-pressure 2 --out docs/profiling/theory-d4-extension
uv run python scripts/theory_correction_poc.py
```

Profilers use atomic per-case results with code/runtime fingerprints. Baseline
source is the PR #6 head before this pass, remote `6a614a78be00dc554b951d98adf24bd170a267da`.
Pass a checkout of it via `profile_physical.py --source-root PATH`. Raw exploratory
ablations live in `physical-pass-baseline`, `physical-pass-cost-cache` and
`physical-pass-routes`; use repeated measurements for performance decisions.

Independent physical-code review found no production solver blocker. Its two
profiling findings were corrected: comparison hashes include all physical inputs,
and timeout cleanup kills the complete spawned process group.

## Recommended ten-run model matrix

See `theory-next-model-matrix.json` for exact environment settings. Use the same
seed across each pair and all compared models. Expected difficulty is a hypothesis,
not a measured ranking.

| Pair | Seed | D/P/R | Theory variants | Expected relative challenge |
| --- | --- | --- | --- | --- |
| 1 | 1 | D3/P2/R1 | T0, T1 | Higher: two discovery stages; performance control |
| 2 | 1 | D4/P2/R1 | T0, T1 | Moderate: selective experiment, action slack |
| 3 | 17 | D4/P2/R1 | T0, T1 | Moderate: second seed |
| 4 | 17 | D4/P2/R2 | T0, T1 | Higher: no action slack |
| 5 | 17 | D4/P3/R1 | T0, T1 | Moderate–higher: delivery dependency |

T1 is hypothesized to add theory interpretation burden within each pair, but the
exact optimal costs may match. D4 has one transformation stage; it need not be
harder overall than D3. Do not include T2 or D5/T1 in this production matrix.
Build with the OCI revision argument, retain startup diagnostics at readiness,
and continue distinguishing actual game outcome from receipt/output parsing.

## Repeated timing and parallelism

All timings use cold Python 3.14.7 subprocesses on a host exposing nine CPUs with
an eight-CPU cgroup quota. Each D3 isolated cell has three repetitions; the D5
control has two. Exact costs, physical hashes and all viable policy replays agree.
These are this host's generation times, not predictions of MindTrial wall time.

| Isolated case | Original | Sequential candidate | 2 workers | 4 workers |
| --- | ---: | ---: | ---: | ---: |
| D3/P2/R1/T1, seed 1 | 5.329 s | 4.531 s | 4.013 s | 3.773 s |
| D3/P2/R1/T1, seed 17 | 4.371 s | 4.005 s | 4.021 s | 3.874 s |
| D5/P3/R1/T0, seed 17 | 25.668 s | 21.459 s | not run | not run |

The candidate includes the unused exact result cache; final cache-free production
verification is recorded separately in `physical-pass-production`. The main
benefit comes from route execution, not cost-only plan suppression on its own.

Seven simultaneous seed-1 episodes: median generation 4.865 s sequential,
5.171 s with two workers per episode (+6.3%), and 5.688 s with four (+16.9%).
Workers add roughly 52 MiB peak RSS per child; reported child peak is the maximum
child usage, not total pool or simultaneous system RSS. Worker startup, payload
serialization and process contention reduce the benefit of independent physical
searches. Minimax and generation remain serial. The PoC uses maintained Python
`concurrent.futures.ProcessPoolExecutor` with explicit spawn semantics, ordered
results, bounded buffers and per-case process-group timeout cleanup.

**Decision:** keep production sequential. The four-worker mode is promising only
for an isolated large hypothesis batch with spare CPU; it is available in the
profiling script, not a production service flag. The seven-way workload is closer
to the supplied model run and does not justify enabling per-episode workers.
GPU execution remains deferred: this object-heavy branch/search workload has no
measured tensor kernel that would justify a GPU backend. Framework reference:
https://docs.python.org/3.14/library/concurrent.futures.html#processpoolexecutor

The D5/P3 profile explains why hypothesis parallelism is unlikely to help that
case much: about 0.42 s is physical screening in the planning-dependency stage,
versus 16.33 s minimax plus 1.48 s requested action values. There are only four
hypotheses. Future D5 optimization should target those searches, not add more
physical workers; retain exact minimality and experiment-value proofs.

## Final cache-free implementation and validation

Final sequential medians: seed-1 D3/T1 **4.237 s** (20.5% below original),
seed-17 D3/T1 **4.016 s** (8.1% below original), and seed-17 D5/P3/T0
**21.750 s** (15.3% below original). All physical hashes, exact costs and replay
counts match the original. These modest improvements should not be extrapolated
to the much larger concurrent MindTrial host timings without a controlled run.

The ten-run production matrix passed preflight: all ten cells accepted, all
96 viable hypothesis policies replayed, and all five pairs matched physical-world
hashes. A second independent review found no D4/T1 production blocker and
identified a replay-harness gap: witness budget and replay count were not explicitly
compared to the certified cost/viable count. Both are now required, with negative
regression tests; all five T2 worlds passed again. T2's current rerun median is
approximately 0.10 s, excluding the separate exhaustive-domain sweep.

The timeout failure branch was exercised with four workers requested: it records
`timeout` and exits nonzero. Source inspection verifies whole-process-group kill
and cleanup on timeout/interruption; descendant liveness could not be independently
observed through `/proc` in this execution environment, so that count is not claimed.
The dependency lock check and diff whitespace check pass. Docker/Podman are not
available locally; actual container build/OCI inspection remains a CI/user build gate.

Validation completed: all **173 current tests** are covered by the 172-test full
suite (257.54 s, three stress seeds) plus the subsequently added replay-gate test
in a six-test targeted rerun (0.70 s). The full run reports two existing Pydantic
serializer warnings from the legacy generic SET-normalization test; no tests fail.
The full suite covers D0–D5 generation, ordinary engine replay, T0 stability,
protocol/terminal secrecy, CLI/service paths and the three-seed stress sample.
Additional current-harness checks passed D4/T1 P0/R0 and P1/R1 and D5/P3/R2,
with 12 further exact policy replays. No paid real-model calls were made.
