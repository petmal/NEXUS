# Compositional repair: observation and acceptance scope

This experimental family is additive; old families and their numeric difficulty
profiles retain their semantics. It currently admits T0/D0 or T3/D5, P0/P1, R1.
It does not claim a calibrated ladder for intermediate T/D values.

The complete finite construction and independently reproduced numbers are in
`structural-reasoning-proof.md` / `.json`; reproduce the independent design probe
with `uv run python scripts/poc_compositional_repair.py` (outputs in ignored
`analysis/compositional-poc/`). Production seeds map by `seed % 615` into the
publicly disclosed solvable grammar, in lexicographic raw-world enumeration order.
Uniform probability claims require uniform admitted indices. No seed filtering
is performed for difficulty; only the separately labelled pilot selects fixtures.

## Public response reduction

A live state factors into private immutable graph/mechanisms plus public room,
inventory, apparatus settings, survey preparation, applied seal treatment, turn,
phase and resources. There is no private specimen state. Arithmetic is exact F3.

- Stage configure validates only public arity/ranges/location. Stage operate
  replaces the eight public preparation fields and clears old readings. Stage
  preview returns that same public preparation without committing it.
- Each sensor probe or operation returns one scalar plus the specimen's already
  public preparation. All 4,374 requests reduce to 486 normalized queries by
  subtracting the known output offset `c+mode*d`; this is an outcome-label
  bijection. Untreated specimens use the disclosed zero preparation. Any mission
  point, context and internal trim is legal immediately, in any order.
- Seal sensor responses are insensitive/null. Surveys do not accept treatment.
  Reusing a specimen, replaying cached readings, previewing a treatment, configuring
  machines or acting on insensitive materials adds no hidden information.
- Doser operate commits four public values to the carried seal. Configure and
  probe alone cannot apply it. The goal tests all four response equations, accepts
  every satisfying vector, and reports only one acceptance bit on an eligible
  finish. It never exposes a residual vector or a failing coordinate.
- Ineligible finish depends on public physical state; it must not eliminate a
  scientifically valid repair. The shared applied-treatment tracker enforces this
  distinction in terminal posterior reconstruction. Failed eligible finish
  removes every world accepting that attempted vector, not one canonical target.
- Movement, take/drop, waiting, observe/status/manifest/evidence and errors depend
  only on public state/contracts. Stocks are identical reusable surveys. Phase is
  constant. There is no reset, family switch, private evidence or hidden import path.
  Invalid actions are atomic. Active responses contain no inference diagnostics.

Induction over these transition classes reduces each successful science-bearing
reading to one normalized query and each eligible finish to a repair-membership
observation. Free preparation in the mathematical audit is a relaxation; its
success ceilings do not require artificially costly preparation. Timing side
channels, source access, externally shared episodes and repeated reset attempts
are outside this single-session claim.

## Witness and costs

The public policy reads only manifest/evidence/status/observations/action responses,
maintains the complete public belief, and stops at a common winning repair.
At P1 it takes seal and one survey, moves once, performs at most seven
configure/prepare/probe triples, then configures/applies/finishes: at most 27
successful actions. The challenge budget is 30. The allowance admits a spare
three-action treatment attempt; it is not a guarantee against arbitrary wasted
work. T0 supplies a valid repair and takes 5 actions with budget 8. P0 saves one
move. These are constructive bounds, not optimality or three-round lower bounds.

## Executable premises and limits

Tests independently enumerate the entire raw grammar and admitted support, all
repair sets, all raw/normalized readings, all 615 public-policy wins and replays,
HTTP privacy/save-load, alternate accepted repairs, preview noncommit, invalid
atomicity, exact query/guess bounds, and passive/context closure obstructions.
The generic decision audit uses acceptance masks and intersections; equivalence
classes alone are unsound when winning regions overlap.

The factored argument is supported by tests, not a formal proof of all Python
runtime behavior or enumeration of every inventory/history product. Qualification
is experimental and constructive. Twelve worlds require an internal intervention
for a guaranteed repair even after all passive observations; most worlds do not.
Both contexts usually matter, but no mandatory mental revision or empirical model
failure rate follows. Preserve those negative findings when extending the family.
