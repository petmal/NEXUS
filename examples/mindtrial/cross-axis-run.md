# NEXUS cross-axis canaries, reruns and small-model smoke tests

This package contains **56 distinct task conditions**: the 32 original
interference tasks and 24 smoke tasks drawn from qualified T/D and P/R worlds.
The canaries separate the eight selected interference rows from the other 24;
`all` runs every condition once. Model allocation gives **120 attempts** when
every enabled model and task is selected.

| Suite | Conditions | Enabled models | Attempts |
| --- | ---: | --- | ---: |
| `canary-core` | 4 (original rows 09–12) | Astra, Luna, Gemini Flash | 12 |
| `canary-slack` | 4 (original rows 25–28) | Astra, Luna, Gemini Flash | 12 |
| `rerun-core` | 12 (remaining original core rows) | Astra, Luna | 24 |
| `rerun-slack` | 12 (remaining original slack rows) | Astra, Luna | 24 |
| `smoke-td` | 16 (stateful, revision and repair) | Luna, Gemini Flash | 32 |
| `smoke-pr` | 8 (spatial planning and resources) | Luna, Gemini Flash | 16 |

The model presets are GPT-6 Astra and GPT-6 Luna with medium reasoning at
20 requests/minute, and Gemini 3.8 Flash with high thinking at 3 requests/minute.
Flash's conservative inherited rate limit can dominate elapsed time. There are
no automatic retries. The new smoke conditions share limits of 600 tool calls
and 650 turns; historical runs with smaller harness limits are not matched
comparisons to this run.

## Run locally

Extract under `~/Downloads`. The launcher builds the exact release commit from
`~/Go-Projects/NEXUS` and runs your existing `~/MindTrial/mindtrial` binary with
interactive input. It builds a temporary Git archive, preserving your checkout
and uncommitted work. It fetches the feature branch only if the pinned commit is
missing locally.

```bash
cd ~/Downloads/NEXUS-cross-axis-test-run-2026-10-29

# Optional: fully qualify all 56 conditions without credentials or model calls.
bash run.sh --preflight-only

# Set OPENAI_API_KEY and GOOGLE_API_KEY in your environment, then run canaries.
bash run.sh --suite canary
```

`canary` is the default if `--suite` is omitted. In each interactive screen,
select **every enabled model run and every task row**. The canary group opens
two runs with four tasks each. Preserve errors and partial results as evidence.
Review tool arguments, transport errors and world access before starting the
remaining matrix. A world loss can still show a working interface; the launcher
does not make this scientific decision or start followups automatically.

After review, run either the full followup or separate groups:

```bash
bash run.sh --suite followup --skip-build

# Equivalent split; do not also run these if you already ran followup:
# bash run.sh --suite rerun --skip-build
# bash run.sh --suite smoke --skip-build
```

`rerun` selects the two remaining interference suites and requires only
`OPENAI_API_KEY`. `smoke` selects both smoke suites and requires both keys.
`followup` selects those four suites. Every individual suite name in the table
is accepted. `--suite all` selects all six suites without duplicating the
canaries; use it only when intentionally running the complete matrix together.
The complete allocation is Astra 32, Luna 56 and Flash 32 attempts.

`--skip-build` still checks the OCI revision, immutable image ID, runtime source
digest and freshly qualified task exports. Both Docker's `sha256:` image IDs
and compatible Podman's bare hexadecimal IDs are accepted. Host Python 3.12+
and a Docker-compatible CLI named `docker` are required. The image uses the
repository's frozen Python environment. Offline mechanical qualification may
take time because it checks all 56 conditions even for one selected suite.

Override paths using `NEXUS_REPO` and `MINDTRIAL_DIR`; `PYTHON` selects the host
Python executable. The launcher invokes your locally built MindTrial as:

```text
./mindtrial -config=<absolute-result-dir>/config.yaml -tasks=<absolute-result-dir>/tasks.yaml --debug --interactive=true --json --evaluation-seed=nexus-cross-axis-pilot-v1 run
```

## Configuration, contract and audit trail

Configs are routed by suite: `nexus-cross-axis-canary-config.yaml`,
`nexus-cross-axis-rerun-config.yaml` and `nexus-cross-axis-smoke-config.yaml`.
Keep keys out of all files. MindTrial's Google provider uses `GOOGLE_API_KEY`.
The launcher checks credentials only for the selected suites; preflight needs
none. Its captured administrative errors never print subprocess stderr or key
values.

Only provider-run `name`, `model`, `model-parameters` and
`max-requests-per-minute` may be edited. Such edits are recorded and define a
different model or execution setting. Provider/run counts, enabled flags,
retry policy, task integration and tool descriptions/schema remain pinned.
Preserve the shipped presets when comparing the recommended matrix. The files
use JSON syntax, which is valid YAML.

Each suite creates a fresh folder under this package's `results/`, containing
the original and effective config, exact tasks, full preflight, release identity,
run manifest and MindTrial outputs. Archive the entire `results/` directory,
including failed and interrupted runs. Keep reruns alongside the original
attempts. An exit code of zero does not establish complete interactive selection
or success on every world.

The release and run manifests identify tool contract `cross-axis-tools-v1`
and hash the configured tool names, descriptions, parameter schemas, parameter
file mappings and commands. This is a **configuration-level contract**; it is
not a capture of the schema actually transmitted to a provider. The interface
still requires the outer `request` object, for example
`{"request":{"operation":"manifest"}}`. Improved diagnostics do not repair or
flatten model arguments.

The manifest also records the source commit, runtime source digest, immutable
image ID, MindTrial binary hash and config/task hashes. The container recomputes
qualification and all six exports without network access. Shipped tasks must
match those exports exactly before any live run begins.

Summarize explicit result folders using the included helper:

```bash
python3 summarize_results.py results/canary-core-* results/canary-slack-*
```

Choose folders for the intended attempt set; broad globs can mix reruns. This
summary checks recorded configuration/task hashes and reads model outcomes. It
does not replay episodes or independently certify victory receipts.

See `guide.md` for row definitions, controls, model-selection rationale and the
analysis plan. `reports/` contains offline qualification and implementation
validation, not model results. Diagnose tool-use failures separately from world
reasoning, compare matched controls within each family, and avoid treating
repeated variants of one generated kernel as independent sampled worlds.
