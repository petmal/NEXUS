"""Immutable process-shared reference data; never caches episode or player state.

Integrity and semantic binding are checked at cold load. Full recurrence and
original tie-breaking are independently recomputed by the offline/CI checker.
A stale or absent optimization falls back to exact computation.
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from time import perf_counter
from types import MappingProxyType

from nexus.ontology.dynamics.reference_identity import SHA256

ROOT = Path(__file__).parents[2]
PATH = Path(__file__).with_name("reference-policy.json")
SOURCES = (
    "engine/engine.py",
    "engine/investigation.py",
    "models/actions.py",
    "models/world.py",
    "models/domain.py",
    "models/episode.py",
    "ontology/contracts.py",
    "protocol/session.py",
    "ontology/dynamics/schema.py",
    "ontology/dynamics/laws.py",
    "ontology/dynamics/inference.py",
    "ontology/dynamics/reference_cache.py",
    "ontology/dynamics/reference_proof.py",
    "ontology/dynamics/policy.py",
    "ontology/dynamics/generation.py",
    "ontology/dynamics/runtime.py",
)
MAX_BYTES = 3_000_000


@dataclass(frozen=True)
class Node:
    query: int | None
    readings: int
    work: int


def source_binding():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES}


def decode(raw: bytes, digest: str, sources: dict[str, str]):
    if len(raw) > MAX_BYTES or hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError("reference artifact integrity mismatch")
    data = json.loads(raw)
    if set(data) != {"version", "sources", "nodes"} or data["version"] != 1:
        raise ValueError("unsupported reference artifact")
    if data["sources"] != sources:
        raise ValueError("reference artifact semantic binding mismatch")
    entries = data["nodes"]
    if not isinstance(entries, list) or not 1 <= len(entries) <= 4096:
        raise ValueError("invalid reference node count")
    nodes = {}
    for entry in entries:
        if not isinstance(entry, list) or len(entry) != 4:
            raise ValueError("invalid reference node")
        key, query, readings, work = entry
        if not isinstance(key, str) or not 1 <= len(key) <= 486:
            raise ValueError("invalid reference mask")
        mask = int(key, 16)
        if mask <= 0 or mask.bit_length() > 1944 or mask in nodes:
            raise ValueError("invalid or duplicate reference mask")
        if query is not None and (type(query) is not int or not 0 <= query < 582):
            raise ValueError("invalid reference query")
        if any(type(v) is not int or not 0 <= v <= 100 for v in (readings, work)):
            raise ValueError("invalid reference bound")
        nodes[mask] = Node(query, readings, work)
    if (1 << 1944) - 1 not in nodes:
        raise ValueError("missing reference root")
    return MappingProxyType(nodes)


@lru_cache(maxsize=1)
def load():
    started = perf_counter()
    try:
        with PATH.open("rb") as handle:
            raw = handle.read(MAX_BYTES + 1)
        nodes = decode(raw, SHA256, source_binding())
    except (OSError, ValueError, TypeError, KeyError) as exc:
        logging.getLogger("nexus.generation").warning(
            "dynamics_reference_cache status=fallback reason=%s", str(exc)
        )
        return MappingProxyType({})
    logging.getLogger("nexus.generation").info(
        "dynamics_reference_cache status=hit nodes=%s seconds=%.6f",
        len(nodes),
        perf_counter() - started,
    )
    return nodes
