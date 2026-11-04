# Run an evaluation

NEXUS supplies the world and checks actions. Your harness supplies the model,
inference settings, tool descriptions, retries, and stopping rules. Keep those
settings with the result: they are part of the experiment.

## Start one local service

From the repository, install with `uv sync --frozen --all-extras --python 3.14.7`.
Generate a compiled world, then start its non-resettable service:

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
starting with the initial observation. See [protocol details](reference/protocol.md).

## Use MindTrial

The maintained panel launchers package configs, tasks, a result summarizer, and
source bindings. Start with the [fresh-world guide](fresh-world-guide.md).
Older [capability](capability-smoke-guide.md), [cross-axis](cross-axis-guide.md),
and [P/R](planning-resource-guide.md) panels remain available for replication.
A source-bound report must match the image's actual runtime digest before a
launcher admits a run. An image tag alone is not sufficient.

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
