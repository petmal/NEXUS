# T0/T1 implementation and calibration evidence

Implementation branch: `feat/theory-prior-axis`, based on integration commit
`cd69107f02af30c10464b85b47fa343a3f96aaef`. No MindTrial changes and no merge into main.

## Implemented behavior

- T0 remains the default. Historical compiled episode hashes for seed 17 / P2 / D0–D5 match
  after removing the new private `theory_level=0` metadata field. Engine/action/retry/validation
  semantics are unchanged.
- `--theory-level 1` / `NEXUS_THEORY_LEVEL=1` enables a formal structural prior: 18 predicates,
  48 independent branch effects, 41,472 syntactic laws and 27,120 distinct behaviors.
- The public `theory.json` and manual are generated from the same immutable specification used
  by the evaluator. Qualification rejects either attachment if it differs from that contract.
- Evidence is filtered against the entire public prior. Only complete surviving classes are
  materialized; oversized classes fail rather than being truncated. D3 uses at most 12
  candidates per machine (144 joint hypotheses), below the existing exact solver's 256 limit.
- The evidence planner preserves paired T0 alternatives for D2/D3 when choosing measurements.
  This retains established ambiguity; it does not restrict the evaluator to the T0 catalogue.
- T0 selects the physical world and P3 cargo first. T1 changes theory/evidence, episode identity,
  private evidence metadata and exact policy/budget. Paired hidden laws, topology, intrinsic
  artifacts, goal and reference physical plan remain unchanged. A qualification failure rejects
  the paired seed; it never silently substitutes another world.
- T1 supports D0–D3, P0–P3, R0–R2 subject to qualification. T1/D4–D5 and T2+ explicitly reject.
  This first release is experimental calibration support, not an all-seeds success promise.
- Performance-v4 adds terminal `theory_level`; v1–v3 schema files remain intact. Its immutable
  schema source is commit `5feedd9b21a7160d29a5cfa4d7b9908014edd14d`. No active telemetry leak.

## Cold P2/R0 sweep

Seeds 0–19, 73 and 2525, each in a fresh Python 3.14.7 process. Each accepted episode is fully
qualified and its policy replayed with ordinary engine actions for every physically viable
hypothesis. Generation timing excludes interpreter startup and the subsequent extra replay.
Source fingerprint: `60f12c969e871cbe8cbd28a258cb536ba7dcbe8af5810353b5b8c088cc19b62a`.
Raw results: `docs/profiling/theory-integration/`.

| T1 profile | Accepted / attempted | Median generation | Maximum generation | Rejected seeds |
|---|---:|---:|---:|---|
| D0/P2/R0 | 22/22 | 0.896 s | 3.027 s | — |
| D1/P2/R0 | 20/22 | 0.915 s | 3.080 s | 8, 19 |
| D2/P2/R0 | 22/22 | 0.931 s | 3.089 s | — |
| D3/P2/R0 | 21/22 | 4.464 s | 6.505 s | 73 |

85/88 accepted, with 748 successful viable-hypothesis replay paths. There were no solver errors
or timeouts. Rejection is a bounded-search result, not a proof that suitable evidence cannot
exist. The sample is a deterministic engineering stress set, not a representative population
estimate. On the original 0–19 seed set, D2 now accepts 20/20 versus 11/20 in the earlier PoC.
D1 still rejects 8 and 19; D3 adds 20/20 accepted cases on that seed set.

These are local generation measurements, not MindTrial service-readiness measurements. They
must not be compared directly with the uploaded host's multi-minute P3 startup or claimed as
model capability evidence. T1 uses the existing paired T0 true-law sampling distribution;
full-universe T1 law sampling is not implemented. D-normalized evidence can differ across T,
so generated T1 is not guaranteed to require more physical actions than T0.

## Validation status

Fast regression: **132 passed**, 34 extended/stress tests deselected, in 84.33 seconds. This
includes exhaustive compositional prior proof, all 288 T0 members, an ordinary-action minimax
comparison, fixed-evidence prior monotonicity, T0 full-package regression hashes, T1 P3 pairing,
known seed rejections, altered-public-contract rejection, CLI/service ENV wiring and active
secrecy. Two existing Pydantic warnings originate in an unchanged generic-rule normalization
fixture (string shape/pattern values); no new theory warning was observed. `uv lock --check` passes.

The final cold dataset has **116 cases: 113 accepted, three explicitly rejected**, all on the
same recorded source fingerprint. All **865 physically viable hypothesis paths** replayed to
victory. All **19 available accepted T0/T1 pairs** have identical physical-world hashes.
Sixteen additional P3/R2 cases (seeds 17 and 2525, D0–D3, T0/T1) all pass, including **77**
viable-path replays at the exact guaranteed budget. Worst measured T1 P3 generation was 19.33
seconds; maximum RSS across the full dataset was 171.34 MiB. These results support P2 as the
cheaper first T-axis model-calibration setting.

Extended/stress gate: **34 passed** in 216.75 seconds, using the existing three-seed stress
configuration. Together the two gates cover **all 166 collected tests**. Existing T0 D0–D5,
P0–P3 and resource-pressure regression/stress gates remain green. No dependency lock changes.
There is no Docker/Podman executable in this environment, so actual image build/inspection is
left to the existing CI container gate, which now passes VCS_REF and asserts the OCI label.

An independent read-only review found no confirmed blocker. Its structural pairing concern was
fixed by moving T1 compilation after T0 world/cargo selection. Focused P3 paired-world tests were
added. The existing P3 qualifier independently proves that its policy overhead under T1 still
equals its physical delivery-dependency overhead.

## Suggested first real-model matrix

Machine-readable ENV matrix: [`theory-model-testing-matrix.json`](theory-model-testing-matrix.json).
Use seed 17 for all ten cells and compare matching T0/T1 pairs. Keep model settings identical
within each pair. This avoids P3 generation cost and holds physical worlds fixed. R2 remains a
separate navigation-sensitive calibration rather than the first T discrimination test.

| Cells | D/P/R | T values | Expected relative challenge |
|---|---|---|---|
| 1–2 | D0/P2/R0 | 0, 1 | Control / low; direct mission context, T1 requires primitive-law reconstruction. |
| 3–4 | D1/P2/R0 | 0, 1 | Low–moderate / moderate; infer the mission without direct-context evidence. |
| 5–6 | D2/P2/R0 | 0, 1 | Moderate / moderate–high; active discovery from the theory-conditioned evidence. |
| 7–8 | D3/P2/R0 | 0, 1 | High / higher expected theory burden; correlated two-stage discovery. |
| 9–10 | D3/P2/R1 | 0, 1 | Highest of this matrix; same theory comparison with less execution slack. |

These are hypotheses for model calibration, not measured difficulty ratings. T1 may be no harder
for a model that readily derives the primitive structure; the experiment should establish that.

## Reproduce and resume

```bash
uv sync --frozen --all-extras
uv run pytest -q -m 'not slow and not stress' --maxfail=1
uv run python scripts/profile_theory.py \
  --seeds 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 73 2525 \
  --theory-levels 1
uv run python scripts/profile_theory.py --seeds 17 73 2525 --theory-levels 0
uv run python scripts/profile_theory.py --seeds 17 2525 \
  --planning-level 3 --resource-pressure 2
```

Each completed case is written atomically. Resume skips only identical case/source/Python
fingerprints; failures and timeouts are rerun. No model API calls are made by this harness.

## Next gate

Run the paired real-model matrix, then assess T1 discrimination. T2 effective-theory/correction
work remains a separate PoC after T1 calibration; T3/T4 require a symbolic-belief proof. Do not
broaden T1 to D4/D5 by concealing the old specialized family or using it as a hidden solver prior.
