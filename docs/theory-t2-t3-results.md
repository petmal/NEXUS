# T2 runtime and T3 feasibility results

T2 is integrated on `feat/theory-prior-axis` (PR #6). T3 is a research PoC only.
The existing T0/T1 generation path, action semantics, scoring and terminal secrecy
are preserved. Runtime checkpoint: `86e6bb6ee4bb7fdc8b9801ad704cc5340e5139b0`.

## Runtime support and use

| Theory | Discovery | Planning / resources | Interpretation |
|---|---|---|---|
| T0 | D0–D5 | P0–P3 / R0–R2 | Existing catalogue prior |
| T1 | D0–D4 | P0–P3 / R0–R2, subject to seed qualification | Structural primitives; paired T0 worlds |
| T2 | D2 only | P0–P3 / R0–R2 | Effective model with bounded corrections; separate world family |
| T3 | Research only | Single-artifact bounded fixture | Independent context-cell prior; no runtime setting |

For an initial MindTrial task:

```yaml
NEXUS_SEED: "17"
NEXUS_DISCOVERY_LEVEL: "2"
NEXUS_PLANNING_LEVEL: "2"
NEXUS_RESOURCE_PRESSURE: "1"
NEXUS_THEORY_LEVEL: "2"
NEXUS_GENERATION_TIMING: "true"
```

Build this branch with `--build-arg VCS_REF=$(git rev-parse HEAD)` to retain the OCI
revision. T2 with other D settings rejects explicitly; T3 is also rejected. A loaded
private episode retains its compiled profile rather than using generation overrides.

T2 publishes the effective additive model and its exact validity region (phases
0 and 2), with independent additive corrections from {0,1,2} at phases 1 and 3.
All nine laws are reconstructed from the same public prior used to render JSON
and prose. The mission requires a correction, making the effective model alone
insufficient. The public solvability promise leaves five viable laws; one informed
probe guarantees a successful policy. A player may still guess. Qualification
checks public-prior identity, calibration, true-law membership, mission uncertainty,
physical solvability, exact policy cost, budget, P3 dependency and engine replay.

T2 is not a physically paired variant of T0/T1, nor a promise of higher model
failure rates. The initial task family tests recognition of model limits and
correction discovery, not selection among informative auxiliary specimens. T0/T1
physical-pairing tests and pre-theory T0 compiled-world hashes still pass.

## T3 PoC and measured effect

Run `uv run python scripts/theory_structure_poc.py`. It writes fingerprinted,
atomic per-seed reports and resumes matching successful cases. Each case runs in
a fresh subprocess with a 120-second timeout; no runtime limits are raised.

The public T3 family has six independent shape × parity cells, each choosing one
of three additive effects: **729 complete laws**. One truthful calibration leaves
**243 laws**. The fixture has one artifact whose shape cannot change, so only two
cells are reachable through any future legal action. The factorized representation
therefore has **nine reachable behavior classes**, each representing **27 complete
laws**. This is an exact quotient, not a truncated or sampled hypothesis set.

For all five seeds (0, 1, 2, 17, 2525):

- complete enumeration and factorization produced the same exact policy cost;
- 135 viable complete laws per seed were covered by the factored witness;
- all **675 full-law policy replays** won through ordinary engine actions;
- **53,460 reachable value/phase comparisons** matched class representatives;
- the minimum guaranteed probe count remained one.

In the final isolated fresh-process pass, median projection-plus-solve time was
**0.083 seconds**, versus **1.944 seconds** for complete enumeration, evidence
filtering and solve. These timings measure this bounded PoC, not a production
solver speedup; the two paths perform different representation work. They show
that irrelevant independent contexts need not multiply the mission search.

The proof does not cover multiple reachable artifact shapes, shape-changing laws,
multiple interacting machines, or correlations between cells. The projector
rejects a second artifact. Production T3 requires a broader proof and worthwhile
model discrimination; it is not enabled merely because this small fixture is fast.

## Generation diagnostics

`NEXUS_GENERATION_TIMING=true` now ends each generation with one
`event=generation_summary` JSON line containing total wall/process-CPU time and
qualified nested stage paths, counts, error counts and inclusive times. Repeated
solver phases are retained and distinguished by enclosing core/theory/P3/qualification
stages. The summary survives a last-50-lines capture even when earlier core records
are omitted. Error summaries omit exception details and reset their collection state.

Additional timings cover catalogue construction, its experiment signature matrix,
mechanics/evidence family search, T1 universe construction, and T2 family, topology,
physical and policy work. Nothing is added to the player observation or compiled
world. Nested durations must not be summed into a new total; process CPU time is
not host utilization or a decomposition of concurrent worker CPU.

The new cold D3/P2/R1/seed-1 controls demonstrate the added attribution: T0
spent 2.254 seconds in mechanics/evidence search out of 3.925 seconds total,
including 0.402 seconds in the signature matrix; catalogue construction itself
was only 0.014 seconds. T1's universe build was 0.040 seconds in its separate
9.391-second sample. These are single local diagnostic samples, not a controlled
regression or a measurement of the user's concurrent MindTrial host.

Terminal payloads now reference immutable **performance-v5** (theory levels 0–2),
at schema commit `c24f44f510df32453c6e2860ef86640ab3ac6f8e`. Prior schemas remain
unchanged. Existing scoring and validation-on-error behavior is untouched.

## Validation and next real-model pass

- Full suite: **206 passed**, 445.05 seconds, three stress seeds. Two pre-existing
  Pydantic warnings in the legacy generic SET-normalization test.
- A subsequent eight-test targeted run includes the newly added runtime-T3
  rejection case; **all 207 current tests are covered**.
- T2 P2/R2: all twelve seeds (0–9, 17, 2525) accepted. Three seeds each at P0,
  P1 and P3/R2 also accepted: **21 cases, 105 viable-law replays**. Unit tests
  additionally exercise all twelve P/R combinations and qualification tampering.
- Those fresh-process generation measurements ranged from 0.119 to 1.132 seconds
  (median 0.148 seconds); broader tests were running concurrently. They exclude
  container/service readiness overhead and are not a controlled comparison with T1.
- Ten-cell model matrix preflight: all accepted, **123 viable policy replays**.
- CLI T2/D2/P3/R2 seed 17: generate, qualify, solve and replay all passed.
- Lock verification, byte compilation, diff checks and an independent read-only
  correctness/secrecy review passed. The immutable remote schema was read back.
- No paid model calls. No local container build: Docker/Podman are unavailable.
  The existing absence of installed lint/type gates remains a tooling gap; this
  change does not migrate the repository toolchain.

Use [the ten-run matrix](theory-t2-model-matrix.json): four T2/P2/R1 seeds, two
T2/P2/R2 cases, two T2/P3/R1 cases, and two established D3/T1 controls. Difficulty
estimates are qualitative; the controls are not physically paired T2 worlds.
Resolve the provider final-answer contract configuration before comparing official
pass rates, retaining the distinction between parser errors and verified game wins.

Raw evidence: `docs/profiling/t2-integration`, `t3-structural-poc`,
`timing-summary-controls`, and `t2-model-matrix-preflight.json`.
Machine-readable gate summary: [validation record](theory-t2-t3-validation.json).
Resume instructions: [execution checkpoint](theory-t2-t3-plan.md).
