# History-coupled PoC: implementation, findings and pilot

Implemented as opt-in `history-coupled-v1` on `feat/theory-prior-axis`.
Existing families remain available. **This is a working experimental family, not
an admitted unavoidable-deep-reasoning tier.** Proof work found useful new
mechanisms and important shortcuts; no real-model failure rate is established.

## What changed

The player constructs an actual seal through state-changing operations. Two hidden
physical registers and two visible registers interact. Later operations disturb
earlier hidden properties. Identical visible readings can hide states with
different future behavior. Two physical intervention readers provide complementary
information. All laws and observations remain exact, finite and fully documented.

A normal, charged anneal operation restores a specimen to zero while preserving
world laws and investigation evidence. There is no new-game endpoint. All valid
winning procedures count; neither a particular order nor measurements are forced.

The implementation separates schemas, laws, inference, policy, evidence,
qualification, generation and runtime. It uses the existing trusted ontology
registry, transactional engine, replay and receipt boundary. Budget-profile
support is now a registry capability, removing duplicated family lists. The old
repair tracker reuses the existing shared applied-treatment tracker.

Terminal inference includes **every visible pulse result**, counterfactual pulse
preview, reader observation and eligible failed finish. It retains supported wins,
compatible wins and failures. Separate terminal logs distinguish readers,
committed construction, pulse previews, anneals and known suffix/recovery options.
Post-resolution construction is not automatically classified as waste.

## What the proofs establish

| Check | Result | Interpretation |
|---|---|---|
| Reachability | All 81 normalized states in all 256 composed laws | All 1,024 complete worlds have a solution |
| Shortest physical preparation | 2–6 pulses | Physical path length is not inference depth |
| Exact legal decisions | All 87,381 histories of length 0–8 | Equivalent winning procedures and overlapping win sets handled exactly |
| History dependence | Same visible pair, different later response | Remembering preparation can matter |
| Orientation rivals | Passive observations agree; winning sets disjoint | Both intervention channels are needed for a guaranteed first submission from measurement evidence alone |
| Joint inconsistency | Reachable 14-world posterior; unique marginal modes form an impossible world | Independent parameter estimates can produce an observation-inconsistent theory |
| Public reference | At most five readers; actual maximum 34 P1 actions | Checked 35-action allowance is an upper bound, not an optimum |
| Fixed panel | Nine queries identify all 1,024 worlds | Mandatory adaptive research depth is not proved |
| Goal-test shortcut | Known normalized law: ≤8 pulses and ≤4 finishes cover every orientation | Failed-finish feedback can replace interventions |
| Omitted apparatus | Vek or nol individually omittable in every world; tor/sen alone solve 608 | Four apparatuses do not imply four necessary stages |
| Best blind single procedure | 96/1,024 = 9.375% under full uniform prior | This is not a model failure probability or a matrix-specific rate |

The first proposed equations were rejected because 256 worlds were impossible.
The revised equations pass reachability. The stronger depth-admission gate remains
**failed** because of the documented shortcuts. We preserve this result in the
certificate instead of silently weakening the gate or banning valid strategies.

The finite mechanisms are compositions of bounded quadratic primitives, with
unknown strengths, bias placement and coordinate orientations. This is an
operational/joint-state PoC, not open-ended theory invention. T0/D0 supplies the
same world's law and a procedure; experimental T3/D5 hides them. Other T/D values
are deliberately rejected until their semantics are separately qualified.

## Performance

The compiler factors 256 normalized laws from four coordinate orientations.
Transition tables contain 82,944 bytes. Exact posterior and winning-history sets
use immutable integer bitsets, with bounded query caches. It does not materialize
world/transcript object products or search minimax per seed. No new runtime
dependency, CPU worker pool or GPU is needed at this size.

Initial local preflight: cold full-prior compilation/generation ≈3.6 s; subsequent
generation ≈1 ms; full public reference play including terminal diagnostics
≈0.04–0.10 s. These are local timings, not deployment guarantees. Fresh-process
checks cover win, exhaustion and explicit finalization.

## Ten-execution matrix

All rows use P1/R1, fresh service and model context, no external Python, extended
terminal diagnostics. Standard unknown-law allowance is 43 actions; generous is49.
T0 keeps the same43-action allowance, separating disclosure from resource pressure.
Seeds and operator labels are absent from player prompts.

| Row | Family / seed | Condition | Shortest physical pulses | Expected relative challenge |
|---|---|---|---:|---|
| 01 | Existing coupled evidence /6943 | Regression | n/a | Previously solved by Astra; baseline |
| 02 | History /440 | Exact-law/procedure control | 6 | Low; execution and state tracking |
| 03 | History /440 | Unknown law | 6 | More operational depth than other chosen worlds; empirical difficulty unknown |
| 04 | History /440 | Same world,+6 actions | 6 | Same science; resource-sensitivity control |
| 05 | History /239 | Passive-indistinguishable orientation rival of440 | 5 | Different final procedure under similar passive evidence |
| 06 | History /216 | Joint-consistency witness world | 4 | Correlated explanations; the model may choose a different trajectory |
| 07 | History /216 | Exact-law/procedure control | 4 | Low |
| 08 | History /216 | Same world,+6 actions | 4 | Same science; resource-sensitivity control |
| 09 | History /483 | Different gate composition | 4 | Coverage; difficulty uncalibrated |
| 10 | History /557 | Further gate composition | 4 | Coverage; difficulty uncalibrated |

The live reference used34 actions on01 and 9,23,23,27,21,7,21,22,23 respectively on
02–10. These are achieved witnesses, not optimal player costs. Four distinct
normalized mechanisms are represented; selecting only the two six-pulse worlds
would have produced poor coverage.

**Recommendation:** start with03,06,09 if minimizing evaluation spend. If Astra
solves them cleanly, do not assume longer runs or tighter budgets will expose the
intended weakness. The next scientific gate is stronger operational coupling and
qualification against the actual goal-test channel, preserving fair recovery.
Selective phase-change revision remains deferred until that gate passes.

## MindTrial and local build

The ready-to-run YAML pair is in `examples/mindtrial/`:
`nexus-history-config.yaml` and `nexus-history-tasks.yaml`. Keep them together.
Existing provider settings are retained; Astra medium is enabled, other runs are
disabled, API keys blank. All three image references use `nexus:history-poc-v1`.
The player prompt and tool description follow the current manifest and explicitly
allow families without a controller/configure action. The validator still requires
the actual live victory receipt. No MindTrial stable behavior is changed.

From this branch's repository root, after pulling the tested commit:

```sh
podman build --build-arg VCS_REF=$(git rev-parse HEAD) -t nexus:history-poc-v1 .
podman run --rm --entrypoint python nexus:history-poc-v1 scripts/preflight_history.py --output /tmp/history-preflight.json
```

Replace `podman` with `docker` for Docker. Do not ignore a failing image preflight.
The Docker build preserves the OCI revision label and canonicalizes Windows line
endings before checking the qualified source binding.

## Validation / resumption

See `history-coupled-design.md`, `history-coupled-implementation.md`, independent
`history-coupled-proof.json`, and both design/implementation review reports.
The proof and preflight scripts are deterministic, standard repository jobs.
Matrix preflight records exact source identity and fails closed on stale output,
false rival claims or any live/replay mismatch. CI runs proof, matrix and actual
container preflight. Final release results are appended below after completion.

Local fast gates: **677 passed**, plus **9 solver proof tests**. The15 repair
construction/conformance/proof prerequisites also passed. Dynamics policy nodes
were independently rebuilt and remained identical; its source identity and the
unchanged repair proof/witness source binding were refreshed. Extended and image
results are pending at this implementation checkpoint.
