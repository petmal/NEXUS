# Operator handoff: bounded T/D cycle

Apply the complete patch series to a clean feature branch based on
`6f346411a7b00d6e530412cbc143aecf2fdfa49d`. Intermediate patches intentionally do
not refresh the global repair source binding; apply all patches before qualifying
or building. Nothing in this handoff requires a push or merge.

```sh
git switch -c td-cycle-review 6f346411a7b00d6e530412cbc143aecf2fdfa49d
git am /absolute/path/to/patches/*.patch
uv sync --frozen --all-extras
uv run --frozen python scripts/preflight_td_cycle.py --output /tmp/td-cycle-preflight.json
uv run --frozen python scripts/qualify_td_prototypes.py --output /tmp/td-prototypes.json
uv run --frozen python scripts/export_td_cycle.py --preflight /tmp/td-cycle-preflight.json --output /tmp/td-cycle-harness --image nexus:td-cycle-v1
```

These commands perform local exact analysis and export only. No provider is called.
The exporter rejects incomplete/stale qualification and altered source templates.
The generated manifest binds source, matrix, template, prompts, inputs and output
files. Keep all of this operator-only. No Python/shell/source access is supplied to
evaluated players.

## Build the image before live evaluation

Docker/Podman was not available in the implementation workspace. Run the image
preflight on the built image, and regenerate/verify the export against that exact
source before using it. The default tag is an operator placeholder, not an image
that was built, uploaded or verified here.

```sh
mkdir -p td-operator-output
podman build --build-arg VCS_REF="$(git rev-parse HEAD)" -t nexus:td-cycle-v1 .
podman image inspect nexus:td-cycle-v1 > td-operator-output/image-inspect.json
podman run --rm --entrypoint python -v "$PWD/td-operator-output:/out" nexus:td-cycle-v1 scripts/preflight_td_cycle.py --output /out/image-preflight.json
uv run --frozen python scripts/export_td_cycle.py --preflight td-operator-output/image-preflight.json --output td-operator-output/harness --image nexus:td-cycle-v1
```

Use `docker` in place of `podman` if preferred. These are POSIX-shell examples.
Require the OCI revision label to identify the applied commit and retain the image
ID; if using a registry, retain its immutable digest. The same image reference must
be used in tool, service and validator. The exporter sets all three.

The container normalizes source line endings. If an export rejects a local checkout
because its source digest differs from the image, inspect the mismatch; use a clean
LF checkout (or the repository's `scripts/prepare_package.py` normalization) and
rerun qualification. Do not edit recorded hashes to make the gate pass.

## Five generated pairs, 40 planned executions

| Config/tasks prefix | Provider/model configuration | Executions |
|---|---|---:|
| `baseline` | Astra, inherited medium reasoning | 24 |
| `single-shot` | Same Astra settings | 10 |
| `consistency-baseline` | Gemini 3.8 Flash, inherited high thinking | 2 |
| `consistency-prompt` | Same Gemini settings | 2 |
| `consistency-checker` | Same Gemini settings | 2 |

Each prefix has `-config.yaml` and `-tasks.yaml`; keep each pair together. Files use
JSON syntax, which is valid YAML 1.2. Provider credentials are empty. The source
harness is pinned; use your existing credential mechanism on exported copies and
retain redacted final configuration identities. Changing model/effort, task prompts,
permissions, caps or retry policy changes the experiment and must be documented.
No current model availability or price estimate was independently asserted.

Only one provider/run is enabled in each config. Task IDs encode case and repeat;
each execution must start with fresh model context and a fresh non-resettable
service. Do not carry conversations or service state across repeats. Use the
existing harness's config-loading and schema/smoke validation flow; its executable
and schema were unavailable here, so no unverified command-line syntax is supplied.

The order in each exported batch is fixed for reproducibility. To control temporal
provider drift, the operator may use a recorded, predetermined interleaving across
paired arms; do not choose order based on observed outcomes. Keep every planned
execution ID and preserve actual timestamps/order in the ledger.

## Result capture and interpretation

Fill `run-ledger.json` from observed artifacts. Capture harness version, image ID and
revision, runtime source digest, exact available provider/model version and effort,
start/end times, retries, token usage, tool calls, world actions, raw provider stop
reason, terminal classification, and exact receipt-validator result. Preserve full
service logs and tool history with file hashes. A missing provider stop reason stays
null. A service shutdown does not establish why the model stopped.

The service logs `binding`, committed `action`, full `report` and bounded
`NEXUS operator summary` entries. Witnesses are in the full report; the summary is
limited to 4096 bytes and contains counts. Joining runtime source identity to the
manifest is required before treating an execution as part of this matrix. A runtime
receipt must come from successful finish; correct construction, support and receipt
submission are distinct outcomes.

Keep the failed first attempt when a provider retry succeeds. Distinguish provider
transport errors, output/tool caps, action exhaustion, single-shot rejection,
ordinary unsupported/contradicted decisions, physical execution and receipt errors.
The service cannot observe the provider or parser, and this code does not pretend
to retrofit the external harness with automatic provider telemetry.

Record per-condition denominators. Two repeats are a screening aid. The selected
worlds are not a random population sample; rival pairs and topology variants are
not new independent structural groups. Use first-submission support and operational
success side by side, and keep actions/readings/tokens/time as separate quantities.

After the 40 planned executions, stop. Select at most one follow-up batch within the
20-run reserve after specifying the contrast, practical effect, fresh structural
cases and interruption treatment. No reserve tasks are pre-generated. W4 did not
qualify for a model pilot in this implementation; the cascade currently provides
an operator proof/specification, not a playable family.

Read `docs/td-cycle-results.md` for corrected C/L* interpretations and prototype
counterexamples. Do not share this guide, matrix, source, seeds, manifests or
qualification reports with the evaluated model.
