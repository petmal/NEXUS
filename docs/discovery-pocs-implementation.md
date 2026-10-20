# Discovery PoCs: implementation complete

Updated 2026-10-20. Active branch: `feat/theory-prior-axis`. Implementation commit:
`fdbc13ec620e00f9f1e92e058d4c72ef6ac420eb` (tree `4bca5cd4785422e6740b692f6f772cbc2bf08081`). Approved scope is two opt-in
plugins and a paired ten-execution pilot with exact, honest shortcut qualification.

## Current implementation

- Both runtime plugins implemented without changing existing laws or defaults.
- Independent all-history memory equivalence and robust-dependence proofs passed.
- Exact permutation factoring replaces 4,838,400 materialized uncertainty worlds.
- Public policies, supported-versus-compatible wins, private terminal diagnostics,
  persistent fixtures, recovery, invalid-action atomicity and replay implemented.
- Ten concrete seeds/profiles qualified; MindTrial YAML exported and parsed.
- 804 fast unit/integration tests passed (49 slow deselected, 3 existing serializer
  warnings, 195.61s); four final finish/T0 regressions also passed. Two exhaustive
  live T2/T3 tests passed across all
  768 memory programs and 120 physical uncertainty mechanisms (1,776 live games).
- The 15 unchanged legacy repair proof/construction/conformance tests passed.
- Independent implementation judgement completed; all three findings addressed.
- Isolated installed wheel passed legacy source binding and the ten-row preflight;
  source/proof/matrix identities agree with checkout. Both families passed CLI
  generate/qualify/solve/replay. Frozen lock, focused Ruff and whitespace checks pass.
- All 49 extended tests passed (576.05s). All three property tests passed
  (149.12s), including the three-seed/24-profile stress sweep. Total local suite: 856 tests.
- CI run [39505676103](https://github.com/petmal/NEXUS/actions/runs/39505676103)
  passed completely: 9 solver, 795 fast, 49 extended and 2 stress tests (855 total),
  all independent proofs and preflights, and CLI smoke tests. The actual Docker
  image, OCI revision label and every installed-image preflight passed, including
  all ten discovery matrix rows. The local total additionally includes one
  determinism property test excluded by CI's stress marker.
- CI tested synthetic merge `fd88ed186d7e415baf0c7f6de6328120bd75fdb5`, whose
  tree exactly matches the implementation tree above. The completion record is
  a documentation-only follow-up; runtime, tests and matrix are unchanged.

## Resume safely

Read `AGENTS.md`, this checkpoint, `discovery-pocs-plan.md`, and `discovery-pocs-guide.md`.
Inspect Git status before edits. Implementation and validation are complete.
The next experimental step is the ten-execution MindTrial pilot described in the
guide, after building and preflighting the selected image. Inspect the actual head
and do not restart the design. No paid model executions were performed.

Primary validation commands:

```sh
uv sync --frozen --all-extras
uv run python scripts/discovery_oracle.py --output docs/discovery-pocs-proof.json
uv run python scripts/preflight_discovery.py --output docs/discovery-pocs-preflight.json
uv run pytest -q -m "not slow and not stress" tests/unit tests/integration --maxfail=1
uv run pytest -q -m slow tests/unit tests/integration --maxfail=1
NEXUS_STRESS_SEED_COUNT=3 NEXUS_STRESS_FAIL_FAST=1 uv run pytest -q -m stress tests/property --maxfail=1
```

Before refreshing `ontology/repair/qualified-release.json`, verify its unchanged proof
and serialized witness digests and the 15 construction/conformance/qualification tests.
Refresh only the complete installed-source map, then run the final gates. Never weaken
or bypass this release check. Later source edits require another validated refresh.

## Decisions and limits

See the guide's matrix for exact minimum supporting measurements. Memory seeds 305/753
have 27 predictive states but respective 3/2-reading certificates. Dependence seeds
123841/123849 have favorable two-reading certificates and a five-reading universal
bound. All science can precede construction. No deep tier or model-failure claim is
admitted. P0/R1 uses 64 actions; R0 has no environment cap. Same harness limits and
identical paired physical worlds isolate disclosure and budget effects.

## Historical checkpoints

- Original design checkpoint `d623c8a`: research/plan and two negative witnesses;
  runtime integration was unavailable then.
- CI 39461075264 passed the earlier product: 9 solver, 748 fast, 47 slow and
  2 stress tests, plus the actual container. It does **not** validate this implementation.
- Paused checkpoint `bd92a63`: local execution restored, 748 baseline tests passed;
  the 972-program coefficient-fitting candidate was rejected as a representation
  challenge and retained as a negative control. The user subsequently authorized resumption.
- The cyclic uncertainty ordering was rejected after a universal three-reading shortcut;
  the integrated grammar allows every fixture permutation and reports its remaining limits.
