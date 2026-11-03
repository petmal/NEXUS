"""Apply the bounded readout-default correction to the original fresh-world package.

No model calls, Docker changes, config edits or result rewrites. The runtime
release commit stays pinned; operator update provenance is recorded separately.
"""

import argparse
import copy
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

PATCH_ID = "fresh-readout-defaults-v1"
BASE_COMMIT = "3ded3ba1a83815ed12950529619b344b23186e68"
BASE_SHA = "8e36e2d148577d3a1c1c448e8190a4b8880f278c0d0e6c348ded3921fe13a46c"
TARGET = "summarize_results.py"


def sha(value):
    return hashlib.sha256(value).hexdigest()


def atomic(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", delete=False) as f:
        temporary = Path(f.name)
        f.write(data)
    try:
        os.chmod(temporary, path.stat().st_mode & 0o777)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def apply(package, bundle):
    package, bundle = package.expanduser().resolve(), bundle.resolve()
    metadata = json.loads((bundle / "patch.json").read_text())
    payload = (bundle / TARGET).read_bytes()
    if (
        metadata.get("id") != PATCH_ID
        or metadata.get("base_source_commit") != BASE_COMMIT
        or metadata.get("old_sha256") != BASE_SHA
        or not re.fullmatch(r"[0-9a-f]{40}", metadata.get("operator_source_commit", ""))
        or sha(payload) != metadata.get("new_sha256")
    ):
        raise ValueError("Invalid hotfix metadata or payload.")
    release_path = package / "release.json"
    before = release_path.read_bytes()
    release = json.loads(before)
    if (
        release.get("source_commit") != BASE_COMMIT
        or release.get("image") != "nexus:fresh-world-v1"
    ):
        raise ValueError("This hotfix requires the original 3ded3ba fresh-world package.")
    target = package / TARGET
    old = target.read_bytes()
    current_hash = sha(old)
    expected = release.get("files_sha256", {}).get(TARGET)
    updates = release.get("operator_updates", [])
    if expected == current_hash == metadata["new_sha256"] and metadata in updates:
        return "already-applied"
    if current_hash != BASE_SHA or expected != BASE_SHA or updates:
        raise ValueError("The readout or operator release has changed; refusing to overwrite it.")
    # Preserve deliberately editable model configs. Other release files must still match.
    configs = release.get("config_contract_sha256", {})
    for name, digest in release["files_sha256"].items():
        path = (package / name).resolve()
        if not path.is_relative_to(package) or not path.is_file():
            raise ValueError("A release file is missing or outside the package.")
        if name not in configs and sha(path.read_bytes()) != digest:
            raise ValueError(f"Release checksum mismatch: {name}.")
    backup = package / "operator-updates" / PATCH_ID
    backup.mkdir(parents=True, exist_ok=True)
    for name, data in (("release-before.json", before), (TARGET, old)):
        path = backup / name
        if path.exists() and path.read_bytes() != data:
            raise ValueError("An existing hotfix backup differs; inspect it before proceeding.")
        if not path.exists():
            path.write_bytes(data)
    updated = copy.deepcopy(release)
    updated["files_sha256"][TARGET] = metadata["new_sha256"]
    updated["operator_updates"] = [metadata]
    after = (json.dumps(updated, indent=2, sort_keys=True) + "\n").encode()
    atomic(target, payload)
    try:
        atomic(release_path, after)
    except BaseException:
        atomic(target, old)
        raise
    return "applied"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package",
        type=Path,
        default=Path.home() / "Downloads/NEXUS-fresh-world-test-run-2026-11-03",
    )
    args = parser.parse_args()
    try:
        status = apply(args.package, Path(__file__).resolve().parent)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Hotfix blocked: {exc}\n")
    print(f"Readout hotfix {status}. Existing results and the pinned image are unchanged.")


if __name__ == "__main__":
    main()
