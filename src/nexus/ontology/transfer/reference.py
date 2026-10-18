"""Small immutable offline policy; generation never searches a policy tree."""

import hashlib
import json
from functools import lru_cache
from importlib.resources import files
from types import MappingProxyType


def semantic_digest():
    digest = hashlib.sha256(b"transfer-reference-v1")
    for package, name in (
        ("nexus.ontology.transfer", "laws.py"),
        ("nexus.ontology.compositional", "laws.py"),
    ):
        digest.update(files(package).joinpath(name).read_bytes())
    return digest.hexdigest()


@lru_cache(maxsize=1)
def load():
    from nexus.ontology.transfer.reference_identity import SHA256

    raw = files("nexus.ontology.transfer").joinpath("reference.json").read_bytes()
    if len(raw) > 1_000_000 or hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError("transfer reference integrity mismatch")
    data = json.loads(raw)
    if data["semantic_digest"] != semantic_digest():
        raise ValueError(
            "stale transfer reference; run scripts/compile_transfer_reference.py --write"
        )
    if len(data["targets"]) != 5184 or any(not 0 <= i < 5184 for i in data["targets"]):
        raise ValueError("invalid transfer target table")
    data["targets"] = tuple(data["targets"])
    for name in ("calibrated", "coupled"):
        data[name] = MappingProxyType(
            {
                "readings": data[name]["readings"],
                "nodes": tuple(tuple(n) for n in data[name]["nodes"]),
            }
        )
    return MappingProxyType(data)
