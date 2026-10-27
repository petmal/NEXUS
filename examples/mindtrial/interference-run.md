# NEXUS disclosed-interference pilot

This package tests longer required plans and interactions between coordinate goals.
It has **32 tasks**: four seeds × short/long targets × independent/coupled writes ×
exact/slack action budgets. The two suites each contain 16 tasks:

- `core`: exact optimum, including taking the seal and finishing (R2).
- `slack`: identical physical problems with extra actions (R1).

Every task discloses the laws, prerequisites, full current state and target. All
machines are in one room. The coupled long targets require 30–33 operations before
take/finish; the shorter targets require 16–19 in this matrix. Every coupled solution
must disturb a coordinate that already matches its target. The laws and proof are
new; difficulty has not yet been measured on models.

## Run locally

Extract the ZIP under `~/Downloads`. The launcher uses `~/Go-Projects/NEXUS` to build
the exact recorded commit and runs your local `~/MindTrial/mindtrial` interactively.
It preserves your checkout and any uncommitted work by building a temporary Git
archive. It fetches the release branch only if the pinned commit is missing.

```bash
cd ~/Downloads/NEXUS-interference-test-run-2026-10-26
# Optional qualification without API credentials or model calls:
bash run.sh --preflight-only

# Set OPENAI_API_KEY in your environment, then run both suites:
bash run.sh --suite all
```

To split the evaluation:

```bash
bash run.sh --suite core
bash run.sh --suite slack --skip-build
```

`--skip-build` still verifies the image revision, immutable image ID, runtime source
digest and freshly qualified task exports. Both Docker's `sha256:` IDs and Podman's
bare hexadecimal IDs are accepted. Host Python 3.12+ is required; the image uses
the repository's frozen Python 3.14.7 environment. Docker or its compatible Podman
CLI must be available as `docker`.

Paths can be overridden with `NEXUS_REPO` and `MINDTRIAL_DIR`. `PYTHON` selects the
host interpreter. The launcher invokes:

```text
./mindtrial -config=<absolute-result-dir>/config.yaml -tasks=<absolute-result-dir>/tasks.yaml --debug --interactive=true --json --evaluation-seed=nexus-interference-pilot-v1 run
```

Select **all 16 tasks in each suite** in MindTrial's interactive screen for the
planned matrix. A successful launcher exit can also follow an intentionally
selected subset, so retain the result JSON/log to establish actual evaluated rows.

## Configuration and results

The default is GPT-6 Astra, medium reasoning, 20 requests/minute, no automatic
retries. In `nexus-interference-config.yaml`, only provider-run `model`, `name`,
`model-parameters` and `max-requests-per-minute` may be edited. The files use JSON
syntax, which is valid YAML. Record model changes as a separate experiment.

Keep API keys out of files; use `OPENAI_API_KEY`. The launcher preserves your terminal
and interactive input. Each invocation creates a fresh directory under this
package's `results/`, containing the input/effective configurations, exact task
definitions, preflight, release identity, run manifest and MindTrial artifacts.
Archive the entire `results/` directory for analysis, including failed/interrupted
attempts. Do not replace failures with reruns.

The immutable image ID is bound into the tool, service and validator configurations.
The manifest records source revision, source/config/task hashes and the actual
MindTrial binary hash. Preflight uses no network and makes no model calls. It checks
all 32 cells before either suite runs.

## Interpretation

The independent condition has local interference too; coupling moves two write
destinations across banks while preserving all prerequisites and gains. Coupling
can shorten a minimum plan. The short/long comparison changes the target while
holding the law fixed, with a certified increase in required operations in both
conditions. These are construction strata, not calibrated difficulty levels.

The regression proof concerns individual coordinate targets, not necessarily a
whole completed bank. Bank revisits are necessary for optimal/R2 coupled solutions;
slack can admit longer bank-contiguous plans. Operators are physically reversible,
but recovery may exceed the remaining budget. Score mission completion, optimality,
goal-breaking operations and reported effort separately. The four kernels and
their repeated variants are not 32 independent sampled worlds.
