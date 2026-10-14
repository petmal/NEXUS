"""Restore canonical line endings in the build copy; never refresh qualification.

Existing Windows checkouts can retain CRLF after .gitattributes changes. The
installed package must still pass the exact source/proof/witness release check.
"""

import argparse
from pathlib import Path


def normalize_sources(root: Path) -> int:
    if not root.is_dir():
        raise ValueError(f"package directory does not exist: {root}")
    changed = 0
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix in (".py", ".json"):
            content = path.read_bytes()
            normalized = content.replace(b"\r\n", b"\n")
            if normalized != content:
                path.write_bytes(normalized)
                changed += 1
    return changed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path("src/nexus"))
    args = parser.parse_args()
    print(f"Package preparation: normalized CRLF in {normalize_sources(args.root)} files")
