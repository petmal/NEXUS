# History-coupled investigation — design and proof contract

Status: implementation in progress. Operator-only document. Existing families,
seeds, action charging, receipts and player observations retain their contracts.

## Why this experiment

The latest pilot produced 10/10 evidence-supported Astra wins. One repeated seed
beat the public reference policy, so a stable efficiency weakness is unproved.
Current transfer missions end in one submitted counterprogram. This experiment
adds actual specimen construction, delayed effects and correlated hidden states.
It tests a different demand; no numerical model failure rate is predicted.

## Bounded artificial world

`history-coupled-v1` is an opt-in trusted ontology. A specimen has two visible
registers x,y and two hidden physical registers H,K, initially all zero. Internal
coordinates are h=aH and k=bK modulo 3, with unknown a,b in {1,2}. Four generated
functions are composed from coefficient, addition, square and bias primitives:

    F_i(u) = c_i * (1 + (u + s_i)^2) mod 3
    c_i in {1,2}; s_i in {0,1}

Four ordinary apparatus operations act in order on the current specimen:

- vek: h <- h + F_0(k)
- nol: k <- k + F_1(h)
- tor: x <- x + F_2(h+k), THEN k <- k+x (new x)
- sen: y <- y + F_3(k+x), THEN h <- h+y (new y)

All arithmetic is mod 3. There are 256 composed laws and four orientations: 1,024
joint worlds. The last two operations disturb earlier hidden properties. A
correct visible pair alone is insufficient. The player must carry the seal in
the array with physical (H,K,x,y)=(1,2,1,2), then finish successfully. Every winning
procedure is accepted. A public history of at most eight pulses reconstructs
private state; no hidden register is serialized or placed in a public hash.

The surface reader reports x,y. Two intervention readers temporarily set physical
H=1 or K=1 on a copy, apply tor then sen to that copy, and report its x,y. Neither
changes the specimen. Operate/probe pulse responses also reveal x,y and MUST count
as evidence. Probe remains a one-step counterfactual; it never advances the real
history. A normal anneal operation restores the specimen to its initial state,
including its history, at the ordinary action cost. It is available in every R
profile and permits recovery; this is not a session reset or special R0 action.

The same finite prior, equations, sequential update order, reading convention,
history limit, recovery operation and exact goal are disclosed in player files.
T3 conceals the generated functions and orientations; T0 supplies them and a
winning procedure. Initially only paired T0/D0 and experimental T3/D5 profiles
are admitted. Other axis levels await separately proved semantics. P0/P1 change
only topology; R0 is unlimited and R1/generous differ only in action allowance.
No measurements or verbal justifications are mechanically required.

## Claims to prove, and limits

1. All 1,024 worlds have reachable goals within the public history bound; enumerate
   all 81 states per normalized law independently. The rejected first design had
   256 impossible worlds because (h,k)=(2,2) was unreachable. Do not reintroduce it.
2. Passive histories, pulse previews and all free observations are invariant under
   a,b. H-reader data are invariant under b; K-reader data under a. The corresponding
   orientation rivals have disjoint winning histories. Thus both intervention
   channels are necessary for a guaranteed first submission in T3. Rejected
   eligible finishes are additional evidence and must be modeled; the statement
   does not forbid lucky guesses or elimination by repeated failed finishes.
3. Exhibit same visible state/different future response, noncommuting order, and
   delayed disturbance. Minimum procedure length is recorded per world, not
   confused with necessary inference depth. Preliminary BFS gives 2–6 pulses;
   this is NOT a universal deep-reasoning guarantee.
4. Compute exact overlapping winning-history sets over ALL words of length <=8,
   not just reference solutions. Preserve complete correlated worlds. Exhibit
   a posterior where coordinate-wise modal parameters fit no surviving world.
5. A public-only investigator must finish every world within a measured bound.
   A small witness query pool may prove an upper bound; any longer legal query
   still updates the exact posterior. Fixed-panel shortcuts and omitted channels
   must be reported honestly. No claim of mandatory adaptive rounds.
6. Information resolution refers to an available fresh preparation procedure.
   The shared diagnostic name `guaranteed_repair` is qualified explicitly in the
   certificate. Anneal makes that procedure physically available from any key
   state, with one additional action. Count that action in reference allowances.

## Extension and performance boundaries

Keep laws, data-only schemas, public evidence, inference, reference policy,
qualification and runtime in separate modules. Reuse engine transactions,
protocol/replay and mission-performance-v3. Add a reusable public artifact-history
tracker only if its contract is independent of this ontology; never alter the
legacy applied-dose tracker semantics. Runtime acceptance follows actual history,
not apparatus settings or probe-returned history.

Compile bounded immutable transition tables for 256*81*4 transitions. Bitset
posteriors and exact winning sets are seed-independent. Keep caches bounded;
profile cold generation and terminal summarization before adding persistent
assets or parallelism. No new dependencies, GPU, worker pools or source evaluation
are justified for this size. Failed-finish exclusion removes all accepting worlds
for the actual eligible history, including equivalent procedures.

## Validation and rollout

Independent scalar oracle first; compare every transition and all reachable
states, then runtime, public-only policy, canonical replay, transactional invalid
actions, probe nonmutation, privacy, finish classifications and controls. Review
all public contracts in fresh context. Run existing fast/proof/extended gates,
legacy preflights, packaging/actual-image CI. Matrix pairs unknown/known laws,
normal/generous allowance, orientation rivals, and distinct gate compositions.
Keep the transfer sentinels as regressions. Experimental results, not labels,
decide whether this family should be expanded. Selective revision remains gated.
