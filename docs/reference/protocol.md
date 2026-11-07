# Protocol and evaluator reference

This reference describes the stable transport and terminal metrics. Start with
[the operator guide](../evaluation-guide.md) for a first run.

## Single-session service and container integration

Use one service process per model attempt. For local use, bind to loopback:

```bash
NEXUS_SEED=17 NEXUS_DISCOVERY_LEVEL=1 NEXUS_PLANNING_LEVEL=1 \
NEXUS_RESOURCE_PRESSURE=0 NEXUS_HOST=127.0.0.1 nexus serve-session
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

When explicitly enabled for a compatible world, `POST /check` also provides the disclosed construction checker. The evaluator-only `POST /finalize` closes the attempt and returns terminal status and performance. Neither access to the evaluator nor arbitrary network access belongs in the model tool.

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
the optimistic-concurrency turn field themselves. For a direct `POST /action`, retry
an uncertain response using the **same** `expected_turn` and action. A committed
retry returns its original turn, observation and events with `duplicate: true`;
terminal performance, when available, reflects current request counters. A different
action for an already committed turn is rejected.

Health checks can use:

```bash
nexus health
```

After the attempt, a trusted process can validate the submitted receipt without reading
the private episode. Validation finalizes the session, even if the player never won; do not expose it as a player tool. For a short code, pass it directly:

```bash
NEXUS_URL=http://nexus:8000 nexus validate --candidate NX-ABCD-EFGH-IJKL-MNOP
```

For file-based transport:

```bash
NEXUS_URL=http://nexus:8000 nexus validate --candidate-file /input/candidate
```

Unlike `nexus request --request-file`, the validator file is **not JSON**. It contains only the
submitted victory code as raw text, for example:

```text
NX-ABCD-EFGH-IJKL-MNOP
```

A valid check prints one JSON object with `correct`, `title`, and `explanation`. An incorrect
candidate is a normal `correct:false` result; transport/protocol failures exit non-zero.

The validator also checks that final status agrees with `performance.terminal_status`,
and that only a won session has a nonempty receipt. A contradictory service
response is a protocol error, not a model score.

A container image can be built directly from the repository. The Dockerfile pins both the
Python/Debian base image digest and the locked Python dependency graph:

```bash
docker build --build-arg VCS_REF="$(git rev-parse HEAD)" -t nexus:0.1.0 .
docker run --rm -p 127.0.0.1:8000:8000 \
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

Windows builds are supported. Git attributes keep qualified Python/JSON files at
LF; the Docker build also restores CRLF to LF in its private source copy for older
checkouts. It then checks the installed package against the exact qualified source,
proof and witness hashes. Other changes still fail the build. Do not regenerate
the qualification manifest merely to make a changed package pass.

Before running the repair model pilot, complete both public missions in the actual
image (the same command works with Docker or Podman, including PowerShell):

```sh
docker run --rm --entrypoint python nexus:0.1.0 scripts/preflight_repair.py
```

Both P0 and P1 must report `qualified`, `won` and `replay verified`. A failed build
or preflight must be resolved before launching the model runs; an OCI label alone
does not certify package contents. Direct wheel builds from older CRLF checkouts
should run `python scripts/prepare_package.py` before `uv build`.

See [Service integration](../service-integration.md) for trust boundaries and configuration
patterns.


## Terminal performance

A terminal action or evaluator finalization can return `performance`. Read
`$schema` for legacy and controller reports, or `version` and `ontology` for
mission reports. [Metric definitions and schema links](metrics.md) explain how to
interpret action costs, evidence support, physical success and missing fields.
The service cannot tell you whether the provider finished normally or whether
the harness accepted the model's final answer.

## Private audit export

The single-session HTTP service and JSONL CLI accept `--audit-dir NEW_DIRECTORY`.
See [the research guide](../research-guide.md) for the bundle, its verification scope,
and the distinction between world status and evaluator closure.

## JSONL agent protocol

```bash
nexus stdio ./episode/private.json
```

The process emits the initial observation, then accepts requests such as:

```json
{"expected_turn": 0, "action": {"type": "wait"}}
```

The example spends one action. Use the observation and action contract to choose
a useful next action. `expected_turn` must be a nonnegative integer.

## Legacy multi-session HTTP

```bash
nexus serve ./episode/private.json --host 127.0.0.1 --port 8000
```

The multi-session service is for legacy exploration. Scientific families that
require a non-resettable attempt reject this mode; use the [single-session service](#single-session-service-and-container-integration).

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
