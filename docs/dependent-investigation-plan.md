# Selective experiments and dependent discovery

## Intent and scope

Approved 10 October 2026: implement recommendation 3 from the latest run audit.
The existing 12-coordinate coupled family is at an accuracy ceiling without
external Python. Add an opt-in `resonant-network-v1` family; preserve both existing
families, axes meanings, moderate P/R, strict validation and terminal receipts.
No paid model calls, external-compute tool, MindTrial edits, or main merge.

## System design

An artificial resonance relation H(x,y) determines the setting z at which a
specimen produces a downstream response G(x,y). A calibration instrument reads
H directly on bench specimens. The response meter returns G when z=H, otherwise
the public `signal:false` with an absent/null reading. Off-resonance experiments are legal, consume
normal actions, and constrain H; they do not reveal G. There is no stage unlock
or required experiment order. Players may infer, search, interleave, or guess.

H is independently chosen from alpha*x+beta*y, alpha*x^2+beta*y,
alpha*x+beta*y^2 (mod7), alpha,beta in1..3. G retains the composed 2,187-world
network prior. Every Cartesian-product combination is admitted. The bench is
all45 GF7 coordinates outside the four field targets. Controller settings are
five values: port0 followed by H+G modulo7 at those held-out targets. A discovered H is an
instrumental theory used to obtain evidence for G; G then predicts new contexts.

D4 supplies prepared bench stocks; D5 supplies the origin and requires the
existing noncommuting shift/shear preparations. T3 withholds both bounded
relations. Initial live scope is D4/D5/T3 plus D0/T0,T3 controls, P0..3/R0..2.
Additional T levels require separate semantic qualification, not relabeling.

Use ordinary `configure meter settings:[z]`, observable instrument settings and
probe/operate. Configuration gives no signal/correctness feedback. It consumes
one action, like controller configuration. Document the per-family contract.

## Proof and performance invariants

- Reuse the exact 12-coordinate downstream policy as a **subset witness**, not
  a claim of global minimax optimality over the expanded experiment domain.
- Prove upstream calibration identification; compose public posterior policies.
- Maintain an exact factorized scientific posterior: a successful meter response restricts
  H by equality and G by reading; no-signal restricts only H. No flat Cartesian
  enumeration/minimax required. Wrong controller submissions exclude complete
  joint H+G vectors; preserve these exclusions separately rather than falsely
  treating the posterior as a product after controller feedback.
- Prove a realizable action bound uniformly over all admitted factor outcomes;
  budgets keep the existing R1 +8 / R2 +0 policy, R0 unlimited.
- Prove complete sweeps cannot fit moderate P1/R1, while the witness can.
- Show omitted upstream inference can still be replaced by legal search; do not
  claim calibration is mechanically mandatory or that players must identify H.
- Preserve deterministic replay, invalid-action atomicity, clear public prior,
  unmeasurable field targets and terminal-only diagnostics.

## Implementation stages and acceptance

1. Mathematical PoC: independent arithmetic, calibration policy, ambiguity and
   sweep bounds. Record proof results and falsification limits before runtime.
2. Integrate typed family specification/truth, apparatus settings, runtime,
   generator, evidence, posterior telemetry and qualifier. Cache immutable prior
   tables and factor witnesses; avoid generation over the 59,049-world product.
3. Regression and tamper tests, exact factorization versus explicit small/product
   oracles, physical reference replay, CLI/server smoke, fixed-seed benchmark.
4. Publish focused commits to existing feature branch/PR with expected-head lease;
   provide paired ten-run matrix and final checkpoint. No force-push.

## Checkpoint

Baseline local af6785e; remote d130f3af406c7a332fe7c92c32037da0ac71aaf6;
matching tree66a61c8f38bbe78a66e366c9a7a3edb854402241. PR6,
feat/theory-prior-axis -> feat/epistemic-calibration. Workspace initially clean.
Stage1 proof passed for 27 x2187 worlds and45coordinates. Review found a two-probe
full-domain calibration witness, (0,6),(6,0), and expanded-domain fitting shortcuts.
Use the improved calibration witness; retain fitting as valid scientific reasoning.
H+G field targets replace G-only targets to ensure both discoveries matter.
Risks: calibration may be a trivial detour; expanded domain
may admit easy shortcuts; factorization only holds under disclosed outcome
semantics. Real-model difficulty improvement remains empirical.
