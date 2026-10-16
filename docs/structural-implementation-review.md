# Independent compositional implementation judgement

Reviewed 2026-10-16 against the working tree of `nexus-theory` on `feat/theory-prior-axis`, baseline `09fe7bb`. Read-only repository review; no paid services, external requests, or subagents. Applied the Short Circuit fresh-context judgement workflow. Repository work continued during review, so the follow-up items below distinguish findings from fixes reported by the implementation owner.

## Verdict

No blocking gameplay-correctness or privacy defect found in the reviewed compositional implementation. It implements the approved experimental family with overlapping accepted repairs, a complete admitted T3 prior, ordinary physical preparation, binary eligible finish feedback, terminal-only diagnostics, and a constructive public witness. This is qualified as a bounded structural PoC, not proof of mental revision, an information-round lower bound, or empirical model difficulty.

## Evidence independently checked

- Read `AGENTS.md`, structural design/proof/implementation documents; all compositional modules; decision audit; mission tracking; metrics/session types; relevant domain/action/episode schemas; engine, renderer, receipt and replay paths; new unit and HTTP integration tests.
- Independently enumerated all 1,728 raw grammar worlds and all 81 repairs with separate arithmetic. The exact admitted list and repair bitmasks match production: 615 worlds. This checks rejected raw worlds too, beyond merely rechecking the already-admitted list.
- Checked there is no context change that is observationally inert over the complete input/internal-trim domain in any admitted world. Topologies have counts 241/194/180; changed modules 194/205/216; largest repair acceptance mass is 41.
- Ran `.venv/bin/python -m pytest -q tests/unit/test_compositional.py tests/integration/test_compositional_service.py -m 'not slow'`: **15 passed, 3 deselected** in 1.31 seconds.
- Independently exercised applied-correct-but-dropped seal rejection followed by retake and success; offset sensor **operate** following an eligible wrong repair; unknown-machine atomicity; v2 response JSON roundtrip; and exact replay. All passed. Reproducible script: `analysis/structural-next/compositional-review-edge-checks.py` in the workspace parent.
- The implementation owner reports that the three new slow tests passed in 33 seconds, including all-world live witness/replay. I did not independently duplicate that exhaustive live run.

## Core findings

1. **Support and overlapping acceptance are sound.** Population includes every solvable raw world, retains equivalent-world mass, and selects by seed modulo 615 without rejection filtering. Victory calls `accepted`, not equality to `expected`. `DecisionAudit.common` correctly tests whether one repair accepts every remaining world. Distinct repair-set signatures are not incorrectly treated as exclusive targets for policy stopping.
2. **The public-response reduction is supported by the code.** Survey sensor operate/probe reveals one scalar for its public preparation. Offsets normalize by a known response-label bijection. Stage and doser previews return public preparations/treatments; unsupported material combinations are public-state no-ops. Sensor on seal has no reading. Only finish acceptance depends on truth outside sensor reading. Movement, take/drop, waiting, apparatus settings, stock IDs, resources, and invalid-request conditions are public-state dependent. Repeated observations can repeat known readings but add no unmodeled truth information. Exhaustion/finalization telemetry is terminal and cannot be used to continue the same attempt.
3. **The physical witness bound matches actions.** T3/P1 takes seal and reusable survey, moves once, uses configure/operate/probe per query, and configure/operate/finish for repair: `6 + 3q <= 27` for `q <= 7`; budget 30. T0/P1 takes 5 actions. The three-action allowance permits an extra configure/apply/finish attempt, but should not be described as a guarantee for every arbitrary recovery heuristic.
4. **Eligibility tracking is correct in tested edge traces.** An unapplied preview does not create a treatment. A dropped seal or wrong room makes a finish ineligible and must not falsify that repair. The existing `AppliedTreatmentTracker` follows committed payloads and physical location. An eligible wrong repair excludes its whole winning mask rather than one canonical answer.
5. **Privacy boundaries are appropriate.** Selected truth/seed, candidate counts, winning recommendations, and certificate stay out of active player responses. Terminal v2 diagnostics preserve their fields through `ActionResponse` serialization. Private episode validation checks truth/seed, evidence, resources, topology, mission, and core certificate fields.

## Actionable precision items

### A. Scope probability claims to a distribution

The exact query/guess maxima are uniform **world-index prior** results. Production mapping is `seed % 615`, which preserves full support but is uniform only under an explicitly appropriate seed distribution. A targeted pilot is not uniform. The implementation owner agreed to state the scope as uniform selection of an index/seed in 0..614 and keep targeted fixtures separate. This is documentation/interpretation, not a gameplay defect.

### B. Distinguish signature reduction from decision resolution

`target_reducing_measurements` currently means a reduction in distinct winning-set signatures. That can occur after a common guaranteed repair already exists and is not the same as gaining a guaranteed decision. The v2 type already carries `target_count_meaning`; add an equally explicit field description and, if useful, a separate count of measurement transitions from no common repair to at least one. A rejection-caused transition should not increment a measurement count. The owner has agreed to this and to regenerate the new v2 JSON schema.

### C. T0 belief is conservative, not the exact generator conditional prior

Generation exposes the lexicographically first accepted repair for T0. `Belief(T0)` includes all worlds accepting that repair, including worlds whose first accepted repair differs and therefore could not emit that T0 evidence under the actual generation algorithm. For disclosed repair `(2,1,2,1)`, production emits it for 2 worlds while belief includes 31 accepting worlds. This does not affect the control witness, T3 prior, victory, or common-repair guarantee. It affects interpretation of T0 `prior_worlds`, signature counts, and measurement gain. Either condition T0 belief on the canonical disclosure algorithm or explicitly call it conservative valid-repair evidence rather than an exact sampler posterior. This is a nonblocking precision limitation if documented.

## Focused tests worth retaining

- Promote the independent dropped-correct-seal / retake / success trace; it protects against accidentally excluding a valid treatment after an ineligible finish.
- Add wrong-room rejection with a previously applied correct treatment and subsequent successful return, for the other eligibility branch.
- Exercise both sensor `operate` and `probe` with nonzero c/d and verify their normalized posterior masks agree, while only operate persists the reading.
- Assert an eligible rejected repair removes exactly its full winning mask from an unresolved prior, including worlds with other accepted repairs.
- Check stage preview leaves settings/readings unchanged on the specimen, re-preparation clears a persisted reading, and doser preview never changes seal doses.
- Check first resolution measurement count and subsequent signature-reducing confirmations separately once the v2 metric is added.
- Bind the v2 JSON schema to `DecisionMissionPerformance.model_json_schema()` in the existing schema-check convention.

These are targeted guards for stated invariants, not a request for another unbounded all-world matrix. The existing exhaustive arithmetic and live witness gates are the appropriate broad checks.

## Remaining claim limits

- Only 12 worlds exhibit the complete-untrimmed observation obstruction. Do not imply every admitted world needs an internal intervention.
- A player may reason jointly from the beginning or start with context 1; mental revision is not enforceable.
- A query/guess ceiling that relaxes preparation costs is not a physical-action optimality certificate.
- T0 and dynamics controls support execution and family comparisons; they do not isolate the causal contribution of local mechanism replacement from every other compositional difference. That would need additional matched controls and later model data.
- The standalone all-world query proof, live tests, and new runtime do not establish any model failure rate. Experimental/uncalibrated labeling remains necessary.

## Final disposition after implementation-owner fixes

Re-inspected the updated source and tests after the owner addressed the review findings:

- **A resolved:** `docs/structural-model-matrix.md` now explicitly states seed modulo 615, uniform index sampling on 0..614, and that query ceilings do not describe the targeted pilot's empirical fraction.
- **B resolved:** v2 gives `target_reducing_measurements` an explicit signature-count description and adds `measurements_establishing_guaranteed_repair` for measurement-driven empty-to-nonempty common-repair transitions. Rejection-only resolution is excluded. Independently compared the generated v2 JSON schema with `DecisionMissionPerformance.model_json_schema()`; they match exactly.
- **C resolved:** public T0 evidence now discloses the canonical lexicographically first accepted repair rule; T0 belief filters exactly on that disclosure algorithm. Added regression checks its conditional support. T3 remains unchanged.
- The dropped-seal eligibility trace, offset sensor-operate/rejected-repair posterior oracle, and T0 posterior check were promoted into repository tests. Independently reran the final focused suite: **18 passed, 3 deselected** in 1.78 seconds. Reran the standalone edge-check script against the updated tree: passed.
- Owner reports wider gates passed (34 release checks, all compositional slow checks, old dynamics all-world replay, and repair live/replay checks). Those broader results remain owner-provided evidence, not tests independently repeated by this reviewer.

**Final recommendation: no unresolved blocker from this review.** Preserve the experimental/uncalibrated scope and the stated claim limits. Additional focused tests listed above are suggestions only unless an existing release gate requires them; they should not delay completion after the mandatory gates pass.
