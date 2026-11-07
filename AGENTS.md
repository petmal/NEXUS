# Working on NEXUS

These instructions apply throughout the repository. NEXUS is a standalone reasoning
environment: humans and models act in the same compiled world, and the engine checks
the result. Keep it possible to run and test NEXUS without a provider account,
MindTrial, Docker or an LLM judge. Harness examples belong under [examples](examples);
the core must not depend on a harness or model vendor.

## Where to make a change

| Concern | Start here |
|---|---|
| State, actions, costs, goals, receipts and replay | [Models](src/nexus/models), [engine](src/nexus/engine), [verification](src/nexus/verification) |
| Legacy rule generation, physical and public-information search | [Generator](src/nexus/generator), [solver](src/nexus/solver), [legacy difficulty](docs/difficulty.md) |
| Scientific world laws, evidence, planners and qualification | [Trusted catalog](src/nexus/ontology/catalog.py), [world author guide](docs/ontology-author-guide.md) |
| Player observations, story, session lifecycle, retries and audit | [Presentation](src/nexus/presentation), [rendering](src/nexus/render), [protocol](src/nexus/protocol), [transport contract](docs/reference/protocol.md) |
| Experiment packages, analysis and reporting | [Evaluation code](src/nexus/evaluation), [operator guide](docs/evaluation-guide.md), [research guide](docs/research-guide.md) |

Read the relevant implementation, tests and current guide before editing.
A dated design or experiment report records what was tried; it does not override
the shipped interface. Use the existing family and protocol boundaries. Prefer a
small explicit implementation to a new framework or speculative game system.

For a player protocol change, check the shared schema and both transports: the typed
[request envelopes](src/nexus/protocol/requests.py), the installed
[lightweight client](src/nexus/protocol/fast_cli.py) and its
[HTTP transport](src/nexus/protocol/transport.py), and the
[JSONL service](src/nexus/protocol/stdio.py). The installed `request`, `validate`
and `health` commands bypass Typer. Test the installed path as well as Python
calls; keep the lightweight path on the standard library (no Pydantic, Typer or
FastAPI imports).

## Invariants to preserve

- A compiled episode, its verifier secret and the same actions reproduce the same
  state, events and receipt. Prefer exact, bounded arithmetic. Renderers and
  prompts describe mechanics; they do not decide them. A rejected action does
  not advance the world. A legal but unhelpful action can still cost a turn.
- Teach the controls. Keep the seed, verifier secret, private plan and operator
  diagnostics away from the player. Expose laws or supplied solutions **when
  the profile promises them**; other profiles require discovery. The file named
  `private.json` and the compiled `PublicEpisode` are operator inputs. Use the
  player manifest, evidence and observations for player-facing interfaces.
- Keep episode data declarative. Only trusted repository code registers
  ontologies; never load modules or execute callbacks named by episode data.
  Vary laws or targets where the experiment calls for it; retain matched
  controls, deterministic replay and a mechanically checked route to victory.
- For player evidence, use the [presentation projection](src/nexus/presentation).
  A compiled attachment may differ from the text actually served. Bind and test
  the delivered text separately from its compiled source. Return independent
  instruction/observation objects; one Python player must not change another's
  inputs. A retry is identified by both the original turn and action.
- Separate a physical win, an issued receipt and a harness-accepted answer.
  Separate a winning witness, a proven minimum and a public-policy upper
  bound. Do not interpret missing diagnostics or an uncapped budget as zero.
  Qualification is evidence about a world, not a model difficulty rating.
- A profile number has meaning within its family. Document supported T/D/P/R
  settings, disclosures, costs, qualification scope and unavailable metrics.
  Keep provider errors, retries, inference settings and harness limits distinct
  from game outcomes. See the [metric contracts](docs/reference/metrics.md).

## Verification and handoff

Work on a feature branch and review changes through a pull request. From a
checkout, run `uv sync --frozen --all-extras --python 3.14.7`. Add a regression
that exercises the observable defect or an independently checked invariant.

| When | Check |
|---|---|
| Normal change | Run relevant tests, then `make check` (Ruff and local docs) and `make test` (fast unit/integration). |
| Core mechanics, solver or release candidate | `make test-full` includes slow unit/integration cases; `make stress` runs the separate property suite. |
| Installed Python/JSON or release-bound code changes | After the final source edit, run `make qualify-release`, then `make preflight`. Use the resulting source and current reports for release checks. Never hand-edit a digest to make a gate pass. |
| Packaging or release | `make package` checks clean distribution installs. See [release readiness](docs/release-readiness.md) for container, live-canary and publication gates. Local tests do not establish provider behavior. |

Keep the lockfile and dependency declarations consistent. Preserve dated research
results; regenerate only the current reports. Version changes to evaluated public
text and schema contracts so old results remain interpretable. Write introductory
docs for a first-time player and research reports for an AI/CS undergraduate.
Record what changed, which checks actually ran, and what remains unverified.
