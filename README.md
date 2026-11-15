# NEXUS

**Can a model figure out how a machine works, then use it to get out?**

NEXUS is a free, MIT-licensed framework for testing reasoning in small, interactive worlds. Inside a sealed facility, a translated console gives you a mission: calibrate a controller, repair a component or build a working replacement. The controls and goal are public. Some worlds disclose the laws; others give you evidence and apparatus for testing your own explanation.

You can play, send a model in, or run the same puzzle twice with one condition changed. The engine checks the actual world state when the player calls `finish`. A win earns a verifiable receipt; a replay shows the actions that got there. No model judge is needed.

## Play your first world

With Git and [uv](https://docs.astral.sh/uv/getting-started/installation/) installed:

```bash
git clone https://github.com/petmal/NEXUS.git
cd NEXUS
uv sync --frozen --no-dev --python 3.14.7
uv run --frozen --no-dev nexus demo --play
```

No Docker, model account or API key is needed for local play. The first install may download Python and dependencies.

At the console, type `mission` to read your goal, `look` to see the room, and `help` for the controls. In the introductory world, try `move R4`, then `look`. Use Tab to complete names, Up to edit your last command, or `log` to review what happened. JSON actions also work. You have spent one world action; reading the display is free. Type `quit` to leave. Prefer to watch first? Run `uv run --frozen --no-dev nexus demo` for a complete unscored playthrough. [See all nine actions](docs/play-guide.md#the-introductory-world-in-nine-actions).

## Send in a model

[Run one model on one control with MindTrial](docs/first-model.md). Pick a tool-capable model and a provider you can access. The example uses Docker for the world and a separate validator for the receipt. You can also [connect your own harness](docs/evaluation-guide.md).

Read three things before comparing scores: **did the world issue a receipt**, **did the harness accept the submitted answer**, and **how many world actions did the player spend**? Reading evidence can cost a model tool call without spending a world action. Some families also tell you whether the evidence justified the winning choice.

## Change the question

The demo uses **seed 17**, **axis version 1**, and four settings at zero. Want to try the same rooms, machine and mission with fewer moves to spare? From the repository, generate a variant that changes only resource pressure, then play it:

```bash
uv run --frozen --no-dev nexus generate ../demo-tight --seed 17 --axis-version 1 \
  --theory-level 0 --discovery-level 0 --planning-level 0 --resource-pressure 2
uv run --frozen --no-dev nexus play ../demo-tight/private.json
```

Your allowance drops from 19 actions to 9. To try discovery instead, replace `demo-tight` with `demo-discovery` in both commands, set `--resource-pressure 0`, and set `--discovery-level 2`. The map stays familiar, but the records leave a question for you to test. [Try more variations on the demo](docs/play-guide.md#try-the-same-world-with-one-change).

| Dial | What it changes | Example question |
|---|---|---|
| T — theory | Information supplied about the mechanism | Can the model still repair it when the law is withheld? |
| D — discovery | What must be inferred or investigated | Can it design a useful experiment? |
| P — planning | Layout or dependencies between operations | Can it get all targets right at the same time? |
| R — resources | Room to spend actions beyond a reference cost | Does the same plan still work without spare moves? |

The settings belong to a world family; a “3” is not a universal difficulty score. NEXUS is experimental research software. It has identified differences between tested model configurations, without establishing a general model ranking.

**Where next:** [Design and read a comparison](docs/benchmark-guide.md) · [Research methods and metrics](docs/research-guide.md) · [All documentation](docs/README.md) · [Release status](docs/release-readiness.md)

[License](LICENSE) · [Citation](CITATION.cff) · [Service and data boundaries](SECURITY.md)
