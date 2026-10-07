# Theory-prior axis (T) — execution plan

Scope decision

Production work is approved for shared theory-prior infrastructure, T0 backward compatibility, and T1 derivational/structural theory. T2 is a separate gated PoC after T1 is stable. T3/T4 are blocked pending a symbolic-belief proof.

1. Branching

Implementation authorized 2026-10-07. Work on feat/theory-prior-axis from integration commit cd69107f02af30c10464b85b47fa343a3f96aaef; preserve historical PoC design separately. OCI revision labeling is already on the integration branch.

2. Commit 1 — T0 compatibility and minimal theory contract

Tests first: omitted theory level equals T0; seeded T0 preserves hidden laws, evidence, topology, goal, public description, physical optimum and exact guaranteed-policy cost; current facility manual remains stable; theory metadata stays private.

Implementation: add theory_level defaulting to 0, CLI/service option, and the smallest immutable internal theory-prior representation needed by T0/T1. Do not add speculative T2-T5 fields.

3. Commit 2 — T1 finite hypothesis universe

Implement the approved T1 grammar: 18 current shape/phase condition forms; each true/false branch independently chooses one of six value operations, optional polarity toggle, and rotation 0/1/2/3. Raw syntax count is 41,472.

Canonicalize on the complete declared domain of 528 shape × phase-parity × value × orientation × polarity contexts. PoC result is 27,120 distinct behaviors and all 288 T0 rules are distinct members.

Use compact behavior signatures and integer hypothesis IDs. Do not materialize tens of thousands of Pydantic Effect objects. Materialize representative ASTs only for evidence-conditioned survivors entering the exact solver.

Proof tests: exact syntax and behavior counts, deterministic canonicalization, exhaustive behavior equality of representatives, T0 subset membership, and no dependence on fields declared non-causal.

4. Commit 3 — T-aware evidence planning for D0-D3

Refactor evidence planning so the theory prior supplies the candidate universe. D semantics remain unchanged but are evaluated after conditioning on the selected T prior.

D0: direct context plus unique mission behavior. D1: no direct context, one mission prediction, zero minimum guaranteed probes. D2: no direct context, multiple mission predictions, exactly one minimum guaranteed probe. D3: both stages meet their guarantees while the joint correlated hypothesis product stays below the exact solver limit.

Reject unsuitable causal families rather than weakening guarantees. Record rejection rates to detect bias toward a tiny subset of laws.

Pairing: fixed seed and D/P/R should preserve selected true law, intrinsic artifacts, goal and topology across T0/T1. Evidence may differ because it is normalized to D under each public prior.

5. Commit 4 — public T1 theory and protocol

Generate the T1 facility manual from the same structured prior used to construct the evaluator hypothesis class. Disclose determinism/stationarity/memorylessness, causal variables, condition primitives and structural bound, primitive branch effects, and preserved fields. Do not disclose current T0 macro templates or private candidate counts.

Add --theory-level and NEXUS_THEORY_LEVEL. Add leakage tests comparing paired T0/T1 public packages.

6. Commit 5 — D4/D5 integration and validation

Enable T1+D4 only after exact policy tests prove the auxiliary experiment remains optimal and the distractor remains dominated under the broader T1 prior.

D5 is a separate proof gate because its current four-member mission family is specialized. Either generalize its public prior honestly or leave T1/D5 unsupported initially. Never hide the D5 manual while secretly optimizing against the undisclosed four hypotheses.

7. T2 PoC — effective theory with bounded correction

After T1 is green, define one small family with true law F, public effective law E, validity region V, and bounded correction C active only outside V. Prove exhaustively that E equals F throughout V, evidence lies in V, the mission reaches outside V, multiple corrections disagree there, and an affordable exact experiment policy resolves enough uncertainty.

Only after candidate sizes and solver runtime are acceptable should T2 receive a production plan.

8. T3/T4 future gate

Do not enumerate all deterministic functions and do not reuse the private DSL as an undisclosed solver prior. Prototype symbolic context uncertainty on tiny domains, where an unobserved context has an unconstrained output and an observation fixes it permanently. The symbolic solver must exactly match explicit enumeration before T3/T4 can proceed.

9. CI and performance

Do not run Actions on every edit. First paid run: T-prior proof tests, T0 regression, T1 D0-D3. Second paid run only after green: fast suite, extended theory tests, three-seed T-aware stress, CLI/service smoke. Five-seed validation only for a release candidate.

10. Stop conditions

Stop rather than weaken guarantees if T1 candidate products routinely exceed exact solver limits, D1 generation acceptance becomes very low or biased, D4/D5 need hidden private assumptions, public theory cannot be mechanically tied to solver semantics, R2 needs a stronger prior than disclosed, or T2/T3 symbolic proofs fail.

11. First-release completion criteria

T0 is backward compatible; T1 has one formal public prior and exact evaluator class; every supported T1×D profile retains its D guarantee; exact guaranteed-policy cost is theory-relative; R2 is fair; paired generation is verified; public/private leakage tests pass; generation acceptance/runtime are measured; replay, CLI, service and schema behavior remain green.

T2+ are not prerequisites for the first T release.
