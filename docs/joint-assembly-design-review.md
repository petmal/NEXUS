# Independent design review: joint inference and component assembly

Scope: read-only design review and independently executed finite oracle. No repository files changed. The parent remains responsible for implementation, full live conformance, and final qualification claims.

## Recommendation

Proceed with the 432-world confounded two-component design, with explicit local slope quality requirements and the full nine-input joint-function goal. This has a small, exact, independently checkable information barrier. It is substantially better specified than a single hidden compatibility bit or calibration prefix. It still does not establish that Astra will fail or that all mental solution paths require deep cognition.

Use the assembly/preparation cross-rotation as a separately described state-tracking requirement. Its public, deterministic nature makes it straightforward to reason about and qualify; it is not itself unknown scientific coupling. A later extension can replace this with latent physical state, but that is a different and considerably larger policy proof.

## Concrete finite design

Arithmetic is modulo three. A world contains `(a,b,s,t,h,r)` with a,b,r in 0..2, s,t in {1,2}, and h one of four public primitives: sum, difference, product, squared-left-plus-right. There are 432 worlds.

Physical joint law:

`P(x,y) = h(s*x+a, t*y+b)`

Confounded public observations:

- B channel: `s*x+a+r`.
- C channel: `t*y+b-r`.
- Joint channel: `P(x,y)+r`.

All x,y range over 0..2. Thus there are 15 informative observation classes. No separate zero-reference exposes r. Both local channels and joint observations constrain one common world, with no mandatory experiment order. The public evidence must explain that these are displays and that the physical response differs from the display.

The calibrated control uses r=0 in observations. It need not change the physical world or target. T2 discloses h, T3 discloses only the complete bounded primitive prior, and T0 supplies the complete usable construction.

The final goal must be disclosed as two simultaneous requirements:

1. Both component slopes equal the true local slopes, determined from first differences of the local responses.
2. The assembled response matches P for every one of the nine x,y input pairs.

The first condition is a real local quality contract, not a hidden preferred parameter spelling. Without it, some whole-function equivalents would validly use different local slopes. If the intended product only cares about whole-device function, do not add this constraint solely to inflate difficulty; in that alternate mission, all worlds have a four-reading certificate and some product worlds can be solved using only joint observations. For the approved component-assembly story, preserving both local contracts is appropriate, provided it is completely public.

All three phase settings are locally valid once the corresponding slope is correct. The assembly law distinguishes phase choices globally. A correct local check therefore does not certify the overall build.

## Independently executed results

Oracle: `joint-independent-oracle.py`, sibling results `joint-independent-results.json` in the task scratch directory. It uses literal primitive tables and direct arithmetic, not production law functions or inference tables.

The full mission has 96 distinct acceptance signatures. Seventy-two signatures cover three worlds each; 24 cover nine worlds each. Behaviourally equivalent accepted builds remain legal.

| Profile | Exact actual-outcome certificate | Public greedy readings | Local-only closure |
|---|---:|---:|---|
| T3/D4 confounded | 4 for product/squared-left-plus-right; 5 for sum/difference | 5–7 | Never supports a full mission |
| T3/D3 calibrated | 4 for all worlds | 4–6 | Never supports a full mission while h is unknown |
| T2/D4, sum disclosed | 4 | 4–5 | Supports every world: offsets cancel |
| T2/D4, difference disclosed | 4 | 4–5 | Never supports a full mission |
| T2/D4, product disclosed | 3 | 4–6 | Never supports a full mission |
| T2/D4, squared-left-plus-right disclosed | 4 | 4–5 | Never supports a full mission |
| T2/D3, sum/difference disclosed | 2 | 3–4 | Supports every world |
| T2/D3, product/squared-left-plus-right disclosed | 3 | 3–4 | Supports every world |

The certificate gives an omniscient chooser any subset of the 15 actual outcomes and asks when a common complete winning decision first exists. It is an exact lower bound on positive measurement evidence along that world, including zero readings. It excludes finish-feedback and physical action costs; it is not an adaptive policy optimum or a cognition guarantee.

Greedy policy chooses the next query by smallest largest posterior bucket, then smallest sum of squared bucket sizes, then query index; it stops at a common mission decision. For T3/D4, 69 worlds need five readings, 321 need six, and 42 need seven. The exact same policy must be used if these numbers are stored in generated metadata.

For T3/D4:

- All local readings leave ten incompatible mission signatures in every local-outcome bucket.
- All joint readings still leave two or six incompatible signatures in every joint-outcome bucket.
- B plus joint resolves product and squared-left-plus-right worlds, but not sum/difference worlds.
- C plus joint resolves product worlds only.
- Consequently the sum/difference rows demand all three evidence channels; product rows legitimately allow a channel-omission shortcut. Preserve these as distinct, labelled conditions rather than calling every operator equally deep.

There is no uniform claim that confounding strictly raises every seed's certificate: squared-left-plus-right and product remain at four in T3. The matched controls should measure whether additional ambiguity actually increases work.

## Finish guesses and scope

The existing DecisionAudit was separately run over the independent observation rows and all 96 mission acceptance masks:

| Reading budget | Finish guesses | Maximum successful world mass /432 |
|---:|---:|---:|
| 0 | 1 | 9 |
| 1 | 1 | 9 |
| 2 | 1 | 27 |
| 0 | 2 | 18 |
| 1 | 2 | 18 |

These are exact optimum masses under free setup and interleaved guesses in the audit's supported horizon. They are uniform-prior quantities, not selected-seed failure probabilities. The generic feedback upper bound uses at most three outcomes per measurement and at most nine worlds accepted by any build. A family-wide guaranteed policy needs more than three feedback actions, but this weak information bound must not be advertised as a full total-action optimum.

Every selected seed can always be guessed correctly by coincidence; classification must distinguish supported success from compatible success. A per-seed certificate cannot rule out lucky guessing.

## Physical preparation and engine conformance

A component can store a public signed slope and a public phase. Preparing one slot sets its slope and phase and rotates the partner's existing phase by the new phase modulo three. This is order-dependent and persistent. Its exact update must be disclosed. From a known initial state, two preparation operations can reach every desired pair by compensating the first phase for the second rotation; never claim this known cross-effect adds an unknown-law inference barrier.

Qualify and replay the complete preparation–assembly–finish trace, including recovery after a wrong but nonterminal finish. Test that:

- every accepted build is reachable;
- swapping preparation order generally changes the outcome;
- every new preparation updates the partner exactly once;
- the public observation reports the new phase state;
- the episode remains recoverable within the advertised allowance;
- any ineligible finish supplies no latent truth information;
- eligible rejection removes all worlds accepting the submitted build;
- probes do not commit preparation or assembly;
- measurements after preparation are either baseline readings or a known invertible adjustment to one of the same 15 classes;
- no error, preview, status, cached reading, or detailed goal-check result reveals additional truth.

Do not introduce a local-pass/fail probe without expanding the proof alphabet. A binary local-slope check immediately reveals a slope in one probe and can reduce the certificate. Do not return a vector of intermediate gate values in a single reading while claiming each reading has three outcomes.

Keep the mission comparison against true physics and local constraints separate from inference caches. A corrupted inference table must not change what wins.

## Suggested ten-run structure

Seed numbers below assume the explicit Cartesian order in the oracle; revalidate if production selection changes.

| Run | Seed | T/D | Role |
|---:|---:|---|---|
| 01 | 338 | 0/0 | Instructions and construction control |
| 02 | 338 | 3/3 | Calibrated matched control |
| 03 | 338 | 3/4 | Sum, five-reading certificate, greedy seven |
| 04 | 365 | 3/4 | Difference, five-reading certificate, greedy seven |
| 05 | 428 | 3/4 | Product, four-reading certificate, greedy six; channel omission allowed |
| 06 | 395 | 3/4 | Squared-left-plus-right, four-reading certificate, greedy seven |
| 07 | 395 | 3/3 | Second calibrated match; certificate need not change |
| 08 | 338 | 2/4 | Deliberate cancellation/shortcut control |
| 09 | 365 | 2/4 | Known operator, remaining joint nuisance inference |
| 10 | 365 | 3/4 +6 budget | Recovery/budget diagnostic paired with 04 |

Do not treat different r values on the same base world as distinct structural coverage. They mostly relabel observations. Include all four primitive families and explicitly tag their shortcut profiles. These rows test mechanistically established differences; the adjective 'challenging' remains an empirical hypothesis until model results arrive.

## Modularity and qualification gates

Keep the four primitive functions, public observation channels, acceptance signature, and preparation state transitions as distinct pure functions. The existing ontology interface is sufficient; no engine-wide adventure quest or inventory dependency framework is needed for this PoC.

Store immutable observation/acceptance masks once per profile and maintain only per-session posterior and public build state. Use bitsets to make exact posterior updates and common-goal checks inexpensive. Run exhaustive subset qualification offline; do not repeat it in ordinary generation.

Matrix preflight should bind certificate data to the actual code/version, public prior, legal query alphabet, and mission. It should fail if any purported hard row has a supporting certificate below its advertised minimum or an omitted-channel closure supports the mission. Each row also needs supported public-policy win, budget accounting, full replay, and correctly classified recovery/guess behavior. Only after these checks should the YAML be recommended for a paid pilot.

## Implementation disposition

The production world order is `(s,a,t,b,h,r)`, whereas the independent exploratory
oracle used `(a,b,s,t,h,r)`. The exploratory seed numbers above are historical, not
the runnable matrix. The equivalent production rows and every claimed shortcut are
requalified in `joint-assembly-matrix.json` and `joint-assembly-preflight.json`.
The reproducible literal-table oracle is committed as `ontology/assembly/proof.py`,
with `scripts/joint_assembly_oracle.py` as its entry point.
