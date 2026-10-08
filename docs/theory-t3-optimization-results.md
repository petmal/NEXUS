# Evidence-selection optimization checkpoint

Cold processes, same host/lockfile, before other runtime changes.

| D3/P2/R0/T1 seed | Before, s | After, s | Reduction | Physical-world hash equal |
|---|---:|---:|---:|---|
| 1 | 4.711 | 4.020 | 14.7% | yes |
| 17 | 4.152 | 2.773 | 33.2% | yes |

Each trial evidence subset now looks up precomputed mission signatures instead of interpreting the same AST repeatedly. Catalogue JSON indexing is also reused. The per-search signatures are local; there is no unbounded per-seed cache. Ordering and tie-breaking are unchanged.

Validation: 44 evidence-oracle/theory generation tests passed. Earlier targeted difficulty/theory run completed 55 checks before the obsolete T3-rejection assertion; that assertion is updated as part of T3 integration. Both profiled worlds replay all 83 viable hypotheses. These two samples demonstrate a useful local gain, not a universal performance guarantee.
