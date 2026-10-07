# NEXUS

NEXUS is a standalone, deterministic interactive environment for evaluating whether an LLM can enter a procedurally novel artificial micro-world, infer its unfamiliar causal structure from evidence and experimentation, maintain an evolving world model, and plan actions that reach a mechanically verified goal.

The central design goal is to evaluate **adaptation and reasoning rather than recalled domain knowledge**. NEXUS does not model an existing human game, real-world physics, or a known scientific experiment. Episodes are compiled from a small compositional grammar that can vary the world topology, entities, latent causal laws, evidence, and objective.

## Prototype goals

The first working prototype should demonstrate:

- procedurally generated world structure and object state;
- compositionally generated latent causal laws, not just selection from fixed complete rules;
- deterministic execution once an episode has been compiled;
- an automatically verified solvable episode with a reference solver;
- exact engine-defined success rather than LLM-as-judge evaluation;
- deterministic replay from an append-only action/event trace;
- a non-forgeable victory receipt emitted only after the goal predicate is satisfied;
- a standalone CLI and structured machine interface;
- human-observable state/replay artifacts that are separate from model-visible observations;
- text-first operation, with optional visual/file renderers added as independent projections of the same canonical world;
- clean integration seams for external harnesses such as MindTrial without making them dependencies.

## Key distinction

Many interactive benchmarks expose agents to fixed games or fixed rule families. NEXUS aims to generate the **causal system itself**. A benchmark episode may synthesize:

- topology;
- entities and properties;
- transition laws;
- dependencies and conditions;
- evidence;
- goal predicates;
- distractors;
- presentation modality.

The resulting episode is then solver-qualified and frozen. Generation may be stochastic; compiled execution must be reproducible.

## Architecture

The canonical symbolic world is authoritative.

```text
Episode generator + qualifier
          |
          v
Canonical episode
  |       |       |
  |       |       +--> private verifier / reference solution
  |       +----------> agent observation renderers
  +------------------> deterministic transition engine
                         |
                         +--> append-only event log
                         +--> observer / replay projection
```

Important invariants:

1. Rules are declarative data, never generated executable Python.
2. Text, files, images, and observer views are projections of canonical state.
3. The player never receives private generation state, solver output, or verification secrets.
4. Identical compiled state plus identical action produces an identical successor state.
5. Success is an engine predicate.
6. Multiple valid plans may exist; equivalent winning outcomes should be accepted.
7. NEXUS remains standalone. Integrations are adapters.

## Initial prototype scope

Keep the first environment deliberately small:

- 4–9 connected rooms selected by the planning profile;
- 1 mission artifact, with auxiliary experimental artifacts on higher discovery profiles;
- 1–3 transformation machines selected by the discovery profile;
- optional gate/phase state;
- small integer/enumerated object properties;
- one or two generated rule ASTs;
- solver-measured physical horizon with a conservative safety cap;
- generated evidence qualified against the requested discovery profile;
- text observations;
- exact victory verification.

The initial episode family is a synthetic **Transformation Facility**: manipulate one or more abstract artifacts through generated machines and deliver a required final state to a target room.

## Planned stack

- Python 3.14
- uv
- Pydantic v2
- Typer
- Rich
- NetworkX where graph utilities help
- pytest
- Hypothesis
- FastAPI/Uvicorn for the later persistent session server
- optional Z3 for generation/constraint analysis after the basic exhaustive approach works

Conventional game engines are intentionally avoided. NEXUS is primarily a symbolic world, generation, search, and verification problem.

## Documentation

- [Player tutorial](docs/tutorial.md) — action reference, CLI help, evidence access, and a tiny solved mechanics example.
- [Difficulty profiles](docs/difficulty.md) — discovery, planning, and resource-pressure knobs and their mechanical guarantees.
- [Service integration](docs/service-integration.md) — single-session service, client, health, validation, and generated-session configuration.
- [AGENTS.md](AGENTS.md) — implementation constraints and staged development guidance.

## Development

See [AGENTS.md](AGENTS.md) for implementation constraints and staged development guidance.

All prototype work should remain isolated from unrelated projects. External harnesses should integrate through the standalone NEXUS protocols and CLI.


## Working prototype

The feature branch currently implements the first end-to-end Transformation Facility prototype:

- compositional latent rule grammar with 288 possible generated laws;
- generated connected room topology, artifact state, machine law, target state, and evidence;
- public `facility_manual.txt` describing the causal grammar;
- generated machine evidence whose mission-relevant ambiguity is qualified to the requested discovery level;
- generic discovery/planning/resource profiles, including P3 delivery dependencies, two-machine sequential discovery, cost-selective experimentation, and constructed diagnostic experiments;
- deterministic transition engine and canonical hashing;
- append-only trace plus deterministic replay verification;
- engine-defined goal predicates and HMAC-based victory receipts;
- exhaustive BFS reference solver and episode qualification;
- player-safe manifest/attachment packaging separated from runner-only private state;
- JSONL stdin/stdout protocol;
- persistent HTTP sessions with idempotent action stepping;
- Rich human observer with facility topology and omniscient debug mode;
- pytest/Hypothesis coverage and GitHub Actions smoke tests.

### Install

NEXUS uses Python 3.14 and commits a `uv.lock` so development, CI, and container builds use
the same resolved dependency graph. Install the pinned `uv` release and sync from the lock:

```bash
python -m pip install --no-deps uv==0.12.21
uv sync --frozen --all-extras
```

Run commands through the locked environment with `uv run`, for example:

```bash
uv run nexus --help
uv run pytest -q
```

Tests are tiered so routine development does not repeatedly pay for the cross-seed generator
matrix:

```bash
# Fast correctness gate used by ordinary PR/main CI.
uv run pytest -q -m "not slow and not stress" tests/unit tests/integration

# Broader multi-profile unit/integration checks.
uv run pytest -q -m slow tests/unit tests/integration

# Full 10-seed D/P stress matrix (default when run locally).
uv run pytest -q -m stress tests/property

# Smaller paid-CI sample when desired.
NEXUS_STRESS_SEED_COUNT=5 uv run pytest -q -m stress tests/property
```

GitHub Actions runs only the fast gate automatically on pull requests and `main`. The expensive
extended/stress/CLI/container suite is an explicit `workflow_dispatch` full run, so feature-branch
commits do not consume Actions budget accidentally.

Direct dependencies use bounded compatibility ranges in `pyproject.toml`: generation-sensitive
and pre-1.0 runtime dependencies stay within their current minor series, while stable-major
non-generation and dev/test dependencies may advance across minor releases. `uv.lock` pins the
exact resolved graph and artifact hashes used by development, CI, and containers. Refresh the
lock intentionally rather than allowing installs to resolve newer packages implicitly.

### Generate an episode

```bash
nexus generate ./episode --seed 17 --discovery-level 1 --planning-level 1
```

The public difficulty surface is intentionally small:

- `--discovery-level 0..5` controls how much mission-relevant causal information must be
  actively discovered;
- `--planning-level 0..3` controls topology/planning complexity; P3 adds a paired delivery dependency without increasing the P2 room-count range;
- `--resource-pressure 0..2` controls only the action allowance above the exact guaranteed-policy cost.

NEXUS derives compatible low-level generation settings and rejects candidates until the selected
profile's guarantees are mechanically satisfied. See [Difficulty profiles](docs/difficulty.md).

The generated directory contains:

```text
episode/
  manifest.json                 # safe to expose to the evaluated agent
  attachments/
    facility_manual.txt         # public causal grammar
    measurements.csv            # M1 experimental evidence
    measurements_M2.csv         # present when an M2 evidence file is needed
  private.json                  # trusted runner only, including generation metadata
```

Do not give `private.json` to the evaluated model. It contains the latent rule,
construction metadata, reference solution, and victory secret.

### Qualify and inspect

```bash
nexus qualify ./episode/private.json
nexus inspect ./episode/private.json
nexus solve ./episode/private.json --trace-out ./episode/run.jsonl
nexus replay ./episode/private.json ./episode/run.jsonl --observer
```

### Human play

```bash
nexus play ./episode/private.json
```

Inside the game, type `help`, `actions`, or `?` for the complete action reference. Read any public file listed by the episode with `evidence <filename>`, for example `evidence measurements.csv`; this does not consume an environment action. You can also run:

```bash
nexus actions
nexus help
nexus --help
nexus qualify --help
```

The human CLI intentionally uses the trusted package because it combines the runner and
observer in one process. Normal evaluated agents should interact through the machine protocol,
not read the private file.

### JSONL agent protocol

```bash
nexus stdio ./episode/private.json
```

The process emits the initial observation, then accepts requests such as:

```json
{"expected_turn": 0, "action": {"type": "move", "target": "R1"}}
```

### HTTP runner

```bash
nexus serve ./episode/private.json --host 127.0.0.1 --port 8000
```

Player-safe endpoints include:

```text
GET  /manifest
GET  /evidence/{filename}
POST /sessions
GET  /sessions/{id}/observe
POST /sessions/{id}/actions
GET  /sessions/{id}/status
GET  /sessions/{id}/events
```

Canonical state, latent rules, reference plans, and verifier secrets remain server-side. The player-safe manifest also includes the machine-readable action schema and human-readable action reference.



### Terminal performance telemetry

Terminal `won`/`failed` action responses include a `performance` object with exact physical and
guaranteed-policy baselines, signed action/probe deltas, profile identifiers, and runtime error/
retry counters. The object includes an immutable `$schema` URL. The published schema is
[schemas/performance-v1.schema.json](schemas/performance-v1.schema.json), whose field descriptions
are intended to make benchmark logs directly interpretable by downstream tools and LLMs.

### Single-session service and container integration

For an external orchestrator that already scopes one service process to one evaluation attempt,
NEXUS can own exactly one non-resettable session:

```bash
NEXUS_SEED=17 NEXUS_DISCOVERY_LEVEL=1 NEXUS_PLANNING_LEVEL=1 \
NEXUS_RESOURCE_PRESSURE=0 NEXUS_HOST=0.0.0.0 nexus serve-session
```

A fixed verifier secret is optional when reproducible victory codes are useful:

```bash
NEXUS_SEED=17 NEXUS_VERIFIER_SECRET=test-secret nexus serve-session
```

The same mode can serve an already compiled private episode:

```bash
nexus serve-session --private ./episode/private.json
```

The single-session API intentionally has no session-creation or reset endpoint:

```text
GET  /health
GET  /manifest
GET  /evidence/{filename}
GET  /observe
POST /action
GET  /status
GET  /events
```

A short-lived client process can talk to the service using `NEXUS_URL`:

```json
{"operation":"observe"}
{"operation":"evidence","filename":"measurements.csv"}
{"operation":"action","action":{"type":"move","target":"R1"}}
{"operation":"status"}
```

Each `nexus request --request-file` file contains exactly one of the JSON request envelopes
shown above. For example:

```json
{"operation":"action","action":{"type":"move","target":"R1"}}
```

Execute it with:

```bash
NEXUS_URL=http://nexus:8000 nexus request --request-file /input/request.json
```

The client resolves the current turn before posting an action, so callers do not need to manage
the optimistic-concurrency turn field themselves.

Health checks can use:

```bash
nexus health
```

After the world is won, a trusted process can validate a submitted victory code without reading
the private episode. For a short code, pass it directly:

```bash
NEXUS_URL=http://nexus:8000 nexus validate --candidate NX-ABCD-EFGH-IJKL
```

For file-based transport:

```bash
NEXUS_URL=http://nexus:8000 nexus validate --candidate-file /input/candidate
```

Unlike `nexus request --request-file`, the validator file is **not JSON**. It contains only the
submitted victory code as raw text, for example:

```text
NX-ABCD-EFGH-IJKL
```

A valid check prints one JSON object with `correct`, `title`, and `explanation`. An incorrect
candidate is a normal `correct:false` result; transport/protocol failures exit non-zero.

A container image can be built directly from the repository. The Dockerfile pins both the
Python/Debian base image digest and the locked Python dependency graph:

```bash
docker build --build-arg VCS_REF="$(git rev-parse HEAD)" -t nexus:0.1.0 .
docker run --rm -p 8000:8000 \
  -e NEXUS_SEED=17 \
  -e NEXUS_HOST=0.0.0.0 \
  nexus:0.1.0 serve-session
```

The image records `VCS_REF` in the standard `org.opencontainers.image.revision` OCI label.
Use the same build argument with `podman build`. Builds without the argument report `unknown`;
build from a clean checkout when using the commit SHA as provenance. Inspect it with:

```bash
docker image inspect nexus:0.1.0 \
  --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}'
```

See [Service integration](docs/service-integration.md) for trust boundaries and configuration
patterns.

## Prototype limitations

This is intentionally a narrow proof of concept rather than the final benchmark. The current
episode family uses a small number of artifacts and up to three transformation machines; the finite
causal grammar is public; runtime execution is deterministic; and observations are text/structured
data only. Discovery level 3 introduces a qualified two-stage transformation chain. Discovery level
4 keeps the same probe mechanics but adds auxiliary and distractor experimental contexts whose
relative value is proved by an exact minimum worst-case action-policy solver. Discovery level 5
keeps those same actions again, but requires constructing a diagnostic context by operating an
auxiliary machine before probing the mission machine; a functional distractor machine remains a
strictly higher-cost alternative. Richer interacting artifacts, larger rule grammars, structural
OOD splits, visual renderers, and broader world families remain follow-up work after calibration
against real models.
