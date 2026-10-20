# Discovery PoCs: implementation checkpoint

Date: 2026-10-20.
Approved task: plan and implement both representation discovery and uncertainty-aware construction; provide a test matrix exercising both.
Baseline branch: feat/theory-prior-axis.
Baseline commit: 9c7939c6531e4a0d6d1e275fafa7420fd3798651.

## Actual status

- [x] Re-read current branch metadata and root AGENTS.md through GitHub.
- [x] Inspect trusted ontology registration, assembly schemas/runtime/generation/qualification, CI, package preparation, and repair release binding.
- [x] Recheck primary research supporting the two hypotheses.
- [x] Write the concrete implementation/qualification plan.
- [x] Execute two independent finite design checks in JavaScript through functions.exec.
- [x] Detect and document a short fixed-state-recovery shortcut and a one-observation dependence shortcut.
- [x] Specify a shared ten-row matrix inventory with controls and R0 pairs.
- [ ] Execute independent Python proof models and candidate search.
- [ ] Establish harder admitted candidates and select actual seeds.
- [ ] Implement/register both runtime ontologies.
- [ ] Integrate terminal-only diagnostics and public reference policies.
- [ ] Export runnable MindTrial YAML.
- [ ] Run regression, source-binding, wheel, HTTP/CLI, and image checks.
- [ ] Verify final implementation CI.

This is a planning and finite-design checkpoint, not a completed implementation.
The draft matrix has null seeds, qualified=false, and status=draft-not-runnable.
Do not treat null seeds as requests for random worlds.

## Previous environment blocker (resolved on resumption)

At the initial checkpoint, the session reported its execution environment as unavailable. The attempted
exec_command call returned: "No usable execution environment is available. Wait
for an environment to become available before using this tool."

GitHub read/write access is available. No local Python, test, shell, container,
or filesystem validation was possible during that initial checkpoint. The design checks used
the JavaScript evaluator only; they did not call the NEXUS runtime.

The current repair release binding covers every installed Python source and
requires proof/witness/conformance gates before refresh. Keep these checks intact.
CI can execute committed work, but this checkpoint contains no new game code and
does not claim that CI has validated the new PoCs.

## CI baseline verification (2026-10-20)

Run: https://github.com/petmal/NEXUS/actions/runs/39461075264
Conclusion: success; both test and container jobs passed.
Feature head: d623c8ac55a6fd2cd0c1da9c89477d7b3ce8fa2c.
The pull-request workflow checked out the synthetic merge
2cd5a86c4798a8adb165cef06d2daa7a4fb680a2 into base
cd69107f02af30c10464b85b47fa343a3f96aaef; it was not a separate
direct-head build. The run completed at 2026-10-20T17:08:28Z.

Verified from the job logs:
- Solver proof tests: 9 passed in 2.42 seconds.
- Fast unit/integration tests: 748 passed, 47 deselected, 3 warnings,
  in 188.63 seconds.
- Extended slow unit/integration tests: 47 passed, 757 deselected,
  in 530.95 seconds.
- Cross-seed property stress: 2 passed, 1 deselected, in 133.48 seconds;
  the difficulty stress reported 3 seeds x 24 profiles = 72 worlds.
- Existing immutable references, history/staged/joint-assembly proofs and
  matrix preflights, and CLI smoke checks passed.
- The actual Docker image built successfully. The OCI revision-label check,
  installed-image preflights, and container smoke commands passed.
- Three Pydantic serialization warnings came from contract-tampering and
  generic-AST normalization tests. They were warnings, not failed assertions.

Scope: this establishes a green existing-product baseline after the documentation
checkpoint. Neither new discovery runtime exists in that commit, so the run
does not validate representation-discovery-v1, uncertainty-construction-v1,
their difficulty claims, qualified seeds, or the draft ten-row matrix.
The history preflight explicitly reports that its deep tier is not admitted;
successful CI does not change that qualification.

Local execution was retried after reviewing this run and remains unavailable
with the same execution-environment error. GitHub CI is operational, but this
result does not restore the local Python/shell environment or complete the
pending PoC implementation. No final-implementation checkbox is closed by it.

## Executed design checks and scope

Representation check:
- Enumerate all eight three-bit states.
- Reach all eight from zero using rotate and toggle-first.
- For every unordered pair, compare the current display and the display after
  one/two rotations.
- All 28 pairs are future-distinguishable; twelve pairs share the current display.
- The resulting minimal exact predictive partition has eight classes.
- The fixed three-reading schedule identifies every state. Consequently this
  witness is useful for testing the qualifier but is unsuitable as evidence of
  a hard representation-discovery tier.

Uncertainty check:
- Enumerate both four-element sign-vector supports with triple product -1/+1.
- Check exact count tables for every one-coordinate and two-coordinate marginal.
- Means and pairwise product expectations coincide.
- Enumerate k in {-1,+1} and require k*z0*z1*z2=1 at every support point.
- Each world has exactly one accepted k and there is no common accepted k.
- One synchronized triple sample determines the support parity. This candidate
  therefore also fails hard-case admission.

The JSON file includes complete witnesses and measured counts. These checks
prove finite arithmetic/behavior statements only. They do not establish a
NEXUS action-cost optimum, model failure probability, or qualified seed.

## Paused checkpoint: execution restored, first candidate audited

User requested a pause after the current unit of work on 2026-10-20.
Execution is available again. The local branch was synchronized to remote
5e4c23bb0f25875a46350a60579ddeb8e2a90253 with exact Git object/tree verification;
no user work was overwritten. Direct git transport was unavailable, so the
GitHub connector supplied the two documentation commits.

Completed in this unit:
- Frozen dependency sync succeeded; local interpreter is Python 3.14.8
  (the earlier CI run used 3.14.7).
- Baseline command: `uv run pytest -q -m "not slow and not stress" tests/unit tests/integration --ignore=tests/unit/test_belief_policy.py --maxfail=1 --durations=5`.
  Result: 748 passed, 47 deselected, the same 3 serializer warnings, 172.06 seconds.
- Executed a standalone scalar representation candidate over all 972 composed
  programs. Exact finite-state partition refinement distinguishes all 972
  initial behaviors; each world has 27 reachable, future-distinguishable states.
- Exhaustive words through length five suffice to distinguish all programs.
  A greedy fixed ten-query panel already identifies every world. This is an
  achieved shortcut, not a minimum-query proof or a deep-reasoning guarantee.
- Saved the reproducible standard-library script and its deterministic report:
  `scripts/poc_representation_discovery.py` and
  `docs/discovery-pocs-representation-candidate.json`.
  Run `.venv/bin/python scripts/poc_representation_discovery.py --output /tmp/representation-candidate.json`.

Qualification remains deliberately incomplete. The candidate may still reduce
to fitting coefficients in a disclosed feature basis; 27 predictive states do
not by themselves prove representation discovery or cognitive depth. Its
query fixture starts at zero for each word and returns only the final trit;
actual NEXUS action costs and alternate information channels are not yet modeled.
Do not register it or select matrix seeds on the strength of this report alone.

Next unit, only after the user resumes: assess whether this candidate provides
a meaningful T2/T3 representation contrast or replace it; complete its shortcut
and mission-acceptance audits; implement the independent uncertainty candidate.
Then proceed through the unchanged runtime/qualification/matrix gates.
No runtime ontology, source-bound release, runnable YAML, or qualified seed has
been added. The ten-row inventory remains a draft. Ruff/ty/basedpyright are not
configured repository gates; adding a new toolchain is deferred outside this
proof checkpoint rather than silently changing the project's tooling.

## Resume procedure

1. Confirm execution remains available and recheck the latest feature head.
   Preserve concurrent user changes; do not reset or force-push.
2. Read discovery-pocs-plan.md and AGENTS.md, then any newly applicable instructions.
3. Restore the standard frozen Python 3.14 environment:
   uv sync --frozen --all-extras
4. The baseline fast suite above passed before runtime edits. Re-run it only
   if the baseline changes; preserve its command, revision, result and duration.
5. Implement independent scalar candidate models first. Reproduce both negative
   witnesses above in Python and use them as admission-regression cases.
6. Require successful candidate qualification before registering either family.
7. Follow the phased plan and replace the draft matrix only after actual preflight.
8. Refresh source-bound legacy manifests after their required gates pass; never
   remove source checks to make the container build.
9. Run final regression and actual-image preflight, then deliver the runnable YAML
   and source/image revision.

## Files

- discovery-pocs-plan.md: design, architecture, proof gates, performance, diagnostics,
  matrix design, and implementation phases.
- discovery-pocs-design-checks.json: executed finite checks with explicit limitations.
- discovery-pocs-matrix.draft.json: non-runnable ten-row inventory, five rows per PoC.

No game runtime, existing family, source-bound release manifest, Dockerfile, or
MindTrial configuration has been changed by this checkpoint.
