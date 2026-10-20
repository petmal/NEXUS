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

## Environment blocker

The session reports its execution environment as unavailable. The attempted
exec_command call returned: "No usable execution environment is available. Wait
for an environment to become available before using this tool."

GitHub read/write access is available. No local Python, test, shell, container,
or filesystem validation was possible in this session. The design checks used
the JavaScript evaluator only; they did not call the NEXUS runtime.

The current repair release binding covers every installed Python source and
requires proof/witness/conformance gates before refresh. Keep these checks intact.
CI can execute committed work, but this checkpoint contains no new game code and
does not claim that CI has validated the new PoCs.

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

## Resume procedure

1. Restore an execution-enabled environment and recheck the latest feature head.
   Preserve concurrent user changes; do not reset or force-push.
2. Read discovery-pocs-plan.md and AGENTS.md, then any newly applicable instructions.
3. Restore the standard frozen Python 3.14 environment:
   uv sync --frozen --all-extras
4. Run baseline fast tests before runtime edits. Record actual command, revision,
   result, and duration.
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
