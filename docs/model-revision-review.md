# Model-revision implementation review

Reviewed 2026-10-22 against the uncommitted implementation after `bf86ce8c`. This was an independent read-only review under the applied Short Circuit workflow. Only this review artifact was written by the reviewer; implementation changes described as fixes were made by the main agent during review.

## Outcome

No unresolved blocking defect was found in the inspected packet-network mechanics, complete-behavior equivalence, reading-only certificate search, paired-world admission, or catalog/options refactor. Three concrete diagnostic/qualification issues were identified and communicated; the current source incorporates their fixes or explicit scope corrections. The main remaining delivery gate is the final source-bound preflight/compatibility run after the ongoing implementation and documentation edits settle.

This review does not establish empirical LLM difficulty or a deep tier. The implementation correctly retains `deep_tier_admitted=false` and distinguishes selected challenge worlds from the full grammar.

## Findings identified and current disposition

### 1. P2 — Compact summaries fabricated zero action counts for legacy episodes

**Location:** `src/nexus/protocol/operator_summary.py:compact_summary`.

The first implementation read `performance["action_counts"]`, defaulting to an empty mapping. Legacy `PerformanceSummary` stores `wait_actions`, `take_actions`, etc. rather than that mapping, so the summary reported every action count as zero despite a nonzero turn count.

Executed reproduction:

```python
session = Session(generate_episode(17))
session.act(0, WaitAction())
session.finalize_attempt()
snapshot = session.operator_snapshot()
summary = compact_summary(snapshot, session.trace_snapshot())
```

Observed before the fix: `turn=1`, detailed legacy `wait_actions=1`, compact `action_counts.wait=0`.

**Disposition:** Fixed during review. The summary now counts canonical committed trace actions, preserving separate invalid/duplicate request counters. The added legacy regression and the focused diagnostic tests pass.

### 2. P2 — The reading minimum needed an explicit exclusion of finish feedback

**Locations:** `src/nexus/ontology/revision/qualification.py:audit`; `src/nexus/evaluation/revision.py:preflight`.

The initial field `minimum_supported_readings=4` was a reading-only certificate minimum, not a live minimum when rejected eligible finishes may supply evidence. I executed supported wins with only three readings under the standard 64-action budget. These do not invalidate the exact supported action minimum; they invalidate an interpretation that four reader calls are necessary in live play.

Each witness below performs: take `carrier`; configure/probe `reader` for each word; configure/operate `assembler` and finish for each listed rejected build; then configure/operate/finish the final build.

| Seed | Three reader words | Displays | Rejected build(s) | Final supported build | Actions |
| --- | --- | --- | --- | --- | --- |
| 5431 | `[0,1,1,1,1,0,1]`, `[0,0,1,0]`, `[1,1,0,0,1]` | `1,0,0` | `[3,1,4,7]` | `[3,1,8,7]` | 13 |
| 1101 | `[1,0]`, `[0,0,1,1]`, `[1,1,0,0]` | `2,1,0` | `[0,7,4,9]` | `[0,7,7,9]` | 13 |
| 5866 | `[1,1,0,0,0,0]`, `[0,1,1,0]`, `[0,1,0]` | `1,2,1` | `[3,4,7,11]`, `[3,4,10,8]` | `[3,4,8,10]` | 16 |
| 6464 | `[1,1,0,0]`, `[1,0,0,0,0]`, `[1,1,0,1]` | `2,1,0` | `[3,7,10,8]`, `[3,8,7,11]` | `[3,8,10,8]` | 16 |

All four completed with `escape_classification="supported_win"`, exactly three measurements, and one/two failed finishes as shown. The witness choices are optimistic actual-outcome traces, not a guaranteed public policy or a population success claim.

**Disposition:** Corrected during review. The current field is `minimum_reading_only_certificate`, and the design now states that finish feedback can substitute for readings while leaving the supported action optimum unchanged. I inspected the added `mixed_feedback_witness`: each hard matrix cell now records a concrete certificate-prefix/rejected-build supported-win witness, checked through real Session actions and exact replay. Hard admission runs before the optional mixed witness, so a shallow substitute blocks without exhausting its budget. Keep these surviving shortcuts visible in the final delivery.

### 3. P2 — Shared terminal logging mislabeled behavioral classes as mechanism programs

**Location:** `src/nexus/ontology/discovery/runtime.py:log_terminal_trace`.

Revision inference deliberately quotients 20,736 legal programs into 748 exact behavior classes. Its `Belief.counts()[0]` therefore counts behavior classes. The original shared log field `remaining_mechanism_programs` gave that number the wrong unit.

**Disposition:** Fixed during review. The label now derives from the per-family `prior_count_key`; old families retain `remaining_mechanism_programs`, while revision emits `remaining_behavior_classes`. The inference compression itself is sound for an all-history behavioral-equivalence mission.

## Independent qualification checks

### Exact reading-only certificate minimum

I independently enumerated all distinct actual-outcome survivor masks and checked all zero-, one-, two- and three-observation combinations, without using the production certificate search's dominance pruning, recursion, pivoting or gain bounds. I then intersected the returned four-query witness and verified that it leaves exactly the true behavioral class.

| Seed | Archive-compatible classes | Distinct actual-outcome masks | Triples checked | Certificate below four | Four-query witness |
| --- | ---: | ---: | ---: | --- | --- |
| 5866 | 69 | 155 | 608,685 | None | Isolates truth |
| 6464 | 69 | 155 | 608,685 | None | Isolates truth |
| 5431 | 58 | 153 | 585,276 | None | Isolates truth |
| 1101 | 192 | 355 | 7,393,585 | None | Isolates truth |

This independently supports a minimum reading-only certificate of four for the selected hard worlds. It does not imply four adaptive rounds, four required live readings, or cognitive depth.

### Supported action minimum with failed finishes

I checked the exchange argument underlying the 12-action selected-world result. It is sound under the current action contract:

1. Suppose a supported winning trace uses `r` distinct informative reader queries and rejects `g` distinct eligible behavioral classes.
2. Each rejected class can be replaced by one legal reader query distinguishing that class from the actual truth, because the complete legal observation rows are pairwise distinct. The resulting `r+g` true reader outcomes isolate the truth, so the reading-only certificate minimum `C` satisfies `C <= r+g`.
3. Each informative query costs configure plus read. The initial reader setting `(0,)` is already supplied by the trusted archive, so it cannot provide a free informative first query. Repeated unchanged readings provide no additional evidence.
4. Each distinct eligible rejected build costs at least installation plus finish. Repeated rejection of an unchanged build provides no further evidence. Ineligible finishes supply no elimination.
5. The successful trace also needs take, final installation and final finish; a nondefault target behavior requires an assembler configuration. Therefore its cost is at least `3 + 2*C`, or `4 + 2*C` when the default assembler behavior is not the truth.
6. `certificate_witness` reaches that bound using real public operations and pre-outcome evidence support. For the four selected hard worlds, this is 12 actions.

This proves the optimistic actual-outcome supported action minimum. It is separate from the reference policy's worst-case bound and from the possibility of an unsupported early guess winning. The current qualification module/design now include this argument; a broad mixed-game solver is unnecessary for this claim.

## Architecture and correctness assessment

- **Primitive execution and equivalence:** `revision/laws.py` uses bounded integer inventories and ordered transfers matching the public primitive specification. `FiniteMachine.signature()` computes reachable minimal Moore-machine behavior without a laboratory cutoff. The independent `revision/proof.py` checks every program/state/mode against separately written scalar mechanics and independently product-checks every program against its representative. Distinct independently verified finite rows separate representatives. Together, these establish no false merge or false split of the complete behavior relation for the current grammar.
- **Complete legal observation coverage:** all binary words of lengths 1 through 8 are included; the empty-word output is fixed by the common initial inventory and is included in machine equivalence. Reader resets, final-only output and the cartridge encoding are explicit and fit the existing strict integer action envelope.
- **Public prior:** archive conditioning is exact. Provisional guidance is generated solely from the archive-equivalent alternatives and never filters the posterior. Paired principles/provisional episodes share truth, initial physical state, resource budget and prior mask. Load validation recomputes the disclosure and rejects altered compiled options.
- **Equivalent builds and finish feedback:** acceptance uses exact behavior classes, and `Belief.accepting_count`/`exclude_target` map any grammar-valid equivalent program to its class, not just a canonical representative. Physically eligible rejected builds eliminate the correct class; success is not fed back to fabricate prior evidence support.
- **Matrix admission:** the pilot validates ordered roles, axes, family/guidance and paired seeds; preflight checks real policy wins/replay, resource matching, legal provisional counterexamples, residual repair uncertainty, all-unary-history ambiguity and distinct behavior/topology contrasts. The greedy fixed panel is correctly an upper bound. Broad synchronization/mental non-decomposition and empirical failure rates remain explicitly unproved.
- **Catalog/options:** duplicate family/specification keys fail before indexing; lazy payload schema resolution avoids runtime/prior imports; legacy identifiers, the `scientific-v2` mapping, unsupported general-generation PoC and default generator selection remain intact. New options pass through a family-owned data schema. No arbitrary import path is selected from episode/player input.
- **Diagnostics:** the separate bounded final summary preserves the detailed event format and avoids another posterior reconstruction. Public active responses remain free of operator metrics; shutdown snapshots remain read-only; receipts and provider completion remain unobserved by the service. The tested 8192-byte message suffix retains the complete final summary. The test assembles captured formatted log records rather than an external harness's stderr wrapper, so final delivery should not overstate what was exercised.

## Executed validation

- `uv run --frozen pytest -q tests/unit/test_model_revision.py tests/unit/test_ontology_registry.py tests/unit/test_operator_summary.py tests/integration/test_operator_diagnostics.py tests/unit/test_ontology_contracts.py`: **37 passed** before the review fixes.
- After the fixes, focused operator summary, revision HTTP and matrix-role/export checks: **9 passed, 3 deselected**. The deselected tests were the complete/negative preflight reruns, which the main agent owns for the final source snapshot.
- Independent zero/one/two/three-reading enumeration for all four selected challenge seeds, plus validation of each four-reading witness.
- Real Session execution of the four three-reading mixed-feedback supported wins above.
- Direct reproduction of the legacy compact-summary count defect, followed by the added passing regression.
- Inspected `/tmp/revision-first-preflight.json` with `status="passed"`; this is not a claim that its source digest covers subsequent edits.

No full legacy suite, container build or final immutable source-binding refresh was run by this reviewer. Those remain the main agent's final gates; this review should not substitute for them. At review completion, there are no remaining actionable correctness or qualification findings from this review. The three findings above have been addressed in inspected source, and the original selected-world claims now have explicit read-only versus mixed-feedback scope.
