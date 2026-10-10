# Scientific branch maintenance review

## Design and scope

Preserve generated worlds, public evidence, difficulty, receipts and replay while
removing duplicated compilation and making the two network ontologies easier to
extend. Existing versioned family identifiers remain the compatibility boundary.
This is preparation for the real-model pilot, not a difficulty redesign.

Use explicit immutable network apparatus definitions (coordinates, instruments,
initial tuning) shared by model/runtime/generation projections. Separate fresh
world construction from scientific certification. Cache only seed-independent
policy bounds keyed by D/P; do not cache mutable episodes, secrets or random draws.
Keep law evaluators, priors and family-specific certificates explicit. No dynamic
plugin loading, universal ontology DSL, new dependencies or legacy solver rewrite.

## Implementation and validation plan

1. Capture deterministic episode, manifest, complete trace and terminal-summary
   hashes before changes across the two network families and shared baseline.
   Review engine/model/protocol boundaries and exact-head CI.
2. Extract reusable network world construction and public apparatus declarations;
   remove coupled generation from resonant generation; cache coupled policy bounds.
   Preserve stock/machine insertion order and identity encoding exactly.
3. Repair verified interface/integrity issues, make shared factor data immutable,
   and optimize posterior bookkeeping only with exact-oracle coverage.
4. Compare compatibility hashes and generation timings; run focused tests, full
   regression including stress, lock/lint checks, and independent review.
5. Publish focused commits to `feat/theory-prior-axis` / PR #6, inspect exact-head
   CI, and record results here. Do not merge main or run paid model evaluations.

## Decisions and checkpoint

- Starting local revision: `8579499`; published revision: `16d2197`.
- Starting CI run 38058250544 completed successfully.
- Network generator currently recomputes policy leaf witnesses per episode;
  resonant generation additionally constructs and discards a complete coupled
  episode. These are measured optimization targets.
- CLI human help omits resonant meter configuration even though the manifest
  correctly exposes it; repair without changing player manifest content.
- Implementation, independent judgement and local validation complete.
- Local code commits: `ce20710` (replay/control fixes), `7564644` (ontology and generation).
- Matching remote code commits: `dbc5a7f` and `bc0c37f`; source tree
  `94b1f302248ccf91106e13b3e3911edb70e0d997`. Publication and exact-head CI are
  tracked by [PR #6](https://github.com/petmal/NEXUS/pull/6).

## Findings and changes

| Finding | Resolution |
| --- | --- |
| Resonant generation compiled a coupled episode, evidence and physical bound twice on cold starts, then discarded them | Build its own validated world directly through `generator/network_world.py`; preserve the coupled RNG stream for paired G laws and the existing receipt identity encoding |
| Coupled policy-bound witnesses repeated for every seed/R setting | Cache the integer bound for the twelve supported D/P layouts; fresh episodes, secrets, evidence, metadata and plans remain individually allocated |
| D4/D5 specimen preparation, movement and turn-based identifiers duplicated across scientific policies | Share `NetworkWitness`; each resonant stage starts at R0 with a fresh specimen and explicit turn offset |
| Apparatus definitions scattered across construction and coordinates | Add immutable public definitions in `ontology/network.py`; retain compatibility exports at old import paths |
| Resonant evidence generated and parsed a coupled JSON bundle before rewriting it | Compose the public theory dictionary and evidence bundle directly; rendered evidence remains identical |
| Cached factor rows claimed immutability but exposed mutable dictionaries | Read-only mappings over tuple rows; derive belief dimensions from the compiled tables |
| Saved replay trusted event payloads and turn labels despite checking state hashes | Check successor turn and JSON-normalized events; reject tampered measurement results, preserve JSONL tuple/list compatibility and non-consuming observations |
| Human CLI help omitted meter configuration | `actions` respects the scientific-family option/environment; `play` derives the contract from the actual episode |
| Scientific settings dispatcher advertised only the shared-response type | Correct its union signature and reject mismatched truth types explicitly |

The general review covered generation, prior/policy compilation, engine transitions,
model boundaries, public projections, CLI, replay, terminal metrics and the physical
solver. No generated-world privacy failure was found. This is a scoped review, not
an assertion that every possible defect has been excluded.

One verified limitation is deferred: the scientific perfect-knowledge solver and
network witness planner assume the generated chain topology. Adding arbitrary
scientific maps requires graph-aware routes, updated physical bounds and qualification;
the current schemas alone do not establish support. An added shortcut can make the
existing physical solver's reported optimum wrong. Current generated profiles have
no such shortcut. No topology semantics are changed in this maintenance patch.

## Measured generation performance

24 sequential fresh processes, interleaved before/after on the same host and Python
3.14.8. Three seeds (7,17,23) per family/D at T3/P1/R1. Each process generates once
cold and once warm, then plays the reference policy successfully. Imports are excluded.
The baseline is local revision `8579499`, identical in tree to published `16d2197`.

| Family / D | Cold before → after | Warm before → after |
| --- | --- | --- |
| Coupled D4 | 0.798 → 0.812 s | 251.4 → 0.48 ms |
| Coupled D5 | 0.779 → 0.773 s | 241.5 → 0.43 ms |
| Resonant D4 | 1.305 → 0.648 s | 252.1 → 0.59 ms |
| Resonant D5 | 1.238 → 0.665 s | 234.7 → 0.46 ms |

Values are medians, not performance guarantees. Coupled cold cost is effectively
unchanged; resonant cold generation falls about 46–50%. Warm generation avoids the
repeated witness sweep. A new process still computes its priors/policies once, and
a new D/P layout computes its own physical bound. Random seeds remain independent;
no episode precompilation or cross-process cache is required.

Raw results: `branch-maintenance-benchmark.json`. Reproduce a case with:

```sh
PYTHONPATH=src uv run python scripts/scientific_investigation_benchmark.py \
  --family resonant-network-v1 --case 5 3 7
```

## Extending the network ontology

| Concern | Owner |
| --- | --- |
| Versioned public bench coordinates, instrument names, initial tuning | `ontology/network.py` |
| Validated specimen, public contract and hidden-law schemas | `models/network.py`, `models/episode.py` |
| Exact law and instrument semantics | `engine/network.py`, `engine/resonance.py` |
| Fresh world allocation and chain-layout specimen/movement planning | `generator/network_world.py` |
| Complete priors, inference policies, bounds and certificates | Family generator and qualifier modules |
| Player evidence | Family docs modules; shared theory/bundle projection |
| Public action descriptions, family routing, terminal inference diagnostics | Actions/manifest, generator/qualifier dispatch, protocol metrics |

The ontology module contains no hidden truth, solver imports or executable law
callbacks. It is intentionally a narrow reusable boundary, not a universal plugin
registry. Changing apparatus names alone does not implement a new instrument: add
its engine behavior, public control description, measurement prior and witness proof.
Changing specimen state requires a typed schema and matching episode-family validation.
Changing relationships requires an evaluator/prior and predictive-identifiability proof.

For a changed game contract, introduce a new family version; keep old golden worlds
stable. Then qualify legal domains, public identifiability, physical reachability,
resource bounds, stage composition, deterministic replay and active-play privacy.
Update each explicit family dispatch site and add a small cross-family regression.
The current shared-response and legacy ontologies retain their own simpler models.

## Validation checkpoint

- 197 before/after cases across all supported network D/T/P/R combinations at seeds
  7/17, plus five shared-response controls: compiled episode, manifest, full trace and
  terminal-summary hashes match. Includes reference actions and victory receipts.
- 21 representative baseline cases retained in a versioned golden fixture.
- Focused gate: 111 passed, four slow cases deselected; one expected malformed-model
  serialization warning. Covers replay event/turn tampering, JSONL round-trip, public
  controls, cache isolation, factor arithmetic and posterior oracle checks.
- Final 197-case compatibility rerun after all edits also has zero mismatches.
- Final focused gate after the independent-review correction: 31 passed, three
  slow CLI cases deselected, no warnings. Tests are separated into generation
  maintenance, replay integrity and CLI coverage.
- Independent judgement found no generation, privacy, difficulty or ownership
  regression. Its valid scalar-type finding is fixed: replay compares canonical
  JSON bytes, rejecting integer-to-boolean/float substitutions as well as altered
  readings, while accepting tuple/list differences from legitimate JSONL I/O.
- Focused Ruff and Pyright pass; frozen lock verification and whitespace checks pass.
- Full regression: **440 passed**, three expected malformed-model serialization
  warnings, **306.96 seconds**, with `NEXUS_STRESS_SEED_COUNT=3`. Includes both
  families' full-prior/factor-witness qualification and legacy stress profiles.
  The subsequent replay scalar-type correction and test-file separation are
  covered by the final 31-test focused gate above.
- No dependencies changed, no paid model calls, no main merge. Container smoke
  remains part of the branch CI rather than a locally claimed Docker run.
