# Stateful discovery: fresh implementation judgement

Review date: 2026-10-21. Repository: `NEXUS`, feature branch
`feat/theory-prior-axis`, baseline `6237c9adda7ac7254464783ac012d3681e24b03e`.
Read-only review of the implementation; the owner made the one required fix.

## Decision

**The reviewed core is suitable for the explicitly scoped experimental pilot,
subject to the final source-bound preflight and ordinary release gates.** One
reproducible correctness blocker was found and fixed during review. No remaining
unsound pruning, physics/probe mismatch, action reset, hidden-state leak, or
incorrect success-support classification was found in the inspected paths.

This is not approval of a universal non-decomposition or model-hardness claim.
The strongest admitted statement remains the bounded feedback qualification
under the declared 256-law public prior. I did not repeat the expensive full
matrix preflight in this review; the owner must run it after the final source
freeze. The stale legacy repair manifest must also be regenerated only after
its required proof and conformance gates.

## Required fix, now verified

**Known-law controls rejected valid worlds requiring more than eight operations.**
The original `Investigator._construct` attempted `install(belief, 8)` and then
required a strictly smaller observation partition. A singleton belief cannot
split, so a physically reachable singleton with distance nine returned no
policy. This was not merely an arbitrary private-state edge case:

* Seed 21 selects law 175 and target `(2,3,1,2)`.
* Its known-law physical optimum is nine operations.
* T0/D5 generation raised `ValueError: no public policy established for complete
  prior`.
* T0/D0 generation succeeded, but its public policy also failed because it
  constructed the investigator before executing the provided procedure.

The owner fixed `policy.py:59–74` to use exact distance descent for every
singleton and moved supplied-procedure execution before investigator creation
at `policy.py:140–145`. I independently verified both T0/D0 and T0/D5 seed 21
finish in 12 actions, receive `supported_win`, and reproduce canonical replay
hashes. I also checked maximum-distance singleton states for each supported
target: physical distances 14, 15 and 15 produce costs 15, 16 and 16 including
finish. The fix therefore covers arbitrary reachable singleton fallback states,
not only the initial nine-operation regression.

## Search and proof review

The belief is an ordered tuple of one current physical state per surviving law.
The observation projection and state transitions agree between the search and
the runtime:

* `search.py:_branches` partitions by the hypothetical next scalar reading.
  Committed operations retain the successor state; probes retain the original
  state. Successful finish worlds terminate; rejected finish removes precisely
  the goal worlds from the continuing branch.
* `strong` removes only an unchanged, uninformative self-loop and branches that
  exceed a per-law exact physical lower bound. Its integer horizon decreases.
  A cap raises `SearchLimit` and is not cached as a negative answer.
* `supported_trace` is an A* search with an admissible actual-law physical
  distance heuristic. The selected truth determines which *observable branch*
  is being minimized; it cannot directly select an unobserved physical state.
  Strictly improving costs handle zero-cost probes and rejected finishes in
  the operations-only audit. The optimistic result deliberately allows unsafe
  off-trajectory branches and does not claim to be a strong-policy optimum.
* `blind_possible` ignores observation partitions, includes all four operations
  and success-aware repeated finish, and prunes only exact physical lower-bound
  failures and unchanged beliefs. Its packed law/state representation preserves
  one world per law. Completion consumes an available finish action exactly
  once.
* The adaptive witness builds safe continuations at every off-spine observation
  and then scalar-replays the contingent policy under every law. Its explicit
  handling of early mixed-belief successful finishes avoids the earlier
  double-counting defect in the prototype.

As an independent regression exercise, I implemented unpruned finite-horizon
strong and blind recurrences using tuple states and the scalar interpreter.
Twenty randomly selected two-law beliefs near the goal, at horizons zero through
four, gave **200 matching comparisons** with the production solvers. This is
supporting evidence for the reviewed recurrence, not a substitute for the
large bounded-negative preflight.

The all-prefix handoff test is correctly stronger than a predetermined two-step
experiment. For an adaptive two-step prefix, its realized branch is one of the
enumerated fixed words; its full observation transcript occurs in the
corresponding partition. Free complete probe panels dominate any subset or
repetition of the legal probes at those states. Rejected finish cannot reveal
additional law information during these prefixes: every selected target has
four nonzero coordinates, whereas at most two local operations cannot reach it.

## Runtime, inference, and controls

The shared engine validates carried-artifact and machine-location preconditions,
charges actions, and commits copied state only on success. The new adapter
contains no additional specimen path. Taking/dropping, moving, waiting, observing,
and invalid actions neither alter the physical history nor create information
about hidden registers. Phase modulus is one; machine uses are unlimited;
configuration is rejected. The HTTP service enforces the family's existing
single-session requirement. These facts justify omitting handling/travel from
the finite physics game and adding the mandatory take/optional move separately.

The public artifact consists only of committed history and its visible reading.
Probe events contain a hypothetical extended history and reading; the inference
adapter uses that history to filter laws but updates its committed history only
for operate. The mission tracker independently follows actual operate events
and specimen eligibility. A rejected finish in the wrong room or without the
carried seal therefore does not incorrectly eliminate possible laws. Winning
feedback is not fed back into the pre-submission posterior, preserving the
supported-versus-compatible distinction. The public action contract and
evidence describe the local modular law, scalar display, joint target, ordinary
probe semantics and absorbing collapse.

## Verified measurements

I reproduced these optimistic supported minima for the four selected hard truths
at target `(1,2,1,2)`. Costs exclude taking/moving; action minima include finish.
The operations-only minimum forgives all probes and rejected finishes.

| Law | Seed | Supported action minimum | Minimum committed operations with free evidence |
|---:|---:|---:|---:|
| 200 | 737 | 12 | 10 |
| 219 | 229 | 13 | 10 |
| 234 | 605 | 12 | 11 |
| 249 | 468 | 13 | 11 |

The current new unit suite passed: **19 tests in 3.32 seconds**. It includes the
independent complete kernel comparison, all-world constructive policy replay
for all three targets, live supported wins, serialization, canonical replay,
invalid-action atomicity, probe nonmutation, handling non-reset, irreversible
collapse, compatible lucky success, known-law minima, cap failure, contract
tampering and paired-matrix validation. The owner's new seed-21 controls were
included in that run.

## Release caveats and follow-up

1. **Freeze, then rerun.** The singleton change alters constructive references
   and potentially adaptive fallback upper bounds. Final reports must come from
   the final source and must pass the complete matrix, source-identity check,
   package/container path, and existing regression gates. Earlier upper-bound
   numbers should not be copied into final documentation.
2. **Keep prior selection explicit.** Generation is unfiltered; operator seed
   selection chooses a challenge set. The 256-law posterior guarantee assumes
   players do not receive seeds, the admission filter, proof reports, or this
   matrix. If those selection facts become available to evaluated players,
   recompute against the conditional prior. A declared public-prior convention
   is not a population-sampling theorem.
3. **Keep diversity claims narrow.** All four hard rows use one initial state,
   one target and one topology; they share gains 0/1 equal to two and powers
   0/1 equal to two/one. They vary the remaining gains/powers. The additional
   generated targets are supported by the reference policy, but are not
   demonstrated hard target/initial-state contrasts in this matrix.
4. **Correct the historical design checkpoint.** At review time,
   `docs/stateful-discovery-plan.md` still described the rejected three-register
   update, nonlinear display, and horizon-11 provisional kernel as the selected
   design. The owner is already rewriting that section. Preserve rejected
   designs as explicitly historical, and describe the final one-coordinate
   update and visible `x0` accurately.
5. **Useful future solver regression.** Retain a compact independent bounded
   recurrence comparison or a specific success-aware mixed-finish fixture in
   tests. Current tests exercise the all-world policy well, but the negative
   certificates deserve a direct regression that would fail if finish were
   accidentally reduced to a single terminal guess.

## Reviewed source identities

These SHA-256 values identify the core reviewed after the singleton correction;
the final source-bound report remains authoritative for release.

| File | SHA-256 |
|---|---|
| `stateful/search.py` | `6a7795aab739fced5f64c271a8569c74dcafb4b25af39f7c95736228c18f7403` |
| `stateful/policy.py` | `803c0579e644f2dc6523a39b66834b3910bd01d0fd48dcb3f20d613bd522a17d` |
| `stateful/proof.py` | `06b4b950cdbae5758fd4abfd9967eac5857de62687da4eda51ce33b207aeca3e` |
| `stateful/runtime.py` | `1638a7347a378b2d5247d2b0ebebf19be255cc6162392daf8d58a2954eccd43a` |
| `stateful/inference.py` | `6c335f200f75d0bd2bef6e94112bd584d38a6f4e4cdced2e1c8d41a0b168a235` |
| `evaluation/stateful.py` | `540e74a39838bb0135701723f98dee3ab901a2f1744348beed599437d5902c4b` |
