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
GET  /events  (operator replay trace)
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

For a new action the client normally reads the current turn. If your harness
may retry after a timeout, put the turn from the last observation in the
**original** request and send exactly that request again:

```json
{"operation":"action","expected_turn":0,"action":{"type":"wait"}}
```

A pinned request goes straight to `POST /action`. A retry with the same turn
and action returns the committed turn, observation and events with
`duplicate: true`; on older presentations, a terminal reply also includes performance with current
request counters. A different action for a committed turn is rejected. Repeating an
**unpinned** request asks to act on the latest turn and can spend a second action.
Raw `POST /action` always requires a nonnegative integer `expected_turn`.

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

Evaluator finalization returns `performance`. Older presentations also returned it in terminal action replies. Read
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

The first output line contains `{"observation": ...}`. After that, send one
JSON object per line. Start with the manifest to learn the mission and which
evidence filenames this world offers:

```jsonl
{"operation":"manifest"}
{"operation":"observe"}
{"operation":"status"}
{"operation":"action","expected_turn":0,"action":{"type":"wait"}}
```

Use `{"operation":"evidence","filename":"..."}` with a listed name; the response
contains `filename` and the presented `content`. These reads are free. The
example's `wait` spends one action. A world that explicitly enables construction
checking also accepts `{"operation":"check","build":[0,0,3,0]}` with an integer list.
The original action envelope, e.g. `{"expected_turn":0,"action":{"type":"wait"}}`,
still works. EOF closes the stream without scoring an active world. There is
no player `finalize` operation.

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
GET  /sessions/{id}/events  (operator replay trace)
POST /sessions/{id}/finalize  (evaluator only)
```

Canonical state, latent rules, reference plans, and verifier secrets remain server-side. The player-safe manifest also includes the machine-readable action schema and human-readable action reference.

## Player console presentation

Newly generated worlds use `sealed-facility-v4`. Operator family, difficulty and
serializer tags are omitted from playable records and object payloads. Family-specific controls now appear under `action_contract.apparatus`. The public
IDs, laws supplied in this run, physical target and remaining resources stay
available. In the four-register worlds an action message labels a hypothetical
seal display or a committed reading. Structured result payloads remain available.
The current display is always in the observation: a preview never replaces it.

In v3 and v4, player action replies omit terminal performance, including on retry. Read
it through the evaluator’s finalization or audit interface. A terminal victory
receipt remains in the player reply. Prior versions keep their wire behavior.
Compare runs using the recorded presentation version and presented evidence hash.
Terminal editing, shorthand and the local log do not change the JSON action protocol.

The survey and routing laboratories also label configuration, preparation,
measurement and installation. Readings are included in action messages and the
local log as well as structured events. A preview leaves the artifact unchanged;
an operated reader or sensor stores a historical measurement. Neither a doser
preview nor an assembler preview checks the mission. The routing reader always
measures the facility reference, even when the carrier has a cartridge installed.
Apparatus records describe these distinctions and preserve the selected finish
policy. These explanations use only public controls and returned results.

V4 adds explicit laboratory notation, context replacement versus output offset,
fixed exit-check semantics and routing link indexing. Saved v1/v2/v3 worlds retain
their evidence and response wording. The local console accepts bracketed integer
arrays as well as space-separated settings, renders checks and links as tables,
and summarizes applied treatments separately from preparations and stored readings.
Structured observation/event payloads are retained; no hidden-law inference or
additional measurement is performed by the display or log.
