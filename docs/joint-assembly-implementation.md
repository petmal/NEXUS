# Joint assembly implementation ledger

Approved scope: implement the joint-inference component-assembly PoC and a
prequalified real-model matrix on `feat/theory-prior-axis`, preserving old families.
Baseline: `139f3bedefa6c5f6af54e101eab0bf68411d6cee`.

## Completed phases

1. **Baseline and design.** Synchronized the checkout byte-for-byte with the latest
   feature head, preserving the earlier local documentation patch separately. Read
   repository instructions and used the Short Circuit proof/review workflow. The
   bounded design and its independent review are committed beside this ledger.
2. **Proof before admission.** Independently enumerated arithmetic, complete mission
   signatures, actual-outcome certificates, channel omissions, finish guesses and
   preparation reachability. A public local gain contract is necessary and explicit;
   phase-equivalent winning builds are accepted. All hard claims have precise scope.
3. **Modular implementation.** Added `joint-assembly-v1` through the existing trusted
   catalog/payload interfaces. Laws, schemas, evidence, inference, physical runtime,
   policy, qualification and independent proof are separate. Generic engine/session/
   replay code has no new family-specific branch. Immutable finite tables and bitsets
   keep ordinary generation free of offline qualification searches.
4. **Qualified matrix and integration.** Ten rows cover all four joint kernels,
   calibrated and known-law controls, the cancellation shortcut, asymmetric channel
   shortcuts, and a matched recovery-budget row. Every row passes exact claim checks,
   supported public play, budget accounting and replay. Science rows also recover
   after an injected rejected build. Matching MindTrial YAML, container contents and
   CI proof/preflight gates are committed.
5. **Review and regression.** Independent implementation review exhaustively checked
   actual engine acceptance and reader payloads. All findings were resolved. The
   final fast suite, cross-seed stress, existing repair proof/conformance and both
   legacy witness preflights pass. The new private solver's physical optimum is
   independently checked for every world at both P0 and P1. See validation status
   below for the longer regression and remote delivery gates.

## Delivery gates and resumption

`joint-assembly-validation.md` records exact results and remaining delivery status.
The extended legacy suite passed all 47 tests; remote CI and container execution
follow publication to the same feature branch. No paid model
evaluations or merge to main are part of this implementation task.

Canonical reproduction:

```bash
uv sync --frozen --all-extras
uv run python scripts/joint_assembly_oracle.py --output /tmp/assembly-proof.json
uv run python scripts/preflight_joint_assembly.py --output /tmp/assembly-preflight.json
uv run pytest -q -m 'not slow and not stress' tests/unit tests/integration
uv run pytest -q -m slow tests/unit tests/integration
NEXUS_STRESS_SEED_COUNT=3 NEXUS_STRESS_FAIL_FAST=1 uv run pytest -q -m stress tests/property
```

Proof/preflight outputs are atomic; incomplete execution replaces stale successes
with running/blocked status. Preflight binds the proof and matrix to installed Python
sources. The old repair release manifest was refreshed only after its unchanged
proof/witness identities and conformance gates passed; its fail-closed check remains.

Core runtime does not read selected matrix seeds, proof JSON or a private reference
plan during play. Operator-side Python is permitted; evaluated models receive only
the NEXUS interface. See the guide for image/build commands and public-facing scope.

## Deliberately deferred

Fatal activation, consumable stock traps, secret state transitions and larger quest
dependency graphs are separate future ablations. This pilot implements persistent
public preparation interactions and joint law/reader inference. It does not claim a
full-budget optimal information policy, unavoidable cognitive depth or model failure.
The qualifier therefore retains `deep_tier_admitted=false` until stronger evidence
justifies a more ambitious tier.
