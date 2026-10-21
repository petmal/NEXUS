# Coupled-memory implementation judgement

Reviewed 2026-10-21 against the working tree at `/workspace/scratch/5185b9a844b2/NEXUS`. Scope: the new coupled-memory package, coupled preflight and matrix, shared discovery adapter changes, runtime acceptance, public evidence channels, tests, and Docker/CI additions. No repository code was modified and no further agents were used.

## Verdict

**No blocking correctness defect found in the inspected implementation.** It implements the narrowed experimental design accurately. Runtime victory checks all future histories; the offline proof independently establishes equivalence of the finite reader signatures and full behavior classes. The new matrix's selected truths exhibit both causal directions of feedback, while reports correctly avoid a universal difficulty claim.

I recommend adding the concrete beyond-horizon regression below before completing this phase. This is a test gap, not a current acceptance bug: I executed the reproduction and the current implementation passed. Remaining full-regression, installed-image, legacy release refresh, documentation, YAML export, and final-source-bound preflight are still release gates, as already identified by the parent.

## Verified correctness and scope

- `laws.equivalent()` traverses the reachable product of two deterministic state machines, compares their initial displays, and follows all three pulse transitions. It includes the empty history and has no four-pulse cutoff. `accepted()` actually calls it; victory does not rely on the finite signature table.
- `proof.prove()` independently computes scalar transitions and observations over all 384 × 135 legal states. Its partition refinement uses the correct per-program transition offsets. It compares the resulting full acceptance masks with the reader-derived masks, not merely the number of classes. The complete row partition also determines the finite inference posterior correctly.
- Single/pair/triple certificate enumeration is exhaustive after deduplicating identical outcome masks. Deduplication does not lose any useful intersection. The six-reading tree plus the 336-class ternary information lower bound proves the stated probe-only minimax optimum. Fixed-panel and mixed probe/finish bounds are explicitly scoped; no total-action optimum or mandatory reader count is claimed.
- The binary/five-symbol controls use unique bounded signatures. Uniqueness implies distinct full behaviors for all 384 programs, so their information bounds do not depend on assuming a nonexistent longer-horizon equivalence theorem.
- Failed eligible finishes remove the accepting class of the attempted construction. Ineligible finishes and stock copies do not exclude a hidden law. Repeated failed finishes are idempotent evidence. The shared action path makes assembler previews public construction previews, not correctness queries.
- Both `probe` and `operate` on the reader return the same final trit from an isolated reference history. Only `operate` commits the reading payload. Default settings are legal and public. Invalid settings are checked against public grammar and rejected atomically.
- Shared `canonical_query()` and `read_world()` hooks preserve the old representation and uncertainty behavior. Their truth selection, initial settings, defaults, and budget formulas remain unchanged. The new family remains opt-in; the CLI/generator default is still `shared-response-v1`.
- Active HTTP/action responses do not expose performance/posterior data. The new runtime requires a single session. The existing hidden finalize endpoint irreversibly ends the attempt before returning diagnostics, so it does not provide a recoverable mid-game oracle. Source-binding covers all installed NEXUS Python files, and preflight separately binds the matrix and proof digests and rejects source changes during the run.
- The pilot validates role-to-T/D/R consistency through `Cell`, pairs T0/T2/T3/R0 by seed and actual mechanism, verifies distinct contrast dynamics/behaviors, and checks diversity of feedback structures, predictive state sizes, and encoders. The source-bound report remains explicitly experimental.

## Independently executed checks

1. **Beyond-reader-horizon acceptance:** replaced the transition/display functions in a temporary in-memory patch with two finite machines that agree on every one of the 120 legal queries but differ on the fifth pulse. Production `equivalent()` rejected the pair. No source edits were made.
2. **Complete legal reader surface:** on a seed-95 R0 episode, issued every legal query through the actual session as both `probe` and `operate`. All 240 readings matched the rule evaluator; each probe preserved the carrier payload; every active response had no performance data; replay reproduced the final canonical hash.
3. **New feedback witnesses:** independently replayed both counterfactual recurrences using direct formulas. Every returned witness's actual and ablated values matched. There are 372/384 memory-to-transfer witnesses within the reader horizon and 384/384 material-to-memory witnesses. All six selected T3 seeds—95, 47, 121, 159, 286, and 7—have both. The twelve absent witnesses must remain nullable/explicitly scoped; they do not establish absence of the causal edge over all future histories. The parent has acknowledged this scope and the selected-matrix gate checks both witnesses.

I did not rerun the parent's full focused suite, full regression suite, or installed container build. Their reported earlier passes are not represented here as independently executed results. The ablation additions were inspected and independently replayed after they were introduced; the final complete proof/preflight should still be rerun on the finished sources.

## Concrete regression gap: protect all-history acceptance

The current `test_equivalent_encoder_spellings_are_accepted_but_partial_transcripts_are_not` uses two programs that agree only on the first 12 entries of the reader table. A mistaken replacement of `equivalent()` by comparison of **all 120** finite reader outputs would still pass that test. Moreover, for this fixed grammar, the proof deliberately guarantees that those 120 entries separate the full classes; ordinary in-grammar examples cannot expose the regression.

Add a small synthetic finite-machine test that preserves equality throughout the reader horizon but differs immediately afterward. The following is the exact tested approach, adapted to pytest and strengthened to call the mission predicate. Clear the equivalence cache before and after temporary monkeypatching so synthetic answers cannot contaminate later tests.

```python
def test_acceptance_rejects_difference_beyond_reader_horizon(monkeypatch):
    from nexus.ontology.coupled_memory import laws

    left, right = laws.PROGRAMS[:2]

    def transition(program, state, pulse):
        return (min(state[0] + 1, 5),)

    def display(program, state):
        return int(program == right and state[0] == 5)

    laws.equivalent.cache_clear()
    try:
        with monkeypatch.context() as patch:
            patch.setattr(laws, "INITIAL", (0,))
            patch.setattr(laws, "advance", transition)
            patch.setattr(laws, "display", display)

            assert all(
                laws.read(left, query) == laws.read(right, query)
                for query in laws.QUERIES
            )
            assert not laws.accepted(laws.Truth(program=left), right)
    finally:
        laws.equivalent.cache_clear()
```

The counter has six states and saturates, so this test terminates even when the equivalence checker explores all continuations. The test is about the published acceptance contract, not the particular reservoir formula.

## Remaining release checks

- Promote the complete legal-query probe/operate check to a compact regression if practical; the current offline proof covers all program/query values, while the live public-policy tests exercise only the selected queries.
- Retain an executable check of the ablation witness values and selected-seed admission, including a known missing-witness program as a negative control. Do not replace nullable witnesses with an unconditional all-program claim.
- Refresh the existing source-bound legacy qualification release only after all Python changes are final, then run the full regression and installed-image gates. The current code changes necessarily invalidate its old source hash; this is a known pending release task, not a new runtime defect.
- Rerun and save the coupled proof and matrix preflight on the final sources, and ensure the final documentation/YAML describe `[6,9]` fixed-panel bounds, the three-reading actual-outcome certificates, T2's at-most-25-action blind-build shortcut, and the absence of empirical difficulty calibration. The proof deliberately does not establish bounded calibration-first policy optimality.
- Keep the operator proof/preflight artifacts separate from player evidence. Existing endpoint projection is sound; the pending packaging/export work must preserve that boundary.

No speculative redesign, additional parameters, reduced sensor alphabet, persistent planning stage, or generic engine change is recommended by this implementation review.
