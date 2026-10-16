# Compositional reasoning pilot

The previous ten-cell matrix remains the control/efficiency benchmark. This
**eight-run pilot** tests a separately selected `compositional-repair-v1` family.
Its difficulty is uncalibrated; run a small model subset before a broad evaluation.
Keep P1/R1, no external interpreter, and use a fresh context for every cell. Do
not disclose seeds, fixture roles, candidate pool, or this document to players.
Do not share a T0 solution with a subsequent challenge context.

| Run | Family | T / D | Seed | Purpose and expected relative challenge |
|---|---|---|---:|---|
| 01 | compositional-repair-v1 | 0 / 0 | 0 | Execution control; exact valid treatment supplied; easiest |
| 02 | coupled-dynamics-v1 | 3 / 5 | 219 | Existing history-transfer control; compare action efficiency |
| 03 | compositional-repair-v1 | 3 / 5 | 0 | Chain composition and local replacement; baseline structural challenge |
| 04 | compositional-repair-v1 | 3 / 5 | 250 | Fork composition; joint-context transfer |
| 05 | compositional-repair-v1 | 3 / 5 | 438 | Reconvergent graph; passive evidence insufficient |
| 06 | compositional-repair-v1 | 3 / 5 | 463 | Same passive equivalence class as 05, different required repair; separate context essential |
| 07 | compositional-repair-v1 | 3 / 5 | 493 | Different mechanism combination with intervention obstruction |
| 08 | compositional-repair-v1 | 3 / 5 | 542 | Different local replacement and joint treatment with intervention obstruction |

Expect 05–08 to exercise intervention selection more directly than 03–04. This
is not a proved ranking of LLM difficulty or a prediction that half the models
will fail. The old dynamics family may still require more readings. Graph depth
and reading count do not establish cognitive depth.

The source matrix is `docs/structural-model-matrix.json`. Generate and validate
complete per-cell environment maps before use:

```sh
uv run python scripts/preflight_structural.py --output /tmp/structural-preflight.json
```

Only use `status: pilot-ready` from the exact image/source being tested. The
preflight report includes environment variables, actual reference actions,
budgets, graph/change coverage, passive and one-context repair obstructions,
qualification and replay results. Invalid matrices and stale bindings fail closed.
Tool-call limit: 120. This harness limit is separate from the game budget (30
for the new P1 challenge, 8 for its T0 control, unchanged 73 for dynamics).
Use `scripts/preflight_structural.py` inside the built image too; do not ignore a
failed preflight. Build with `--build-arg VCS_REF=$(git rev-parse HEAD)`.

The player task/tool description must defer to the current manifest rather than
hardcode controller arity or old evidence filenames. Here stage has eight fields
and the doser has four; configure prepares an apparatus, operate changes a
specimen, and successful finish returns the real receipt. Direct mission probes
are legal. Preserve the no-Python setup for this initial pilot.

## Interpretation and distribution

These are targeted, nonrandom diagnostic fixtures. The production sampler is
`seed % 615`; sampling seeds uniformly from 0..614 gives the stated uniform
world prior. Arbitrary seeds or a selected fixture pool need not. The exact
query-level success ceilings in `structural-reasoning-proof.md` concern that
uniform full prior, **not** this matrix's empirical success fraction. Matrix
selection never changes the generator's disclosed support.

Separate success, scientific evidence sufficiency, first attempted treatment,
physical execution, budget efficiency, and returned-receipt formatting. For the
new family, terminal `mission-performance-v2` reports common accepted repairs and
whether the first applied submission was supported by all remaining worlds.
Winning-set signature counts are not exclusive target classes; reducing them
alone need not establish a guaranteed repair. Multiple hidden worlds may remain
when a fully justified treatment is already known.

If all models pass, inspect their shortest valid traces and use those policies
as adversarial baselines before increasing graph size. If failures occur, replay
them and distinguish inconsistent inference, poor intervention choice, incorrect
joint repair, and ordinary protocol/logistics errors. Never infer population
failure rates from the targeted fixtures.
