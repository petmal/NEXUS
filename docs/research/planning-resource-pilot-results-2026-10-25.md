# Planning/resource pilot: selected-row rerun audit

Audited 2026-10-25. The supplied rerun adds **one new attempt per row** on rows 06, 07, 08, 15 and 16. Each selected row now has two supplied attempts, counting the original pilot. It does not add two fresh repeats per row.

All five rerun attempts physically win and return the winning session's receipt. Four of the five finishes are supported by the public evidence available before finish. The original versions of these selected rows also produced five physical wins and four supported wins. The unsupported success moves from original row 06 to rerun row 15.

## Row comparison

All selected rows use theory T3 and discovery D5. “Supported” means every law still compatible with the public evidence puts the seal at the target before the successful finish. “Compatible” means only some do. The fractions count accepting laws over remaining laws; they are not calibrated success probabilities.

| Row | World seed | P / R | Action budget | Original → rerun actions | Original final evidence | Rerun final evidence |
|---|---:|---:|---:|---:|---|---|
| 06 | 21 | 0 / 2 | 41 | 41 → 29 | compatible (2/4) | supported (2/2) |
| 07 | 21 | 3 / 2 | 105 | 80 → 48 | supported (2/2) | supported (4/4) |
| 08 | 21 | 3 / 1 | 158 | 48 → 48 | supported (4/4) | supported (4/4) |
| 15 | 31 | 3 / 2 | 98 | 61 → 37 | supported (2/2) | compatible (8/16) |
| 16 | 31 | 3 / 1 | 147 | 51 → 59 | supported (4/4) | supported (2/2) |

- **06:** the original attempt failed at turn 29 and won without sufficient evidence at turn 41. The rerun wins on its first finish at turn 29, supported by both remaining laws. It uses 27 operations, no probes, take and finish.
- **07 / 08:** rerun R2 and R1 executions have identical ordered 48-action sequences: take, 28 moves, 13 operations, five probes and finish. The original 80-versus-48 action difference is not stable.
- **15:** the 37-action rerun has 16 surviving laws; eight predict `[1,2,3,1]` and eight predict `[1,2,3,2]`. The actual state is the target `[1,2,3,1]`, so the win is real, but its correctness is not established by the observations. No guaranteed-repair point is reached. The run uses 18 moves, 15 operations, two probes, take and finish.
- **16:** the supported rerun uses 59 actions, up from 51: 34 moves, 21 operations, two probes, take and finish. Both remaining laws are at target before finish.

The rerun totals 251 successful tool calls and 221 accepted actions. The five original counterparts used 311 calls and 281 actions. Every rerun reads all four evidence files and makes one successful finish; no invalid actions, duplicate requests or protocol conflicts are reported. Action totals are descriptive; the lower aggregate is not an estimate of improvement.

## What was verified

The audit reads the raw result JSON and raw log independently of their headline outcomes. Task records, trace IDs, start blocks and tool call IDs reconcile, with exactly one new attempt per selected row. All tool calls have successful process status. An immutable checkout of the recorded source generates each episode from its bound parameters; a fresh session replays every manifest, observation, evidence read and action. Observations, action events, turn numbers, messages and terminal performance records match exactly.

A separate scalar implementation of the published modular update rule tracks the actual state and all 256 candidate laws. It filters candidates using each public reading, preserves state for probes, commits state for operations, and incorporates failed-finish feedback where applicable. It evaluates final evidence before using successful-finish feedback. This independent reconstruction agrees with the reported submission diagnostics, including row 15's unsupported success. Re-auditing the original 16-row input reproduces its prior action traces, classifications, performance and totals: 16 physical wins, 15 supported wins, 573 calls and 477 actions.

Public investigation and evidence hashes, bound seed/axis/budget values, source digests and recorded container revisions match for both inputs. The three captured rerun operator action records also match reconstructed before/after hashes (one each for 07, 08 and 15). The raw log does **not** contain a complete action-hash journal, so the audit claims complete public-response replay and matching available hashes, not a complete captured-journal verification.

Each terminal receipt matches the submitted answer and result, and the recorded custom validator says the session was won and its receipt matched. Fresh replay independently confirms physical success. The original verifier secrets were not supplied, so this audit does not claim to recompute the original receipt HMAC. Receipt values and raw logs are intentionally omitted from this report.

## Historical source checkpoint

These are observations of the **initial input source**, not of subsequent changes made after reviewing the rerun. Later source edits require their own qualification; they do not rebind the historical model attempts.

| Binding | Value |
|---|---|
| Commit / recorded image revision | `0deb982c6d04e3591f69750eb4ad51fdc9283025` |
| Recomputed source digest | `f9307e24620cfd68ce5da3caeacc29ca6d4e179e66dafee912b618c2176c5ef8` |
| Container image ID | `sha256:5db10c8f072a1d7efe45089ef3e65274054de21b1d1b3842aa547654050cfc10` |
| Container manifest digest | `sha256:7907311ecdd735b54b60350c9b80bf99295eac412e6d19718597b16e8e7dfec4` |
| Matrix file SHA-256 | `4a0595878a969eb1b63054bf460fa9196c1da7acb9194847186f8388cab2aad7` |
| Matrix canonical SHA-256 | `9218ffc3fd8ac59206ef6284710f1f337fd73240eb44f8d1167c529cef4dd428` |
| Preflight file SHA-256 | `63693bfbf8d8f38a89d02d4a68ae17f0dd81a2f6c836b20155a0d6980a6ccd69` |
| Model / reasoning effort | `gpt-6-astra` / `medium` |
| MindTrial version | `v0.25.3-0.20261017164258-00dada61a962` |

| Input file | SHA-256 |
|---|---|
| `12-29-30.json` | `091920d752ae1cf4688feb9506c7b77a90554037038884dcc75330a49a9aaf19` |
| `12-29-30.log` | `a8de543e1c7bd75094c7f7092661bed0cc9249bba0b27059833be77657041fab` |
| `19-37-58.json` | `712b309edf8da5e623b443c6b18c148003816f5a8021789437ece30f1f821444` |
| `19-37-58.log` | `482543747dfc212f9af82a97ac4bf80451efe39247bce8c569525e1473672170` |

## Interpretation and next decision

This is a targeted diagnostic of five selected cells over two operator-chosen worlds, with only two supplied attempts per selected row. It does not establish a stable R2/R1 effect or population difficulty calibration. Seed 21's rerun resource pair is identical; seed 31's cheaper R2 attempt is unsupported. The original and rerun evidence together support retaining the experimental label and keeping physical wins separate from evidence-supported wins.

No budget rebalance follows from these results. T3 action allowances are based on the worst-case cost of one public policy, not the optimal information cost or a proof that a probe is necessary. The next empirical decision should use prospectively specified, matched repetitions and record independent attempt identities, source bindings, physical success, evidence support, actions and resource pair comparisons. Keep this historical checkpoint separate from any new source qualification.

The [machine-readable summary](planning-resource-pilot-results-2026-10-25.json) contains per-attempt counts, submission evidence, action-sequence digests, source bindings and audit limits. This audit made no live model or service calls.
