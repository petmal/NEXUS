# Contributing to NEXUS

Read [AGENTS.md](AGENTS.md) and the [research guide](docs/research-guide.md) before
changing mechanics or reported metrics. Work on a feature branch and open a pull
request. Keep changes small enough to review; explain the observed problem,
changed behavior, checks and remaining limitations.

```bash
uv sync --frozen --all-extras --python 3.14.7
make check
make test
```

`make check` runs the pinned lint baseline and documentation-link checks.
`make test` runs fast unit/integration tests. `make test-full` includes slower
unit/integration cases; `make stress` runs the property suite. `make package`
builds a wheel and source distribution and checks clean installation. None of
these commands calls a paid model. See [release status](docs/release-readiness.md)
for the separate container and live-provider gates.

The engine owns atomic transitions, costs, terminal state, receipts and replay.
Ontologies supply validated laws, inference and qualification. Renderers project
public state and never implement mechanics. Extend the
[ontology contract](docs/ontology-author-guide.md) rather than add family-specific
branches to the generic engine. Add regression tests for defects and meaningful
invariant tests for new mechanics; avoid tests that only repeat implementation.

Public schema and presentation changes can invalidate comparisons. Version them,
record the reason, and preserve old artifacts. Changing installed Python/JSON
source changes the runtime digest. `coupled-repair-v1` additionally binds its
qualification to Python source and its checked proof/witness. After final source
edits, run `make qualify-release`; it executes the proof and conformance gates
before refreshing the binding. Never merely replace a digest to bypass a gate.
Then run `make preflight` for the current cross-axis and fresh-world matrices,
and validate the resulting candidate with the full and property suites.

Use frozen dependencies. For a dependency update, edit `pyproject.toml`, run
`uv lock --python 3.14.7`, inspect the lock diff, and run the relevant checks.
The explicit Ruff baseline catches import/name/syntax errors. A complete static
type-checking and formatting migration is not yet enforced; avoid unrelated
mass reformatting in a functional change.

New reports should explain the question, controls, sample, exact measurements,
interpretation and limitations in language accessible to an AI/CS undergraduate.
Keep quickstart docs short; place technical detail in a linked reference.
