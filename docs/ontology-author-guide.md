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
remain private. Diagnostics become available only after termination. Inference
adapters receive the public specification and public measurement results; they do
not receive selected private truth.

T remains theory sufficiency, D inferential dependency/experiment construction,
P logistics, and R resource pressure. An ontology must qualify its supported
profiles; assigning a number or drawing a dependency graph does not prove a
particular difficulty. Equivalent mission predictions count as the same target,
and unsuccessful eligible submissions are evidence. There are no mandatory
verbal scientific-method rituals or stage unlocks.

## Extension points

| Component | Responsibility | Existing example |
|---|---|---|
| `ontology/catalog.py` | Explicit version/family selection and lazy factories | Published scientific adapters |
| `ontology/contracts.py` | Runtime ownership and structural interface | `builtin_runtime.py` |
| `ontology/payloads.py` | Trusted role-specific schema registration | Categorical specimen/stock/spec/truth |
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

Shared `Machine` and `ConfigureAction` models retain their existing Pydantic
integer normalization. Initial selector checks enforce arity and range after
that normalization; this refactor does not introduce stricter raw JSON scalar
semantics for controls. Ontology payload schemas separately validate their own
properties (including strict integer permutation laws).
