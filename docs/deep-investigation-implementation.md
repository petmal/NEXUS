# Deep investigation implementation checkpoint

Approved design: [deep-investigation-design.md](deep-investigation-design.md),
including the 14 October robustness revision. The two falsification scripts will
be incorporated into semantic tests. This file is the resumable execution ledger.

## Anchor and invariants

- Existing feature branch: `feat/theory-prior-axis`; PR #6; no main merge.
- Exact remote base: `4f394126ee6d5943b62f09ab0b1d7ec8f48ec0dc`.
- Source tree: `e4c610f8718ed1c62fbe0792dc7eccf7d9a5d945`.
- The previous inspection checkout had identical files but a different local
  history. It is now anchored to the hash-verified remote commit as a shallow
  boundary, preserving the remote parent; publication must be a leased fast-forward.
- Preserve old mechanics, seeds, private/public separation and historical replay.
- Common facility presentation applies to every current ontology; repair is opt-in.
- Strict deep registration requires an executable public three-round witness,
  two-round success upper bound at most 1/2 at the actual recovery-inclusive budget,
  genuine scientific dependencies, and complete interface conformance.
- Experimental, qualified and calibrated are distinct statuses. Unknown fails closed.
- No paid model calls, public MindTrial changes, force push or unapproved dependency.

## Phases

| Phase | Status | Gate |
|---|---|---|
| 0 Baseline | Running | Existing full suite; exact remote/tree anchor |
| 1 Proof contract | Pending | Tiny oracle, executable rounds, proof payload, shortcut mutations |
| Shared presentation | Pending | Versioned public rendering across families, historical compatibility |
| 2 Stateful construction | Pending | All strict gates in one small exact configuration |
| 3 Runtime integration | Pending | Complete tiny quotient/live conformance, public transcript, receipt/replay |
| 4 Local regime | Pending | Paired revision problem; otherwise explicitly deferred by its gate |
| 5 Hardening/evaluation | Pending | Compatibility, performance, supported matrix, final review |

## Resume

Read this checkpoint and the approved design, inspect git status and current head,
then continue the first unfinished phase. Keep findings and commands here after
each phase. Baseline command:

```sh
uv sync --frozen --all-extras
NEXUS_STRESS_SEED_COUNT=3 uv run pytest -q --maxfail=1 --durations=12
```

Next: finish baseline, implement finite public-policy proof contract, then attempt
the smallest stateful positive construction. Do not advertise a live deep family
from the prior static routing proof; that fixture fails the strict success ceiling.
