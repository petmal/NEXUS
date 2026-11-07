# Give one model its first NEXUS mission

Start with one repair whose solution is supplied. This answers a useful first question: can your model read the mission, control the apparatus and return the receipt? One control is an integration check, not a benchmark score.

**You need:** a NEXUS checkout with the [local demo](../README.md#play-your-first-world) working, Docker Engine 25+ running, a tool-capable model with provider access, and [MindTrial](https://github.com/petmal/MindTrial) with task services and custom validators. With Go as specified by MindTrial, build its current source with `go install github.com/petmal/mindtrial/cmd/mindtrial@main` and put the Go binary directory on PATH. An existing compatible binary works too; substitute its absolute path for `mindtrial` below.

## 1. Prepare the world and the two files

From the **NEXUS repository root**, using Bash:

```bash
docker build --build-arg VCS_REF="$(git rev-parse HEAD)" -t nexus:first-run .
uv run --frozen --no-dev python examples/mindtrial/first_run.py ../nexus-first-run \
  --provider openai --model gpt-6-luna
```

Use the provider name MindTrial recognizes and the model ID your account can actually call. For example, with OpenRouter, use `--provider openrouter --model YOUR_MODEL_ID` and set `OPENROUTER_API_KEY`; OpenAI uses `OPENAI_API_KEY`. Leave the key field blank in the generated config: MindTrial reads the provider's environment variable. For a model that loses tool use with structured final output (observed with GLM and MiniMax), add `--text-output` when preparing the files. Other provider-specific settings belong in the single run's `model-parameters`; consult the [MindTrial configuration guide](https://github.com/petmal/MindTrial#basic-usage).

Preparation makes no model calls. The script creates a **new** directory. Inspect `tasks.yaml`: it contains just F05, a supplied-solution repair control. `config.yaml` has one model, one tool, its persistent world service and a receipt validator. The example uses provider defaults for inference; it does not reproduce the historical panel's model settings.

## 2. Run it and read the result

With your chosen provider's credential already in the environment:

```bash
cd ../nexus-first-run
mindtrial --config=./config.yaml --tasks=./tasks.yaml --json --debug \
  --interactive=false --evaluation-seed=nexus-first-visit run
```

This step uses your provider and may incur charges. Set `--interactive=true` if you want to confirm the selection. Look in `./results/` for the dated JSON report and log. Keep the two input files with them.

- **Passed:** the validator accepted the submitted receipt. This world has an eight-action budget; a checked example used five and ended with three left. It doesn't require the player to discover the supplied solution.
- **Failed:** inspect the final tool response and the submitted answer. A rejected `finish`, running out of world actions, and winning but returning the wrong text are different outcomes.
- **Error or no usable attempt:** inspect provider availability, credentials, tool requests and the Docker service log. An error alone says little about reasoning. The tutorial also caps harness turns at 40 and tool calls at 32; a free evidence read still counts as a tool call.

A second run starts a fresh service. Use a new output directory for a new configuration. This tutorial does **not** grant admission to a research panel or preserve a complete private audit bundle. For matched controls, preflight and comparisons, continue to [Design a benchmark](benchmark-guide.md).
