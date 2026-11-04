# Service and data boundaries

NEXUS is a local research environment. It is not an authenticated public hosting
service or a multi-tenant sandbox. The default HTTP listener is loopback only.
If a harness binds another address, isolate it with a private container/network
boundary. `/finalize` is evaluator-only by contract; hiding it from OpenAPI does
not enforce access control. Allowlist the player tool operations in the harness.

Keep generator seeds, compiled private episodes, verifier secrets, reference
plans, operator logs and audit bundles outside player filesystem/process access.
Only the player manifest, evidence and allowed protocol responses are public.
Do not mount the repository or engine credentials into an evaluated model's shell.
Audit exports contain secrets and possibly model-supplied text; inspect and redact
external logs before sharing. Never reuse a secret from a published test bundle.

Compiled episodes use validated data and registered built-in adapters, not dynamic
code imports or `eval`. Still, treat compiled private files as trusted operator
inputs: arbitrary large/adversarial files are outside the resource-isolation
claim. Keep HTTP/body, process-memory and execution-time limits at the harness
boundary. The application capture limits bound audit retention, not all server
resource use.

Report a suspected defect privately to the repository maintainer where private
reporting is available. Do not post secrets, provider keys or held-out worlds in
a public issue. There is no claim of a completed independent security audit.
