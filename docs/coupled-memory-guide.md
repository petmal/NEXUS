# Coupled memory pilot

Status: implemented and validated on `feat/theory-prior-axis`, implementation
`17a23bd`. All 886 local tests have passing coverage; implementation CI passed 885
tests and the actual Docker image. Experimental family, not an admitted deep tier.
Keep the old discovery pilot available as a baseline.

## What changes for a player

The facility contains a reference reader, an assembler and the actual mission
carrier. A hidden transfer lattice circulates four packets among three reservoirs.
Two memory cells remember past transfers, influence later transfers and contribute
to the sensor display. The player selects pulse histories, sees each history's
final displayed trit, and installs a seven-selector predictive cartridge. The
cartridge must reproduce the facility for **every** finite future pulse history,
including histories longer than the laboratory's four-pulse limit and the empty
history. Equivalent programs are accepted; private parameter spelling is irrelevant.

Each laboratory query starts an isolated reference at its disclosed initial state.
The memory lives within the queried dynamics; it is not a hidden between-call
mutation of the player's specimen. The live world persists, and installing the
cartridge still requires configure, operate and a successful finish. This pilot
does not yet evaluate experiments that irreversibly alter the state being controlled.

Public evidence gives all formulas, wiring options, old/new update timing, integer
ranges and construction syntax. It explicitly distinguishes packet counts,
transferred amount, memory and displayed signal. Nothing requires real-world physics
knowledge or an undisclosed operator. The old default family is unchanged.
Conservation holds for every legal program by construction. This is not a direct
test of inventing or independently enforcing a conservation law; it constrains
the inference problem and can make that problem easier.

## Proved facts and limits

| Quantity | Result | Interpretation |
|---|---:|---|
| Complete programs / behavioral classes | 384 / 336 | 48 dynamics × 8 encoders; 48 pairs have equivalent complete behavior |
| Independent all-state checks | 51,840 states × 3 inputs | Exact conservation, bounds, recurrence and observation conformance |
| Reachable / predictive states | 40–135 | State complexity, not cognitive difficulty |
| Exact actual-outcome certificate, T3 | 3 readings for every world | A truth-aware choice of experiments; not a public three-reading policy |
| Exact guaranteed adaptive reader depth | 6 worst case | Lower bound `3^5 < 336`; exported tree achieves six |
| Universal fixed panel | Between 6 and 9 readings | Nine-query witness; no proof that adaptation is necessary |
| Dynamics disclosed / encoder disclosed | 2 / 4 worst-case readings | Oracle costs are additive, not a demonstrated joint-inference penalty |
| Binary / five-valued sensor controls | 9 / 4 worst-case readings | More readings can result entirely from bandwidth restrictions |
| Mixed reader/finish evidence-event bound | 6–7 worst case | Counts reader outcomes AND finish outcomes; not a reader-only or total-action optimum |
| Public policy environment actions | At most 16 | Construction included; generous R1 remains 64 |
| T2 blind construction | At most 25 actions | Eight attempts can succeed without reading; a real shortcut |

A single legal query cannot logically eliminate an encoder under the full dynamics
prior, but every query has encoder-dependent output frequencies. Thus absence of a
blank calibration fixture does not mean probabilistic independence. Some equivalent
programs use different encoders: demanding unique calibration would create fake
difficulty from irrelevant nonidentifiability. Multi-query calibration-first policy
optimality is not proved and is not an admission claim.

Removing material→memory feedback changes observable behavior for every program.
Removing memory→transfer feedback has a legal-query witness for 372/384 programs.
The remaining 12 lack a witness within the laboratory horizon; do not infer full
behavioral equivalence or no causal feedback from that absence. Every selected new
matrix truth has witnesses in both directions. The matrix also requires same-display,
different-future histories and distinct dynamics, behavior and encoder structures.

Eligible failed finish removes one entire behavioral class from the posterior.
An unsupported lucky guess can still win. T3 has 336 disjoint accepting classes;
a simple 21-attempt strategy fits 64 actions. Under a uniform program prior, choosing
21 two-program classes wins on 42/384≈10.94%; under uniform classes it is 21/336=6.25%.
These are explicit blind baselines, not success predictions for the selected seeds
or trained models. Mixed experiment/build strategies may be better.

## Ten executions per model

P0 throughout, standard budget 64 for R1; R0 is uncapped within NEXUS. Fresh context,
120 tool calls, 160 harness turns, no external Python. Relative difficulty is a
hypothesis; preflight numbers are properties of the reference policies.

| Run | Family / seed | T/D/R | Reference reads | Exact certificate | Purpose / expected relative difficulty |
|---|---|---|---:|---:|---|
|01|previous representation /305|3/4/1|5|3|Repeat the previous baseline under the same harness|
|02|coupled memory /95|0/0/1|0|0|Execution control; easiest|
|03|coupled memory /95|2/4/1|2|2|Known dynamics, infer encoder; low|
|04|coupled memory /95|3/4/1|6|3|Full joint inference; candidate higher effort|
|05|coupled memory /95|3/4/0|6|3|Same physical truth; action-pressure control|
|06|coupled memory /47|3/4/1|5|3|Indirect feedback and destination recurrence;135 predictive states|
|07|coupled memory /121|3/4/1|5|3|Rate/feedback and encoder contrast|
|08|coupled memory /159|3/4/1|6|3|Different routing with full recurrence|
|09|coupled memory /286|3/4/1|6|3|Display without the cross term; isolates its contribution imperfectly|
|10|coupled memory /7|3/4/1|6|3|Smaller45-state control; more reads need not mean greater reasoning difficulty|

Rows 06–10 vary multiple factors and are structural coverage, not clean one-factor
causal estimates. Only 02–05 are matched disclosure/resource controls. Expect T3 to
require more simulation/state tracking than T2; there is no justified predicted
failure rate and no guarantee it is harder than the previous memory family.

## Build and preflight

From the latest `feat/theory-prior-axis` checkout, Bash:

```sh
docker build --build-arg VCS_REF="$(git rev-parse HEAD)" -t nexus:coupled-memory-v1 .
docker run --rm --entrypoint python nexus:coupled-memory-v1 scripts/preflight_coupled_memory.py
```

PowerShell with Podman:

```powershell
$nexusRevision = (git rev-parse HEAD).Trim()
podman build --build-arg "VCS_REF=$nexusRevision" -t nexus:coupled-memory-v1 .
podman run --rm --entrypoint python nexus:coupled-memory-v1 scripts/preflight_coupled_memory.py
```

Require `preflight passed` from the actual image. The Dockerfile preserves the OCI
revision label and normalizes Windows source line endings before the exact package
release check. A dirty checkout does not describe the labeled commit; build the
published clean revision for evaluations.

Use `examples/mindtrial/nexus-coupled-memory-config.yaml` and its adjacent tasks
file. Provider/model/pricing settings are copied from the previous supplied template,
not independently refreshed recommendations; insert credentials and enable the models
you intend to run. The only image tag is `nexus:coupled-memory-v1`. Prompts and tool
schema stay manifest-driven; they contain no private seed solutions or arity guesses.

For inspectable proof and report artifacts outside the container:

```sh
uv sync --frozen --all-extras
uv run python scripts/preflight_coupled_memory.py --output /tmp/coupled-preflight.json --proof-output /tmp/coupled-proof.json
```

The report binds the matrix, installed Python sources and independently regenerated
proof. Reports fail closed and overwrite stale success on errors. The full proof
exports the decision tree, all certificate witnesses, feedback ablations and sensor
controls. These are operator artifacts; do not expose them to evaluated models.

## Diagnostics and interpretation

Existing supported/compatible/contradicted classifications remain. New terminal
telemetry reports remaining dynamics and encoder counts separately from behavioral
classes. Multiple encoder spellings can remain after a fully supported solution.
`first_supported_reading_ordinal` and `first_support_source` distinguish the number
of observations obtained when support first arose from support gained through a
failed finish. Active player responses contain no posterior or qualification hints.

Track live victory, evidence support, exact installed state, stale configuration,
readings after support, repeated experiments and final receipt separately. The
previous pilot's 69/70 success and one correct-but-uninstalled construction do not
establish scientific-inference failures. A model that wins at this pilot also does
not thereby demonstrate open-ended representation discovery.

## Validation record

- Independent design review supported experimental admission only; all advertised
  lower bounds are separate from physical action upper bounds.
- Thirty generated old-family snapshots match baseline b61c6f2 byte-for-byte after
  removing random episode IDs. Old laws, schemas, seeded truths and evidence retained.
- Shared runtime tests cover all three families, HTTP privacy, invalid-action
  atomicity, actual carrier vs copies, preview vs commit, wrong finish and recovery.
- New mutation tests reject packet loss and using new memory where old memory is
  required; proof independently checks complete behavioral partitions.
- Both old and new ten-row preflights passed. The old committed partial/running
  snapshot is replaced with a complete regenerated report.
- Full local coverage: 833 fast + 50 extended + 3 property = 886. CI: 9 solver + 824
  fast + 50 extended + 2 stress = 885, plus actual-image/OCI/preflight/CLI gates.
  [Implementation CI](https://github.com/petmal/NEXUS/actions/runs/39541221262) passed;
  its tree exactly matches 17a23bd. Isolated wheel results match the checkout.
- See coupled-memory-validation.json and coupled-memory-plan.md for the durable
  completion record. No paid model evaluation was performed.
