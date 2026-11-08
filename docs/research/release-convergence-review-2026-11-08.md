# Release review: from player input to verified result

Two supported player workflows failed on the model-revision family. Neither
failure was in the world laws, plan cost, receipt calculation or agent transport.

| Reproduction | Fix and regression |
|---|---|
| Generate a revision world with `consistency_check: readings`. In `nexus play`, enter the check request from its manifest. The console rejected it as invalid action JSON; the agent interface returned a reading-consistency result at turn zero. | Human help now shows the optional request only in episodes that disclose it. The console uses the same request type and session check. Tests cover enabled and disabled profiles, invalid input, the audit count and zero world actions. |
| Run `nexus actions --axis-version 2 --science-family model-revision-v1`. The family help tried to read an episode that did not exist and raised an exception. | Family-level help lists its actions without assuming a finish policy or offering assistance. A regression invokes the CLI for all 20 selectable scientific families. |

**Gameplay and accounting pass.** The private planner won all 26 fresh conditions,
all 56 cross-axis conditions and a legacy world. Each run included a future-turn
conflict and a retry of every committed action: 1,476 actions in 83 runs. Each retry
preserved the result and cost no action. Replay and the private audit agreed with
the live terminal state and receipt. These were mechanical runs, not model trials.

For the 16 fresh interference conditions (eight tight/relaxed pairs), a separate
calculation built the directed graph from the scalar guard and update laws. It
searched backward from the target and compared every finite distance and every
unreachable state with the production continuation calculation. All 250,000
state/condition comparisons agreed. Paired budgets reuse the same physical world;
these are not 16 independent samples.

**Independent confirmation.** Across the 26 fresh conditions, an assisted revision
world and a legacy world, the same public requests were run over HTTP and JSONL
on each of three paths: winning, using up the action budget, and stopping early.
All 2,377 normalized public exchanges agreed across the 168 sessions. Closing
JSONL left the unfinished world active; explicit HTTP evaluator finalization
marked it failed. Both outcomes verified against their respective audit bundles.
A separate loopback CLI run checked that a correct receipt passes, a wrong answer
after a real win fails, and an unfinished attempt supplies no receipt.

The wheel and source archive each installed cleanly and completed the documented
generate, qualify, solve and replay workflow. On 28 fixed compiled episodes
(the 26 fresh conditions plus both assisted finish policies), the candidate and
the previous commit produced identical agent-facing responses, receipts and
operator summaries. Both current preflights were regenerated: 56 cross-axis
conditions and 32 fresh/anchor rows. Only source identities and elapsed times
changed. The repair binding was refreshed after its 7,203-world qualification.

These checks found no further material defect. They cover the listed worlds and
paths, not every possible integration or model. Keep the final-source live canary
and hosted container checks as separate publication gates.
