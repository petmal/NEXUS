# Qualification design and validation

## Why a new optional family was justified

The existing repair family admits a universal short cancellation chain: a
reference reveals a; x=a reveals b; y=b reveals c and d; substitution constructs
the treatment without identifying r. Its three-round proof remains valid but
does not establish cognitively difficult inference. The matrix now explicitly
uses its linear, quadratic and cubic laws as controls.

An independent complete-query PoC examined `causal-mechanisms-v1`: 648 worlds,
113 target classes, 20,433 legal sensor queries plus three normalized reference
signatures. Exactly 162 worlds admit a two-reading certificate; 486 do not.
Every mission-order-sensitive truth admits a two-reading certificate, and all
targets are resolved by complete untreated/one-pulse data. The previous seed 7
already belongs to the at-least-three group. Selecting another seed could not
support the proposed conjunction of stronger gates. We did not relabel existing
worlds or weaken those gates.

The optional `coupled-dynamics-v1` extension uses the existing trusted ontology
registry, schemas, canonical engine, public protocol, exact receipt and replay.
It adds two hidden state components updated simultaneously. Routing, transition
form, response form, coefficients, initial state and sensor offset vary over a
fully disclosed product prior of 1,944 worlds. Eight mission responses define a
physical treatment for the carried seal. Direct measurements of those exact
protocols are publicly excluded; all other allowed experiments remain available
from the outset. This is bounded transfer, not open-ended theory invention.

Supported profiles are T0/D0 and T3/D5, P0/P1, R1. No intermediate T/D profile is
silently invented, and defaults/old families retain their behavior. The family
is experimental until model calibration. Numeric T/D values alone do not imply
cross-family difficulty equivalence.

## Exact audit and its limitations

The generic finite-observation audit works with target equivalence, not exact
latent-world identification. For a selected truth, each actual reading defines
the target-distinct rivals it fails to exclude. A certificate is a set of these
rival masks with empty intersection. Duplicate and dominated masks can be
removed without changing existence of a certificate. Exhaustive pairs and a
transposed third-query search prove the minimum through three readings, or a
lower bound of four. Found certificates retain original query indices.

Arbitrary fresh preparation is free in the audit, making its negative result
stronger. Any adaptive resolving path with at most three readings would itself
be a certificate, including a path selected by a truth-aware oracle. This is
not feedback-round complexity, psychological depth, or a necessity to observe
before a lucky victory. Failed-finish information is excluded from this specific
certificate and handled by a separate population bound.

All 4,674 normalized legal queries are included: sensor histories of length
0..3 at every bit point, excluding eight declared mission protocols, plus two
reference signatures that cover every history/point for that apparatus. The
prior has 585 target classes. Complete untreated data leaves all 1,944 worlds
target-ambiguous. Complete one-pulse data leaves 24 worlds ambiguous. Complete
two-pulse data resolves all targets. The selected six challenges have no
certificate of at most three readings. Only the separately tagged history case
needs more than one pulse when given every possible short-history reading.

The guess-inclusive bound uses at most 23 distinct physical submissions at
budget 73: at least two setup actions, then at least configure + operate + finish
for each distinct treatment. With at most k ternary readings, arbitrary
interleaved guesses yield at most 23*3^k successful target leaves. Assigning those
leaves the largest target equivalence classes is a relaxation. Their exact
uniform prior masses are 156/1944, 396/1944, 810/1944 and 1944/1944 for k=0,1,2,3.
Thus k<=2 permits success at most 5/12. Measurement/preparation costs are ignored,
so this is an upper bound, not an optimal policy. No nontrivial k=3 bound follows.
Assumptions: one non-resettable attempt, absorbing success, generic failure,
the documented public channels, no private-process or timing side channels, and
no cross-cell knowledge narrowing the prior. The bound is not a selected-matrix
success estimate.

## Selection, qualification and privacy

The machine-readable matrix separates compact adaptive controls, an execution
control, five broad structural cases and one history-transfer diagnostic. It
checks actual generated laws, world and target identity, transition/response/
wiring coverage, order sensitivity, untreated ambiguity, certificate lower
bounds and long-history ambiguity. It rejects duplicates, missing law branches,
unsupported profiles and incomplete qualification. Reports are atomically
checkpointed and bound to package and matrix digests; errors never leave an old
ready report in place. The saved-report verifier requires per-row qualification,
win and replay evidence, exact inventory/coverage, and current source identity.

The full prior remains the game's generation/disclosure prior. Matrix selection
does not filter it. Revealing the selected candidate pool invalidates the
full-prior interpretation and can reduce cases to one-query identification.
Selection and reports stay operator-only; fresh contexts are mandatory for the
paired control. The evaluator should report stratified outcomes, not pretend the
matrix estimates a population pass rate.

## Performance and maintainability

- Compile 72 immutable primitive tables, each with nine states and eight points,
  instead of repeatedly interpreting every history expression.
- Cache immutable observation partitions, target sets and public-policy choices;
  retain a separate belief mask per session.
- Use a smaller complete-enough query subset for constructive reference policies;
  use the complete legal space only for offline lower-bound qualification.
- Use integer bitsets, dominance pruning and transposed exclusion checks. Stream
  pair intersections instead of allocating quadratic pair storage.
- Cap generic input at 16 million outcome bytes; certificate search checks a
  finite deadline during preprocessing and search. Timeout is a failed audit,
  never a proof. Package compilation is outside this per-certificate time cap.
- Preserve ordinary action costs, reset policy and exact physical victory. The
  reusable committed-treatment tracker does not treat configuration as success.
- No new dependencies, multiprocessing overhead or GPU stack is introduced.

Generation logging reports compilation time; terminal diagnostics report
reference/insensitive readings, post-resolution measurements, and target classes
at first submission. Live player responses do not expose these diagnostics.

## Independent judgement

Fresh-context implementation review compared 7,206 random finite-problem cases
with an independent exhaustive oracle. It independently evaluated 56,112 legal
queries and all 15,552 mission responses, and won/replayed each selected challenge
through the public policy. No blocking mathematical/runtime defect remained.
The review identified stale-ready output on malformed matrix input; this was
fixed and regression-tested. Resource caps and saved-report completeness were
also strengthened. The failed-finish-inclusive bound was independently checked.

The committed [preflight](difficulty-matrix-preflight.json) is the authoritative
generated per-cell evidence. The [matrix guide](difficulty-model-matrix.md)
describes the image check, pilot procedure and interpretation. Structural
qualification is complete only when those gates pass; empirical LLM difficulty
remains uncalibrated.


## Final local validation

All **606 tests** passed in partitioned gates: 563 fast, 40 extended, two
three-seed stress tests and one Hypothesis determinism test. The extended gate
includes actual public-policy victory and exact replay for all 1,944 dynamics
worlds and all 7,203 existing repair worlds. Three existing malformed-object
warnings remain unchanged. The original repair proof and serialized witnesses
are unchanged; the complete package source manifest was requalified.

All ten cells passed both checkout and separately installed-wheel preflight,
with identical source/matrix digests. CLI generation/qualification/omniscient
physical solve/replay, HTTP privacy, save/load, focused Ruff, new-module Pyright,
frozen lock and whitespace checks passed. The omniscient CLI solve is not the
public-information investigator used for matrix qualification.

The checkout preflight took 43.82 seconds while regression tests shared the host.
This is offline qualification, not per-task generation. Docker/Podman is absent
in the local environment; actual-image qualification is included in full CI and
must also pass for the image used by MindTrial. See the
[validation record](difficulty-validation.json) and
[independent implementation judgement](difficulty-implementation-review.md).
