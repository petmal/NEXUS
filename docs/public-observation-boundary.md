# Public observation boundary

`public-interactions-v1` records application-visible exchanges separately from
accepted-action replay. It never adds a player endpoint or changes action costs,
validation, retries, receipts, or terminal scoring.

| Surface | Captured |
|---|---|
| HTTP, single and multiple sessions | Consumed request body/path/query/content type; exact JSON response or plain text; status and ASGI response headers; validation, missing-file, conflict, retry and server-error responses. |
| JSONL | Initial observation, parsed requests or malformed raw input, responses and parser errors. |
| Direct Session | Manifest, evidence, observation, status, action response and raised evidence errors. Typed argument construction is outside this interface. |
| Resource effects | Turn, action allowance and terminal status before/after each Session call, captured under its lock. |

The HTTP recorder wraps outside the framework's error middleware. A ContextVar
passes per-request effects across the sync endpoint boundary without duplicate
records. Internal observations used to form responses are not extra player calls.
The recorder retains nested artifact payloads, public instrument settings, cached
responses and terminal telemetry exactly as exposed. Active responses contain no
new private diagnostics. Public reference agents should use `Session.manifest()`
and `Session.evidence()` so their initial information is also recorded.

Operators can inspect `app.state.public_transcript.snapshot()` or
`session.public_transcript.snapshot()` and save it to an operator-owned path.
The JSONL runner accepts an optional transcript sink. Default retention is 10,000
exchanges / 16 MiB; HTTP body capture is capped at 2 MiB per direction. Overflow,
partial delivery or an interrupted response marks coverage incomplete. Such a
record cannot justify a complete-evidence or interface-equivalence claim.

This is an application projection, not a packet capture: credentials, external
proxy behavior, network headers and wall-clock timing are excluded. Unconsumed
request bodies cannot affect the current application; transport parser errors
before ASGI are outside scope. Concurrent records are completed exchanges, not
an assertion of a total order on overlapping network requests. Per-call effects
are captured atomically; single-session policy certificates require serialized
scientific commands. An unrecorded external side channel is never silently
certified by this transcript.

Reference: ASGI HTTP specification 2.5,
https://asgi.readthedocs.io/en/latest/specs/www.html .
