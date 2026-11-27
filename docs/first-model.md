# Give one model its first NEXUS mission

Start with one repair whose solution is supplied. This answers a useful first question: can your model read the mission, control the apparatus and return the receipt? One control is an integration check, not a benchmark score.

**You need:** a NEXUS checkout with the [local demo](../README.md#play-your-first-world) working, Docker Engine 25+ running, a tool-capable model with provider access, and [MindTrial](https://github.com/petmal/MindTrial) v0.27.0 or newer. With Go as specified by MindTrial, install the tested version with `go install github.com/petmal/mindtrial/cmd/mindtrial@v0.27.0` and put the Go binary directory on PATH. An existing compatible binary works too; substitute its absolute path for `mindtrial` below.

## 1. Prepare the world and the two files

From the **NEXUS repository root**, using Bash:

```bash
docker build --build-arg VCS_REF="$(git rev-parse HEAD)" -t nexus:first-run .
uv run --frozen --no-dev python examples/mindtrial/first_run.py ../nexus-first-run \
  --provider openai --model gpt-6-luna
```

Use the provider name MindTrial recognizes and the model ID your account can actually call. For example, with OpenRouter, use `--provider openrouter --model YOUR_MODEL_ID` and set `OPENROUTER_API_KEY`; OpenAI uses `OPENAI_API_KEY`. Leave the key field blank in the generated config: MindTrial reads the provider's environment variable. For a model that loses tool use with structured final output (observed with GLM and MiniMax), add `--text-output` when preparing the files. The named Astra, Luna and Gemini Flash presets request provider summaries in the MindTrial log. Other provider-specific settings belong in the single run's `model-parameters`; consult the [MindTrial configuration guide](https://github.com/petmal/MindTrial#basic-usage).

Preparation makes no model calls. The script creates a **new** directory. Inspect `tasks.yaml`: it contains just F05, a supplied-solution repair control. `config.yaml` has one model, one tool, its persistent world service and a receipt validator. The example uses provider defaults for inference; it does not reproduce the historical panel's model settings.

## 2. Run it and read the result

With your chosen provider's credential already in the environment:

```bash
cd ../nexus-first-run
mindtrial --config=./config.yaml --tasks=./tasks.yaml --json --debug \
  --interactive=false --evaluation-seed=nexus-first-visit run
```

On an SELinux host, the service needs a container-accessible label on its dedicated audit directory. The smoke script below prepares that label for its own new directory.

This step uses your provider and may incur charges. Set `--interactive=true` if you want to confirm the selection. Look in `./results/` for the dated JSON report and log. Keep the two input files with them.

- **Passed:** the validator accepted the submitted receipt. This world has an eight-action budget; a checked example used five and ended with three left. It doesn't require the player to discover the supplied solution.
- **Failed:** inspect the final tool response and the submitted answer. A rejected `finish`, running out of world actions, and winning but returning the wrong text are different outcomes.
- **Error or no usable attempt:** inspect provider availability, credentials, tool requests and the Docker service log. An error alone says little about reasoning. The tutorial also caps harness turns at 40 and tool calls at 32; a free evidence read still counts as a tool call.

A second run starts a fresh service. MindTrial mounts `private-audits/` only on that service. Its `{{ .Service.InstanceID }}` input gives each attempt, including retries, a new child directory. The player tool and receipt validator have no filesystem access to it. Keep these exports private: they contain the compiled world and verifier secret. The debug log links the result trace ID to the service name. This tutorial does not grant admission to a research panel.

## Test that the mount works

From the NEXUS checkout, run `bash examples/mindtrial/test-persistent-mounts.sh --preflight-only` for a local Docker test with no provider calls. Drop the flag for the same check followed by one non-interactive F05 run. Defaults: build committed source from `~/Go-Projects/NEXUS`, use `~/MindTrial/mindtrial`, write a fresh folder under `~/Downloads`, and run OpenAI's `gpt-6-luna`. Set `NEXUS_REPO`, `MINDTRIAL_DIR`, `OUTPUT_ROOT`, `PROVIDER`, `MODEL`, or `TEXT_OUTPUT=1` to override. Only the live run needs provider credentials.

The script removes the preflight container before verifying its unfinished session. After a live run it verifies every retained service attempt using the same image, mounted read-only, even when Docker owns the files. It checks the final win and accepted receipt separately. A partial bundle or missing attempt fails the check and the files are kept. See [Design a benchmark](benchmark-guide.md) for comparisons.
