# Story and player-language review — 6 November 2026

## Assessment

NEXUS works best as a series of compact science-fiction puzzles in one shared
setting. The premise gives the player a reason to investigate and build something;
the exact mission supplies the challenge. It does not need a campaign, characters
or a second layer of secret objectives to support that role.

Before this pass, the setting was too thin in several places. The exit, portable
mission parts and success check were all called a “seal”; many worlds missed the
shared terminology; and the interface supplied little explanation of the action
allowance or the ending. These were avoidable interpretation problems, rather
than useful reasoning difficulty. One briefing also contradicted its disclosed-law
control. This pass addresses those gaps without changing a world's formal puzzle.

The revised premise is deliberately modest: NEXUS is an automated facility of
unknown origin. A translated console offers exit clearance for a local repair,
calibration or construction mission. Each episode is a separate visit. The
facility's origin remains background, not an unresolved task the player must solve.
The action allowance is a command authorization budget, not an oxygen supply or
wall-clock deadline. A successful `finish` grants clearance and ends the visit.
There is no unimplemented door-opening action after the receipt.

This is a coherence and writing assessment, not evidence from a human usability
study. The setting now supports the mechanics more clearly; whether people find
it engaging still needs observation of new players.

## Findings and changes

| Finding | Why it mattered | Change |
|---|---|---|
| “Seal” had three competing meanings. | A player could mistake a carried part for the exit or expect another interaction after success. | Introduced the exit **interlock**, changed portable “exit seal” phrases to “seal component” in four families, and distinguished the goal check from the receipt. Object IDs stay unchanged. |
| The premise barely explained the player's situation, limits or ending. | It encouraged expectations of time pressure, extra story objectives or an escape sequence that the engine does not implement. | Added a short console/mission premise, an authorization-budget explanation and a clear success ending. Local play prints the ending only after a real victory receipt. |
| The shared orientation covered only `manual.txt` and `manual.md`. | Families using `facility.txt`, and legacy worlds using `facility_manual.txt`, did not receive it. | Applied the same orientation to all four entry-record names and checked every registered family plus legacy. |
| The routing revision briefing always said the composed routing was hidden. | This contradicted the directly disclosed T0 control and could encourage unnecessary investigation. | Replaced it with a fixed brief that refers to the supplied records. T0 and T3 receive exactly the same story text; the formal records state what is known. |
| Terms such as array, lattice, excitation, residual and carrier lacked a shared introduction. | Alien naming could become a vocabulary test instead of the intended reasoning task. | Added short definitions, exact-ID guidance and an explanation that local terms do not imply familiar physics or secret word clues. |
| Nested map labels overwrote copied room-function labels during rendering. | A public room description could disappear when the display renamed a room as a sector. | Preserved the existing public function in the new presentation using a separate nested copy. No rooms or private facts are added. |
| Entry documentation did not tell one consistent, concise story. | Human readers had to reconstruct the premise from implementation-oriented notes. | Aligned the README, play guide and facility-setting page. Kept the README introduction short and put the glossary and reproducibility details in the setting page. |

## Information and mechanics boundaries

The review covered the shared presentation, generated briefings and manuals for
the 21 registered families plus legacy, player CLI, manifest/evidence service,
exported attachments and current entry documentation. The standalone categorical
prototype is included. Family records and controls were checked against the shared
setting; the presentation changes do not replace the mathematical specifications.

The new renderer accepts only the public episode. It does not use private seeds,
selected hidden laws, solutions, qualification results or future states. The
routing replacement depends only on the already public family identity and uses
one fixed paragraph. It does not tell the player which hidden construction was
selected or which experiment to perform. Five fixed phrase substitutions clarify
portable parts in public prose; otherwise the existing manuals remain intact
after the shared orientation. Numeric evidence, formulas, machine controls,
object IDs and acceptance predicates are unchanged.

The nested-map fix restores a role description already present in the public
input; it does not infer a role from the private solution. The narrative ending
is triggered by the existing successful receipt, not by a second victory test.

No new hidden-law disclosure was found in this presentation path. This is a
scoped finding, not a proof that every possible generated wording is free of
information signals. Future writing must continue to avoid labels chosen from
private truth. In particular, dramatic descriptions must not identify a useful
probe, required sequence or unobserved state.

## Reproducibility

New worlds use `sealed-facility-v2`. Saved `sealed-facility-v1` worlds keep their
original wording, including historical imperfections; unversioned worlds keep
canonical presentation. Golden hashes were recorded from v1 **before** making the
edits and now guard its description, evidence and room labels for all 22 families.
The generator still accepts v1 explicitly for controlled comparisons.

The change preserves formal world mechanics, but it changes the text a model
receives and its token count. It may therefore affect performance. Do not pool v1
and v2 results without recording the version, or claim that equivalent mechanics
prove equivalent model behavior. The RC2 live canary used v1 and does not validate
this new wording. Existing T/D and P/R conclusions remain historical findings
under their original inputs; this pass supplies no new model-performance evidence.

Current source-bound qualification and preflight artifacts must be regenerated
because runtime identity includes the presentation code. Keep old reports intact.
After the remaining requested review passes, rebuild the small canary from the
final candidate and run it once with matching controls. There is no need to pay
for a separate live run after every intermediate writing edit.

## Validation

The new regressions check behavior, public-output agreement and historical
compatibility; they are not a measure of literary quality.

- All **51 presentation and CLI cases passed**, including the 22-family golden
  compatibility/public-surface check, portable-part naming in four families,
  disclosed/hidden routing wording and the real-success ending. Six family
  playthroughs produced identical traces, states, status and receipts under
  canonical, v1 and v2 presentation.
- The existing dynamics whole-episode snapshots passed with their historical v1
  presentation explicitly selected. The expected hashes were not replaced.
- The final repair refresh passed **30 tests**, including all **7,203** live
  policy/receipt/replay cases; P0 and P1 then qualified and won in 14 and 15 actions.
- Dynamics and transfer reference compilation/checking passed without changing
  their stored artifacts. Clean wheel and source-distribution installs passed
  demo, generation, qualification and replay checks.
- All **56 cross-axis conditions** and **32 fresh/anchor rows** passed with the
  new source binding. Both reports retain identical substantive content after
  removing source identities and timing fields. The qualified runtime digest is
  `1e064b6fd5d3a7e330e61fa04da529c2e084f05258002f668694157b4c06bb99`.
- The final fast unit/integration suite passed **1,698 cases** in 270.44 seconds;
  52 slow cases were excluded by that gate. This pass adds **31 regression cases**.
  The full slow suite was not repeated for this presentation change; the separate
  exhaustive repair gate above was run on the final runtime.
- Lint, whitespace checks and local file links in all 14 current entry documents
  passed. The guided demo was also read through from its actual console output.

No paid model calls or human play study were performed. Require green CI on the
final candidate before merging, as recorded in [release readiness](../release-readiness.md).

## Remaining scope

No story blocker remains identified in the reviewed surfaces. The formal JSON
records still require technical reading and the CLI still expects structured
actions. A glossary improves access, but does not make every advanced world a
beginner puzzle. Keep the guided demo as the first visit.

A short observation session with unfamiliar human players would be useful: can
they explain the mission, distinguish the portable part from the exit, locate
controls and recognize a completed visit without asking for hidden hints? That
would test the main assumptions in this writing pass. It is separate from the
mechanical release gate. More lore, characters or campaign progression would be
optional product work, not a prerequisite for releasing the research framework.

The language choices are consistent with general usability guidance on
[plain language for expert readers](https://www.nngroup.com/articles/plain-language-experts/)
and [recognition rather than recall](https://www.nngroup.com/articles/recognition-and-recall/).
Those references inform the writing approach; they are not evaluations of NEXUS.
