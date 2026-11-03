# Run the fresh-world multi-model pilot

This package runs four models on 26 fresh conditions each, plus six historical
Astra anchors: **110 attempts maximum**, with no automatic repetitions. Live
model calls begin only when you run the launcher. The [design guide](../../docs/fresh-world-guide.md)
explains the matrix, exact costs, controls and interpretation limits.

## Complete unattended run

Unpack the ZIP in ~/Downloads. From a terminal with your provider credentials
already configured:

```bash
git -C "$HOME/Go-Projects/NEXUS" fetch origin
cd "$HOME/Downloads/NEXUS-fresh-world-test-run-2026-11-03"
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

The batch halts on HTTP 429, incomplete results, interruption, launcher failure or
a failed fresh-control gate. It does not automatically retry. Ordinary completed
challenge losses do not stop later tasks.

All four fresh controls must have accepted receipts in this package's results
under the same release, binary, exact input config and evaluation seed before
that model can start challenges. Recorded inference settings and qualified task
objects must also match. A newer failed control supersedes an older success.

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
separate folders and retain the same world/evaluation seeds. A changed model config
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

## Regenerate from the repository

```bash
uv run --frozen --python 3.14.7 python scripts/fresh_worlds.py \
  --output docs/research/fresh-world-preflight-2026-11-03.json \
  --tasks-output examples/mindtrial
uv run --frozen --python 3.14.7 python scripts/export_fresh_world_configs.py
# Commit the qualified artifacts first; packaging requires a clean checkout.
uv run --frozen --python 3.14.7 python scripts/package_fresh_world.py \
  --output-dir /absolute/path/NEXUS-fresh-world-test-run-2026-11-03 \
  --runtime-source-sha256 ba22502788acf7ce1684e1e527e5aa332cd1746b37423fececabc90d71b8ee83
```
