# AGENTS.md

## Purpose

This repository implements NEXUS: a standalone procedural interactive environment designed to stress modern LLM reasoning, planning, memory, state tracking, causal discovery, tool use, and eventually multimodal understanding.

Read this file before modifying the project.

## Product principles

### 1. Build for LLMs, not by copying human games

Do not reproduce a familiar board game, adventure game, real scientific experiment, or physical simulation merely because it is convenient.

A NEXUS episode should present an artificial micro-world whose useful rules must be learned from the episode itself.

### 2. Generate the laws, not only the level

Procedural generation must eventually vary causal rule structure compositionally.

Bad:

```python
rule = random.choice([effect_1, effect_2, effect_3])
```

Preferred:

```text
Conditional(
    And(PhaseParity(even), Equals(shape, triangle)),
    Sequence(AddMod(value, 3, 11), Toggle(polarity)),
    Rotate(1),
)
```

The complete rule above is data constructed from primitives, not a hard-coded game mechanic.

### 3. Deterministic compiled execution

Generation may use randomness.

Once an episode is compiled:

```text
same initial state + same action trace == same state trace and terminal result
```

Avoid floating point mechanics in the prototype. Prefer bounded integers and enums.

### 4. Controls are public; world mechanics may be hidden

Do not make undocumented control syntax part of ordinary NEXUS difficulty.

The evaluated player should receive the stable interaction contract:

- available action types;
- required fields / JSON schema;
- ordinary action semantics such as take, move, operate, probe, wait, and finish.

Episode-specific causal laws, hidden state, reference plans, and verifier data remain private.

If a future benchmark deliberately studies instruction-following under incomplete controls, make
that an explicit separately tagged evaluation mode rather than silently mixing it into the normal
reasoning score.

### 5. Canonical state is authoritative

Never place game logic in prose, rendering, UI, or LLM prompts.

Maintain one canonical symbolic state. Text, files, images, and human-observer views are projections of that state.

Renderers must be side-effect free.

### 6. Exact success

Do not use an LLM judge to decide whether the player won.

The engine evaluates declarative goal predicates. A victory receipt may be emitted after success for integration with external benchmark systems.

### 7. Keep private state private

Never expose:

- private generator seed;
- latent rule AST when it is supposed to be hidden;
- solver/reference plan;
- verifier secret;
- hidden target metadata.

Public and private episode data should be separable.

Do not rely on obscurity. Assume the player can inspect every file/process explicitly made available to it.

### 8. Standalone first

NEXUS must run independently of any evaluation harness or model vendor.

Core code must not import OpenAI, Anthropic, Google, or another evaluation harness.

External systems integrate through adapters over a neutral NEXUS protocol.

### 9. Prefer small explicit code over speculative frameworks

This is a prototype.

Do not add abstractions for NPCs, combat, multiplayer, RL training, plugins, audio, 3-D rendering, databases, or distributed execution until they are needed.

Refactor after the second concrete use case proves an abstraction useful.

## Initial architecture

Use a package layout close to:

```text
src/nexus/
  models/
  engine/
  generator/
  solver/
  render/
  protocol/
  verification/
  cli.py
tests/
  unit/
  property/
  integration/
```

Use Python 3.12+ and modern typing.

### Models

Use Pydantic v2 for external schemas and serializable domain models where practical.

Initial concepts:

- Episode
- WorldState
- Room
- Artifact
- Machine
- Gate
- Resources
- Action
- Observation
- Goal
- Rule AST
- Event

Actions should use a structured/discriminated schema rather than a natural-language command parser.

### Rule language

Rules are declarative ASTs interpreted by a centralized evaluator.

Initial condition nodes may include:

- Always
- Equals
- PhaseEquals
- PhaseParity
- ValueModulo
- And
- Or
- Not

Initial effect nodes may include:

- AddMod
- MultiplyMod
- Toggle
- Rotate
- Set
- Sequence
- Conditional

Do not use eval/exec or generate Python source.

### Engine

The engine should behave conceptually as:

```python
next_state, events = step(state, action, episode)
```

Keep transitions deterministic and testable.

Invalid actions must not partially mutate state.

### Canonicalization and replay

Implement a deterministic canonical state serialization.

Every accepted action should produce an event record containing at least:

- turn;
- action;
- before-state hash;
- after-state hash;
- emitted events;
- terminal status.

Replay must validate hashes at every step.

### Goals and victory

Goals are declarative predicates over canonical state.

The player explicitly invokes a finish/commit action. Only then does the engine test victory.

Victory receipt requirements:

- generated only after success;
- based on a private secret plus a canonical goal projection;
- stable for equivalent valid terminal outcomes;
- not derivable from the public episode alone.

Use standard-library HMAC/SHA-256 rather than custom cryptography.

### Solver

Start with exhaustive BFS over canonical states and equal-cost actions.

The solver should return:

- solvable;
- optimal action count;
- one optimal plan;
- number of states explored;
- terminal state information.

Reject generated episodes that exceed a conservative state-space bound.

Only add A*, Dijkstra, or Z3 when they solve a demonstrated problem.

### Generator

Prefer solution-first generation:

1. create topology and entities;
2. compose latent rules;
3. construct a candidate successful trajectory or reachable target;
4. derive a goal from the reachable state;
5. solve from the real initial state;
6. reject trivial, impossible, too-deep, or pathological episodes;
7. compile public/private episode packages.

Never expose the construction seed as the public episode identifier.

### Evidence

The first prototype may generate a CSV of prior machine experiments.

For a finite rule grammar, enumerate candidate rules and mechanically verify that evidence narrows the hypothesis space as intended.

Start by requiring a unique rule after supplied evidence. Active information gathering can be added later.

### Human observability

Observer output must be separate from the agent observation projection.

For the prototype prefer Rich terminal rendering over a browser application.

Developer/omniscient observer mode may show hidden rules and reference plans only when private episode data is explicitly supplied.

## Dependencies

Prefer maintained third-party libraries where they remove undifferentiated infrastructure work:

- Pydantic: schema/model validation
- Typer: CLI
- Rich: terminal observer
- NetworkX: world-graph utilities
- pytest: testing
- Hypothesis: property/stateful testing
- FastAPI/Uvicorn: later HTTP session server

Keep the deterministic transition engine itself simple and locally understandable.

## Test expectations

Every meaningful mechanic needs deterministic unit tests.

Use Hypothesis for invariants such as:

- rule serialization round-trips;
- state serialization round-trips;
- same state/action gives same successor;
- invalid actions do not corrupt state;
- replay reproduces hashes exactly;
- generated episodes are solvable;
- solver-produced plans actually win;
- victory receipts cannot be produced before victory;
- public episode serialization does not contain private fields.

Tests should focus on semantic invariants rather than implementation details.

## Prototype stages

Implement in this order unless a concrete blocker requires otherwise:

1. project tooling and schemas;
2. canonical state + actions;
3. rule AST + interpreter;
4. deterministic engine;
5. canonical hashing + replay;
6. goal predicates + victory receipt;
7. reference BFS solver;
8. procedural episode generator;
9. qualification pipeline;
10. generated evidence;
11. CLI / JSONL machine protocol;
12. terminal observer;
13. persistent HTTP session server;
14. neutral service/client integration interfaces;
15. optional visual renderers.

Do not put visual support on the critical path of the first working engine.

## Definition of prototype success

The central proof is not that a model can walk through rooms.

A meaningful prototype must demonstrate:

- a complete latent causal rule that was not directly authored as one hard-coded mechanic;
- an automatically generated episode containing that rule;
- solver proof that the episode is winnable;
- deterministic execution/replay;
- exact mechanically verified success;
- a public interface that does not reveal the private solution;
- at least one real LLM capable of interacting with it through a structured interface.

## Changes and commits

Keep commits focused by stage.

Do not modify `main` directly. Prototype work belongs on a feature branch and should be reviewed through a pull request before merge.
