# Run an evaluation

NEXUS supplies the world and checks actions. Your harness supplies the model,
inference settings, tool descriptions, retries, and stopping rules. Keep those
settings with the result: they are part of the experiment. For your first model,
use the [one-task MindTrial tutorial](first-model.md). For a comparison, start
with the [worked budget pair](benchmark-guide.md).

The maintained MindTrial run presets use v0.27.0 or newer to request official
summaries from supported models. The OpenAI presets use `reasoning-summary: auto`,
the Google presets use `thinking-summaries: auto`, and the Claude presets with
adaptive effort use `thinking-display: summarized`. Look in the MindTrial INFO
log for summaries returned between tool calls. The Alibaba presets use Qwen3.8;
Alibaba documents summarized display for Qwen4-Max with thinking and thinking
preservation both enabled. See the [MindTrial provider settings](https://github.com/petmal/MindTrial#basic-usage).

## Start one local service

From the repository, install with `uv sync --frozen --all-extras --python 3.14.7`.
Generate a compiled world into a new or empty directory, then start its
non-resettable service. Use fresh paths for a new attempt; keep the original
world and audit directory if you want to reproduce the first one:

```bash
uv run --frozen nexus generate ./trial-world --seed 17 --planning-level 0
uv run --frozen nexus serve-session --private ./trial-world/private.json \
  --audit-dir ./trial-audit --extended-diagnostics
```

The default address is `http://127.0.0.1:8000`. In another terminal:

```bash
curl http://127.0.0.1:8000/manifest
curl http://127.0.0.1:8000/observe
curl -H 'Content-Type: application/json' http://127.0.0.1:8000/action \
  -d '{"expected_turn":0,"action":{"type":"wait"}}'
```

This last request deliberately spends one action. A real player should read the
mission and evidence first. An action request has an integer `expected_turn`
and a JSON `action`. Repeating the same action at the same turn returns the
cached result, marked as a duplicate, without charging twice. A different stale
request is a conflict. Use the returned turn for the next action.

Player tools should expose the manifest, listed evidence, observation, actions,
status and, where supported, the public construction checker. The evaluator
alone calls `nexus validate` or `/finalize` after the attempt. Finalization is
irreversible; it marks an unfinished world failed and exposes terminal metrics.
Stopping the service normally closes its audit bundle without inventing a loss
for a still-active world.

After stopping the server with Ctrl-C, verify the private export:

```bash
uv run --frozen nexus verify-audit ./trial-audit --json
```

Use a new directory for every attempt. See [research records](research-guide.md)
for what this verifies. The simpler JSONL transport also supports
`nexus stdio ./trial-world/private.json --audit-dir ./stdio-audit`; stdout is JSONL,
starting with the initial observation. A JSONL-only player can request its mission
and evidence through that stream. For clients that retry actions after timeouts,
send the original turn with the action. See [protocol details](reference/protocol.md).

## Use MindTrial

The current tutorial and panel launcher require MindTrial v0.26.0+ for private audit mounts. The service alone gets the writable directory. Each service attempt writes a separate bundle; the provider log and result JSON stay separate. For the panel, find the parent in `manifest.json` under `private_audit_dir` or at `private-audits/<run-folder>/` beside `results/`. On SELinux, prepare that dedicated parent with a container-accessible label before running the panel. See the [mount smoke](first-model.md#test-that-the-mount-works) to test your setup without spending provider credits.

The maintained panel launchers package configs, tasks, a result summarizer, and
source bindings. Start with the [fresh-world guide](fresh-world-guide.md).
Older [capability](capability-smoke-guide.md), [cross-axis](cross-axis-guide.md),
and [P/R](planning-resource-guide.md) panels remain available for replication.
A source-bound report must match the image's actual runtime digest before a
launcher admits a run. An image tag alone is not sufficient.

To build the current panel from a **clean, committed** NEXUS checkout (Bash):

```bash
export NEXUS_REPO="$PWD"
export MINDTRIAL_DIR="$HOME/MindTrial"  # directory containing the mindtrial executable
runtime=$(uv run --frozen --all-extras python -c 'from nexus.provenance import source_digest; print(source_digest())')
uv run --frozen --all-extras python scripts/package_fresh_world.py \
  --output-dir ../nexus-fresh-panel --runtime-source-sha256 "$runtime"
cd ../nexus-fresh-panel
bash run-canary.sh luna --preflight-only
```

The package command also writes a ZIP for use on a different machine. Use a new
destination. Preflight requires Docker but makes no model calls. To run the six
selected attempts with credentials configured, use `bash run-canary.sh luna --skip-build`.
The canary supports four fixed presets; for other endpoints use the single-model
tutorial or build a separate matched experiment. The [panel run guide](../examples/mindtrial/fresh-world-run.md)
lists groups, admission rules and results directories.

Run `bash run.sh --help` in the unpacked package. Use non-interactive mode for an
unattended full group; choose interactive mode when selecting tasks or models.
Controls must pass for the same model/settings and release before challenges.
The launcher preserves failed results and stops later groups/repetitions after
recognized billing, quota, rate-limit, authentication, permission or server
errors. It cannot cancel tasks already running inside a MindTrial group. Resume
only after fixing the provider issue, preserving the original and rerun artifacts.

For models with tool/structured-output incompatibilities, use the declared
`disable-structured-output: true` setting and rerun matched controls. Do not
silently combine those results with a different protocol configuration.

## Keep the boundary clear

Keep the compiled world, generator seed, verifier secret, service logs, and audit
bundle outside the evaluated player's filesystem and process access. Exported
`manifest.json` and `attachments/` are player-safe. The internal Python
`PublicEpisode` is trusted nonsecret engine data, not a player projection.

This is a local experimental service, with no authentication or tenant isolation.
Use a harness-managed network/container boundary; do not expose its port to the
public internet. The hidden `/finalize` route is not an authorization mechanism.
See [security scope](../SECURITY.md). Local human play is for exploration, not a
sandbox against the person controlling the computer.
