# Service integration

For a first run, use the [evaluation guide](evaluation-guide.md). The service is
local research infrastructure, with no authentication or tenant isolation. Bind
`0.0.0.0` only inside a harness-isolated network, never on a public interface.
Keep `/finalize` evaluator-only through the harness tool allowlist.

`serve-session --audit-dir NEW_DIRECTORY` records a private source-bound bundle.
The surrounding framework owns persistent storage, attempt-to-bundle mapping and
collection after shutdown. Use [the research guide](research-guide.md) for that
storage contract, verification and disclosure limits. MindTrial is one example
adapter; the NEXUS runtime and audit format remain independent of it.

NEXUS exposes neutral service and client interfaces for external orchestrators. The interfaces
do not assume a particular evaluation framework, model vendor, or transport beyond HTTP.

## Single-session lifecycle

Use `nexus serve-session` when the surrounding system already creates one NEXUS process for one
independent attempt. The process creates exactly one mutable session and exposes no endpoint for
creating, resetting, or replacing it.

A generated episode can be selected with a seed:

```bash
NEXUS_SEED=17 NEXUS_THEORY_LEVEL=0 \
NEXUS_DISCOVERY_LEVEL=1 NEXUS_PLANNING_LEVEL=1 \
NEXUS_RESOURCE_PRESSURE=0 NEXUS_HOST=0.0.0.0 nexus serve-session
```

Or an existing compiled private episode can be mounted and loaded:

```bash
nexus serve-session --private /episode/private.json --host 0.0.0.0
```

Supported startup environment variables are:

```text
NEXUS_SEED               private deterministic episode generation seed
NEXUS_AXIS_VERSION       1=legacy, 2=scientific family semantics
NEXUS_SCIENCE_FAMILY     registered family name
NEXUS_THEORY_LEVEL       supplied-theory profile (family-specific)
NEXUS_BUDGET_PROFILE     standard or a supported diagnostic profile
NEXUS_ONTOLOGY_OPTIONS   validated JSON family options
NEXUS_AUDIT_DIR          new private audit export directory
NEXUS_EXTENDED_DIAGNOSTICS  private operator stderr diagnostics
NEXUS_DISCOVERY_LEVEL    causal-discovery profile, integer 0..5 (default 0)
NEXUS_PLANNING_LEVEL     topology/planning profile, integer 0..3 (default 1)
NEXUS_RESOURCE_PRESSURE  action-budget pressure, integer 0..2 (default 0)
NEXUS_VERIFIER_SECRET    optional fixed private secret for reproducible victory codes
NEXUS_HOST               server bind address
NEXUS_PORT               server port
```

The difficulty variables apply only when the service generates from `NEXUS_SEED`; a mounted
private episode already contains its compiled world and metadata. When `NEXUS_VERIFIER_SECRET`
is omitted, each generated service process gets a fresh private secret and therefore a fresh
victory code even when the private construction seed is the same. Public identifiers are opaque.

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

## Terminal performance telemetry

The action response that first reaches `won` or `failed` includes a terminal-only `performance`
object. It is absent while the episode is active, so trusted solver information cannot influence
play.

Legacy profiles report mechanically qualified policy baselines. Scientific families
use separate mission metrics and certificates; a reference upper bound must not be
read as an exact optimum. Consult the actual certificate for the tested condition.
The legacy terminal object includes an immutable `$schema` URL pointing to the versioned
`schemas/performance-v6.schema.json` contract stored in this repository. In addition to the run
counters it records the discovery/planning/resource-pressure profile, terminal status, initial
budget, resource allowance, and P3 dependency cost.

Important baseline fields are:

- `optimal_physical_actions`: omniscient selected-world BFS optimum;
- `minimum_guaranteed_probes`: minimum worst-case causal probe count;
- `guaranteed_policy_actions`: exact minimum worst-case total action cost across all viable
  public-evidence-consistent hidden worlds;
- `action_delta_from_guaranteed_policy`: signed realized actions minus that minimax baseline; and
- `probe_delta_from_guaranteed_minimum`: signed realized probes minus the guaranteed probe count.

The deltas are intentionally signed. A negative value does not automatically mean better
reasoning: an agent may beat a worst-case guarantee because the selected hidden world was
favorable or because it took epistemic risk and guessed correctly.

`invalid_actions`, `duplicate_requests`, and `protocol_conflicts` do not consume environment
actions. Rejected `finish` attempts do consume an action and are counted separately as
`failed_finishes`.

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


## Terminal diagnostics and operator timing

Terminal action responses contain `performance` using the immutable performance-v5 schema
referenced by `$schema`. This adds accepted action counts, room visits/revisits, a comparison to
moves in the stored physical reference plan, and public-goal satisfaction diagnostics. A room
revisit is not necessarily waste, and the stored plan's move count is not a standalone optimum
for navigation. Leaf counts describe atomic predicates, not a score for arbitrary OR/NOT goals.

`nexus validate` finalizes the attempt before checking the submitted code. If the session is still
active, finalization irreversibly marks it failed without consuming a game action. It returns
terminal diagnostics even for an early model stop. A won session retains its receipt; repeated
finalization is idempotent. The validator writes the usual `{correct,title,explanation}` JSON to
stdout and a `NEXUS terminal performance: {...}` line to stderr, including through the fast CLI
entrypoint. Capture stderr separately from the validator result.

This distinguishes a satisfied goal with no successful `finish` from missing deliveries or
incorrect transformations. It does not weaken the explicit-finish victory rule. `/finalize` is
excluded from the player request envelope and OpenAPI description; direct premature calls end
the attempt, so diagnostics cannot be used to continue playing. Ordinary active-session action,
status, observation, and manifest responses contain no terminal diagnostics.

If the orchestrator aborts on an API/parsing error before invoking its validator, it must still
call the evaluator's finalization endpoint before destroying the service to collect this report.
NEXUS cannot record the model provider's error category; retain that harness outcome alongside
the NEXUS terminal outcome. Finalization is an evaluator lifecycle operation, not a replayed
game action; an interrupted attempt's action trace ends at its last accepted environment action.

For slow service generation, enable operator-side timing:

```yaml
NEXUS_GENERATION_TIMING: "true"
```

Or use `nexus serve-session --seed 17 --discovery-level 5 --planning-level 3
--generation-timing`. Stage start/completion/error records go to server stderr. They cover core
generation, P3 dependency compilation, resource pressure, final qualification, and cold policy
solver phases. Timings never enter compiled episode data or player responses. Keep service logs
outside the player's tools/files; they are operator diagnostics. No seeds, rules, witnesses,
verifier secrets, or goal values are written by these timing records.

For a cold troubleshooting run with a durable JSON report:

```bash
uv run python scripts/profile_generation.py \
  --seed 17 --discovery-level 5 --planning-level 3 --resource-pressure 0 \
  --json-out /tmp/d5p3.json
```

Progress is streamed to stderr while JSON is emitted to stdout and the requested file. The report
includes runtime information, peak RSS (MiB), solver memo/branch counts, and a hash of the compiled
episode for reproducibility with the profiler's fixed verifier secret. Use `--cprofile` and
`--profile-out /tmp/d5p3.prof` for function-level attribution; profiled wall times include cProfile
overhead. Parent/child stage times are inclusive and must not be added together. Run each seed
and profile in a fresh process when comparing cold service startup costs.

The current payload also includes `action_delta_from_physical_optimum` and
`unsatisfied_goal_conditions`. The latter decomposes false conjunctions but preserves OR/NOT
expressions, so a false atomic leaf is not misreported as an independently required condition.
Historical v1–v4 schemas remain unchanged. See [model testing matrix](model-testing-matrix.md).


## Theory-prior configuration

Use `--theory-level 1` or `NEXUS_THEORY_LEVEL=1` when generating a session. The default T0
preserves existing worlds. T1 supports D0–D4 and P0–P3/R0–R2, subject to paired-seed qualification;
T2 supports D2/P0–P3/R0–R2 using `NEXUS_THEORY_LEVEL=2`. T1/D5, T2 with any D other
than D2, and T3+ fail explicitly. Settings are generation inputs; loading `--private` uses the
already compiled episode's metadata, as with D/P/R.

T1's `theory.json` and manual describe the same complete structural prior used by the evaluator.
Evidence is replanned against that prior; budgets are recomputed from its exact policy. Some
seeds cannot be certified by the bounded evidence planner and fail before serving. Preflight a
seed with `nexus generate` and `nexus qualify`; never silently retry another seed while labeling
it as the original paired task. See [T-axis validation](theory-implementation-results.md).

T2 is an effective model with independently bounded corrections at phases 1 and 3;
its supplied calibration at phases 0 and 2 agrees exactly with the effective model.
The complete disclosed prior contains nine laws, five of which satisfy the public physical
solvability promise. Every accepted episode has an exact guaranteed policy. Its world family
is separate from T0/T1; only T2's own P2/P3 and resource variants have the documented pairing.

Terminal telemetry uses performance-v5, permitting required integer `theory_level` 0, 1 or 2.
The immutable schema reference points to commit `c24f44f510df32453c6e2860ef86640ab3ac6f8e`.
The previous v1–v4 schemas remain unchanged for historical artifacts. No active-session
performance fields or evaluator-finalization behavior changed.

Operator generation logging now ends with `event=generation_summary`: one JSON line with
total wall/process-CPU seconds and stage paths, counts, errors and inclusive elapsed times.
Thus a last-50-lines container capture retains the core timing even for P3/theory generation.
Paths distinguish repeated solver work under core, theory, planning dependency and qualification.
Do not sum nested stage durations; use the summary's total for whole-generation time. Process
CPU time includes all threads in that process and is not host CPU utilization. Catalogue
construction/signature-matrix and mechanics/evidence stages expose pre-solver cold-start work.
Logging remains opt-in via the existing `NEXUS_GENERATION_TIMING=true` setting, on stderr only;
operator logs must not be mounted or forwarded into the player's tool response.
