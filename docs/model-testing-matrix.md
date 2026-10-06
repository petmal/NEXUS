# Ten-run model calibration matrix

Run these **10 tasks per model** on `feat/epistemic-calibration` after the solver integration.
Difficulty is an ordinal prediction, not a calibrated success probability. D measures causal
inference/experiment design, P planning and delivery, R action pressure. There is no production
T axis yet. A single seed schedule is a smoke/calibration pass, not a leaderboard.

| Run | D/P/R | Expected relative difficulty (1–10) | What it tests |
| --- | --- | ---: | --- |
| 01 | D0/P1/R0 | 1 | Read direct evidence; execute and finish correctly |
| 02 | D1/P1/R0 | 2 | Infer an unseen context from evidence without probing |
| 03 | D2/P1/R0 | 3 | Resolve ambiguity with one informative probe |
| 04 | D3/P1/R0 | 5 | Two dependent transformations and informed probes |
| 05 | D4/P1/R0 | 6 | Choose informative auxiliary experiment; ignore distractor |
| 06 | D5/P1/R0 | 7 | Construct a diagnostic sample before probing the mission law |
| 07 | D5/P2/R0 | 8 | Same causal task with greater navigation/planning demand |
| 08 | D5/P3/R0 | 8 | Add cargo delivery dependency to the paired P2 world |
| 09 | D5/P3/R1 | 9 | Same P3 world, reduced allowance for exploration/mistakes |
| 10 | D5/P3/R2 | 10 | Exact guaranteed-policy budget; no extra exploration allowance |

The P3 prediction overlaps P2 because the added dependency can be easy for a model with good
state tracking. R2 is especially severe: the solver baseline knows topology, while a player may
spend actions discovering it. Failure here is not sufficient evidence of poor causal inference.
Prior observed D5/P3/R1–R2 failures motivate those cells; they do not establish a universal ranking.

## Seed and harness setup

Use `model-testing-matrix.json` as a neutral manifest, not as MindTrial-specific YAML. Sample one
fresh private integer seed at the start of the suite; use it for **all 10 cells and all models**.
Keep it out of player prompts/files. D0–D2 share a causal family; D3–D5 have distinct families.
Across P levels topology may differ; P2/P3 are the strongest matched planning comparison.
R0/R1/R2 must use the same seed to isolate resource pressure. Generate another fresh shared seed
when repeating the suite. Fresh seeds benefit from the promoted within-solve caches; persistent
cross-task episode reuse is not required.

For each row, start a fresh session/container and map its `environment` object into service
variables, replacing `${SUITE_SEED}` with the chosen integer. Leave `NEXUS_VERIFIER_SECRET`
unset for fresh private receipts. Keep service stderr/operator logs outside the player sandbox.
Use the same model sampling, reasoning/token budget, prompt, tools, and harness timeout policy
across all rows. Record model/version and settings. Do not reuse conversations across rows.

Keep the external tool-call ceiling comfortably above the environment budget plus setup/evidence
reads. Use a common ceiling of at least the maximum `recommended_tool_call_limit` from the private
generation metadata across the suite, plus any harness-specific setup/retry calls. Do not set it
from D/P/R alone. The built-in recommendation is action budget + evidence file count + 5.
Use generous, equal inference ceilings to isolate R; label tool/token/time exhaustion separately.
Generation startup needs a separate timeout from model play. Measure cold startup on your host
before choosing that timeout; the integration measurements are not a deployment SLA.

Example single task (substitute a privately recorded seed):

```sh
NEXUS_SEED="$SUITE_SEED" NEXUS_DISCOVERY_LEVEL=5 NEXUS_PLANNING_LEVEL=3 \
NEXUS_RESOURCE_PRESSURE=1 NEXUS_GENERATION_TIMING=true nexus serve-session
```

Call the normal `nexus request` player interface. After the model submits its final answer, run
`nexus validate` as the evaluator, including on abandonment or wrong-code attempts. Validation
irreversibly finalizes active sessions and writes terminal `performance` to stderr while retaining
the normal validation JSON on stdout. Do not call `/finalize` during play or expose it as a tool.

## Capture and interpret

Record exact success, terminal status, exit reason, cold generation seconds, model play seconds,
tool/token use, private seed and episode ID, code commit, and complete terminal performance-v3.
Retain the accepted trace and model transcript for failure analysis. Compare:

- Runs 01–06: evidence reading, causal ambiguity, experiment selection/construction.
- Runs 06–08: navigation, cargo handling and goal completion under forgiving budgets.
- Runs 08–10: same world under decreasing action slack.
- On failures: `unsatisfied_goal_conditions`, action mix, revisits, failed finishes, invalid actions,
  and remaining budget. Atomic false leaves are descriptive; OR/NOT conditions are authoritative.
- On wins: action/probe deltas against exact baselines. A negative delta on a failed run is not
  efficiency. A win below the worst-case guarantee may reflect favorable outcomes or guessing.

If most models fail 09/10 but succeed 06–08, inspect navigation and action pressure before adding
more causal difficulty. If 05/06 already separate models, prioritize the research T-axis at P1/P2
next. A T-axis run should be a separately versioned experiment; this matrix cannot validate it.
