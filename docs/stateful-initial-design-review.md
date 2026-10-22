# Stateful candidate: fresh design judgement

Review date: 2026-10-21. Read-only review of NEXUS plan, actual candidate scripts,
and the new `stateful/search.py` and `stateful/laws.py`; no implementation changes.
Base commit: `6237c9adda7ac7254464783ac012d3681e24b03e`.

## Decision

**Do not admit the current modulo-5 target `(1,2,1,2)` as the proposed deep
trajectory tier.** It improves substantially on the trit candidate, but it fails
the requested two-commit, one-handoff shortcut test. An experimental stateful
family remains defensible. Strong-policy solvability and useful finite
adaptivity gaps have been established; universal non-decomposition and cognitive
hardness have not.

The most valuable next search is for candidates that pass the one-handoff test
before integration or broad seed generation. Target variation can be attempted,
but the observation channel itself may be the limiting design choice.

## Executed findings

All measurements below include one action for finish. Blind suffix searches
ignore operation/probe readouts but allow repeated finish: worlds that succeed
terminate; failed worlds continue the same predetermined sequence. Thus they
include a stronger baseline than one final blind guess.

| Check | Four trits | Four coordinates modulo 5 |
|---|---:|---:|
| Reachable initial laws | 256 | 256 |
| Exact optimal strong horizon | 9 | 11 |
| Known-law physical operations | 3–6 | 4–6 |
| Full initial probe-panel partition | 16 beliefs of 16 laws | 4 beliefs of 64 laws |
| Blind suffix after free initial panel | Every belief solvable by 11; 15/16 by 7 | No belief solvable through 14 |
| Initial-probes-only phase then blind suffix | Exact optimum 13 total | Not fully optimized |

Modulo-5 initial panel signatures are `(3,3,3,3)`, `(3,4,3,3)`,
`(4,3,3,3)`, `(4,4,3,3)`. Only the first two probes reveal coefficient bits.
The no-blind-suffix-through-14 result exhaustively visited 97,278 memo states;
it is a bounded negative certificate, not a claim of impossibility forever.

The trit failure is concrete: signature `(0,0,2,0)` admits
`operate 0, operate 2, operate 2, finish`, robust over all 16 remaining exponent
assignments. The exceptional all-2 signature admits
`0,0,1,2,finish,0,0,finish,3,2,finish`. Residual law ambiguity therefore cannot
stand in for mission-relevant uncertainty.

### Requested one-handoff test: modulo 5 fails

For each fixed committed prefix of length 0, 1, or 2, supply the complete four
one-step probe results and current scalar readout at the initial state and after
every prefix operation, for free. Partition laws by the complete transcript.
Then permit only a blind suffix, including success-aware repeated finish, with
remaining budget `11 - prefix_length`.

* Empty prefix: 0/256 laws lie in a suffix-solvable belief.
* Prefix `(1,)` or `(3,)`: 244/256 laws lie in a suffix-solvable belief.
* Prefix `(0,0)`: **all 83 resulting beliefs**, containing all 256 laws, have a
  blind suffix within 9 actions.
* Thirteen of the sixteen length-two prefixes solve every resulting belief.
  Only `(2,0)`, `(2,2)`, `(3,3)` fail for some worlds.
* This complete sweep used 19,862 memo states and did not hit a cap.

This is an intentionally generous observation oracle. It does not prove a
two-operation, eleven-total-action strategy under ordinary charged probes:
the free panels conceal up to twelve probe actions. It does prove that two
committed context changes suffice for the requested structural shortcut, so
the current candidate fails that expressly scoped deep-admission condition.

### Two different meanings of an early supported exit

I separately minimized supported branch length over **all strong policies
whose worst-case horizon is the optimal 11**, requiring the goal to be entailed
before successful finish:

| Minimum supported branch length | Laws |
|---|---:|
| 8 | 72 |
| 9 | 52 |
| 10 | 70 |
| 11 | 62 |

Minimum committed operations on such branches are 6–10: counts are
`{6:42, 7:82, 8:56, 9:74, 10:2}`. Computation checked all legal actions and all
winning sibling outcomes, using 3,623 branch-DP states and 18,004 strong-search
states for the action-length result.

This does **not** contradict the main agent's unrestricted supported-trajectory
result of 5–8. That optimistic search admits a short realized trace even when
other observation outcomes would exceed 11 or fail. The new production
`supported_minimum()` explicitly documents this distinction correctly. Report
both quantities. Never replace an unrestricted no-early-exit requirement with
the more favorable optimal-policy-only statistic. If the guarantee refers to
R1, use the actual playable R1 budget, not merely the minimax optimum.

After a free initial panel, every modulo-5 belief has strong remaining horizon
10. With remaining horizon 11, minimum supported committed operations across
those beliefs fall to 4–7. Thus a six-operation claim does not survive that
oracle intervention.

## Critical correctness and qualification issues

1. **Selected hard truths can change the public prior.** If target and published
   deterministic admission procedure reveal that only laws 132/133 could have
   been selected, a grammar-wide 256-law certificate overstates the actual
   uncertainty. Either qualify a complete public-design prior, qualify the
   conditional admitted support, or explicitly define and defend the benchmark's
   epistemic convention. If filtering laws, recompute all certificates after
   filtering; difficulty-dependent selection can require a fixed-point check.
   Disclose the actual support and selection procedure in proof metadata.

2. **The shortcut certificates must cover the actual observation projection.**
   The engine currently serializes the transformed artifact in probe and operate
   events. Keep hidden coordinates out of that payload and all observation,
   error, replay, and diagnostics channels. Public committed history plus scalar
   readout is compatible with reconstructing private state from the law. Prove
   movement, handling, wait, configuration and invalid actions introduce no
   additional specimen, reset or measurement shortcut before quotienting them
   out of the finite game.

3. **`inspect.py` miscounts a successful mixed-belief finish.** It appends the
   finish, reaches an empty success branch, then unconditionally adds another
   final action. Current inspected policies did not use finish this way, so the
   reported horizons above are unaffected. Production replay must count an
   explicit terminal finish exactly once and distinguish supported from lucky
   mixed-belief success.

4. **Cross-coordinate updates do not prove non-decomposition.** Each operation's
   unknown coefficient/exponent pair is independent of the other pairs in the
   current grammar. The complete initial/visited probe panel can therefore
   resolve much of the operational uncertainty very quickly. The one-handoff
   failure is more informative than graph connectivity or the 256-law count.

5. **There is a useful but narrow invertibility fact.** Before damage, each
   update is a composition of additive modular shears and hence a permutation.
   A safe word cannot merge two distinct states of the same law. This rules out
   that form of synchronization, but does not rule out returning the particular
   one-state-per-law belief to a common initial state, common goal, or useful
   equivalence class. Continue bounded belief-level reset/blind-word searches.

6. The prototype's `99` distance sentinel and silent exclusion of initially
   unreachable laws are unsuitable as a generic qualification contract. The
   new production code improves this with a finite state-count sentinel and
   includes all laws initially. Preserve fail-closed `SearchLimit`; never record
   a cap as a negative result. Source-bind target, initial state, public prior,
   cost convention, observable outcomes, search bound and all controls.

## Proposed admission contract

Keep the existing proposed thresholds explicit; do not lower them to admit the
current target. For a deep candidate, require:

* A full legal-action strong policy, replayed under every admitted law, with an
  exact optimum or honestly labeled interval. Count handling/travel separately
  if omitted by a proved quotient.
* Unrestricted pre-finish-supported cost at least 8 for every claimed admitted
  truth, using the actual public prior. Report physical shortest cost and minimum
  committed progress after free initial closure separately; do not infer them
  from total action count.
* No blind suffix through at least `H+3` after a free complete initial panel,
  with the exact bound stated. For a stronger R1 claim, use the actual R1 budget.
* **No fixed committed prefix of length at most two** followed by the requested
  free-panel/transcript-selected blind suffix within `H-prefix_length`. The
  current modulo-5 target fails. Enumerate all sixteen pairs, not one reference
  prefix. Record per-truth success coverage as well as the universal result.
* A separately named actuator-decomposition control if desired: constrain
  committed uses of each actuator to one contiguous block, while retaining all
  probes and failed finish. Prove no strong policy within the stated horizon
  under that restriction. This supports only “requires actuator revisitation,”
  not “cannot decompose into any independent tasks.”
* Diverse public goals/initial states and non-equivalent law structures, checked
  before model runs. Coordinate renamings or truth changes under one public
  target are not sufficient evidence of structural diversity. Include known-law,
  resettable-reference and easy negative controls with matched accounting.

## Stronger tractable direction if target variation fails

The current full panel consists of four modulo-5 values: one panel has enough
raw output capacity to distinguish more than 256 laws. Two committed changes
make that information useful for nearly every law. Increasing the state modulus
alone can improve apparent action length without preventing this collapse.

Try the same 625-state, 256-law size with **local actuation and a local readout**:
an operation changes one coordinate or a neighboring pair, while observation
reads one fixed coordinate; information about distant state must be transported
through cyclic couplings by real operations. Keep joint exact goals and legal
one-step probes. This changes the mechanical reason why experiments must alter
the escape system, rather than imposing an explicit experiment-count gate.
Consider shared latent factors across multiple operation rules so the law grammar
is not merely four independent two-bit identification problems. These are
candidate directions, not certified stronger instances; run the same shortcut
tests before integration.

## Reproduction identities

Read and executed with `PYTHONDONTWRITEBYTECODE=1`, Python standard library only:

* `explore4.py`: `29bfe9773436a87e4168d5803778883af0a2063f124e6fe4362dd3180e73e10f`
* `explore_mod.py`: `23e2debd33e901230e354e1a78c01bf48fed2a9c9192a7262f83ef4753dfcedd`
* `inspect.py`: `0fa4d354090af75743fb15053b7dc86a1fa25c540a4cb02a77c27ac2c31701bb`

Blind-search recurrence used a tuple of current `(law,state)` worlds and horizon.
For an operation, advance every world without observation partitioning. For
finish, remove goal worlds. Recurse with one fewer action; prune only if some
world's exact physical distance plus finish exceeds the remaining horizon.
For the handoff control, group worlds by the sequence of full panels along the
fixed prefix, then apply that recurrence to every group. This can be reproduced
directly using the production `initial_panel`, `branches`, `blind_possible`
primitives, with free panels inserted at every prefix state.
