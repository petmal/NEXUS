"""Explicit offline refresh/check of immutable dynamics policy data. No player state."""

import argparse
import hashlib
from pathlib import Path

from nexus.ontology.dynamics.reference_cache import PATH
from nexus.ontology.dynamics.reference_proof import serialized


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Publish independently checked data and pinned identity",
    )
    args = parser.parse_args()
    raw = serialized()
    identity = (
        '"""Pinned digest of the offline checked, data-only public reference policy."""\n\nSHA256 = "'
        + hashlib.sha256(raw).hexdigest()
        + '"\n'
    )
    identity_path = PATH.with_name("reference_identity.py")
    if args.write:
        for path, data in ((PATH, raw), (identity_path, identity.encode())):
            temporary = Path(str(path) + ".tmp")
            temporary.write_bytes(data)
            temporary.replace(path)
    elif PATH.read_bytes() != raw or identity_path.read_text() != identity:
        raise SystemExit("reference artifact stale; run --write after reviewing semantic changes")
    print(f"dynamics reference independently checked: {len(raw)} bytes")


if __name__ == "__main__":
    main()
