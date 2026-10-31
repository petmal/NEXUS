# Capability smoke implementation validation

31 October 2026 UTC. Offline checks only; no live model evaluation was run.

The five-model panel contains 16 unique historical conditions per model, split
into two controls and fourteen followups (80 possible attempts). Exact selected
task objects, names, prompts, world inputs, 600-call/650-turn ceilings and the
cross-axis evaluation seed are preserved. The configured tool contract remains
`cross-axis-tools-v1`. No `src/nexus` file changed; runtime source stays
`ba22502788acf7ce1684e1e527e5aa332cd1746b37423fececabc90d71b8ee83`.

The full 56-condition cross-axis qualification was recomputed successfully before
release. The new selector rejects missing/duplicate source tasks and differing
harness contracts. The embedded container program is additionally exercised on
the host with only `/app/docs` translated to the checkout path, then its two task
exports compared exactly with the shipped subset. The launcher recomputes this
qualification in the actual pinned container before any paid execution.

Focused release-boundary tests exercise model/key routing, default ten controls,
explicit two-stage selections, effective config/task/image/seed manifests,
credential exclusion, exact historical task identity, checksum rejection and the
real Bash entry point from a directory with spaces. Existing coordination and
cross-axis launcher regressions remain in the gate. The source exporter exactly
reproduces every new config/task file.

Real subprocess/HTTP/tool/receipt checks passed both controls (S05/S21) and five
screen examples (interference11, S03, S08, S23, S16). Valid reference receipts
were accepted, altered receipts rejected, and pre-play forged receipts rejected.
These checks use the actual new configuration contract; they do not execute
MindTrial's Docker orchestration or validate live provider requests.

Independent read-only review confirmed the audit JSON against the two earlier
audits, the supplied text leaderboard counts, task identity, routing and retained
runtime. Its package-relative documentation link finding was repaired in the
packager. A separate check corrected the guide's planning interpretation:
09↔11 combines horizon and coupling changes; only 09↔25 and 11↔27 are pure
budget comparisons. The screen does not claim an isolated coupling effect.

The fast regression run passed 1,354 tests, with 54 slow/stress cases deselected
and three existing malformed-fixture serializer warnings. After the final
package-assembly test was added, the focused launcher/package suite passed
161 tests. Scoped Ruff lint/format checks pass. The existing frozen Python3.14 environment
is used without dependency changes. Repository-wide type/coverage/tooling debt
recorded in the prior validation remains out of scope. Docker is unavailable in
the editing environment, so a new container build is not claimed locally. CI's
existing exact-feature image and service sweep now also packages and qualifies
the five-model launcher. Consult the commit's CI status separately.

The final delivered ZIP pins the clean release commit, runtime, all files, each
config contract and the configured tool contract. Source/API inspection supports
the proposed model IDs/settings; the user's live controls remain necessary for
provider routing, credentials, billing, multi-turn behavior and actual difficulty.


## Control audit and unattended launcher revision

The supplied five-model control archive was independently replayed: nine started
attempts, eight complete result records, 146 valid public responses, 30 accepted
actions and all 28 captured action hashes matched. Five supported world victories
produced three accepted final answers. The exact archive, source and binary
identities are retained in `capability-controls-results-2026-10-31.json`.

The launcher now supports explicit interactive/default and non-interactive modes.
Unattended execution closes stdin, inherits progress output, and stops on missing,
empty, malformed, duplicate or unexpected result coverage after a zero child
exit. Complete Failed/Error records remain recorded outcomes. Interactive subset
selection is preserved. The readout handles missing/empty JSON without inventing
records. Neither model settings, exported tasks, budgets, seeds nor runtime code
changed. Ruff now records the shipped host scripts' Python 3.12 target separately
from the Python 3.14 engine, and a syntax regression test protects that boundary.

The revised focused suite passed **188 tests**, covering both modes, sequential
suite execution, result coverage failures, corrupt/duplicate identities, preserved
process/launcher exit codes, partial summaries and prior release boundaries.
Scoped Ruff checks pass. Historical full-suite and live-service checks above were
not repeated for this launcher-only revision. The release packager recomputes
the full parent qualification before producing the updated ZIP. Docker remains
unavailable in this editing environment. No paid model evaluation was run.
