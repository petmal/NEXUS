# NEXUS five-model smoke run

Five models, 16 unchanged conditions each: **80 attempts** if all proceed.
Start with ten control attempts; then run seventy challenge attempts. See
`guide.md` for the exact row mapping, settings and analysis rules, and
`reports/smoke-findings-2026-10-31.md` for the consolidated earlier findings.

## Current recommendation after the control run

Read `reports/capability-controls-results-2026-10-31.md`. Grok passed both
controls; Muse solved both worlds but added prose to one final receipt. GLM and
MiniMax now have corrected text-output presets; Mistral still needs response
diagnostics before challenge runs. This v3 package sets run-level
`disable-structured-output: true` for GLM and MiniMax, matching the compatibility
setting the user reports needing in prior MindTrial evaluation. Their run names
now include “text output.” Other model settings, tasks, world mechanics, seeds
and receipt validation remain unchanged. The unattended options from v2 remain.

Repeat **S05 and S21 for both GLM and MiniMax**, four attempts total:

```bash
cd ~/Downloads/NEXUS-capability-smoke-test-run-2026-10-31-v3
bash run.sh --model glm --suite controls --non-interactive &&
bash run.sh --model minimax --suite controls --non-interactive --skip-build
```

Set `OPENROUTER_API_KEY` first. The first command builds the new pinned source;
the second reuses it. Keep the original structured-output results separately.
Do not run these models' challenge rows until their controls demonstrate working
interaction. These reruns test the output-mode explanation; success is not yet
known. Do not alter tool/turn limits or reasoning effort for this comparison.
The flag belongs beside `model` under a provider run, not in `model-parameters`.
The tool argument schema remains enabled.

Grok can independently run its fourteen remaining rows (omit this if already run):

```bash
cd ~/Downloads/NEXUS-capability-smoke-test-run-2026-10-31-v3
bash run.sh --model grok --suite screen --non-interactive
```

This builds the new pinned source using `~/Go-Projects/NEXUS`, then runs your
`~/MindTrial/mindtrial` without confirmation prompts. Set `XAI_API_KEY` first.
Use `--skip-build` if you already built v3 while running GLM. Otherwise build
once: the required source revision changed even though the runtime is identical.

For Muse, repeat **S21 only** using the interactive picker, retaining both attempts:

```bash
bash run.sh --model muse --suite controls --interactive --skip-build
```

Set `OPENROUTER_API_KEY`, then select S21 only. If exact receipt delivery works,
run its remaining fourteen rows with `--model muse --suite screen
--non-interactive --skip-build`. Do not repeat Grok's controls. GLM/MiniMax
challenge panels wait for the new controls; Mistral remains held for response diagnostics.

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
records count as recorded outcomes and do not halt a complete batch.

Non-interactive runs check that exactly one result exists for every enabled
provider/run/task. A zero MindTrial exit with missing, empty, malformed,
duplicated or unexpected records stops the batch with launcher exit code 2.
The manifest retains the actual child `exit_code`, `launcher_exit_code`, mode
and result coverage. Any nonzero child exit also stops the batch. Existing
results remain intact; resume remaining groups explicitly to avoid repeats.
Interactive subsets do not require full-matrix coverage. Their zero process
exit alone still does not certify a complete evaluation.

The remaining instructions describe the original panel and general operation.

## Run from Downloads

Extract this package under `~/Downloads`. Set the three credential environment
variables in your shell: `OPENROUTER_API_KEY`, `MISTRAL_API_KEY`, `XAI_API_KEY`.
Keys stay out of files. The launcher builds the pinned NEXUS commit using your
clone at `~/Go-Projects/NEXUS`, then invokes your locally built
`~/MindTrial/mindtrial` with `--debug --interactive=true --json`.

```bash
cd ~/Downloads/NEXUS-capability-smoke-test-run-2026-10-31-v3
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
classification. It does not turn a failed mission into a provider failure or
certify evidence-supported wins.
