# Testing and CI

The aggregate also checks the literal host/container matrices against the required
group lists. Removing, duplicating or excluding a matrix group must fail even when
the remaining parent jobs report success.

Every pull request to main, main push and merge-queue revision runs the full
deterministic suite. There are no paid model calls. The final **complete** check
passes only when all groups succeed; a skipped or cancelled group is a failure.
Live model canaries remain a separate release check.

## Run checks locally

```bash
uv sync --frozen --all-extras --python 3.14.7
make check                       # Ruff and documentation links
make test                        # Fast unit/integration feedback
make test-full                   # Every pytest case, including slow/property
make ci-partition                # Check complete, disjoint test ownership
make ci GROUP=interfaces          # Same tests and extra checks as CI
make ci GROUP=container-panels    # Requires Docker
```

`make test-fast` is an explicit alias for the fast command. `make stress` runs
only property tests. The CI runner always uses all ten existing stress seeds and
ignores caller-supplied pytest selection flags. It rejects empty, failed or
skipped test reports. Run ordinary pytest directly for a deliberately smaller
local investigation.

## Parallel groups

| Group passed to `make ci` | Tests and additional checks |
|---|---|
| `quality` | Frozen lock, actual pytest collection/partition, Ruff, documentation, actionlint, clean wheel and source-distribution installations |
| `core` | Engine/rules, state ownership, solver invariants and certification, finite-machine oracle, generation, all property tests |
| `scientific` | Scientific worlds and independent oracles; immutable dynamics/transfer assets; transfer/Astra, history, staged, assembly, discovery, coupled-memory, stateful and revision qualification/preflights |
| `planning` | Planning/resources, coordination, interference and structural costs; planning, coordination, interference and comparison preflight/task exports |
| `interfaces` | CLI/console, public device help, frozen presentations, HTTP/JSONL, retries and integration tests; seven legacy/scientific generate/qualify/solve/replay CLI scenarios |
| `evaluation` | Metrics, audit, admission, matrix exports, packaged launchers/readouts and CI guards; cross-axis and fresh-world qualification/task exports; standalone operator entry points |
| `container-scientific` | Image CLI and Python; repair, difficulty, structural, budget, transfer/Astra, history, staged, assembly, discovery, coupled-memory, stateful and revision preflights; legacy/scientific generation |
| `container-planning` | Planning/coordination/interference/comparison image preflights; all planning rows, coordination core/spatial/slack, comparison core/slack, original interference row 01 through real services and receipt validators |
| `container-panels` | Persistent mounts and audit survival after container removal; cross-axis/fresh-world image qualification; all coordination/interference/cross-axis/capability/fresh packaged launcher suites; six cross-axis and four fresh-world service suites |

The exact module lists are in [ci-groups.json](../../tests/ci-groups.json).
[ci-host.sh](../../scripts/ci-host.sh) and
[ci-container.sh](../../scripts/ci-container.sh) retain the non-pytest command
inventory formerly spread across two workflows. Different environments check
different contracts: a mathematical test does not replace an installed-service
or package-boundary check.

All 7,203 repair-policy worlds remain covered by the exhaustive scientific test.
The core property sample covers 240 legacy worlds (six D settings × four P
settings × ten seeds), plus the other property checks; it is not exhaustive
coverage of every scientific family.

## Add or move a test

Assign every test module to exactly one group. `make ci-partition` compares the
manifest with real pytest collection and rejects unassigned modules, duplicate
ownership, nonexistent/empty modules and empty groups. Do not hide new tests
behind a broad fallback group.

Keep tests with the behavior they protect. Shared parametrized contracts must
retain each relevant world/settings case. Preserve independent mathematical
oracles, frozen player presentations and supported historical utilities.
Remove a test only when its contract is retired or a surviving test covers the
same failure. The [CI migration record](ci-test-migration.json) maps the tests
moved from review-specific modules and records the one removed inapplicable
case, which previously always skipped.

Player fixtures return compiled worlds; each test creates its own session.
Tests that mutate compiled data must take an independent copy or use a fresh
fixture. Do not share mutable sessions to accelerate the suite.

## Environments and results

Core tests use Python 3.14.7, frozen dependencies and uv 0.12.21 in GitHub Actions.
The workflow pins Ubuntu 24.04 and action commits. Dependabot groups action
updates; verify new pins and actionlint checks before merging.
Operator entry points additionally run on Python 3.12 without NEXUS or site
packages. To reproduce that check locally:

```bash
uv python install 3.12
NEXUS_OPERATOR_PYTHON="$(uv python find --no-project 3.12)" make ci GROUP=evaluation
```

Without that variable, the local operator tests use the current Python.
The workflow validator downloads a checksum-verified actionlint 1.7.12 on Linux
x86-64 if none is installed; other hosts can install it or set `ACTIONLINT`.

Each group writes timings and, for pytest groups, JUnit results under ignored
`ci-results/<group>/`. GitHub retains these diagnostics for seven days.
Timing metadata records the tested commit, local dirty state, PR head, runner image, Python/uv and
stress sample. Private episode/proof exports live in temporary directories;
they are not uploaded. CI checks committed reference bindings and never
refreshes tracked certification reports.

PRs test GitHub's proposed merge; main tests the pushed commit. Superseded PR
runs are cancelled, while non-PR runs have distinct concurrency groups so
merged revisions are not discarded. Independent groups keep running after
another group fails.

The manual **Generation profiling** workflow accepts a seed and axis settings;
its defaults preserve the previous seed-17 D5P2/D5P3 comparison. It uploads JSON
profiles and is not a correctness gate.

## Required check and performance

After the new workflow has a successful run, require its **complete** check in
the main branch rules and retire the previous individual required contexts.
Use the actual context shown by GitHub; do not remove the existing protection
before the replacement check is available. Check the first merged main run too.

As checked on 22 November 2026, GitHub reports that rulesets are unavailable on
this private repository's current plan. The CI workflow still runs normally.
Enable the required check when the repository becomes public or uses an eligible
plan; this CI change does not alter visibility or billing.

Compare GitHub wall time and runner minutes using complete runs. The former
roughly 13-minute host run excluded slow/property work; it is not a full-suite
baseline. Aim for under 30 minutes after parallelization, without reducing
assertions or seeds. If one group dominates, split by responsibility rather
than arbitrary filenames. The initially generous timeouts are limits, not
expected durations.
