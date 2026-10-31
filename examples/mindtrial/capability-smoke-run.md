# NEXUS five-model smoke run

Five models, 16 unchanged conditions each: **80 attempts** if all proceed.
Start with ten control attempts; then run seventy challenge attempts. See
`guide.md` for the exact row mapping, settings and analysis rules, and
`reports/smoke-findings-2026-10-31.md` for the consolidated earlier findings.

## Run from Downloads

Extract this package under `~/Downloads`. Set the three credential environment
variables in your shell: `OPENROUTER_API_KEY`, `MISTRAL_API_KEY`, `XAI_API_KEY`.
Keys stay out of files. The launcher builds the pinned NEXUS commit using your
clone at `~/Go-Projects/NEXUS`, then invokes your locally built
`~/MindTrial/mindtrial` with `--debug --interactive=true --json`.

```bash
cd ~/Downloads/NEXUS-capability-smoke-test-run-2026-10-31
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
not an independent replay/receipt audit; concurrent logs may have unknown access
classification. It does not turn a failed mission into a provider failure or
certify evidence-supported wins.
