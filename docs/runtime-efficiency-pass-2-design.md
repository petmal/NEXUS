# Runtime efficiency pass 2 — design and robustness proof plan

Base: `feat/epistemic-calibration` at `6a8e6f2c429735cd7775ad22bc9eba436aceee94`.

This pass targets high-value, low-risk runtime/allocation costs that remain after the first D5 generation optimization. The governing rule is that no optimization may weaken generation or qualification semantics. Every returned episode must remain exactly solver-qualified and replay-valid under the existing independent checks.

## Scope

Implement only these six changes:

1. remove duplicate belief-node storage;
2. copy an artifact only once per `apply_effect()` call;
3. allow richer cached policy results to satisfy weaker no-action-value queries;
4. stop deep-copying the whole `PrivateEpisode` for each causal hypothesis;
5. avoid redundant deep copies when normalizing fresh solver-owned states;
6. remove the CLI's redundant second qualification after `generate_episode()`.

Explicitly defer specialized probe transitions, compact custom solver state, multiprocessing, new pruning rules, and approximation.

## Invariant 1 — belief visited-node accounting

Current exact minimax search stores each explored key in both `memo` and `visited_nodes`. Every search body path stores a boolean in `memo` before returning, so the set of evaluated keys equals `memo.keys()` at solve completion.

Optimization:
- remove `visited_nodes`;
- report `visited_belief_nodes = len(memo)`.

Proof obligation:
- for deterministic fixtures covering solvable, unsolvable, fixed-cost certificate, and branched belief cases, old/reference and optimized solvers must return identical solvability, exact optimum, witness, action values, and visited count;
- no algorithmic ordering or pruning changes are permitted in this change.

## Invariant 2 — single-copy rule interpretation

Current `apply_effect()` deep-copies the artifact at every recursive AST node. The rule language is purely sequential mutation of one artifact value; a child effect never needs to preserve its input object independently from its parent.

Optimization:
- copy the caller-owned artifact exactly once at the public `apply_effect()` boundary;
- recursively apply validated effect nodes to that private working artifact in place;
- retain current result validation semantics for `SET` where necessary.

Proof obligation:
- differential equivalence against a local reference implementation preserving current recursive-copy semantics;
- exhaustive coverage over every generated transformation-rule catalogue member, every shape, both phase parities, all values 0..10, all orientations, both polarities, and representative patterns;
- focused coverage of `ALWAYS`, `PHASE_EQUALS`, `VALUE_MODULO`, `AND`, `OR`, `NOT`, `SET`, nested `SEQUENCE`, and nested `CONDITIONAL` nodes not necessarily present in the generation catalogue;
- input artifact must be byte/model equal before and after every call;
- result must be a distinct artifact object.

## Invariant 3 — cache dominance

A cached policy result that includes action values contains the same exact minimax optimum/witness proof as a no-action-value result, plus additional analysis. Therefore it can answer a weaker `include_action_values=False` query if all other semantic key components and proof bounds match.

Optimization:
- on a miss for a no-action-value query, search the small LRU for richer entries with the same semantic episode, physical-state limit, and hypothesis limit;
- adapt the richest compatible result by dropping action values using the existing bound-safety logic;
- do not permit weaker cached entries to answer stronger action-value queries.

Proof obligation:
- fresh no-action-value solve == adapted richer cached solve in solvability, exact optimum, witness and exact certificate behavior;
- insufficient cached action bound must still miss/recompute;
- unsolved/exhausted cached results must obey the existing stored-bound restriction;
- requested action-value subsets remain isolated from other rich selections.

## Invariant 4 — hypothesis episode isolation

Each causal hypothesis differs from the base episode only in selected rule mappings and the solver-local normalized initial action budget. Topology, goal, evidence, metadata, reference plan, secret, room data and unrelated rules are read-only during solving.

Optimization:
- shallow-copy the `PrivateEpisode` and public episode;
- copy only the mutable maps/state that will be changed (`rules` and initial state/resources);
- leave immutable/read-only structures shared.

Proof obligation:
- constructing and solving any hypothesis must not mutate the base episode;
- two sibling hypothesis episodes must not observe each other's rule or initial-budget mutations;
- old deep-copy and optimized hypothesis episodes must serialize equivalently except for object identity;
- compressed physical costs and exact minimax results must remain identical on proof fixtures.

## Invariant 5 — fresh-state normalization ownership

`step()` always returns a newly deep-copied state on successful consuming transitions. The solver then deep-copies that fresh state again merely to zero `turn` and restore the synthetic search budget.

Optimization:
- keep the existing copying normalization for caller-owned initial/external states;
- add an internal normalization helper that mutates only a solver-owned fresh state returned by `step()`;
- use it only at call sites where ownership is mechanically evident.

Proof obligation:
- optimized and copying normalization produce identical semantic/search keys;
- pre-transition/source states remain unchanged;
- successful transition results match the old implementation after normalization;
- no shared state from branch caches or caller inputs is mutated.

## Invariant 6 — one qualification per generated CLI episode

`generate_episode()` returns only after final qualification succeeds. The CLI `generate` command currently calls `qualify_episode()` again after saving the episode.

Optimization:
- remove that second CLI qualification.

Proof obligation:
- unit test patches/counts `qualify_episode` at the generation boundary and proves `generate_episode()` still rejects a failed final qualification;
- CLI test proves it saves/prints a generated episode without invoking an extra qualification pass;
- `nexus qualify` remains unchanged as the explicit independent validation command.

## Cross-cutting robustness gate

After individual proof tests pass:

1. existing exact solver proof suite;
2. complete unit/integration fast suite;
3. slow/extended suite;
4. at least one seed across all 24 D0-D5 × P0-P3 profiles;
5. dedicated cold D5/P3/R1 generation with exact qualification;
6. compare generated semantic metadata and exact costs against the pre-optimization baseline for fixed proof seeds where deterministic generation is expected to be unchanged.

No change is accepted if it changes hidden laws, topology, evidence, goal, physical optimum, guaranteed-policy optimum, resource budget, reference-plan validity, or final qualification outcome for the same seed/profile.

## Performance measurements

Record for cold D5/P3/R1:
- wall time;
- user CPU time;
- peak RSS;
- exact physical and guaranteed-policy costs.

The optimization is worthwhile even if only memory improves, but any semantic discrepancy is a hard failure regardless of speedup.
