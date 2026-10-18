"""Rebuild all observation masks from scalar laws; no runtime asset dependency.

The packaged masks cover every program/query, not selected episode seeds.
Default: compare against the checked-in artifact; --write deliberately replaces it.
"""

import argparse
import base64
import hashlib
import json
import zlib
from pathlib import Path
from time import perf_counter

from nexus.ontology.transfer.laws import PROGRAMS, QUERIES, components, signatures
from nexus.ontology.transfer.reference import semantic_digest


def compile_observations():
    size = len(PROGRAMS)
    width = (size + 7) // 8
    physical = signatures()
    companion = tuple(
        bytes(components(p, (1 - q[0], *q[1:]))[1] for q in QUERIES) for p in PROGRAMS[::3]
    )
    raw = bytearray()
    for kind in range(3):  # physical, raw survey, raw reference; reader offset zero
        for query in range(len(QUERIES)):
            masks = [0, 0, 0]
            for i in range(size):
                value = physical[i][query] if kind != 2 else 0
                if kind:
                    value += companion[i // 3][query]
                masks[value % 3] |= 1 << i
            raw.extend(b"".join(mask.to_bytes(width, "little") for mask in masks))
    return {
        "version": "transfer-observations-v1",
        "semantic_digest": semantic_digest(),
        "programs": size,
        "queries": len(QUERIES),
        "channels": 3,
        "encoding": "base64-zlib-little-endian-bitsets",
        "data": base64.b64encode(zlib.compress(raw, 9)).decode("ascii"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    started = perf_counter()
    path = Path(__file__).resolve().parents[1] / "src/nexus/ontology/transfer/observations.json"
    rendered = json.dumps(compile_observations(), separators=(",", ":")) + "\n"
    identity = (
        '# Offline observation identity; update through the compiler.\nSHA256 = "'
        + hashlib.sha256(rendered.encode()).hexdigest()
        + '"\n'
    )
    identity_path = path.with_name("observations_identity.py")
    if args.write:
        path.write_text(rendered, encoding="utf-8")
        identity_path.write_text(identity, encoding="utf-8")
    elif path.read_text(encoding="utf-8") != rendered or identity_path.read_text() != identity:
        raise SystemExit("transfer observations differ; use --write after reviewing semantics")
    print(json.dumps({"seconds": perf_counter() - started, "bytes": len(rendered)}))


if __name__ == "__main__":
    main()
