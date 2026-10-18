"""Verified immutable observation partitions; never compile scalar laws during play."""

import base64
import hashlib
import json
import zlib
from functools import lru_cache
from importlib.resources import files

from nexus.ontology.transfer.laws import PROGRAMS, QUERIES
from nexus.ontology.transfer.reference import semantic_digest


@lru_cache(maxsize=1)
def load():
    from nexus.ontology.transfer.observations_identity import SHA256

    raw = files("nexus.ontology.transfer").joinpath("observations.json").read_bytes()
    if len(raw) > 1_000_000 or hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError("transfer observations integrity mismatch")
    data = json.loads(raw)
    size, queries = len(PROGRAMS), len(QUERIES)
    if (
        data["version"] != "transfer-observations-v1"
        or data["encoding"] != "base64-zlib-little-endian-bitsets"
        or (data["programs"], data["queries"], data["channels"]) != (size, queries, 3)
        or data["semantic_digest"] != semantic_digest()
    ):
        raise ValueError(
            "stale transfer observations; run scripts/compile_transfer_observations.py --write"
        )
    width = (size + 7) // 8
    expected = 3 * queries * 3 * width
    decoder = zlib.decompressobj()
    decoded = decoder.decompress(base64.b64decode(data["data"], validate=True), expected + 1)
    if len(decoded) != expected or not decoder.eof or decoder.unused_data:
        raise ValueError("invalid transfer observation payload")
    masks = tuple(
        int.from_bytes(decoded[i : i + width], "little") for i in range(0, expected, width)
    )
    rows = tuple(masks[i : i + 3] for i in range(0, len(masks), 3))
    full = (1 << size) - 1
    if any(a | b | c != full or a & b or a & c or b & c for a, b, c in rows):
        raise ValueError("invalid transfer observation partition")
    return tuple(rows[i : i + queries] for i in range(0, len(rows), queries))
