# NEXUS

**Small artificial worlds. Explicit rules. Verifiable outcomes.**

NEXUS tests how a model investigates, plans, and acts over many steps. A player is
inside a sealed facility. It reads records, experiments with apparatus, changes
the world, and tries to meet an exact mission. The engine checks success and
issues a victory receipt. No model judge is involved.

You can play locally, connect a model through a JSON interface, or build matched
experiments. Generation produces a compiled world; replay checks every accepted
action against its recorded state hash.

**Status:** experimental research software, preparing for public release. NEXUS
has shown useful differences between model/settings combinations. It is not yet
a calibrated general-purpose leaderboard. See the
[latest results](docs/research/fresh-world-results-2026-11-04.md) and
[release status](docs/release-readiness.md).

## Try it

From a repository checkout, with [uv](https://docs.astral.sh/uv/) installed:

```bash
uv sync --frozen --all-extras --python 3.14.7
uv run --frozen nexus demo
uv run --frozen nexus demo --play
```

The guided demo needs no model account, API key, or Docker. The interactive
version accepts JSON actions. Type `help`, `mission`, or `evidence <filename>`
for free information; `quit` exits. [Learn to play](docs/play-guide.md).

To save a world and play it later:

```bash
uv run --frozen nexus generate ./my-world --seed 17 --planning-level 0
uv run --frozen nexus play ./my-world/private.json
```

`private.json` belongs to the local engine/operator. Evaluated models receive
only the player interface and approved public files.

## Use it for research

| Goal | Start here |
|---|---|
| Connect a model or run MindTrial | [Evaluation guide](docs/evaluation-guide.md) |
| Design comparisons, interpret scores, verify runs | [Research guide](docs/research-guide.md) |
| Export a current matched multi-model panel | [Fresh-world guide](docs/fresh-world-guide.md) |
| Understand what past experiments established | [T/D synthesis](docs/td-experiments-and-next-directions.md) and [fresh-world results](docs/research/fresh-world-results-2026-11-04.md) |
| Add a world or contribute code | [Contributing](CONTRIBUTING.md) and [ontology guide](docs/ontology-author-guide.md) |
| Find technical references and historical reports | [Documentation index](docs/README.md) |

NEXUS varies the information supplied (**T**), investigation requirements (**D**),
planning structure (**P**), and resource pressure (**R**). These labels describe
family-specific experimental conditions, not a universal difficulty scale.
Disclosed laws, matched controls, mechanically checked solutions, and separate
physical/evidence outcomes help explain *why* a model succeeds or fails.

NEXUS runs independently of model vendors and evaluation harnesses. Python 3.14,
Typer, Pydantic, and Rich support the local interface; an optional FastAPI service
supports external tools. The checked-in lockfile pins the tested environment.

[MIT license](LICENSE). [Service and data boundaries](SECURITY.md).
