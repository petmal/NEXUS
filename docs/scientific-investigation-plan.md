# Scientific investigation implementation and resume checkpoint

Branch: `feat/theory-prior-axis`, private `petmal/NEXUS`, PR #6. Never modify main
or publish to MindTrial. Local baseline `9f916384`; remote baseline `307e9f6f`.
Their tested trees match; publish through Git data with an expected-head lease.

## Phases

1. Research and semantic decision record (design document). **Recorded.**
2. Standalone finite-family proof: independent oracle, adaptive/fixed comparison,
   dependency/transfer/goal-leakage checks, shortcut baselines. **Passed.**
3. Fresh read-only proof review. **Passed; limits incorporated in design.**
4. Integrate declarative models, stock semantics, unlimited resources, operational
   controller, generated laws and player-safe documentation in existing sessions. **Complete.**
5. Add v2 generation selection, qualification, reference execution, terminal
   science telemetry and timing. Preserve legacy behavior by default. **Complete.**
6. Run focused semantic/property/API tests, full regressions and cold/warm
   performance comparisons. Independently review the integrated implementation. **Passed.**
7. Commit/publish focused stages; document supported cells, limitations and a
   roughly ten-cell nonzero-axis real-model matrix with diagnostic supplements. **Prepared and locally verified.**

## Required checkpoint contents

After every phase record commit, exact command/results, next action and unresolved
risks here. Keep proofs and design in git. Experimental scratch outputs are not
deliverables. No model/API spend is needed for deterministic local validation.
The host's credit/free-usage scheduling is not controllable by this repository;
small committed phases allow safe resumption whenever execution stops.

## Current unresolved technical questions

- Real-model difficulty remains unmeasured. The bounded shared-response family is
  scientifically coherent but enumerable. Run the paired pilot after release.
- R0 eventually permits goal enumeration; retain explicit certificate scope and
  first-submission telemetry. Do not claim winning necessarily proves inference.
- Existing repository gates are pytest and configured Ruff; no established
  type-check or coverage gate. Do not silently claim those gates passed.

## Checkpoint: proofs and integration

- Semantic design published as remote commit623555c6 (local f3489b9).
- `scripts/scientific_investigation_poc.py` independently verifies18 family cases;
  output in `docs/profiling/scientific-investigation-proof.json`.
- Bitmask solver agrees with tuple oracle and15 arbitrary small random problems.
  Initial largest-case cold solve0.031s versus tuple0.037s; repeat queries reuse
  the immutable problem cache. No parallel framework is justified at this scale.
- Integrated ordinary take/probe/operate, stock copying, declarative controller,
  unlimited R0, CLI version selection, exact all-truth qualification and terminal
  diagnostics. Legacy default remains unchanged.
- Focused74-test gate passed in9.84s; prior57 legacy tests passed in32.44s.
- Independent integration review found goal/stock/resource/certificate tampering
  gaps, missing-stock exception, and omitted R0 null fields. All fixed with
  regression coverage.

## Final implementation checkpoint

- Proof/solver published as remote `ad69ba1a` (local `686ec8e`).
- Immutable scientific schema published as remote `dd6564d8` (local `0b20ac4`).
- Integrated runtime published as remote `5c7f056b` (local `6e6139ee`), matching
  tree `2beef5b0d4a90cebdc3cddf52b4244a1c9378aae`.
- Full regression: `NEXUS_STRESS_SEED_COUNT=3 uv run --frozen pytest -q --durations=12`:
  **323 passed**, 2 warnings, 243.37 seconds.
- Final human CLI/display gate: **10 passed**, 67 deselected, 4.53 seconds.
- All ten primary pilot cells qualified: **2,928 complete-world policy replays**.
- Live HTTP D5/T3/P0/R0 seed 7: 16 actions, first submission correct, won,
  separate command-line receipt validator exit 0.
- Fresh-process cold generation maximum: **0.12435 seconds**, excluding imports,
  over ten D3-D5/T1-T3 seed-7/23 benchmark cases. Largest family: 576 worlds,
  132 representative policy leaves. Exhaustive qualification remains unchanged.
- Independent final review: all raised findings resolved; no remaining blocker
  within reviewed scope. Leaf equivalence additionally checked over 1,600 worlds.
- GitHub CI run `37886563711` passed at remote `5c7f056b`, including extended
  tests, cross-seed stress, CLI smoke and container smoke.
- Full evidence, caveats and commands: `docs/scientific-investigation-results.md`.
- Primary matrix: `docs/scientific-investigation-model-matrix.{md,json}`; all axes
  nonzero. Diagnostic controls are explicitly outside the ten primary runs.

### Resume/publication procedure

The final documentation/display commit follows the integrated runtime commit.
Publish its exact tree through Git data with an expected-head lease, preserving
the remote ancestry; do not force-push the imported local ancestry. Verify local
and remote tree equality, update PR #6, and inspect CI without claiming an
unobserved pass. No further design approval is required. The next user-run stage
is the real-model pilot, not more optional local testing.
