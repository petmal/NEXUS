# Run the NEXUS P/R pilot

This package runs **16 tasks against GPT-6 Astra at medium reasoning**. Each task
gets a fresh persistent NEXUS service. The only model tool is NEXUS; external
Python is unavailable. The validator checks the actual terminal victory receipt.
No model calls are made by the build or preflight commands below.

The implementation is on `main` in
[petmal/NEXUS](https://github.com/petmal/NEXUS/pull/7). Build from the exact commit
listed in the downloaded package's `run-manifest.json`; keep that file with the
results. Main contains the earlier T/D checkpoint, not this P/R runner.

## Files

- `nexus-planning-resource-config.yaml`: provider, tool, persistent service and
  victory validator configuration.
- `nexus-planning-resource-tasks.yaml`: all 16 qualified task definitions.

Both files use JSON syntax, which is valid YAML and is accepted by MindTrial's
YAML loader. Keep them in the same directory. The API key is intentionally blank;
MindTrial reads `OPENAI_API_KEY` from the host environment. No API keys need to be
written into these files. Current token prices are not supplied; add an explicit
`pricing` block if you want cost estimates.

## Build and qualify the image

From the NEXUS checkout at the package's recorded commit:

```bash
docker build --build-arg VCS_REF="$(git rev-parse HEAD)" -t nexus:planning-resource-v1 .
docker image inspect nexus:planning-resource-v1 --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}'
docker run --rm --entrypoint python nexus:planning-resource-v1 scripts/preflight_planning.py
```

The build command works in Bash and PowerShell. Confirm the printed OCI revision
matches the checked-out commit and the preflight reports **16 cells passed**.
Use Docker Engine 25.0 or newer, as required by MindTrial task services. Rebuild
this image after any code change; do not reuse an older image under the same tag.

CI also runs the real NEXUS service process, stateless tool CLI, receipt validator
and shutdown telemetry inside the image for all 16 cells. It rejects wrong
receipts and verifies that submitting a forged receipt before play finalizes a
failed attempt. This is an integration check without a model, not a model result.

## Start the evaluation

Set `OPENAI_API_KEY` through your usual secret/environment setup. From the folder
containing the two YAML files, run:

```bash
mindtrial --config="nexus-planning-resource-config.yaml" --tasks="nexus-planning-resource-tasks.yaml" --json=true --verbose --evaluation-seed="nexus-pr-pilot-v1" run
```

The fixed evaluation seed records a reproducible harness identity. World seeds
are separately fixed in the task definitions. Logs and results are written under
`./nexus-pr/<date>/`; retain the `.json` and `.log` outputs. The command uses the
current MindTrial CLI and task-service configuration documented in its
[README](https://github.com/petmal/MindTrial/blob/main/README.md).

The runner enables one model configuration only. For a controlled comparison,
change its model/effort deliberately and keep a separate result set. No paid
evaluation was launched while preparing this package.

## What this run measures

Each of two physical fixtures has eight cells:

| Rows | Conditions | Comparison |
|---|---|---|
| 01–04 and 09–12 | T0, P0 through P3, R2 | Known laws; spatial layout and exact-budget planning |
| 05 and 13 | T0/P3/R1 | Extra action allowance for the same planning problem |
| 06 and 14 | T3/P0/R2 | Unknown-law investigation without travel |
| 07 and 15 | T3/P3/R2 | Unknown-law investigation with travel |
| 08 and 16 | T3/P3/R1 | Extra allowance for the same investigation and layout |

All cells use D5. Every map and machine location is disclosed. The environment
action allowances range from 10 to 158. The separate harness limits are **600
NEXUS tool calls and 650 conversation turns per task**, including free public
reads. These ceilings are deliberately above the public reference requirements.

At T0, R2 equals the exact minimum total cost. At T3, R2 equals the worst-case cost
of one public investigation policy; it is not proved optimal. T0/T3 comparisons
also change the budget, so they do not isolate theory difficulty. The fixtures
were selected for genuine route/transformation tradeoffs and are not a random
population sample.

Automatic **task retries are disabled** (`max-retry-attempts: 0`), so an error is
visible as one attempted cell. This differs from older sample configurations
which retried tasks. Provider/SDK request retries may still occur internally.
If infrastructure fails, keep the original record and label any rerun separately.

For the first read, inspect the slack known-law cells 05/13, then their R2 partners,
then the unknown-law cells. Separate physical wins, receipt-validation failures,
unsupported guesses, action exhaustion, harness limits and provider errors.
Keep the config, tasks, source revision/image digest and full logs together.
The [P/R guide](https://github.com/petmal/NEXUS/blob/main/docs/planning-resource-guide.md)
contains the mechanical guarantees and interpretation limits.
