# NEXUS selected rerun review — 26 October 2026

All four supplied attempts are legal, evidence-supported wins. Three are action-optimal. The new core 10 attempt fixes the previously observed failure and finishes in the exact 10-action budget; the new slack 34 attempt succeeds with three excess actions. This demonstrates variation on the same small fixtures, rather than a stable failure of core 10 or uniformly optimal coupled planning.

The archive supplies **one additional attempt per condition**, four attempts total. The earlier recommendation was four additional attempts for each condition, 16 total. This is one quarter of the proposed repeat matrix. The user has authorized proceeding with the next planning extension; the remaining repeats are not a release prerequisite. Every supplied condition uses seed 41. These are repeated evaluations of two six-register fixtures under two budgets, with no new seeds.

| Condition | Structure | Original result/actions | Rerun result/actions | Budget | Exact minimum | Rerun excess | Reasoning tokens, original → rerun |
|---|---|---:|---:|---:|---:|---:|---:|
| core 09 | Independent banks | Passed / 12 | Passed / 12 | 12 | 12 | 0 | 279 → 269 |
| core 10 | Coupled banks | Failed / 10 | Passed / 10 | 10 | 10 | 0 | 1,982 → 1,126 |
| slack 33 | Independent banks | Passed / 12 | Passed / 12 | 18 | 12 | 0 | 373 → 278 |
| slack 34 | Coupled banks | Passed / 10 | Passed / 13 | 16 | 10 | 3 | 510 → 755 |

Actions include taking the seal and finishing. Each rerun issued one successful finish, with the original seal carried in the required room and the full target state satisfied. All four finishes have one accepting world out of one remaining world and the `supported_win` classification. There are no failed finishes, no no-change operations, and no rejected action calls in these reruns.

The independent fixture needs 10 operations plus take and finish. The coupled fixture needs eight operations plus take and finish; its cheapest bank-contiguous solution costs 11 total actions. Thus the new core 10 win necessarily demonstrates useful interleaving: its bank blocks are 2, 1, 2, 0, with one bank revisit. The slack 34 rerun has seven bank blocks and four revisits, but those revisits alone do not establish efficiency: its 13-action solution exceeds both the joint optimum of 10 and bank-contiguous minimum of 11.

An independent reverse-graph breadth-first search over all 729 ternary states reproduces each exact minimum. It also locates the slack 34 detour. At accepted turn 4, `bank0_r0` changes the remaining operation distance from six to seven, introducing two excess operations relative to an optimal continuation. At turn 5, `bank1_r1` leaves that distance at seven, introducing one more. Every subsequent operation reduces the distance by one. The three excess actions therefore reflect a real planning detour, not a reporting or finish-accounting discrepancy.

All four action sequences differ from their own original attempt. The independent reruns exchange the two previously observed optimal action sequences: new core 09 matches old slack 33, and new slack 33 matches old core 09. New core 10 matches the old optimal slack 34 sequence after swapping its first two operations; the remaining operations are identical. The new slack 34 sequence is longer and differs from its original beginning at accepted turn 3. Full action and state sequences are preserved in `coordination-rerun-results-2026-10-26.json`.

Reasoning-token counts remain higher for the coupled condition than the independent condition within each new budget pair. They are usage measurements, not a direct measure of planning depth or a causal effect. With only two observed attempts per condition across the original and rerun archives, these counts do not establish stable ratios or reliable condition-level success rates. Among these selected records, core 10 is one supported win in two attempts; each other condition is two in two. Pooling these selected records into a benchmark score would be misleading.

The review verifies the recorded source commit `60536d54e6575470366195dfccb8b0d96572ae4c`, runtime source digest, released input configuration and task files, derived effective configuration, preflight source bindings, image ID/revision, MindTrial binary digest/version, and per-task model configuration. These match the original selected evaluations. All four trace identifiers are distinct from one another and from the original archive's trace identifiers. This establishes distinct recorded attempts, not statistical independence.

All **71 captured public responses** replay exactly against the pinned source after excluding secret-dependent victory-receipt values. The evidence responses match both filename and content. All 47 accepted actions, scalar state transitions, action accounting, support diagnostics, and final result/answer/validator agreement verify. All **11 available private action-hash records** match the replay. The supplied logs contain only a partial action-hash journal; this review does not imply that all 47 actions have private hash records. The original receipt HMACs are not independently recomputed because the original verifier secrets are not used. Original receipts and secrets are excluded from the generated audit output.

The replay ran with Python 3.14.7, Pydantic 2.13.5, and NetworkX 3.7, using only the pinned source. There were no live model calls or network requests in the replay.

The results support treating these fixtures as a short-horizon diagnostic with stochastic outcomes. They do not establish a persistent inability to solve the coupled fixture, reliable optimality under slack, or a need for any particular proposed mechanic. Stronger planning mechanics should be assessed by their certified horizon and unavoidable sequencing constraints, then evaluated on fresh seeds and repeated attempts; these four reruns provide no empirical evidence about such new mechanics.

## Audit artifacts and decision

The accompanying JSON preserves the replay findings and traces without original
receipt values. The full original coordination analysis and replay bundle remain
available in the delivered 26 October analysis artifacts. Reproduction uses source
commit `60536d54e6575470366195dfccb8b0d96572ae4c`, not the newly extended runtime.

Rerun archive SHA-256: `463a66b2b79cec3db5e8032b8b76baad3c0106e75a7128e6f5c3e351f6102a6b`.
Runtime source SHA-256: `86a8d4568b747e17d39e0aaaff42b7f347c72ef347b32232dfb8ddee73f48a83`.

Proceed with the separately named disclosed-interference family. Keep these old
cells as regression controls; make new targets longer by exact qualification and
prove coordinate-goal interference before any live evaluation. See the
[interference guide](../interference-guide.md) for the implementation, matrix and
limits. This decision is an exploratory design choice, not a claim that the reruns
prove the proposed mechanic will defeat a model.
