# Follow-up: bounded handoff qualification

2026-10-21. Scratch-only review. No repository implementation changes.

## Decision

The **four-coordinate local modulo-5 candidate**, target `(1,2,1,2)`, has a
concrete pool of **24 truths passing the requested two-commit handoff exclusion
through 20 counted actions** under the full 256-law prior. This is worth carrying
forward to final qualification. It does not yet establish all admission criteria,
an optimal full-policy cost, universal non-decomposition, or model hardness.

The qualifying truth indices are:

`200–207, 216–223, 232–235, 248–251`.

The other **232 truths have a replayed positive handoff witness** within the same
bound. Thus no truth remains undecided for the question “does at least one of
the tested prefixes yield a shortcut on this truth's observation branch?”
Some individual prefix/truth combinations for those already-failing truths
remain capped; that does not affect their exclusion or the 24 passing truths.

## Exact scope

For every fixed word over the four committed actions of length zero, one, or two
(21 words), supply for free:

* the scalar current-state readout;
* the complete four-action non-mutating, one-step probe panel;
* both at the initial state and after each committed prefix operation.

Partition the full prior by the complete transcript. For every resulting belief,
search for a fixed suffix of at most `20 - prefix_length` actions. Operation
readouts are ignored. Repeated finish is legal: successful worlds terminate,
failed worlds continue the fixed suffix. A negative result means that even this
generous measurement oracle cannot yield a bounded blind continuation for that
belief. It does not mean no longer continuation exists.

For each of the 24 truths, **every one of its 21 relevant beliefs was exhausted
with a negative result**. These results also imply exclusion through 18 actions.
They are not inferred from a capped search, residual law count, or one reference
trajectory.

The decisive five formerly unresolved queries for truth 219 were:

| Committed prefix | Belief size | Suffix horizon | Exhaustive memo states |
|---|---:|---:|---:|
| `(2,1)` | 32 | 18 | 11,044 |
| `(3)` | 128 | 19 | 16,707 |
| `(2)` | 128 | 19 | 22,028 |
| `(0)` | 128 | 19 | 25,795 |
| empty | 128 | 20 | 57,058 |

These searches finished within a 100,000-state cap and jointly resolved the last
unknowns for all 24 candidates. The final row proves the complete initial-panel
belief with first gain 2 has no blind success-aware continuation through 20. An
additional exhaustive search extended this to **22 actions**, visiting **502,740
memo states** in about 50 seconds under a 1,000,000-state cap. Thus this belief's
blind continuation cost is at least 23. It covers all truth indices 128–255 and
is retained in the same cache and certificate manifest.

## Important exclusions

Previously proposed local-modulo-5 truths 67, 93, 127, 173 and 255 **fail** this
handoff requirement. Repeated failed finish is essential to many witnesses.
For example, truths 93 and 127 have a successful branch after prefix `(0,1)`
with suffix:

`2,2,2,3,finish,3,3,finish,3,3,2,2,2,3,finish,3,3,finish`.

All positive witnesses were independently replayed with a scalar implementation
that directly updates the coordinate tuple, rather than using compiled transition
tables: **688 world/prefix witness replays passed**.

## Remaining admission work

1. Check unrestricted pre-finish-supported minimum at least 8 for each selected
   truth, and the desired minimum committed progress. This review did not replace
   those thresholds with the more favorable handoff result.
2. Pair the 20-action negative with an adaptive comparison. A reported global
   constructive upper bound of 39 does not alone show a cost advantage over this
   restricted controller. Useful evidence would be a replayed branch of a global
   strong policy costing at most 20 for each selected truth, or a full strong
   upper bound below the blind lower bound. State which comparison is proved.
   The main agent is constructing short supported branches with safe public
   fallbacks on every off-path observation; if replay proves all branches finish
   within the generous 64-action budget, that is a valid strong-policy comparator
   even if the selected branch is much shorter than the worst case.
3. Keep private operator selection separate from the 256-law public epistemic
   contract. If the truth-selection support is made public, requalify that
   conditional prior. The passing pool is concentrated: all 24 share gains
   `(2,2,*,*)` and first power 2. It is not yet a diverse matrix of public
   structures/goals. Vary public targets/initial states and re-run the same gates.
4. Preserve whole-action runtime conformance, hidden-state projection, scalar
   interpreter checks, source identity, exact success, and terminal-only
   diagnostics from the earlier review.

## Other candidates examined

The three-coordinate rich-bit candidate, modulo 5, target `(2,3,4)`, has 4,096
laws. With the analogous handoff horizon 18 and a 2,500-state cap per query,
2,932 truths have positive shortcut witnesses. The remaining 1,164 have no
positive witness but at least one unresolved prefix; none is certified against
all prefixes. The two large initial-panel beliefs, containing 3,072 truths in
total, do have exhaustive blind negatives through 18. These partial results are
preserved; they do not support deep admission.

For the local modulo-3 candidate at horizon 18, truths 0, 5, 17 and 35 fail via
prefix `(2,1)`. An eight-law coordinate-sign symmetry gives a useful 19-action
blind lower bound for some beliefs, but the main agent rejected this candidate
and the modulo-5 results above do not rely on that argument.

## Reproducible artifacts

Directory: `/workspace/scratch/5185b9a844b2/stateful-poc`.

* `review_local5_handoff.py`: complete initial capped sweep and witness storage.
* `review_local5_certify.py`: raises the five decisive caps, proves the initial
  panel negative through 22, validates all positive witnesses with the scalar
  interpreter, and emits the final certificate manifest.
* `review-local5-certified.json`: parameters, public prior size, qualifying truth
  indices, gains/powers, all 21 negative-prefix records per qualified truth, and
  exact node counts.
* `review-local5-handoff-results.pkl`: retained complete query results, beliefs,
  positive action words, and negative searches. The JSON sweep summary is only
  the initial sweep; use the certified JSON or pickle for final status.
* `review-rich-handoff-results.pkl`: retained rich-bit positive/negative/unknown
  query results, without treating unknown as negative.

Reproduce from the scratch directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python review_local5_certify.py 4 5
```

Deleting the local5 result cache first reproduces the initial sweep followed by
the five 100,000-cap queries and the 1,000,000-cap initial-panel query at 22.
The certificate wrapper asserts exact width,
modulus and target, and checks the expected qualified set.

Local dynamics source SHA-256:
`9a33e6d370151387ae213cd3e6c25c70039cb49702ecb03ca46ddf97781cf447`.

Rich-bit dynamics source SHA-256:
`2f593af97072cd773774dee51664a97071f5e0a3504dbccbba3d2619a85902f1`.

The blind solver is deterministic finite reachability with a decreasing integer
horizon. Its only pruning is the exact maximum per-law physical distance plus
finish, dominated no-op removal, and previously completed identical subqueries.
It includes successful-world removal on finish and all four committed actions.
Ignored scalar readouts cannot influence its fixed suffix, by construction.
