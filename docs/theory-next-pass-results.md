# Physical-search optimization, D4/T1 and T2 correction PoC

This is the continuation of the T-axis calibration work, following the seven-model
`20-19-27` run. Engineering measurements are distinct from model ability scores.
Production generation remains sequential; process workers are profiling-only.

## Implemented behavior

The physical solver now omits plan construction when screening hypotheses, shares
immutable shortest-path tables, retains up to 512 exact cost-only results, and
applies movement macros without deep-copying every intermediate move. Ordinary
engine transitions still perform interactions, and the generated policy witness
still consists entirely of ordinary actions. The shortcut relies on the current
contract that movement does not change phase, artifacts or machine state; changes
to that contract require revisiting the quotient and its tests.

The cache includes topology, state, rules resolved by machine, goal, phase modulus,
state ceiling and effective search budget. AST identity is deliberately conservative.
It does not require repeated random seeds; repeated physical hypotheses within
one generation can reuse results. Different seeds get no assumed cache benefit.
State-limit exhaustion is retained and raises during qualification.

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

Final repeated measurements, concurrency decision and full validation are pending.
