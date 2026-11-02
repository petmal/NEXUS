# Focused follow-up after the smaller-model repetitions

1 November 2026. This is an operator plan; no live evaluation has been run.
The [latest synthesis](research/smaller-model-synthesis-2026-11-01.md) supplies
the rationale. The first two questions are whether MiniMax's response behavior
is reproducible and whether GLM's long-plan stops depend on its effort setting.
Keep these separate from physical-resource and intrinsic-discovery claims.

The NEXUS changes are limited to the operator readout, launcher and documentation.
All 204 focused tests pass. The revised readout reproduces the audited stopping
categories on all 46 compiled attempts, including the two length-with-text cases.
See the [regression record](research/inference-diagnostic-validation-2026-11-01.json).
The world runtime digest is unchanged. Docker is unavailable in the development
environment; the packaged launcher will recompute qualification locally before
any model call. Provider-level response changes still need live diagnosis.

## Recommended first wave

| Stage | Configuration | Exact rows | Repetitions per row | Attempts | Purpose / admission |
|---|---|---|---:|---:|---|
| A | MiniMax M3, existing default/text-output preset | S05, S21 | 2 | 4 | Recheck disclosed multi-turn controls and response/usage behavior. Inspect before B. |
| B | Same MiniMax configuration | interference 09, 25 | 1 | 2 | Short tight/slack pair, only if A has interpretable responses and working tools/receipt delivery. |
| C | GLM 5.2 **high**, text output, otherwise unchanged | S05, S21, interference 09, 25 | 1 | 4 | Admit the new effort setting and check simple execution. Inspect before D. |
| D | GLM 5.2 xhigh and high, separately labelled | interference 11, 27 | 2 per setting | 8 | Same long tight/slack worlds, changing effort only. Contemporary xhigh attempts complement the existing baseline. |

Maximum first-wave size: **18 attempts**, subject to the gates. A and C are
independent and can be scheduled separately. Do not automatically advance from
controls to challenges merely because MindTrial exits zero. A legitimate world
loss is data; recurring empty responses, malformed tool use or unreadable usage
semantics require diagnosis. Retain every attempt, including stopped batches.

Keep the 65,536 completion ceiling, zero retries, 600-call/650-turn ceilings,
RPM, model IDs, tool schema, world inputs and `nexus-cross-axis-pilot-v1` seed.
GLM high/xhigh is an inference-setting comparison, not a pure world-axis effect
or an equal-compute comparison. A lower effort may reduce a length stop while
also weakening reasoning; measure success, evidence support, actions and usage.

For D, alternate settings across two blocks (high then xhigh; xhigh then high)
where practical, preserving within-suite row order. Do not retry until success.
Two attempts only screen repeatability; they do not calibrate a probability.

OpenRouter documents both GLM `high` and `xhigh` support; `xhigh` maps to max.
See [the model page](https://openrouter.ai/z-ai/glm-5.2), checked 1 November 2026.
The alternative changes effort, **not** the completion ceiling. Do not silently
change settings if a route rejects it. Treat that as an integration outcome.

## Using the revised launcher

The capability package retains its five original presets and full qualified
parent matrix. The new selectors avoid manually deleting tasks or confirming
each unattended run. Set the applicable API-key environment variable first.

```bash
cd ~/Downloads/NEXUS-capability-diagnostics-2026-11-01

# Stage A: build the pinned image once, then run four attempts unattended.
bash run.sh --model minimax --suite controls --repeat 2 --non-interactive

# Stage B: run only after inspecting A.
bash run.sh --model minimax --suite screen --task-id 09 --task-id 25 \
  --non-interactive --skip-build
```

For C/D, change only the GLM run name and `model-parameters.reasoning-effort`
to `high` in `nexus-capability-smoke-glm-config.yaml`. These are documented
editable fields; the launcher records the exact input/effective configuration
and marks its difference from the shipped preset. Use a distinct name such as
`GLM 5.2 high - inference diagnostic (text output)`. Keep
`disable-structured-output: true` at run level. Preserve a copy of the shipped
file outside the package before editing; restore it for the xhigh arm.

```bash
# Stage C with the high preset selected as described above:
bash run.sh --model glm --suite all --task-id S05 --task-id S21 \
  --task-id 09 --task-id 25 --non-interactive --skip-build

# One block of D under the currently selected GLM effort; run each setting
# once in each of the two blocks, restoring/editing the config between arms.
bash run.sh --model glm --suite screen --task-id 11 --task-id 27 \
  --non-interactive --skip-build
```

`--task-id` filters only whole verified task objects. It rejects unknown,
duplicate or ambiguous row identifiers before build/model calls. Full runtime
qualification still runs; the original full preflight and exact selected task
file are both retained. Repetitions use separate folders with indexed manifests.
Interactive mode remains available for further manual selection, whose full
coverage cannot be inferred from the configured task file alone.

After each stage, run the readout on the explicit folders produced by that stage:

```bash
python3 summarize_results.py results/<first-folder> results/<second-folder>
```

Use actual folder names in place of the placeholders. Keep complete logs and
JSON records, not just the readout. The readout preserves raw scores and reports
response-length stops with/without returned text, empty candidates, world-budget
losses and receipt delivery separately. Its last observed world state is not a
replay certificate. Token sums are reported accounting, not a spending limit.

## Provenance and decisions

MiniMax's prior anomaly cannot be fixed by changing NEXUS world mechanics.
Where available, retain OpenRouter generation/request IDs, upstream provider,
returned model identifier, native finish reason and per-response usage. The
current artifacts do not expose all of these fields. NEXUS cannot manufacture
them or prove the provider's reasoning mode from aggregate token counts.

The existing routing flags require parameter support and disable fallbacks,
but do not pin one provider across requests. If a supported endpoint can be
verified and pinned, treat it as a separately labelled route diagnostic and
rerun controls; do not merge it into the old cohort. See
[OpenRouter provider routing](https://openrouter.ai/docs/guides/routing/provider-selection).
No public MindTrial changes are part of this NEXUS refinement.

- If MiniMax A is again inconsistent, stop after the controls and resolve the
  response/provider path. Do not add S22/S23 or long planning work yet.
- If GLM high produces actions where xhigh stops at length, continue that
  configuration as a practical candidate, while reporting the inference effect.
- If both GLM settings repeatedly stop, avoid another unchanged rerun. A larger
  verified completion ceiling is a separate later experiment, not an automatic
  recovery in this matrix.
- Once diagnostics are interpretable, add an Astra anchor on S05/S08 and
  S21/S22/S23/S24 at its established cross-axis preset (six attempts). This
  provides a contemporary comparison; it alone still does not prove a pure T/D effect.
- Next qualify fresh seeds and decision-relevant alternative worlds. Then vary
  component count and dependency depth separately, with disclosed controls,
  generous-budget baselines and exact physical-cost qualification before adding R pressure.

Grok's existing 14-row screen can proceed independently if still outstanding.
Muse's pending S21 receipt check is one exact row, not another full control run.
Mistral remains a response-format diagnostic before axis interpretation.
