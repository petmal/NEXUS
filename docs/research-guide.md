# Research with NEXUS

NEXUS makes small interactive experiments reproducible. It checks physical
success exactly, records what the player saw and did, and can compare a decision
with the evidence available at that time. It does not measure intelligence with
one universal number. A useful result identifies a model, its settings, a world
family, the tested condition, and the limits of the evidence.

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
hashes, episode binding, accepted-action replay with the original verifier secret,
lifecycle closure and exchange counts/order. It fails or returns a nonzero exit
for incomplete coverage. It does **not** independently reconstruct every public
response, authenticate the external provider, or certify inference settings.
Checksums detect byte changes; they do not make an editable bundle tamper-proof.
Human-play capture records semantic session calls, not terminal keystrokes or
rendered pixels. HTTP capture covers application responses, not network timing.
Provider logs and configuration belong beside, not inside, the game trace.

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
