# Dependent discovery: resonant-network-v1

## Why and what changed

The preceding real-model audit found43 successful coupled-world tasks and one
output-limit Error in the available later-run prefix. Every scientific submission
was correct on its first attempt;12 wins used all12 bench coordinates. The user
approved selective experiments and dependent discovery, keeping P/R moderate.

The new opt-in family adds a resonance law H. A model uses measurements to learn
which setting z makes its response meter useful at a chosen specimen coordinate.
At resonance the meter returns G(x,y), the existing composed response network;
otherwise it returns `signal:false` with no reading. The exact goal is now H+G
at four unmeasurable field coordinates. This makes the first discovery relevant
to both the next experiments and the final prediction.

Both priors and all controls are public. No stage unlock forces a particular
method. Calibrator-free search, interleaved inference, enumeration and direct
fitting remain legal. Scientific success is prediction, not recovery of a
preferred symbolic program or verbal explanation.

Enable `NEXUS_AXIS_VERSION=2` and `NEXUS_SCIENCE_FAMILY=resonant-network-v1`.
Live support: D4/D5 at T3, D0/T0,T3 controls, P0–3/R0–2. Other cells reject.
Existing families and defaults remain. D4 supplies prepared stocks; D5 supplies
the origin and public noncommuting shift/shear operations. T3 leaves both bounded
relationships unknown. This patch does not silently expand the live T1/T2 grid.

## Proofs and claim boundaries

H is chosen independently from alpha*x+beta*y, alpha*x²+beta*y, alpha*x+beta*y²
modulo7, with alpha,beta independently in1..3. G retains the27 composed structures
and2,187 complete worlds. Every27×2,187=59,049 joint world is admitted; no
truth-dependent solvability filtering is used. There are2,401 joint field targets.

The bench expands from12 to all45 GF7 coordinates outside the four field targets.
There are315 possible coordinate/tuning meter experiments. Both instruments
reject field coordinates, including specimens prepared there from legal stocks.

| Proven property | Value / scope |
|---|---|
| Identify H | Exactly2 readings; 27 functions cannot fit into one7-valued outcome |
| Public policy for G | At most5 readings using the existing12-point subset |
| Joint scientific measurement bounds | At least4 and at most7 in the worst case, before controller feedback; no exact joint minimum claimed |
| D4/P1 policy / R1 budget | 34 /42 actions |
| D5/P1 policy / R1 budget | 51 /59 actions |
| Complete45-coordinate response sweep | At least92 actions, even with perfect tuning and no navigation cost |

The92 lower bound counts one acquisition/preparation and one response measurement
per distinct coordinate, plus controller configure and finish. Thus a complete
sweep cannot fit either moderate profile, while the certified policy can.
R1 still means uniform reference bound+8, R2 means bound+0, and R0 is unlimited.

The four-measurement lower bound follows from2,401 mission targets and at most8
outcomes per scientific measurement: 8³<2,401. The upper bound composes2 H
measurements with the5-reading G witness. It is not a full joint minimax result.
`required_probe_count` reports this lower bound; terminal certificates explicitly
separate it from the realizable measurement/action upper bounds. Omniscient CLI
`solve` still only proves physical goal reachability; it is not the scientific
reference policy and must not be interpreted as a three-action reasoning solution.

The prefix returns to R0 before the downstream stage; D5 takes a fresh origin
specimen. Each stage's action count depends on its own observed transcript;
inferred H changes downstream tuning numbers but not route/action counts. Summing
factor maxima therefore covers the whole admitted product. Qualification replays
all2,187 G witnesses with one H, all27 H witnesses with one G, and the actual
episode, then relies on that explicit composition invariant. It does not claim
to have physically replayed all59,049 joint worlds.

The scientific posterior stays factored: calibration restricts H; no-signal
restricts H by inequality; a signal restricts H by equality and G by the reading.
A rejected H+G submission introduces correlation, so its complete target vector
is retained as an exclusion over the factor product. An explicit59,049-world
oracle verifies rejection followed by calibration, misses and hits. The terminal
summary counts the correct joint posterior, not independent marginals alone.

## Review findings and limitations

Independent design and implementation reviews found no remaining critical bug
or player leak. The following are intentional limits, not hidden disadvantages:

- Calibration has a particularly efficient two-point solution. It may be a small
  detour for top models. The generator uses that improved witness for budgets.
- The expanded domain admits a seven-point fixed G witness, full axes-plus-diagonal
  identification, and polynomial fitting in the union basis. Old restricted-domain
  shortcut exclusions do not carry over. The PoC checks the fixed witness.
- Full axes alone still leave202 G transcripts ambiguous, with up to34 distinct
  target vectors. D5 therefore still needs some mixed preparation for a guaranteed
  scientific solution; repeating only one preparation kind per specimen is insufficient.
- Exhaustive sweeps are excluded, but good fixed subsets remain viable. Adaptivity
  is useful in the reference subset; it is not proved mandatory across the whole game.
- H+G can be predicted without identifying both exact programs. This is valid
  scientific behavior. Increased model failure rate remains an empirical question.
- The new family changes both the measurement domain and mission. Its comparison
  against the old family is not an isolated causal ablation of dependency alone.

The generator deliberately avoids a59,049-world joint minimax search. It reuses
the small G policy, caches the27-world calibration problem and per-profile composed
physical bounds, and constructs cached factor tables only when needed. This
keeps random per-task seeds practical without precompiled episodes or GPU work.

## Validation and reproduction

The committed [proof](resonant-network-proof.json) and
[fresh-process benchmark](resonant-network-benchmark.json) contain quantitative
results. Ten reference-policy cases won. The final measured cold generation
range was1.318–1.863 seconds; warm range0.249–0.389 seconds on Python3.14.8,
excluding imports and standalone qualification. These are local timings, not a
controlled host-normalized speed comparison with earlier user runs.

Semantic coverage includes independent arithmetic on every H/G world at all49
coordinates, exact joint-posterior comparison,24 D/P/R profiles, both controls,
deterministic replay, no-signal versus zero, forbidden field measurements,
configuration atomicity, probe immutability, wrong-finish recovery, tamper
rejection, HTTP privacy/terminal metrics and CLI environment selection.

Full regression: **413 passed**, four warnings,354.77 seconds, including the
three-seed stress pass. After the final metadata/type refinements and added
wrong-submission integration regression, the final focused suite passed
**42 tests**, no warnings,70.52 seconds, including both full factor-witness cases.
The full-run warnings came from deliberately malformed test objects; the new
tamper test now explicitly asserts its expected warning. Focused Ruff and Pyright
checks passed; lockfile and whitespace checks passed. CLI generation, omniscient
solve and trace replay passed. CI contains additional resonant CLI/container
smoke cases; remote CI status must be checked at the published head.

Operator timing stages: `resonance.base_witness`, `resonance.factor_prior`,
`resonance.composed_witness`, `resonance.public_evidence`, and
`resonance.factor_witness_replay`. Terminal-only logs report calibration/no-signal
counts, measurements after target identification, and target ambiguity at first
submission. No posterior, witness or solution timing hint is added during play.

```bash
uv sync --frozen --all-extras
uv run python scripts/resonant_network_poc.py --out /tmp/resonance-proof.json
uv run pytest -q tests/unit/test_resonant_network.py
NEXUS_STRESS_SEED_COUNT=3 uv run pytest -q --durations=12
uv run python scripts/scientific_investigation_benchmark.py \
  --family resonant-network-v1 --out /tmp/resonance-benchmark.json
uv run nexus generate /tmp/resonance --axis-version 2 \
  --science-family resonant-network-v1 --seed 17 --discovery-level 5 \
  --theory-level 3 --planning-level 1 --resource-pressure 1
uv run nexus qualify /tmp/resonance/private.json
uv run nexus solve /tmp/resonance/private.json --trace-out /tmp/resonance/trace.jsonl
uv run nexus replay /tmp/resonance/private.json /tmp/resonance/trace.jsonl
```

The [ten-run model pilot](resonant-network-model-matrix.md) is the next empirical
gate. Keep no external Python and record family, image revision, reasoning/output
limits and harness call limit. No paid model calls were made during implementation.
The [execution checkpoint](dependent-investigation-plan.md) records final gate
status and publication details for resumption.
