"""Package the operator-only fix for the already-running fresh-world release."""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from apply_fresh_readout_hotfix import BASE_COMMIT, BASE_SHA, PATCH_ID

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    if subprocess.check_output(
        ["git", "-C", str(ROOT), "status", "--porcelain"], text=True
    ).strip():
        parser.error("Commit the operator fix before packaging.")
    commit = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    directory = args.output_dir.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    for name, source in {
        "apply.py": ROOT / "scripts/apply_fresh_readout_hotfix.py",
        "summarize_results.py": ROOT / "examples/mindtrial/summarize-pilot-results.py",
        "resume.sh": ROOT / "examples/mindtrial/fresh-world-resume-after-readout-fix.sh",
        "README.md": ROOT / "docs/fresh-world-readout-fix.md",
    }.items():
        shutil.copy2(source, directory / name)
    metadata = {
        "id": PATCH_ID,
        "base_source_commit": BASE_COMMIT,
        "operator_source_commit": commit,
        "old_sha256": BASE_SHA,
        "new_sha256": hashlib.sha256((directory / "summarize_results.py").read_bytes()).hexdigest(),
        "scope": "Known false response-format defaults only; no runtime/config/task/result changes.",
    }
    (directory / "patch.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(shutil.make_archive(str(directory), "zip", directory.parent, directory.name))


if __name__ == "__main__":
    main()
