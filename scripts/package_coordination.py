"""Package the clean checkout's pinned pilot; stdlib only, no model calls."""

import argparse
import importlib.util
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--runtime-source-sha256", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{64}", args.runtime_source_sha256):
        parser.error("runtime source SHA-256 must be 64 lowercase hexadecimal characters")
    git = ["git", "-C", str(ROOT)]
    if subprocess.check_output([*git, "status", "--porcelain"], text=True).strip():
        parser.error("commit or isolate checkout changes before packaging")
    commit = subprocess.check_output([*git, "rev-parse", "HEAD"], text=True).strip()
    examples = ROOT / "examples/mindtrial"
    spec = importlib.util.spec_from_file_location(
        "coordination_runner", examples / "coordination-runner.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load the pilot launcher")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    destination = args.output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    copies = {
        "run.sh": examples / "coordination-run.sh",
        "runner.py": examples / "coordination-runner.py",
        "README.md": examples / "coordination-run.md",
        **{name: examples / name for name in runner.CONFIGS},
        **{
            f"nexus-coordination-{suite}-tasks.yaml": examples
            / f"nexus-coordination-{suite}-tasks.yaml"
            for suite in runner.SUITES
        },
    }
    for name, source in copies.items():
        shutil.copy2(source, destination / name)
    reports = destination / "reports"
    reports.mkdir()
    for name in (
        "coordination-preflight-2026-10-25.json",
        "coordination-legacy-preflight-2026-10-25.json",
        "planning-resource-pilot-results-2026-10-25.md",
        "planning-resource-pilot-results-2026-10-25.json",
    ):
        shutil.copy2(ROOT / "docs/research" / name, reports / name)
    release = {
        "source_commit": commit,
        "branch": runner.BRANCH,
        "image": runner.IMAGE,
        "runtime_source_sha256": args.runtime_source_sha256,
        "config_contract_sha256": {
            name: runner.config_contract_sha256(runner.read_json(destination / name))
            for name in runner.CONFIGS
        },
        "files_sha256": {
            path.relative_to(destination).as_posix(): runner.sha256(path.read_bytes())
            for path in sorted(destination.rglob("*"))
            if path.is_file()
        },
        "design_url": f"https://github.com/petmal/NEXUS/blob/{commit}/docs/coordination-guide.md",
    }
    runner.write_json(destination / "release.json", release)
    runner.load_release(destination)
    for name in runner.CONFIGS:
        runner.load_config(destination, release, name)
    archive = shutil.make_archive(str(destination), "zip", destination.parent, destination.name)
    print(archive)


if __name__ == "__main__":
    main()
