# Independent implementation judgement: transfer and evidence

18 October 2026. Reviewed the implementation worktree on
`feat/theory-prior-axis`, including the complete transfer adapter, public policy
compiler and artifact loader, factory/catalog/payload registration, episode
validation, terminal metrics, and transfer tests. The review also inspected the
new matrix/preflight surface while it was being added. No implementation source
was edited by this reviewer.

## Decision

The runtime design is coherent: full-prior generation, correlated inference,
behavioral acceptance, immutable probe previews, committed seal application,
and bounded public-policy resources agree with the stated construction. No
blocking runtime correctness or hidden-truth disclosure defect was found.

However, the companion-upstream reader changes the information available under
restricted experiments. **Physical-only passive and single-context obstruction
counts must not be presented as obstruction counts for the combined raw
reader.** Complete passive paired readings identify every joint world. This is
a material limitation of the stronger discovery interpretation, not a failure
of the implemented equations. The implementation owner accepted this
limitation and retained the original reader with narrowed claims: coupled
observation ambiguity, without uniform intervention necessity or a universally
stronger D guarantee. Under that scope, the implementation is acceptable. The
physical-only passive obstruction remains available in the calibrated
controls. This report does not certify the outstanding release/packaging gates.

## Material scientific-scope finding

The implemented reader is `E = r + n2_(1-c)` and exposes survey `F+E` and
reference `E`. Consequently, paired raw observations expose both physical `F`
and companion upstream `n2`, rather than only the physical response used in the
original restricted-closure counts.

An independent computation using only the standalone scalar oracle found:

| Restricted paired raw observations | Result |
| --- | --- |
| Both contexts, all inputs, `a=b=0` | 15,552 distinct signatures for all 15,552 joint worlds; maximum signature group size 1 |
| Context 0 only, full inputs and trims | 1,112 base-program signatures; 200 ambiguous target groups covering 816 of 1,728 base programs |
| Context 1 only, full inputs and trims | The same counts: 1,112 signatures, 200 ambiguous groups, 816 affected base programs |

The passive computation used all 54 legal zero-trim settings and both raw
channels, totaling 108 scalar readings. It includes unknown reader offsets;
this is not a known-nuisance assumption. The all-zero reference identifies the
offset. In particular, the matrix's physical passive rivals 3550 and 3562 each
have a unique full target under complete paired passive raw observations.

This does not establish a cheap passive policy or invalidate the general
two-reading certificate. It does rule out any claim that a combined-reader
fixture requires nonzero trims for eventual evidence-supported identification.
The `passive_physical_rival` field in preflight is accurate as named. Keep that
qualification visible in the proof, matrix interpretation, and walkthrough.
Similarly, both contexts remain part of the physical mission, but observing
both contexts is not universally necessary once a reference observes the
companion upstream mechanism.

The implementation owner requested checks of three proposed repairs. None
retained structural survey ambiguity beyond the scalar `q+r` ambiguity:

| Reader contribution, with the stated offset added | Complete base survey signatures | Ambiguous physical-target groups |
| --- | --- | --- |
| Companion `n2(a,b)-n2(0,0)` | 1,700 | 0 |
| Same-context `n2(a,b)-n2(0,0)` | 1,700 | 0 |
| Same-context `-[n2(a,b)-n2(0,0)]` | 1,700 | 0 |

All three retain 37 complete reference signatures. Their remaining distinct
base-physical-target histogram is `{8:20,16:8,24:4,64:2,192:1,420:1,576:1}`;
including unknown q gives 24–1,728 remaining physical targets. Both same-context
variants preserve single-context target ambiguity for all 1,728 base programs
in either context. Their passive behavior restores the physical-only
obstruction because the reader delta is zero. These are useful negative
results, but none simultaneously meets the intended structural-survey gate.

## Runtime and inference findings

- `PROGRAMS` enumerates all 5,184 physical syntax programs. Selection is direct
  modular indexing, with the reader offset in a separate block; there is no
  solvability or difficulty filter. The calibrated and combined physical laws
  remain paired, and the generous budget leaves scientific fields unchanged.
- Physical and reader equations match the public contract. The reference
  suppresses current physical output while retaining the companion upstream
  contribution. Raw payloads expose only material, settings, reading, and
  applied dose; they do not expose selected program, physical response,
  upstream components, or offsets.
- Acceptance compares all 486 physical conditions independently of the policy
  cache. Equivalent syntax programs are accepted. T0 discloses a canonical
  representative of the physical behavior, and its posterior correctly keeps
  all observationally possible equivalent programs and reader offsets.
- Joint bit masks preserve program/reader correlations and syntax-world
  probability mass. Target masks contain whole behavioral equivalence classes.
  An eligible failed finish excludes the entire accepted behavior class.
  Wrong-room, uncarried-seal, or preview-only finishes do not exclude a valid
  program through `AppliedTreatmentTracker`.
- The canonical engine performs copy-on-step rollback, probe immutability,
  resource consumption, final mission assessment, and victory receipt issuance.
  The adapter does not introduce a family-specific engine branch. Preparation
  clears stale readings. Configuring or previewing the doser does not apply it.
- The public witness consumes only public evidence and live observations.
  Generation reads the offline artifact and does not search a policy. The
  artifact is hash-checked, source-bound to the scalar laws, and immutable at
  both mapping and nested-node levels. Observation tables are frozen and caches
  have explicit finite `lru_cache` capacities.

## Checks executed by this reviewer

`uv run --frozen pytest -q tests/unit/test_transfer.py -m 'not slow'` passed:
15 tests, one deselected. This includes traversal of every reachable policy
node against standalone oracle observations for all calibrated and combined
worlds. The maxima are nine and ten readings respectively. The slow exhaustive
scalar conformance test was running separately under the implementation owner;
its result is not asserted by this report.

A separate live check used program index 3480, whose canonical equivalent
representative is 3471. The noncanonical program won through real
configure/operate/finish actions and replayed to exactly the same canonical
state. Before that win, an eligible wrong finish removed its complete
three-world joint behavior class: the next submission's posterior contained
15,549 rather than 15,552 worlds. Attempts to mutate the reference's outer
mapping, nested policy mapping, and node tuples were rejected.

The fixed action overhead is visible in the actual policy:

| Profile | Guaranteed action upper bound before slack |
| --- | --- |
| T0 execution control | `4 + P`, for P0/P1 |
| Calibrated inference | `5 + P + 3*9 = 32 + P` |
| Combined inference | `6 + P + 3*10 = 36 + P` |

Each reading costs configure, committed preparation, and probe. Taking the
seal/specimens, the P1 move, doser configuration/application, and finish are
included. Standard resources add six actions; diagnostic resources add twelve.
Unlimited specimen reuse and apparatus use support this bound without hidden
stock assumptions. These are upper bounds, not optimality claims.

A fresh process measured cold coupled episode generation at 0.038 seconds and
49.9 MiB peak RSS. First coupled posterior compilation took 8.97 seconds,
reaching 70.9 MiB; a warm posterior constructor took 54 microseconds. These are
observations in this workspace, not service-level guarantees. The cold
inference cost is separate from generation and occurs when public evidence is
analyzed, including terminal diagnostics. These measurements preceded the
owner's subsequent q-independent upstream-row cache, which this reviewer
inspected but did not rebenchmark. That cache is valid because q does not enter
the upstream equations and programs are enumerated in three-q blocks.

## Corrections and release follow-through

1. Record the combined-reader passive and single-context negative ablations
   above. Preserve the exact structural survey and full reference obstructions
   already established; do not broaden their meaning to intervention or
   context necessity.
2. **Resolved and inspected:** `log_terminal_belief` originally emitted
   `reference_carries_upstream_information=true` for both families. This is
   false for the calibrated family, where references are identically zero.
   The telemetry is now conditional on the coupled reader.
3. **Resolved and inspected:** the CLI family and budget help initially omitted the
   transfer families and still limited the generous profile to compositional
   T3/D5/P1/R1. Both relevant commands now describe the implemented support.
4. Preserve the planned installed-wheel/CLI/HTTP smoke, full regression,
   exhaustive arithmetic conformance, and refreshed source-bound preflight
   gates. New matrix assets and documentation were still being added during
   review; their final release state is outside this report's executed checks.

**Resolved and inspected:** the offline compiler now has a 16,384-node and
120-second fail-closed search guard; the table compiler also caps world and
outcome counts. Its recursive splitting is finite because each split strictly
shrinks the posterior and leaf sets are disjoint. These additions address the
reviewer's initial hardening recommendation. They do not change the scientific
equations or turn a timeout into a successful certificate.

No model calls, main merge, or claims of required adaptive rounds, cognitive
depth, guessed model failure, or necessary reference-first ordering are needed
to resolve this review. The revision non-integration decision remains sound
for the stationary construction.
