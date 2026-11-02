# NEXUS five-model smoke run

Five models, 16 unchanged conditions each: **80 attempts** if all proceed.
Start with ten control attempts; then run seventy challenge attempts. See
`guide.md` for the exact row mapping, settings and analysis rules, and
`reports/smoke-findings-2026-10-31.md` for the consolidated earlier findings.

## Current recommendation after the compiled repetitions

**2 November update:** MiniMax Stage A encountered three 429 errors and a
separate empty-content stop. Pause its repeated/challenge runs. After a cooldown,
run `bash probe-minimax-rate.sh` once: it backs up the MiniMax config, labels a
2-RPM diagnostic, and runs only S05. It builds this release by default; use
`--skip-build` only if this exact release is already built. See
`reports/minimax-control-interruption-2026-11-02.md`. GLM C/D is independent.

The GLM/MiniMax controls, initial screens and selected repetitions are complete.
Do not repeat either full screen. Read `followup-matrix.md` for the focused
MiniMax reliability checks and GLM high/xhigh comparison, and
`reports/smaller-model-synthesis-2026-11-01.md` for the evidence.

This release improves operator reporting and unattended row selection. World
mechanics, task objects, seeds, qualification, player instructions and the
GLM/MiniMax text-output setting are unchanged. Build this release once before
using `--skip-build`; its source revision differs from the earlier v3 package.

Grok's fourteen-row screen, Muse's S21 receipt-delivery repeat and Mistral's
response diagnostic remain unreported. If Muse still needs its repeat:

```bash
bash run.sh --model muse --suite controls --task-id S21 --non-interactive
```

Only S21 is included in that run's task file. Do not also run the whole control
suite. Set `OPENROUTER_API_KEY` first. Grok can independently run its remaining
screen with `--model grok --suite screen --non-interactive`, using `XAI_API_KEY`.

## Choosing interactive or unattended execution

Interactive selection remains the default; `--interactive` makes it explicit.
Use `--non-interactive` to run every enabled model/task in the selected config
and suite without prompts. Progress output remains visible. The two flags are
mutually exclusive. They also work when several model groups are selected.

For a **deliberate future full panel**, after resolving integration issues:

```bash
bash run.sh --model all --suite all --non-interactive --skip-build
```

This repeats controls and runs all seventy screen attempts. It is **not** the
recommended continuation of the attached controls. There is no automatic
scientific admission gate between controls and screen. Failed, Error and Skipped
records count as recorded outcomes. An HTTP 429 Error is the exception: after
the current MindTrial group finishes, the launcher stops before any further
group or repetition, with status `rate_limited` and launcher exit code 2. It
preserves the child exit code and all results. It cannot stop inside a group or
infer a retry delay from the status alone.

Non-interactive runs check that exactly one result exists for every enabled
provider/run/task. A zero MindTrial exit with missing, empty, malformed,
duplicated or unexpected records stops the batch with launcher exit code 2.
The manifest retains the actual child `exit_code`, `launcher_exit_code`, mode
and result coverage. Any nonzero child exit also stops the batch. Existing
results remain intact; resume remaining groups explicitly to avoid repeats.
Interactive subsets do not require full-matrix coverage. Their zero process
exit alone still does not certify a complete evaluation.

For a bounded unattended subset, repeat `--task-id` for each row. A selector
must be an exact task name or a unique suffix such as `11` or `S23`. Unknown,
ambiguous and duplicate selections fail before build or model calls. Selection
keeps complete task objects and their harness settings; full qualification still
runs. `--repeat 2` runs the selected jobs twice in separate result folders with
the same world seed. It measures repeatability, not new-world generalization.

```bash
# Two repetitions of only the long tight/slack pair, current GLM preset:
bash run.sh --model glm --suite screen --task-id 11 --task-id 27 \
  --repeat 2 --non-interactive --skip-build
```

The following full-panel examples are reference usage, not the current recommendation.

## Run from Downloads

Extract this package under `~/Downloads`. Set the three credential environment
variables in your shell: `OPENROUTER_API_KEY`, `MISTRAL_API_KEY`, `XAI_API_KEY`.
Keys stay out of files. The launcher builds the pinned NEXUS commit using your
clone at `~/Go-Projects/NEXUS`, then invokes your locally built
`~/MindTrial/mindtrial` with `--debug --interactive=true --json`.

```bash
cd ~/Downloads/NEXUS-capability-diagnostics-2026-11-02
bash run.sh --suite controls
```

This opens five interactive runs sequentially, one model and two tasks each.
Select the enabled model and **both tasks** in every screen. A process exit code
of zero does not certify complete selection or a successful mission. Check the
results for working multi-turn world access and any provider issues.

If all five integrations work, run the remaining fourteen rows per model:

```bash
bash run.sh --suite screen --skip-build
```

Select all fourteen tasks for each model. A model losing a control legitimately
is still informative; it need not win to proceed. Provider or schema failures
need diagnosis before interpreting axis effects. The launcher does not run the
followup automatically after the controls.

Run one model independently (only its credential is required):

```bash
bash run.sh --model glm --suite controls --skip-build
bash run.sh --model glm --suite screen --skip-build
# Other selectors: muse, minimax, mistral, grok
```

Do not rerun the example's controls if that model already completed them, unless
you intend and label a repetition. `--model all` is the default. `--suite all`
runs controls plus screen once per selected model; do not use it after completed
controls unless you intentionally want repeated controls. On any nonzero
MindTrial process exit, the launcher stops and preserves that run. Select the
remaining models individually to resume without repeating completed models.

Offline qualification, with no credentials or model calls:

```bash
bash run.sh --preflight-only
```

`--skip-build` verifies the existing immutable image ID, OCI source revision,
runtime digest and fresh task qualification; it never bypasses qualification.
The full 56-condition parent panel is recomputed even though this subset has 16
conditions. The package works with Docker-compatible Podman's bare image IDs.
Host Python 3.12+ and a CLI named `docker` are required. Override paths with
`NEXUS_REPO`, `MINDTRIAL_DIR` and `PYTHON` if needed. The pinned source is built
from a temporary Git archive, preserving your working checkout; the launcher
fetches the feature branch if the release commit is missing.

## Model settings

| Selector | Model | Effort | Credential |
|---|---|---|---|
| glm | GLM 5.2 | xhigh/max | OPENROUTER_API_KEY |
| muse | Muse Spark 1.2 Contributor | xhigh | OPENROUTER_API_KEY |
| minimax | MiniMax M3 | provider default | OPENROUTER_API_KEY |
| mistral | Mistral Large 4 | high | MISTRAL_API_KEY |
| grok | Grok 4.7 | medium | XAI_API_KEY |

Muse's Contributor endpoint permits Meta to use prompts and outputs to improve
its products. OpenRouter routing requires support for supplied parameters and
disables fallback. The route is not a pinned upstream provider. No external
search, Python or model-managed tools are enabled; only NEXUS is available.

The 65,536-token setting is a per-request completion ceiling, not a spending
cap. Tool/turn limits remain 600/650. All retries are disabled. Keep the shipped
settings for the planned comparison. Model/name/effort/RPM edits are recorded
as changed configurations; other contract edits are rejected. The files use
JSON syntax, which is valid YAML. Each model has a standalone config to avoid
requiring credentials for unused providers.

## Collect results

Each invocation creates a fresh folder under this package's `results/`, with
exact tasks, input/effective config, source/image identity, qualification,
MindTrial binary hash and run manifest. The `input_config_file` identifies the
model even though folder prefixes name the stage. Existing results are never
overwritten. Keep interrupted and failed attempts alongside reruns.

```bash
# Run from this package directory after evaluation:
python3 summarize_results.py results/controls-* results/screen-*
zip -r NEXUS-capability-smoke-results.zip results/
```

Send the complete results ZIP. Choose explicit folders if globs would mix
unintended repeats or preflight-only folders. The helper is an outcome readout,
not an independent replay/receipt audit; missing or empty JSON is reported as
zero completed records with missing expected slots; concurrent logs may have unknown access
classification. Raw MindTrial labels remain unchanged. The v3 readout adds terminal response
stops (including length with text), no-candidate errors, last observed world
status/actions remaining, detailed malformed-call accounting, effective-setting
drift and token-accounting totals. World state before validation and terminal
performance remain separate. Missing or ambiguous evidence stays unknown; the
readout does not certify supported wins or recover upstream provider metadata.
