# Joint assembly PoC design

Status: implemented and independently checked. Base `139f3bedefa6c5f6af54e101eab0bf68411d6cee`,
branch `feat/theory-prior-axis`. Previous families and their seeded behavior stay intact.

## Purpose and scope

Test whether joint inference plus globally compatible physical construction is more
informative than independent staged calibration. A player confined to an artificial
workshop must prepare two components and assemble a phase compensator for the exit.
Local validity allows several phases; the assembled device must satisfy the complete
operating envelope. No travel maze, fatal activation, external interpreter, mandatory
experiment ordering, or new core action types are needed for this first experiment.

## Proven bounded design

Arithmetic is modulo 3. Hidden laws are U(x)=s*x+a and V(y)=t*y+b, with s,t in
{1,2}, a,b in {0,1,2}; shared reader bias r in {0,1,2}. The joint law is one of
u+v, u-v, u*v, u*u+v. All 432 combinations are admitted, with no hidden difficulty
filter. D4 local readings are U(x)+r and V(y)-r; joint readings are H(U(x),V(y))+r.
D3 is a matched calibrated-reader control with the same physical laws and goal.
T3 withholds the joint operator; T2 supplies its shape; T0/D0 supplies the exact law.

The workpiece contains two prepared slots. Each slot has a slope and a phase.
Its local functional contract fixes slope but permits all three phases. An assembled
device must satisfy both component slope contracts and match H(U(x),V(y)) at all
nine x,y pairs. Behaviorally equivalent complete builds remain valid.

Preparing one slot sets its slope/phase and rotates the existing other slot's phase
by the new phase. This public deterministic mounting interaction is persistent:
repairing one component may invalidate the assembled response while preserving both
local contracts. Probes preview without committing; configure only sets apparatus.
All builds remain reachable, recovery is legal, and finish reports only binary
success/rejection. Materials and apparatus are reusable; R1 limits actions, not retries
through an arbitrary stock trap. Finite stock and fatal activation are later ablations.

## Qualification contract

Qualify the complete accepted build, never parameter identity or local checks alone.
Enumerate all public-prior worlds, all legal observation classes and all complete
builds. Include reader copies, preparation previews, errors, state projections and
eligible/ineligible finish feedback in a written live-to-finite conformance argument.
Track actual committed component state separately from the law posterior.

Proof outputs must distinguish:

- whole-local-sweep closure versus a guaranteed final build;
- exact actual-outcome certificates (oracle experiment choice, not an agent policy);
- adaptive constructive public-policy cost and exact replay;
- uniform-prior feedback success bounds including rejected/successful finishes;
- actual selected-seed facts versus prior averages;
- mathematical qualification versus unmeasured LLM difficulty.

Hard rows must have unresolved full-local closure, nontrivial minimum evidence for
a complete build, different operator/phase profiles and a public solution within
budget. T2 known-sum cancellation and disclosed-law episodes remain labelled controls. T3 sum/difference episodes are harder than the nonlinear cases in this bounded grammar: all three channels are needed and exact certificates require five readings.
No claim of unavoidable deep cognition follows from these finite facts.

## Architecture and performance

Implement as trusted built-in `joint-assembly-v1` through existing catalog/payload
registration. Keep schema, laws, finite tables, belief, runtime, evidence, policy,
qualification and offline proof separate. No family branch in engine/session/replay.
Immutable prior-wide response/acceptance tables are cached and bitsets update beliefs.
Generation performs direct seed selection, not expensive per-episode minimax search.
Exact certificate search is offline, bounded and fail-closed. Generalize only a proved
reusable inference/qualification primitive; avoid a speculative crafting framework.

## Decisions and invalidation triggers

- Joint biased channels instead of an independent reference calibration: local
  observations provably leave mission-relevant uncertainty. Invalidate if full local
  closure or a one-shot joint reading resolves every selected hard row.
- Public cross-slot preparation effects instead of additional secret dynamic state:
  isolates joint inference while testing forward planning and repair. Hidden dynamic
  state would require a larger world/state policy proof and is explicitly deferred.
- Full operating envelope plus explicit local contracts: physical validity is exact,
  and cosmetic parameter identity is never required. Review whether a local contract
  is redundant and disclose its role precisely.
- Reusable workshop and recoverable activation first: failure should diagnose reasoning,
  not an undisclosed irreversible trap. Matched risk variants can follow measured pilots.
