# Staged repair: independent design review

Reviewed base: `ca471a6702a4da8be9023b4846acef7cc24b2ae6` (verified local HEAD), `AGENTS.md`, the proposed design/implementation documents, and the existing engine, rendering, mission tracker, inference, and terminal metric contracts. Read-only review; no production modifications or paid calls. Scalar enumeration below used only Python standard-library arithmetic and did not import proposed implementation code.

**Verdict:** the mathematical core is sound. Proceed with implementation after recording the revised family-qualified axis meaning and making interface conformance an admission gate. No mathematical impossibility or universal repair was found. The evidence supports an experiment-selection benchmark, not an unavoidable deep-reasoning claim.

## Findings requiring explicit treatment

1. **Axis names initially conflicted with the repository contract.** The original design's D1–D3 mechanism counts contradict `AGENTS.md:261–274`, which gives those values probe-related semantic guarantees. The owner's revised proposal—three mechanisms in every live world, family-qualified axes-v2 D3 independent readers versus D4 linked readers, plus D0 control—resolves the silent-reinterpretation risk if this meaning is explicit in the public contract, matrix, and certificates. Do not imply cross-family numerical equivalence or legacy exact probe guarantees. One-to-three mechanism checks can remain offline controlled experiments.

2. **Downstream observations reveal upstream routes.** Fixed-panel lower bounds must include this information. For T3 linked readers the exact minima for one, two, and three mechanisms are **3, 10, 15**, not 3, 12, 21. For T2 the disclosed exponent makes a route identify the preceding shift, allowing optimal fixed panels to omit the middle reader entirely. These are legal shortcuts, not failures of the design.

3. **All information-bound claims remain conditional on the actual interface.** `engine.py:107–123` serializes the entire transformed artifact into events; `render/text.py:20–53` copies entire visible/carried artifacts; `engine.py:192–193` returns free invalid-action error text. Hidden loads, active-route flags, residual-dependent exceptions, or truth-dependent machine limits would invalidate the proof. Require all-world comparison of legal nonreader transitions and free observations within each public disclosure profile. A reading of zero must never be tagged as known inactive/no-signal. Cached readings are previously acquired evidence, not a new measurement.

4. **Reading comparisons do not establish total-action optimality.** A fixed panel here means a predetermined set of reader queries that identifies the law/repair before one final submission. Its minimum is not a bound on strategies interleaving guesses and failed finishes. The sequential adaptive witness is an upper bound unless separately minimized. Physical treatment is additive and commutative; no required machine order or history-sensitive control has been proved. A seal's target dose is already all zero in all 6 one-mechanism worlds, 12/36 two-mechanism worlds, and 24/216 three-mechanism worlds. Therefore three trimming operations cannot be assumed mandatory in an action lower bound.

## Independent mathematical checks

### Repair injectivity

The six stage laws, ordered `(k,e)=(0,1),(0,2),(1,1),(1,2),(2,1),(2,2)`, have distinct three-tag tables:
`012, 011, 120, 110, 201, 101`.

Given every seal's successful cumulative doses, first recover `F_0(u)=d_0(u)` for all three tags, hence its unique `(k_0,e_0)` and route. Inductively recover `F_i(u)=d_i(u)+r_(i-1)*d_(i-1)(u) mod 3`; its three values identify its law and route. Thus every world has a unique repair, and every repair accepts at most one world. This also proves solvability by computing the doses in the forward recurrence.

| Mechanisms | Worlds / distinct full repairs | One-tag repair classes | Two-tag repair classes |
|---|---:|---:|---:|
| 1 | 6 / 6 | 3 | 5 |
| 2 | 36 / 36 | 9 | 27 |
| 3 | 216 / 216 | 27 | 155 |

The partial-goal counts use tags `{0}` and `{0,1}`. They independently demonstrate why parameter ambiguity is insufficient when the mission covers fewer seals. The existing history seed-239 witness still needs its separate proposed regression; this review did not independently reconstruct its 32-world posterior.

### Public adaptive witness

At the known active carrier, read tag 0. A result of 2 uniquely identifies `(k,e)=(2,1)`. A result of 0 leaves the two laws with shift 0: read tag 2. A result of 1 leaves three laws: read tag 1, whose outputs distinguish them. The identified route selects the next stage's carrier. This uses only public observations, never more than two readings per stage.

Exact T3 sequential-witness length distributions across all worlds:

| Mechanisms | Number of worlds at each reading count |
|---|---|
| 1 | 1 reading: 1; 2 readings: 5 |
| 2 | 2: 1; 3: 10; 4: 25 |
| 3 | 3: 1; 4: 15; 5: 75; 6: 125 |

These distributions are achieved-policy statistics, not per-world minimum certificates.

### Fixed panels

I enumerated all pairs of worlds and their separating reader-query sets, removed supersets, and enumerated panel subsets until a feasible minimum. Stage-0 carriers 1 and 2 are constant and safely omitted. There were respectively 3, 10, and 67 inclusion-minimal pair constraints for one, two, and three stages. The exact minima were 3, 10, and 15.

Sufficient linked T3 panels:

- One mechanism: all three stage-0 tags at carrier 0.
- Two: stage 0/carrier 0/tag 0, plus all nine stage-1 carrier/tag combinations.
- Three: all three stage-0 tags at carrier 0; stage 1/tag 0 at each carrier; all nine stage-2 combinations.

For three mechanisms with independently active carrier 0, the T3 fixed minimum is 9 and the same sequential witness uses at most 6.

T2 must be qualified separately for every disclosed exponent vector. Independent enumeration gives:

| Exponents | Independent fixed minimum | Linked fixed minimum |
|---|---:|---:|
| 111 | 3 | 6 |
| 112 | 4 | 7 |
| 121 | 4 | 6 |
| 122 | 5 | 7 |
| 211 | 4 | 7 |
| 212 | 5 | 8 |
| 221 | 5 | 7 |
| 222 | 6 | 8 |

In every linked T2 row an optimal panel exists using only stage 0 and stage 2. The sequential T2 witness has worst-case reading count `3 + number_of_squared_stages`; no optimality claim for that linked witness follows from this table.

### Finish-inclusive coverage ceiling

Let `B(k)` bound how many distinct repair signatures a deterministic strategy can win on with at most `k` feedback actions, granting all physical setup and arbitrary repair selection for free. A reader has at most three continuations; a finish succeeds on at most one signature and otherwise has one continuing failure branch. Therefore

`B(0)=0`, `B(k) <= max(3 B(k-1), 1+B(k-1))`, giving `B(k)<=3^(k-1)` for `k>=1`.

The bound includes failed finishes, guesses, and repeated submissions. The probability ceiling below also applies to randomized strategies by conditioning on their random coins and then averaging; their union of possible successes need not obey the deterministic coverage count. Ineligible finishes cannot provide extra hidden information. Success terminates, so its receipt/terminal diagnostic richness creates no continuation.

Under the stated uniform conditional prior, success probability is at most `min(1,3^(k-1)/N)`, with `N=6^m` for T3 and `N=3^m` for an exact T2 exponent disclosure. T0/T1 exact-law controls have `N=1`. With a nonuniform prior, use the total mass of the largest `3^(k-1)` signature probabilities instead. This is not an empirical matrix success rate or an exact minimax action bound. For T3 with three mechanisms, five feedback actions cover at most 81/216=37.5%; six yield no nontrivial ceiling. This alone does not prove six readings necessary.

## Runtime and metrics acceptance gates

- The new mission tracker must track all three named seals, cumulative doses, room, and carried eligibility. `configure` and `probe` do not commit dose; stock specimens never replace actual seals. Repeated treatments and anneal must match the scalar recurrence.
- Preserve the existing pre-outcome assessment order (`investigation_metrics.py:149–168`). Exclude a rejected repair only when the submission is physically eligible. A missing seal/wrong room does not falsify the dose vector.
- Preserve the distinction between supported and compatible wins (`decision_metrics.py:124–131`): a successful guess must not become retrospectively supported merely because success identifies the world.
- Post-resolution construction is not wasted experimentation. Count reader actions separately from treatment operations. A trace's chosen contexts do not establish that the player cognitively adapted; describe observed reading paths and reference-policy path lengths accurately.
- Keep diagnostics unavailable while active (`session.py:241–258` already enforces this); don't expose private qualification certificates, seeds, truth-selected resource budgets, or matrix seed labels in player evidence.
- Validate public disclosures exactly: T2's exponent tuple, T1's full laws if enabled, T0's complete repair table, constant physical goals/topology, and identical truth for paired independent/linked profiles. Unsupported combinations must fail clearly.

The updated implementation can satisfy these gates without changing the existing engine's charging, transactionality, replay, or receipt semantics.
