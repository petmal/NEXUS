# Overall quality review — 7 November 2026

This review followed the path from generating a world to scoring an attempt.
The largest problem was a baseline that could make an efficient player look
better than an alleged mathematical minimum. Two other paths could accept
internally inconsistent research records.

| Finding | Correction and evidence |
|---|---|
| The private solver reported the length of every scientific witness as optimal. | A generated `staged-repair-v1` world (seed 0, T0/D0/P1/R1) has an 11-action reference plan. The trimmer is already at the first requested settings; omitting that action still wins in 10. A winning replay supplies `plan_action_count`. The separate `optimal_action_count` is null unless the planner establishes a minimum. The 10-action counterexample alone does **not** prove 10 is minimal. |
| Generation output could report both an optimum and an action budget of zero for an unlimited world with a positive physical cost. | The CLI reads the starting allowance from world state and labels family bounds by what they establish. An interference control at seed 107 has a 12-action minimum at both R0 and R2: the CLI now says `unlimited` and `12` respectively. |
| An audit could verify even when its binding disagreed with the compiled world, or when a free observation was counted as a committed action. | Verification checks the bound versions and generation metadata, strict JSON turn/count types, committed turns, and capture coverage. Regression fixtures replace metadata **and recompute file checksums**, so they exercise semantic checks. Concurrent checkpoints also preserve one journal entry per turn without copying the whole prefix on each write. |
| The receipt validator could accept the code for a “won” response while its performance report said “failed.” | A disagreement, impossible counter, or receipt inconsistent with the terminal status is now a protocol error. It cannot become a success or a scored model failure. A wrong candidate for a consistent won response remains a normal incorrect answer. |
| Retrying an action from Python could return caller-modified data. Reusing an export directory could mix evidence from two worlds. | Requests for a committed turn return independent response objects. Export now requires a new or empty episode destination; a batch checks all destinations before generating the first world. Existing operator files are preserved. |

The [agent instructions](../../AGENTS.md) now describe the actual code boundaries,
profile-specific disclosures, research claims, release bindings and offline checks.
They replace the initial prototype roadmap, which still described the HTTP server
as future work and gave one family's rules as universal. The local documentation
check now covers heading links from that file as well.

## What this changes for existing results

The fixes do not change world transitions, legal actions, action prices, target
laws or victory conditions. Retain historical model results with their original
source. **Recheck a derived efficiency comparison** if it used the old private
solver's plan length as an optimum on a family without an independent proof.
The staged-repair example is not evidence that any model's receipt, or the
separately audited 12-action F11/F12 minimum, was wrong. A stored bundle still
needs its recorded source to verify; a successful audit does not authenticate the
provider, certify a model's private reasoning, or rerun world qualification.

## Verification and reproduction

On runtime `07d7a19764de9e661a61b68297a8133fefaff9a454cf043d1d0bf28d4838ae88`:

| Check | Result |
|---|---|
| Source-bound qualification (`make qualify-release`) | All 7,203 public-policy repair cases passed receipt and replay checks. P0 and P1 then won in 14 and 15 actions. |
| Current matrices (`make preflight`) | All 56 cross-axis conditions and 32 fresh/anchor rows passed. Compared with the previous reports, only source identity and elapsed time changed. |
| Distribution and documentation (`make package`, `make check`) | Clean wheel and source-distribution installs passed, as did Ruff and the local Markdown checks. |
| Targeted regressions | The shorter staged-repair witness wins in the engine. Corrupted bindings and contradictory finalization replies are rejected. Retried observations are independent, overlapping checkpoints replay once per turn, and occupied exports preserve existing files. |

Use `make test-full` for the unit/integration collection and `make stress` for
cross-seed properties. These checks run offline. No paid model trial was part of
this review; keep the final-source canary separate from mechanical verification.
