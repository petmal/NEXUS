# What the original compositional pilot asks the player to do

**Operator guide: contains selected-world spoilers. Do not include in model tasks.**
The original eight-cell pilot is defined in [structural-model-matrix.json](structural-model-matrix.json).
Run 02 is a different family; the compositional runs are 01 and 03–08.

## The shared problem

You are confined to a counterphase array. To open the exit you must treat one seal
so it gives zero response in **four specified situations across two contexts**.
The same four treatment settings must work in all four situations. Take the seal
and a reusable survey specimen, carry them to the array, investigate, apply the
treatment to the seal, and successfully call `finish`.

The world uses only digits 0, 1 and 2; arithmetic wraps modulo 3. A survey lets you
choose an input `(x,y,z)`, a context, and treatment settings `(a,b,c,d)`, then read
one output digit. The hidden system has three connected mechanisms, each chosen
from four disclosed operations: addition, subtraction, multiplication, or
square-the-first-input-plus-the-second. One mechanism changes between contexts;
the other two and their wiring stay the same. Both contexts are available from
the start. There is no required order of experiments.

`a` and `b` intervene inside the system; `c` shifts its final output, while `d`
adds a further shift in context 1. “Passive” below means `a=b=0`, not that the
experiment costs no action. Changing only the known output shifts does not reveal
the hidden internal response to `a` or `b`.

To make one ordinary experiment: configure stage with
`[context,x,y,z,a,b,c,d]`, **operate** stage on the survey, then probe sensor.
Those are three actions. Configure alone does not prepare a specimen; probing
stage only previews. Each example below is an illustration, not a complete
guaranteed solution from the full prior.

## Original runs, in plain language

| Run | What is hidden in this selected world? | Verified example experiment | Challenge / baseline budget |
|---|---|---|---|
| **01**, seed 0, T0/D0 | Nothing needed for the mission: a valid treatment is supplied. | Apply the disclosed `[0,0,2,0]` with doser, carry the seal in array, then finish. No science experiment is needed. | Execution control; 8 actions; reference uses 5. |
| **03**, seed 0, T3/D5 | A **chain**: the first result feeds the second, then the third. Context 1 changes the first mechanism from addition to square-plus. | At input `(2,1,0)` with all trims zero, context 0 returns **2** and context 1 returns **1**. That difference is evidence of a changed mechanism. | Infer the graph and laws, then combine them into one repair. Passive data can suffice. 30 actions; reference uses 21. |
| **04**, seed 250, T3/D5 | A **fork**: two branches are computed separately and their results are subtracted. Context 1 changes the first branch from addition to subtraction. | At input `(2,1,0)` with all trims zero, context 0 returns **2** and context 1 returns **0**. | Infer how separate branches combine. Passive data can suffice; a two-reading positive certificate exists. 30 actions; reference uses 21. |
| **05**, seed 438, T3/D5 | **Reconvergent wiring**: the first result feeds the second mechanism and is also reused at the final mechanism. Context 1 changes the second mechanism from addition to multiplication. | Set `[0,0,0,0,0,1,0,0]`: the sensor returns **0**. This internal `b=1` intervention distinguishes this world from run 06, which returns 1. | Passive observations alone cannot identify a safe repair. Need a useful intervention and cross-context evidence. 30 actions; reference uses 24. |
| **06**, seed 463, T3/D5 | The same wiring pattern, but different mechanisms: context 0 ends in square-plus; context 1 replaces that final mechanism with multiplication. | The identical experiment `[0,0,0,0,0,1,0,0]` returns **1**, ruling out the run-05 alternative. | Same kind of intervention necessity as 05; a different changed mechanism and different required repair. 30 actions; reference uses 24. |
| **07**, seed 493, T3/D5 | Reconvergent wiring; the first mechanism subtracts, and context 1 changes the second mechanism from multiplication to addition. | Set `[1,0,0,0,0,1,0,0]`: the sensor returns **0**. Its passive-equivalent rival (world 498) returns 1. | Resolve an internal causal ambiguity, then use the evidence consistently when choosing the seal treatment. 30 actions; reference uses 24. |
| **08**, seed 542, T3/D5 | Reconvergent wiring; all three mechanisms multiply in context 0. Context 1 replaces the final multiplication with addition. | Set `[1,0,0,0,0,1,0,0]`: the sensor returns **1**. Its passive-equivalent rival (world 541) returns 0. | Distinguish how branches reunite after the context change, and reserve actions to apply the repair **and finish**. 30 actions; reference uses 24. |

The exact example outcomes are checked against both the compiled mechanics and
live configure/operate/probe actions in the test suite. Knowing a discriminating
query for one pair does not establish that those are the only remaining candidates:
the player initially faces all **615** admitted worlds.

**Run 02**, seed 219, is `coupled-dynamics-v1`, an older-family comparison with a
73-action budget (reference uses 40). Here pulses change two hidden specimen
components; history and order matter. A sample experiment is: use two fresh
surveys, prepare/pulse at `(1,0,0)` then `(0,1,0)` on one, and reverse that order on
the other; measure both at the legal non-mission point `(0,0,0)`, with reference
readings to correct sensor offset. This probes order-dependent dynamics. The
mission asks for eight predicted responses used as seal doses, rather than the
four-setting common repair of the compositional family. The experiment describes
a valid comparison, not a promise that this particular pair will distinguish
every world or return different values.

## Why 03–04 differ from 05–08

All six science runs start with the **same public grammar and uncertainty**; the
player is not told which topology or selected category it received. Each has
three mechanisms, so the distinction is not simply “more stages.”

For 03 and 04, sufficiently informative passive observations identify a usable
repair. For 05–08, even **every possible passive observation in both contexts**
leaves two worlds that demand incompatible repairs. No amount of extra passive
measurement resolves that ambiguity. The player must change `a` or `b` in a useful
way and examine the result. An unhelpful intervention can still fail to distinguish
the alternatives.

Runs 05 and 06 make this especially tangible: their complete passive behavior is
identical, but their sole winning treatments are `[1,1,0,2]` and `[1,1,2,0]`.
The internal intervention in the table separates them. Runs 07 and 08 have
analogous passive-equivalent rivals not selected as separate cells in this pilot.

One way to see the 05/06 distinction: write `q=x+y+a` and temporarily set output
offsets `c=d=0`. In context 0, run 05 computes `q*(q+z+b)` while run 06 computes
`q*q+q*z+b`. With `b=0` these are identical, even if `a` changes. At `q=z=0, b=1`,
they give 0 and 1. Thus simply “doing an intervention” is insufficient: the player
must choose one that exposes where an internal effect enters the system.

The qualification proves a lower bound of **at least three positive readings**
for 05–08, even when a query chooser knows the selected world; this excludes
short zero/one/two-reading certificates. It does not prove deep human-like
reasoning, a large minimum number of adaptive rounds, or failure of a particular
LLM. Guesses and rejection feedback are separate possibilities. Run 03 also needs
at least three positive readings under that audit, despite lacking the passive
obstruction; run 04 has a two-reading certificate.

The latest pilot's live escape counts were 7/7 for 03 and 04, then 4/7, 6/7, 5/7
and 4/7 for 05–08. These include interrupted runs in the denominator and include
one unsupported escape in 08 and one receipt mismatch after escape in 07. They
show the harder cells were more discriminative, but do not establish a monotonic
ranking or a clean scientific-reasoning failure rate.
