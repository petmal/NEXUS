# Independent design judgement: transfer and evidence

18 October 2026. Review of baseline `b36703d`, plan commit `c6fbcbf`, and the
refinement agreed during this review. This is a design judgement, not runtime
certification. No source files were edited. The reviewer read `AGENTS.md`, the
two evidence-transfer plans, the compositional and dynamics laws, schemas,
inference, evidence, runtime and policy seams, mission tracking, and the finite
decision audit. Counts below were independently computed in memory from scalar
gate equations, without importing NEXUS or the implementation PoC.

## Decision

The complete-behavior transfer mission is a defensible improvement over the
old four-point repair objective. The original final-response cross-talk reader
fails its intended coverage gate and should not be integrated under the stronger
evidence-reasoning claim. The revised upstream-reference construction has
material, mechanically demonstrable observation ambiguity and is suitable to
proceed to implementation **after** the main PoC reproduces the results and the
plans are updated. Executable action bounds, runtime conformance, resource
measurements, and selective-revision qualification remain separate gates.

The revised construction supports the narrow description “coupled observation
inference with a complete-behavior physical objective.” It does not establish
necessary adaptive rounds, cognitive depth, or increased model failure rate.
Matched subtraction remains an intentionally legal complete strategy.

## Original candidate: a material negative result

Let `G_c` be the existing three-gate response. The proposed original reader was
`S_c = G_c + offset + gain*G_(1-c)` and
`R_c = offset + gain*G_(1-c)`, with gain 1 or 2. The 1,728 worlds have 1,672
distinct complete physical behaviors over the 486 conditions.

Complete reference-only observations identify the physical target for 1,724 of
the 1,728 worlds. Of 10,020 distinct complete reference signatures, 10,008 have
one physical target and twelve have two. Only 24 of the 10,368 joint
world/offset/gain instances retain target ambiguity. The four exceptional base
worlds, using zero-based lexicographic enumeration, are:

| Index | `(topology,f,g,h,changed,replacement)` |
| --- | --- |
| 732 | `(1,1,0,1,1,1)` |
| 768 | `(1,1,1,1,1,0)` |
| 1155 | `(2,0,0,0,1,1)` |
| 1191 | `(2,0,1,0,1,0)` |

These form global-sign pairs. They use only addition/subtraction and replace
only `g`; none uses topology 0. Thus reference-only obstruction cannot also
supply the proposed broad primitive/replacement coverage. This is an
identifiability result, not a proof that a reference-only policy is cheap.
Nevertheless it defeats a general claim that the construction requires both
observation channels. The reference is an almost complete physical sensor.

Survey-only ambiguity is much broader, but does not repair that shortcut:
7,992 joint instances retain multiple physical targets under complete surveys.
For gain 1, the two context surveys contain the same sum; for gain 2, they
contain opposite differences plus offset. These algebraic facts should be
preserved in the negative-result record rather than hidden by fixture selection.

## Accepted refinement and independent checks

Use `q` for the physical output offset and `r` for the reader offset, avoiding
confusion with the existing trim `b`. The revised semantics are:

```
F_c = G_c + q
E_c = r + n2_(1-c)
survey_c = F_c + E_c
reference_c = E_c
```

All arithmetic is modulo 3. Both offsets independently range over 0, 1, 2.
`n2_(1-c)` uses the companion context's actual upstream gates and the same
input and trim preparation. Reader strength is the public constant 1. The
reference intervention cancels the current final physical response while
preserving that companion upstream path. These are authoritative instrument
semantics, not a suggested experiment order.

This gives 5,184 physical programs and 15,552 joint worlds. Physical complete
behaviors number 5,016: every base response is zero at the all-zero preparation,
so the three output offsets cannot collapse onto one another. The complete raw
table has `972 * 15552 = 15,116,544` scalar outcomes. This fits the existing
raw table bound, although Python object/cached-mask overhead must still be
measured. Three reader-offset blocks of physical-world masks are a reasonable
exact representation; updates must preserve correlations between those blocks.

The following universal obstructions are immediate:

- Every reference-only history is invariant to changing `q`; its possible
  physical targets therefore remain incompatible.
- Every survey-only history is invariant to `q -> q+1, r -> r-1`. The physical
  counterprogram must change, so complete surveys cannot resolve the mission.
- Matched survey minus reference equals `F_c` exactly. Full paired observations
  identify the physical target and provide a public constructive upper bound.

The improvement is not solely the added scalar gauge. Removing the known
scalar `q+r` from a complete survey field leaves `G_c+n2_(1-c)`. That field has
1,431 signatures. Of these, 227 still contain incompatible `G` targets; they
cover 524 of 1,728 base worlds, including 480 worlds with a multiplication or
square primitive. The distribution across topology is 196/152/176, and across
replacement position `f/g/h` is 168/308/48. Thus structural observation
ambiguity survives even if both offsets are disclosed.

Complete reference fields partition the base worlds into 128 upstream-behavior
classes. Their remaining distinct `G` target counts are:

| Remaining `G` targets | Number of reference classes |
| --- | --- |
| 8 | 96 |
| 16 | 12 |
| 24 | 16 |
| 96 | 4 |

The reader offset is determined by the all-zero reference, but this does not
identify the upstream response field. Including the three possible physical
offsets, complete reference closures retain 24–288 physical targets. In
contrast to the rejected reference, there is substantial physical uncertainty
beyond an unknown sign. The pair `(complete G, complete n2)` distinguishes all
1,728 base programs, while the physical mission itself deliberately accepts the
1,672 behavioral equivalence classes.

A suggested alternative with independent reader field
`r+k*phi(x,y)`, where phi is `xy`, `x²y`, or `xy²`, is genuinely separable
calibration. The fixed three-reference panel `(1,2),(2,1),(2,2)` identifies all
18 reader states: the position of the odd value identifies phi, its difference
from the repeated value identifies k, and the repeated value identifies r.
That construction fixes single-channel shortcuts but adds a short calibration
prefix. It should not be preferred for the present north star without evidence
of a separate benefit.

## Mission consequences and fixture coverage

For the base physical grammar, exhaustive restricted-observation closures give:

| Available physical conditions | Queries | Worlds retaining incompatible full targets |
| --- | --- | --- |
| Both contexts, zero trims | 54 | 148 / 1728 |
| Context 0 only | 243 | 1728 / 1728 |
| Context 1 only | 243 | 1728 / 1728 |
| Inputs with at most one nonzero coordinate | 126 | 182 / 1728 |
| First trim fixed to zero | 162 | 16 / 1728 |
| Second trim fixed to zero | 162 | 132 / 1728 |

These are exact closure results, not requirements that every player perform
every kind of experiment. Both contexts are mission-relevant throughout the
prior. Intervention and mixed-input necessity are fixture properties, not
universal ones. Adding `q` retains these physical distinctions.

Representative structurally ambiguous survey fixtures are below. “Survey rival”
means identical complete `G_c+n2_(1-c)` but a different complete physical `G`.
The same q and reader offset therefore give identical full raw survey fields.
“Passive rival” means identical complete zero-trim physical observations but a
different full physical target. Rows are evidence-backed candidates, not a
uniform sampler or a completed live matrix.

| Base index | Base world | Survey rival | Passive rival |
| --- | --- | --- | --- |
| 1 | `(0,0,0,0,0,2)` | 288 | — |
| 4 | `(0,0,0,0,1,2)` | 75 | — |
| 586 | `(1,0,0,1,0,2)` | 622 | — |
| 580 | `(1,0,0,0,1,2)` | 651 | — |
| 1162 | `(2,0,0,1,0,2)` | 873 | — |
| 1183 | `(2,0,0,3,1,2)` | 1229 | 1187 |
| 1159 | `(2,0,0,0,2,2)` | 1295 | — |
| 0 | `(0,0,0,0,0,1)` | 144 | 1296 |
| 588 | `(1,0,0,1,1,1)` | 1164 | 759 |
| 1155 | `(2,0,0,0,1,1)` | 1191 | 147 |

There are 32 worlds in the intersection of passive physical ambiguity and
structural survey ambiguity: eight with topology 0, four with topology 1,
twenty with topology 2; four replace f and 28 replace g. None replaces h.
Do not claim the full cross-product of properties. Include both sides of chosen
indistinguishability pairs, nonlinear mechanisms, output/reader offsets, and
behaviorally equivalent accepted programs in the final matrix. If physical
indexing is `base_index*3+q`, explicitly verify that convention against the
generator rather than assuming it from this table.

## Requirements to resolve before declaring the phase complete

1. **Update the design contract.** The checked-in plan at review time still
   described six selectors and the rejected gain/final-response reader. The
   refined counterprogram needs seven fields, including q. Give exact selector
   ranges and define residual as `F_world - F_program`. Distinguish public
   physical constants, hidden physical offsets and hidden reader offsets.

2. **Accept full behavior, not private syntax.** Acceptance must compare all
   486 conditions, or a proved equivalent complete signature, and accept every
   equivalent program. A wrong finish excludes every world accepting the
   submitted behavior, not merely the chosen private program. Public resolved
   controls must state their selection convention and condition the belief on
   the actual information that convention reveals.

3. **Keep physical comparisons paired.** The calibrated and combined families
   must share base world and q for a fixed scientific seed. Standard/generous
   profiles must also retain all scientific fields. P0/P1 variation should only
   alter the planned physical logistics. Do not let the extra nuisance draw
   shift the physical sampler or introduce hidden solvability filtering.

4. **Use the appropriate solver representation.** The current `DecisionAudit`
   permits only 256 acceptable decisions; 5,016 physical behavior classes do
   not fit despite the world/row bounds fitting. A target-equivalence backend
   or narrow class-mask implementation is appropriate. Do not raise generic
   search caps or instantiate quadratic pairs of all programs. Preserve
   syntax-world probability mass when equivalent programs are grouped.

5. **Prove resources through the actual action interface.** A greedy query
   tree is only an upper bound. Replay all reachable branches of a public
   policy, accounting for specimen reuse, configuration, committed preparation,
   both readings, moves, application and finish. Compare with fixed paired
   subtraction and practical fixed-panel baselines. Report cold time, peak
   memory and artifact size; no per-episode deep proof search. A timeout is
   unknown, not a lower-bound result.

6. **Audit guesses under the claimed scope.** With a uniform syntax-world
   prior, the largest physical behavior class has 12 of 5,184 physical worlds,
   so the best zero-observation single program succeeds on 1/432 of the prior.
   This is useful but does not bound query/failed-finish interleavings. Any
   stronger finite-budget claim must include eligible rejection feedback and
   the complete legal query domain. Distinguish population success ceilings,
   per-fixture obstructions and guaranteed worst-case policies.

7. **Protect public/runtime semantics.** Keep raw readings and their instrument
   identity public; do not expose physical G, n2 or offset components as extra
   payload fields. Re-preparation must clear stale readings. Probes preview
   without committing. Only an applied program on a carried seal in the mission
   room can succeed. Invalid configurations and preview/error messages must
   depend on public validity rules, never on hidden acceptance or failing
   mission conditions. Reuse the existing mission tracker and family adapter
   seams; no family-specific engine branches are warranted.

8. **Keep T/D and telemetry claims local.** These are separately versioned
   finite structural families, not a universal increase in T or D difficulty.
   A reference reading carries physical upstream information and must not be
   described as pure calibration overhead. Mission resolution counts physical
   behavior classes; full-world resolution additionally distinguishes nuisance
   and observationally distinct but mission-equivalent programs. The two are
   different stopping criteria. Keep all such inference diagnostics terminal
   and private.

## Selective revision and proof limits

The current two-context mechanism is stationary joint inference with a public
one-module relationship. It does not itself require revision. A truthful
inherited program/notebook changes the public prior and may reveal much of the
answer; ignoring that information would make qualification unsound. Compare
the revision PoC against fresh-start, anticipatory and final-context-only
policies, while testing the old context so unaffected capabilities remain
consequential. Do not force the player to submit a wrong belief or delay an
available experiment. If the PoC reduces to stationary inference or a longer
calibration sequence, record the negative result and keep revision unintegrated.

The present evidence supports consequential full-behavior transfer and the
refined coupled observation model. It does not yet establish affordable live
bounds, production correctness, an optimal experiment policy, a required
scientific order, or empirical difficulty. Those limitations are concrete
remaining gates, not reasons to narrow the prior or tighten budgets silently.
