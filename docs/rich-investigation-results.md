# Richer scientific worlds: coupled-network-v1

## Change and rationale

The latest audited run had 103 legitimate first-submission wins and one provider
Error. Every played task had a uniquely determined target at submission. Increasing
the action pressure would mostly penalize extra work. This opt-in family instead
replaces the small separable response curve with interacting, composed mechanisms
and makes experiment construction depend on operation order.

Enable with `NEXUS_AXIS_VERSION=2` and
`NEXUS_SCIENCE_FAMILY=coupled-network-v1`, or the corresponding CLI options.
Live support is T3/D4 and T3/D5, P0–3/R0–2, plus D0/T0 and D0/T3 diagnostic
controls. Unsupported cells reject explicitly. The existing shared-response
family, default axis version, and seed meanings remain unchanged.

## Architecture

All arithmetic is exact modulo 7. Every specimen shares hidden properties
`a,b in {1,2,3}`. Correction parameters `c,d in {1,2,3}` and three independently
chosen relationship nodes are fixed throughout an episode:

```
u = U(x,a)        U ∈ {x+a, x*a, x²+a}
v = V(y,b)        V ∈ {y+b, y*b, y²+b}
response = F(u,v,c,d)
F ∈ {u*v+c*u²+d*v², (u+c)*v²+d*u, (u²+c)*v+d*u*v}
```

The generator composes typed immutable expression ASTs; the deterministic runtime
interprets them without generated code or eval. The full bounded prior is public.
This gives 27 structures and 2,187 complete worlds, with 1,175 distinct field
response vectors. Every prior world is admitted. Scientific success requires
correct predictions, not recovery of a unique hidden symbolic representation.

T3 controls the missing relationship structure. D4 supplies specimens at twelve
calibrated bench coordinates. D5 supplies only `(0,0)` and two public preparation
operations: `A(x,y)=(x+1,y)` and `B(x,y)=(x,y+x+1)`, modulo 7. Their order matters:
starting at zero, A then B gives `(1,2)`, while B then A gives `(1,1)`.
The four field conditions are `(4,1),(1,4),(4,3),(3,4)` and cannot be measured.
Both D levels share the same truth for the same seed. There is no controller
preview and no correctness feedback from configure; finish checks the joint vector.

R0 retains unlimited source copies, machine uses and actions. Finite R profiles
have sufficient stock/machine limits for the proved strategy; R1 gives the
realizable worst-case reference action count plus eight, R2 gives that count.
This is not a full physical minimax optimum. P controls room separation.

## Proofs before integration

`scripts/coupled_network_poc.py` and
[machine-readable results](profiling/coupled-network-proof.json) provide executable
checks against an independently written arithmetic evaluator.

| Matched mathematical prior | Worlds | Prediction classes | Adaptive worst case | Minimum fixed set |
|---|---:|---:|---:|---:|
| T1: mechanisms and c=d=1 supplied | 9 | 9 | 2 | 2 |
| T2: mechanisms supplied, c,d unknown | 81 | 73 | 3 | 4 |
| T3: mechanisms and c,d unknown | 2,187 | 1,175 | 5 | 8 |

T1/T2 are mathematical ablations, not integrated live profiles. Their D semantics
need separate qualification before broadening support.

- Runtime and independent evaluator agree on 111,573 world/coordinate cases.
- All twelve bench readings determine the field vector for every admitted world.
- Axis-only experiments leave 271 ambiguous transcripts covering 887 worlds.
  Even adding diagonal points leaves 54 ambiguous transcripts covering 145 worlds.
  The proof artifact includes actual admitted world pairs with different targets.
- Repeating only A or only B from the origin reaches only the axes. A guaranteed
  D5 solution therefore needs some mixed construction. Combined operations reach
  all 49 states; every bench point needs at most four operations from the origin.
- A relaxed union-polynomial fit has bench rank 12 and bench-plus-field rank 14.
  `(1-x)*(y-y⁴)` vanishes at every bench point but changes a field prediction.
  This witness belongs to the relaxed polynomial class; it is **not** a pair of
  admitted generated worlds. Using the disclosed structural prior resolves the gap.
- A baseline of 32 seeded random experiment orders over every world gives mean
  5.290 measurements and worst case 12; the exact adaptive guarantee is five.

These results establish richer inference and useful experiment selection. They
do not establish a drop in model success. Enumeration is legitimate, the prior
is still small, and GF7 carries less information per reading than the previous
GF17 family. Cross-family measurement counts are not a pure structural ablation.

## Performance and diagnostics

Exact adaptive search now uses target-mask lookups, a safe outcome-fanout lower
bound, duplicate information-partition removal, and incumbent pruning. The exact
minimum fixed experiment set learns necessary pair-separation constraints from
counterexamples. The 100,000-belief guard is retained. An independent exhaustive
oracle agrees on all 12,886 nonempty beliefs in 200 small random problems and on
all 200 minimum fixed-set results.

These optimizations made the new prior practical without parallel worker startup
or additional dependencies. The recorded PoC solves its adaptive and fixed costs
in 0.581 seconds on this host; this is not a controlled cross-version speedup
measurement. Compiled priors and exact policies are shared across arbitrary
episode seeds within a process; whole episodes need not be precompiled.

Ten fresh-process pilot cases on Python 3.14.8 measured the following; imports and
standalone full-prior qualification are excluded from generation timing. Each
process generated its case twice, then successfully played its reference policy.
See [raw benchmark](profiling/coupled-network-benchmark.json).

| Profile, five seeds | Cold generation range | Warm generation range | Reference actions | Guaranteed bound / R1 budget |
|---|---:|---:|---:|---:|
| D4/T3/P1/R1 | 0.791–0.895 s | 0.279–0.285 s | 17–21 | 21 / 29 |
| D5/T3/P1/R1 | 0.838–0.985 s | 0.272–0.341 s | 15–25 | 28 / 36 |

An additional diagnostic D5 call reported 0.182 s for prior construction, 0.328 s
for information policy (16,817 cached beliefs), and 0.284 s for 2,028 physical
policy-leaf witnesses. Public evidence took under a millisecond. This workload
does not warrant CPU/GPU parallelization. Seed-independent physical-bound caching
could reduce warm generation further if multi-episode service workloads justify
it; it would not remove cold per-task construction cost.

Operator timing now separates prior compilation, information policy, physical
witnesses, public evidence, and full-prior qualification. Logs include prior size,
cache state, cached beliefs, policy leaves and action bounds. None of these are
added to active-play responses. Terminal performance uses the appropriate prior
and two-coordinate experiment names, with the existing receipt/metric contract.

## Review and validation

Independent mathematical and integration reviews found no field-preview bypass
or public/private leak. Review identified mixed specimen-family acceptance and
malformed in-memory AST handling; both are repaired with regression coverage.
Qualification validates schema and prior membership first, compares the complete
compiled public contract and metadata, checks the actual trace, then physically
replays every evidence-compatible prior world.

The previous real-model artifact was replayed after integration: 104 sessions,
1,370 action responses, 104 manifests, 416 evidence responses, 105 observations,
nine status responses, 103 terminal metric summaries and 103 validator summaries;
zero discrepancies. Victory signatures are excluded from regenerated equality
because replay uses a fresh private signing secret.

Full regression: **372 passed**, three warnings, 283.14 seconds, with three stress
seeds. Warnings come from deliberately malformed objects in tamper/reference
tests. This includes all 2,187 complete-world physical replays for D4/P1/R1 and
D5/P2/R2, 24 D/P/R reference profiles, controls, arbitrary solver-oracle comparisons,
HTTP terminal-only metrics, serialization/tamper rejection and legacy baselines.
A final focused gate after telemetry/model-boundary changes passed **45 tests**
(two full-prior cases deselected). CLI D5/T3/P1/R1 seed17 generate/qualify/solve/replay
passed, including qualification of all 2,187 worlds. CLI solve is the existing
omniscient physical solver; the separate reference policy proves public-information
winnability. Lockfile, whitespace and focused Ruff checks passed. CI adds explicit
coupled-family CLI and container smoke cases.

The [paired ten-run pilot](rich-investigation-model-matrix.md) is the next empirical
gate. No paid model evaluations were made in this implementation.
