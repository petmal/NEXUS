# Authoring a scientific ontology

NEXUS now separates scientific runtime behavior from engine accounting. Existing
shared-response, coupled-network and resonant-network formats remain supported by
one compatibility adapter. New domains use versioned validated envelopes, without
inventing legacy shape, orientation or polarity fields.

## What remains fixed

The engine owns transactional state copying, locality checks, turn/resource
consumption, terminal transitions, replay records and HMAC victory receipts.
Adapters must not change these. Invalid actions raise `ValueError` and the engine
discards the working copy. Probe results do not mutate the carried specimen.

Player manifests and observations contain controls and observable properties.
Selected laws, seeds, solver witnesses, hidden targets and inference diagnostics
remain private. Player-visible diagnostics become available only after termination. Private operator
reports may inspect an active attempt and must remain outside player access. Inference
adapters receive the public specification and public measurement results; they do
not receive selected private truth.

T remains theory sufficiency, D inferential dependency/experiment construction,
P logistics, and R resource pressure. An ontology must qualify its supported
profiles; assigning a number or drawing a dependency graph does not prove a
particular difficulty. Equivalent mission predictions count as the same target,
and unsuccessful eligible submissions are evidence. There are no mandatory
verbal scientific-method rituals or stage unlocks.

## Writing the player briefing

Use the [facility setting](facility-setting.md): one local mission, exact acceptance
conditions and exit clearance on successful `finish`. Call the exit lock an
interlock and a portable part a seal component; keep action IDs explicit. Define
new artificial terms beside their controls. Give the world a listed `facility.txt`,
`manual.txt`, `manual.md` or `facility_manual.txt` so it receives the shared orientation.

Keep the brief valid for both disclosed and hidden-law profiles. Story labels must
not depend on private truth, reference plans or qualification results. Do not add
an implied time limit, secret object, experiment order or extra escape step. Keep
formal records complete; prose cannot override an action or goal contract. Use the
shared presentation layer for player output, preserve historical presentation
versions, and extend the public-surface tests when adding a family.

## Extension points

| Component | Responsibility | Existing example |
|---|---|---|
| `ontology/catalog.py` | Explicit version/family selection and lazy factories | Published scientific adapters |
| `ontology/contracts.py` | Runtime ownership and structural interface | `builtin_runtime.py` |
| `ontology/payloads.py` | Role lookup through the catalog; no second registration map | Lazy data-only schemas |
| `models/domain.py` | Common JSON envelopes with load-time validation | No additional core union per future ontology |
| `ontology/graph.py` | Immutable ordered DAG, trusted primitive evaluation | Categorical chains; resonant dependency description |
| `ontology/inference.py` | Public measurement and belief interfaces | Flat and resonant posterior adapters |
| `protocol/investigation_metrics.py` | Common trace accounting, legacy or mission projection | Terminal-only mission diagnostics |

A new ontology supplies data-only Pydantic payload schemas, a runtime adapter,
generator, public evidence, inference backend and qualification checks. Register
its version explicitly. No runtime import paths, executable expressions or package
installation can come from episode/player data. Third-party plugin discovery is
not implemented; these are trusted built-in extension points.

Payload roles are determined by the containing typed envelope class. A public
artifact is validated against the artifact schema, never the truth schema.
Unknown ontology/version, extra fields and wrong property types fail loading.
After deserializing a private episode, validate cross-envelope relationships and
initial apparatus settings as well as each individual payload.

`configure` currently accepts bounded integer vectors (0..16, at most nine
values). A categorical domain can publish selectors, but arbitrary text-valued
controls require a deliberate versioned action-contract extension. This refactor
does not quietly broaden the interaction protocol.

## Mutation and inference contracts

`spawn` and `transform` return fresh entities. `configure` and `assess_mission`
may mutate only the engine-owned working state. They do not consume actions or
emit receipts. Public projections receive public data; a private truth payload
must never be embedded in a public entity. The generic engine serializes only the
returned entity for measurement events.

`belief(spec)` builds a fresh mutable posterior over immutable reusable data.
`measurement(record)` normalizes existing event formats, preserving saved trace
compatibility. `observe` and `exclude_target` update that posterior. Zero readings
and no-signal outcomes are distinct. Flat enumeration, factored inference and
future backends can implement this contract without changing session accounting.
Do not force a large ontology through the small finite-minimax backend's limits.

A graph proves that references are defined, unique and acyclic. The family still
has to prove identifiability, predictive equivalence, meaningful dependencies,
reference-policy realizability and any claimed resource bound. The existing
resonant law evaluator remains unchanged for compatibility; its graph is a
structural description. The categorical evaluator executes its graph directly.

## Categorical composition PoC

`categorical-chain-poc-v1` uses invented symbols `ka`, `tu`, `ve`, and two or
three independent unknown permutations. A later instrument needs the composed
upstream response as its tuning. The mission submits the composed response for
all three symbols on a prediction board, with no legacy port.

The reference policy learns each permutation from two readings. Exhaustive
checks cover all 36/216 worlds, with four/six readings and ten/fourteen actions.
Wrong tuning is informative; there is no forced experiment ordering. The target
space has only six equivalence classes at either depth. This is an extension and
composition proof, **not evidence that deeper chains defeat LLMs**.

The PoC is deliberately separate from production `generate_episode` profiles.
It supports one room, unlimited stocks/uses/actions and depth 2 or 3. Its
certificate says `experimental=true`, `calibrated_axes=false`. The legacy
metadata's D0 field is a compatibility placeholder, **not a D0 qualification**;
mission diagnostics report the experimental certificate rather than a calibrated
D claim. Do not put these runs into production D/T leaderboard comparisons.

Example (trusted operator Python, not a tool granted to evaluated models):

```python
from pathlib import Path
from nexus.io import save_episode
from nexus.ontology.categorical.generation import generate_categorical

save_episode(generate_categorical(7, depth=3), Path("categorical-episode"))
```

The generated private file can be served with the existing `nexus serve` or
`nexus stdio` commands. Keep it away from the evaluated player; provide the live
interface, manifest and public evidence. The private file is `categorical-episode/private.json`.

## Acceptance gates for a future ontology

1. Independent small-world proof before production integration.
2. Exact public-policy wins and posterior agreement with an independent oracle.
3. Private/public JSON round trips; reject mismatched versions and roles.
4. Invalid-action rollback, probe immutability and independent session state.
5. Replay including event payloads, active-play privacy and terminal finalization.
6. Existing compatibility fixtures unchanged; cold/warm generation measured.
7. Family-specific qualification before claiming a supported D/T/P/R profile.

Keep new family logic out of session, replay, receipt and generic measurement
accounting. Performance projections may differ by mission contract, but should
not require a branch for every ontology.

Submitted `ConfigureAction.settings` requires strict JSON integers; booleans,
floats and numeric strings are rejected. Stored `Machine.settings` retains its
existing Pydantic normalization for saved-world compatibility. Each runtime must
also check its own arity and range. Payload schemas validate their own properties
independently (including strict integer permutation laws).


## Stateful causal example

`ontology/causal` is a second domain adapter, with normal CLI/service selection.
Its specimens carry their complete public preparation history; immutable private
laws reconstruct a hidden mode. This avoids storing secret values in publicly
serialized artifact payloads or state hashes. A bounded history is essential:
unobserved exogenous updates or unbounded histories need a different state design.

The catalog now owns lazy runtime/generator/qualifier import targets and an optional
standalone action-reference hook. These paths are code-owned registrations, never
read from episodes. Declare `schema_module` in the same catalog registration. Its data-only `SCHEMAS`
map is loaded lazily without importing runtime or inference, avoiding model/runtime
import cycles. No additional map in `payloads.py` is needed. No changes to engine/session/replay are needed.

The causal adapter proves its graph semantics against independent arithmetic,
compiles complete finite transition/response tables, and maintains a joint bitset
posterior. The 568-experiment policy pool is only a sufficient witness: all legal
off-pool measurements still update the posterior exactly. See its tests and
[design](causal-mechanisms-design.md) before claiming difficulty guarantees for
another ontology. D/T labels require epistemic evidence, not graph size alone.

## Overlapping accepted decisions

`compositional-repair-v1` demonstrates a mission with multiple valid treatments.
Its runtime `assess_mission` checks the actual predicate, not equality with the
canonical vector used by an omniscient physical witness. Never turn overlapping
winning regions into transitive target-equivalence classes.

A belief adapter may additionally supply `common_decisions()` and `supports(dose)`.
The former returns decisions accepted by every currently possible world; the
latter checks a proposed, physically eligible treatment against that set. These
capabilities select terminal `mission-performance-v2`. Its signature counts are
explicitly distinguished from guaranteed-repair progress; resolution may occur
while several hidden worlds and winning-set signatures remain possible.
`exclude_target(dose)` must remove every world accepting a rejected eligible
submission. Ineligible failures must not eliminate its values; use the shared
applied-treatment tracker. No posterior diagnostics belong in active responses.

For `mission-performance-v3`, additionally expose belief `accepting_count(dose)`
and runtime `measurement_features(measurement) -> (context, intervention)`.
The count is the number of remaining worlds accepting that eligible dose, not a
probability; features return `(None, None)` for no-signal material readings.
These optional capabilities add pre-outcome submission classifications, physical
goal versus escape separation, and experiment coverage. The v2 adapter and parser
remain supported. See [post-run diagnostic design](budget-diagnostic-design.md).

For offline qualification, `solver.decision_audit.DecisionAudit` accepts complete
observation rows and decision acceptance masks. It supports common-decision
closure, bounded exact query/guess success, and an exhaustive zero/one/two-reading
certificate search. A returned lower bound of three means only at least three
measurements, including zero-valued readings; it does not cover rejected finishes
or certify a three-round policy. Qualify selected fixture scope separately from
uniform-prior probability claims, and keep both separate from empirical LLM
performance. The family-specific live conformance document must explain why every
legal response reduces to the mathematical audit's observation classes.

## Bounded specimen history example

`history-coupled-v1` demonstrates a physically constructed goal using public pulse
history and recomputed private state. Its eight-pulse domain has exact overlapping
winning sets; all committed/probed visible transitions update the public posterior.
A family-specific tracker follows actual seal history and ignores previews.
`log_terminal_trace(state, trace, posterior)` is an optional terminal-only hook for
operational evidence categories and recovery diagnostics. It does not affect play.

`OntologyDefinition.diagnostic_budget` declares support for the explicit
`budget_profile` generator argument and private-envelope validation. Add support
in one registration rather than repeating family-name lists in shared code.

The history family's `deep_tier_admitted=false` is intentional: finite proof found
shortcuts through repeated finishes and apparatus omission. A registered runtime
and a successful reference policy do not constitute deep-difficulty qualification.

## A concrete author workflow

Start with `uv run nexus ontologies --json`. This lists registered family/version,
schema location, factory availability and option schema without constructing any
world or inference prior. Registration is not difficulty admission.

Use `ontology/revision/` as a complete, small adapter example. It shares the
reader/carrier/assembler interaction with `ontology/discovery/` while owning its
physics and proof. `ontology/categorical/` demonstrates a different interaction.
Choose the example matching your controls; do not force every ontology into the
reader/assembler protocol.

1. Write `schema.py`: strict, extra-forbidden Pydantic models for public specimen,
   public investigation and private truth. Export `SCHEMAS = {"artifact": Specimen,
   "investigation": Investigation, "truth": Truth}`; add `"stock"` only if needed.
   This module must not import runtime, generator or inference.
2. Write pure laws and typed public evidence. State the complete primitive grammar,
   update order, measurement meaning, control ranges and success criterion. Derive
   latent state from bounded public history or keep it in private truth; never
   put private fields into public specimen payloads.
3. Implement the interface in `ontology/contracts.py`. Runtime hooks perform only
   domain work; the engine owns action costs, transactions, locality, receipts
   and replay. Share a runtime only when these semantics actually match.
4. Supply a public-data-only belief and measurement adapter, a deterministic
   generator, and a qualifier. If using the discovery runtime, also add a small
   `Adapter` in `discovery/domains.py` declaring that runtime's reader/build defaults,
   package and reference-policy bound. This second declaration describes shared
   interaction parameters, not payload registration.
5. Add one `OntologyDefinition` to `REGISTRY` in `ontology/catalog.py`:

```python
OntologyDefinition(
    "model-revision-v1", "model-revision-v1",
    runtime_module="nexus.ontology.revision.runtime",
    schema_module="nexus.ontology.revision.schema",
    generator=("nexus.ontology.revision.generation", "generate_episode"),
    qualifier=("nexus.ontology.discovery.qualification", "qualify"),
    options_schema=("nexus.ontology.revision.schema", "GenerationOptions"),
    standalone_contract=True,
    diagnostic_budget=True,
)
```

This is an excerpt of the working registration, not a call to add it twice.
Use your own unique family and specification identifiers. The registry rejects
duplicate families/versions and unsupported API versions, and exposes immutable
indexes. Paths are trusted application code; episode JSON can only select a
registered identifier. The generic qualifier above checks live solvability and
inference consistency; the revision family's stronger pilot admission is in
`evaluation/revision.py`. Keep that distinction explicit for your own family.

6. Add independent scalar or small-world proofs and a public reference policy.
   Check equivalence, identifiability, legal-query coverage, alternative winning
   builds, failed-finish feedback, easy worlds, rollback and privacy. A graph,
   high parameter count or generator rejection does not establish depth.
7. Add a source-bound preflight and matched evaluation matrix. Record certificate
   lower bounds separately from constructive policy upper bounds. Run the old
   compatibility suites and refresh affected immutable proof bindings through
   their documented proof workflow.

Optional generator settings belong to the adapter's `GenerationOptions` schema,
not another core CLI flag. For example:

```sh
uv run nexus generate /tmp/revision-example --axis-version 2 \
  --science-family model-revision-v1 --seed 5866 --theory-level 3 \
  --discovery-level 5 --planning-level 0 --resource-pressure 1 \
  --ontology-options '{"guidance":"principles"}'
uv run nexus qualify /tmp/revision-example/private.json
uv run nexus solve /tmp/revision-example/private.json --trace-out /tmp/revision-example/run.jsonl
uv run nexus replay /tmp/revision-example/private.json /tmp/revision-example/run.jsonl
```

The same JSON object works as `NEXUS_ONTOLOGY_OPTIONS` for `serve-session`.
Unknown options fail validation; options cannot modify an already compiled private
world. Keep the private file, operator tools and source away from evaluated agents.
Run `examples/ontologies/revision_example.py` for a small executable lifecycle example.

`solver/finite_machine.py` supplies exact canonical Moore-machine minimization
and shortest product-machine counterexamples without a horizon cutoff. It is a
semantic building block, not a depth qualifier. Keep an independent proof oracle
separate from this implementation. Revision compiles immutable tables once per
process, folds equivalent wirings and updates bitset posteriors; a new family need
not use enumeration if another inference representation suits it better.

Automatic discovery of installed third-party packages is not implemented. It
would require explicit trust, distribution/source provenance and qualification
binding before being safe to claim reproducible evaluation. Human developers can
add adapters through the catalog today without editing engine, session or replay.

For architecture selection, shared artifact utilities and the optional private
decision-equivalence hook, see [Preparing future experiments](future-experiments.md).

## Exact continuation diagnostics

A family may implement `remaining_physical_actions(public_spec, state) -> int | None`
for disclosed-law conditions. Return the exact remaining cost including retrieval,
travel and finish, or `None` only when physically unreachable. The common private
report replays accepted actions and identifies the first budget-infeasible state.
It must not infer hidden laws or supply active-player hints. Test costs against an
independent search, including dropped objects, irreversible transitions and the
last finish action. No hook means unavailable, never zero. See the
[research guide](research-guide.md) for interpretation and audit exports.
