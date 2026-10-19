# Joint assembly independent implementation judgement

Reviewed working tree `/workspace/scratch/5185b9a844b2/NEXUS`, branch
`feat/theory-prior-axis`, baseline `139f3be`, on 2026-10-19. This was a read-only
implementation judgement under the Short Circuit fresh judgement workflow. The
only written artifact is this report. The implementation owner was concurrently
adding tests, documentation, YAML, and packaging changes; findings below distinguish
the initial observation from the last checked state.

## Verdict

The new mechanics match the intended bounded PoC: law/reader inference is genuinely
joint for the selected T3/D4 sum and difference rows, locally valid phases can be
globally incompatible, preparation changes persistent committed state, and success
uses the complete physical predicate. I found no correctness blocker in the new
assembly law, inference, runtime, or certificate-search code.

Delivery is not yet approved unconditionally: the existing coupled-repair release
binding is stale in the reviewed working tree and the written conformance argument
was still being completed. The mixed image tags found during review were corrected.
The main agent should finish these gates and inspect its final CI/container results.

## Findings and disposition

### 1. Existing coupled-repair generation is currently blocked by stale release binding

Severity: high release regression; acknowledged by implementation owner, pending at
last check.

`nexus.ontology.repair.qualification.release_mismatches()` reports eleven added
Python sources and two modified sources (`ontology/catalog.py`,
`ontology/payloads.py`). The existing qualified generator calls `require_release()`,
so older qualified repair generation cannot run until its existing release process
is completed. This is the intended fail-closed behavior of the old family, but it
means “older families preserved” is not yet true operationally.

Repeat the applicable repair proof, conformance, replay and packaging gates, then
record the reviewed source/proof/witness identity. Do not bypass `require_release`
or simply weaken its source coverage. `scripts/prepare_package.py` only normalizes
CRLF and explicitly does not refresh qualification; it cannot fix this finding.

### 2. Assembly harness initially selected the old runtime image

Severity: high pilot integration issue; fixed during review.

`examples/mindtrial/nexus-assembly-config.yaml` originally used
`nexus:joint-assembly-v1` for the tool but `nexus:staged-repair-v1` for the service
and validator. The service owns generation and would reject the new family if the
old tag pointed to its existing image. Last inspection confirmed all three image
roles use `nexus:joint-assembly-v1`.

The new YAML test only checked that the new tag occurred somewhere, which would
have missed this real bug. Check all three image values, not mere occurrence.

### 3. One runtime-error test initially failed at schema construction

Severity: test defect; fixed during review.

The original invalid-configuration parametrization included assembler settings
`()`, but `ConfigureAction.settings` requires at least one item. Construction
raised before the session could return the asserted invalid-action response.
The empty tuple was absent at last inspection. A separate schema rejection test,
or a nonempty wrong-arity setting, is the appropriate coverage.

### 4. Live-to-finite proof needs an explicit factored argument

Severity: qualification documentation gap, not a discovered runtime exploit.

The design requests a written live-to-finite conformance argument. At inspection,
`proof.py` returned one paragraph stating the reduction, but did not itself run
the transport/engine conformance premises. New runtime and integration tests help;
the guide was still forthcoming. Write the induction and its premises explicitly:

- All 27 reader settings reduce to 15 ternary query classes. `probe` and `operate`
  yield the same trit; the latter only caches already returned information.
- Reader values are independent of component state and specimen identity. Copies
  therefore do not add query classes. Historical cache projection is not new evidence.
- Forge and assembler results/previews depend only on public component fields and
  settings; public precondition errors cannot test hidden validity.
- Configure, movement, stock, observe, status, invalid requests and resource changes
  have public-state transitions. Preview effects never become committed state.
- A complete eligible finish is membership in the accepting mask of its actual
  build; wrong room, absent carrier, or incomplete build gives no law exclusion.
- Successful finishes end play. Terminal diagnostics cannot be reused within the
  one non-resettable player session. Do not imply a timing/process-access guarantee.
- Given identical public histories, these transition facts preserve identical public
  state until a reader result or eligible finish feedback splits the history.

The finite audit grants free construction/setup, so its bounds are conservative
for the live interface once these premises hold. Source hashes identify the checked
code; they do not prove these premises by themselves.

## Executed verification

All commands below ran using the project's `.venv/bin/python` without repository
source mutations.

1. Exhaustively ran `engine.step(..., FinishAction(), ...)` for every one of 432
   worlds and 144 complete builds: **62,208 cases passed**. Victory and
   `mission_accepted` exactly equaled the independent literal-table oracle signature.
2. Compared runtime reader transforms for all 432 worlds, D3 and D4, blank and
   assembled carriers, and all 27 legal settings: **46,656 cases passed**. Values
   equal the independent oracle, component fields are preserved, and input artifacts
   remain unchanged.
3. Executed P0 and P1 sessions with committed reader readings, construction, forge
   previews, wrong-room finishes and dropped-carrier finishes. Law-posterior counts
   remained stable across physical-only actions and ineligible finishes. A winning
   finish did not retrospectively classify the winning guess as supported.
4. Qualified selected seeds 349, 136, 127 and 178 through live public policy and replay.
   Their exact certificates/closure results match the matrix claims.
5. Independently reran `prove_all()`: **passed** with 432 worlds, 144 builds, 96
   mission signatures, and 7,056 construction/recovery cases. Production exact
   certificates agreed with independent exhaustive query-subset enumeration across
   every science prior/profile. The public greedy policy needs at most seven readings.
6. Verified exact small-horizon query/finish success masses:

   | Readings | Finish attempts | Accepted world mass / 432 |
   | --- | --- | --- |
   | 0 | 1 | 9 |
   | 1 | 1 | 9 |
   | 2 | 1 | 27 |
   | 0 | 2 | 18 |
   | 1 | 2 | 18 |

The complete project suite, final Docker build, and paid model runs were not run by
this reviewer. The implementation owner is running the project gates separately.

## Semantic assessment

**Complete acceptance and equivalent builds.** Signature comparison includes both
local gain contracts and all nine output points. Sum/difference worlds accept three
different phase spellings, so identity with the private target is not required.
Product and squared-left worlds have one accepted spelling under the local contracts.
There are no accepted cross-kernel equivalents in this particular grammar once both
gain contracts apply. Wording that allows equivalents is correct, but avoid implying
that actual cross-kernel examples exist.

**Local contracts are nonredundant.** For every kernel family, matching only the
nine joint outputs admits extra builds with wrong local gain(s). Therefore the gain
conditions are part of the scientific objective, not incidental verifier metadata.
Keeping them explicit in the public mission is necessary and is done correctly.

**Joint inference and shortcut accounting.** T3/D4 sum and difference worlds have
five-reading exact certificates and unresolved closure for all three two-channel
panels. Product can use either local channel plus joint, and squared-left can use
B plus joint. Known-sum T2 permits local cancellation. The matrix preserves these
worlds and labels the controls rather than silently filtering them away.

**Physical state versus law belief.** The tracker follows actual carrier operate
events and location; probe/configure cannot substitute for preparation. Reader
evidence narrows a separate finite law/reader posterior. Failed eligible finishes
exclude every world accepting the attempted complete build. Successful finishes
do not supply retrospective evidence for supported-win classification. Recovery's
public policy starts with a fresh prior, which is conservative and still wins
within the selected budget after the injected fault.

**Construction fidelity.** The public cross-slot rotation is applied on every forge
operation, including repairs. Existing assembly kernels persist. The construction
sequence reaches any requested build from any prior component arrangement in two
preparations plus kernel installation. This is a deterministic workshop/assembly
PoC rather than an irreversible-material or hidden-dynamics task, consistent with
the approved scope.

**Modularity and older families.** New behavior lives behind the existing catalog
and payload registration. The generic engine/session/replay code was not modified
for assembly. No older-family seeded behavior change was apparent from the catalog
and payload diffs, apart from the release binding issue above.

## Limits to retain in final claims

- Exact supporting certificates use oracle query selection along an actual world;
  they are not a public optimal policy or a minimum live-action proof.
- The public policy is constructive and bounded, not proved optimal.
- The exact query/guess audit is limited to the five small horizons above. The
  general feedback upper masses are 9, 27, 81, 243, 432, 432, 432 for one through
  seven feedback actions. The bound becomes uninformative at five; it does not rule
  out every efficient full-budget strategy or establish deep cognition.
- Prior-wide probabilities use uniform mass over the full 432-world T3/D4 prior.
  They are not success probabilities for the curated matrix or an LLM.
- The reported hardest selected rows and known shortcuts are mathematically
  qualified within the finite grammar. Model difficulty remains unmeasured.

These limits are already mostly expressed accurately in the implementation. Keep
them in the operator guide and final handoff, especially any use of “all channels
necessary,” which refers to reading-only supported complete builds, not lucky wins.

## Addendum: exact private physical optimum

Reviewed the subsequent `omniscient_construction`, `runtime.physical_plan`,
`proof.physical_costs`, and catalog-derived CLI family-help changes. No new issue
found. The private solver's optimum claim is now justified for the compiled initial
states; it remains separate from the non-optimal public information-gathering policy.

The BFS state contains both committed components, installed kernel, forge control
and assembler control. It starts at the actual compiled defaults and includes every
legal configuration, repeated forge operation, both component orders, and repeated
assembly operation. Unit-cost FIFO traversal and first-dequeue recording give the
minimum construction cost for each complete build. Stopping once all 144 builds
have been recorded is sound. Minimizing across every accepted build correctly handles
equivalent phase assignments.

Excluded actions cannot improve the omniscient physical cost: reader operations,
previews and waits do not change mission-relevant component fields; copies cannot
replace the mission carrier; dropping or extra movement cannot help. Taking the
carrier and finishing are each unavoidable, with one additional unavoidable movement
for P1. Skipping a configuration in the witness is safe because its stored setting
already equals the requested setting.

Executed the BFS and replayed the generic solver's witness through live sessions
for all 432 worlds at both P0 and P1: **864 successful replays**, with cost exactly
equal to the minimum independent-oracle-accepted BFS build cost plus take/finish
and P1 movement. The P0 histogram is **6 actions: 54 worlds; 7: 108; 8: 270**.
Catalog-derived family help reads the static registry without constructing a prior.

The implementation owner separately reported resolving the earlier delivery findings
and completing 15 legacy repair gates plus 1,728 all-world science-profile sessions.
Those later gate results are owner-provided evidence, not reruns by this reviewer.

## Owner disposition after review

All four findings are resolved. The original repair proof and serialized witnesses
remain unchanged; 15 repair construction/conformance/qualification tests and both
P0/P1 public witness replays passed before recording the reviewed source binding.
All three MindTrial image roles are tested explicitly. Invalid nonempty apparatus
settings exercise runtime rollback. The guide now contains the live-to-finite
induction and every public action surface. See `joint-assembly-validation.md` for
the final regression, proof and delivery status; do not read the earlier pending
verdict as the final release disposition.
