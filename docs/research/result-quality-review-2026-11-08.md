# Third quality review: which run counted, and what did it show?

The review followed a selected panel condition through launch, control admission and
offline reporting. It found two distinct ways to misread a result: a record could
occupy the right slot while describing a different run, and the last available
observation could describe an active world without telling us how it ended.

| Finding | Correction |
|---|---|
| Unattended coverage checked provider, run label and task name, while the offline readout checked more settings but ignored the evaluation seed. A Boolean could also match a numeric setting in either comparator. | Both paths now check the result format, unique trace identity, provider, selected model, recorded settings and seed. Known omitted provider defaults still match. An error record can occupy a slot without establishing a loss. |
| A prior control could admit a challenge built with a different image. A changed tool or validator in the effective config could pass its own checksum. Equal start times were resolved by directory name. | Admission binds the actual image ID and reconstructs the whole effective config from the archived input, output location and image. A tie between the latest attempts for one control requires a new result for that control. |
| A log ending in an active state counted as an observed failure. A cached response could displace a newer state, and overlapping output from an unreported trace could be attributed to a known one. A successful public construction check was missed. | Readout v5 leaves the world outcome unknown without terminal evidence, follows game turns, flags conflicting verdicts, and treats overlapping logs conservatively. A checker response confirms access but supplies neither a victory nor a spent action. |
| Rebuilding the November 3 operator hotfix copied the current readout under the old patch name. | The packager reads the four original files from the recorded fix commit. It stops if that source is unavailable. New packages use the current readout. |

## Effect on the experiments

We compared the previous readout at `2a6f687` and v5 on the same saved folders.
No new inference, replay or private receipt verification was performed.

| Archive | Attempts / folders | Harness verdicts | World outcomes under v5 |
|---|---:|---|---|
| [Fresh-world study](fresh-world-results-2026-11-04.md) | 110 / 17 | 84 passed, 15 failed, 11 errors | 84 won, 15 terminal failures, 11 unassessed |
| [RC2 canary](rc2-canary-results-2026-11-06.md) | 6 / 2 | 6 passed | 6 won |

Two fresh-world rows moved from “observed failure” to “unassessed”: Flash on F17
(billing interruption) and Grok on F26 (provider unavailable). Neither recorded
a terminal world state. No harness verdict, confirmed win, matrix coverage decision
or diagnostic outcome category changed. The saved input, image ID and original
output location reproduced each of the 19 effective configurations. The RC2 archive
also contains a preflight-only folder. Testing the documented multi-folder command
exposed a crash on that folder; the command now identifies it explicitly and
continues to the live runs. A damaged run still produces an error.

This correction matters when calculating failure rates: counting these two rows
as model losses would overstate the evidence. It does not change the T/D or P/R
findings or establish a new model ranking. Keep the original folders, identify
the readout version in new analyses, and keep the final candidate’s live canary
as a separate release check.
