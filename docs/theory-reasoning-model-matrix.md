# T-axis reasoning matrix

Ten runs per model. All cells prequalified and every viable policy path replayed.

| Run | Profile | Seed | Expected difficulty /10 | Purpose |
|---|---|---:|---:|---|
| 01 | D2/P0/R0/T1 | 7 | 4 | Exact structural-prior reasoning |
| 02 | D2/P0/R0/T2 | 7 | 3 | Infer a correction to a supplied effective law |
| 03 | D2/P0/R0/T3 | 7 | 3 | Infer a missing context-dependent operator |
| 04 | D2/P0/R0/T1 | 23 | 4 | Exact structural-prior reasoning |
| 05 | D2/P0/R0/T2 | 23 | 3 | Infer a correction to a supplied effective law |
| 06 | D2/P0/R0/T3 | 23 | 3 | Infer a missing context-dependent operator |
| 07 | D2/P2/R0/T2 | 7 | 4 | Navigation sensitivity control |
| 08 | D2/P2/R0/T3 | 7 | 4 | Navigation sensitivity control |
| 09 | D3/P0/R0/T1 | 7 | 6 | Two-stage composition control |
| 10 | D3/P0/R0/T1 | 23 | 6 | Two-stage composition control |

Use [the exact environment values](theory-reasoning-model-matrix.json). Difficulty estimates are deliberately not monotonic in T: this bounded missing-law T3 is much smaller than the existing broad T1 prior. These are separate world families, so seed equality across T does not isolate a pure T effect. Cells 7–8 keep the T2/T3 mechanics of Seed7 while raising P within each family. Cells 9–10 provide two-stage T1 controls.

Prefer the six P0/D2 cells for initial theory interpretation. R0 reduces navigation pressure; it does not make map uncertainty disappear. Do not interpret moves or delivery failures as theory-inference failures. Do not use R2 to rank T reasoning: the exact policy cost assumes known topology.

Use the same player instructions for every cell. Clarify stable controls: an artifact remains at `@inventory` while carried, even when the agent is at the destination. `drop` puts it in the room; a separate `finish` action is required. Copy the actual returned receipt exactly, without a hard-coded group count.

For analysis separate: (1) correct experiment selection, (2) whether the measured output informed the next operation, (3) final transformed fields, (4) navigation/delivery/finish, (5) provider parsing. Preserve official Pass/Fail/Error and report audited live outcomes alongside them. A win after a direct mission probe demonstrates local prediction, not broad transfer.

The cumulative progression PoC is not a live NEXUS setting. Its next real-model experiment should compare the coupled fixture with the independent and known-c controls at matched budgets and contexts. Do not send the `judge_only` block in PoC reports to a model.
