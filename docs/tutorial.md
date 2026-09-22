# NEXUS player tutorial

## What is supposed to be known?

NEXUS intentionally separates the **interaction contract** from the **episode mechanics**.

The player should know:

- which actions exist;
- the JSON shape of each action;
- ordinary control semantics such as "take puts an artifact in inventory" and
  "operate applies the machine to a carried artifact";
- the mission goal;
- any public episode evidence and manuals.

The player should **not** know:

- the selected latent machine law;
- private canonical state that is not observable;
- the construction seed;
- the reference/optimal plan;
- the verifier secret;
- hidden future state.

The benchmark is intended to measure reasoning inside an unfamiliar world, not the ability to
reverse-engineer an undocumented API.

Use:

```bash
nexus actions
```

or, while using `nexus play`:

```text
nexus> help
```

to see the action reference.

## Actions

### Observe

```json
{"type":"observe"}
```

Refreshes the current observation. It does not consume an environment action.

### Move

```json
{"type":"move","target":"R1"}
```

Moves to an adjacent room. Anything in your inventory moves with you.

### Take

```json
{"type":"take","artifact":"A1"}
```

Picks up an artifact in the current room. The artifact is now carried in inventory.

There is no separate "move artifact" command: carry it by taking it and then moving the agent.

### Drop

```json
{"type":"drop","artifact":"A1"}
```

Places a carried artifact into the current room.

### Operate

```json
{"type":"operate","machine":"M1","artifact":"A1"}
```

Applies a machine in the current room to a carried artifact.

This changes the real artifact according to the episode's hidden machine law and consumes one
machine use.

### Probe

```json
{"type":"probe","machine":"M1","artifact":"A1"}
```

Tests what the machine would do to a carried artifact without changing the real artifact and
without consuming a machine use. The returned event contains the hypothetical result.

A probe does consume one environment action.

### Wait

```json
{"type":"wait"}
```

Advances the facility phase by one step.

### Finish

```json
{"type":"finish"}
```

Asks the engine to check the current state against the mission goal. A victory code is returned
only if all goal predicates are satisfied.

## Tiny illustrative solved example

This example is deliberately simpler than a generated benchmark episode. It exists only to show
the mechanics.

Suppose an episode has:

```text
R0 -- R1 -- R2

You are in R0.
A1 is in R0.
M1 is in R1.
The Nexus destination is R2.

Goal:
  A1 must be in R2
  value = 5
  polarity = positive
  orientation = east
  phase = 0
```

Assume the public manual and measurements have let you infer that, for A1 at phase 0, operating
M1 transforms its current state into exactly the required value/polarity/orientation.

A successful interaction would be:

```json
{"type":"take","artifact":"A1"}
{"type":"move","target":"R1"}
{"type":"operate","machine":"M1","artifact":"A1"}
{"type":"move","target":"R2"}
{"type":"drop","artifact":"A1"}
{"type":"finish"}
```

The important mechanics are:

1. `take` moves A1 into inventory.
2. Moving the agent also moves carried A1.
3. `operate` acts on the carried artifact.
4. `drop` places A1 in the destination room.
5. `finish` performs the exact victory check.

A real generated episode may additionally require selecting the correct phase, distinguishing
between candidate laws from the supplied evidence, probing, or avoiding an irreversible bad
operation.

## CLI help

Top-level help is available through either:

```bash
nexus --help
nexus help
```

Per-command help uses Typer's standard form:

```bash
nexus generate --help
nexus qualify --help
nexus solve --help
nexus play --help
nexus serve --help
```

In broad terms:

- `generate`: create solver-qualified episodes;
- `qualify`: run benchmark-validity checks against a compiled private episode;
- `solve`: run the reference BFS solver;
- `play`: human interactive client;
- `replay`: verify a recorded trace deterministically;
- `stdio`: JSONL machine interface;
- `serve`: persistent HTTP machine interface;
- `actions`: display the stable player action vocabulary.
