# NEXUS

The latest opt-in families are `coupled-transfer-v1` (a counterprogram must match
the complete physical behavior) and `coupled-evidence-v1` (raw readings also
depend on a coupled upstream mechanism). See the [qualified pilot and limits](docs/transfer-pilot.md),
[public-response walkthrough](docs/transfer-player-walkthrough.md), and
[implementation ledger](docs/evidence-transfer-implementation.md). These are
experimental capability contrasts, not a promise that the combined reader is
uniformly harder or that models will fail. Existing defaults remain unchanged.

The earlier opt-in `compositional-repair-v1` discovers shared local
mechanisms across two contexts and apply one joint physical repair. See the
[eight-run experimental pilot](docs/structural-model-matrix.md),
[paired budget diagnostic](docs/budget-diagnostic-matrix.md),
[construction and proof limits](docs/structural-reasoning-proof.md), and
[resume ledger](docs/structural-reasoning-implementation.md). Existing families
and the [ten-run dynamics/control matrix](docs/difficulty-model-matrix.md) remain
available. Dynamics generation now reuses a checked seed-independent proof;
episode laws, evidence and budgets are unchanged. New structural difficulty
remains uncalibrated until real-model trials.

NEXUS is a standalone, deterministic interactive environment for evaluating whether an LLM can enter a procedurally novel artificial micro-world, infer its unfamiliar causal structure from evidence and experimentation, maintain an evolving world model, and plan actions that reach a mechanically verified goal.

The central design goal is to evaluate **adaptation and reasoning rather than recalled domain knowledge**. NEXUS does not model an existing human game, real-world physics, or a known scientific experiment. Episodes are compiled from a small compositional grammar that can vary the world topology, entities, latent causal laws, evidence, and objective.

## Current research feature: the Sealed Facility

Newly generated episodes share a versioned alien-facility presentation across all
ontologies; historical episodes retain their saved presentation and mechanics.
The opt-in `coupled-repair-v1` family adds a physical repair mission with a checked
three-feedback-round public policy. At its exact T3/D5/P0-or-P1/R1 budgets, any
policy using at most two feedback rounds has success probability at most 3/7 over
the declared conditional uniform prior. This is a structural guarantee, not an
empirical prediction that models will fail. One extra action removes that bound.

Use the [ten-run model matrix](docs/repair-model-matrix.md),
[exact environment blocks](docs/repair-model-matrix.json),
[implementation results and scope](docs/repair-results.md), and
[live conformance argument](docs/repair-live-conformance.md).
Existing families and default selection remain available.

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
- [Scientific investigation, axes v2](docs/scientific-investigation-design.md) — approved T/D meanings, zero-level controls, proofs and bounded-family limitations.
- [Scientific model pilot](docs/scientific-investigation-model-matrix.md) — ten nonzero-axis runs with exact environment settings.
- [Service integration](docs/service-integration.md) — single-session service, client, health, validation, and generated-session configuration.
- [AGENTS.md](AGENTS.md) — implementation constraints and staged development guidance.

## Development

See [AGENTS.md](AGENTS.md) for implementation constraints and staged development guidance.

All prototype work should remain isolated from unrelated projects. External harnesses should integrate through the standalone NEXUS protocols and CLI.


## Working prototype

The scientific investigation profiles are opt-in: use `NEXUS_AXIS_VERSION=2` for
services, or `nexus generate ./episode --axis-version 2 --seed 7 --discovery-level 5
--theory-level 3 --planning-level 1 --resource-pressure 1`. These profiles combine
instrument calibration, correction/relationship inference, specimen preparation,
and predictions at unmeasured field conditions through the existing facility API.
Use `nexus actions --axis-version 2` for their controls. R0 is unlimited/recoverable;
P0 has one room. Existing profiles and seed meanings remain the default version1.
See the [results and validation](docs/scientific-investigation-results.md) before
interpreting these bounded tasks as evidence of frontier-model difficulty.

The richer experimental family is selected separately with
`NEXUS_SCIENCE_FAMILY=coupled-network-v1` (CLI: `--science-family coupled-network-v1`).
It requires axes v2 and supports T3/D4 or T3/D5, plus D0/T0,T3 controls.
Three composed relationship choices replace the simple response curve; D5 requires
combining noncommuting preparation operations. See the
[design and validation](docs/rich-investigation-results.md) and
[ten-run paired pilot](docs/rich-investigation-model-matrix.md).
Without this setting, the existing `shared-response-v1` family remains unchanged.

For dependent discovery and a larger experimental domain, select
`NEXUS_SCIENCE_FAMILY=resonant-network-v1` with the same supported T/D/P/R cells.
Infer a resonance law to tune downstream measurements, then combine both laws
for held-out field predictions. There are45 bench coordinates; complete sweeps
exceed moderate P1/R1 budgets, while a public-information policy is certified.
See the [proofs and limitations](docs/resonant-network-results.md) and
[ten-run model matrix](docs/resonant-network-model-matrix.md). Existing families
remain selectable; real-model difficulty of this new family is not yet measured.

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


## Theory prior (T)

T0 is the existing explicit finite grammar. Opt-in T1 supplies independent value, polarity and
rotation primitives with bounded shape/phase conditions. Its public `theory.json` and manual
come from the evaluator's structured prior, covering 27,120 distinct behaviors. Only evidence
survivors are materialized for exact policy solving; the belief is never silently truncated.

```bash
uv run nexus generate /tmp/nexus-t1 --seed 17 --discovery-level 2 \
  --planning-level 2 --resource-pressure 0 --theory-level 1
uv run nexus qualify /tmp/nexus-t1/private.json
```

For services set `NEXUS_THEORY_LEVEL=1`. T1 currently supports D0–D4; T1/D5 remains
unsupported. Seeded T0/T1 pairs preserve their physical world; T1 evidence and exact action
budgets can differ. A seed is explicitly rejected when bounded evidence search cannot certify
its D guarantee. This is an experimental calibration release, not a promise that every seed or
higher T value is supported. True laws currently retain the paired T0 sampling distribution;
T1 tests a broader disclosed prior, not full-universe true-law sampling.

D4/T1 retains the exact selective-experiment proof: an informative auxiliary probe is optimal,
while the distractor probe costs an extra action. The direct mission probe can also be optimal;
D4 is not guaranteed to be harder than the two-stage D3 tasks. D4 evidence search is bounded and
may reject paired seeds (including seeds 0 and 2 in the initial P2 sample). See
[the next-pass results](docs/theory-next-pass-results.md) for acceptance and model calibration.
T2 now supports **D2/P0–P3/R0–R2** through `--theory-level 2` or
`NEXUS_THEORY_LEVEL=2`. It discloses an effective additive model, exact validity phases,
and the complete nine-law correction family. Calibration leaves the correction unknown;
one informed probe guarantees the mission under all five physically viable laws.
This is a separate world family: equal seeds do **not** imply T0/T1/T2 physical pairing.
Other T2 discovery levels reject explicitly. For example:

```bash
uv run nexus generate /tmp/nexus-t2 --seed 17 --discovery-level 2 \
  --planning-level 2 --resource-pressure 1 --theory-level 2
uv run nexus qualify /tmp/nexus-t2/private.json
```

T3 now supports **D2/P0–P3/R0–R2** through `--theory-level 3` or
`NEXUS_THEORY_LEVEL=3`. Its complete bounded prior permits an independently selected
add-one, add-two or multiply-two operator for each shape/parity context, with no supplied
baseline law. Another-shape calibration leaves 243 full laws; nine reachable behavior classes
suffice for exact solving. The reduction is validated against full-law enumeration/replay.
T3 is a separate family and is not guaranteed harder than T1/T2.

```bash
uv run nexus generate /tmp/nexus-t3 --seed 7 --discovery-level 2 \
  --planning-level 0 --resource-pressure 0 --theory-level 3
uv run nexus qualify /tmp/nexus-t3/private.json
uv run python scripts/theory_progression_poc.py
```

The cumulative T1→T2→T3 progression remains a separate information-only PoC. It proves
correction-to-relationship dependencies and held-out prediction with independent/known-c
controls; it does not change D semantics or introduce a live progression flag. The earlier
`scripts/theory_structure_poc.py` remains an additive-only historical research control.
See [T3/progression results](docs/theory-t3-progression-results.md),
[the reasoning-focused ten-run matrix](docs/theory-reasoning-model-matrix.md), and
[the resumable checkpoint](docs/theory-t3-progression-plan.md).

See [validation and model matrix](docs/theory-implementation-results.md) and the
[resumable checkpoint](docs/theory-implementation-progress.md).

### Scientific ontology extension

Scientific families now run behind an explicit runtime and inference adapter.
New domains can use validated entity payloads and composed investigation graphs
without legacy shape/polarity fields or controller ports. See the
[ontology author guide](docs/ontology-author-guide.md),
[architecture plan](docs/ontology-architecture-plan.md), and
[implementation checkpoint](docs/ontology-implementation-plan.md).
The categorical chain example is an exhaustive conformance PoC, not a calibrated
production difficulty profile or a claim of increased LLM failure rates.


### Causal mechanism laboratory

Select `NEXUS_AXIS_VERSION=2` and `NEXUS_SCIENCE_FAMILY=causal-mechanisms-v1`
for the new experimental ontology. It combines latent preparation state, unknown
causal wiring, known-shape corrections and six held-out transfer predictions.
Use T3/D5/P1/R1 for the main pilot. Supported alternatives are T1/D1, T2/D2 and
D0/T0–T3, with P0/P1 and R0–R2. Existing families and defaults remain available.
See the [design](docs/causal-mechanisms-design.md),
[validation and limits](docs/causal-mechanisms-results.md), and
[ten-run pilot](docs/causal-mechanisms-model-matrix.md).

The opt-in [`history-coupled-v1` PoC](docs/history-coupled-results.md) adds specimen
history, delayed effects and exact joint-state inference while preserving prior
families. Its ten-row diagnostic includes known-law and budget controls. It is
experimental: qualification records legal shortcuts and does not admit a certified
deep-reasoning tier.
