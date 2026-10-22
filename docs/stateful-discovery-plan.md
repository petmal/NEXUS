# State-changing discovery: design, implementation and resume checkpoint

## Intent and boundaries

Add `stateful-discovery-v1` on `feat/theory-prior-axis`, preserving every previous
ontology. The experimental subject is the original exit seal. Investigating it
changes the same physical state that must eventually satisfy the mission. Normal
counterfactual probes, failed-finish feedback and valid shortcuts remain legal.
No mandatory experiment sequence, theory submission or synthetic phase gate.

Baseline: `6237c9a`. Existing PR6 targets `feat/epistemic-calibration`; no main merge,
public MindTrial changes or paid model calls. Read the operator guide and final
source-bound preflight before conducting model runs.

Research grounding, not a model-failure guarantee:
- Alpcan 2011, https://arxiv.org/abs/1105.2211: simultaneous identification/control.
- Guevarra et al 2025, https://doi.org/10.1039/D5DD00325C: path-dependent experiments.
- Muise et al 2014, https://ojs.aaai.org/index.php/AAAI/article/view/9049: contingent
  planning under partial observability.

## Final system design

Four registers in 0..4 start at zero. Mode i changes only its own register:
`x_i := (x_i + g_i * (1 + x_next^p_i)) %5`, with cyclic next index and independent
`g_i,p_i in {1,2}`. The complete 256-law prior is public. Only x0 is displayed.
Hidden changes must propagate through later interventions to become observable.
The joint target is public. Reaching all 4s collapses the seal irreversibly.

The public specimen stores committed history and its actual display, never hidden
registers. The immutable law kernel reconstructs the canonical hidden state.
`probe` previews exactly one update and its output without committing it. There
are no reset or duplicate specimens. `finish` checks the actual joint goal;
rejection costs one action and supplies the correct negative evidence.

The existing engine retains transactions, charging, replay and receipt issuance.
The trusted registry supplies schema, generation, runtime, inference and qualification.
A domain-local finite planner handles beliefs over (law,current state), rather
than adding domain branches to the core engine. Bounded caches, interned joint
state IDs and physical-distance pruning keep qualification separate from cheap
per-episode compilation. No new runtime dependency.

Supported controls: T3/D5 discovery; T0/D5 known-law planning; T0/D0 supplied
procedure. P0/P1; R1=64 actions and R0=no environment action cap. R0 does not undo
physical collapse. The generator does not filter hidden laws for difficulty;
operator preflight selects and labels the challenge set.

## Rejected designs and critical judgements

1. Four trits with broad nonlinear display: initial probes followed by blind
   installation bypassed most unknown structure. Rejected.
2. Four registers modulo 5 with three-register updates: an 11-action strong policy
   looked promising, but two committed experiments plus free probe panels enabled
   blind completion. Rejected as a deep trajectory candidate.
3. Enlarging the grammar/coarsening the display increased search size but was less
   convincing than changing the causal observation structure. Not integrated.
4. Local observation modulo3 introduced sign/gauge ambiguities and weak selected
   branches. Not integrated. Modulo5 with gains{1,2} passed the supported-policy
   and exact shortcut gates below.

Fresh design and implementation reviews are preserved alongside this plan. The
implementation review caught a real control bug: a bounded common-install search
incorrectly rejected known-law routes longer than 8 operations. Singleton beliefs
now use exact physical BFS descent; the supplied-procedure control bypasses
investigator construction. Nine-operation initial routes and diameter 15 fallback
states were checked. No qualification threshold was lowered to hide the defect.

## Admission contract and what it means

Every matrix hard row must pass:
- Independent scalar agreement for every law/state/mode and all 256-law replay of
  the constructive public policy; all its finishes are evidence-supported.
- Exact optimistic supported-action minimum>=12. A lucky successful finish does
  not become retroactive support. All legal science-bearing actions are included.
- At least 9 committed operations even with every probe and rejected finish free.
- No observation-blind success-aware completion through 22 actions after a free
  complete initial probe panel.
- No handoff after0,1,2 committed operations followed by blind completion through
  20 actions, even granting free full probe panels at every prefix state. All 21
  prefixes are checked. Repeated finishes and synchronizing words are included.
- An adaptive supported branch<=20 with certified safe public continuations for
  every alternative observation, replayed independently for all 256 laws and
  bounded within the same 64-action allowance including handling/travel.
- Distinct gain and nonlinear-power structures, exact live mission wins/replay,
  and matching source/matrix identities. Unknown/capped searches block admission.

This excludes the stated shallow feedback strategies and autonomous coordinate
blocks. It does not prove universal cognitive depth, forbid arbitrary mental
factorizations, or guarantee model failure. Operator selection is not a uniform
population difficulty estimate. Do not expose matrix seeds, selection rules,
source code or proof reports to evaluated players; their disclosed prior remains
all 256 laws. If that access changes, qualify the resulting conditional prior.

## Implementation and validation sequence

1. Mathematical candidate search and fresh design judgement: complete.
2. Plugin, finite planner, inference/terminal diagnostics, exact proofs: complete.
3. Independent implementation judgement and targeted regression: complete;
   singleton control defect fixed and independently rechecked.
4. Ten-row pilot, MindTrial YAML, installed-image preflight, operator guide: complete.
5. Final source freeze, legacy proof/witness refresh after unchanged 15-test gates,
   broad regression, source-bound matrix preflight and actual-image CI: see the
   operator guide's validation record for final outcomes.
6. Publish to the existing feature branch/PR6 only. No paid models or main merge.

## Resume commands

```sh
uv sync --frozen --extra dev --extra server
uv run pytest -q tests/unit/test_stateful_discovery.py
uv run python scripts/preflight_stateful.py --output docs/stateful-preflight.json
uv run pytest -q -m 'not slow and not stress' tests/unit tests/integration --ignore=tests/unit/test_belief_policy.py --maxfail=1
uv run pytest -q tests/unit/test_belief_policy.py
uv run pytest -q -m slow tests/unit tests/integration --maxfail=1
NEXUS_STRESS_SEED_COUNT=3 NEXUS_STRESS_FAIL_FAST=1 uv run pytest -q -m stress tests/property --maxfail=1
```

Each preflight writes atomic running/passed/blocked checkpoints and per-cell
results. Rerun after any source change; a previous report is not proof of a new
image. The current bounded recursive cell restarts after interruption; no Python
stack or untrusted pickle is loaded. Do not refresh the legacy repair source
manifest without its unchanged proof, witness and conformance checks.

## Next-iteration decision gate

The user requested that the follow-up research analysis be retained until the
current real-model pilot is complete. Read
[the recorded conclusions](research-reasoning-followup-2026-10-22.md) when reviewing
those results. The leading candidate is controlled model revision that preserves
earlier valid predictions and global constraints, with matched controls and
explicit shortcut qualification. This is a deferred research hypothesis, not an
instruction to change the running pilot or implement another family now.

The same note now also retains the exact-data identifiability discussion, the
principles-to-response-model example, T/D distinctions and a ranked tentative
backlog. Model revision/global validity is the leading research candidate;
deriving response families from primitive laws is a complementary candidate and
control. Reassess both after the current pilot rather than beginning either now.
