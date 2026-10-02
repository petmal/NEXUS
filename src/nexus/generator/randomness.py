from __future__ import annotations

import hashlib
import json
import random


def derive_seed(seed: int, namespace: str, *parts: object) -> int:
    """Derive a stable independent pseudo-random seed for one generation concern."""
    payload = json.dumps(
        [seed, namespace, *parts],
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:16], "big")


def rng_for(seed: int, namespace: str, *parts: object) -> random.Random:
    return random.Random(derive_seed(seed, namespace, *parts))


def scenario_family_id(seed: int, family_kind: str, family_attempt: int) -> str:
    payload = json.dumps(
        ["nexus-scenario-family", seed, family_kind, family_attempt],
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]
