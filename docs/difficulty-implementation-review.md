# Independent difficulty implementation judgement

Reviewed the actual working tree, using the Short Circuit evaluation review discipline. Read-only repository review; only this scratch report was written. No paid calls, repository edits, or delegated agents. Snapshot time: 2026-10-15T01:44:33.504530+00:00.

## Judgement

No blocking algorithmic defect found in the finite-observation certificate or the implemented two-state scientific model. The selected six challenge truths support the stated **at least four positive measurement outcomes under the full disclosed prior** condition. Public policy execution, serialization and replay succeeded independently for each selected challenge. This supports a structurally qualified pilot candidate, not empirically calibrated cognitive difficulty or a full-rollout decision.

The review found an admission reporting defect in the first implementation: malformed matrix input could leave an older `pilot-ready` output untouched. The implementation owner fixed it during this review; a fresh subprocess check confirmed malformed input now returns nonzero and overwrites the prior status with `blocked`. The owner also added saved-report identity/inventory checking and end-of-run source-digest comparison during the review. Final repository gates, service privacy checks, matrix preflight, and the intentionally stale repair release binding remained the implementation owner's release work, not independently completed by this reviewer.

## Evidence independently executed

1. **Exact certificate oracle:** 1,200 deterministic random finite problems; 7,206 per-world comparisons with an independent combinations-and-sets brute-force oracle. Target-equivalent worlds, duplicate readings, non-identifying observations and zero-through-three-reading certificates were included. Every exact minimum, lower bound and returned witness matched.
2. **Scientific arithmetic:** independently implemented routing, simultaneous transitions and response expressions, without calling the production physical evaluator. Checked all legal sensor/reference histories and points for the six selected truths: 56,112 legal queries. Checked all 15,552 mission physical values across the complete 1,944-world prior. All matched. Every reference history/point normalized to its e-only representative exactly.
3. **Complete-query certificates:** production audit contained 4,674 normalized legal queries. All six selected challenge truths returned lower_bound=4 and exact_minimum=None. This proves absence of a certificate using at most three readings, not that four readings always suffice.
4. **Public execution:** generated, serialized/deserialized, then ran the public-information policy on all six challenge truths. Each won, stayed within the declared 65-action public-policy bound, and replayed to the identical canonical state. Actual trajectories used seven measurements and 47–50 actions; action budget 73.
5. **Scope countercheck:** the truth-aware physical plan won each selected challenge in five actions with zero measurements. This deliberately verifies that the certificate condition is an information requirement, not a prohibition on guesses or an unavoidable action count for every successful trace.
6. **Malformed input reporting:** a pre-existing ready report was overwritten with blocked after invalid matrix JSON, and the CLI returned status 1.

| Seed / world index | Untreated-data target classes | Complete ≤1-pulse target classes | Positive-measurement lower bound | Public policy actions |
|---|---:|---:|---:|---:|
| 128 | 6 | 1 | 4 | 47 |
| 839 | 24 | 1 | 4 | 47 |
| 1013 | 24 | 1 | 4 | 50 |
| 649 | 12 | 1 | 4 | 50 |
| 1509 | 6 | 1 | 4 | 50 |
| 219 | 6 | 2 | 4 | 50 |

The first five cases can be resolved from sufficiently many one-pulse experiments. Only the separately labeled history-transfer cell retains ambiguity after receiving every untreated/one-pulse measurement. The implementation's split labels and coverage tests preserve this distinction.

## Certificate reasoning

For fixed true world w, each query contributes the set of target-distinct rival worlds sharing w's actual outcome. A sufficient evidence certificate is exactly a set of queries whose rival sets have empty intersection. Removing target-equivalent worlds is correct: the mission asks for a dose vector, not latent-law identification.

Deduplicating equal rival sets loses no information. Discarding a rival set B when retained A is a subset of B is sound because substituting A for B can only shrink every later intersection. Sorting by cardinality ensures no previously retained strict superset needs retroactive removal. The pair search is exhaustive on these undominated sets. The transpose search marks every candidate third query containing any surviving rival from the pair; its complement consists precisely of third queries excluding all such rivals. A surviving complement supplies a real witness; exhausting all pairs proves there is no three-query certificate. Repeated queries cannot improve an intersection, so considering distinct pairs is sufficient.

The resulting pointwise negative certificate covers every adaptive path of that many positive measurements for that truth: the queries encountered on any resolving path would themselves form a certificate. It does not cover information gained from rejected finish guesses, a lucky correct treatment, hidden access, context carried across cells, or model cognition. The implementation states these exclusions explicitly.

## Scientific runtime and public/private boundary

- Both next-state components are computed from the old h,k. The tabulated execution agrees with an independent sequential-history evaluator using simultaneous per-step updates.
- Sensor results use the post-history state at the current point, then add delta*(e+1); reference results depend only on delta and e. The two reference representatives therefore cover every legal reference history/point. The eight prohibited protocols are excluded only for sensor measurements, as publicly documented.
- All other public operations expose preparation, cached readings, doses, location or resources. Stage/pulse previews expose no hidden components; seal probes expose no reading or residual; configuring a doser does not apply treatment. The generic engine's finish response is a generic rejection until a correct physical submission wins.
- The complete query audit grants arbitrary fresh preparation without physical cost. That relaxation strengthens a negative evidence-resolution result. It does not establish an optimal game policy, feedback-round depth, or cognitive demand.
- The public investigator imports the public finite law grammar, not the selected private world. It uses only player operations and public evidence while choosing queries. Evidence equality is enforced at episode validation, so the code's fixed public grammar cannot silently disagree with an accepted episode's grammar.
- T3 budgets, apparatus, evidence and public settings do not depend on the selected hidden truth. Public episode identifiers are independent random nonces. Hidden state, operator selected-pool indices, selected roles and certificate witnesses are outside player evidence.
- `AppliedTreatmentTracker` follows committed seal doses, not apparatus settings or previews. Drop/take and room eligibility are tracked before failed-finish exclusion. The new adapter hook leaves pre-existing prediction trackers and the repair tracker unchanged.
- Existing trusted registry/payload registration is extended with a fixed family identifier; no player-chosen import path or public truth payload is introduced.

The paired T0 control discloses the same target as one T3 challenge, so the full-prior claim presumes independent player context between cells. Operator matrix/report/seed disclosure also changes the relevant prior. The preflight explicitly measures and warns about selected-pool conditioning; retain these boundaries in rollout instructions.

## Coverage, source binding, and residual limitations

Coverage uses generated truth and target identities, not descriptive labels. It checks all three repair law degrees, no selected zero coupling, six distinct dynamics worlds/mission targets, all transition and response forms, both wirings, the four-measurement gate, untreated ambiguity, both order-sensitivity outcomes, one long-history discriminator, and an exactly paired execution control. The strongest role depends on the full disclosed prior, not the six-case matrix population. Population success mass is explicitly uniform-prior mass, not an empirical rate for this stratified ten-cell matrix.

The updated preflight records semantic matrix and installed package content digests, writes atomic running/blocked reports, compares package identity again at completion, and exposes a saved-report verifier. This is identity checking, not cryptographic proof of report authenticity or a replacement for rerunning qualification. Final source freeze and fresh successful preflight are still required after any edit. The repair manifest is intentionally stale at review time and must be requalified through the existing release gates; this review does not bypass it.

Two nonblocking hardening points were sent to the implementation owner:

- `certificate(max_seconds=...)` now checks finite positive limits and inner-loop progress, but the cached `partitions` property is constructed before its first preprocessing-loop deadline check. The generic accepted dimensions allow 50,000×16,384 input bytes and potentially much larger partition storage. A total outcome-cell cap or streaming/deadline-aware construction would make the general API's resource guarantee stronger. The actual dynamics problem has ~9.1M outcome bytes and completed audit construction in ~6.5 seconds, with all six certificate searches in ~12 seconds total on this environment; this is not a selected-matrix correctness blocker.
- A saved-report completeness verifier should require each row's `qualification.passed is True`, in addition to win, replay and coverage fields, if it is intended to reject missing/corrupted qualification evidence. This is separate from protecting against an adversary forging an entire report, which is not the stated trust model.

No evidence here establishes model failure rates, proves that the finite grammar cannot admit a human-discoverable shortcut, or removes the need for empirical pilot calibration. Broad rollout should remain blocked until that calibration and the repository's release gates are complete.

## Reviewed source snapshot

The tree was being implemented during review. These hashes identify the files present when this report was written; the findings above distinguish original defects from observed fixes. A later source revision requires the owner to rerun final gates.

- `src/nexus/solver/observation_audit.py`: `10b03ba4468b27cfe4ea257f988af5ad51d424375b80fd561b48b88b5c06d33b`
- `src/nexus/ontology/dynamics/__init__.py`: `43e2d62f14eed0443c523425e668930cbe48ab3e5fe444c84bcb268dc51c3f3c`
- `src/nexus/ontology/dynamics/evidence.py`: `2dbf65c1c2310685239f92af230e57dcd8f852bfcdcfe8a45f4d14093660229f`
- `src/nexus/ontology/dynamics/generation.py`: `bee110f6dcc1b99fe78b7f562ebd434a6906d55632a6193774e4f1bd2a780a34`
- `src/nexus/ontology/dynamics/inference.py`: `8b82e6d3e9b636d8427cf3d550cd6b9e20b03bcf074c99647f90c86d1c113bb7`
- `src/nexus/ontology/dynamics/laws.py`: `7813b6c38c2203eccfceb3ed1fcfd86fe8274d43401b31af4183ec29cb0b7c99`
- `src/nexus/ontology/dynamics/policy.py`: `edf6f6cb351e61719faa954ba4acc933bf251a60892f62de9cb3b88cdbf13162`
- `src/nexus/ontology/dynamics/qualification.py`: `a5b2ebe01ac63a08bce6880d03675a1465ed797bad7394bbc29ff87c159a91e1`
- `src/nexus/ontology/dynamics/runtime.py`: `4123057310ce416eff87731297dfbf024c8061023b7b159b64ca62377299675d`
- `src/nexus/ontology/dynamics/schema.py`: `323547e5adfaa3f7f8ff119829021bb613809315b5a887ebf359a945ee1aaa2d`
- `src/nexus/evaluation/__init__.py`: `fdf4cf1fa3c7213f2687aa137774dc54b0b8d2a1d624a85ccf9ec151600426e0`
- `src/nexus/evaluation/difficulty.py`: `866f664afbc7dc55512bbd8142a0a02a3a99a18570d595b11e346b3187252503`
- `src/nexus/evaluation/matrix.py`: `caef71746c169a9b84930e2d73d3fd91d459ec0d045fbb51d3b8f72daa690243`
- `src/nexus/ontology/mission.py`: `200f95b997d6c6602d743340dcd3cc84f36f0be01fbe9da807aecff317e6c654`
- `src/nexus/ontology/catalog.py`: `e46637e53aa69d5c64bce51eedefa91b436025c8c7a30a254a4e72de90118e79`
- `src/nexus/ontology/payloads.py`: `6f780f6e136d25232fb943f4b66a8cf9029127ff9e52b68070f6bd82ea4c4294`
- `scripts/preflight_matrix.py`: `4b6c08d90c9ea75e95bf894a5993c40665242c4debabc4033ad8c596e1e46e60`
- `docs/difficulty-model-matrix.json`: `ca8eeba4ed5b0e62c4f4cb6e042a6f61a10a0f5f4782164b4eb47847bde782cb`

## Supplemental review: proposed failed-finish-inclusive mass bound

After the source snapshot above, the owner proposed a separate full-prior success bound that includes adaptive guesses and failed finishes. The mathematical argument is valid; this supplement reviews the proof, not the later implementation.

At P1, a successful physical attempt must take the unique seal and move to array, costing at least two actions. Each distinct complete dose-vector guess requires configure doser, operate doser, and finish, costing at least three further actions. Repeating an unchanged guessed vector supplies no new success possibility for a fixed truth. Under budget B=73, the number of distinct physically eligible guesses on any path is at most g=floor((73−2)/3)=23. Treating all preparation and measurement costs as free only makes this upper bound more permissive.

For a strategy allowing at most k ternary scientific measurements and g guesses per path, the number of successful target-vector leaves is at most L(g,k)=g·3^k. This follows by induction: a guess creates one absorbing successful leaf plus a continuation bounded by L(g−1,k); a measurement creates at most three continuation subtrees bounded by L(g,k−1). Both are at most g·3^k. Arbitrary interleaving and adaptive query/guess choice are therefore covered. Repeated target vectors across success leaves can only decrease their union. Randomized strategies are mixtures of deterministic strategies and satisfy the same mass bound.

The full prior has 585 target classes: 528 classes of size 3, 51 of size 6, and 6 of size 9. Summing the largest min(23·3^k,585) classes gives the following independently computed conservative bounds:

| At most k scientific readings | Maximum successful target classes | Uniform full-prior correct mass | Probability upper bound |
|---:|---:|---:|---:|
| 0 | 23 | 156 / 1944 | 8.02469% |
| 1 | 69 | 396 / 1944 | 20.37037% |
| 2 | 207 | 810 / 1944 | 41.66667% = 5/12 |
| 3 | 585 | 1944 / 1944 | 100% (vacuous) |

This argument presumes one non-resettable attempt, no private process/timing side channels, no cross-cell context exposing the paired control, and only the disclosed public ternary scientific channels plus generic rejection/absorbing success. It is a **uniform full-1944-world prior** bound, not a bound for the selected six challenges or a model failure-rate prediction. It must remain separate from the selected-truth positive-measurement certificate; in particular, it supplies no nontrivial three-reading population success ceiling.

## Owner final disposition

After this review, the generic input cap was reduced to 16 million outcome bytes,
certificate preprocessing was made deadline-aware without lazy partition build,
and saved reports now require per-row qualification success. The reviewed
guessing bound was implemented and tested against independent absorbing-success
tree recursion. All 606 tests, ten-cell checkout and installed-wheel preflights,
and the refreshed unchanged repair proof/witness release gates passed. See
`difficulty-validation.json` for final source identity and scope.
