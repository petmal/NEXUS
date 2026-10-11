# Causal laboratory model pilot

Use the image built from the feature head containing `causal-mechanisms-v1`, with
its OCI revision recorded. The new family is opt-in; previous families and defaults
are preserved. No real-model results are claimed by this implementation.

The first pilot has ten runs per model, without external Python or source access.
The JSON companion supplies exact environment blocks. Keep model/tool token limits
constant and leave enough harness calls for the disclosed reference budget plus
manifest/evidence/observation calls. Do not silently retry provider errors as wins.

| Run | Family | T | D | P | R | Seed | Expected relative challenge / purpose |
|---|---|---:|---:|---:|---:|---:|---|
| 1 | causal | 0 | 0 | 1 | 1 | 7 | Control: supplied answers, configuration and receipt |
| 2 | causal | 1 | 1 | 1 | 1 | 7 | Low: exact laws, infer initial mode from one reading |
| 3 | causal | 2 | 2 | 1 | 1 | 7 | Medium: known forms, combine untreated measurements |
| 4 | causal | 2 | 2 | 1 | 1 | 17 | Medium: second known-form correction case |
| 5 | causal | 3 | 0 | 1 | 1 | 7 | Transfer/inference control: sufficient records supplied |
| 6 | causal | 3 | 5 | 1 | 1 | 7 | Highest new setting: design preparations, infer and transfer |
| 7 | causal | 3 | 5 | 1 | 1 | 17 | Same challenge with another mechanism |
| 8 | causal | 3 | 5 | 1 | 1 | 29 | Same challenge with another mechanism |
| 9 | causal | 3 | 5 | 1 | 0 | 7 | Remove resource pressure; compare with run 6 |
| 10 | resonant | 3 | 5 | 1 | 1 | 7 | Previous-family anchor under the same harness |

Causal = `causal-mechanisms-v1`; resonant = `resonant-network-v1`; axes version 2.
Expected difficulty is a hypothesis, not calibrated ranking. T2/D2 changes the
response form to a publicly disclosed member of {0,1}; other mechanism components
share the seed. It is not an exact matched-truth T comparison. T3/D0 and T3/D5
use the same truth at the same seed, as do R0/R1. Cross-family seed numbers do not
imply equivalent worlds or equal information content.

## Player prompt / tool integration

Use the existing NEXUS transport and action schema. Replace family-specific task
text that assumes `controller`, port-first responses, five/nine settings, materials,
or legal direct mission probes. Those assumptions do not apply to this family.
The manifest carries the exact action contract. A suitable task prompt is:

> Investigate the current artificial world. Begin with manifest and observe, then
> read every listed evidence file. Use only the public action contract and evidence
> to plan experiments and predict the mission outcomes. Use returned specimen IDs.
> Follow the mission's configuration order and arity. Finite hypothesis enumeration
> is valid. Use the NEXUS interface for all in-world observations and actions.
> Finish successfully and return exactly the actual victory receipt, nothing else.

For causal worlds, stage uses three selectors `[x,y,context]`; board uses six
physical responses. There is no controller preview. Probe stage/pulse previews
public preparation only and does not commit it. Sensor and reference readings are
in `result.payload`. All six exact mission sensor protocols are disclosed and
unmeasurable; reference readings remain legal there. This is a public apparatus
restriction, not an undocumented failure trap.

## Analyze science separately from execution

Primary: live victory rate, first-submission correctness, and target classes before
first submission. Also examine informative versus redundant measurements, failed
joint submissions, preparation history/order mistakes, resource exhaustion, invalid
actions, provider failures and final-answer/receipt extraction. Scientific metrics
are terminal-only in `mission-performance-v1`; inspect the existing certificate
field for family/theory/profile bounds. Never expose that private certificate during
play. There is no new active-play hint channel.

Run 6 versus 5 isolates discovery from inference on sufficient evidence; 6 versus 9
helps distinguish reasoning from budget pressure. Run 1 detects integration mistakes.
Run 10 provides a historical anchor, not a mathematically controlled comparison.

Do not declare that the architecture defeats half the models from a single seed.
After this pilot, freeze the architecture and run fresh seeds across the model panel.
Report both per-model and per-episode failure, separating provider/parser failures.
R0 allows eventual whole-vector guessing; first-submission diagnostics prevent that
from being mistaken for evidence-based discovery.
