UV = uv run --frozen --python 3.14.7 --all-extras

.PHONY: check test test-fast test-full stress package qualify-release preflight ci ci-partition
check:
	$(UV) ruff check src tests scripts examples
	$(UV) python scripts/check_docs.py

test: test-fast

test-fast:
	$(UV) pytest -q -m 'not slow and not stress' tests/unit tests/integration

test-full:
	$(UV) pytest -q tests

ci:
	$(UV) python scripts/ci.py run $(GROUP)

ci-partition:
	$(UV) python scripts/ci.py partition

stress:
	$(UV) pytest -q tests/property

package:
	$(UV) python scripts/smoke_distribution.py

qualify-release:
	$(UV) python scripts/compile_dynamics_reference.py --write
	$(UV) python scripts/compile_transfer_observations.py --write
	$(UV) python scripts/compile_transfer_reference.py --write
	$(UV) python scripts/refresh_repair_release.py

preflight:
	$(UV) python scripts/preflight_cross_axis.py --output docs/research/cross-axis-preflight-current.json
	$(UV) python scripts/fresh_worlds.py --output docs/research/fresh-world-preflight-current.json
