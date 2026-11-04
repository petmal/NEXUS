# Protocol and evaluator reference

This reference describes the stable transport and terminal metrics. Start with
[the operator guide](../evaluation-guide.md) for a first run.

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

## HTTP runner

```bash
nexus serve ./episode/private.json --host 127.0.0.1 --port 8000
```

The multi-session service is for legacy exploration. Scientific families that
require a non-resettable attempt reject this mode; use `serve-session` below.

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



## Terminal performance telemetry

Terminal `won`/`failed` action responses include a `performance` object. Legacy
profiles report exact physical and guaranteed-policy baselines, action/probe deltas,
profile identifiers, and error/retry counters. Scientific families report their
own certificates and mission/evidence metrics; unavailable fields are not zero. The object includes an immutable `$schema` URL. The published schema is
[schemas/performance-v6.schema.json](../../schemas/performance-v6.schema.json), whose field descriptions
are intended to make benchmark logs directly interpretable by downstream tools and LLMs.

## Single-session service and container integration

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


## Private audit export

The single-session HTTP service and JSONL CLI accept `--audit-dir NEW_DIRECTORY`.
See [the research guide](../research-guide.md) for the bundle, its verification scope,
and the distinction between world status and evaluator closure.
