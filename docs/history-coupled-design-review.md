# Fresh design review: history-coupled-v1

Review date: 2026-10-18. Read-only review of `docs/history-coupled-design-draft.md`, the revised independent oracle in `tools/history_oracle.py`, AGENTS.md, scientific runtime/inference/mission contracts, engine finish handling, and terminal decision diagnostics. Repository was not modified. Scratch computations are in `history-review/` alongside this report.

## Decision

The revised finite dynamics are feasible as an explicitly experimental history-dependent family. The initial draft is not feasible, and the stronger claim that both intervention channels are necessary for guaranteed escape does **not** hold under the existing repeatable finish contract. Preserve the narrow evidence-only claim and test the ordinary finish-feedback shortcut as a first-class baseline. Do not claim certified deep/adaptive reasoning or likely Astra failure from the current proof.

## Findings ordered by importance

### 1. Original equations make one quarter of the prior impossible

The original A/B increments vanish at `(h,k)=(2,2)`. That point is fixed under both reversible shears and unreachable from zero. Orientation `(a,b)=(2,1)` requires this state, so 256/1024 worlds are impossible even without the eight-pulse bound. Filtering just those orientations would compromise the paired indistinguishability argument. The revised oracle's everywhere-nonzero conditional quadratic increments fix this: all 81 states are reachable under every normalized law.

The revised equations I reviewed are:

- Each gate has coefficient `c∈{1,2}` and shift `s∈{0,1}`.
- Its increment is `c*(1+(input+s)^2) mod 3`, with inputs `(k,h,h+k,k+x)` for A/B/C/D respectively.
- C first updates x, then updates k by **new x**.
- D first updates y, then updates h by **new y**.

The update order matters and must be disclosed exactly. Each complete operation remains invertible; reversibility does not imply a particular specimen can be repaired within its remaining pulse allowance.

### 2. Repeatable finish completely bypasses intervention necessity

I independently searched `(physical normalized state, set of already visited orientation targets)` for every normalized law. For **all 256 laws**, one path of at most eight pulses visits all four orientation-specific goal states with x=1,y=2. Minimum cover lengths are:

| Pulses to visit all four targets | Normalized laws |
|---:|---:|
| 5 | 32 |
| 6 | 106 |
| 7 | 92 |
| 8 | 26 |

Once the normalized law is known, a player can follow this path and call finish at each of its four eligible target states. This guarantees success using at most four finish calls, **without either physical-clamp intervention and without replacing the seal**. The engine currently permits failed finish followed by further action. Every rejection is valid additional evidence.

This is a constructive bypass, not a theoretical low-probability guess. It is also a legitimate strategy under the public contract. The intervention claim must therefore say “no guaranteed winning preparation from passive evidence alone, before goal-test feedback.” Do not shorten this to “interventions required to win.” If the product requirement is genuinely mandatory intervention information even allowing finish feedback, the revised family fails that gate and should remain a PoC; changing submission semantics needs an explicit public contract and separate tests.

At minimum, the qualification output should contain this counterexample baseline, including full action costs and final success classification. A model that uses rejected finishes is not necessarily reasoning badly.

### 3. Strong physical-stage depth claims are unsupported

Exact shortest goal depths over all 1024 revised worlds are:

| Pulses | Worlds |
|---:|---:|
| 2 | 128 |
| 3 | 280 |
| 4 | 483 |
| 5 | 131 |
| 6 | 2 |

A and B are **each individually omittable in every world within eight pulses**. C/D are necessary because x/y begin zero and only their respective operations change them. C and D alone solve 608/1024 worlds within eight pulses. Thus no world proves four required transformation stages under this family.

Only two worlds have depth six: law IDs 7 and 11 in the oracle order, both orientation (1,1), and both share the witness A,A,B,D,B,C. Selecting only the deepest instances would dramatically narrow mechanism coverage. Include varied depth-four/five cases and report known-law shortest physical depth separately from information depth.

### 4. The normalization argument is sound only for physical-coordinate interventions

With normalized h=aH, k=bK, all ordinary histories are orientation-independent from zero. Setting physical H=1 means setting normalized h=a; setting physical K=1 means normalized k=b. This preserves the intended paired indistinguishability: H-only queries cannot reveal b, K-only queries cannot reveal a, while the four orientation targets are disjoint.

If the implementation instead clamps normalized h or k to a public value, it reveals no orientation and the goal can become unidentifiable except through finish. The public law document should show the coordinate relation and physical goal explicitly. Avoid suggesting that the two coordinate systems are two independently controllable state spaces.

### 5. Common fresh procedures and feasible current repairs are different

Existing terminal metrics call `common_decisions()` without committed-state context. For this family, that can naturally mean winning words from a fresh zero specimen. It must not be silently described as a repair still available for the current seal: a committed wrong history can exhaust the eight-pulse bound even after the law is fully identified.

Minimal strengthening:

1. Define the decision identity as the complete committed history, not the last pulse or cached reading.
2. Track actual key location and committed history; ignore counterfactual probe histories for the attempted decision.
3. Expose a separate terminal field for existence/shortest length of a winning **suffix** from the current specimen within the remaining pulse allowance.
4. State whether a fresh replacement seal is legal. If it is, distinguish replacement feasibility/cost from continuation feasibility.
5. Keep a supported scientific inference win separate from an operationally stranded key.

`AppliedTreatmentTracker` is unsuitable unchanged because it hard-codes seal/doses. A small family-specific tracker is preferable to broad engine restructuring.

### 6. All public outputs are evidence

Committed A/B/C/D results contain public x/y, as do pulse probes. Include every such result in posterior updates, even when no reader action occurs. A failed eligible finish removes all worlds accepting that exact committed history; an ineligible finish due to wrong room or missing key removes none.

The reader's temporary C,D execution must have separate readout fields. It must never overwrite the specimen's committed x/y/history. Reader `operate` may cache a reading, but does not apply those dynamics. Pulse `probe` returns a counterfactual successor but does not change the key or its pulse allowance. Invalid over-length pulses must leave both key and budget unchanged.

Clarify whether a reader's two virtual operations count against the eight-pulse **specimen preparation** bound. My interpretation is that they are reader internals, so a length-eight specimen remains readable. This should be explicit to avoid an accidental hidden measurement exclusion.

### 7. Bounded inference is feasible, but adaptive depth is not demonstrated

Using every committed public output and both intervention results for histories of length at most three distinguishes 1020/1024 revised worlds (four pairs remain). A simple fixed panel of nine queries with histories no longer than four distinguishes all 1024 worlds. This is a constructive upper bound, not an optimal policy or a lower bound.

One such panel, with operation IDs A=0,B=1,C=2,D=3, is:

- H clamp after B,D,C,B
- K clamp after A,C,B,D
- H clamp after C,A,C,B
- K clamp after A,A,C,A
- H clamp after B,A,A,C
- H clamp after B,B,A,C
- H clamp after A,B,D,B
- ordinary x/y after A,A,B,C
- H clamp after A,B

Committed preparation observations can only help this panel. The two nine-valued readers are relatively high-bandwidth. A long physical witness or a need for both channel names does not establish many adaptive research rounds.

Best blind single-word acceptance over all words of length at most eight is 96/1024 (9.375% under the uniform full prior). Recompute any blind-success figure conditional on actual matrix qualification; a filtered deep-world prior can change it.

For the joint-consistency qualification, prefer a reachable posterior where **unique** marginal parameter modes combine into an observation-inconsistent complete world, or a concrete failure of a defined marginal solver. A mismatch produced only by arbitrary tie-breaking would be weak evidence for the intended challenge.

## Minimal implementation gate checklist

- Commit an independent oracle result identifying the original failure and revised all-world reachability.
- Check compiled tables against scalar equations on every world/state/operation, including update order.
- Prove physical-clamp semantics and orientation indistinguishability, explicitly excluding goal-test feedback from that theorem.
- Include the four-finish, zero-intervention constructive baseline; report its cost.
- Check omitted-mode and reversed-word alternatives per selected instance; do not require nonexistent all-four-mode necessity.
- Qualify current-key suffix viability separately from existence of a fresh winning word.
- Prove posterior updates use pulse probes, committed x/y, interventions, and eligible failed finishes.
- Verify reader/probe immutability, invalid-action transactionality, deterministic replay, and no private-state payload leakage.
- Keep the known-law operational control and a generous-budget control. Preserve existing families and metrics schemas through additive capabilities or family-specific fields.

## Source and reproducibility

All numerical results above come from independent scratch scripts using the revised scalar oracle as the dynamics definition; reachability, omission, word coverage, fixed-panel partitioning, and blind-word calculations were separately implemented. Scripts: `history-review/check.py`, `revised.py`, `revised_identify.py`, `revised_blind.py`, and `finish_shortcut.py`. The original-equation checks are fully independent of the repository oracle.

## Final design adjudication

I additionally read the subsequently created `docs/history-coupled-design.md` and implementation ledger. These address the main review findings appropriately for an experimental rollout:

- The failed original gates are replaced and the impossibility is recorded.
- The guarantee is narrowed to a guaranteed **first submission**, before rejected goal-test feedback.
- Ordinary charged anneal is available at every resource profile, making a fresh preparation physically available without changing the hidden law or resetting the investigation.
- The design explicitly avoids a universal deep-reasoning or mandatory adaptive-round claim.

Proceed on that bounded scope. Preserve the explicit four-finish shortcut and omitted-mode statistics in the final qualification report/matrix rationale rather than losing them behind the shortened first-submission theorem.

One final diagnostic caution: committed key construction pulses are legitimate evidence events but may be operationally necessary after scientific uncertainty is already resolved. Counting them under shared `redundant_measurements` / `measurements_after_guaranteed_repair` is mathematically consistent only if the new family clearly defines those fields as evidence-event counts. They must not be interpreted as wasted scientific experiments. A terminal breakdown of reader observations, counterfactual pulse probes, and committed construction pulses is sufficient; no broad metrics rewrite is required.
