#!/usr/bin/env python3
"""Run the fresh-world panel through the shared pinned launcher."""

import importlib.util
from pathlib import Path


def main():
    package = Path(__file__).resolve().parent
    helper = package / "pilot_runner.py"
    if not helper.is_file():
        helper = package / "coordination-runner.py"
    spec = importlib.util.spec_from_file_location("nexus_pilot_runner", helper)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load the shared pilot runner")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    return runner.main(package_dir=package, pilot=runner.FRESH_WORLD)


if __name__ == "__main__":
    raise SystemExit(main())
