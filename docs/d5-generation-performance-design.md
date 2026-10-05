# D5/P3 generation performance — design and proof plan

Base: `5d95a584fdd0254b87d7f02a5a88034f3b9bfae7`.

Goal: reduce cold D5/P3 generation time and peak/resident memory without weakening any property that makes a returned NEXUS episode benchmark-valid.

This work deliberately does **not** add persistent episode caching. It optimizes the first generation of a previously unseen seed/profile.

## Safety invariant

A generation optimization is acceptable only if it preserves the semantic contract of the returned episode.

For every returned episode, final qualification remains authoritative and must independently verify at least:

1. public/private separation and disclosed causal grammar;
2. discovery-profile semantics (including D4/D5 experiment-value requirements);
3. exact theory-consistent guaranteed-policy cost and witness;
4. P3 causal isolation via reconstruction of the P2 counterfactual;
5. an independent ordinary-action BFS optimum;
6. reference-plan length equal to that optimum;
7. replay of an ordinary-action winning trace with exact canonical hashes and victory receipt;
8. exact action-budget/resource-pressure semantics.

Faster generation-side solvers may reject or select candidates, but they may never replace these final independent checks for a returned transformed episode.

## Baseline cost structure

D5/P3 currently performs several overlapping proofs:

```text
generate fully-qualified D5/P2 base
  ordinary BFS
  exact belief-policy solve + all immediate action values
  full P2 qualification

compile P3
  deep-copy candidate rooms
  ordinary BFS per candidate
  exact belief-policy solve + all immediate action values per candidate

apply R1/R2

full final qualification
  exact D5 belief-policy solve
  exact P2 counterfactual policy proof
  ordinary BFS final episode
  ordinary BFS P2 counterfactual
  replay / metadata / leakage checks
```

The first five optimizations remove duplicated or unnecessarily expensive internal work while leaving the returned-world proof boundary intact.

---

## Optimization 1 — skip full qualification of the intermediate P2 base for P3

### Change

Allow `_generate_episode_core(...)` and its D4/D5 family generators to return an internally generated P0-P2/R0 episode without running `qualify_episode` when—and only when—it is immediately consumed by `_add_planning_dependency` for P3.

Normal P0-P2 public generation continues to qualify before return.

P3/R1/R2 still receives one complete final `qualify_episode` after all transformations.

### Why it is safe

The intermediate P2 episode is not exposed to the player or caller. Its metadata and solver results are construction hints only.

The final P3 qualifier independently reconstructs the P2 counterfactual by:

- removing the dependency artifact;
- restoring the original goal;
- solving the counterfactual with ordinary BFS;
- proving the exact counterfactual minimax policy cost;
- checking that both physical and guaranteed-policy cost increases equal the stored dependency overhead.

Therefore an invalid intermediate P2 can at worst cause generation to fail at final qualification; it cannot cause an invalid P3 episode to be returned.

### Proof/tests

1. For representative D0-D5 P2 seeds, `_generate_episode_core(..., qualify_result=False)` itself passes `qualify_episode` when explicitly checked.
2. P3 generation still calls final qualification exactly once and rejects a deliberately corrupted final episode.
3. Ordinary P0-P2 generation still calls full qualification before return.
4. Existing P3 planning-dependency qualification tests remain unchanged and green.

---

## Optimization 2 — use exact movement-compressed physical solving during generation

### Change

Replace generation-side ordinary `solve(...)` calls used for candidate screening/reference-plan construction with `solve_compressed_physical(...)`.

This applies to core generation and P3 candidate screening. Final `qualify_episode` continues to run ordinary BFS as the independent physical oracle.

Extend `CompressedPhysicalResult` with `max_frontier_size` so generation diagnostics remain meaningful.

### Existing proof

`docs/exact-belief-policy-solver-design.md` already proves that movement compression preserves exact cost under current engine semantics:

- movement changes only `agent_room`;
- movement does not advance phase;
- movement does not alter artifacts/machines;
- movement emits no hidden-law-dependent observation;
- topology is static;
- carried artifacts move without extra cost;
- every movement segment between interactions can be replaced by a deterministic shortest path;
- every compressed macro expands to legal ordinary actions with identical interaction outcomes and exact cost.

### Additional robustness proof

Generation obtains an expanded ordinary-action plan from the compressed solver. Final qualification independently runs ordinary BFS and checks:

- the BFS optimum equals `metadata.optimal_action_count`;
- stored reference-plan length equals that optimum;
- BFS winning plan executes and replays exactly.

Thus a compression bug cannot silently certify a returned world.

### Metadata semantics

`solver_visited_states` and `solver_max_frontier_size` are generation diagnostics, not semantic properties. They may now describe the compressed generation solver. Qualification must not require those implementation-specific counters to equal ordinary BFS counters. Optimal action count remains exact and mandatory.

### Proof/tests

1. Existing compressed-vs-BFS proof fixtures remain green.
2. Add generated D0-D5 fixtures asserting compressed optimum equals ordinary BFS optimum.
3. Expanded compressed plans execute successfully and have exact optimum length.
4. Qualification rejects an intentionally wrong `optimal_action_count` even though it no longer compares exploration counters.

---

## Optimization 3 — compute only requested D4/D5 initial action values

### Problem

The minimax solver currently computes a worst-case total cost for every immediate legal interaction whenever `include_action_values=True`. D4/D5 definitions inspect only a small named subset:

D4:
- mission probe `M1/A1`;
- epistemic probe `M1/A2`;
- distractor probe `M1/A3`.

D5:
- constructor operation `M2/A2`;
- direct mission probe `M1/A1`;
- distractor operation `M3/A3`.

P3 adds another artifact and therefore increases irrelevant immediate branching.

### Change

Add an optional `requested_action_values` parameter to `solve_guaranteed_policy`.

Semantics:

- `include_action_values=False`: compute no initial values (backward compatible);
- `include_action_values=True, requested_action_values=None`: compute all immediate values (backward compatible);
- `include_action_values=True, requested_action_values=(...)`: compute values only for exactly those immediate actions.

The action selector affects only diagnostic/action-value calculation **after** the exact minimax optimum and witness are proved. It must not filter actions available to `can_win` or witness construction.

### Why it is safe

The optimal policy search still enumerates the complete legal macro-action set. Requested values merely choose which already-legal initial alternatives receive extra counterfactual cost analysis.

Therefore:

```text
optimal(policy, requested subset) == optimal(policy, all values)
witness(policy, requested subset) == witness(policy, all values)
```

Only `initial_action_values` differs by projection.

### Proof/tests

1. Solve the same fixture with all values, requested subset, and no values.
2. Assert identical solvability, viable hypothesis count, optimum, and witness.
3. Assert subset results equal the corresponding entries in the full result.
4. Assert requesting a non-immediate/nonexistent action simply yields no value (or reject explicitly; choose one documented behavior and test it).
5. D4/D5 qualification remains unchanged semantically and green using the requested subset.

---

## Optimization 4 — bound policy-result cache memory with a small LRU

### Problem

The process-global `_POLICY_RESULT_CACHE` currently retains up to 256 deep-copied `BeliefPolicyResult`s and clears the whole cache only at the limit. Rejected topologies have different semantic keys, so long generation can retain many large policy witnesses/action-value sets. Python may retain freed arenas even after clear, producing steadily increasing RSS.

### Change

Use an `OrderedDict` LRU with a conservative limit of 16 entries.

- cache hit moves entry to MRU;
- insertion updates/replaces same key;
- overflow evicts one LRU entry immediately;
- keep deep-copy-on-store/return isolation;
- cache key includes the action-value selection so a partial action-value result is never mistaken for a full one.

Expose only a private test reset/introspection helper if needed; no public API.

### Why it is safe

Caching is a pure memoization optimization. Eviction changes only whether a calculation is repeated. It cannot change the mathematical result.

Deep copies preserve caller isolation. Bound-specific adaptation rules remain unchanged: an exhausted result can only prove through its searched bound, and rich action-value results are reused only when their selection/bound is sufficient.

### Proof/tests

1. Cached and uncached equivalent calls return equal results.
2. Mutating a returned model does not mutate cached data.
3. Insert >16 distinct semantic keys and prove cache length never exceeds 16 and LRU entry is evicted.
4. Requested-action subset/full-action results use distinct cache keys.
5. N/N-1 exact policy certificates still pass.

---

## Optimization 5 — replace cryptographic solver state keys with immutable semantic tuples

### Problem

Every solver state currently calls `model_dump(mode="json")`, removes cost fields, serializes canonically, and computes SHA-256. Search visited/memo tables need equality and hashing, not a cryptographic digest.

### Change

Define an immutable `SearchStateKey` tuple containing every semantic field relevant to future transitions/goals:

```text
phase
agent_room
sorted artifacts:
  id, location, shape, pattern, orientation, value, polarity
sorted machines:
  id, room_id, uses_remaining
terminal_status
```

Intentionally omit only:

- `turn`;
- `resources.actions_remaining`.

Those are already omitted by the current key because BFS depth/minimax budget dominates them.

Replay/canonical-state integrity continues to use `canonical_hash`; only internal solver memoization changes.

### Proof of equivalence

For current `WorldState`, the old key is SHA-256 of exactly the JSON state after removing `turn` and `actions_remaining`. The proposed tuple contains every remaining field exactly once in deterministic key order. Therefore:

```text
old_key(s1) == old_key(s2)
iff
new_key(s1) == new_key(s2)
```

assuming valid Pydantic `WorldState`s and current schema.

### Proof/tests

1. Changing only turn leaves key equal.
2. Changing only actions remaining leaves key equal.
3. Independently vary phase, room, every artifact field, artifact membership, machine room/use count, machine membership, and terminal status; each must change the key.
4. Dict insertion order must not affect key.
5. On representative generated worlds, ordinary BFS optimum/plan length before and after stays equal to compressed optimum and qualification passes.
6. Canonical replay hashes remain SHA-256 based and unchanged.

---

## Cross-optimization proof gate

Before accepting the branch:

1. TDD proof tests for each optimization.
2. Fast unit/integration suite.
3. D5/P2 and D5/P3 targeted generation on fixed seeds.
4. At least a small D0-D5 cross-profile sample asserting every returned episode passes full qualification.
5. Compare deterministic public/private world semantics against base `5d95a584` for fixed seeds where metadata implementation diagnostics are excluded:
   - public episode mechanics/evidence/goal/topology must match;
   - hidden rules must match;
   - physical optimum and guaranteed-policy optimum must match;
   - reference plan may differ only if both are optimal ordinary-action plans.
6. Measure generation runtime and, where practical, peak RSS before/after. Performance improvements are secondary to semantic equality.

## Stop conditions

Stop and redesign rather than weakening validation if:

- compressed generation chooses a world ordinary BFS says has a different optimum;
- skipping P2 qualification permits a P3 world that final qualification does not catch;
- requested action-value projection changes optimum or witness;
- tuple keys merge any semantically distinct states;
- cache selection/bound reuse changes exact policy results;
- deterministic world mechanics drift for the same seed/profile.
