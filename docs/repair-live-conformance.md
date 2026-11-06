# Coupled repair: live-interface conformance argument

Scope: `coupled-repair-v1`, `stationary-three-round-v1`, T3/D5/P0 or P1/R1,
exactly 17 or 18 actions. One non-resettable attempt, serial application requests,
no private files/process access, and a uniformly sampled truth index in 0..7202.
P and presentation (canonical, sealed-facility-v1 or sealed-facility-v2) are operator-fixed before sampling,
and the prior is uniform within each such public stratum. The public nonce is sampled independently. This is a bound on policy success over
that population, not a guarantee for each fixed seed or for model failure rates.
Application messages are included; timing, operating-system and network side
channels are not. An operator who leaks the seed invalidates the scope.

The proof is **factored**, not enumeration of the full inventory/history product.
Its trusted base is the reviewed transition adapter and existing session engine.
The independently checked query upper bound alone is not a live certificate.

## 1. State invariant and complete observation partition

Every reachable canonical state consists of public room, location, specimen
preparation/treatment, machine settings, resource/turn/phase values, previously
returned cached readings, and acceptance/terminal flags. Hidden `a,b,c,r,d` occur
only in immutable private truth, never in canonical WorldState. Each stock take
creates an identical fresh survey; there are no specimen-specific latent values.
The only hidden-dependent active transitions are the readings below and finish.

| Request class | State effect and complete information class |
|---|---|
| Manifest/evidence/health/schema | Fixed validated template plus independent opaque identity; no truth-dependent generator choices |
| Observe/status/action-observe | Projection of public state and already returned readings; no new hidden evaluation |
| Move/take/drop/wait | Public topology, identity, location, material creation and cost only; phase is constant |
| Configure stage | Public `[mode,x]`; accepts exactly 14 possibilities; clears acceptance flag; no reading |
| Configure doser | Any of 2401 public four-vectors; no correctness check or key treatment |
| Operate stage | Survey orientation overwritten, charge cleared, cached reading cleared; seal insensitive |
| Operate coupler | Oriented survey charged; otherwise insensitive; cached reading cleared |
| Operate doser | Seal dose overwritten, survey insensitive; cached reading cleared |
| Reference probe/operate | Survey yields A=a; seal yields null; all other payload fields public |
| Reader probe/operate | Charged oriented survey yields B(x) or C(y); all others yield null; all other fields public |
| Stage/coupler/doser probe | Same public hypothetical payload, without committing; cannot create a new usable specimen |
| Finish | Unapplied, uncarried or misplaced seal always rejects. Eligible dose gives only generic rejection or absorbing victory |
| Invalid fields/IDs/ranges/state/turn | Parser/control/public-state error with rollback; no hidden-dependent validity test |
| Duplicate/conflicting request | Cached public reply or public turn conflict; no fresh query; terminal diagnostics only after terminal |
| Events | Accepted public actions/results and hashes of the above public-state closure |
| Finalize/deadline/terminal requests | Absorbing terminal state; diagnostics cannot aid a later successful continuation |
| Unknown route/method/body | Framework response independent of hidden truth; included in transport transcript |

This table is exhaustive for the discriminated Action union and the Session,
JSONL and single-session HTTP operations. In each case, the transition returns
only public inputs/state or one named query. Induction on the history proves that
no unlisted hidden channel can be synthesized by combining classes. A stored
reading is tied to its original context: changing preparation clears it; observing
it never re-evaluates a law. Hashing this closure does not introduce hidden data.
The response fields suppressed by the witness's `ok` normalization are therefore
computable from its public state/history and chosen actions. The upper bound does
not restrict arbitrary players to that witness normalization.

The general multi-session server is rejected through an optional trusted-runtime
capability. Creating another process/session for the same hidden world is an
operator reset and outside the attempt. External HTTP/stdio isolation, rather
than an in-process Python wrapper, is the player/private-process boundary.

## 2. Global cost charging, including preconstruction

For each **distinct** informative B/C context in a complete history charge:

1. A stage configuration selecting that context (initial settings are unset).
2. A committed stage operation on a survey creating that orientation.
3. A committed coupler operation after that orientation, because reorientation
   always clears charge, even if the same coordinates are selected.
4. A paid reader request exposing its response.

All four sets of charged events are disjoint across distinct contexts. Extra
specimens, earlier configurations, interleaving, retained charge and repeated
uses do not share an orientation-changing event across distinct contexts.
Repeated readings of one context add no information because truth is immutable.
Previews do not commit and cannot satisfy steps 2/3. Configuration reuse can save
cost only for duplicate immutable queries. A costs one paid reference request.

For each distinct eligible repair tested by finish charge a doser configuration,
a committed operation on the unique seal, and finish. There is no initial dose,
second seal, partial treatment, component verdict or correctness-sensitive
configuration. Doser overwrites; repeated finishes on the same rejected dose are
uninformative. All vectors, including impossible targets, are legal. An impossible
vector has publicly predictable rejection and is dominated by omitting it.

Any successful querying path also pays one seal take, one survey take, and P1's
unavoidable move into the array. Removing these costs gives query budget 15.
**A pure-guess policy need not take a survey.** It has 16 after key acquisition and
travel but can still afford only five three-action attempts, exactly the abstract
budget-15 allowance. This separate case avoids falsely charging mandatory survey
acquisition to every policy. Interleaved attempts use the next normal form.

## 3. All-policy reduction and upper bound

Move the charge for a prepared context to its reading; this gives the abstract
player more freedom to choose the context using later information. Discarding
public-only state logistics also helps. Grant d freely at the start. Its three
strata are isomorphic, each containing 2401 equiprobable `(a,b,c,r)` worlds and
343 distinct targets. An arbitrary live policy can therefore be simulated in this
player-favoring query model without losing successful worlds or adding feedback
boundaries. All legal query subsets, not only the investigator's A/B/C path, are
included in the independent checker.

Generic rejected guesses do not alter the laws or future experiments. Reserve
their costs, follow the original policy's all-rejected continuation, then prepend
the reserved guesses to the final fixed continuation. If a counterfactual branch
has no remaining worlds, its reserved guesses already cover the successful paths.
Trim unreachable trailing commands after universal success; stop before exceeding
the reserved spending budget. This handles policies whose real executions halt
before their written suffix. No extra feedback is used. Choosing the k largest
posterior target masses dominates each funded fixed list of k guesses.

The complete independently checked 576-choice payload proves the relaxed optimum
**1029/2401 = 3/7 < 1/2** for at most two feedback rounds. Thus no perfect two-round
live policy exists at the exact release budget. The full hidden-degree query
calculation gives 19/49, retained as supplementary evidence, not needed for the
conservative certificate. At one extra action a shallow policy becomes perfect;
the certificate cannot be reused under budget or preparation changes.

## 4. Positive policy, science and recovery

The serialized public program uses fixed batches A; B(a); C(b), then the fixed
correct repair. The third reading distinguishes the functions `c+z`, `c+z*z`,
`c+(z*z)*z` and transfers them to contexts 3/4. This is a small bounded T3 grammar,
not broad open-ended discovery. Degree uncertainty is mission relevant but is
not responsible for all the calibration depth: granting d still leaves the bound.

Raw/unprepared specimens reveal at most a, leaving different required doses.
Removing r's shared coupling permits the same fixed three contexts in one batch
with preparation costs unchanged. Thus dependence is scientific, not only action
padding. The coupled residual system prevents simple copying of the measurements,
but its known triangular inverse is deliberately small; no broad operational
planning difficulty is claimed.

Every truth has a three-round winning policy in 14+P actions. The same policy
works after any one failed complete dose attempted after setup, using the
three-action recovery allowance; no private successor selection is required.
Wrong guesses that win terminate automatically. The witness does not promise
recovery from arbitrary wasted experiments or from exhausted deadlines.

## 5. Executable evidence and invalidation

- `test_repair_construction`: all 7203 truths × 14 response contexts; unique target
  mapping, preparation ablation, raw insufficiency, structural transfer.
- `test_repair_conformance`: every preparation class/legal stage and dose control,
  both materials, engine probe/operate semantics, every eligible/ineligible raw
  dose, ineligible-finish telemetry, restart rejection and malformed programs.
- `test_repair_runtime`: all truths through serialized public play, real receipts
  and exact replay; recovery, active privacy and complete HTTP payloads.
- `test_public_observation_coverage`: full transport projections, errors, bounded
  capture and delivery failures. An incomplete capture cannot establish coverage.
- `test_repair_qualification`: separate upper checker, scope/false-payload rejection.

These finite checks discharge component premises and support the induction above;
they do not enumerate every complete live state. The release binding records the
reviewed semantic source/proof/witness identity and fails closed on source changes.
Hashes establish identity only. Requalification must repeat the relevant proof,
conformance and replay gates, not merely regenerate hashes.
