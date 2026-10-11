# Causal mechanism laboratory: implementation results

## Delivered architecture

`causal-mechanisms-v1` is an opt-in trusted ontology adapter. Existing axis-v1,
shared-response, coupled-network, resonant-network and categorical-chain worlds
remain supported. Default family selection is unchanged. Engine, session, action
accounting, replay, receipt and HTTP protocols did not need a new state mechanism.

New worlds compose unknown input routing, a latent specimen mode, transition and
response graphs, and an instrument offset. The player prepares independent fresh
specimens, interprets offset-bearing readings, and predicts six held-out physical
responses across context and treatment-order changes. Exact public histories retain
all mutable causal inputs; private laws reconstruct the hidden mode. No secret
state is placed in player-visible payloads or low-entropy state hashes.

The registry owns lazy runtime/generator/qualifier targets and standalone action
references. Payload registration remains data-only; an episode cannot select an
arbitrary Python import. New-family code lives under `ontology/causal`.

## Supported settings and proof scope

| Cell | Public information | Proven reference guarantee |
|---|---|---|
| T0/D0 | Six exact physical predictions | Configure and finish |
| T1/D1 | Exact laws, unknown initial specimen mode | One untreated reading |
| T2/D2 | Known forms; coefficients, offset and initial mode unknown | Untreated-only strategy, at most four readings; at least three needed for a guarantee |
| T3/D5 | Complete bounded structural prior | At most six readings; untreated data alone cannot guarantee mission identification |
| T1–T3/D0 | Sufficient experimental records supplied | No new measurements required |

P0/P1 and R0/R1/R2 are supported; unsupported cells fail explicitly. D2 publicly
restricts the response form to 0/1, because form 2 otherwise introduces a construction
requirement. All coefficient/state combinations under that disclosed form remain
admitted. A named response draw preserves other same-seed mechanism components;
T2/D2 is not an exactly matched-truth ablation of T3/D5.

The T3 prior contains 648 worlds and 113 joint mission answers. Complete untreated
data produces 126 observation classes, 120 still mission-ambiguous. The remaining
six classes are retained: this is a guarantee over the prior, not a claim every
selected world individually needs treatment. A 568-experiment subset witnesses
identifiability; every other legal history/setting remains supported by exact joint
posterior inference. There is no hidden filtering of T3 truths.

The P1 reference action upper bound is 40, including specimen preloading, movement
and final submission; R1 allows 48, R2 allows 40. R0 removes resource limits while
retaining a specimen's public two-pulse capacity; ordinary take supplies a fresh
copy. All six exact mission sensor protocols are publicly outside the measurement
contract, including sensor operate. This deliberate transfer requirement must be
included in the task contract, not treated as an accidental tool restriction.

D5 proves construction is needed for a guaranteed strategy over the prior. It does
not prove an optimal discovery→preparation sequence or an adaptive advantage over
every fixed panel. D4 remains unsupported. CLI solve is an omniscient physical
solver; scientific winnability is separately proved by the public-information policy.
The entire family is marked experimental until real-model difficulty is measured.

## Validation

- Independent arithmetic matches all finite graph transition/response states;
  one-step agreement implies every legal bounded history by induction.
- All 648 admitted truths win through the real player-only interface, within the
  advertised budget, with exactly reproducible JSON trace replay. First submissions
  have one remaining joint target class and are correct.
- Tests cover all supported T/D/P/R cells, arbitrary off-witness measurements,
  failed whole-vector submissions, immutable previews, capacity rejection,
  specimen isolation, stock renewal, drop/take, duplicate idempotence, HTTP privacy,
  metadata/evidence tampering, CLI/service selection, and persistence.
- All 197 prior episode, manifest, trace and terminal-summary snapshots are unchanged.
- Independent design and implementation reviews completed. Findings fixed: D2's
  construction confound, evidence/spec consistency, metadata/resource alignment,
  scoped D5 claims and registry-owned CLI help. No remaining material blocker.
- Focused Ruff, new-module Pyright, frozen lock and whitespace checks pass.
- CLI generate → qualify → solve → replay passed. Container execution is covered
  by the extended CI smoke definition; local container execution was not performed.

Final regression counts and publication checkpoint are in
[the implementation plan](causal-mechanisms-implementation-plan.md).

## Performance

Complete immutable transition/response tables replace repeated graph evaluation
while preserving the central declarative graph semantics. There are 72 law tables,
each with 81 mode/point rows. Exact posterior masks and policy subproblems have
bounded caches; generation still accepts arbitrary seeds.

Six interleaved fresh-process runs compare interpreted graphs with compiled tables
on this host, imports excluded. All public reference runs win with identical action
counts. Interpreted cold generation takes 6.29–8.41s; compiled takes 0.66–1.37s
(4.6–9.6× faster in the paired samples). Warm generation takes roughly 2–4ms.
Concurrent regression load was not controlled, so these are indicative timings,
not a latency SLA or a precise warm-speedup claim. A quiet initial smoke measured
6.89s versus 0.67s cold and about 1.8ms warm. See
[raw data](causal-mechanisms-benchmark.json) and `scripts/profile_causal.py`.
No CPU/GPU parallelism or additional runtime dependency is justified at this scale.

Operator logs include compile/generation timing and terminal calibration,
post-identification measurement and first-submission ambiguity counts. Active play
receives no posterior diagnostics, reference policy, certificate or private truth.

## Remaining empirical question

This implementation tests a different reasoning burden rather than increasing the
number of worlds. The prior is smaller than the earlier resonant family; enumeration
remains valid. It does not establish that at least half of evaluated models fail.
Use the [ten-run matrix](causal-mechanisms-model-matrix.md) without external Python,
then a frozen fresh-seed panel. Separate scientific failures from preparation,
interface, provider, token-budget and receipt-extraction failures.
