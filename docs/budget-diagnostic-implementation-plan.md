# Implementation and resume checklist

Starting commit: `178f59b9219b57dc34cdbedb3555fa93109e1aa4`.
Design: [budget-diagnostic-design.md](budget-diagnostic-design.md).

## Phases

1. **Semantics and proof fixtures** — define typed submission/evidence diagnostics;
   add independent support-count and live trace cases from the pilot patterns.
   Acceptance: no classification relies on undisclosed truth except the explicitly
   separate physical-success predicate; failed ineligible finishes preserve belief.
2. **Integration** — attach decision metrics v3, private extended lifecycle logs,
   separate receipt classification, and strict named +6 generation profile.
   Acceptance: default game/other ontology behavior unchanged; extended logs cannot
   enter active player responses; read-only shutdown; reject unsupported profiles.
3. **Diagnostic matrix and guide** — eight paired executions with exact model
   configurations, source-bound preflight and verified example experiments for
   original cells. Acceptance: all eight generated, qualified, won and replayed;
   each pair differs only in budget condition; original matrix unchanged.
4. **Review, compatibility and release** — independent focused review; repair
   qualification proof/conformance before refreshing its complete source binding;
   focused tests plus existing fast/slow/stress gates, packaging and CLI smoke;
   update Docker preflight and CI. Publish to the existing PR with lease protection.

## Resume state

- [x] Inspect baseline code, latest pilot findings, repository and skill guidance.
- [x] Record design, scope and critical proof obligations before edits.
- [x] Implement classifications and proof cases.
- [x] Implement named budget profile and operator lifecycle diagnostics.
- [x] Validate matrix and document original experiments.
- [x] Review, refresh qualified release after gates, run regression tests.
- [x] Prepare feature-branch publication; track exact revision and image CI in PR 6.

Do not infer a provider stop reason from NEXUS state. Do not treat passive-only
experiments as enough for seeds 438/463/493/542. Do not mark a successful guess as
evidence-supported. Do not skip the repair source binding after Python changes.

## Completion evidence

All 678 collected tests have passing partitioned coverage; see
[validation](budget-diagnostic-validation.json). Seven sanitized observed action
traces reproduce the pilot classifications. Ten numeric guide experiments pass
live execution. Both independent review findings are repaired with regression
tests. Default budgets and original matrix seeds are unchanged; v2 metric parsing
is retained. All 3043 independently checked dynamics reference nodes are unchanged
after rebinding shared source changes. The repaired source qualification, wheel,
eight-row budget preflight and both original matrix preflights pass.

Build the feature head with its OCI revision and require the in-image budget
preflight before model calls. Current publication/CI status is recorded in
[PR 6](https://github.com/petmal/NEXUS/pull/6); this document intentionally does not
embed its own future commit hash. No paid model execution or MindTrial behavior
change is part of this work.
