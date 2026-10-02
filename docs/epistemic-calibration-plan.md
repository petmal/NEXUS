# Epistemic calibration roadmap

This plan implements the post-calibration NEXUS work identified after the Astra seed-17 run.
Milestones are ordered. A later milestone starts only after the previous milestone's tests,
qualification checks, cross-seed generation checks, and CI pass.

## Global invariants

Every milestone preserves the existing NEXUS guarantees:

- compiled execution remains deterministic;
- invalid actions never partially mutate state;
- generated worlds are solver-qualified and genuinely winnable;
- discovery guarantees are proved against all evidence-consistent causal worlds;
- no private rule, verifier, reference-plan, seed, or optimality metadata is exposed during play;
- victory is still an exact engine predicate and receipt;
- public difficulty remains semantic rather than a proxy such as row or room count.

New epistemic features add one invariant:

> Any generated distractor or auxiliary experiment must be classified mechanically from the
> public evidence. Difficulty must not depend on luck or on secretly knowing the selected rule.

## Milestone 1 — terminal performance telemetry

Goal: make successful and failed sessions report model behavior relative to the qualified baseline
without leaking private information during play.

Requirements:

- track accepted environment actions, probes, invalid game actions, protocol conflicts/duplicates,
  and rejected finishes;
- report a typed terminal-only performance summary;
- for D0-D3 report physical optimum, minimum guaranteed probes, baseline actions, excess actions,
  excess probes, budget remaining, and the runtime counters;
- no optimality fields appear on non-terminal responses;
- duplicate/retried transport calls do not inflate game-action counts;
- replay/engine semantics remain unchanged.

Acceptance:

- unit tests cover wins, budget failure, invalid actions, duplicate requests, and failed finishes;
- existing end-to-end and property tests remain green.

## Milestone 2 — paired scenario-family generation

Goal: make difficulty comparisons controlled experiments.

Requirements:

- derive deterministic named RNG streams with a stable cryptographic hash, never Python hash();
- separate at least mechanics, topology, evidence, and presentation randomness;
- D0/D1/D2 for a given seed and planning level share the same one-machine mechanics, artifact,
  target, phases, topology, and role locations whenever generated as the same scenario family;
- planning variants share mechanics/evidence while topology changes;
- difficulty-specific evidence rejection must not silently reroll mechanics;
- record a private scenario-family identifier and family attempt;
- retain rejection sampling and full qualification before a world is returned.

Acceptance:

- property tests prove pairing invariants across multiple seeds;
- all existing D0-D3 profiles still generate successfully across the stress seed set.

## Milestone 3 — compact state protocol

Goal: reduce repeated context without changing game semantics.

Requirements:

- protocol version is advanced for the changed observation shape;
- manifest remains the source of immutable goal/evidence/action-contract context;
- action responses omit repeated immutable goal/evidence metadata;
- explicit observe/status remain sufficient for robust clients;
- old private episode files remain readable where practical; no hidden-state leak is introduced.

Acceptance:

- protocol/service/CLI tests validate exact response shapes and idempotency;
- generated-session MindTrial-style request flow remains functional.

## Milestone 4 — experiment-value analysis

Goal: generalize causal discovery from a single number (minimum probes) to explicit experiment
quality under the current belief state.

Definitions:

- legal experiment: mechanically executable probe context;
- discriminative experiment: evidence-consistent hypotheses predict more than one observation;
- mission-relevant experiment: the partition can change the minimum guaranteed winning policy;
- useless experiment: provably cannot improve the mission-relevant belief/policy;
- risky commitment: an irreversible operation while remaining viable hypotheses disagree about
  whether the commitment preserves guaranteed success.

Requirements:

- expose private analysis objects for candidate experiment partitions and classifications;
- keep the player unaware of these classifications;
- post-run analysis can label probes and irreversible operations using only information available
  to the player before each action;
- existing D0-D3 minimum-probe guarantees remain exactly reproducible.

Acceptance:

- hand-constructed proofs cover zero-information, discriminative-but-irrelevant, mission-relevant,
  redundant, and risky-commit cases;
- property tests compare the new analyzer with current D0-D3 guarantees.

## Milestone 5 — D4 selective experimentation

Implementation note after Milestone 4: non-destructive `probe` semantics remain identical at all
difficulty levels. D4 is therefore a **cost-optimal experiment-selection** profile, not a profile
where a special artifact is mechanically required to make an observation. Brute-force probing is
legal. Qualification must prove that selecting a more informative context yields a lower
worst-case total environment-action cost than indiscriminate probing.

The exact minimum guaranteed total-action policy solver originally scoped for Milestone 7 is a
prerequisite for this guarantee and is implemented at the start of Milestone 5. Milestone 7 then
focuses on exposing exact regret/trace metrics and validating the generalized solver across all
profiles rather than introducing the solver for the first time.


Semantic guarantee:

> Multiple plausible legal experiment contexts exist. At least one is predictably useless or
> mission-irrelevant from public information, while an informative experiment is required by the
> minimum guaranteed policy. The efficient policy must select informative experimentation rather
> than indiscriminately probing available contexts.

Requirements:

- support auxiliary artifacts that are not required by the final goal;
- generate at least one lower-cost epistemic resource/context and at least one epistemic distractor;
- distractor uselessness is proved from the full evidence-consistent hypothesis set, not from the
  selected hidden rule;
- the world remains winnable if the agent guesses or brute-force probes; the semantic guarantee
  is that an informative experiment strictly improves minimum guaranteed total action cost;
- qualifier proves the D4 semantic profile before return.

Acceptance:

- generated D4 episodes have a mechanically identified informative context and distractor;
- multiple seeds pass generation, solver, replay, and qualification stress tests.

## Milestone 6 — D5 experiment construction

Semantic guarantee:

> A guaranteed efficient policy must construct an informative experimental state using auxiliary
> objects and/or machines before testing the mission-relevant transformation.

Canonical pattern (not hard-coded as the only pattern):

    acquire epistemic artifact
      -> auxiliary transformation
      -> informative probe of mission machine
      -> mission transformation
      -> finish

Requirements:

- support multiple artifacts in generated worlds;
- support auxiliary epistemic machines whose purpose is information acquisition, not the final
  goal trajectory;
- support functional distractor artifacts/machines that do not improve the guaranteed policy;
- qualifier proves the auxiliary epistemic chain is necessary for the selected profile and proves
  distractor paths do not improve the minimum guaranteed policy;
- generation remains compositional rather than selecting a pre-authored puzzle.

Acceptance:

- hand-authored proof fixtures first establish that the policy analyzer can distinguish required
  epistemic intermediates from distractors;
- generated D5 episodes satisfy the same proof mechanically across stress seeds.

## Milestone 7 — integrated belief-policy cost and epistemic regret

Goal: generalize the exact minimum worst-case action-cost solver introduced for D4/D5, expose
regret/trace metrics from it, and validate it across all discovery profiles. This replaces the
D0-D3 approximation "physical optimum + probe count" wherever an exact policy cost is available.

State conceptually includes:

    physical world state + evidence-consistent hypothesis set

Requirements:

- search policies may branch on observable probe/operate outcomes;
- optimize total environment actions, including travel, acquisition, waits, auxiliary operations,
  probes, mission execution, and finish;
- record minimum guaranteed total cost and one policy witness privately;
- terminal performance reports exact total regret when available;
- preserve the existing physical BFS as an independent concrete-world solvability proof.

Acceptance:

- small exhaustive fixtures are independently enumerable and match the policy solver exactly;
- D0-D3 exact costs agree with the previous baseline where the assumptions hold;
- D4/D5 costs include epistemic detours and cannot be undercounted by physical optimum + probes.

## Milestone 8 — dependency planning and resource pressure

Planning:

- introduce dependency-based planning complexity rather than merely increasing room count;
- use generated dependencies (for example phase/access/resource ordering) that remain declarative
  and solver-qualified;
- do not add a new planning level unless the generator can prove it creates a distinct planning
  burden.

Resource pressure:

- add a separate resource-pressure axis only after exact policy costs exist;
- default remains forgiving;
- tighter profiles derive their budgets from the exact guaranteed policy cost plus an explicit
  allowance, never from arbitrary constants that make worlds accidentally impossible.

Acceptance:

- every public profile is mechanically qualified;
- cross-seed stress generation has no impossible/invalid episodes;
- CI and deterministic replay remain green.

## Commit discipline

Each milestone uses a focused group of commits:

1. tests/proof fixtures defining the invariant;
2. implementation;
3. integration/docs/stress fixes only if required.

No milestone proceeds while the previous milestone has failing tests, failed qualification,
unexplained generation rejection, or unresolved ambiguity.
