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

- 5–7 connected rooms;
- 2 artifacts;
- 1–2 transformation machines;
- optional gate/phase state;
- small integer/enumerated object properties;
- one or two generated rule ASTs;
- 8–15 optimal environment actions;
- one generated evidence file;
- text observations;
- exact victory verification.

The initial episode family is a synthetic **Transformation Facility**: manipulate one or more abstract artifacts through generated machines and deliver a required final state to a target room.

## Planned stack

- Python 3.12+
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

## Development

See [AGENTS.md](AGENTS.md) for implementation constraints and staged development guidance.

All prototype work should remain isolated from unrelated projects. MindTrial support should eventually be a thin adapter over the standalone NEXUS protocol.


## Working prototype

The feature branch currently implements the first end-to-end Transformation Facility prototype:

- compositional latent rule grammar with 288 possible generated laws;
- generated connected room topology, artifact state, machine law, target state, and evidence;
- public `facility_manual.txt` describing the causal grammar;
- generated `measurements.csv` that uniquely identifies the selected law within that grammar;
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

Using `uv`:

```bash
uv venv
uv pip install -e ".[dev,server]"
```

A normal pip environment also works:

```bash
python -m pip install -e ".[dev,server]"
```

### Generate an episode

```bash
nexus generate ./episode --seed 17
```

The generated directory contains:

```text
episode/
  manifest.json                 # safe to expose to the evaluated agent
  attachments/
    facility_manual.txt         # public causal grammar
    measurements.csv            # generated experimental evidence
  private.json                  # trusted runner only
```

Do not give `private.json` to the evaluated model. It contains the latent rule,
construction metadata, reference solution, and victory secret.

### Qualify and inspect

```bash
nexus qualify ./episode/private.json
nexus solve ./episode/private.json --trace-out ./episode/run.jsonl
nexus replay ./episode/private.json ./episode/run.jsonl --observer
```

### Human play

```bash
nexus play ./episode/private.json
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

Canonical state, latent rules, reference plans, and verifier secrets remain server-side.

## Prototype limitations

This is intentionally a narrow proof of concept rather than the final benchmark. The current
episode family uses one artifact and one transformation machine; the finite causal grammar is
public; runtime execution is deterministic; and observations are text/structured data only.
Visual renderers, richer rule grammars, multiple interacting machines/artifacts, structural OOD
splits, active information-gathering scenarios, and a MindTrial adapter are follow-up work after
the core generator/solver/verifier loop is validated against real models.
