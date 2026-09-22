# MindTrial integration design

## Goal

NEXUS should appear to an evaluated model as **one structured stateful tool** while remaining a
standalone environment.

The model should be able to act in the world, but it must not control session creation,
restarting, private state, or verification.

## Model-facing tool

Conceptually MindTrial exposes one tool:

```text
nexus_action(action)
```

where `action` follows NEXUS's public discriminated-union action schema.

Example:

```json
{
  "action": {
    "type": "operate",
    "machine": "M1",
    "artifact": "A1"
  }
}
```

The tool result contains the public NEXUS action response and observation.

The tool description should include the stable action semantics, or derive them directly from
NEXUS's published action contract.

## Session ownership

**One MindTrial task execution equals one NEXUS session.**

The harness, not the model, creates that session.

The evaluated model must never receive or control:

- `POST /sessions`;
- a reset/restart command;
- the NEXUS session identifier;
- the private episode path;
- the verifier secret.

The adapter binds the MindTrial task/run to one NEXUS session internally.

Conceptually:

```text
MindTrial task starts
        |
        v
adapter creates exactly one NEXUS session
        |
        v
model calls nexus_action(action)
        |
        v
adapter sends action to bound session
        |
        v
NEXUS returns observation/result
```

When the NEXUS state becomes `won` or `failed`, that session remains terminal. Further action
calls return the terminal state; they do not create a new session.

## Why not keep session state in MindTrial /app/shared?

The current MindTrial Docker-tool executor creates a fresh tool container for each invocation and
mounts a persistent `/app/shared` directory across all local tools in the task.

That is useful for ordinary tools but is the wrong trust boundary for NEXUS:

- the model's Python tool can also access `/app/shared`;
- therefore private NEXUS state or a reusable secret session token stored there could be read or
  modified by the evaluated model.

NEXUS private state must instead remain in a trusted process/storage boundary inaccessible to
the model's Python environment.

## Preferred integration

The cleanest implementation is a small MindTrial-side **stateful NEXUS adapter**:

1. at provider/task-run initialization, create a NEXUS session against a persistent NEXUS server;
2. keep the opaque session ID in Go memory associated with that tool executor/run;
3. expose only the NEXUS action schema to the model;
4. on each tool call, forward the supplied action to the already-bound session;
5. destroy/end the binding when the MindTrial task finishes.

This is a small amount of MindTrial-specific code, but game semantics remain entirely inside
NEXUS.

An alternative is to add a generic stateful/remote-tool abstraction to MindTrial if another
environment soon needs the same lifecycle. Do not add that abstraction solely speculatively.

## Can the agent cheat by restarting a lost game?

Not with the intended adapter.

Restart prevention should exist at several layers:

1. **No reset action in the public NEXUS action schema.**
2. **No model-facing session-creation endpoint.**
3. **Session ID is harness-owned and invisible to the model.**
4. **A terminal NEXUS session cannot transition back to active.**
5. **NEXUS private/server state is outside the model's Python/container filesystem.**
6. **MindTrial creates at most one bound NEXUS session per task attempt.**

The model could ask to "restart" in natural language, call `observe`, or deliberately submit
invalid actions, but none of those creates a new world.

If the entire MindTrial benchmark task is explicitly rerun by the human/operator, that is a new
benchmark attempt and should be recorded as such rather than treated as an in-game restart.

## Episode files in MindTrial

For a text-first episode, MindTrial can provide public evidence such as:

- `facility_manual.txt`;
- `measurements.csv`.

These may be exposed natively to models that support files and/or locally to Python according to
the benchmark configuration.

The private NEXUS package must never be attached to the task.

For a future paired-modality benchmark, the same adapter/session can be used while the task
chooses which public renderers/attachments are exposed.

## Expected result

The task prompt can instruct the model:

```text
Complete the NEXUS mission using the nexus_action tool.
When NEXUS reports victory, return the victory code exactly.
```

MindTrial's normal exact-result validation can compare that code with the expected receipt.

No LLM judge is required.
