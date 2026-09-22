# MindTrial integration design

## Principle

NEXUS must remain independent of MindTrial.

MindTrial should not contain NEXUS-specific session logic, protocol handling, or game semantics.
Instead, MindTrial can gain a generic capability that is useful for NEXUS and other stateful
interactive tools:

> Start one isolated service instance for each task execution attempt, keep it alive for the
> duration of that attempt, and allow explicitly selected tools to communicate with it.

NEXUS is then simply one possible service.

The same NEXUS interfaces should also be usable directly through HTTP/JSONL, MCP, another agent
loop, or a human client.

## Correct lifecycle scope

"One service per task" must mean one service per **task execution attempt**, not one service per
logical task definition.

MindTrial evaluates the same task across multiple providers and run configurations. Those runs
must never share mutable environment state.

Conceptually:

```text
(provider A, run X, task T) -> service instance 1
(provider B, run X, task T) -> service instance 2
(provider A, run Y, task T) -> service instance 3
```

Each evaluated model therefore receives an identical initial episode but an independent mutable
world instance.

## Retry scope

The service lifetime must wrap MindTrial's whole provider/task retry loop.

MindTrial's execution layer may retry an entire provider task attempt after a transient failure.
If the service were created inside `Provider.Run`, each retry could silently reset the game.

The correct ordering is:

```text
create task services
    |
    +-- provider attempt
    |      |
    |      +-- API/tool turns
    |
    +-- transient retry of provider attempt
    |      |
    |      +-- same service instance and state
    |
destroy task services
```

A service crash during an active attempt should normally make the task an infrastructure error.
MindTrial should not automatically replace it with a fresh service, because doing so would reset
state and could give the model another attempt.

## Generic MindTrial service configuration

A possible configuration shape is:

```yaml
services:
  - name: nexus
    image: ghcr.io/petmal/nexus:latest
    command:
      - nexus
      - serve-session
      - /app/episode/private.json
      - --host
      - 0.0.0.0
      - --port
      - "8080"

    health-check:
      type: http
      port: 8080
      path: /health

    parameter-files:
      episode: /app/episode/private.json
```

A task binds the service and supplies private service-only inputs:

```yaml
service-selector:
  services:
    - name: nexus
      files:
        episode: ./episodes/example/private.json
```

These service files are infrastructure inputs. They are **not** task attachments and are never
exposed to the model or ordinary local tools.

The exact YAML shape is only illustrative; the important distinction is between:

- model-visible task files;
- tool-local task files;
- private service-only files.

## Tool connectivity

MindTrial's current Docker tools run with `NetworkMode: none`, which is a good default and should
remain unchanged.

A tool may explicitly declare service dependencies:

```yaml
tools:
  - name: nexus
    image: ghcr.io/petmal/nexus:latest
    command:
      - nexus
      - call
      - --url
      - http://nexus:8080/action
    services:
      - nexus
    parameters:
      type: object
      properties:
        action:
          # NEXUS action schema
```

For each task attempt, MindTrial creates private Docker networking for the selected services.
Only tools that explicitly list a service are attached to the relevant service network.

Therefore:

- the NEXUS tool can reach the NEXUS service;
- the Python tool cannot reach NEXUS unless explicitly configured to do so;
- external internet access remains disabled;
- the model cannot access Docker or the service network directly.

This keeps the trust boundary narrow without requiring MCP support in MindTrial.

## Why a Docker client tool is acceptable

The first version does not need a new generic HTTP-tool implementation in MindTrial.

The existing Docker-tool mechanism can invoke a small client command from the NEXUS image:

```text
model function call
      |
      v
short-lived NEXUS client tool container
      |
      | private Docker service network
      v
persistent NEXUS service container
```

The client container remains stateless. The service owns all mutable game state.

A generic in-process HTTP tool executor could be added later if service-backed tools become
common and container-per-call overhead matters.

## NEXUS single-session service mode

Because MindTrial already creates one service instance per task execution attempt, NEXUS does
not need to expose model-visible session creation in this mode.

NEXUS should provide a runner-friendly single-session service interface such as:

```text
GET  /health
GET  /manifest
GET  /evidence/{name}
GET  /observe
POST /action
GET  /status
GET  /events
```

There is:

```text
no POST /sessions
no reset
no restart
no new_game
```

The service creates its one game session when the process starts.

NEXUS may retain its existing multi-session HTTP API for other consumers. Single-session service
mode is simply another transport/lifecycle option and is not MindTrial-specific.

## Restart prevention

With this architecture, the evaluated model cannot restart a failed game:

1. the public NEXUS action schema contains no reset action;
2. the per-attempt service exposes no session-creation/reset endpoint;
3. the model does not control service/container lifecycle;
4. the tool container does not receive the Docker socket;
5. terminal NEXUS state is irreversible;
6. provider/task retries reuse the same service;
7. a crashed service is an infrastructure error, not an automatic fresh game.

A human/operator explicitly rerunning the entire MindTrial task is a new benchmark attempt and
should be recorded as such.

## Public action contract

The model should know the stable NEXUS control interface.

The tool schema and description should expose ordinary semantics for:

- observe;
- move;
- take;
- drop;
- operate;
- probe;
- wait;
- finish.

The challenge is discovering the episode's causal world and planning within it, not guessing an
undocumented tool API.

## Evidence and attachments

Public NEXUS evidence can still use MindTrial's ordinary task-file mechanisms when desired:

- `facility_manual.txt`;
- `measurements.csv`;
- future images or other public attachments.

These can be exposed natively to the model, locally to Python, or both according to MindTrial's
normal file-access configuration.

The private compiled episode is different: it is a service-only input and must never enter
MindTrial's model/task file set.

## Expected result

A task prompt can remain simple:

```text
Complete the NEXUS mission using the nexus tool.
When NEXUS reports victory, return the victory code exactly.
```

MindTrial compares that final code using ordinary exact-result validation.

No NEXUS-specific validation logic or LLM judge is required.

## Why this abstraction is useful beyond NEXUS

A generic per-task service facility could support other interactive or stateful evaluation
environments:

- game/simulation servers;
- local web applications;
- databases with task-specific state;
- API emulators;
- coding sandboxes with daemon state;
- mock external systems;
- browser targets;
- robotics/simulation bridges.

That makes the MindTrial change defensible as a general execution capability rather than a
benchmark-specific integration.
