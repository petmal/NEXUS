# D5/P3 generation performance — execution plan

This plan implements the five optimizations proved in `docs/d5-generation-performance-design.md`.

## Commit 1 — tuple search keys + bounded LRU cache

Files:
- `src/nexus/solver/search.py`
- `src/nexus/solver/belief.py`
- solver unit tests

Work:
1. Replace cryptographic solver visited-state keys with immutable semantic tuples.
2. Keep canonical SHA-256 hashing only for replay/state-integrity paths.
3. Replace clear-all 256-entry policy cache with a 16-entry LRU.
4. Include action-value selection in cache identity.
5. Add cache isolation/eviction tests and state-key equivalence tests.

Proof gate:
- all semantic state fields perturb the tuple key;
- turn/action budget do not;
- exact policy N/N-1 tests remain green;
- compressed and ordinary physical solvers retain identical optimum on proof fixtures.

## Commit 2 — requested D4/D5 action values

Files:
- `src/nexus/solver/belief.py`
- `src/nexus/generator/generator.py`
- `src/nexus/generator/qualify.py`
- solver unit tests

Work:
1. Add optional `requested_action_values` to `solve_guaranteed_policy`.
2. Preserve existing all/none behavior when omitted.
3. D4 requests exactly M1/A1, M1/A2, M1/A3 probes.
4. D5 requests exactly M2/A2 operate, M1/A1 probe, M3/A3 operate.
5. P3 D4/D5 uses the same subsets.
6. Final qualification requests the exact subset needed to prove profile semantics.

Proof gate:
- full/subset/none runs have identical optimum and witness;
- subset entries equal full-run entries;
- D4/D5 mechanical definitions are unchanged.

## Commit 3 — compressed physical generation

Files:
- `src/nexus/solver/belief.py`
- `src/nexus/generator/generator.py`
- `src/nexus/generator/qualify.py`
- generation/solver tests

Work:
1. Add `max_frontier_size` to compressed physical result.
2. Use compressed physical solver for all generation-side candidate screening/reference plans.
3. Use compressed solver for P3 candidate screening.
4. Treat generation solver exploration counters as diagnostics; final qualifier no longer compares them to BFS counters.
5. Keep final qualification ordinary BFS unchanged as the independent oracle.

Proof gate:
- generated optimum metadata equals qualifier BFS optimum;
- stored expanded reference plan has exact optimum length;
- replay still succeeds;
- deliberate optimum corruption is rejected.

## Commit 4 — skip intermediate P2 qualification for P3

Files:
- `src/nexus/generator/generator.py`
- generation tests

Work:
1. Thread private `qualify_result` flag through core D0-D5 generators.
2. Default true everywhere.
3. `generate_episode(... planning_level=3)` requests an unqualified internal P2 base.
4. P3 final output always runs one full final qualification after P3/R transformation.

Proof gate:
- direct P0-P2 generation still qualifies before return;
- unqualified-core fixtures independently pass qualification;
- final P3 qualifier still proves counterfactual physical/policy overhead;
- corrupted P3 final metadata/world is rejected.

## Commit 5 — cross-optimization regression/performance instrumentation

Files:
- targeted tests/property tests
- optional private timing diagnostics (no player-visible surface)

Work:
1. Add D5/P2 and D5/P3 fixed-seed full qualification regressions.
2. Add representative D0-D5 generated-world checks that compare compressed generation metadata with ordinary BFS qualification.
3. Assert deterministic hidden mechanics/topology/evidence for repeated fixed seeds.
4. Record generation timings in test diagnostics without imposing brittle wall-clock assertions.
5. Keep expensive tests under `slow`/`stress` markers.

Validation order:
1. solver proof tests;
2. focused D5/P2 and D5/P3 tests;
3. fast unit/integration suite;
4. extended tests;
5. small cross-seed stress matrix;
6. CLI/container smoke if branch is otherwise green.

No optimization is accepted merely because it is faster. A returned episode must still pass full `qualify_episode` with ordinary BFS and replay.