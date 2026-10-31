# NEXUS smoke findings and decisions

Consolidated 31 October 2026 UTC (30 October in the user's timezone). This is the
project's current evidence record for choosing subsequent model smoke tests.
It supersedes the earlier suggestion to start with GLM 5.1: the next panel uses
GLM 5.2 at the user's request. Historical results and task definitions remain intact.

## Five-model controls: latest update

The [control audit](capability-controls-results-2026-10-31.md) adds nine started
attempts from ten planned slots, eight complete result records, five supported
world wins and three accepted final answers. Grok passed both controls. Muse
solved both worlds but failed exact receipt delivery on S21. Mistral solved S21
but failed final-response parsing; S05 ended early with a parsing error. GLM
made no tool calls. MiniMax's interrupted S05 loop made zero world actions;
S21 never started. These are predominantly interface/delivery findings and do
not establish new T/D or P/R effects. Advance Grok's fourteen-row screen,
repeat Muse S21 once, and diagnose the other three integrations before spending
on their challenge panels. Historical evidence below remains unchanged.

## What the experiments establish

NEXUS already supplies meaningful challenges for some tested configurations.
The clearest planning result is sensitivity to action allowance. Hidden-law
revision also reduces success relative to its disclosed control, and repetitions
show that several apparent failure boundaries vary between attempts. These are
useful effects without claiming that one numerical axis measures universal
reasoning difficulty or that a particular model is intrinsically unable to solve
a task.

A valid victory and a solution justified by the available evidence are different
measurements. A **supported win** succeeds under every world still consistent
with the player's observations. A **compatible win** succeeds in the actual
world but leaves a consistent alternative in which the submitted solution fails.
Both are mechanical wins. The latter is weaker evidence of discovery; it is not
reclassified as a failed mission. The audit examines public actions and evidence,
not private model reasoning.

## Earlier cohorts retained as context

The [T/D synthesis](https://github.com/petmal/NEXUS/blob/fe2d58f770f9e12aa6570ac30f3bd962849429b5/docs/td-experiments-and-next-directions.md)
records the earlier 40/40 receipt-accepted screen, with only 34 final submissions
supported by the available evidence. It found no reliable pure T/D failure boundary
for the strongest tested model. The [early P/R rerun audit](https://github.com/petmal/NEXUS/blob/fe2d58f770f9e12aa6570ac30f3bd962849429b5/docs/research/planning-resource-pilot-results-2026-10-25.md)
added five physical wins, four supported. The [coordination rerun](https://github.com/petmal/NEXUS/blob/fe2d58f770f9e12aa6570ac30f3bd962849429b5/docs/research/coordination-rerun-results-2026-10-26.md)
added four supported wins and showed that an earlier coupled-condition failure
was not stable; one relaxed win still used three unnecessary actions.

The pre-cross-axis Astra/Luna comparison had 32 reported Astra wins and ten
Luna wins, but 15 Luna failures never accessed a world. Those interface failures
must not be interpreted as planning failures or pooled with the later repaired
interface cohort. The current cross-axis tool contract and larger harness limits
define the observations tabulated below. This historical context motivates the
same rules: preserve exact cohorts, distinguish winning from justification, and
verify world access before assigning a reasoning failure.

## Attempt accounting

The initial archive contains 144 attempts: the 120 planned model–condition
combinations plus 24 Google repetitions. The first Google smoke run produced
three successes and 21 HTTP 402 credit errors. The primary analysis uses the
**whole complete second Google smoke panel**, including its three repeated early
rows, rather than choosing successful attempts individually. The original three
successes remain extra replications; billing errors remain infrastructure events.

The primary panel therefore contains 120 attempts, 89 wins and 31 losses. Of the
89 wins, 86 are supported and three compatible. Two additional rerun folders
contain launcher records but no model attempts; they contribute no observations.

`additions.zip` supplies two further ten-row panels for Luna and Flash: 40 new
attempts, 31 wins, nine losses, no provider errors. Combining those with the 20
matching original observations yields 60 attempts on the selected panel. This
is not a new version of the 120-attempt aggregate and must not be compared with
it as a trend. The two panels overlap.

## Initial results by family

Astra and Luna used medium reasoning; Flash used high thinking. Effort labels,
provider implementations and rate limits are not equal compute allocations.

| Family | Astra | Luna | Flash |
|---|---:|---:|---:|
| Interference, exact action budget | 16/16 | 1/16 | 3/4 canaries |
| Same interference worlds, extra actions | 16/16 | 13/16 | 4/4 canaries |
| Stateful discovery S01–S04 | not run | 4/4 | 4/4 |
| Revision S05–S12 | not run | 6/8 | 6/8 |
| Repair S21–S24 | not run | 1/4 | 3/4 |
| Spatial planning S13–S20 | not run | 4/8 | 8/8 |

These denominators differ. On the same 32 conditions Luna won 17 and Flash 28.
On the eight common interference conditions Astra won eight, Flash seven and
Luna two. There are no contemporary Astra smoke results for the other families.
Astra's success in interference cannot establish its result on revision or repair.

### Planning and resource pressure

Every one of Astra's 32 interference solutions used the minimum number of
physical actions, including tasks requiring previously completed goals to be
reopened. This bounded design has not demonstrated an Astra failure boundary.

For Luna, 12 of 16 matched interference pairs changed from loss under the exact
budget to win with slack; one passed both and three failed both. None reversed.
Sixteen of its 18 losses were already impossible to recover within the remaining
action budget. Two tasks reached the physical target but had no action left to
finish. Thirteen of its 14 wins used more than the physical minimum. Thus,
execution efficiency is the strongest observed explanation of the resource effect.
The budget includes acquisition and the final finish action.

Flash's one tight interference loss became unrecoverable at an early unnecessary
probe. Its paired relaxed run passed. That does not isolate difficulty from
mandatory reopening of completed goals. Longer plans, stronger dependencies and
slack are interpretable through matched controls, not the descriptive row labels.

Spatial planning was less orderly: Luna passed P2 while failing some lower and
higher labels at seed 21. Its two matched spatial slack pairs did not change
success. Flash solved all eight layouts optimally. P changes topology and required
work; its numeric labels are not a calibrated monotonic scale of cognitive difficulty.

### Disclosure and discovery

S01/S02/S03 retain one stateful world and a 64-action allowance while removing a
procedure and then hiding laws. Both models passed; accepted actions were
10/17/26 for Luna and 10/11/38 for Flash. Uncapped S04 also passed. These trials
show extra work, not a reliable failure boundary. They should not be pooled with
historical runs having smaller harness ceilings.

The better matched hard revision contrast is S05 versus S08: same world and
64-action allowance, disclosed versus hidden laws/procedure. This changes T and
D together. It cannot identify a pure T or pure D effect.

## What the repetitions add

Each entry is wins / supported wins, out of three attempts on the same fixed row.

| Row | Luna | Flash |
|---|---:|---:|
| S05 disclosed revision | 3 / 3 | 3 / 3 |
| S07 revision | 2 / 2 | 3 / 3 |
| S08 hidden counterpart of S05 | 1 / 0 | 1 / 1 |
| S10 revision | 3 / 1 | 3 / 0 |
| S11 revision | 3 / 1 | 3 / 2 |
| S12 revision | 2 / 2 | 2 / 2 |
| S21 disclosed repair | 3 / 3 | 3 / 3 |
| S22 hidden repair, 30 actions | 1 / 1 | 1 / 1 |
| S23 same repair, 36 actions | 1 / 1 | 3 / 3 |
| S24 second repair world, 36 actions | 0 / 0 | 2 / 2 |
| Selected panel total | 19/30 wins; 14 supported | 24/30 wins; 20 supported |

Both models pass S05 three times and fail S08 twice. Flash's failed S08 attempts
obtained enough public evidence for a guaranteed decision before exhausting the
budget, but later submissions contradicted known evidence. Luna showed both
unresolved uncertainty and a compatible win. A single explanation such as
“insufficient time to discover the law” misses these differences.

All three Flash S10 wins used the same build, while retaining the same conflicting
alternative world. Repeating the same favorable world does not resolve that
ambiguity or create three independent tests of a guessing probability. A future
qualified rival-world test is more informative than further identical repetitions.

Repair gives a reproducible Flash budget signal: one of three wins at 30 actions,
three of three at 36, all supported. Luna remains one of three at each budget;
individual paired repeat outcomes reverse. Do not claim the same repair resource
rescue for Luna. S24 is Luna's most consistent observed loss (0/3), but Flash's
2/3 shows it is not uniformly beyond both configurations.

Three attempts on a fixed seed are a small variability check, not an accurate
population success estimate or evidence of transfer to new worlds.

## Audit strength and limits

The initial audit replayed 3,823 public responses and 3,084 accepted actions,
matching all 127 available recorded action hashes. The additions replayed 1,577
responses and 1,359 actions, matching all 85 available hashes. Replays use a new
verifier secret: original submitted receipts match original returned receipts and
recorded validator acceptance, rather than pretending to reconstruct a private
original HMAC. Missing bounded operator tails are not invented.

All primary and new repeat attempts accessed the world and read the listed
evidence. Luna's 35 initial and 25 new malformed calls were recovered; Flash had
none. API syntax and transport failures must remain separate from world losses.
The bundled convenience summary conservatively reports unknown access when
concurrent log blocks cannot be attributed safely. The detailed audits join
TraceID, call ID, task and episode before replay; summary output alone does not
certify supported wins. An unlimited public budget is null, not the operator's
numeric zero sentinel.

## Model selection decision

“Smaller” is not an adequate selection criterion. The supplied leaderboard's
39 common text tasks are a better preliminary guide than its mixed 98-task score,
but those tasks often allow Python and are not NEXUS. Keep errors visible:

| Configuration in supplied leaderboard | Passed | Failed | Error | Passed / 39 |
|---|---:|---:|---:|---:|
| GLM 5.2 xhigh/max | 30 | 7 | 2 | 76.9% |
| MiniMax M3 | 30 | 5 | 4 | 76.9% |
| Muse Spark 1.2 Contributor xhigh | 36 | 1 | 2 | 92.3% |
| Mistral Large 4 high | 35 | 3 | 1 | 89.7% |
| Grok 4.7 xhigh | 39 | 0 | 0 | 100% |
| Flash 3.8 high | 39 | 0 | 0 | 100% |

Excluding errors gives GLM 30/37 and MiniMax 30/35; their total scores partly
reflect reliability. Older records lacking individual ToolCalls still contain
aggregate ToolUsage, so missing detailed calls must not be interpreted as no tool use.

The next screen includes the first five families. GLM 5.2 replaces the earlier
5.1 recommendation. Grok uses **medium**, a new effort setting, because its
xhigh text result gives no reason to expect a weak reasoning baseline. Muse and
Mistral are cost/diversity probes, not proven weak models. No scores are predicted
for these NEXUS configurations. See [the frozen next-panel guide](../capability-smoke-guide.md).

## Next decisions after live evaluation

First distinguish a working multi-turn integration from refusal, malformed calls,
empty responses, billing or transport failure. Retain controls even when they
lose; advance functioning integrations without selecting only winning models.
Then compare within-model matched contrasts, report wins and supported wins
separately, and retain all attempts. Repeat informative contrasts before enlarging
world mechanics. Fresh qualified seeds and a rival-world diagnostic come after
this fixed-world screen. If the panel is uniformly easy, raise controlled P/R
requirements; if uniformly hard, locate easier controls before adding complexity.
Repeatability, exact receipts, disclosure, replay and customizable difficulty
remain core NEXUS value even without a single-axis impossibility result.

## Evidence references

The current cross-axis trials tabulated here used source commit `fe2d58f770f9e12aa6570ac30f3bd962849429b5`
and runtime `ba22502788acf7ce1684e1e527e5aa332cd1746b37423fececabc90d71b8ee83`.
The companion JSON retains source hashes, aggregate observations and per-row
repeat counts. Detailed reports and reproducible audit bundles remain available:

- [Initial analysis](https://chatgpt.com/library?file_id=libfile_d70e56ebc89081919919a93c1c65efd8&account_id=personal)
- [Initial audit bundle](https://chatgpt.com/library?file_id=libfile_4c7d74af918c819193e3db50b0fb652f&account_id=personal)
- [Repeat analysis](https://chatgpt.com/library?file_id=libfile_992a49eb341081919023ae27850d664c&account_id=personal)
- [Repeat audit bundle](https://chatgpt.com/library?file_id=libfile_311cdb7ccc748191b950c3920336cebf&account_id=personal)

These account-specific links supplement, rather than replace, committed counts,
source hashes and interpretation. Raw user archives are not copied into Git.
