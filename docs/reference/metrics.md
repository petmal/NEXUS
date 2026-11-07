# Reading NEXUS metrics

Start with one attempt. Join its harness record to its world and configuration, identify the schema, then interpret the fields. A terminal game report describes what happened inside the world. Provider tokens, request time, model settings, tool-call limits, submission validation and outages belong to the harness. They cannot be reconstructed from game actions alone.

## Select the schema before extracting fields

| Terminal `performance` discriminator | Read this field contract |
|---|---|
| `$schema` ending in `performance-v6.schema.json` | [Legacy transformation worlds](../../schemas/performance-v6.schema.json). Field descriptions include units and baselines. |
| `$schema` ending in `performance-scientific-v1.schema.json` | [Scientific controller worlds](../../schemas/performance-scientific-v1.schema.json). Includes field calibration and controller submissions. |
| `version: mission-performance-v1` | [Ontology mission report](../../schemas/performance-mission-v1.schema.json). Read its `ontology` and family `certificate`. |
| `version: mission-performance-v2` or `mission-performance-v3` | [v2 decision fields](../../schemas/performance-mission-v2.schema.json); [v3 decision and evidence records](../../schemas/performance-mission-v3.schema.json). Dispatch on the actual version, including for archived data. |

Earlier legacy contracts remain in [schemas](../../schemas). A missing object, an unknown version and a measured zero are three different cases. An active session has no terminal performance report. A `null` budget means uncapped **inside NEXUS**; a null first-submission statistic can mean no such submission occurred. Do not fill either with zero.

## What each group measures

| Fields | Readout and common pitfall |
|---|---|
| `terminal_status`, `termination_reason`, `goal_satisfied`, `physical_goal_satisfied` | World outcome, reason where reported, and physical target at closure. Reaching a target with no action left for `finish` is possible. An issued receipt and an accepted answer are separate observations. |
| `theory_level`, `discovery_level`, `planning_level`, `resource_pressure`, `axis_version`, `ontology`, `experimental` | Identify the condition and family. Supplement absent labels from the bound episode/config; a profile number has no universal scale. |
| `actions_used`, `initial_action_budget`, `budget_remaining`, `action_counts` | Accepted actions and the world allowance. Legacy reports split `probes_used`, `move_actions`, `wait_actions`, `take_actions`, `drop_actions`, `operate_actions` and `finish_actions`. A charged preview or unchanged operation is still an action. |
| `invalid_actions`, `failed_finishes`, `duplicate_requests`, `protocol_conflicts` | Distinguish rejected requests, accepted but unsuccessful checks, replayed identical requests and stale/conflicting ones. They are not interchangeable error counts. |
| `goal_leaf_count`, `satisfied_goal_leaf_count`, `unsatisfied_goal_leaves`, `unsatisfied_goal_conditions` | Legacy partial state at termination. Counted leaves are not a fraction of optimal progress; logical OR/NOT conditions matter. Unsatisfied conditions are not a repair plan. |
| `rooms_visited`, `room_revisits`, `reference_plan_move_actions`, `move_delta_from_reference_plan` | Distinct rooms, revisits and travel relative to one reference route. An alternative route can be equally valid. |
| `optimal_physical_actions`, `action_delta_from_physical_optimum` | Legacy exact shortest successful path **knowing the true world**; delta is actual actions minus that cost. A failed short attempt can have a negative delta. |
| `minimum_guaranteed_probes`, `guaranteed_policy_actions`, `probe_delta_from_guaranteed_minimum`, `action_delta_from_guaranteed_policy` | Legacy worst-case information and total-action guarantees over worlds compatible with public evidence. Deltas compare the observed run with those guarantees. A successful guess can beat a worst-case guarantee. |
| `resource_allowance`, `planning_dependency_action_cost` | Legacy extra actions above the guaranteed-policy cost, and measured overhead from the P3 delivery dependency. Use the family's own budget rule for newer worlds. |
| `certificate` | Family-specific proof data. Distinguish **exact minimum**, **lower bound** (at least this much is necessary), and **constructive upper bound** (one strategy suffices at this cost). A successful reference strategy alone proves no minimum. |
| `measurements_used`, `informative_measurements`, `target_reducing_measurements`, `redundant_measurements` | Readings, readings narrowing candidate worlds, readings narrowing possible task outcomes/signatures, and readings that do not narrow the worlds. An operation can advance the physical plan while yielding a redundant observation. |
| `target_classes_before_first_submission`, `target_count_meaning`, `first_submission_correct`, `controller_submissions`, `mission_submissions` | Remaining classes and actual submission history. For overlapping goals, different sets of accepted repairs are signatures; their count is not the number of remaining physical worlds. |
| `final_correct_field_values`, `field_value_count`, `final_port_correct`, `final_submission_correct` | Family-specific controller/mission results. A partially correct field vector need not win. Never substitute partial credit for receipt validation without declaring a new scoring rule. |
| `common_repairs_before_first_submission`, `first_submission_supported_by_evidence`, `measurements_establishing_guaranteed_repair`, `measurements_after_guaranteed_repair` | Whether a common repair existed, whether the **chosen** repair was supported, and measurements establishing/following resolution. Several surviving worlds can share a repair. |
| `decision_diagnostics` | Nested decision-by-decision account in v3. See below and the schema definitions for reading, evidence and submission records. |

The private `nexus solve` command reports the cost of its returned plan as
`plan_action_count`. A non-null `optimal_action_count` denotes a known minimum
for that world with its laws known. An unproven minimum stays null even if
the plan wins. Neither field measures the work of discovering a hidden law.

For service logs, `operator-summary-v4` records the world family and starting
allowance even if the attempt is still active. `repeated_build_submissions: null`
means witness analysis was unavailable; zero means it ran and found none. Some
older summaries labeled scientific controller worlds `legacy`. For those records,
recover the family and allowance from the bound world before pooling runs.

## Evidence at the moment of a decision

For an eligible submitted build, let **W** be the set of worlds still consistent with public observations **before** feedback on this submission. Let **A** be the subset accepting the build. If A equals W, the build is **guaranteed**; if A is nonempty but smaller than W, it is **compatible**; if A is empty, it is **contradicted**. **Ineligible** means there was no physically eligible decision to assess. These labels say what the evidence permits, not what the model privately believed.

The v3 report includes `remaining_worlds`, `accepting_worlds`, `winning_set_signatures`, `common_repairs`, submissions and their turns, the final evidence and `escape_classification` (supported win, compatible win or no win). It also distinguishes passive/intervention readings, measured contexts, no-signal readings, the first intervention and first available guaranteed repair. Where enabled, the private operator report adds a reading timeline and witnesses such as a remaining alternative or an earlier contradiction. See the [diagnostic types](../../src/nexus/ontology/diagnostics.py). Unsupported analysis means “unavailable,” not “compatible win.”

**A real example:** in the F05 supplied-solution control, a local reference execution won in 5 of 8 actions. The v3 report recorded zero measurements, eight remaining worlds, four distinct winning-set signatures and one common repair. All eight worlds accepted the chosen repair. It was a supported win even though the player never identified a unique mechanism. This is an engine example, not a model trial.

## Measuring a detour

For supported **disclosed** planning/interference worlds the operator can compute an exact remaining physical cost after each accepted action. If the initial minimum is 12 and, after 3 actions, at least 10 more are needed, the trajectory now needs at least 13. Its `excess_actions` is 1. A 12-action budget is infeasible at that point; an 18-action budget still leaves room. If no continuation exists at any budget, the cost is unavailable as a finite number.

The report names `initial_minimum_actions`, `minimum_remaining_actions`, `accepted_actions`, `first_budget_infeasible_turn` and `first_unreachable_turn`. Check `available` and `reason` first. This diagnostic is private during play. It accounts for physical actions including `finish`, not thinking time, provider limits or the cost of learning hidden laws.

For publication, preserve the raw family report, schema/version, terminal status, receipt verdict, trace and the harness stop. See [research methods and audit limits](../research-guide.md) before deriving a cross-family score.
