# Bounded audit: shared-mask calibration, structural transfer, and coupled key repair

Date: 2026-10-14. Follow-up to `repair-construction-judgement.md`. No repository or approved-plan edits were made. The calculations below certify the stated finite query model; live qualification remains conditional on the explicit conformance obligations below.

## Judgement

The F7 extension is a substantially better candidate than the null-gated pointer chain. The shared r creates a real calibration dependency. The three candidate response functions have different behavior at mission contexts. The proposed triangular key residuals create actual cross-effects between treatments and preserve a bijection to the mission predictions.

The bounded calculation succeeds: the complete 7,203-world weighted-query model has exact two-round success **19/49**, including recoverable final guesses. A smaller, player-favoring model that reveals the structural choice for free has exact success **3/7**, sufficient for the 50% ceiling. Both examined cost patterns give these results.

This supports proceeding to a small experimental live implementation and conformance proof. It does **not** yet establish that the real interface satisfies the query-cost lower bounds, generic-failure assumption, or full action coverage. It also does not establish broad scientific richness or LLM difficulty. The initial <=128-world target was not met; the expansion is explicit and measured below.

## Reusable evidence

- Source: `scripts/prove_repair_queries.py`
- Results: `docs/repair-query-proof-results.json`
- Reproduction: `uv run python scripts/prove_repair_queries.py`
- Smaller sufficient calculation: `uv run python scripts/prove_repair_queries.py --model granted`

The source is independent of the repository's general finite-game solver. It uses exact integers and fractions, has a per-model 60-second limit, and bounds the recomputable partition LRU to 1,024 entries. It does not silently convert a timeout into a proof.

## 1. Exact scientific and mission model

All arithmetic is in F7. Initially `a,b,c,r` are independent uniform field elements, and `d` is independently uniform in `{1,2,3}`. Thus there are `7^4 * 3 = 7,203` equally weighted truths.

```
f(z) = c + z^d
A    = a
B(x) = b + r*(a-x)
C(y) = [c + r*(b-y), c + 2^d + r*(b-y)].
```

The difference between C's two channels identifies d. The first channel is a masked estimate of c. The three-round policy is A, then B(a), then C(b). It learns a,b,c,d, but need not learn r.

The mission contexts genuinely distinguish the candidate relationships:

| d | C-channel difference `2^d` | `3^d` | `4^d` | `f(4)-f(3)` |
|---|---:|---:|---:|---:|
| 1 | 2 | 3 | 4 | 1 |
| 2 | 4 | 2 | 2 | 0 |
| 3 | 1 | 6 | 1 | 2 |

Therefore `(f(3),f(4))` uniquely determines `(c,d)`, and the complete mission target `(a,b,f(3),f(4))` is bijective with `(a,b,c,d)`. Each target has seven equally weighted r variants. The calculation preserves these weights.

This meets the minimal **semantic** T3 criterion if the public uncertainty is explicitly the missing choice among linear, quadratic, and cubic relationships: they are different functions, have different algebraic invariances, and require different operational targets. It is not merely an alternative label for the same function or a hidden selector irrelevant to success. It remains a very small, fully disclosed structural grammar; do not describe it as broad structural discovery.

The structural d uncertainty is not what drives all three adaptive rounds. Granting d leaves the calibration dependency. Report these axes separately: multistage calibration plus relationship identification and transfer, not “three stages of structural discovery.”

## 2. Coupled key residuals improve the operational claim

The proposed real key response is

```
R0 = a-u
R1 = b+a*u-v
R2 = f(3)+b*v-w
R3 = f(4)+f(3)*u*v-z.
```

The public goal is all four residuals zero after applying treatment `(u,v,w,z)`. A successful dose is

```
u = a
v = b+a^2
w = f(3)+b*v
z = f(4)+f(3)*a*v.
```

This is real known coupling in the actuation model: u affects R0, R1, and R3; v affects R1, R2, and R3. Applying independent copied readings generally fails. For example, with `a=b=1,c=0,d=1`, direct copying `(1,1,3,4)` produces residuals `(0,1,1,3)`, while `(1,2,5,3)` zeros all four.

The information calculation transfers exactly because the mapping is invertible on the admitted target set:

```
a = u
b = v-a^2
f(3) = w-b*v
f(4) = z-f(3)*a*v.
```

The mission-pair difference then determines d and c. No two distinct `(a,b,c,d)` targets share a successful dose. Generic failure of a complete dose therefore eliminates precisely that repair target, regardless of r.

This is more than putting predictions in an artifact payload: interventions now alter several acceptance conditions jointly, and an inferred relationship must transfer to new operating contexts. Nonetheless, the repair map is a known triangular system once the calibrated predictions are available. The family remains a compact controlled science task, not evidence of rich open-ended repair reasoning. Do not claim preservation of an initially working channel unless the actual initial state and goal provide it.

## 3. Weighted-cost results including guesses

The abstract grammar consists of all 15 queries A, every B(x), and every C(y), plus a complete candidate repair followed by generic success/failure. Queries are immutable and commute. Repair rejection does not affect future queries. A candidate attempt has a fixed cost and can be repeated with a new complete candidate.

| Cost model | A | B/C | Candidate attempt | Budget after setup | Full hidden-d exact S<=2 | d granted free exact S<=2 |
|---|---:|---:|---:|---:|---:|---:|
| Initial model | 1 | 3 | 2 | 11 | 19/49 | 3/7 |
| Proposed physical model | 1 | 4 | 3 | 15 | 19/49 | 3/7 |

The hidden-d policy attaining 19/49 is:

1. First batch: A.
2. Second batch: B(a) and C(y0), with y0 fixed when the batch starts.
3. Commit up to two complete candidate repairs using the posterior.

If `b=y0`, c is resolved and the first repair succeeds. Otherwise the unknown uniform r leaves seven equiprobable c values, and two guesses succeed on two of them. Thus

```
S = 1/7 + (6/7)*(2/7) = 19/49.
```

The exhaustive search found no better permitted policy. The larger value 3/7 in the d-granted relaxation is attained by A; then B(a); then three c guesses, without any C reading. This is precisely why the simple two-query-plus-C strategy is not the optimum of that relaxation.

The two cost patterns are not identical in every irrelevant corner: A alone permits five final guesses in the first model but four in the second; one B/C without A permits four versus three. The exhaustive results agree despite these differences.

### One extra action destroys the bound

At one additional action, both models admit

```
batch 1: A
batch 2: B(a), C(y0), C(y1), with y0 != y1
commit: the correct repair.
```

C's first components give

```
r = [C0(y0)-C0(y1)] / (y1-y0)
c = C0(y0)-r*(b-y0).
```

d is identified by either channel difference. This succeeds in every world. A fixed query batch `A,B(x0),B(x1),C(y0)` also suffices, by first recovering r from the B difference and then decoding offline.

For the physical model, the setup-free cost is `1+3*4+3=16`. Therefore the query model has exact guaranteed one-round and two-round costs 16, versus a nominal three-round witness of 12. At released setup-free budget 15, the shallow success ceiling holds; at 16 it becomes 1.

With the latest proposed logistics, P0 has nominal 14, release budget 17, and shallow guaranteed success at 18. P1 has nominal 15, release budget 18, and shallow guaranteed success at 19. Publish this one-action cliff. It is permitted by the approved contract but cannot be hidden behind the recovery label.

## 4. Why final-guess normal form covers recoverable submissions

This is the key reduction behind the calculation; it is valid only for the stated immutable-query/generic-failure abstraction.

Take any policy with guesses interleaved among its query batches. Reserve the costs of its guesses, but defer their execution. Choose subsequent experiments exactly as the original policy would after those guesses all failed. This choice uses only public history and the known guessed target list; it is not a hidden-truth oracle.

Trim suffixes unreachable after universal success or exhaustion. If the counterfactual continuation would exhaust its reserved budget, stop and execute its reserved guesses; they already cover any otherwise missing successful paths. This includes words with irrelevant trailing requests after all real worlds halted.

At the final commitment, prepend the deferred guess list to the original final continuation. If an observation has no branch in the counterfactual all-fail policy, the actual target must be one of the deferred guesses, so committing that reserved list suffices. On other branches, all reserved costs plus subsequent queries and guesses fit the original budget. Absorbing success automatically halts the list. No extra feedback round is needed.

The resulting final list is dominated by choosing the k targets with greatest posterior mass, where `k=floor(remaining_budget/attempt_cost)`. Therefore all interleaved generic attempts are covered by an optimization over two query batches followed by this top-k value. This is a genuine all-policy reduction in the abstract model, not a restricted heuristic policy pool.

Repeated identical queries are redundant, and immutable queries commute within a batch. At these budgets at most three distinct queries can occur before a funded repair. There are 576 admissible query subsets, including the empty subset. The solver enumerates every first subset, every response cell, every affordable second subset for that cell, and the exact top-k posterior mass. A final non-feedback query cannot affect repair choices and is dominated by omitting it.

The reduction fails if rejection reveals residuals/components, if failed repair changes the survey response, if a partial operation can carry out a useful unknown compensation, or if candidate changes cost less than the stated amount. Those are live conformance questions, not optional assumptions to omit from the manifest.

## 5. Smallest sufficient relaxation and measured search growth

Grant d initially for free. Since it is independent of a,b,c,r and only changes a known bijection from calibrated values to the final target, all three disclosed-d strata are isomorphic. The remaining problem has 2,401 worlds, 343 repair targets, and 15 queries. The free disclosure helps every real policy, so its exact 3/7 value is a useful **upper bound** for the hidden-d task once the action abstraction is justified.

The source also enumerates the full 7,203-world model for independent confirmation. Reproducible observed resource use after bounding the partition LRU:

| Model | Cached branch/budget subproblems per cost scenario | Cached target-mass beliefs | Both cost scenarios elapsed | Process peak RSS |
|---|---:|---:|---:|---:|
| d granted, 2,401 worlds | 21,225 | 21,127 | about 2.08 s | 67,028 KiB |
| d hidden, 7,203 worlds | 61,993 | 61,797 | about 11.90 s | 433,292 KiB |

The full model peak is measured in a process that first ran the smaller model; it remains below 512 MiB. An earlier unlimited partition cache used about 2.29 GiB; that implementation was replaced. Search sizes here are not live state counts and should not be advertised as such.

For the release ceiling, independently checking the smaller player-favoring model and its abstraction is enough. There is no need to expand every live inventory/settings/history combination into a 7,203-world transition cross-product merely to reproduce this number. The trusted query-model boundary and normal-form proof must be explicit, however; a digest or asserted macro cost is insufficient.

## 6. Live preparation-cost obligations

The proposed survey state is plausible: material, an initially unset orientation `(plane,x)`, a public charged flag initially false, and a context-tagged last reading. A stage operation commits its configured orientation and clears charge. Coupler operation commits charge. A reader returns the masked value only from the committed prepared state. Probe previews of stage/coupler return only the stated public changes, not a masked reading or hidden residual.

To prove cost >=4 for each distinct informative contextual query, charge across the **whole history**:

1. One stage configuration selecting its distinct `(plane,x)`.
2. One committed stage operation creating that orientation and clearing charge.
3. One committed coupler operation after that stage operation.
4. One paid reader operation/probe.

Do not require these actions to be consecutive or to occur after the latest feedback. A player may pre-stage settings, retain specimens, or construct several contexts in advance. The lower bound must still count all those actions. Moving their cost to an abstract query performed later is player-favoring: the abstract player may choose the context using at least the information the concrete preparation used.

The following conditions are essential:

- Stage settings start `None`. A useful default orientation or already prepared specimen must be modeled rather than erased.
- One configuration cannot specify several planes/values at once. Every legal compound setting is included in the actual grammar.
- Reusing a configuration across several specimens yields only the same immutable query, not new specimen-specific hidden parameters.
- Repeating the coupler is idempotent for the hidden response. A repeated excitation that changes a coefficient could create a cheap new measurement.
- Changing orientation clears charge. Otherwise a context change might cost only configure+stage+read, allowing a fourth useful reading inside the release budget.
- Probe previews cannot be chained as committed objects. Reading the real specimen after a preview sees its real unmodified state.
- Merely observing a prepared artifact, reading its history, or receiving an operate response must not recompute and expose a new hidden reading. Stored old readings need their original context tags.
- Raw/uncharged/key reader responses and invalid-input responses depend only on public state unless included as additional queries.

These are physical and public-state rules, not locks requiring prior discovery. All contexts remain legal before A or B is known. There is no rule requiring an explanation or an earlier correct reading.

## 7. Live attempt and setup-cost obligations

A new tested dose costs three actions only if it requires configure, committed key operation, and finish. The key must start publicly unconfigured. A valid default dose would create a cheaper first guess. Repeating finish on an unchanged failed key gives no new information; changing dose requires another committed operation. Configuration alone and probe previews must not affect the assessed key.

Every raw dose vector remains legal, even if it cannot win under the admitted function family. Such impossible-target attempts may be omitted from the abstract target list only because their rejection is publicly predictable, their physical effects do not aid later surveys, and they are dominated by wasting/omitting their cost. This is not a private legality oracle.

The current P1 accounting uses key take + survey take + one unavoidable movement. The survey take is **not** universally necessary: an uninformed guessing policy can omit it. A sound normalization can still work here:

- Any informative survey query requires the survey acquisition, so those paths pay all three setup actions.
- Without the survey, P1 leaves 16 action units after key take and movement; P0 also leaves 16 after key take. Either permits only five three-action attempts, the same as abstract budget 15.
- Interleaved early guesses can be deferred as above while reserving their costs; the no-query branch also fits the five-guess abstract allowance.

Prove this arithmetic/normalization explicitly instead of subtracting three supposedly mandatory actions from every policy. Confirm the key's location, inventory constraints, and finish predicate actually make the stated move/take obligations unavoidable. Initial key and survey availability must match the witness.

Generic wrong-finish feedback is essential. Any residual value, failed-condition index, partial-correctness score, truth-dependent key appearance, or mission-probe result adds a channel. The full response, error, status, receipt, retry, and terminal/deadline inventory still requires live audit.

## 8. Scientific ablations and release recommendation

The construction can distinguish actual inferential dependency from preparation padding while keeping all preparation costs and controls unchanged:

- Remove the shared r terms while retaining the same latent support/weights as irrelevant r variants: B becomes b and C becomes `(c,c+2^d)`. A, any B, and any C in one fixed batch resolve the mission. This changes information, not the number of setup actions.
- Supply r: A and any fixed B/C readings can be decoded offline in one batch.
- Supply a matched prepared context or upstream calibration: recompute the savings and round change under the exact disclosed control.
- Supply d: the task remains adaptively calibrated, but shallow success rises from 19/49 to 3/7. This separates structural uncertainty from calibration depth.
- Replace the key residuals with independent component goals: direct copying becomes sufficient after calibration. The explicit example in Section 2 witnesses the cross-effects lost by this ablation.

Raw unprepared contexts reveal at most a under the proposed contract. Worlds sharing a but differing in b or `(c,d)` require different unique doses, so raw evidence has a direct acceptance obstruction. This supports D5 once every raw/preview/error alternative is covered. It does not exclude eventual R0 guessing.

Recommendation: proceed with the smallest live implementation of this explicitly expanded, bounded family; retain `experimental` status until the complete protocol and global cost-accounting proof pass. Use the d-granted 3/7 relaxation for the conservative success ceiling, keep the full 19/49 result as checked abstract detail, publish the one-extra-action failure, and name the small structural grammar and known triangular actuation model honestly. No threshold change, hidden family exclusion, stage lock, or omitted legal request is needed by the abstract construction.
