# Run the NEXUS coordination pilot

Download and unpack the package in `~/Downloads`. It contains an enclosing
`NEXUS-coordination-test-run-2026-10-25` directory, the configurations and a
one-command launcher. Defaults match the existing local workflow:

- NEXUS clone: `~/Go-Projects/NEXUS`.
- MindTrial working directory and existing binary: `~/MindTrial/mindtrial`.
- Results: `<unpacked-package>/results/<suite>-<unique-run>/`.

The host needs Bash, Python **3.12 or newer**, Git, a working Docker CLI/daemon
and the existing MindTrial binary with task services/custom validators. The Python
launcher uses only the standard library. It does not install or replace MindTrial.
Keep the default credentials in `OPENAI_API_KEY`; do not paste keys into the files.

From any directory, run:

```bash
bash ~/Downloads/NEXUS-coordination-test-run-2026-10-25/run.sh
```

This builds the exact revision in `release.json`, performs free local qualification,
then launches **16 core tasks against GPT-6 Astra at medium reasoning**. The last
step makes paid model calls. To build and qualify without starting an evaluation:

```bash
bash ~/Downloads/NEXUS-coordination-test-run-2026-10-25/run.sh --preflight-only
```

The launcher reads the exact source commit from the local clone and builds an
isolated archive of that commit. If the commit is missing, it fetches the named
feature branch from `origin`. It does not change the checkout, switch branches,
discard edits or merge anything. It checks the built image's OCI revision and
runtime digest, runs qualification inside that image, and verifies that generated
task definitions match the shipped files. No bind-mounted output directory is
needed for qualification. The effective MindTrial configuration uses the inspected
image ID, so changing a tag cannot silently change the run.

The interactive command runs from `~/MindTrial`, using absolute configuration and
task paths. It preserves the requested options:

```bash
./mindtrial -config="<absolute-run-config>" -tasks="<absolute-run-tasks>" \
  --debug --interactive=true --json --evaluation-seed="nexus-coordination-pilot-v1" run
```

Output and log paths in that saved effective configuration are absolute and point
inside the package, regardless of MindTrial's working directory. The original
configuration, effective configuration, task snapshot, preflight evidence and run
identity record are retained there. The record includes source/image identity and
the actual local MindTrial binary hash, so unreleased harness fixes are identifiable.
Provider secrets are neither printed nor written by the launcher.
The manifest status `completed` means MindTrial exited with code 0; it does not mean
every task succeeded. Read the task results and victory-validation outcomes separately.
Administrative Git/Docker failures report their stage and exit code. Their raw
subprocess output is not saved, so detailed build failures require a separate
local Git or Docker diagnostic.

## Choose the next suite

| Suite | Tasks | When to run |
|---|---:|---|
| `core` (default) | 16 | First: matched independent/coupled groups at exact budgets, no travel |
| `slack` | 16 | Follow up core failures with extra allowance on the same problems |
| `spatial` | 8 | Largest shape with travel, comparing exact and slack budgets |
| `repeat` | 10 | Two more attempts on each selected historical T3 row |
| `all` | 50 | Explicitly run all four suites sequentially |

Examples after the first successful image build:

```bash
bash ~/Downloads/NEXUS-coordination-test-run-2026-10-25/run.sh --suite slack --skip-build
bash ~/Downloads/NEXUS-coordination-test-run-2026-10-25/run.sh --suite spatial --skip-build
bash ~/Downloads/NEXUS-coordination-test-run-2026-10-25/run.sh --suite repeat --skip-build
```

`--skip-build` still checks the image revision/digest and reruns qualification. The
repeat suite uses evaluation seed `nexus-pr-pilot-v1`; the new suites use
`nexus-coordination-pilot-v1`. World seeds are fixed separately in each task.
Task retries are disabled. Each invocation creates a fresh result directory;
explicit reruns do not overwrite earlier attempts.

To use different local paths, override the environment variables:

```bash
NEXUS_REPO="$HOME/other/NEXUS" MINDTRIAL_DIR="$HOME/other/MindTrial" \
  bash ~/Downloads/NEXUS-coordination-test-run-2026-10-25/run.sh --preflight-only
```

To compare another supported OpenAI model or reasoning effort, edit the selected
config's provider run. Only its `name`, `model`, `model-parameters`, and
`max-requests-per-minute` fields may change. Provider identity, enabled runs,
retry policies, tools, service mappings, validator settings and all other fields
are pinned by the release's config contract checksum. The launcher rejects changes
outside the four allowed fields before it builds or starts an evaluation.

`core`, `slack`, and `spatial` use `nexus-coordination-config.yaml`. `repeat` uses
`nexus-coordination-repeat-config.yaml`, which preserves the historical planning
tool description and interface. Both ship with the same model/provider settings.
Each file's model choices are independent: edit both when using `--suite all` if
you want the same changed model or effort throughout. The launcher uses each
file's settings without copying or overriding choices from the other file, and
records the selected filename, original-byte checksum and contract checksum.

The qualified task files and launcher are release artifacts and should not be
edited in place. All suites keep a 600-tool-call and 650-turn harness ceiling;
the smaller world-action budgets are separate.

Collect the relevant subdirectory under the package's `results/`, including its
JSON and log outputs, configuration/task snapshots and run identity record. An
interrupted or failed attempt should be retained and any rerun labelled separately.

The new family has known laws and a complete state display. It compares structural
group sizes and added cross-group dependencies, not hidden-law difficulty. R2 is
an exact physical minimum; R1 adds slack. At P0 the coupled fixtures have a certified
advantage for revisiting groups over every group-contiguous solution. A lack of
model failures would remain a valid result. See the repository's
[coordination guide](https://github.com/petmal/NEXUS/blob/feat/planning-resource-axes/docs/coordination-guide.md)
for controls, guarantees and interpretation limits.

No model calls were made while preparing this package. Its `release.json` records
the implementation revision; historical pilot results retain their own earlier
source checkpoint.
