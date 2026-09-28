# Service integration

NEXUS exposes neutral service and client interfaces for external orchestrators. The interfaces
do not assume a particular evaluation framework, model vendor, or transport beyond HTTP.

## Single-session lifecycle

Use `nexus serve-session` when the surrounding system already creates one NEXUS process for one
independent attempt. The process creates exactly one mutable session and exposes no endpoint for
creating, resetting, or replacing it.

A generated episode can be selected with a seed:

```bash
NEXUS_SEED=17 NEXUS_HOST=0.0.0.0 nexus serve-session
```

Or an existing compiled private episode can be mounted and loaded:

```bash
nexus serve-session --private /episode/private.json --host 0.0.0.0
```

Supported startup environment variables are:

```text
NEXUS_SEED               deterministic public episode generation seed
NEXUS_VERIFIER_SECRET    optional fixed private secret for reproducible victory codes
NEXUS_HOST               server bind address
NEXUS_PORT               server port
```

When `NEXUS_VERIFIER_SECRET` is omitted, each generated service process gets a fresh private
secret and therefore a fresh victory code even when the public episode seed is the same.

## Player-safe single-session API

```text
GET  /health
GET  /manifest
GET  /evidence/{filename}
GET  /observe
POST /action
GET  /status
GET  /events
```

The API deliberately has no reset, restart, or create-session operation.

The status response exposes the victory code only after the session has reached `won`. This is
equivalent to the code returned by the successful `finish` action and lets a trusted validator
verify the final submitted value without access to the private episode.

## Stateless client command

`nexus request` is intended for short-lived tool containers and other stateless callers. It reads
one JSON request envelope from a file and uses `NEXUS_URL` (or `--url`) to reach a
single-session service.

Supported operations are:

```json
{"operation":"manifest"}
{"operation":"evidence","filename":"measurements.csv"}
{"operation":"observe"}
{"operation":"status"}
{"operation":"action","action":{"type":"wait"}}
```

Each request file contains exactly one of these JSON objects. For example, a file containing:

```json
{"operation":"action","action":{"type":"wait"}}
```

can be executed with:

```bash
nexus request --request-file /input/request.json
```

For `action`, the client first reads the live status and supplies the current turn automatically.

## Health command

`nexus health` performs a real request against `/health` and exits non-zero if the service is
unreachable or unhealthy.

## Validation command

`nexus validate` verifies a submitted victory code against the live session:

```bash
nexus validate --candidate NX-ABCD-EFGH-IJKL
nexus validate --candidate-file /input/candidate
```

The `--candidate` form is convenient for a short victory code. The `--candidate-file` form is
preferable when the candidate is supplied through a generic file transport or may contain data
that is awkward to place on a command line.

The candidate file is **raw text**, not a `nexus request` JSON envelope. Its entire contents are
treated as the submitted code, with surrounding whitespace ignored:

```text
NX-ABCD-EFGH-IJKL
```

An ordinary wrong answer is represented as `correct:false` with exit code 0. Connectivity,
protocol, or inconsistent-server failures exit non-zero.

## Container image

The repository Dockerfile installs the server extra and uses `nexus` as the image entrypoint.
The same image can therefore act as the persistent service, short-lived request client, health
check, and trusted validation client.

## Trust boundaries

The private episode, latent rule AST, reference plan, and verifier secret remain inside the
service process. Player-facing clients need only the service URL. The surrounding orchestrator
owns process/container lifetime; restarting a crashed service is a new attempt, not a continuation
of the previous mutable world.
