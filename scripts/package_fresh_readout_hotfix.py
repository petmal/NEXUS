"""Rebuild the original operator-only correction for the November 3 fresh-world package."""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from apply_fresh_readout_hotfix import BASE_COMMIT, BASE_SHA, PATCH_ID

ROOT = Path(__file__).resolve().parents[1]
PATCH_COMMIT = "7e2b74e5c16a8afd4687bfaf4538bbba72592ed6"
FILES = {
    "apply.py": "scripts/apply_fresh_readout_hotfix.py",
    "summarize_results.py": "examples/mindtrial/summarize-pilot-results.py",
    "resume.sh": "examples/mindtrial/fresh-world-resume-after-readout-fix.sh",
    "README.md": "docs/fresh-world-readout-fix.md",
}


def package(directory):
    # Newer readouts have different semantics. Never ship HEAD under the old patch ID.
    try:
        contents = {
            name: subprocess.check_output(
                ["git", "-C", str(ROOT), "show", f"{PATCH_COMMIT}:{path}"],
                stderr=subprocess.PIPE,
            ) for name, path in FILES.items()
        }
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"Historical patch source unavailable; fetch commit {PATCH_COMMIT} first.") from exc
    directory.mkdir(parents=True, exist_ok=False)
    for name, content in contents.items():
        (directory / name).write_bytes(content)
    for executable in ("summarize_results.py", "resume.sh"):
        (directory / executable).chmod(0o755)
    metadata = {
        "id": PATCH_ID,
        "base_source_commit": BASE_COMMIT,
        "operator_source_commit": PATCH_COMMIT,
        "old_sha256": BASE_SHA,
        "new_sha256": hashlib.sha256(contents["summarize_results.py"]).hexdigest(),
        "scope": "Known false response-format defaults only; no runtime/config/task/result changes.",
    }
    (directory / "patch.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return shutil.make_archive(str(directory), "zip", directory.parent, directory.name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    try:
        print(package(args.output_dir.resolve()))
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
