# Second quality review: what the player saw and what the harness recorded

This review checked the boundary between an episode, a player and a research
record. Its main finding is that two fields called “public evidence hash”
could disagree for **the same world**. One identified the family's source text;
the other identified the text the player could actually read.

| Finding | Correction |
|---|---|
| Startup diagnostics and matrix rows hashed compiled attachments. The private audit hashed presented attachments. Some reference runs also read files before presentation. | Current records identify both maps and the presentation version. The affected cross-axis and T/D reference runs use presented evidence. Startup and audit also identify the full player manifest, including the mission, goal and controls. |
| An active legacy session with a finite cap could report a null starting allowance. An uncapped scientific session could log a starting allowance of zero, and scientific controller worlds could be labeled `legacy`. | The startup record and compact summary now obtain the family from the world and the allowance from its initial state. The summary takes its metrics and action history from one snapshot. An unavailable witness count stays null. |
| Python players could accidentally change another session's action example by annotating a dictionary from their own manifest. | Each action contract owns its example data. Regression tests edit one player's example and compare another player's instructions. |
| Repeating a file-client action after a lost reply could spend an extra turn. Only raw HTTP let the caller identify the original turn. | Python and file clients accept an explicit `expected_turn`. A pinned retry reuses the committed response without spending another action. Omitting the turn still means “act now.” |
| JSONL returned an observation and accepted actions, but a player using only that stream had no way to request the mission or its evidence. | JSONL now supports the public request envelopes, including free reads and the checker where enabled. Existing action lines and the first observation retain their formats. EOF preserves an active result. |

**Historical interpretation.** Keep dated results bound to their original source.
For earlier startup logs or matrix rows, a matching `public_evidence_sha256`
alone establishes neither identical wording nor identical mission instructions.
If that distinction matters, reconstruct the player view from the saved world
and matching source. Likewise, use the bound episode to resolve an ambiguous
family or starting cap in an older summary. These defects do not change which
actions won or the validity of an issued receipt. A transport retry is a possible
explanation for an extra action only when a trace or harness log shows it happened.

**Reproduction.** The [boundary tests](https://github.com/petmal/NEXUS/blob/f098fe9603c905774219641e40f6277c0329e86b/tests/unit/test_review_boundaries.py)
compare the files delivered by HTTP with the exported attachment bytes and both
operator bindings. They also check a changed mission with recomputed file
checksums, separate Python sessions, retransmission of a committed action, and
JSONL access and audit coverage. The source qualification, matrices, package
and full-suite commands are in [AGENTS.md](../../AGENTS.md). See the
[protocol reference](../reference/protocol.md) for a pinned retry and
[research guide](../research-guide.md#reproducibility-record) for the hash convention.

**Verification on the candidate.** For each of the 56 cross-axis rows and 32
fresh/anchor rows, we generated the world again with an independent verifier
secret. We requested its manifest, read every listed file through the player
interface and hashed the resulting mapping. All 88 hashes matched the new
reports; on all 88 rows the presented files differed from the compiled files.
After setting aside source identity, timings and evidence-binding fields, both
reports matched their previous versions. The 7,203-case repair gate, both
clean distribution installs and local documentation checks also passed.
An installed file client repeated a pinned action against a live local HTTP
service after discarding the first reply. The resulting private bundle verified
with exactly one committed action. No model calls were involved.

All 1,794 collected unit/integration cases passed across the local checks. The
archived interference comparison was rerun after updating its assertion to
check the old and new hash conventions separately; the archived data was not
edited. All three property tests passed with the default ten-seed sample.
Qualified runtime: `db0f53bf27ee18fac26dbac8034e9b0d6556855b30a9a168cf15c4d9236a146d`.
