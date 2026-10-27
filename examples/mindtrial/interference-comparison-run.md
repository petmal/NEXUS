# NEXUS two-model interference comparison

Compare **GPT-6 Astra (medium)** and **GPT-6 Luna (medium)** on the same 32
qualified v1 tasks: four seeds × short/long targets × independent/coupled writes
× exact/slack action budgets. Both model runs are enabled, each at 20
requests/minute, with no automatic retries. The complete comparison is
**32 tasks × 2 models = 64 attempts**.

The suites each contain 16 rows:

- `core`: exact optimal action allowance, including taking the seal and finishing (R2).
- `slack`: the same physical problems with extra actions (R1).

Every task discloses the laws, prerequisites, complete state and target. The
physical worlds, neutral tool description and harness limits match the original
interference pilot. Structural qualification adds exact machine-block and
whole-bank reopening metrics. The bounded three-bank proposal did not meet its
admission threshold; this package introduces no new harder family. Anchor rows
11, 12, 27 and 28 are already included in the full matrix.

## Run locally

Extract the ZIP under `~/Downloads`. The launcher builds the exact recorded
commit from `~/Go-Projects/NEXUS` and uses your existing
`~/MindTrial/mindtrial` binary interactively. It preserves your checkout and
uncommitted work by building a temporary Git archive. It fetches the release
branch only if the pinned commit is missing.

```bash
cd ~/Downloads/NEXUS-interference-comparison-test-run-2026-10-27
# Optional qualification without API credentials or model calls:
bash run.sh --preflight-only --suite all

# Set OPENAI_API_KEY in your environment, then run both suites:
bash run.sh --suite all
```

In **each** MindTrial interactive screen, select **both model runs** and **all
16 task rows**. This produces 32 attempts per suite and 64 across both suites.
Selecting fewer models or rows produces a partial matrix, even if the launcher
exits successfully. Retain the result JSON and log to establish what ran.

To split the evaluation:

```bash
bash run.sh --suite core
bash run.sh --suite slack --skip-build
```

`--skip-build` still verifies the image revision, immutable image ID, runtime
source digest and freshly qualified exports. Both Docker's `sha256:` IDs and
Podman's bare hexadecimal IDs are accepted. Host Python 3.12+ is required; the
image uses the repository's frozen Python 3.14.7 environment. Docker or its
compatible Podman CLI must be available as `docker`.

Override paths with `NEXUS_REPO` and `MINDTRIAL_DIR`; `PYTHON` selects the host
interpreter. The launcher invokes:

```text
./mindtrial -config=<absolute-result-dir>/config.yaml -tasks=<absolute-result-dir>/tasks.yaml --debug --interactive=true --json --evaluation-seed=nexus-interference-comparison-pilot-v1 run
```

## Configuration and results

Keep the shipped models and medium reasoning for this comparison. The config
permits edits only to provider-run `model`, `name`, `model-parameters` and
`max-requests-per-minute`; any changes define a separate experiment and are
recorded in the run manifest. Both runs must remain present and enabled. The
config and task files use JSON syntax, which is valid YAML.

Keep API keys out of files; use `OPENAI_API_KEY`. The launcher preserves your
terminal and interactive input. Each suite creates a fresh directory under this
package's `results/`, with input/effective configs, exact tasks, preflight,
release identity, run manifest and MindTrial artifacts. Archive the entire
`results/` directory, including failed or interrupted attempts. Do not replace
failures with reruns.

Optionally summarize the collected result folders with the included host helper:

```bash
python3 summarize_results.py results/core-* results/slack-*
```

The helper checks recorded config/task hashes and reports coverage against the
64-attempt matrix, per-model reported outcomes and timings. It separates the
wait before the first logged task from task execution time. Include only the
intended attempt folders; broad globs can also include reruns. This summary
does not replay episodes or audit victory receipts.

The immutable image ID is bound into the tool, service and validator configs.
The manifest records source revision, source/config/task hashes and the actual
MindTrial binary hash. Preflight uses no network and makes no model calls. It
checks all 32 rows before either suite starts. The launcher does not claim that
an interactive selection completed the full comparison.

## Interpretation

Report model outcomes separately for exact and slack budgets and distinguish
success from optimality, machine blocks, coordinate goal breaks and whole-bank
reopenings. Coupling can shorten a minimum plan. Minimum blocks across all
successful paths and minimum blocks on optimal paths answer different questions;
slack can allow longer paths with fewer blocks. The four kernels and their
repeated variants are not 32 independent sampled worlds.

See `guide.md` for metric definitions and the analysis plan. `reports/` contains
the structural preflight, bounded three-bank feasibility result and implementation
validation. These are offline qualification records, not model results.
