# Post-run classification and paired budget diagnostic

Status: implemented and locally validated on `feat/theory-prior-axis`.
Publication and actual-image CI are tracked in [PR 6](https://github.com/petmal/NEXUS/pull/6).

## Purpose and evidence

The 23-00-26 pilot produced 44 accepted answers but 45 live escapes. One successful
repair was not guaranteed by the collected evidence; one exhausted episode had a
correctly treated seal but no successful finish; another submitted a repair
incompatible with every remaining world. A single pass/fail label loses these
distinctions. Provider length stops, refusals and quota failures are separate
harness observations, not facts the NEXUS engine can infer.

## Contracts

1. Preserve exact live victory and receipt validation. Diagnostic labels do not
   award a win or change MindTrial's policy for validation on error.
2. Classify each eligible submission **before** incorporating its rejection:
   guaranteed = accepted by every evidence-compatible world; compatible = some
   but not all; contradicted = none. Ineligible physical submissions have no
   evidential rejection. Counts are finite support counts, not probabilities.
   A successful finish must not retrospectively make its own evidence sufficient.
3. Distinguish the final physical mission predicate, live escape, action
   exhaustion, evidence sufficiency and receipt match. Report observations about
   actions and information, never an assertion about a model's private reasoning.
4. Record measured contexts, passive versus intervention readings, the first
   intervention and when a guaranteed repair first became available. No signal
   from a seal is not a passive survey reading. Configuration without application
   is not a specimen change. Preview does not commit a treatment.
5. Bump only compositional decision metrics to `mission-performance-v3`; preserve
   earlier fields and other ontologies' metric contracts. Extended operator logs
   include a bounded evidence timeline at terminal completion or graceful service
   shutdown. Active public responses remain free of posterior metrics.
6. Extended mode records replayable accepted actions and an episode binding to
   private stderr. A graceful-shutdown snapshot does not finalize or mutate an
   active game. A hard kill cannot guarantee a final summary; the action journal
   and external harness stop reason are then required. No new player endpoint.
7. Add the named `diagnostic-plus6` budget profile, restricted to compositional
   T3/D5/P1/R1. `standard` remains the default and serializes existing episodes
   unchanged. Use generation metadata for the operator profile; public evidence,
   laws, seed mapping and initial physical state are identical apart from the
   disclosed action budget. Validate profile, budget, certificate and allowance
   together on compilation/load. Reject arbitrary budget edits.
8. The eight executions are four pairs: Gemini seeds 438, 493, 542; Grok seed 438.
   Each pair compares standard 30 against diagnostic 36 actions. Pin the exact
   prior model IDs/reasoning settings; fresh context and session for each execution;
   no external Python; same prompt, response-token limit and tool-call ceiling.
   This is a targeted diagnostic, not a population failure-rate estimate. One
   execution per condition cannot separate stochastic variation from a budget
   effect. Counterbalance order; do not supply this document or the seed guide to
   players. More actions may help but do not repair bad experimental design.

## Critical proof obligations

- Reconstruct the posterior from public measurements and physically eligible
  failed finishes only. Check support against an independently enumerated oracle.
- Exercise supported and unsupported wins, contradicted/compatible rejections,
  incorrect-room or missing-seal attempts, and correct state without finish.
- Check identical seed/truth/evidence/action semantics for each budget pair;
  replay the same public witness under both budgets and obtain identical actions
  and observations after normalizing only budget and terminal metadata.
- Ensure active HTTP responses/OpenAPI do not expose the operator report; shutdown
  is read-only; duplicate requests do not create extra committed journal entries.
- Preflight all eight executions on the built image, bind the result to matrix
  and installed source digests, and reject stale or incomplete reports.

## Decisions and non-goals

Use the existing finite-prior inference and ontology seams, not a second game
solver or a new plugin framework. Reuse compiled partition bitmasks when filtering
measurements: this is an exact optimization with an independent oracle test.
No game difficulty redesign, arbitrary budget override, model calls, provider
integration, GPU work, or changes to original pilot seeds are included.

The original run guide is operator material with spoilers. It will explain the
shared goal, the chain/fork controls (03–04), and the reconvergent worlds (05–08)
where all passive observations still leave incompatible repairs. Run 02 belongs
to `coupled-dynamics-v1`, not the compositional family.
