# Ontology modularity implementation results

Implemented on `feat/theory-prior-axis`, PR #6, without a main merge.
Baseline local revision: `39d051b`; corresponding remote revision:
`eaeb8f5cbecd08109569c14228334cf7b2bfd8f6`.

## Delivered boundaries

- Scientific runtime, mission, manifest, generation/qualification and physical
  reference-plan selection moved behind an explicit built-in catalog.
- Existing scientific wire formats retained through a compatibility adapter;
  axis-v1 execution unchanged.
- Public-only belief construction and normalized measurement interfaces support
  flat and factored inference. Generic trace accounting no longer identifies
  particular instruments or law families.
- Validated domain artifact/stock/spec/truth envelopes permit new property
  vocabularies without legacy shape/polarity requirements. Public roles cannot
  load private truth payloads. Cross-family/version loading fails closed.
- Generic mission acceptance and terminal diagnostics support a prediction board
  without controller/port semantics. Existing performance projection preserved.
- Immutable dependency graphs and trusted exact primitives compose a categorical
  ontology. Session, replay and receipt need no categorical-specific branch.
- Added author guide, mathematical proof, exhaustive conformance tests and a
  separate experimental generator. No external tools added to evaluated agents.

## Proof and regression evidence

| Gate | Result |
|---|---|
| Independent pre-implementation finite proof | All 36 depth-2 and 216 depth-3 worlds |
| Live public-policy wins and JSON replay | All 252 admitted worlds |
| Independent posterior oracle | Every legal categorical experiment/outcome, plus rejected targets |
| Legacy compatibility comparison | 197 cases; zero episode, manifest, trace or terminal-summary changes |
| Focused scientific regression | 78 passed |
| Full suite, `NEXUS_STRESS_SEED_COUNT=3` | 451 passed, 3 pre-existing serializer warnings, 304.88 s |
| Post-format conformance/compatibility/replay | 36 passed |
| New-module Pyright / focused Ruff | Passed |
| Frozen lock / whitespace | Passed |

The full suite was run on a stable source tree. An earlier run overlapped adapter
review edits and lazy imports, so it was stopped and is not counted as validation.
No paid model evaluations were run.

Independent review caught and verified fixes for three issues in the new PoC:
keyed episode identity to prevent seed enumeration; loaded apparatus arity/range
validation; and correct submission metrics when a board starts configured.
Shared integer normalization is intentionally preserved rather than tightening
existing control behavior.

## Performance

Sixteen sequential fresh-process measurements compare baseline and refactor,
interleaving revisions across D4/D5, seeds 7/17, T3/P1/R1. Imports are excluded;
each process generates cold, generates warm, then executes its reference policy.
Raw data: `ontology-refactor-benchmark.json`. All sixteen references won.

Median milliseconds across the two seeds:

| Family/profile | Cold before | Cold after | Warm before | Warm after |
|---|---:|---:|---:|---:|
| Coupled D4 | 757.885 | 778.417 | 0.513 | 0.461 |
| Coupled D5 | 781.232 | 726.662 | 0.461 | 0.453 |
| Resonant D4 | 659.201 | 657.679 | 1.106 | 0.637 |
| Resonant D5 | 640.643 | 623.925 | 0.497 | 0.474 |

This small sample shows no material generation regression; it does not establish
a broad speedup. Existing bounded compilation caches remain. The refactor removes
a redundant resonant artifact copy, copies only the mutable sample for other
scientific transformations, keeps inference imports out of runtime resolution,
and caches immutable categorical graphs/worlds/predictions with explicit bounds.

## Scope and limitations

The categorical PoC demonstrates compositional dependencies and a different
property vocabulary. Four/six readings suffice, but the mission has only six
prediction classes at either depth. It is not a calibrated D profile, a proof of
optimal action cost, or evidence of greater LLM difficulty. Its explicit
experimental certificate must be excluded from production D/T comparisons.

Plugin installation/discovery, arbitrary text-valued configuration and generalized
physical search are not implemented. New families register trusted code and
validated schemas explicitly. Existing resonant graph structure is described,
while its published evaluator remains unchanged. Family-specific qualification
remains necessary when increasing reasoning complexity.

See `ontology-author-guide.md` for the concrete extension workflow and
`ontology-implementation-plan.md` for the resumable checkpoint.
