# Coupled repair integration: results and scope

The feature branch adds opt-in `coupled-repair-v1` through the existing trusted
ontology registry. It uses the ordinary engine, action vocabulary, session,
receipt and replay contracts. Existing family selection defaults remain unchanged.
A shared versioned Sealed Facility presentation applies across current ontologies.
Historical serialized episodes without the presentation field remain unchanged.

## What the player does

The player is confined in a sealed enclosure with survey stock, a unique seal
specimen, and five apparatuses. They obtain and prepare survey specimens, calibrate
masked responses, distinguish a missing bounded relationship, and transfer that
knowledge to a joint physical treatment of the seal. Apparatus configuration does
not itself treat a specimen. Escape requires carrying the correctly treated seal
into the array and successfully calling finish. Every control is public and usable
from the start; no scientific milestone unlocks an action.

The small T3 prior contains `c+z`, `c+z*z`, and `c+(z*z)*z`; these functions require
different mission treatments. Shared calibration parameters make experiment
selection depend on earlier measurements. Known cross-effects in the repair
system require applying an inverse relationship, rather than simply copying the
readings. This is a compact, controlled reasoning task, not open-ended science.

## Qualified profiles

| Profile | Rooms | Actual actions | Public witness | Recovery allowance | Any <=2-round policy |
|---|---:|---:|---:|---:|---:|
| T3/D5/P0/R1 | 1 | 17 | 14 actions, 3 feedback rounds | 3 | success <=3/7 |
| T3/D5/P1/R1 | 2 | 18 | 15 actions, 3 feedback rounds | 3 | success <=3/7 |

Other repair T/D/P/R cells are rejected. Existing ontologies provide the control
profiles in the [evaluation matrix](repair-model-matrix.md). Cross-family controls
are useful diagnostic anchors, not matched scientific worlds.

The bound assumes one non-resettable attempt, serial application requests, no
private-process/source access, and uniform truth indices conditional on every
operator-fixed public configuration. Choose P/presentation before sampling the
truth, and sample the index uniformly from 0..7202. Fixed seeds are reproducible
fixtures, not themselves a probability distribution. A fresh independent public
nonce avoids encoding the private seed; saved compiled episodes are the replay
unit. Timing/network side channels are outside the claim.

**One extra action permits a guaranteed shallow solution.** The release has no
hidden resource margin and no support for arbitrary budget overrides. The stated
recovery allowance covers one complete rejected repair after acquiring and
transporting materials; it does not cover arbitrary wasted experiments. A lucky
shallow win is valid. A model using three or more rounds may always win.

## Evidence

- Independently checked finite query payload: all 576 first-batch choices, exact
  relaxed upper bound 1029/2401=3/7; full hidden-degree query audit 19/49.
- Complete-state factored conformance proof covers all action classes, public
  responses, errors, retries, cached readings, previews, speculative guesses,
  eligibility and terminal outputs. It is not a full inventory/history-product
  state enumeration. See [construction](repair-construction-proof.md) and
  [live reduction](repair-live-conformance.md).
- All 7,203 truths passed the serialized public investigator in the real Session
  engine, emitted victory receipts and replayed exactly. Recovery wins at the
  final permitted action. Finite component tests cover all legal repair vectors
  and preparation classes, including noncommitting previews and ineligible finishes.
- Independent final review found no remaining live-proof blocker under this scope.
  Its adversarial public-conditioning example confirms why the uniform prior must
  hold separately within every public configuration, not just marginally.
- Full qualification recomputes the query upper proof and executes the public
  witness. Normal generation checks a bound source/proof/witness release identity.
  Compiled episodes bind that release too; changed/missing qualification fails closed.
  Hashes prove identity only, and must never replace requalification after changes.

## Final validation — 14 October 2026

All **572 collected tests have passing coverage** across the completed groups:
100 presentation/network tests, 421 other non-stress tests, 49 final theory tests,
and two cross-seed stress tests with three seeds (72 legacy profile/seed worlds,
plus resource pairing). This was partitioned validation, not one uninterrupted
green full-suite invocation. Three existing warnings remain.

The first full attempts exposed presentation compatibility mismatches. Both old
network qualifiers now reproduce the selected presentation before comparison.
Historical theory fixtures explicitly request the absent presentation and still
match their original hashes; no fixture hash was replaced. A legacy manifest test
checks the approved shared description while retaining the exact mission text.
Affected groups were rerun. The earlier passing stress paths do not call the two
changed network qualifiers, so their expensive result was retained.

CLI generate/qualify/solve/replay, HTTP play, save/load and human help pass. The
wheel contains all 109 source modules with exactly the release-bound hashes and
the required proof assets. Focused Ruff, new-module Pyright and whitespace checks
pass. Validated source commit: `53bedc7d83737af2ecf272fc80a7628e402d6e73`.
See [machine-readable validation](repair-validation.json). GitHub CI status is
reported separately on the PR; local validation does not imply CI completion.

## Performance and diagnostics

[six fresh-process samples](repair-performance.json) measured cold generation
0.110–0.163 seconds and subsequent generation 0.00064–0.00124 seconds, excluding
imports. Peak process RSS was about 61 MiB. The host was not controlled for other
load, so these are operational timings, not a precise speedup claim. All 24 timed
missions won through the public investigator. All 10 [matrix reference missions](repair-reference-matrix-results.json)
won as well.

Reusable proof search is offline. The final independent proof/check job used
16.15 seconds and 79.2 MiB under a 512 MiB cap. Generation decodes the selected truth
in constant space, reuses the checked family certificate, and avoids reconstructing
the full prior. Immutable bounded caches hold policy/query tables; sessions own
only their mutable belief masks. No CPU/GPU runtime framework was needed for
roughly 1 ms warm generation.

Terminal-only logs distinguish calibration readings, insensitive measurements,
measurements after decision resolution, and first-attempt uncertainty. Mission
tracking follows the applied key state, including location and drop/retake history,
so an ineligible finish does not falsely eliminate a correct treatment. Accepted
replay traces remain unchanged; bounded complete public transcripts additionally
record rejected/free requests and transport failures, with explicit incompleteness.
No active-play posterior or solution hint was added.

## Local regime: checked and withheld

The bounded local-offset PoC examined 50,421 paired old/new cases; 43,218 invalidate
the old repair. One new context-sensitive reading repairs the changed component
while preserving unaffected knowledge. However, a player can trigger the change
before any investigation and solve one stationary world. Its required-revision
gate therefore fails. The approved plan permits withholding this variant, and it
is not registered or included in the model matrix. No artificial ordering lock was
introduced to hide the shortcut.

Reproduce with `uv run --no-sync python scripts/poc_local_regime.py`; see
[recorded result](repair-local-regime-poc.json). Future revision work needs a
separately proved transfer objective that accounts for anticipatory policies.

## Reproduction and deployment

```sh
uv sync --frozen --all-extras
uv run --no-sync python scripts/qualify_repair_offline.py --output /tmp/repair-proof.json --max-seconds 60 --memory-mib 512
uv run --no-sync pytest -q tests/unit/test_repair_construction.py tests/unit/test_repair_conformance.py tests/unit/test_repair_runtime.py tests/unit/test_repair_qualification.py tests/integration/test_repair_service.py
uv run --no-sync python scripts/run_repair_matrix_reference.py --output /tmp/repair-matrix.json
uv run --no-sync python scripts/profile_repair.py --output /tmp/repair-profile.json
```

Run the service with axes-v2, family `coupled-repair-v1`, T3/D5/P0-or-P1/R1 and
an explicit privately sampled seed. Use `serve-session`; the general reset-capable
multi-session server rejects this profile. The [matrix](repair-model-matrix.md)
contains family-neutral task text. Keep external Python disabled for the first
pilot. Record the actual OCI revision label, supplied by the existing Dockerfile.
No MindTrial behavior, paid model calls or default family were changed.

The offline wrapper checkpoints completed jobs atomically and fails closed on
time/state/memory limits. An incomplete search cell restarts; it does not resume
a serialized recursive stack. Source packages are immutable during a running
process; restart and requalify after changes. Wheel inspection verifies the exact
bound Python sources and both required JSON proof assets are packaged.
