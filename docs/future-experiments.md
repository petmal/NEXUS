# Preparing experiments beyond a single T/D task

Read the [T/D synthesis](td-experiments-and-next-directions.md) for the evidence
behind the architecture choices. This guide is for authors and operators. It does
not add new axis levels or claim that a multi-module production family exists.

The first implemented follow-up is the separate
[planning/resource pilot](planning-resource-guide.md): fully disclosed spatial
layouts over the stateful laws, exact known-law costs and public unknown-law policy
bounds. Its live evaluations and subsequent interference/cross-axis work are summarized
in the [1 November smaller-model report](research/smaller-model-synthesis-2026-11-01.md).
That report updates the immediate sequence: distinguish response limits and
provider behavior, then confirm contrasts on fresh worlds before adding broader
composition. The qualification principles below remain in force.

## Choose a base by the question

| Question | Start here | Matched control |
|---|---|---|
| Can the player preserve and revise evidence across several constructions? | `model-revision-v1`; `ontology/revision`, `evaluation/td_cycle.py` | Supplied construction; separate investigations with identical local access |
| Can it coordinate interventions and a repair valid across contexts? | `compositional-repair-v1`; `ontology/compositional`, `evaluation/structural.py` | Passive evidence where sufficient; supplied mechanism; generous resources |
| Can it investigate while preserving shared state and earlier achievements? | `stateful-discovery-v1`; `ontology/stateful`, `evaluation/stateful.py` | Known-law execution on the same state and goal; explicit reset-access control |
| Is the question specifically about compatible physical components? | `joint-assembly-v1`; `ontology/assembly`, `evaluation/assembly.py` | Independent valid components versus the joint compatibility requirement |

Coupled memory, coupled dynamics and shared response remain useful simpler
controls. Historical families, matrices and traces stay available. Their presence
does not mean every family needs another broad model sweep.

For a first composition, use the assisted two-module specification described in
[the bounded-cycle results](td-cycle-results.md). Its implementation in
`evaluation/td_prototypes.py` is an offline qualification experiment. Before adding
it to the ontology catalog, define the playable interface, update order, resets,
repair actions and costs, then verify live replay. Downstream-only observation
and the tested selective-control design failed their stated validity requirements.

## Keep the extension boundaries small

Follow the [ontology author guide](ontology-author-guide.md). Reuse a runtime only
when actions, locality and state semantics match. The engine continues to own
transactions, costs, terminal status, receipts and replay. New family options go
in its validated options schema, not a collection of core CLI switches.

Two shared utilities are now independent of the original repair/dynamics pilot:

```python
from nexus.evaluation.artifacts import StrictModel, atomic_json
from nexus.provenance import source_digest
```

`source_digest()` hashes the same relative `.py` and `.json` byte inventory as
before. Moving source necessarily changes its value. It binds artifacts to source;
it does not prove correctness or identify the whole container environment.
`evaluation.matrix` retains compatibility reexports for existing operator code,
but new code should use the imports above. `atomic_json` is a single-writer report
replacement helper; use distinct output paths for concurrent jobs.

Keep each matrix's actual admission rules beside that experiment. The old
`evaluation.matrix.Matrix` describes a particular ten-cell pilot, not a universal
schema to extend with every future axis. A second genuinely shared use case can
justify another extraction; an imagined future need does not.

## Decision equivalence in private diagnostics

The latest audit found four different-wiring submissions that repeated a rejected
behavior. `evidence-witnesses-v2` therefore adds:

- `decision_equivalence_available`: whether the family supplies the capability;
- `previous_rejected_equivalent_turn`: the first earlier eligible, rejected finish
  with an equivalent decision, or null if none is known;
- the existing `repeated_build`, still measuring literal repeated submissions.

The optional runtime hook is
`decision_equivalence_key(public_spec, decision) -> Hashable`. A returned key must
be non-null, determined only by public semantics, and stable for the entire
episode's eligible finish decisions. Equal keys must mean the same complete
mission behavior or acceptance set. Shared observations, the same current display,
or merely overlapping sets of valid repairs are insufficient. In particular,
overlap is not an equivalence relation.

Only revision currently implements this hook, using exact all-history behavior
classes. Families whose acceptance changes with physical state should omit it
until they have an appropriate explicit contract. No hidden selected truth is
needed. Ineligible finishes are not rejections, and a successful finish does not
exclude its decision. The rejection history is evaluated before each submission;
later observations cannot rewrite earlier classifications.

`operator-summary-v2` reports `rejected_equivalent_submissions`. It is **null** when
unavailable, including when summarizing an older v1 witness report, and an integer
otherwise. Literal and equivalent counts can overlap; do not add them. A separate
reading-contradiction witness can take precedence while this repeat field still
records the earlier rejection. These are private operator schema revisions;
the player response schema and victory rule are unchanged. Consumers must retain
version-aware handling of archived v1 records rather than relabel them v2.

## Qualification and evaluation gates

Before a live pilot, make the following concrete and reviewable:

1. A public task contract, including experiment reset rules, feedback from failed
   finishes, recovery actions, budgets and any assistance.
2. A joint world model that preserves correlations. Do not multiply component
   possibilities unless their independence is part of the declared model.
3. A reachable goal and a successful policy using only public information. For
   restrictions such as short-query ambiguity, separately check the complete
   legal observation set, bypasses and alternative winning decisions.
4. A live reference trace, exact replay, and an independent small-world or scalar
   check of the new mechanics. Keep lower bounds, certificate sizes and policy
   upper bounds separately named.
5. A source-bound matrix with known-law, independent-task and combined-task
   controls, comparable budgets, held-out mechanisms and explicit run identifiers.
6. A ledger joining each attempt to model/effort, source/image, options, public
   evidence hash, trace, receipt, first/final support and provider stop. Unknown
   immutable model versions or SDK retry counts remain null.

The committed [latest ledger](research/td-latest-run-ledger.json) is an example of
completed records, not a template to launch again unchanged. The existing T/D
exporter already verifies its source-bound preflight. Re-run preflight after any
source change; do not substitute a new hash into an old result. The repair release
binding covers the whole Python tree and must be refreshed only after its actual
proof/conformance checks. The dynamics cache uses a narrower source list; refresh
it when one of those inputs changes. Preserve dated historical reports.

Start with generous resources. Increase module count and dependency depth
separately; compare equal-size independent and interacting tasks. Only then add
resource pressure or logistics. Failure of a combined task can be accumulation
of ordinary component errors, so record component outcomes before attributing it
to coordination. Run a small interleaved pilot before a larger evaluation.

The preparation in this change adds no paid model run, no speculative composition
engine and no altered game rules. It leaves the next architectural experiment
explicitly testable while preserving historical behavior.
