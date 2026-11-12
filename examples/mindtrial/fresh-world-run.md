# Run the fresh-world multi-model pilot

This package runs four models on 26 fresh conditions each, plus six historical
Astra anchors: **110 attempts maximum**, with no automatic repetitions. Live
model calls begin only when you run the launcher. The [design guide](../../docs/fresh-world-guide.md)
explains the matrix, exact costs, controls and interpretation limits.

## Small release canary

Before a larger run, check one model and provider on the candidate package:

```bash
bash run-canary.sh astra --preflight-only
bash run-canary.sh astra --skip-build
```

The first command builds and qualifies the pinned image without model calls or
API keys. The second makes **six paid attempts**, unattended: controls F01, F03,
F05 and F08, then the matched planning/resource pair F11/F12. Controls exercise
model revision and repair; the pair exercises the interference service with
disclosed laws, a short independent plan, and two action allowances. A failed
control gate or recognized provider interruption stops the next group.

Use `luna`, `flash` or `grok` instead of `astra` to check that model/provider path.
One model's canary does not validate another provider. `all` is intentionally not
accepted here; use the full-panel launcher for a multi-model study.

Keep all six result records and their manifests/logs. Confirm successful control
admission, complete output, receipt validation, and expected source/model/settings
bindings. Investigate a challenge loss from its trace: it can be a model outcome
and does not by itself prove a software defect. This is an integration check,
not a new estimate of model ability. Existing empirical reports remain separate.

## Recommended completion and confirmation panel

For the already completed screen, use a bounded follow-up instead of repeating
all 110 attempts. On a new runtime, obtain fresh matching controls first. These
commands run 12 controls and 16 selected challenges, without interactive prompts.
Run them from the unpacked package directory with credentials already configured.
They make paid model calls; run preflight alone if you only want to check setup.

```bash
bash <<'BASH'
set -euo pipefail
bash run.sh --model all --suite fresh --preflight-only
bash run.sh --model astra --suite controls --non-interactive --skip-build
bash run.sh --model flash --suite controls --non-interactive --skip-build
bash run.sh --model grok --suite controls --non-interactive --skip-build
bash run.sh --model flash --suite challenges --non-interactive --skip-build \
  --task-id F17 --task-id F18 --task-id F19 --task-id F20 --task-id F21 \
  --task-id F22 --task-id F23 --task-id F24 --task-id F25 --task-id F26
bash run.sh --model grok --suite pr-b --non-interactive --skip-build \
  --task-id F25 --task-id F26
bash run.sh --model astra --suite pr-b --non-interactive --skip-build \
  --task-id F21 --task-id F22 --repeat 2
BASH
```

Stop if a command fails; preserve its output and fix the reported problem before
continuing. Each challenge invocation checks matching control admission. Keep new
attempts alongside earlier results and report their new runtime binding separately.

## Complete unattended run

Unpack the ZIP in ~/Downloads. From a terminal with your provider credentials
already configured:

```bash
git -C "$HOME/Go-Projects/NEXUS" fetch origin
cd "$HOME/Downloads/NEXUS-fresh-world-release-candidate"
bash run-all.sh
```

The required environment variables are OPENAI_API_KEY, GOOGLE_API_KEY and
XAI_API_KEY. Use your existing credential setup; keys do not belong in this
package. OPENROUTER_API_KEY is not needed.

The script builds the pinned release commit from ~/Go-Projects/NEXUS into
nexus:fresh-world-v1, checks the image and mechanically qualifies all 32 fixtures.
It runs the locally built ~/MindTrial/mindtrial with debug logs, JSON output and
--interactive=false. Your repository working tree is not switched or overwritten.
The first job is the six-row Astra anchor. Then Astra, Luna, Flash and Grok each
run controls → td → pr-a → pr-b. The second invocation reuses the image and
requalifies it. No confirmation is needed between groups.

Host Python 3.12+, Docker, the release commit in your local clone and your local
MindTrial binary are required. The image uses the repository's pinned Python and
dependencies. Override paths with NEXUS_REPO, MINDTRIAL_DIR or PYTHON when needed.
If fetch does not bring in the feature commit, fetch the feature branch explicitly:

```bash
git -C "$HOME/Go-Projects/NEXUS" fetch origin feat/planning-resource-axes
```

## Preflight or selected runs

Qualify without model calls or provider keys:

```bash
bash run.sh --model all --suite fresh --preflight-only
```

Run one model, including its four fresh controls:

```bash
bash run.sh --model luna --suite fresh --non-interactive --skip-build
```

--skip-build is appropriate after this package's image was built successfully.
Omit it otherwise. Each invocation checks the immutable image identity and repeats
qualification before starting model calls.

| Suite | Exact rows | Tasks per model |
|---|---|---:|
| anchor | S05, S08, S21, S22, S23, S24 | 6 |
| controls | F01, F03, F05, F08 | 4 |
| td | F02, F04, F06, F07, F09, F10 | 6 |
| pr-a | F11–F18 | 8 |
| pr-b | F19–F26 | 8 |
| fresh | controls, td, pr-a, pr-b | 26 |
| challenges | td, pr-a, pr-b | 22 |

Model selectors are astra, luna, flash, grok or all. Using --suite all includes
anchors for every selected model; the default run-all.sh deliberately anchors
only Astra. A bare run.sh defaults to controls for all models and interactive
selection. Use --non-interactive for unattended work.

## Stops, resumption and selected reruns

The batch halts on recognized provider HTTP errors (including 402, 429 and 5xx),
incomplete results, interruption, launcher failure or
a failed fresh-control gate. It does not automatically retry. Ordinary completed
challenge losses do not stop later tasks.

All four fresh controls must have accepted receipts in this package's results
under the same release, Docker image ID, MindTrial binary, exact input config and evaluation seed before
that model can start challenges. Recorded inference settings and qualified task
objects must also match. The launcher reconstructs the effective configuration, including the player tool and validator, using the saved output location and image ID. A newer failed control supersedes an older success. If two latest attempts for one control have the same start time, preserve both and rerun that control. For an unattended group, a row from the wrong model, settings or seed stops the batch even when all task names are present.

A control folder with a missing, unreadable or invalid manifest blocks admission:
the launcher cannot safely decide which attempt it represents. Restore the
original manifest where possible. Otherwise preserve the entire damaged folder
outside `results/` for inspection, record why it was moved, and rerun the affected
controls (all four if their identity is unknown). Include that preserved folder
when sharing results. Do not discard a known failure to restore an older pass.
Well-formed records for other releases, binaries or configurations are ignored.

After diagnosing a failed control, a selected rerun can fill the control record.
Then resume the remaining suite without rerunning completed challenges:

```bash
bash run.sh --model grok --suite controls --task-id F05 --interactive --skip-build
bash run.sh --model grok --suite challenges --non-interactive --skip-build
```

The second command resumes all challenges for Grok. If some already completed,
choose only the outstanding suite/rows instead. This is an explicit selection,
not automatic checkpoint recovery.

For an exact fresh resource pair with two indexed repetitions:

```bash
bash run.sh --model luna --suite pr-a --task-id F17 --task-id F18 \
  --repeat 2 --non-interactive --skip-build
```

Use --interactive when selecting tasks in MindTrial. Selecting all desired rows
through --task-id plus --non-interactive avoids prompts. Repetitions create
separate folders and retain the same world/evaluation seeds. A changed model config, different image ID
or rebuilt MindTrial binary needs new matching controls; do not reuse earlier
admission as if it were the same condition.

Astra anchor task failure does not block fresh controls; its purpose is historical
comparison. The fresh control gate is operational receipt/configuration checking,
not a substitute for the later trace/replay audit.

## Collect the results

Every group has its own results/<suite>-<timestamp>-<suffix>/ directory, including
manifest.json, effective and input configs, selected tasks, release/preflight
records, and MindTrial JSON/log/HTML output when produced. Keep incomplete folders,
too. Challenge manifests identify the control results that admitted the run.

For a convenience readout and one upload archive:

```bash
python3 summarize_results.py --help
zip -r fresh-world-results.zip results release.json README.md guide.md matrix.json \
  nexus-fresh-world-*-config.yaml nexus-fresh-world-*-tasks.yaml
```

The convenience readout is not canonical replay or receipt re-verification.
Return fresh-world-results.zip, including all attempted runs. Do not delete earlier
failures after a successful rerun. Control admission hashes records from this
package; moving result folders to another package does not provide automatic
portable admission.

Newly built panels require MindTrial v0.26.0 or newer. The launcher adds the audit mount and service-instance input to the effective run files after qualification. The supplied tasks, prompts and player tools remain the same. Private exports are in `private-audits/<run-folder>/<service-instance>/` **beside** `results/`, outside the ZIP command above. The manifest identifies the parent; the debug log links each service name to its result trace. Keep failed attempts as well as successes. Verify each export with the matching NEXUS image or source; an unclosed bundle is partial evidence. Old result folders do not acquire bundles. See the [audit storage contract](../../docs/research-guide.md#reproducibility-record).

## Regenerate from the repository

```bash
uv run --frozen --python 3.14.7 python scripts/fresh_worlds.py \
  --output docs/research/fresh-world-preflight-current.json \
  --tasks-output examples/mindtrial
uv run --frozen --python 3.14.7 python scripts/export_fresh_world_configs.py
# Commit the qualified artifacts first; packaging requires a clean checkout.
uv run --frozen --python 3.14.7 python scripts/package_fresh_world.py \
  --output-dir /absolute/path/NEXUS-fresh-world-release-candidate \
  --runtime-source-sha256 "$(uv run --frozen python -c 'from nexus.provenance import source_digest; print(source_digest())')"
```
