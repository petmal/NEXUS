# Research with NEXUS

NEXUS makes small interactive experiments reproducible. It checks physical
success exactly, records what the player saw and did, and can compare a decision
with the evidence available at that time. It does not measure intelligence with
one universal number. A useful result identifies a model, its settings, a world
family, the tested condition, and the limits of the evidence.

For a first experiment, start with [the worked comparison](benchmark-guide.md).
For field-level definitions and schema dispatch, use the [metric reference](reference/metrics.md).

## From a world to a claim

1. **Specify the family and profile.** The ontology defines legal laws, public observations and the acceptance rule. Generation selects one instance. Keep the compiled world on the operator side; the player receives the manifest and listed evidence.
2. **Check what was proved.** Run `nexus qualify WORLD/private.json`. Read the family certificate and its assumptions: a replayed winning procedure proves a solution exists; a shortest-path proof additionally establishes a physical optimum. A worst-case guarantee over publicly indistinguishable worlds answers a different question. The [repair conformance proof](repair-live-conformance.md) shows what is needed to lift an offline bound into an executable strategy.
3. **Measure the attempt.** The engine checks the committed state at `finish`. A receipt certifies success for this episode. It does not certify a belief, inference chain or empirical difficulty level. Use terminal evidence diagnostics where supported and preserve the harness verdict separately.
4. **Check what generalizes.** For training, split by world **before** tuning on traces. Record the generator version, laws/behavior classes, selection procedure and which splits were exposed to the model. A fresh numeric seed can encode the same behavior. For a stronger transfer test, reserve law structures or whole families, and label that as a different evaluation distribution.

For a worked extension, run `uv run --frozen python examples/ontologies/revision_example.py`
as a trusted operator. It generates a revision world, executes a public reference
policy and checks replay. The [author guide](ontology-author-guide.md) describes
schema registration, transition semantics, public evidence, independent checks
and how to earn a family-specific difficulty claim. This is a built-in extension
mechanism, not a runtime loader for arbitrary third-party code.

## Define the question before the run

Choose one primary contrast. To study resource pressure, keep laws, target,
layout, information and interface fixed while changing the action allowance.
To study investigation, compare hidden laws with their disclosed-law control.
To study dependencies, compare coupled and independent subgoals with matched
size and resources where possible. Disclose any remaining difference.

Theory (**T**) concerns the supplied theory; discovery (**D**) concerns the
experiments/inferences needed; planning (**P**) concerns action structure and
logistics; resource pressure (**R**) concerns the allowance above a reference
cost. Their numeric settings have family-specific meanings. A minimum number of
observations is an information bound, not a proof of difficult reasoning.

For exact level definitions start with the family and axis version:

| Setting | Where to look before using a numeric level |
|---|---|
| Legacy (v1) | [Legacy difficulty](difficulty.md) gives the D0–D4 probe guarantees, P0–P3 logistics and finite resource rules. For example, the introductory R0 demo starts with 19 actions. |
| Scientific T/D (v2) | [Design and supported semantics](scientific-investigation-design.md#approved-semantic-contract): T0 resolved control, T1 exact laws, T2 a correction of known form, T3 missing structure. D0–D5 describe investigation structure, from supplied evidence to constructed experiments. Not every family implements every level. |
| Planning, breadth and resource contrasts | [Fresh matrix](fresh-world-guide.md) gives exact combinations, options and allowances. P0 can have one room and still require a long plan. Coupling and horizon can be ontology options, not numeric P levels. R0 is uncapped where supported in v2; the tight and relaxed formulas are family-specific. |

Qualification means the declared finite-world checks passed. It is separate
from empirical calibration: a qualified world can still be easy for every model.
Registration in the ontology catalog alone implies neither property.

## Record separate outcomes

| Dimension | Question |
|---|---|
| Harness result | What did the external evaluator return, including its raw error? |
| World result | Did an accepted `finish` produce a valid victory receipt? |
| Physical goal | Was the mission state actually reached, even without a successful finish? |
| Evidence support | Did the available public evidence support the chosen decision, or was it only compatible with it? |
| First submission | Was the first eligible attempt supported/correct, before feedback from rejection? |
| Resource trajectory | When, if ever, did a valid continuation become impossible within the remaining budget? |
| Availability | Did billing, rate limits, transport, or provider failure interrupt the attempt? |

Do not count an API outage as a reasoning failure. Conversely, an outage does not
erase a demonstrable earlier planning error. Report both facts. An unplayed row
is unassessed. Preserve every attempt; rerun selection must not silently replace
unfavorable outcomes. Show explicit denominators and the rules for exclusions.

Evidence diagnostics are family-specific. Missing support analysis means
unavailable, not unsupported. A physically correct guess can win without being
justified by the observed evidence. That is a different result from a supported
win. Terminal information is unavailable to the player during an active attempt.
Private operator reports can inspect active attempts and must remain private.

Measurement counters describe information gain, not planning efficiency.
`redundant_measurements` counts observations that do not narrow the candidate
worlds; a necessary state-changing operation can contribute to that counter when
the laws are already disclosed. Use exact physical costs and `excess_actions`
where available to assess wasted actions. Read bounds from the family's scoped
certificate: plugin worlds can leave shared legacy generation fields such as
`optimal_action_count` at zero even when their certified plan cost is positive.
That default is not a zero-action optimum. In `nexus solve` output,
`plan_action_count` is the cost of the returned private plan. Only use
`optimal_action_count` as a baseline when it is non-null: a replayed winning
plan proves it is possible to win at that cost, not that every win costs as much.

## Reproducibility record

Save the compiled episode and accepted-action trace. A seed alone is insufficient:
source, dependencies, family options and public presentation also matter, while
fresh identity/verifier secrets may differ. New legacy episode IDs are opaque;
saved historical episodes retain their original IDs. Pin the exact source commit,
locked Python environment, image ID/digest, harness version, model provider/ID,
reasoning setting, temperature, output mode, token/tool/action caps, retries,
timeout, date, and all task/config hashes. Record provider routing if known.

Use [CITATION.cff](../CITATION.cff) when citing the software. Also identify the
exact commit and experiment artifacts in the paper or supplementary material;
a project citation alone does not identify a reproducible experiment. No release
date or DOI is declared in this citation; use the tested revision explicitly.

The optional `--audit-dir` export produces an operator-only directory:

| File | Contents |
|---|---|
| `binding.json` | Runtime source digest, Python and protocol versions, world/evidence identity, generation metadata |
| `private.json` | Compiled world **including the verifier secret** |
| `exchanges.jsonl` | Captured public request/response exchanges, including rejected requests and retries |
| `trace.jsonl` | Accepted actions with before/after hashes, events and receipts |
| `outcome.json` | Actual final state hash, replay state hash, performance, evidence and physical-cost diagnostics |
| `manifest.json` | File hashes, coverage counts, and whether export closed normally |

The directory is created exclusively, with owner-only permissions on POSIX.
Public capture is bounded to 10,000 exchanges and 16 MiB retained data; HTTP body
capture is additionally capped at 2 MiB per request/response. Exceeding a limit
marks coverage incomplete. Journals are appended during play. A crash can leave
an open manifest or partial tail; retain it as partial evidence. This is not a
power-loss durability guarantee or a resumable session file.

`nexus verify-audit DIR --json` requires matching runtime source. It checks file
hashes, bound episode ID, protocol/presentation versions, generation metadata,
public evidence and initial state against the compiled world. It replays committed
actions with the original verifier secret and checks lifecycle closure, exchange
counts and order. It also recomputes game-derived
performance, evidence witnesses and physical continuation costs from that trace.
`game_metrics_verified` reports this check. Invalid-action, duplicate-request and
protocol-conflict counts need the public transcript, so they are explicitly listed
in `unverified_outcome_fields`, along with assistance and provider/receipt-validation
metadata. Their presence in a bundle does not certify them.
Metric reconstruction uses the recorded compiled world and its declared reference
bounds. It does not rerun the whole world-qualification search:
`world_qualification_rechecked` remains false. Use
`nexus qualify DIR/private.json` to recheck episode admission and the family's
documented proof/preflight command for stronger population-level guarantees.

The command fails or returns a nonzero exit
for incomplete coverage. It does **not** independently reconstruct every public
response, authenticate the external provider, or certify inference settings.
Checksums detect byte changes; they do not make an editable bundle tamper-proof.
Human-play capture records semantic session calls, not terminal keystrokes or
rendered pixels. HTTP capture covers application responses, not network timing.
Provider logs and configuration belong beside, not inside, the game trace.

Audit storage belongs to the calling framework or operator. NEXUS writes portable
files and verifies them without depending on MindTrial or another harness. For a
containerized service, mount a persistent operator-only parent directory and set
`--audit-dir` (or `NEXUS_AUDIT_DIR`) to a new child directory for each attempt;
NEXUS creates that child itself. The harness records which attempt owns the bundle
and its episode ID, allows graceful service shutdown, then collects and verifies
the files. Preserve interrupted exports as partial evidence. Keep this storage
outside the player's filesystem and tool access. Bounded container logs are not
a substitute for an audit bundle.

Do not publish private bundles or secrets for held-out test worlds. If you later
release a world and its solution for replication, retire it from uncontaminated
evaluation. Scrub provider credentials and unrelated data from external logs.

## Exact physical continuation costs

For disclosed `stateful-planning-v1` and `stateful-interference-v1` worlds,
operator reports use an exact search for the cheapest remaining physical plan.
Costs include picking up the seal, travel, operations and `finish`. They account
for dropped objects and irreversible states. They ignore later evaluator closure
and do not estimate cognition or the experiments needed to learn hidden laws.
Other families, and hidden-law conditions, report this diagnostic as unavailable.

If `spent + minimum_remaining > initial_budget`, success is already impossible
under that budget. `first_budget_infeasible_turn` records the first such accepted
action; `first_unreachable_turn` records a state with no physical solution at any
budget. These are private diagnostics, never an active-player hint service.

## Compare models responsibly

Use passing controls to establish basic tool competence. Then run matched
conditions, multiple fresh seeds and repeated attempts per model/settings pair.
Set the sample size and stopping rule before looking at outcomes. Separate
exploratory screens from confirmatory tests. Purpose-selected challenging seeds
are useful diagnostics but do not estimate performance over random worlds.

Report per-family results, support and physical success, costs, failures and
availability. For uncertainty across repeated trials, account for attempts that
share the same world; treating all attempts as independent can overstate
precision. Model rankings from a small, selected panel are provisional and apply
to the tested settings. Do not infer a universal ordering or equate a model's
product tier with its reasoning performance.

Use public families and development seeds for iteration, reserve held-out seeds
and configurations for confirmation, and document seed-selection rules. Public
source allows players to exploit regularities; varying seeds alone does not prove
absence of memorization. The [latest analysis](research/fresh-world-results-2026-11-04.md)
explains what the present sample supports. [Next experiments](future-experiments.md)
prioritize breadth, dependencies, and resource curves while retaining T/D controls.
