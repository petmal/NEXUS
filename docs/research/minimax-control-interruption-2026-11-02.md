# MiniMax Stage A: rate limits and an empty response

The attached `http-err-v1.zip` contains four completed error records from the
two intended control repetitions on 2 November 2026, 11:13–11:14 Toronto time.
These are integration outcomes; Stage A has not passed admission to challenges.

| Repetition | Row | Recorded outcome | World interaction |
|---|---|---|---|
| 1 | S05 | HTTP 429 Too Many Requests | No tool call logged before the request error |
| 1 | S21 | HTTP 429 Too Many Requests | No tool call logged before the request error |
| 2 | S05 | No actionable content; stop reason `stop` | Manifest and observe succeeded; turn 0, all 64 actions available |
| 2 | S21 | HTTP 429 Too Many Requests | No tool call logged before the request error |

The fourth outcome is not a response-length stop: its recorded usage is 217
output tokens, including 42 reasoning tokens. No world action was recorded in
any attempt. The same local MindTrial binary, text-output setting, 10 RPM limit,
65,536 completion ceiling, zero retries and disabled fallback routing were used.
The first request can receive 429, so a locally excessive sequence of tool turns
is not required to explain the problem.

OpenRouter documents 429 as rate limiting and 402 as insufficient credits.
A 429 can originate at OpenRouter or its upstream provider. The saved logs
omit the error body, upstream identity, rate-limit headers and `Retry-After`, so
they do not distinguish request limits, token limits or provider capacity.
The `OpenAI API error` wording is the compatible client error, not evidence that
the task was sent to an OpenAI model. References, checked 2 November 2026:
[errors](https://github.com/OpenRouterTeam/docs/blob/main/api_reference/errors-and-debugging.mdx) and
[limits](https://openrouter.ai/docs/api_reference/limits).

## Immediate action

Pause MiniMax challenges and automatic repetitions. After a cooldown, with other
concurrent MiniMax requests paused, make **one S05 attempt at 2 RPM**. This is a
conservative rate diagnostic, not a proven fix. Keep all other settings fixed.
If it receives another 429, stop and inspect OpenRouter activity/error metadata
before trying again. Honor `Retry-After` if available. If it instead returns
empty content, that is the separate response reliability problem already seen.
Do not increase world budgets or token limits to treat this 429.

The updated package includes `probe-minimax-rate.sh`. It backs up the MiniMax
config, changes only the run label and RPM, and invokes S05 once. It leaves the
modified config in place; exact input and effective settings are captured in
the result folder. This new rate cohort must be distinguished from the original
10-RPM attempts. A successful probe permits completing controls at the selected
rate; it is not itself admission of the model to the challenge rows.

GLM's Stage C is independent and can proceed while MiniMax is held.

## NEXUS refinements

The launcher now stops **after the current MindTrial group** if its result file
contains HTTP 429, before invoking a later group or repetition. It does not cancel
an in-progress group or retry a request. The manifest preserves MindTrial's exit
code and complete result coverage, adds the affected trace identities, and returns
launcher exit 2 with status `rate_limited`. Other complete Failed/Error results
retain their previous behavior.

Readout v3 now identifies `http_rate_limited` and `no_actionable_content`, and
reads structured error stop reasons even without logs. Raw scores remain intact.
All 213 focused tests pass. Both attached groups reproduce the table above; the
previous 46-attempt readout regression remains unchanged. No world runtime,
public prompt, qualification or MindTrial code was changed. No model calls were
made during this fix; Docker remains unavailable in the development environment.

[Machine-readable record](minimax-control-interruption-2026-11-02.json).
